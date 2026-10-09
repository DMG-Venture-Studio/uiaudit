"""PreToolUse on Bash: refuse the commands that switch the git hooks off.

`git commit --no-verify` (or `-n`), `git push --no-verify`, `git merge --no-verify`, a one-off
`-c core.hooksPath=...`, and `git config core.hooksPath` set to anything but this project's hooks
are refused with exit 2, which blocks the call and shows the reason to the session. Quotes are
dropped before reading, so `"git" commit --no-verify` is still git; the command is split at `;`,
`&&`, `|`, newlines and subshells, and git is judged where it is the command, after `env`, `exec`
and the like. A flag quoted inside a commit message is refused too; rephrase the message.
Reads the hook's JSON from stdin; anything unreadable is allowed, so a bug here never blocks.
"""

import json
import re
import sys

HOOKS_PATH = "tools/git_hooks"
SPLIT = re.compile(r"[;&|\n`(){}]|\$\(")
WRAPPERS = {"env", "command", "exec", "nohup", "time", "sudo", "doas", "nice", "ionice", "stdbuf", "xargs"}
NO_VERIFY_SUBCOMMANDS = {"commit", "push", "merge", "rebase", "cherry-pick", "am", "revert"}
SHORT_N = re.compile(r"^-[A-Za-z]*n[A-Za-z]*$")
READ_CONFIG = {"--get", "--get-all", "--get-regexp", "--list", "-l", "--show-origin", "--show-scope"}
WHY = (
    "Refused: {what} switches off the git hooks that hold this project's checks (CONSTRAINTS.md). "
    "Run `make check`, fix what fails, and commit without it; a check that blocks something the "
    "conventions require is reported, never bypassed."
)


def words(segment: str) -> list[str]:
    """The segment's words with env assignments and wrappers stripped from the front."""
    tokens = segment.split()
    while tokens and (
        re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]) or tokens[0].rsplit("/", 1)[-1] in WRAPPERS
    ):
        tokens.pop(0)
    return tokens


def git_parts(tokens: list[str]) -> tuple[list[str], str | None, list[str]]:
    """A git command's global options, its subcommand and the rest; subcommand None when absent."""
    i, options = 1, []
    while i < len(tokens) and tokens[i].startswith("-"):
        options.append(tokens[i])
        if tokens[i] in {"-c", "-C", "--git-dir", "--work-tree", "--namespace"} and i + 1 < len(tokens):
            options.append(tokens[i + 1])
            i += 1
        i += 1
    return options, (tokens[i] if i < len(tokens) else None), tokens[i + 1 :]


def hooks_path_override(options: list[str], subcommand: str | None, rest: list[str]) -> str | None:
    """What overrides the hooks path in this git command, if anything does."""
    if any("core.hookspath" in o.lower() for o in options):
        return "`-c core.hooksPath=...`"
    if subcommand == "config" and any("core.hookspath" in r.lower() for r in rest):
        if any(r in READ_CONFIG for r in rest):
            return None
        if "--unset" in rest or "--unset-all" in rest:
            return "unsetting core.hooksPath"
        value = [r for r in rest if not r.startswith("-") and "core.hookspath" not in r.lower()]
        if value and value[-1].rstrip("/") == HOOKS_PATH:
            return None
        return f"setting core.hooksPath to {value[-1] if value else 'nothing'!r}"
    return None


def refusal(command: str) -> str | None:
    """Why the command is refused, or None when it may run."""
    cleaned = command.replace('"', "").replace("'", "").replace("\\", "")
    for segment in SPLIT.split(cleaned):
        tokens = words(segment)
        if not tokens or tokens[0].rsplit("/", 1)[-1] != "git":
            continue
        options, subcommand, rest = git_parts(tokens)
        override = hooks_path_override(options, subcommand, rest)
        if override:
            return WHY.format(what=override)
        if subcommand in NO_VERIFY_SUBCOMMANDS and any(
            r == "--no-verify" or r.startswith("--no-verify=") for r in rest
        ):
            return WHY.format(what=f"`git {subcommand} --no-verify`")
        if subcommand == "commit" and any(SHORT_N.match(r) for r in rest):
            return WHY.format(what="`git commit -n` (short for --no-verify)")
    return None


def main() -> int:
    """Read the tool call from stdin; exit 2 with the reason on stderr to refuse it."""
    try:
        payload = json.load(sys.stdin)
        command = str(payload.get("tool_input", {}).get("command", ""))
    except (json.JSONDecodeError, AttributeError):
        return 0
    why = refusal(command)
    if why:
        sys.stderr.write(why + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
