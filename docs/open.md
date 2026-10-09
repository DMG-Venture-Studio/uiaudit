# Open questions

Role: every undecided question, keyed by slug. Everything that refers to a question uses the
slug. When one is decided: write the decision record, update the standing docs, delete the entry.
This file only shrinks or churns; it never archives.

## mapping-findings-to-source-files
How each finding is mapped to the exact source file and line in the audited repo. Proposed: a small dev-only build plugin that stamps rendered elements with their source location, tested in voice-resume before the remediation plan is built. Fallback: a third-party inspector plugin.

## inline-review-ui-inside-claude
Whether the Claude desktop host accepts the image sizes the review UI needs, runs the slider widget, delivers context updates to the model, and enforces app-only tools. Settled by a half-day test at the start of review-and-compare.

## where-regression-tests-run
Proposed: locally in the first version, run by the fix loop after every fix; revisit when a second app adopts the tool.

## improving-recommendations
How the design reviewer proposes skills or MCP servers that would have improved its advice, where those proposals are recorded, and how Fili approves them. Nothing is installed without his yes.
