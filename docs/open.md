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

## internal-exit-code
the exit code for an unexpected exception (kind `internal`); the brief's table has 0 to 3 only. Recommendation: 4, so CI never reads a crash as an environment problem; the build uses 4 until decided.

## summary-wording-without-checks
the roadmap's demo says the summary prints "how many findings it found", but this gate runs no checks, and a zero would read as a clean report, which the floor forbids. Recommendation: the summary says "not checked (no checks ran)" until the accessibility adapter lands, and intake changes the roadmap's Demo wording before `/serial-build:demo-brief` runs, since the demo brief reads the roadmap.

## environment-check-exposure
whether `environment.check` becomes its own catalog operation on every surface in this gate, or stays a function `run.start` calls until the full matrix. Recommendation: stays a function; the Builds line names only `run.start`.

## engine-sha-outside-checkout
the brief types `engine_sha` as a string and `engine_dirty` as a boolean, but an engine installed from a tag has no checkout. Recommendation: the tag's sha recorded at build time once releases exist; None and False until then.

## viewport-height
the brief gives viewport widths only (375, 768, 1440); a 16:9 height at 375 wide is 211 pixels, which no phone has. Recommendation: portrait 9:16 under 768 wide and 16:9 from 768 up, and the build uses that until decided.

## chromium-install-home
who installs Chromium into the tool environment, since Playwright downloads it separately from the package. Recommendation: `make browsers`, called by `make setup` and both workflows now, and by the planned `doctor --fix` when doctor is built.

## audited-repo-config
where the audited repository's `uiaudit.toml` lives and who writes it before the Copier template exists. Recommendation: the repository root, read from the working directory, hand-written for voice-resume in this gate's demo brief; the template renders it later.

## state-throws-attack
the roadmap's "make the state setup throw" attack cannot be reached while only `default` exists; the full-matrix gate inherits it. Recommendation: intake adds it to that gate's Tried to break when it is written out.
