# Architecture

Date: 2026-10-09

## Decided

**uiaudit is built from 6 nouns.**

- `environment`: An app under audit in one environment, local or staging: its config, stored sign-in and health. Operations: environment.check, environment.sign_in.
- `run`: One capture of the route, state, viewport and theme matrix, and cell-by-cell comparison across runs. Operations: run.start, run.show, run.list, run.compare. Depends on environment.
- `finding`: One problem in one cell, with its recommendation, triage status and identity across runs. Operations: finding.add, finding.list, finding.accept, finding.reject, finding.diff.
- `plan`: The task plan built from accepted findings that a coding agent executes in the audited repo. Operations: plan.create, plan.show. Depends on finding.
- `regression_test`: A generated test in the audited repo that fails if a closed finding comes back. Operations: regression_test.create, regression_test.list. Depends on finding.
- `design_reference`: Optional design tokens and reference screens for the audited app, and the check of captured styles against them. Operations: design_reference.load, design_reference.check.

**Ways in: cli, http, mcp.** Every one is a projection of the operation catalog.
Adapters: `browser` over playwright, `accessibility` over axe_playwright_python, `images` over PIL, `views` over prefab_ui. Flows: audit, verify_fix. Database: none.

**The first slice is `run.start`**, built end to end through every surface it declares.

**Add-ons:** serial-build on, agent-skills on,
factory off.

Sources, kept verbatim:
- `docs/decisions/sources/2026-10-09-intake.json`, the confirmed intake the scaffold was generated from
- `docs/decisions/sources/2026-10-09-bootstrap-prompt.md`, the plan for the first session
- `docs/decisions/sources/2026-10-09-uiaudit-design.md`
- `docs/decisions/sources/2026-10-09-uiaudit-ledger.md`
- `docs/decisions/sources/2026-10-09-uiaudit-conversation-source.md`

## Rejected

- A sqlite index of runs and findings: a second source of truth beside the JSONL files.
- A jobs way in: nightly audits were dropped; audits run when someone is changing UI.
- environment.check or finding.add as the walking skeleton: neither proves capture works.
- A bundled fixture page as the first demo: it proves nothing about voice-resume.
- The repository name dmg-uiaudit: the owner chose uiaudit.
- The factory add-on: no queue or hand-off pain has been observed yet.

## Reopens if

A second app needs a capture model the route, state, viewport and theme matrix cannot express, or findings need concurrent writers that files cannot serve.
