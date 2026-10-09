"""The pre-push review check: every reviewer has reported on the covered paths that changed.

For each reviewer in tools/reviewers.toml, the paths it covers that changed since the base (the
remote's commit, or the merge base with main) must be covered by a current report under
.harness/reviews/, written by tools/review_report.py and keyed by a hash of the covered files'
content. A report with flags passes and the flags are printed: reviewers flag, they do not block.
Only a missing or stale report refuses the push.

    uv run python tools/review_check.py [--base <ref>]
    uv run python tools/review_check.py --state <reviewer>   # print the covered-state hash
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWERS = ROOT / "tools/reviewers.toml"
REPORTS = ROOT / ".harness/reviews"
SHOWN = 4  # changed paths named in a refusal before "..."


@dataclass(frozen=True)
class Reviewer:
    """One reviewer: its name, its question and the path patterns it covers."""

    name: str
    question: str
    paths: tuple[str, ...]

    def covers(self, path: str) -> bool:
        """Whether a repository path is under this reviewer's cover."""
        return any(pattern(p).match(path) for p in self.paths)


def pattern(glob: str) -> re.Pattern[str]:
    """A glob as a regex: `**` crosses directories, `*` does not."""
    parts = [
        ".*" if piece == "**" else re.escape(piece).replace(r"\*", "[^/]*")
        for piece in re.split(r"(\*\*)", glob)
    ]
    return re.compile("^" + "".join(parts) + "$")


def git(*args: str) -> str:
    """Git's stdout for the arguments, empty when it fails."""
    done = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    return done.stdout if done.returncode == 0 else ""


def reviewers() -> list[Reviewer]:
    """The reviewers the table declares."""
    rows = tomllib.loads(REVIEWERS.read_text()).get("reviewer", [])
    return [Reviewer(str(r["name"]), str(r["question"]), tuple(str(p) for p in r["paths"])) for r in rows]


def default_base() -> str:
    """The remote's commit for this branch, else the merge base with main, else HEAD."""
    for candidate in ("@{upstream}", "origin/main", "main"):
        base = git("merge-base", "HEAD", candidate).strip()
        if base:
            return base
    return "HEAD"


def changed_since(base: str) -> set[str]:
    """Paths changed in commits since the base, plus uncommitted and untracked changes."""
    committed = git("diff", "--name-only", base, "HEAD").split()
    pending = [line[3:] for line in git("status", "--porcelain", "--untracked-files=all").splitlines()]
    return {p.split(" -> ")[-1] for p in committed + pending}


def covered_state(reviewer: Reviewer) -> str:
    """A hash of the content of every file under the reviewer's cover, as it is in the working tree."""
    tracked = git("ls-files", "--cached", "--others", "--exclude-standard").split()
    covered = sorted(p for p in tracked if reviewer.covers(p) and (ROOT / p).is_file())
    lines = [f"{path} {git('hash-object', path).strip()}" for path in covered]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def report_for(reviewer: Reviewer) -> dict[str, object] | None:
    """The reviewer's report, when one exists and parses."""
    path = REPORTS / f"{reviewer.name}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def verdict(reviewer: Reviewer, changed: set[str]) -> tuple[bool, str]:
    """Whether the reviewer's cover is satisfied for the changes, and the line to print."""
    touched = sorted(p for p in changed if reviewer.covers(p))
    if not touched:
        return True, f"ok    {reviewer.name}: nothing under its cover changed"
    report = report_for(reviewer)
    state = covered_state(reviewer)
    if report is None or report.get("covered") != state:
        shown = ", ".join(touched[:SHOWN]) + (" ..." if len(touched) > SHOWN else "")
        why = "no current report" if report is None else "its report predates a change under its cover"
        return False, (
            f"FAIL  {reviewer.name}: {len(touched)} changed path(s) under its cover ({shown}) and {why}. "
            f"Run the {reviewer.name}-reviewer agent; it ends by running: "
            f"uv run python tools/review_report.py {reviewer.name}"
        )
    raw = report.get("flags", [])
    flags = [f for f in raw if isinstance(f, str)] if isinstance(raw, list) else []
    head = f"ok    {reviewer.name}: report {state[:10]} covers {len(touched)} path(s), {len(flags)} flag(s)"
    return True, "\n".join([head, *(f"      flag: {f}" for f in flags)])


def main(argv: list[str] | None = None) -> int:
    """Check every reviewer against the changes since the base; exit 1 when a report is missing or stale."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="the ref to compare against (default: the remote's commit)")
    parser.add_argument("--state", metavar="REVIEWER", help="print the covered-state hash for one reviewer")
    args = parser.parse_args(argv)
    table = reviewers()
    if args.state:
        chosen = [r for r in table if r.name == args.state]
        if not chosen:
            print(f"no reviewer named {args.state!r} in {REVIEWERS.relative_to(ROOT)}")
            return 1
        print(covered_state(chosen[0]))
        return 0
    changed = changed_since(args.base or default_base())
    results = [verdict(r, changed) for r in table]
    for _, line in results:
        print(line)
    return 0 if all(ok for ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
