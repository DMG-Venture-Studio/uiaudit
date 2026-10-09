"""The debt ratchet: no ledger grows, no rule is removed, no limit is raised, unless the commit says so.

Compared against the base (the merge base with main; HEAD when already on main), the candidate tree
(the working tree, the index with --staged, or a commit with --commit) may not:
- grow a ledger under tools/ledgers/, nor hold a suppression comment in code that no ledger lists;
- lose a rule from ruff's select or extend-select, gain an ignore, a per-file ignore or an exclude;
- raise a numeric limit in ruff.toml or a budget in harness.toml;
- drop a check or a plant from a plants file.
A commit message trailer `Debt-Raised: <reason>` in the range, or in --message-file, allows it, and
the reason is printed so it is seen.

    uv run python tools/ratchet.py [--staged | --commit <sha>] [--base <ref>] [--message-file <path>]
"""

import argparse
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGERS = "tools/ledgers"
CODE_DIRS = ("src", "tests", "tools")
SUPPRESSION = re.compile(
    r"#\s*(noqa|type:\s*ignore|pyrefly:\s*ignore|pyright:\s*ignore|cq-allow|pragma:\s*no cover)"
)
TRAILER = re.compile(r"^Debt-Raised:\s*(.+)$", re.MULTILINE)
type Toml = dict[str, object]
type Reader = Callable[[str], str | None]


@dataclass(frozen=True)
class Limit:
    """A value that may only move one way: the file, the dotted key, and whether it may only shrink."""

    file: str
    key: str
    only_down: bool = True


# Sets that may only shrink (lists the ratchet counts) or only grow (rules that must stay selected).
ONLY_SHRINK = (
    ("ruff.toml", "lint.ignore"),
    ("ruff.toml", "extend-exclude"),
    ("ruff.toml", "lint.per-file-ignores"),
)
ONLY_GROW = (("ruff.toml", "lint.select"), ("ruff.toml", "lint.extend-select"), ("plants.toml", "check"))
ONLY_GROW += (("plants.toml", "plant"), ("plants-hooks.toml", "check"), ("plants-hooks.toml", "plant"))
LIMITS = (
    Limit("ruff.toml", "line-length"),
    Limit("ruff.toml", "lint.mccabe.max-complexity"),
    *(Limit("ruff.toml", f"lint.pylint.{k}") for k in ("max-args", "max-positional-args", "max-branches")),
    *(Limit("ruff.toml", f"lint.pylint.{k}") for k in ("max-statements", "max-returns", "max-locals")),
    *(Limit("ruff.toml", f"lint.pylint.{k}") for k in ("max-public-methods", "max-nested-blocks")),
    *(Limit("harness.toml", f"harness.budgets.{k}") for k in ("always_loaded_bytes", "mandated_read_bytes")),
    *(
        Limit("harness.toml", f"harness.budgets.{k}")
        for k in ("doc_bytes", "description_chars", "check_stages")
    ),
    *(Limit("harness.toml", f"harness.budgets.{k}") for k in ("edit_hook_seconds", "bash_hook_seconds")),
    Limit("harness.toml", "harness.budgets.commit_hook_seconds"),
)


def git(*args: str) -> str:
    """Git's stdout for the arguments, empty when it fails."""
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    return done.stdout if done.returncode == 0 else ""


def default_base() -> str:
    """The merge base with main, or HEAD when main is not ahead of or beside this branch."""
    for candidate in ("origin/main", "main"):
        base = git("merge-base", "HEAD", candidate).strip()
        if base:
            return base
    return "HEAD"


def reader_for(ref: str | None, *, staged: bool) -> Reader:
    """A function from a repository path to its text in the base, the index, a commit or the tree."""
    if staged:
        return lambda path: git("show", f":{path}") or None
    if ref:
        return lambda path: git("show", f"{ref}:{path}") or None
    return lambda path: (ROOT / path).read_text() if (ROOT / path).exists() else None


def ledger_lines(text: str | None) -> list[str]:
    """The entries of a ledger: non-empty lines that are not comments."""
    return [line for line in (text or "").splitlines() if line.strip() and not line.startswith("#")]


def lookup(table: Toml, key: str) -> object:
    """The value at a dotted key in parsed TOML, or None."""
    node: object = table
    for part in key.split("."):
        node = node.get(part) if isinstance(node, dict) else None
    return node


