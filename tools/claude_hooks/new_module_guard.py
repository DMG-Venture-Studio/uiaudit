"""PreToolUse on Write: refuse a new file whose path is not on the closed lists, and show the layout.

Every module's path is a noun or a fixed package, and a role, from `project-spec.toml`; a test sits
at `tests/<noun>/test_<role>.py` or `tests/test_<name>.py`; a migration is `migrations/NNNN_<slug>.sql`;
a new top-level directory needs a deployable. A Write to a file that already exists is not this
hook's business (serial-build guards the generated ones). Exit 2 blocks the call and shows the layout.
Reads the hook's JSON from stdin; anything unreadable is allowed, so a bug here never blocks.
"""

import json
import os
import re
import sys
import tomllib
from pathlib import Path

ROLES = ("ops", "render", "rules", "store", "model")
KERNEL = ("principals", "envelope", "errors", "resources", "ids", "clock")
ROOTS = {
    "src",
    "tests",
    "tools",
    "docs",
    "migrations",
    "web",
    ".claude",
    ".github",
    "claude_outputs",
    ".harness",
}
MIGRATION = re.compile(r"^\d{4}_[a-z0-9_]+\.sql$")
FIXED_TESTED = {"kernel", "catalog", "flows", "adapters", "surfaces"}
MODULE, FOLDER_MODULE = 2, 3  # parts in <package>/<member>.py and <noun>/<role>/<name>.py
type Spec = dict[str, object]


def tables(spec: Spec, key: str) -> list[dict[str, object]]:
    """The array of tables at a spec key, empty when absent."""
    value = spec.get(key, [])
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def spec_lists(spec: Spec) -> dict[str, list[str]]:
    """The closed lists the spec declares: nouns, flows, adapters, surfaces, and each noun's roles."""
    nouns = tables(spec, "nouns")
    surfaces = spec.get("surfaces", {})
    return {
        "nouns": [str(n["name"]) for n in nouns],
        "flows": [str(f["name"]) for f in tables(spec, "flows")],
        "adapters": [str(a["name"]) for a in tables(spec, "adapters")],
        "surfaces": [k for k, v in surfaces.items() if v] if isinstance(surfaces, dict) else [],
        **{f"roles:{n['name']}": roles_of(n) for n in nouns},
    }


def roles_of(noun: dict[str, object]) -> list[str]:
    """The roles a noun declares, or every role when it declares none."""
    declared = noun.get("roles")
    return [str(r) for r in declared] if isinstance(declared, list) else list(ROLES)


def _module_allowed(parts: tuple[str, ...], lists: dict[str, list[str]]) -> bool:
    """Whether a path under src/uiaudit/ is on the closed lists."""
    if len(parts) == 1:
        return parts[0] in {"__init__.py", "__main__.py", "boot.py", "py.typed"}
    package, member = parts[0], parts[1]
    stem = member.removesuffix(".py")
    if package in lists["nouns"]:
        roles = lists[f"roles:{package}"]
        if len(parts) == MODULE:
            return member == "__init__.py" or (member.endswith(".py") and stem in roles)
        return parts[1] in roles and len(parts) == FOLDER_MODULE and parts[2].endswith(".py")
    fixed = {"kernel": KERNEL, "catalog": ("index",), "flows": lists["flows"]}
    fixed.update({"adapters": lists["adapters"], "surfaces": lists["surfaces"]})
    allowed = fixed.get(package)
    return allowed is not None and len(parts) == MODULE and (member == "__init__.py" or stem in allowed)


def _test_allowed(parts: tuple[str, ...], lists: dict[str, list[str]]) -> bool:
    """Whether a path under tests/ follows tests/<noun>/test_<role>.py or tests/test_<name>.py."""
    if parts[0] == "fixtures":
        return True
    if len(parts) == 1:
        return parts[0] == "conftest.py" or bool(re.match(r"^test_[a-z0-9_]+\.py$", parts[0]))
    if len(parts) != MODULE or parts[1] == "__init__.py":
        return False
    group, name = parts
    if group in lists["nouns"]:
        return name == "conftest.py" or name in {f"test_{r}.py" for r in lists[f"roles:{group}"]}
    return group in FIXED_TESTED and name.startswith("test_")


def allowed(rel: Path, lists: dict[str, list[str]]) -> bool:
    """Whether a new file at this project-relative path is on the closed lists."""
    root, *rest = rel.parts
    if root == "src":
        return len(rest) > 1 and rest[0] == "uiaudit" and _module_allowed(tuple(rest[1:]), lists)
    if root == "tests":
        return bool(rest) and _test_allowed(tuple(rest), lists)
    if root == "migrations":
        return len(rest) == 1 and bool(MIGRATION.match(rest[0]))
    return not rest or root in ROOTS


def layout(lists: dict[str, list[str]]) -> str:
    """The closed lists, shown so the session can place the file or change the spec first."""
    nouns = ", ".join(f"{n} ({'/'.join(lists[f'roles:{n}'])})" for n in lists["nouns"])
    fixed = ", ".join(
        f"{package}/{{{','.join(members)}}}.py"
        for package, members in (
            ("kernel", KERNEL),
            ("catalog", ("index",)),
            ("flows", lists["flows"]),
            ("adapters", lists["adapters"]),
            ("surfaces", lists["surfaces"]),
        )
    )
    return (
        f"Nouns and their roles: {nouns}. Module paths: src/uiaudit/<noun>/<role>.py, or <role>/<name>.py"
        f" once a role grows into a folder. Fixed packages: {fixed}, boot.py, __main__.py."
        " Tests: tests/<noun>/test_<role>.py, tests/test_<name>.py, tests/fixtures/."
        " Migrations: migrations/NNNN_<slug>.sql. A new noun, role, flow, adapter or surface is a change to"
        " project-spec.toml first, with a decision record; a new top-level directory needs a deployable."
    )


def main() -> int:
    """Read the Write from stdin; exit 2 with the layout on stderr when the new path is off the lists."""
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd()).resolve()
    try:
        payload = json.load(sys.stdin)
        target = Path(str(payload.get("tool_input", {}).get("file_path", ""))).resolve()
    except (json.JSONDecodeError, AttributeError):
        return 0
    if not str(target) or target.exists() or not target.is_relative_to(root):
        return 0
    rel = target.relative_to(root)
    lists = spec_lists(tomllib.loads((root / "project-spec.toml").read_text()))
    if allowed(rel, lists):
        return 0
    sys.stderr.write(f"Refusing to create {rel}: its path is not on the closed lists.\n{layout(lists)}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
