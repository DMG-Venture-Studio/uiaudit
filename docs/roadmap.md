# Roadmap

Role: pending gates only, grouped under stage headings, in order. Each gate carries the same
sections: Builds (what it produces), Demo (the scripted scenario Fili runs and what they
should see, ending with a Break it: step where they try to break it), Depends on (the gates that
must ship first), Decided (constraints it honours, each naming its decision record by slug),
Decide by proof (options, what is measured, the criterion; each outcome becomes a dated decision
record naming the rejected option; numeric thresholds are proposals until the gate is planned),
Open (unresolved questions by slug, with a recommendation where one exists), QA (mechanical
checks, which become the proof commands when the gate ships), Tried to break (the attacks the red
lane must at least attempt: inputs, orders, neighbours, and limits meant to make it fail), and
Acceptance (what Fili does on the running product and the sentence they can then say).
No estimates, no status. A stage may end with a list opening "Later:", naming gates in one line
each, in order, not yet written out; intake writes the next one out in full, with every section,
before it is planned. A gate is done only when Fili has run its demo; a report, a test, or a green
check never accepts a gate. Rationale lives in the decision records a gate names, never here.

## Stage: first-local-audit

Goal: Running uiaudit against voice-resume on Fili's Mac captures every configured cell with accessibility findings, including the recording, microphone-denied and upload-failure states.

### capture-one-cell

Builds: run.start through the cli way in: loading the config, the browser adapter, one cell's screenshot, the run manifest with the engine version, and exit codes 0 to 3.

Demo: With voice-resume's dev server running on the Mac, run uiaudit for one route, one state and one viewport. The screenshot for that cell appears in the run folder and the command prints a run summary with the cell count and how many findings it found. Break it: stop the dev server and run it again; it must exit with an environment error that names the command to fix it, never a clean summary.

Depends on: none.

Decided: the nouns, the ways in and the closed module lists (see `architecture`).

Decide by proof: none.

Open: none.

QA: every check in the constraints file passes; every plant is caught; the parity test shows the operation on each way in.

Tried to break: Stop the dev server before and during a run; point the config at a route that does not exist; use an expired or missing sign-in; make the state setup throw; run twice on an unchanged UI and compare the findings; remove the browser from the tool environment.

Acceptance: I ran uiaudit against voice-resume, saw the cell's screenshot and summary, and a broken app failed loudly with the fix instead of passing.

Later: one line each, until intake writes them out in full.
- full-matrix: Fili runs the whole route, state, viewport and theme matrix, including fake-microphone and mocked-failure states, and two reruns give identical findings.
## Stage: review-and-advice
Goal: Fili sees every finding on its screenshot with a recommendation and a before and after preview, and decides by looking.
- review-and-compare: Fili browses findings on annotated screenshots, compares any cell before and after with a slider, and triages in the browser or inline in Claude.
- critique-with-recommendations: the design reviewer adds look, feel and flow findings, each with a recommended fix and a preview where possible, and proposes skills or MCP servers that would sharpen its advice.
## Stage: remediation
Goal: A coding agent with no context turns accepted findings into fixes that stay fixed.
- remediation-plan: accepted findings become a task plan with exact files that a naive Claude Code agent executes.
- fix-loop: an agent fixes one finding per commit, reruns the affected cells, and a generated regression test fails if the fix is reverted.
## Stage: design-and-staging
Goal: Audits judge against the intended design and reach staging safely.
- intended-design: off-palette and off-scale styling is flagged against the design tokens, and reference screens join the slider.
- staging-audit: Fili audits staging on demand, read-only, without spending money unless he asks.
