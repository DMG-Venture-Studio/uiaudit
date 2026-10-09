# Bootstrap prompt: the first Claude Code session

From the project folder in cmux: `claude "$(cat docs/decisions/sources/2026-10-09-bootstrap-prompt.md)"`,
or paste everything below the line into a new Claude Code session opened on this folder.

---

You are setting up the enforcement for a new project, **uiaudit**, before any feature work. The scaffolder
wrote the skeleton, the spec, the starter checks and a plant for each. Your job is to make the conventions
impossible to drift from, prove every check works, and hand the first gate to serial-build.

## 0. The repository and the scaffold's own checks

- If `git status` says this is not a repository, or `git log` is empty: `git init -b main && git add -A && git commit -m "Scaffold uiaudit"`.
- The remote exists: `https://github.com/DMG-Venture-Studio/uiaudit`. If `git remote -v` does not list it, `git remote add origin https://github.com/DMG-Venture-Studio/uiaudit.git`. Then `git push -u origin main`.
- Run every command in this block. Each passes on the scaffold, and every `prove_checks.py` line says `caught`:

```
uv sync  # tools
uv run ruff check . && uv run ruff format --check .  # lint, format
uv run pyrefly check  # types
uv run python tools/toolkit/render_import_contracts.py --check project-spec.toml contracts.toml src/uiaudit  # contracts match the spec
PYTHONPATH=src uv run lint-imports --config contracts.toml  # import contracts
uv run deptry src  # dependencies
uv run pytest  # tests
uv run python tools/toolkit/harness_audit.py --gate  # context budgets
uv run python tools/toolkit/prove_checks.py plants.toml  # plants
```

If anything fails here, stop and report it with the output. A scaffold that fails its own checks is a
scaffolder bug, not something to fix in this project.

## 1. Plugins

`.claude/settings.json` declares `serial-build@serial-build-harness`, `agent-skills@addy-agent-skills`, `mcp-legibility@mcp-legibility`. Trust the folder when asked, accept the install prompts (or `/plugin install <name>` each), then `/reload-plugins`, and confirm in `/plugin` that each is enabled.

The settings deny agent-skills' `spec-driven-development`, `planning-and-task-breakdown` and `shipping-and-launch` skills and its `spec`, `plan`, `build` and `ship` commands, and deny writes to `tasks/**` and `SPEC.md`, because those write a second plan beside serial-build's one active plan. A typed `/agent-skills:plan` still expands its own text, but the planning skill it calls is blocked and the write to `tasks/plan.md` is refused. Prove both: run `/agent-skills:plan add a refund`, and show `Skill execution blocked by permission rules` and the refused write. If either is not refused, say so and stop; do not work around it.

## 2. The harness

Run `/serial-build:scope`. It finds `.claude/serial-build.json` and the saved answers in `docs/decisions/sources/scoping-answers-2026-10-09.json`, so it does not interview again: choose to fill the missing files. It writes `CLAUDE.md`, the design, the roadmap with the first gate (`capture-one-cell`), the glossary, its rules and the inbox. Its config and canon checks must both pass. Commit.

## Read before building

1. `docs/tech/conventions.md`: the architecture.
2. `docs/tech/enforcement.md`: how checks are owned and proven, and the acceptance list below.
3. `CONSTRAINTS.md`: every check, its command, and which ones you build.
4. `project-spec.toml`: the nouns (environment, run, finding, plan, regression_test, design_reference), ways in (cli, http, mcp), adapters (browser, accessibility, images, views).
5. `tools/toolkit/README.md`: the shared toolkit, version 0.1.0. Use it as it is.
6. `docs/decisions/sources/2026-10-09-uiaudit-design.md`: a brief this project started from.
7. `docs/decisions/sources/2026-10-09-uiaudit-ledger.md`: a brief this project started from.
8. `docs/decisions/sources/2026-10-09-uiaudit-conversation-source.md`: a brief this project started from.

## Rules for this session

