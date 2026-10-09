"""SessionStart: say when the git hooks are off or the tool environment is missing. Never blocks.

Stdout becomes session context, so a warning here is read before the first edit. Without it a
clone whose `core.hooksPath` is unset commits past every git hook without a word.
"""

import os
import subprocess
import sys
from pathlib import Path

HOOKS_PATH = "tools/git_hooks"


def hooks_path(root: Path) -> str:
    """The clone's core.hooksPath, empty when unset or outside a repository."""
    done = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"], cwd=root, capture_output=True, text=True, check=False
    )
    return done.stdout.strip()


def main() -> int:
    """Print each warning that applies; always exit 0."""
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    if hooks_path(root).rstrip("/") != HOOKS_PATH:
        print(
            f"uiaudit: git hooks are off in this clone (core.hooksPath is not {HOOKS_PATH}); run: make setup"
        )
    if not (root / ".venv").is_dir():
        print("uiaudit: the tool environment is missing; run: uv sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
