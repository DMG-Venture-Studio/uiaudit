# Source: claude.ai conversation, Project "aside", 2026-10-01

No raw transcript export was available. USER turns are verbatim. ASSISTANT turns
are a condensed reconstruction by the assistant that wrote this doc: one claim per
line, same content, shorter wording. Every ASSISTANT line is AI-produced.

## Turn 1 - USER
do some research and find skills / plugins that would work with a playright'esq crawler, or claude in chrome to do a UI design audit + remediation plan for CC

## Turn 1 - ASSISTANT (condensed)
A real audit splits into a deterministic layer (crawl, Lighthouse, axe) and a judgment layer (visual and UX critique).
Do not use Claude in Chrome as the crawler: it requires /login (no API key or setup-token, so no CI) and has repeated native-host conflicts with Claude Desktop on macOS.
Browser layer option: Chrome DevTools MCP plugin (bundled a11y-debugging skill, lighthouse_audit excludes performance, --autoConnect reuses the logged-in Chrome session).
Browser layer option: Playwright CLI or Vercel agent-browser for lower token cost and CI fit.
Coverage option: Unlighthouse crawls sitemap and links and runs Lighthouse in parallel; public routes only.
Deterministic a11y option: AccessLint plugin (WCAG 2.2, live DOM, branch diff mode).
Judgment rubric option: impeccable (audit and critique commands, 61 deterministic detector rules, edit hook); pick one rubric, not impeccable plus Vercel web-design-guidelines.
Audit-fix loop option: gstack /design-review (one commit per fix, before/after screenshots) but it wants to own the browser layer.
Gap none of these cover: crawlers see routes, not states; Aside's risk is state (mic denied, recording, upload failed, voice masking, password gate, empty resume).
Proposal: scripted route x state x viewport x theme matrix in playwright-python with WorkOS storageState, dumping screenshot plus axe JSON per cell.
Proposal: group remediation by component, not by page.
Proposal: ratchet every fixed finding into a test (axe assertion or screenshot baseline) so fixes cannot silently regress.

## Turn 2 - USER
should we create this as a new project entirely? considering the amount of front end work we do it might be nice to have a package we can reuse across other projects?

## Turn 2 - ASSISTANT (condensed)
Reusable core is the glue, not the browser, a11y engine, or rubric, which are already packaged by others.
Glue: harness runner, findings schema, plan and fix skills, ratchet, auth adapters.
Findings schema should be stable and SQL-queryable (DuckDB over findings.jsonl) across portfolio apps.
Do not vendor or fork third-party skills; reference them.
Pushback: build inside Aside first and extract only after a second app runs it.
Commercial angle: fixed-fee UI audit plus remediation plan as a consulting deliverable; findings report is the sales artifact.
Repo name proposed: DMG-Venture-Studio/dmg-uiaudit; command name uiaudit.

## Turn 3 - USER
fully aligned, how do we proceed?

## Turn 3 - ASSISTANT (condensed)
Phase 0: install DevTools MCP, AccessLint, impeccable in the app repo; run impeccable init; seed DESIGN.md from Claude Design output; dedicated WorkOS test user.
Phase 1 schema first: Finding model with id, source, rule, severity, route, state, viewport, theme, evidence_path, component, confidence, status.
Phase 1 config: uiaudit.toml with routes, viewports 375/768/1440, themes, auth adapter, gitignored output dir.
Phase 1 states are Python setup functions; fake mic via Chromium flags; error states via page.route mocks.
Phase 1 exit: screenshot count equals matrix size; two runs give identical axe findings; full run under 5 minutes locally.
Phase 2: design-reviewer subagent appends critique findings; audit-plan groups by component; human triage; rejected become ignore rules.
Phase 3: one commit per fix; re-run affected cells; emit guard per fix; reverting a fix fails CI.
Phase 4: second app (TLDR Recall) then extract.
Question to user: local dev, staging, or both.

## Turn 4 - USER
what about if we did it as a separate repo, installable as a CLI driven by an agent so it could be installable into the repo, dogfooding voice-resume . i'd say local + staging

## Turn 4 - ASSISTANT (condensed)
Agree: voice-resume as consumer from day one removes the no-consumer risk; rule is nothing voice-resume-specific in core.
Agent-facing CLI: every command takes --json, never prompts, fixed exit codes 0 clean, 1 findings over threshold, 2 config error, 3 environment problem.
Errors include the fix command.
uiaudit schema prints the findings JSON Schema.
Critique stays out of the CLI; agent appends via uiaudit findings add --json which validates against the schema.
Env config: local with mocks true; staging with mocks false and read_only true.
Mock-dependent states run local only.
Staging runs read-only against a dedicated test account with seeded resumes.
Replicate-triggering states gated behind --allow-paid.
Cadence: local on demand; PRs against Railway PR environments if enabled; nightly staging via GitHub Action failing only on new high-severity findings.

## Turn 5 - USER
could it support a symlink instead?

## Turn 5 - ASSISTANT (condensed)
Skill install via symlink plus SessionStart hook to self-heal; uiaudit doctor checks the link; --copy fallback.

## Turn 6 - USER
that's good, but i mean for Install model

