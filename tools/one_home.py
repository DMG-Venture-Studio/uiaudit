"""Refuse a literal with two homes: bound to constants in two modules, or spelled out where one names it.

A value that matters gets one module-level constant, and every other module imports it. The check
walks the package: every UPPER_CASE module-level name bound to a literal is a home; the same literal
bound in a second module, or written out anywhere as a bare literal, is refused with both places.
Small values (short strings, 0, 1, 2, flags) are not worth a home and are ignored.

    uv run python tools/one_home.py [package dir, default src/uiaudit]
"""

import ast
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_STRING = 3
SMALL_INTS = {-1, 0, 1, 2}
type Literal = str | int | float | bytes | tuple["Literal", ...]


@dataclass(frozen=True)
class Home:
    """Where a literal is bound to a constant: the module, the name and the line."""

    module: str
    name: str
    line: int


def worth_a_home(value: object) -> bool:
    """Whether a literal is big enough that a second copy is a second home."""
    if isinstance(value, bool) or value is None:
        return False
    if isinstance(value, str):
        return len(value) >= MIN_STRING
    if isinstance(value, int):
        return value not in SMALL_INTS
    if isinstance(value, tuple):
        return bool(value) and all(worth_a_home(v) or isinstance(v, (str, int)) for v in value)
    return isinstance(value, (float, bytes))


def literal_of(node: ast.expr) -> Literal | None:
    """The literal a constant expression holds, or None when it is not a plain literal."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bytes)):
        return node.value
    if isinstance(node, ast.Tuple):
        items: list[Literal] = []
        for element in node.elts:
            item = literal_of(element)
            if item is None:
                return None
            items.append(item)
        return tuple(items)
    return None


def constant_bindings(tree: ast.Module, module: str) -> dict[Literal, Home]:
    """Module-level UPPER_CASE names bound to a literal worth a home, keyed by the literal."""
    out: dict[Literal, Home] = {}
    for node in tree.body:
        target = node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None
        target = node.target if isinstance(node, ast.AnnAssign) else target
        value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
        if not (isinstance(target, ast.Name) and target.id.isupper() and value is not None):
            continue
        literal = literal_of(value)
        if literal is not None and worth_a_home(literal):
            out[literal] = Home(module, target.id, node.lineno)
    return out


def _skipped(tree: ast.Module) -> set[int]:
    """Ids of nodes whose literals are not values: annotations, docstrings, f-string pieces, bindings."""
    skip: set[int] = set()
    for node in ast.walk(tree):
        parts: list[ast.AST | None] = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parts = [node.returns, *[a.annotation for a in node.args.args + node.args.kwonlyargs]]
        elif isinstance(node, (ast.AnnAssign, ast.arg)):
            parts = [node.annotation]
        elif isinstance(node, ast.JoinedStr):
            parts = list(node.values)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            parts = [node.value]  # a docstring or a bare string statement
        for part in parts:
            skip.update(id(n) for n in ast.walk(part)) if part is not None else None
    return skip


def spelled_out(tree: ast.Module) -> list[tuple[Literal, int]]:
    """Every literal worth a home written out in the module as a value, with its line."""
    skip = _skipped(tree)
    bound = {id(n.value) for n in tree.body if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value}
    return [
        (node.value, node.lineno)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and id(node) not in skip
        and id(node) not in bound
        and isinstance(node.value, (str, int, float, bytes))
        and worth_a_home(node.value)
    ]


def check(package: Path) -> list[str]:
    """The problems in a package: a literal with two constant homes, or spelled out where one names it."""
    files = sorted(p for p in package.rglob("*.py"))
    trees = {str(p.relative_to(ROOT)): ast.parse(p.read_text()) for p in files}
    homes: dict[Literal, list[Home]] = defaultdict(list)
    for module, tree in trees.items():
        for literal, home in constant_bindings(tree, module).items():
            homes[literal].append(home)
    problems = []
    for literal, places in homes.items():
        if len({h.module for h in places}) > 1:
            where = " and ".join(f"{h.module}:{h.line} ({h.name})" for h in places)
            problems.append(f"{literal!r} is bound to a constant in two modules, {where}; one home, imported")
    for module, tree in trees.items():
        problems.extend(
            f"{module}:{line}: {literal!r} is spelled out where {home.name} in {home.module} names it"
            for literal, line in spelled_out(tree)
            for home in homes.get(literal, [])
        )
    return problems


def main(argv: list[str]) -> int:
    """Check the package given (default src/uiaudit); print each problem and exit 1 when any."""
    package = ROOT / (argv[0] if argv else "src/uiaudit")
    problems = check(package)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