def count(value: object) -> int:
    """How many entries a TOML value holds: the sum over a table of lists, else the list length."""
    if isinstance(value, dict):
        return sum(len(v) if isinstance(v, list) else 1 for v in value.values())
    return len(value) if isinstance(value, list) else 0


def toml_of(text: str | None) -> Toml:
    """Parsed TOML, or an empty table for a missing file."""
    return tomllib.loads(text) if text else {}


def ledger_problems(base: Reader, now: Reader, files: list[str]) -> list[str]:
    """Ledgers that grew, and suppression comments in code that no ledger lists."""
    problems = []
    listed: set[tuple[str, str]] = set()
    for ledger in sorted(ROOT.glob(f"{LEDGERS}/*.txt")):
        rel = str(ledger.relative_to(ROOT))
        before, after = ledger_lines(base(rel)), ledger_lines(now(rel))
        if len(after) > len(before):
            problems.append(f"{rel} grows from {len(before)} to {len(after)} entries against the base")
        listed.update((row.split("\t")[0], row.split("\t")[1]) for row in after if row.count("\t") >= 1)
    for path in files:
        text = now(path) or ""
        for number, line in enumerate(text.splitlines(), 1):
            match = SUPPRESSION.search(line)
            if match and not any(p == path and r in line for p, r in listed):
                problems.append(
                    f"{path}:{number}: suppression '{match.group(1)}' is not in any ledger under {LEDGERS}/"
                )
    return problems


def config_problems(base: Reader, now: Reader) -> list[str]:
    """Rules removed, exemptions added, limits raised or plants dropped, relative to the base."""
    problems = []
    files = ("ruff.toml", "harness.toml", "plants.toml", "plants-hooks.toml")
    tables = {f: (toml_of(base(f)), toml_of(now(f))) for f in files}
    for file, key in ONLY_SHRINK:
        before, after = (count(lookup(t, key)) for t in tables[file])
        if after > before:
            problems.append(f"{file}: {key} grows from {before} to {after} entries")
    for file, key in ONLY_GROW:
        before, after = (count(lookup(t, key)) for t in tables[file])
        if after < before:
            problems.append(f"{file}: {key} shrinks from {before} to {after} entries")
    for limit in LIMITS:
        before, after = (lookup(t, limit.key) for t in tables[limit.file])
        if isinstance(before, (int, float)) and isinstance(after, (int, float)) and after > before:
            problems.append(f"{limit.file}: {limit.key} is raised from {before} to {after}")
    return problems


def code_files(ref: str | None, *, staged: bool) -> list[str]:
    """The code files of the candidate tree, under src/, tests/ and tools/."""
    if staged or ref:
        listed = git("ls-tree", "-r", "--name-only", ref or "HEAD", *CODE_DIRS) if ref else ""
        listed = listed or git("ls-files", *CODE_DIRS)
    else:
        listed = git("ls-files", "--cached", "--others", "--exclude-standard", *CODE_DIRS)
    return [f for f in listed.split() if f.endswith((".py", ".toml", ".sh")) and not f.startswith(LEDGERS)]


def raised_reasons(base_ref: str, ref: str | None, message_file: str | None) -> list[str]:
    """Every Debt-Raised reason in the range's commit messages and in the message being written."""
    text = git("log", "--format=%B", f"{base_ref}..{ref or 'HEAD'}")
    if message_file and Path(message_file).exists():
        text += "\n" + Path(message_file).read_text()
    return TRAILER.findall(text)


def main(argv: list[str] | None = None) -> int:
    """Compare the candidate with the base; print each problem and exit 1 unless debt was raised."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="check the index instead of the working tree")
    parser.add_argument("--commit", help="check this commit instead of the working tree")
    parser.add_argument("--base", help="the ref to compare against (default: the merge base with main)")
    parser.add_argument("--message-file", help="the commit message being written, for its trailer")
    args = parser.parse_args(argv)
    base_ref = args.base or default_base()
    base, now = reader_for(base_ref, staged=False), reader_for(args.commit, staged=args.staged)
    problems = ledger_problems(base, now, code_files(args.commit, staged=args.staged)) + config_problems(
        base, now
    )
    if not problems:
        return 0
    reasons = raised_reasons(base_ref, args.commit, args.message_file)
    for problem in problems:
        print(problem)
    if reasons:
        print(f"allowed: debt raised with reason {reasons[-1]!r}")
        return 0
    print(
        'refused: debt may not grow against main; to raise it, commit with a "Debt-Raised: <reason>" trailer'
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
