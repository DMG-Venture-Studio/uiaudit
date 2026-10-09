---
paths:
  - "src/**"
  - "tests/**"
  - "tools/**"
  - "migrations/**"
  - "web/src/**"
  - "project-spec.toml"
  - "plants.toml"
---

# Architecture

- uiaudit is built from nouns (environment, run, finding, plan, regression_test, design_reference), each a package under `src/uiaudit/` holding only the roles
  `ops`, `render`, `rules`, `store` and `model`. The fixed packages are `kernel`, `catalog`, `flows`,
  `adapters`, `surfaces` and `boot`. The rules and the reasons: `docs/tech/conventions.md`.
- New behaviour is an operation on a noun. A new noun, adapter or surface changes `project-spec.toml`
  first, then the contracts are re-rendered, then the code.
- `contracts.toml` is generated: `uv run python tools/toolkit/render_import_contracts.py project-spec.toml contracts.toml src/uiaudit`.
- A check is done when its plant is caught: `uv run python tools/toolkit/prove_checks.py plants.toml`.
- With serial-build, a gate is one or more slices Fili can run and judge; its QA lists the checks from `CONSTRAINTS.md` that prove it.

## Kits

- **CLI**: the `better-cli` skill in `.claude/skills/` applies to every change to the CLI surface: data on stdout, diagnostics on stderr, `--json`, never a prompt, errors that name the next command.
- **MCP**: the `mcp-surface` skill says how the MCP surface is built for a cold agent; audit it with `/mcp-legibility:legibility-audit --no-headless` after each change.
- **agent-skills**: technique skills (test-driven development, debugging, code review, security, API design) apply inside any slice. serial-build owns the lifecycle, so its spec, plan, build and ship skills are denied in `.claude/settings.json`; plan a gate with `/serial-build:gate`.
