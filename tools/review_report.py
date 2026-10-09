"""Record a reviewer's report so the pre-push review check can require it.

The reviewer agent ends by piping its report into this script. The report is kept under
.harness/reviews/<reviewer>.json, keyed by the hash of the covered files' content at the time, so
it stays valid until a file under the reviewer's cover changes. Lines that start with `FLAG:` are
the reviewer's flags; the review check prints them at push and lets the push through.

    uv run python tools/review_report.py <reviewer> < report.md
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / ".harness/reviews"
CHECK = ROOT / "tools/review_check.py"


def covered_state(reviewer: str) -> str:
    """The covered-state hash the review check computes for this reviewer right now."""
    done = subprocess.run(
        [sys.executable, str(CHECK), "--state", reviewer],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode:
        sys.stderr.write(done.stdout + done.stderr)
        sys.exit(1)
    return done.stdout.strip()


def main(argv: list[str]) -> int:
    """Write the report read from stdin for the named reviewer."""
    if len(argv) != 1:
        sys.stderr.write("usage: review_report.py <reviewer> < report\n")
        return 2
    reviewer, body = argv[0], sys.stdin.read()
    flags = [line.removeprefix("FLAG:").strip() for line in body.splitlines() if line.startswith("FLAG:")]
    report = {
        "reviewer": reviewer,
        "head": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout.strip(),
        "covered": covered_state(reviewer),
        "written_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "flags": flags,
        "body": body,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{reviewer}.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"recorded {path.relative_to(ROOT)}: {len(flags)} flag(s), covered state {report['covered'][:10]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
