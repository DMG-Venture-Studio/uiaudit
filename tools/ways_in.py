"""Refuse a way in that is not a declared surface: a main guard, a load by name or path, `python -m`.

The surfaces under `src/uiaudit/surfaces/` and `__main__.py` are the only places a process starts or
a module is chosen at run time; everywhere else those are hidden entry points the import contracts
cannot see. The reader resolves import aliases, so `import importlib as il; il.import_module(...)`
is caught, and a main guard is caught in any spelling that mentions `__name__` in a condition.
`[project.scripts]` in pyproject.toml must point into the surfaces too.

    uv run python tools/ways_in.py
"""

import ast
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src/uiaudit"
SURFACES = PACKAGE / "surfaces"
ALLOWED_FILES = {PACKAGE / "__main__.py"}
LOADERS = ("importlib", "runpy")
LOADER_BUILTINS = {"__import__", "exec", "eval", "compile"}
PYTHON_M = re.compile(r"\bpython[\d.]*\s+-m\b|^-m$")
SCRIPT_PREFIX = "uiaudit.surfaces."


def aliases(tree: ast.Module) -> dict[str, str]:
    """Every imported name in the module and the dotted name it stands for."""
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update({(a.asname or a.name.split(".")[0]): a.name for a in node.names})
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.update({(a.asname or a.name): f"{node.module}.{a.name}" for a in node.names})
    return out


def dotted(node: ast.expr, names: dict[str, str]) -> str:
    """The dotted name an expression refers to, aliases resolved; empty when it is not a name."""
    if isinstance(node, ast.Name):
        return names.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        head = dotted(node.value, names)
        return f"{head}.{node.attr}" if head else ""
    return ""


def main_guard(node: ast.AST) -> bool:
    """Whether a condition or a match subject reads `__name__`: a main guard in any spelling."""
    test = (
        node.test
        if isinstance(node, (ast.If, ast.IfExp))
        else node.subject
        if isinstance(node, ast.Match)
        else None
    )
    return test is not None and any(isinstance(n, ast.Name) and n.id == "__name__" for n in ast.walk(test))


def _loader_call(node: ast.Call, names: dict[str, str]) -> str | None:
    """The loader a call reaches, if it loads code by name or path."""
    target = dotted(node.func, names)
    if target in LOADER_BUILTINS or target.split(".")[0] in LOADERS:
        return target
    return None


def _python_m(node: ast.Constant) -> bool:
    """Whether a literal spells `python -m`, in a string or as the `-m` item of a command list."""
    return isinstance(node.value, str) and bool(PYTHON_M.search(node.value))


def problems_in(path: Path) -> list[str]:
    """Each hidden way in found in one module, as `path:line: what`."""
    tree = ast.parse(path.read_text())
    names = aliases(tree)
    rel = path.relative_to(ROOT)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp, ast.Match)) and main_guard(node):
            found.append(f"{rel}:{node.lineno}: main guard outside the surfaces")
        elif isinstance(node, ast.Call) and (loader := _loader_call(node, names)):
            found.append(f"{rel}:{node.lineno}: load by name or path through {loader} outside the surfaces")
        elif isinstance(node, ast.Constant) and _python_m(node):
            found.append(f"{rel}:{node.lineno}: python -m outside the surfaces")
        elif isinstance(node, ast.Attribute) and dotted(node, names) == "sys.argv":
            found.append(f"{rel}:{node.lineno}: reads sys.argv outside the surfaces")
    return found


def script_problems() -> list[str]:
    """Console scripts in pyproject.toml that do not point into the surfaces."""
    scripts = tomllib.loads((ROOT / "pyproject.toml").read_text()).get("project", {}).get("scripts", {})
    return [
        f"pyproject.toml: script {name} = {target!r} is a way in outside {SCRIPT_PREFIX}"
        for name, target in scripts.items()
        if not str(target).startswith(SCRIPT_PREFIX)
    ]


def main() -> int:
    """Read every module outside the surfaces; print each hidden way in and exit 1 when any."""
    files = [p for p in sorted(PACKAGE.rglob("*.py")) if SURFACES not in p.parents and p not in ALLOWED_FILES]
    found = [problem for path in files for problem in problems_in(path)] + script_problems()
    for problem in found:
        print(problem)
    if found:
        print("A way in is a declared surface under src/uiaudit/surfaces/; see docs/tech/conventions.md.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
