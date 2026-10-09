"""The MCP legibility check: what a cold client receives on connect names an entry point.

Runs mcp-legibility's static probe (`probe_connect.py --repo . --json`), which reads the FastMCP
constructor from source, including an `instructions=` block held in a constant, and refuses when
the block is missing or names no entry-point tool. The probe is taken from the installed plugin
when present, else fetched once at a pinned commit into a cache directory, so CI needs no plugin.

    uv run python tools/mcp_legibility.py
"""

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_GLOB = (
    ".claude/plugins/cache/mcp-legibility/mcp-legibility/*/skills/legibility-audit/scripts/probe_connect.py"
)
PINNED = "f9c5cb3d50d08ca5ddc2218eb8d685c5ec27a1fd"
URL = f"https://raw.githubusercontent.com/DMG-Venture-Studio/mcp-legibility/{PINNED}/skills/legibility-audit/scripts/probe_connect.py"
CACHE = (
    Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    / "uiaudit"
    / f"probe_connect-{PINNED[:10]}.py"
)
REFUSALS = ("NO `instructions=` BLOCK", "names no ENTRY POINT")


def probe_path() -> Path:
    """The probe script: from the environment, the installed plugin, the cache, or a pinned download."""
    explicit = os.environ.get("MCP_LEGIBILITY_PROBE")
    if explicit:
        return Path(explicit)
    installed = sorted(Path.home().glob(PLUGIN_GLOB))
    if installed:
        return installed[-1]
    if not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(URL, timeout=30) as response:
            CACHE.write_bytes(response.read())
    return CACHE


def main() -> int:
    """Run the probe on this repository; print the instructions and exit 1 on a connect-axis refusal."""
    probe = probe_path()
    done = subprocess.run(
        [sys.executable, "-I", str(probe), "--repo", str(ROOT), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode:
        print(f"the probe refused: {done.stderr.strip() or done.stdout.strip()}")
        return 1
    report = json.loads(done.stdout)
    surface, findings = report["surface"], report["findings"]
    problems = [f for f in findings if any(r in f for r in REFUSALS)]
    server = Path(surface["server_file"]).relative_to(ROOT)
    state = "present" if surface["instructions"] else "missing"
    print(f"{server}: instructions {state}, {len(surface['tools'])} static tools")
    for problem in problems:
        print(f"mcp legibility: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
