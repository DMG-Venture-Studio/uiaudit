# Architecture

Role: why the code is the way it is, current state, indexed by stack. Code comments cite entries
here by anchor, for example `docs/tech/architecture.md#toolchain`. Rewritten when a decision
changes; the history is in `docs/decisions/`. Never holds status or plans.

## backend

**Every module's path comes from closed lists: a noun or a fixed package, and a role.** Nouns are the business's things, each a vertical slice with only the roles it needs; the import contracts, rendered from the spec, hold the direction of every import. The rules and their reasons are in the conventions document under docs/tech; the nouns were decided in See `architecture`, the first decision record.

**Every surface is a projection of one operation catalog.** A command, a route and an agent's tool call are the same operation behind the same authority check, so a parity test can prove they agree.

## toolchain

**Python is pinned to 3.12 and every tool to an exact version through uv.** ruff, pyrefly, import-linter, deptry and pytest are dev dependencies, so a check means the same thing on every machine.

**The checks are listed with their commands in the constraints file at the repository root.** Each is proven by a planted violation that the toolkit's prove_checks runs; a check without a caught plant is not trusted.

**Generated files are never hand-edited.** The import contracts file is rendered from the spec by the toolkit's renderer and committed, because lint-imports reads it; re-render with `uv run python tools/toolkit/render_import_contracts.py project-spec.toml contracts.toml src/uiaudit`. Each generated path and the command
that regenerates it are listed in `.claude/serial-build.json`; a hook refuses a hand edit to one
and names the command, because a hand edit is silently lost on the next regeneration.

**Local gates name the line in the session that wrote it.** The checks in
`.claude/serial-build.json` run from hooks: the edit checks after every edit to their paths, the
stop checks when a session ends its turn with uncommitted changes under their paths that have not
yet passed. Both run `tools/check.py`, which reads the constraints table, so a session and a person run the
same thing.
