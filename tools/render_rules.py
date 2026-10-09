"""Render the path-scoped agent rules from the spec and the module docstrings, or check them for drift.

One rule file per noun and per fixed package under `.claude/rules/`, each scoped by `paths:` so it
loads only when a session touches that package. The content is what the spec declares (purpose,
operations, dependencies, roles) and what each module says it is, in its own docstring, with what
it may import. Rendered, never hand-kept: a hand edit is lost on the next render, and a docstring
that lies shows up here.

    uv run python tools/render_rules.py           # write .claude/rules/noun-*.md and tier-*.md
    uv run python tools/render_rules.py --check   # fail when any rule is out of date or stale
"""

import ast
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "project-spec.toml"
PACKAGE = ROOT / "src/uiaudit"
RULES = ROOT / ".claude/rules"
ROLES = ("ops", "render", "rules", "store", "model")
KERNEL = ("principals", "envelope", "errors", "resources", "ids", "clock")
FOOTER = (
    "Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings;"
    " never edited by hand."
)
type Table = dict[str, object]
type Row = tuple[str, str, str, str]


def tables(spec: Table, key: str) -> list[Table]:
    """The array of tables at a spec key, empty when absent."""
    value = spec.get(key, [])
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def strings(table: Table, key: str, default: tuple[str, ...] = ()) -> list[str]:
    """The list of strings at a key, or the default when the key is absent."""
    value = table.get(key)
    return [str(v) for v in value] if isinstance(value, list) else list(default)


def docstring(path: Path) -> str:
    """The first line of a module's docstring, or a note that the module does not exist yet."""
    if not path.exists():
        return "(not built yet)"
    doc = ast.get_docstring(ast.parse(path.read_text())) or ""
    return doc.splitlines()[0] if doc else "(no docstring)"


def frontmatter(paths: list[str]) -> str:
    """The `paths:` block that scopes a rule to its package."""
    return "---\npaths:\n" + "".join(f'  - "{p}"\n' for p in paths) + "---\n\n"


def rows(table: list[Row]) -> str:
    """A markdown table of role, module, what it is, and what it may import."""
    lines = ["| Role | Module | What it is | May import |", "|---|---|---|---|"]
    lines += [f"| {role} | `{module}` | {what} | {imports} |" for role, module, what, imports in table]
    return "\n".join(lines) + "\n"


def page(paths: list[str], title: str, *paragraphs: str) -> str:
    """One rule file: its scope, its title, its paragraphs and the footer."""
    return frontmatter(paths) + f"# {title}\n\n" + "\n\n".join(paragraphs) + f"\n\n{FOOTER}\n"


def noun_rows(name: str, roles: list[str], depends: list[str]) -> list[Row]:
    """One row per declared role, top to bottom, with what each may import."""
    ordered = [r for r in ROLES if r in roles]
    out: list[Row] = []
    for i, role in enumerate(ordered):
        below = ", ".join(ordered[i + 1 :]) or "nothing in this noun"
        reach = [f"`{d}.ops` and `{d}.model`" if role == "ops" else f"`{d}.model`" for d in depends]
        imports = "; ".join([f"{below}; the kernel", *reach])
        out.append((role, f"src/uiaudit/{name}/{role}.py", docstring(PACKAGE / name / f"{role}.py"), imports))
    return out


def noun_rule(noun: Table, nouns: list[Table]) -> str:
    """The rule for one noun: its purpose, operations, dependencies and roles."""
    name, roles, depends = str(noun["name"]), strings(noun, "roles", ROLES), strings(noun, "depends_on")
    others = ", ".join(str(n["name"]) for n in nouns if n["name"] != name and str(n["name"]) not in depends)
    return page(
        [f"src/uiaudit/{name}/**", f"tests/{name}/**"],
        f"{name}, a noun",
        str(noun["purpose"]),
        f"Operations: {', '.join(strings(noun, 'operations'))}. Each is one function in `ops`, declared"
        " once in the catalog; a surface is a projection of that declaration.",
        f"Depends on: {', '.join(depends) or 'no other noun'}. Never imports {others} or an adapter: an"
        " outside service arrives as a resource the catalog hands in.",
        rows(noun_rows(name, roles, depends)),
        "Roles it does not declare are not created; a new role is added to this noun's `roles` in the spec"
        f" first. Tests: `tests/{name}/test_<role>.py`.",
    )


