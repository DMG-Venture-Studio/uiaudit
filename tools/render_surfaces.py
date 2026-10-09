"""Render the committed record of each surface from the catalog, or check that it has not drifted.

The OpenAPI document, the MCP tool list and the CLI help are projections of the operation catalog.
They are committed so a reviewer, a client generator and a cold agent can read them without running
the code, and this check refuses a commit where the committed copy no longer matches the code.

    uv run python tools/render_surfaces.py           # write docs/api/*
    uv run python tools/render_surfaces.py --check   # fail when any committed copy is out of date
"""

import json
import sys
from pathlib import Path

from uiaudit.surfaces import cli, http, mcp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/api"


def renders() -> dict[Path, str]:
    """Each committed file and the text the catalog renders for it now."""
    return {
        OUT / "openapi.json": json.dumps(http.openapi(), indent=2) + "\n",
        OUT / "mcp-tools.json": json.dumps(mcp.tool_list(), indent=2) + "\n",
        OUT / "cli-help.txt": cli.help_text(),
    }


def main(argv: list[str]) -> int:
    """Write the renders, or with --check report each file that differs from its render."""
    check = "--check" in argv
    stale = []
    for path, text in renders().items():
        current = path.read_text() if path.exists() else None
        if current == text:
            continue
        if check:
            stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            print(f"wrote {path.relative_to(ROOT)}")
    if stale:
        names = ", ".join(str(p) for p in stale)
        fix = "uv run python tools/render_surfaces.py"
        sys.stderr.write(f"out of date: {names} is not the render of the catalog; run: {fix}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
