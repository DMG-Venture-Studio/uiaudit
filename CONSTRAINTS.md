# Constraints

The quality bar for uiaudit, set before the first line of product code. Every row names the command
that gives the verdict; a row marked "starter" works now and is proven by a plant in `plants.toml`; a row
marked "to build" is built by the first Claude Code session, with its plant, and then marked built. How the
checks are owned and kept: `docs/tech/enforcement.md`.

Read this before writing code. Do not weaken it to make a change pass.

## Floor (always enforced)

- No new suppression: no `noqa`, `type: ignore`, `@ts-ignore`, `biome-ignore`, per-file ignore or
  contract edit for code you write. When a rule blocks something the conventions require, stop and say which.
- No unimplemented stubs: no `raise NotImplementedError`, no function whose body is `pass`, no empty `except`.
- No skipped or deleted tests without a reason in the commit message; a skipped database test is a failure.
- No secrets in source.
- This file, `ruff.toml`, `project-spec.toml`, `contracts.toml` and the web configs are not weakened to make a
  change pass.

## Enforced with commands

| Dimension | Rule | Checked by | Runs at | Status |
|---|---|---|---|---|
| Lint | `select = ["ALL"]`, reasoned ignores in `ruff.toml` | `uv run ruff check .` | edit, push, CI | starter |
| Format | ruff's formatter | `uv run ruff format --check .` | edit, push, CI | starter |
| Types | every module typed from its first commit | `uv run pyrefly check` | stop, push, CI | starter |
| Architecture | tiers, roles, noun independence, one home per outside package, surfaces as leaves, no cycles | `PYTHONPATH=src uv run lint-imports --config contracts.toml` | stop, push, CI | starter |
| Contracts drift | `contracts.toml` is the render of `project-spec.toml` | `uv run python tools/toolkit/render_import_contracts.py --check project-spec.toml contracts.toml src/uiaudit` | stop, push, CI | starter |
| Dependencies | imported means declared; declared means imported | `uv run deptry src` | stop, push, CI | starter |
| Tests | pass; a skipped database test is a failure | `uv run pytest` | stop, push, CI | starter |
| Harness | the context every session loads stays under the budgets in `harness.toml`, and no always-loaded file names a path that does not exist | `uv run python tools/toolkit/harness_audit.py --gate` | commit, CI | starter |
| Plants | every check refuses its planted violation, and the tree comes back clean | `uv run python tools/toolkit/prove_checks.py plants.toml` | weekly in CI; push when a check changes | starter |
| One home | a literal bound to constants in two modules, or spelled out where a constant names it | `uv run python tools/one_home.py` | stop, push, CI | built |
| Ways in | no main guard, load-by-name or `python -m` outside `src/uiaudit/surfaces/`, and every console script points into the surfaces; ruff's `banned-api` refuses the direct spellings | `uv run python tools/ways_in.py` | stop, push, CI | built |
| Surface parity | every operation on every surface it declares; the committed OpenAPI document, MCP tool list and CLI help under `docs/api/` equal what the catalog renders | `uv run python tools/render_surfaces.py --check && uv run pytest -q tests/test_surface_parity.py` | stop, push, CI | built |
| Debt ratchet | no ledger under `tools/ledgers/` grows against `main`, no suppression in code outside a ledger, no rule removed, no limit or budget raised, no plant dropped, unless the commit says `Debt-Raised: <reason>` | `uv run python tools/ratchet.py` (the commit-msg hook runs it on the index with the message) | commit, CI | built |
| No bypass | `--no-verify`, `-n` and hooks-path overrides refused | a Claude Code PreToolUse hook and the git hooks, each with a plant | every command | to build |
| MCP legibility | the server sends an `instructions=` block naming its entry-point tool | mcp-legibility's static probe (`probe_connect.py --repo . --json`) | push | to build |

Every row names the command that produces the verdict. A dimension with no command is an aspiration, not a
constraint.

## Measured, not yet enforced

None yet. When a number is worth holding (coverage of changed lines, bundle size, an agent run's cost),
measure it, write today's value here, and hold the direction.

## Exceptions

None. Ledgers start empty and may only shrink against `main`. An exception exists only with
`Debt-Raised: <reason>` in its commit message, and is listed here with its owner and expiry.

| ID | Rule | Path | Reason | Owner | Expires |
|---|---|---|---|---|---|
