"""Prove the Claude Code hooks are wired and still refuse what they exist to refuse.

Each hook is run as Claude Code runs it, a subprocess fed the tool call as JSON, over a table of
calls that must be refused (exit 2 with a reason on stderr) and calls that must pass (exit 0). A
hook that crashes exits 1, which Claude Code treats as "allow", so a crash counts as an allowance
here. `.claude/settings.json` must parse and name each hook: a settings file that does not parse
switches every hook off without a word.

    uv run python tools/claude_hooks/prove.py
"""

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / ".claude/settings.json"
HOOKS = ROOT / "tools/claude_hooks"
REFUSE, ALLOW = 2, 0


@dataclass(frozen=True)
class Case:
    """One tool call, the hook's expected exit code, and the words a refusal must carry."""

    payload: dict[str, object]
    expect: int
    says: str = ""


def bash(command: str) -> dict[str, object]:
    """The hook input for a Bash call."""
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def write(path: str) -> dict[str, object]:
    """The hook input for a Write call to a project path."""
    return {"tool_name": "Write", "tool_input": {"file_path": str(ROOT / path), "content": ""}}


BASH_CASES = [
    *(
        Case(bash(c), REFUSE, "switches off the git hooks")
        for c in (
            "git commit --no-verify -m x",
            "git commit -nm x",
            "git commit -a -n",
            "git push --no-verify",
            "git merge --no-verify topic",
            "git -c core.hooksPath=/dev/null commit -m x",
            "git config core.hooksPath /tmp/none",
            "git config --unset core.hooksPath",
            'cd src && "git" commit --no-verify',
            "uv run ruff check . && git commit -m x --no-verify",
        )
    ),
    *(
        Case(bash(c), ALLOW)
        for c in (
            "git commit -m x",
            "git push",
            "git push -n",
            "git log -n 3",
            "git config --get core.hooksPath",
            "git config core.hooksPath tools/git_hooks",
            'grep -rn "git commit --no-verify" docs',
            "make check",
            "ls",
        )
    ),
]
WRITE_CASES = [
    *(
        Case(write(p), REFUSE, "closed lists")
        for p in (
            "src/uiaudit/run/helpers.py",
            "src/uiaudit/utils.py",
            "src/uiaudit/undeclared/ops.py",
            "src/uiaudit/run/store.py",
            "src/uiaudit/kernel/cache.py",
            "src/uiaudit/surfaces/jobs.py",
            "tests/helpers.py",
            "tests/run/test_helpers.py",
            "migrations/init.sql",
            "scripts/run.sh",
        )
    ),
    *(
        Case(write(p), ALLOW)
        for p in (
            "src/uiaudit/run/ops.py",
            "src/uiaudit/finding/rules/identity.py",
            "src/uiaudit/run/ops/start.py",
            "src/uiaudit/kernel/clock.py",
            "src/uiaudit/flows/audit.py",
            "tests/run/test_ops.py",
            "tests/test_smoke.py",
            "tests/fixtures/page.html",
            "migrations/0001_init.sql",
            "docs/notes.md",
            "tools/anything.py",
            "README.md",
        )
    ),
]


def run_hook(script: str, payload: dict[str, object], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run one hook the way Claude Code does: from the project root, the call as JSON on stdin."""
    return subprocess.run(
        ["uv", "run", "--no-sync", "python", str(HOOKS / script)],
        cwd=cwd,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(cwd)},
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def failures(script: str, cases: list[Case]) -> list[str]:
    """Every case the hook got wrong: allowed what it must refuse, refused what it must allow, or crashed."""
    out = []
    for case in cases:
        done = run_hook(script, case.payload, ROOT)
        shown = json.dumps(case.payload["tool_input"])
        if case.expect == REFUSE and done.returncode != REFUSE:
            out.append(f"{script} allowed {shown} (exit {done.returncode}): {done.stderr.strip()[:200]}")
        elif case.expect == REFUSE and case.says not in done.stderr:
            out.append(f"{script} refused {shown} without saying {case.says!r}")
        elif case.expect == ALLOW and done.returncode != ALLOW:
            out.append(f"{script} refused {shown} (exit {done.returncode}): {done.stderr.strip()[:200]}")
    return out


def session_start_failures() -> list[str]:
    """The session-start hook must warn in a clone whose hooks are off, and stay quiet once they are on."""
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=clone, check=False)
        (clone / ".venv").mkdir()
        off = run_hook("session_start.py", {"hook_event_name": "SessionStart"}, clone)
        if off.returncode != 0 or "git hooks are off" not in off.stdout:
            out.append(
                f"session_start.py did not warn with hooks off (exit {off.returncode}): {off.stdout!r}"
            )
        subprocess.run(["git", "config", "core.hooksPath", "tools/git_hooks"], cwd=clone, check=False)
        on = run_hook("session_start.py", {"hook_event_name": "SessionStart"}, clone)
        if "git hooks are off" in on.stdout:
            out.append("session_start.py warned although core.hooksPath is set")
    return out


def wiring_failures() -> list[str]:
    """The settings file must parse and name each hook under the right event and matcher."""
    try:
        hooks = json.loads(SETTINGS.read_text()).get("hooks", {})
    except json.JSONDecodeError as error:
        return [
            f"{SETTINGS.relative_to(ROOT)} is not valid JSON ({error}); Claude Code drops every hook in it"
        ]
    wanted = {("PreToolUse", "Bash", "bash_guard.py"), ("PreToolUse", "Write", "new_module_guard.py")}
    wanted.add(("SessionStart", "", "session_start.py"))
    present = {
        (event, group.get("matcher", ""), Path(hook["command"].split()[-1]).name)
        for event, groups in hooks.items()
        for group in groups
        for hook in group.get("hooks", [])
        if hook.get("type") == "command"
    }
    return [
        f"{SETTINGS.relative_to(ROOT)} does not wire {s} to {e} {m!r}".rstrip()
        for e, m, s in wanted - present
    ]


def main() -> int:
    """Prove the wiring and every case; print one line per hook and exit 1 on any failure."""
    problems = wiring_failures()
    for script, cases in (("bash_guard.py", BASH_CASES), ("new_module_guard.py", WRITE_CASES)):
        found = failures(script, cases)
        problems += found
        print(f"{'FAIL' if found else 'ok  '}  {script}: {len(cases)} calls")
    found = session_start_failures()
    problems += found
    print(f"{'FAIL' if found else 'ok  '}  session_start.py: warns when the git hooks are off")
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
