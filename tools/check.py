"""Run every check `CONSTRAINTS.md` lists for a stage, one summary line each.

The constraints table is the one home of every check's command and the stages it runs at, so this
runner reads it rather than keeping a second list: a row whose command does not exist fails here,
and a row with no command is skipped and said so. Checks run in parallel; the output of each failed
one is printed after the summary.

    uv run python tools/check.py                 # the CI stage: everything that is not weekly
    uv run python tools/check.py --stage commit  # the rows whose local stage is the commit
    uv run python tools/check.py --stage push --checks-changed
    uv run python tools/check.py --list
"""

import argparse
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTRAINTS = ROOT / "CONSTRAINTS.md"
COMMAND = re.compile(r"`([^`]+)`")
STAGES = ("edit", "stop", "commit", "commit-msg", "push", "ci", "weekly")
# Rows whose "Runs at" cell says they run at push only when a check changed.
CONDITIONAL = "when a check changes"
COLUMNS = 5  # Dimension | Rule | Checked by | Runs at | Status


@dataclass(frozen=True)
class Row:
    """One row of the constraints table: a dimension, its command, its stages and its status."""

    dimension: str
    command: str | None
    runs_at: str
    status: str

    def runs_at_stage(self, stage: str, *, checks_changed: bool) -> bool:
        """Whether this row belongs to the stage; weekly rows only to the weekly stage."""
        cell = self.runs_at.lower()
        if stage == "push" and CONDITIONAL in cell:
            return checks_changed
        if "weekly" in cell and stage != "weekly":
            return False
        return stage in re.findall(r"[a-z][a-z-]*", cell)


def rows(text: str) -> list[Row]:
    """The rows of the table under "Enforced with commands", in order."""
    section = text.split("## Enforced with commands", 1)[1].split("\n## ", 1)[0]
    out = []
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != COLUMNS or cells[0] in {"Dimension", "---"}:
            continue
        dimension, _rule, checked_by, runs_at, status = cells
        found = COMMAND.findall(checked_by)
        # A built row names exactly one command; prose with stray backticks is not a command.
        command = found[0] if len(found) == 1 and status != "to build" else None
        out.append(Row(dimension, command, runs_at, status))
    return out


@dataclass(frozen=True)
class Result:
    """What one check did: its row, whether it passed, how long it took, and its output."""

    row: Row
    ok: bool
    seconds: float
    output: str


def run_row(row: Row) -> Result:
    """Run one row's command with sh from the repository root."""
    start = time.perf_counter()
    done = subprocess.run(
        ["sh", "-c", str(row.command)],
        cwd=ROOT,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    return Result(row, done.returncode == 0, time.perf_counter() - start, done.stdout + done.stderr)


def summary_line(result: Result) -> str:
    """One line: the verdict, the seconds and the dimension."""
    return f"{'ok  ' if result.ok else 'FAIL'}  {result.seconds:5.1f}s  {result.row.dimension}"


def main(argv: list[str] | None = None) -> int:
    """Run the stage's checks in parallel and report; exit 1 when any fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=STAGES, default="ci")
    parser.add_argument("--checks-changed", action="store_true", help="include the conditional push rows")
    parser.add_argument("--list", action="store_true", help="print the stage's commands and exit")
    args = parser.parse_args(argv)
    table = rows(CONSTRAINTS.read_text())
    chosen = [r for r in table if r.runs_at_stage(args.stage, checks_changed=args.checks_changed)]
    runnable = [r for r in chosen if r.command]
    for row in chosen:
        if not row.command:
            print(f"skip         {row.dimension} ({row.status}: no command yet)")
    if args.list:
        for row in runnable:
            print(f"{row.dimension}: {row.command}")
        return 0
    with ThreadPoolExecutor(max_workers=max(4, os.cpu_count() or 4)) as pool:
        results = list(pool.map(run_row, runnable))
    for result in results:
        print(summary_line(result))
    failed = [r for r in results if not r.ok]
    for result in failed:
        print(f"\n--- {result.row.dimension}: {result.row.command}\n{result.output.rstrip()}")
    print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed, stage {args.stage}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