- Do not loosen a starter. No rule removed from `ruff.toml`, no limit raised, no contract edited by hand, no
  `noqa`, `type: ignore` or per-file ignore added for code you write. If a starter rule blocks something the
  conventions require, stop and say which rule and why; do not work around it.
- Do not rewrite toolkit pieces. If one does not fit, say what is missing; do not fork it. A piece the toolkit
  does not have yet is built under `tools/` in the smallest form that passes its plants.
- Generated files are generated: `contracts.toml`, the agent rules under `.claude/rules/`, `openapi.json`, the
  MCP tool list, the CLI help snapshot and `web/src/generated/`. Each gets a `--check` drift check.
- Every check you add gets at least one plant in `plants.toml` before you rely on
  it. Run `prove_checks.py` after each check; a check whose plant is MISSED is not done.
- Commit after each step with a message that says what the check refuses and names the plant that proved it.

## Build, in this order

1. **Check runner.** `make check` (backed by `tools/check.py`) runs every row of `CONSTRAINTS.md` that works,
   one summary line per check, under 15 seconds on this empty project.
2. **Git hooks.** `tools/git_hooks/` with pre-commit (the checks whose local stage in `CONSTRAINTS.md` is the
   commit, and `harness_audit.py --gate`), commit-msg (debt ratchet), pre-push (everything plus the review
   check) and pre-merge-commit. `make setup` sets `core.hooksPath`. Each hook gets a plant. A check runs at
   one local stage, then at push and in CI, never at every local stage.
3. **Claude Code hooks.** serial-build's hooks already run ruff on the edited file after every edit, and the contracts, types, deptry and the tests when a turn ends, from `.claude/serial-build.json`: that end-of-turn hook is those checks' one local stage, so the pre-commit hook does not repeat them. Add only what serial-build lacks, in `.claude/settings.json` (merged, never replaced): the new-module guard on Write, the commit and push refusals of `--no-verify`, `-n` and hooks-path overrides, and the session-start warning when git hooks are off. Each hook gets a plant; none is pinned by digest.
4. **Project checks.** Each "to build" row of `CONSTRAINTS.md`: one home, ways in, surface parity, the debt
   ratchet. Each becomes a command with a plant, and its row says "built".
   - **MCP legibility.** Turn its row in `CONSTRAINTS.md` into a check: mcp-legibility's static probe on this repository reports an `instructions=` block with an entry point. Read the `mcp-surface` skill first.
5. **Agent context.** Path-scoped rules under `.claude/rules/`, one per noun and tier, rendered from the spec
   and the module docstrings, with their drift check. The reviewer agents, each answering one question and
   flagging rather than blocking: authority and sprawl (serial-build already ships an adversarial reviewer and a red-breaker), wired into the pre-push review check.
6. **CI** running `make check` and the tests on every push and pull request, plus a weekly job that runs the
   plants and posts the ledger counts. `.github/workflows/harness-audit.yml` is already here: the weekly
   harness audit, its auditor when `vars.HARNESS_MODEL` is `true`, and issues when `vars.HARNESS_ISSUES` is.
   Before finishing, run `uv run python tools/toolkit/harness_audit.py --time-hooks` and fix every high or
   medium finding your own work caused.
7. **The first gate.** The walking skeleton is the first gate, `capture-one-cell`: `run.start` as one slice through every role it needs and every way in it declares. Do not build it as part of this session's enforcement work: plan it with `/serial-build:gate`, which runs the adversarial review, and Fili accepts it by running its demo.
## Finish with one message containing

- the output of `make check`;
- the output of every `prove_checks.py` run, every line `caught`;
- the refused `git commit --no-verify` attempt, shown;
- the list of ledgers, each empty;
- `CONSTRAINTS.md` with no row left "to build", or the reason each remaining one is not;
- anything in the conventions or the enforcement document you could not hold mechanically, with the reason,
  so it can go to a reviewer agent or back to the scaffolder.