def tier_rules(spec: Table) -> dict[str, str]:
    """The rule for each fixed package: what it holds, module by module, and what it may import."""
    nouns = [str(n["name"]) for n in tables(spec, "nouns")]
    flows, adapters = tables(spec, "flows"), tables(spec, "adapters")
    surfaces_table = spec.get("surfaces")
    surfaces = [k for k, v in surfaces_table.items() if v] if isinstance(surfaces_table, dict) else []
    kernel: list[Row] = [
        (
            "kernel",
            f"src/uiaudit/kernel/{m}.py",
            docstring(PACKAGE / "kernel" / f"{m}.py"),
            "the standard library",
        )
        for m in KERNEL
    ]
    flow_rows: list[Row] = [
        (
            "flow",
            f"src/uiaudit/flows/{f['name']}.py",
            f"{f['purpose']} Calls {', '.join(strings(f, 'uses'))}.",
            "the catalog, nouns' `model`, the kernel",
        )
        for f in flows
    ]
    adapter_rows: list[Row] = [
        (
            "adapter",
            f"src/uiaudit/adapters/{a['name']}.py",
            (
                f"{docstring(PACKAGE / 'adapters' / f'{a["name"]}.py')} Wraps `{a['wraps']}`,"
                f" implements `{a['implements']}`."
            ),
            "the kernel; the wrapped package inside the one function that needs it",
        )
        for a in adapters
    ]
    surface_rows: list[Row] = [
        (
            "surface",
            f"src/uiaudit/surfaces/{s}.py",
            docstring(PACKAGE / "surfaces" / f"{s}.py"),
            "boot, the catalog, the kernel, a noun's `model` for types",
        )
        for s in surfaces
    ]
    boot_rows: list[Row] = [
        ("boot", "src/uiaudit/boot.py", docstring(PACKAGE / "boot.py"), "the adapters, the kernel"),
        ("entry", "src/uiaudit/__main__.py", docstring(PACKAGE / "__main__.py"), "the surfaces"),
    ]
    return {
        "tier-kernel": page(
            ["src/uiaudit/kernel/**", "tests/kernel/**"],
            "kernel, the floor",
            "Principals, the result envelope, errors, the resource protocols, ids and the clock. Its member"
            f" list is closed: {', '.join(KERNEL)}. It imports nothing of this project.",
            rows(kernel),
        ),
        "tier-catalog": page(
            ["src/uiaudit/catalog/**", "tests/catalog/**"],
            "catalog, the index of operations",
            docstring(PACKAGE / "catalog/index.py"),
            "Every operation enters here when its slice is built, with its grant, effect, resources and"
            " surfaces; the catalog is the only module above the nouns that imports a noun's `ops`."
            " May import: every noun's `ops` and `model`, the kernel.",
        ),
        "tier-flows": page(
            ["src/uiaudit/flows/**", "tests/flows/**"],
            "flows, use cases across nouns",
            "One module per flow, calling operations through the catalog, never a noun's `ops` directly."
            f" Flows declared: {', '.join(str(f['name']) for f in flows)}.",
            rows(flow_rows),
        ),
        "tier-adapters": page(
            ["src/uiaudit/adapters/**", "tests/adapters/**"],
            "adapters, one outside service each",
            "Each implements a protocol from `kernel/resources.py`; boot builds it once and the catalog hands"
            " it to the operations that name it. No noun imports an adapter."
            f" Adapters declared: {', '.join(str(a['name']) for a in adapters)}.",
            rows(adapter_rows),
        ),
        "tier-surfaces": page(
            ["src/uiaudit/surfaces/**", "tests/surfaces/**", "docs/api/**"],
            "surfaces, the ways in",
            "Each is a projection of the catalog with no logic of its own; nothing imports a surface but"
            f" `__main__`, and surfaces never import each other. Surfaces declared: {', '.join(surfaces)}."
            " The committed projections under `docs/api/` are rendered by `tools/render_surfaces.py`.",
            rows(surface_rows),
        ),
        "tier-boot": page(
            ["src/uiaudit/boot.py", "src/uiaudit/__main__.py"],
            "boot, the composition root",
            "The one place adapters are built and handed to the catalog as resources."
            f" Nouns: {', '.join(nouns)}.",
            rows(boot_rows),
        ),
    }


def renders() -> dict[Path, str]:
    """Every rule file and the text the spec and docstrings render for it now."""
    spec = tomllib.loads(SPEC.read_text())
    nouns = tables(spec, "nouns")
    out = {RULES / f"noun-{n['name']}.md": noun_rule(n, nouns) for n in nouns}
    out.update({RULES / f"{name}.md": text for name, text in tier_rules(spec).items()})
    return out


def main(argv: list[str]) -> int:
    """Write the rules, or with --check report each one that is out of date or stale."""
    check = "--check" in argv
    wanted = renders()
    stale = [p for p in [*RULES.glob("noun-*.md"), *RULES.glob("tier-*.md")] if p not in wanted]
    outdated = [p for p, text in wanted.items() if (p.read_text() if p.exists() else None) != text]
    if not check:
        for path in outdated:
            path.write_text(wanted[path])
            print(f"wrote {path.relative_to(ROOT)}")
        for path in stale:
            path.unlink()
            print(f"removed {path.relative_to(ROOT)}")
        return 0
    for path in outdated:
        print(
            f"out of date: {path.relative_to(ROOT)} is not the render of the spec and the module docstrings"
        )
    for path in stale:
        print(f"stale: {path.relative_to(ROOT)} names nothing in the spec")
    if outdated or stale:
        print("run: uv run python tools/render_rules.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
