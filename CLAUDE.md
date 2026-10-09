<!-- serial-build -->
# uiaudit

An agent-driven UI audit. What it is, who it is for and what it is not: `docs/design.md`.

How this project is built, gate by gate, and how to write to Fili, spend money, and keep
systems decoupled: `.claude/rules/serial-build.md`, which always loads.

## Floors

- The engine never calls a model; judgment enters only as validated findings.
- An unchanged UI yields identical deterministic findings on rerun, and a coverage gap fails loudly, never as a clean report.
- Only a human accepts or rejects a finding; agents raise findings but never triage them.
- Staging runs are read-only against a test account, make no paid calls without an explicit flag, and sign-in files are never committed.
- Every finding carries a recommendation; a finding without one is rejected.
- Agents keep improving their recommendations: after each critique they propose the skills or MCP servers that would have made the advice better, for Fili to approve.
- Every module's path is a noun or a fixed package, and a role, from closed lists. A new noun, adapter
  or surface is a change to the spec first, with a decision record: stop and ask.
- No suppression for code you write: no noqa, no type-ignore, no per-file ignore, no hand edit to the
  import contracts. When a check blocks something the conventions require, stop and say which.

## Where things live

| Path | Holds |
|---|---|
| `src/uiaudit/` | The backend: one package per noun, plus kernel, catalog, flows, adapters, surfaces and boot. Never scripts, fixtures or test tooling |
| `tests/` | pytest, `tests/<noun>/test_<role>.py`. Never product code |
| `tools/` | The pinned toolkit, the check runner, git hooks. Never imported by the product |
| `docs/` | The records below |
| `.claude/` | Rules scoped by path, and `serial-build.json`: the owner's name, the generated files, the checks the hooks run, and the test paths the red lane may write |
| `claude_outputs/` | An inbox other sessions drop files into; never committed, emptied by whoever reads it |

| Doc | Holds |
|---|---|
| `docs/design.md` | What the product is, who it is for, what they do today, and what it is not. Current state only |
| `docs/tech/architecture.md` | Why the code is as it is, by stack; generated files and local gates under toolchain |
| `docs/glossary.md` | The only place a term is defined |
| `docs/roadmap.md`, `docs/plan.md`, `docs/done.md` | One gate ledger: pending, in flight, shipped with proof |
| `docs/open.md`, `docs/decisions/` | Open questions by slug; dated append-only records: decided, rejected, reopens if. `decisions/sources/` holds the verbatim briefs, handoffs, interviews, and red-lane output the records cite |

Tests sit beside the code they test (pytest `tests/<noun>/` beside the package).

## Commits

Commit finished, proven work without asking. Never move a gate to done before Fili has run its demo.

## Commands

```
uv sync       # tools
make setup    # switch the git hooks on in this clone
make check    # every check in CONSTRAINTS.md, the one list of commands; one line each
make plants   # prove every check and hook refuses its planted violation
```