## Turn 6 - ASSISTANT (condensed)
Global editable tool install keeps harness deps out of the app lockfile.
requires field in uiaudit.toml pins the engine version; CI uses uvx from a git tag.
Run manifest records harness git SHA and dirty flag.
States are loaded by file path, not imported; states may use only stdlib, Playwright, and the uiaudit API.
Seed data via HTTP or fixture SQL, never the app ORM.
doctor --fix installs Chromium into the tool environment.

## Turn 7 - USER
what if it copied the repo locally?  idk do some research and give me options. it would be nice to see local previews and have it generate a solid plan for the source repo to implement

## Turn 7 - ASSISTANT (condensed)
Option Copier: vendored copy with recorded version; copier update does a 3-way merge; one-directional.
Option git subtree: bidirectional via subtree pull and push; history clutter.
Option shadcn registry: any files, granular, but Node CLI for a Python tool and no merge-based update found.
Option submodule: rejected; clones and cloud sandboxes skip --recursive.
Proposed hybrid for later: engine installed and pinned; app layer (config, states, skill, CI workflow, report template) scaffolded by Copier.
Local previews: uiaudit serve, a local FastAPI app showing the matrix grid with finding boxes drawn from captured element bounding boxes.
Triage in the browser writes status back to findings.jsonl.
uiaudit report exports the same view as one static HTML file.
Before/after visual diff by wrapping reg-cli rather than building one.
Plan quality lever: deterministic file attribution via a dev-only source-stamp plugin in the local env; verify React 19 compatibility.
Plan format: spec-kit tasks.md lines [ID] [P?] [Story] description with file path; story equals remediation theme; task lists finding IDs and a done-check.
Deterministic parts of plan (grouping by file, severity order, [P] by file overlap, done-checks) produced by uiaudit plan; agent writes only story names and fix descriptions.

## Turn 8 - USER
i'm aligned, I want the hybrid version first. why is the harness such a consideration OOC?

## Turn 8 - ASSISTANT (condensed)
The harness is the measuring instrument; it must be the fixed reference frame because everything downstream is model output.
Harness coverage gaps are invisible downstream: an unreached state yields a clean report.
Harness is the differentiated, sellable part.
Harness holds staging credentials and executes code against live environments.
Hybrid layout: one repo, engine at src/uiaudit, Copier template under template/ via _subdirectory, single shared version tag.
Local dev of the engine via uv tool install --editable; doctor warns on mismatch with requires; CI uses uvx at the tag.
Skill becomes a Copier-managed copied file; drop the symlink-plus-hook scheme.
First scaffold order: engine core, then template, then voice-resume adoption with recording, mic-denied, upload-500 states.

## Turn 9 - USER
you can, or you can detail in a spec for me to kick off in a separate CC repo

## Turn 10 - USER (structured interview answers)
OI-1 Findings contract: Accept as proposed
OI-2 Engine contract: Add an MCP server now too
OI-3 Staging: Accept as proposed

## Turn 11 - USER (2026-10-08)
what's replicate?
also if we were to build a front end to drive this, what would it look like? electron? something else?

## Turn 11 - ASSISTANT (condensed)
Replicate is a pay-per-compute hosted model API (acquired by Cloudflare, API unchanged); voice-resume uses it for voice models.
Not Electron: it duplicates Playwright's Chromium and adds a Node runtime.
Option 1: grow uiaudit serve into the app (runs, matrix, cell, plan views), installable as a Chrome app window.
Option 2: the same views as an MCP App rendered inline in Claude, where the model sees user actions.
Option 3: Tauri only for a client double-click installer; hosted is the better client answer.
Build one frontend over the command layer so it runs in serve, as an MCP App, and later hosted.
A launch-Claude-Code button belongs in the UI layer, never the engine.

## Turn 12 - USER
re: MCP layer, what about this? we could drive it from cowork?
https://prefab.prefect.io/docs/welcome
FWIW I like 1 & 2

## Turn 12 - ASSISTANT (condensed)
Prefab is a Python UI DSL with a bundled React renderer; FastMCP tools marked app=True return Prefab UIs.
One view module can serve three hosts: MCP App (CallTool), FastAPI page (Fetch), static HTML export.
SendMessage and UpdateContext let the UI post to and inform the conversation.
App-only tool visibility keeps triage human-only, enforced by the host.
Prefab is pre-1.0 with breaking minor versions; pin exactly.
Draw finding boxes into PNGs with Pillow at capture time rather than as a UI overlay.
Image payloads inside the host iframe are unverified; spike before Milestone 2.
Claude desktop renders MCP Apps; terminal Claude Code gets text only.
Proposed spec changes: Prefab dependency, shared views module with three hosts, Pillow overlays, a rendering spike issue, drop the React bundle.

## Turn 13 - USER
yes, provided we get this as well: before/after slider.
you can also clip the nightly thing - i don't know why you'd need a nightly UI audit
also, do you think it worth having something like a claude design output to optionally reference?

## Turn 13 - ASSISTANT (condensed)
OI-8 proposed: tokens plus optional reference screens, tokens first; reference screens never ratcheted.

## Turn 14 - USER
as proposed
