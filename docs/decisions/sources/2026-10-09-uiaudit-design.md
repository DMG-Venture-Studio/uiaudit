# uiaudit Design Doc

## Metadata

- **Status**: Draft
- **Created**: 2026-10-01
- **Updated**: 2026-10-08
- **Audience**: Claude Code (or an engineer) bootstrapping the new `dmg-uiaudit` repo with no access to the planning conversation. Assumes fluency with Python, uv, Playwright, and Claude Code skills.
- **Sources**: `sources/conversation-2026-10-01.md`, `sources/aside-memory.md` @ none (not extracted from a git repo)
- **Verified against repo**: no (greenfield; the consumer repo voice-resume was not reachable). Code claims about voice-resume (Vite, React version, routes) must be verified during the first local audit.
- **Ledger**: [ledger.md](ledger.md)
- **Excluded sections**: Service level objectives (internal developer tool, no external users); Legal and compliance (internal tool; license choice deferred until it ships to clients); Monitoring and alerting (no unattended jobs since the nightly staging run was dropped)

## Objective

Give every DMG frontend a repeatable, agent-driven UI audit that captures each screen state, lets a person review findings locally, and emits a fix plan Claude Code can execute.

## Background

DMG ships a lot of frontend work across portfolio apps. The first consumer is voice-resume (working name Aside): candidates upload a resume, record voice narrations on sections, and publish a shareable page, public or password-protected, with optional voice masking. It is designed in Claude Design and built with Claude Code.

The goal was a UI design audit plus remediation plan that Claude Code can run. Research found the building blocks already exist as third-party tools: Chrome DevTools MCP, Playwright, AccessLint, impeccable, Unlighthouse, and gstack's `/design-review`. None of them covers the part that matters most for an app like this. Crawlers and Lighthouse see routes; they do not see states. Aside's riskiest screens are states: microphone denied, recording in progress, upload failed, voice masking on, password gate, empty resume. A crawler that never reaches those states produces a clean report on the screens most likely to be broken.

So the reusable asset is the glue around those tools, not the tools themselves:

- a harness that drives a scripted matrix of route × state × viewport × theme;
- a stable findings format;
- a review UI that works in a local browser and inline in a Claude conversation, where the person and the agent look at the same view;
- a plan generator;
- a ratchet that turns fixes into tests.

The harness is the measuring instrument; everything downstream is judgment layered on its evidence. That is the assistant's reasoning, not something measured, but it is why the design spends most of its constraints on the harness:

- It must be the fixed reference frame, so findings change only when the UI changes. That is why it is version-pinned and every run records the harness SHA.
- Its coverage gaps are invisible downstream.
- It holds staging credentials and executes code against live environments.
- It is the differentiated part: the browser, the a11y engine, and the rubric are commodities.

The same output, a findings report with a plan, is also a plausible fixed-fee consulting deliverable for DMG later. That is context only, not a v1 goal.

## Goals

- Any DMG frontend repo can adopt the audit with one scaffold command, without adding audit dependencies to the app's own lockfile.
- A reviewer can see every audited route × state × viewport × theme cell, with findings drawn on the screenshot, compare any cell before and after a change, and triage findings, either in a local browser or inline in a Claude conversation.
- Each audit yields an implementation plan with exact file paths and done-checks that a coding agent can execute without re-deriving context.
- Findings from every app are queryable with SQL for cross-portfolio patterns.
- A fixed finding stays fixed: reverting the fix makes the generated regression tests fail.
- When a repo supplies its design tokens, styling that drifts from the intended design system is flagged in the same audit, without a person spotting it by eye.

## Non-goals

- Reimplementing browser automation, an accessibility engine, or a design rubric.
  - Playwright, axe-core, and impeccable already do these; the value is the harness and glue.
- Vendoring or forking third-party skills and plugins (impeccable, AccessLint, DevTools MCP).
  - Consumers install them directly; copying them means owning their update churn.
- Scheduled or nightly audits.
  - Audits run on demand, when someone is changing UI; a scheduled run of an unchanged UI finds nothing new.
- A packaged desktop app (Electron, Tauri).
  - The review UI runs in a local browser and inside Claude; a desktop shell adds packaging and signing for no new capability.

## Scenarios

### Fili audits voice-resume locally

1. In voice-resume, Fili runs `uvx copier copy --vcs-ref v0.1.0 gh:DMG-Venture-Studio/dmg-uiaudit .`. That writes `uiaudit.toml`, `uiaudit/states/`, `.claude/skills/uiaudit/SKILL.md`, `.claude/agents/design-reviewer.md`, and `.mcp.json`. The app's `pyproject.toml` and `package.json` are untouched.
2. He runs `uiaudit auth local`. A headed Chromium opens, he signs in through WorkOS as the dedicated test user, and the session is saved to `.uiaudit/auth/local.json`.
3. With the dev server on `http://localhost:5173`, Claude Code runs `uiaudit run --env local --json`.
   - The matrix is 6 routes × applicable states × 3 viewports (375, 768, 1440) × 2 themes.
   - Every cell is captured to `.uiaudit/runs/20261001T1415Z/`, including `editor/recording` with a fake microphone feeding `fixture.wav` and `editor/upload-500` with the upload API mocked to return 500.
4. The command exits 1 because 14 findings are at or above the severity threshold. The JSON summary lists counts by severity and the run path.

### Fili triages and generates a plan

1. Claude Code invokes the `design-reviewer` subagent. It reads the run's screenshots and `DESIGN.md`, and appends 9 `source=critique` findings through `uiaudit findings add --json`.
2. Fili runs `uiaudit serve`, opens `http://127.0.0.1:8765`, and filters to `severity>=high`.
3. He accepts 17 findings and rejects 6. The rejected ones are intentional, such as a deliberately low-contrast watermark on masked-voice badges.
4. `uiaudit plan` writes `.uiaudit/plans/20261001T1415Z/tasks.md`.
   - Accepted findings are grouped by the component file that renders them, for example 11 findings fold into one task on `src/components/RecorderControls.tsx`.
   - Tasks that touch different files are marked `[P]`.
   - Claude Code fills in only the story titles and fix descriptions.

### Claude Code implements the plan

1. Claude Code works through `tasks.md`, one commit per task, each message citing the finding IDs it closes.
2. After each task it runs `uiaudit run --env local --only editor/recording` to re-capture the affected cells.
3. It runs `uiaudit diff` against the previous run to confirm those findings are closed, and `uiaudit ratchet` to emit a regression test for each closed finding.
4. Fili opens the Compare view for `editor/recording` at 375px, light theme, and drags the before/after slider between the run before the fix and the run after it. The diff mode highlights the changed pixels around the record button.

### Fili reviews inline in Claude

1. In the Claude desktop app, with voice-resume connected, Fili writes "audit voice-resume locally".
2. The model calls `start_run`, polls `get_run` until the run finishes, then calls `open_audit`. The Matrix view renders inline in the conversation.
3. Fili opens `share/password-gate` at 375px, sees a button outlined as finding F-7d21a0 with no accessible name, and accepts it. He rejects two critique findings about the watermark. Each decision updates the model's context with the finding ID and new status, and nothing else.
4. He clicks "Plan accepted findings". That posts the request into the conversation, and the model runs `plan`.

## Constraints

- Claude in Chrome cannot be the capture layer. Claude Code's Chrome integration only works when signed in with `/login`, so it is disabled under API-key or token auth and cannot run in CI. It also has repeatedly reported native-messaging conflicts with Claude Desktop on macOS.
- The first consumer's stack is fixed: React + Tailwind frontend; FastAPI + uv + Pydantic backend; WorkOS auth; Doppler secrets; Postgres with RLS; Railway hosting; Replicate voice models.
- Python (with uv) and SQL are the server-side languages of choice. The developer machine is a Mac.
- DMG is a three-person studio running at low overhead. Anything requiring ongoing babysitting, a hosted service, or per-app forks of the engine is a cost to avoid.

## Interfaces

Decided surfaces are below. The field-level contracts in the resolved issues "Findings and run format" and "Engine contract" are binding.

### Repository layout (decided)

One repo with two artifacts, released under a single version tag so the template and the engine it pins cannot drift.

```
dmg-uiaudit/
  pyproject.toml              # engine package; console script `uiaudit`
  src/uiaudit/
    schema.py                 # Finding, RunManifest (Pydantic)
    config.py                 # uiaudit.toml loader
    states.py                 # state loader + uiaudit state API
    capture.py                # Playwright driver, fake mic, mocks, bbox capture
    axe.py                    # axe-core run + normalization to Finding
    annotate.py               # Pillow: numbered finding boxes, thumbnails, diff images
    views/                    # Prefab view trees shared by every host
    serve.py                  # FastAPI host for the views (local browser)
    plan.py                   # tasks.md skeleton generator
    ratchet.py                # emits pytest guards
    cli.py
    mcp.py                    # stdio MCP server over the same command functions
  tests/
  copier.yml                  # _subdirectory: template
  template/                   # rendered into consumer repos
    uiaudit.toml.jinja        # requires pinned to this repo's tag
    uiaudit/states/example.py.jinja
    uiaudit/fixtures/fixture.wav
    .claude/skills/uiaudit/SKILL.md.jinja
    .claude/agents/design-reviewer.md.jinja
    .mcp.json.jinja           # registers `uiaudit mcp`
```

### Distribution (decided)

- **Consumers adopt with Copier:** `uvx copier copy --vcs-ref vX.Y.Z gh:DMG-Venture-Studio/dmg-uiaudit .`.
- **Consumers update with Copier:** `uvx copier update` three-way-merges template changes into any local edits.
- **Rendered config pins the engine:** `requires = "vX.Y.Z"` in `uiaudit.toml`.
- **CI runs the pinned engine:** `uvx --from git+https://github.com/DMG-Venture-Studio/dmg-uiaudit@vX.Y.Z uiaudit ...`.
- **Local engine development:** `uv tool install --editable ~/code/dmg-uiaudit`. `uiaudit doctor` warns when the installed engine does not match `requires`.
- **The Claude Code skill ships as a template file**, versioned and merged by Copier like the rest of the template. There is no symlink.

### Capture matrix (decided)

- A run is the cross product of routes × states × viewports × themes, filtered to the states declared for each route and allowed in the selected environment.
- Each cell is captured by a scripted Playwright (Python) session that loads the stored WorkOS session (`storageState`).
- Each cell yields a screenshot, axe results normalized into findings, and the bounding boxes of flagged elements.
- Environments are `local` and `staging`. Per-environment behavior is set by the resolved issue "Staging policy".

### MCP server (decided)

`uiaudit mcp` starts a stdio MCP server, registered in consumer repos by a template-rendered `.mcp.json`. Rules:

- **Same code path as the CLI.** Each data tool calls the command function the CLI calls and returns the same JSON. CLI and MCP output for the same input must be byte-identical, which a test enforces. View tools (below) return a Prefab UI instead and are tested separately.
- **Long work is asynchronous.** A full run takes minutes, longer than typical MCP client tool timeouts, so `start_run` returns a `run_id` immediately, and `get_run` reports progress and the final summary. The CLI's `run` stays synchronous.
- **Error parity.** Exit codes map to structured errors: `{"code": 3, "kind": "environment", "fix": "uiaudit auth staging"}`.
- **No network transport in v1.** Stdio only, and no model calls.

Data tools: `doctor`, `start_run`, `get_run`, `diff`, `list_findings`, `add_findings`, `schema`, `plan`, `ratchet`.

View tools: `open_audit` is the entry point the model calls to show the review UI. `get_cell`, `get_compare`, and `set_finding_status` are app-only: the UI calls them, and they are marked hidden from the model so triage stays a human decision. The host enforces that visibility, not the server, so every status change is also written to the triage log with the surface it came from.

`auth` and `serve` stay CLI-only because they open a browser for a human.

### Review UI (decided)

**One view module, three hosts.** `src/uiaudit/views/` builds Prefab component trees from command-layer data. Each view takes a transport adapter that emits `CallTool` over MCP or `Fetch` over HTTP; everything else is identical.

- **Inline in Claude (MCP App):** the `open_audit` tool returns the UI, and the Claude desktop or web app renders it in the conversation.
- **Local browser:** `uiaudit serve [--run latest]` starts a FastAPI app bound to 127.0.0.1. Its routes call the same command functions, and write routes require the per-session token.
- **Static file:** `uiaudit report --run latest --out report.html` exports one self-contained HTML file with images inlined and write actions hidden.

**Views:**

- **Runs:** run history with findings by severity per run, and a start-run action.
- **Matrix:** route/state rows, viewport/theme columns, a thumbnail and finding count per cell.
- **Cell:** the annotated screenshot, a findings table filterable by severity and source, and accept/reject. A reject also records an ignore rule in the committed `uiaudit.ignore.toml`, so the finding is not re-raised on later runs.
- **Compare:** one cell from two runs. It defaults to the latest run against the previous run that captured the same cell, and either side can be changed. Three modes:
  - a before/after slider over the two screenshots;
  - side by side;
  - a diff image with changed pixels highlighted.
- **Plan:** the rendered `tasks.md`, with each task's status derived from its findings.

**Slider implementation:** a small self-contained HTML widget (two images and a range input) inside Prefab's `Embed` component, which runs custom HTML in a sandboxed iframe. If a host blocks it (see the open issue "Inline review UI inside Claude"), the Compare view falls back to a before/after toggle driven by Prefab state.

**Evidence is drawn at capture time, not in the UI.** `annotate.py` writes, per cell, an annotated PNG with numbered boxes on each finding's captured bounding box, a small JPEG thumbnail, and on request a diff image between two runs. Every host, the static report, and the critique agent see identical evidence.

**Agent loop, MCP host only:**

- Accepting or rejecting a finding also sends `UpdateContext` with the finding ID, rule, and new status. It never includes page-derived text.
- A "Plan accepted findings" button sends `SendMessage`, which posts the request into the conversation.

Whether the host delivers these is checked in the open issue "Inline review UI inside Claude".

**Boundary:** the CLI and engine never call a model. A future "fix with Claude Code" button belongs in the UI layer, not the engine.

### Design reference (decided)

Optional. When `uiaudit.toml` has no `[design]` section, nothing below runs and no finding mentions design tokens.

```toml
[design]
tokens = "design/tokens.json"          # DTCG JSON, or a CSS file of custom properties
compare_to_shipped_theme = true        # also read the app's built Tailwind theme

[design.screens]                       # optional reference screens, keyed by cell
"editor/recording@375-light" = "design/editor-recording.png"
"share/password-gate@1440-light" = "design/share-gate.png"
```

- **Token detector (deterministic).** For every visible element in a cell, the harness reads computed `color`, `background-color`, `border-color`, `font-size`, `line-height`, spacing, and `border-radius`, and compares them against the token set. Values off the set by more than a small tolerance become `source=detector` findings with rules such as `off-palette-color`, `off-scale-font-size`, `off-scale-spacing`, and `off-scale-radius`, each carrying the nearest token in its message. These findings are fingerprinted, triaged, planned, and ratcheted like axe findings.
- **Design drift.** When the shipped Tailwind theme and the design tokens disagree on a token, the detector raises one `design-drift` finding for that token, not one per element using it.
- **Reference screens (advisory).** A mapped reference image appears as a third source in the Compare view, so the slider can run between intended and actual. The critique agent also receives it as the intended design. Any finding it produces from the comparison is `source=critique` with confidence below 1, and `uiaudit ratchet` never emits a test for it.
- **`uiaudit doctor`** fails with exit 2 if a configured token file does not parse, and warns when a reference screen is older than the last change to the component that renders its cell, as far as source stamps can tell.

### Plan output (decided)

`uiaudit plan` writes `tasks.md` in GitHub spec-kit's checklist format, so `/speckit.implement` or any agent can execute it:

```
## Phase 1: High severity, shared components

### Story US1: Recorder controls are keyboard- and screen-reader-operable

- [ ] T001 [P] [US1] Give icon-only record/stop buttons accessible names in src/components/RecorderControls.tsx (closes F-3fa9c2, F-91be07, F-0c44d1; check: `uiaudit run --env local --only editor/recording` shows them closed and `uv run pytest tests/uiaudit -q -k F_3fa9c2` passes)
```

The skeleton is computed deterministically; the agent supplies only the prose.

- **Computed by `uiaudit plan`:**
  - phases by severity;
  - task-per-file grouping;
  - `[P]` when tasks touch disjoint files;
  - finding IDs and done-checks for each task.
- **Supplied by the agent:** story titles and fix descriptions.

Running `uiaudit plan` twice on the same findings yields an identical skeleton.

## Glossary

- **Engine**: the `uiaudit` Python package and CLI in this repo.
- **App layer**: files Copier renders into a consumer repo (config, states, skill, agent, MCP registration).
- **Consumer repo**: an app repo that has adopted the app layer; voice-resume is the first.
- **State**: a named UI condition reached by a setup function (for example `recording`, `mic-denied`, `upload-500`).
- **Cell**: one route × state × viewport × theme combination, captured once per run.
- **Run**: one execution of the matrix, stored under `.uiaudit/runs/<run-id>/`.
- **Finding**: one problem observed in one cell, from axe, a detector, Lighthouse, or the critique agent.
- **Fingerprint**: the stable finding ID that lets the same problem be matched across runs (see "Findings and run format").
- **Source stamp**: a dev-only attribute on rendered elements giving the source `file:line` that produced them (see "Mapping findings to source files").
- **Ratchet**: an automatically emitted regression test that fails if a closed finding reappears.
- **View**: one screen of the review UI (Runs, Matrix, Cell, Compare, Plan), defined once in `views/`.
- **Host**: where a view is displayed: inline in Claude (MCP App), the local browser (`serve`), or the static report.
- **Design reference**: optional intended-design input from Claude Design: a token file and reference screens (see Interfaces > Design reference).

## Data model

Storage is files, not a database. The shapes come from the resolved issue "Findings and run format".

```
.uiaudit/                       # gitignored in consumer repos
  auth/{env}.json               # Playwright storageState, chmod 600
  runs/{run_id}/
    manifest.json               # RunManifest
    findings.jsonl              # one Finding per line
    triage.jsonl                # every status change: finding id, old, new, surface, time
    cells/{route_slug}/{state}/{viewport}-{theme}.png            # raw screenshot
    cells/{route_slug}/{state}/{viewport}-{theme}.annotated.png  # numbered finding boxes
    cells/{route_slug}/{state}/{viewport}-{theme}.thumb.jpg
  diffs/{run_a}__{run_b}/{route_slug}/{state}/{viewport}-{theme}.png
  plans/{run_id}/tasks.md
uiaudit.ignore.toml             # repo root, committed: rules created by rejecting findings
```

The cross-app SQL view is DuckDB over the JSONL files. Nothing is persisted outside the files.

```sql
CREATE VIEW findings AS
SELECT * FROM read_json_auto('.uiaudit/runs/*/findings.jsonl', filename = true);

-- Which components keep failing, across runs
SELECT component, rule, count(*) AS n
FROM findings
WHERE status IN ('open', 'accepted')
GROUP BY ALL
ORDER BY n DESC;
```

## Security

### Attack surface

- **Stored sessions:** `storageState` files under `.uiaudit/auth/` hold live session cookies for local and staging.
- **State modules:** these execute arbitrary Python against the app.
- **`uiaudit serve`:** an HTTP server that can modify findings files.
- **The inline review UI:** it shows screenshots and page-derived finding text inside the Claude conversation, and can send context to the model.
- **The critique subagent:** it reads rendered page text and screenshots. Page content is untrusted input and could contain instructions aimed at the agent.
- **Staging runs:** these act on a shared environment that a non-read-only state could mutate.

### Authentication and authorization

The harness never stores passwords. `uiaudit auth {env}` opens a headed browser for a human to sign in as a dedicated test user, and saves only the resulting session. It reuses the app's real auth path; there are no auth bypasses in the app.

### Threats

#### Session file leakage

A committed or world-readable `storageState` gives staging access to whoever reads it. Mitigations:

- `.uiaudit/` is gitignored by the template.
- Auth files are written with mode 600.
- `uiaudit doctor` fails if an auth file is tracked by git.
- The test user has no admin rights.

#### Preview server exposed on the network

Mitigations:

- `uiaudit serve` binds 127.0.0.1 only. There is no flag to bind elsewhere in v1.
- Write endpoints require a per-session token printed at startup and embedded in the served page.

#### Prompt injection through audited content

A page, or a resume rendered on a share page, could contain text instructing the critique agent. Mitigations:

- The `design-reviewer` agent definition limits its tools to file reads and `uiaudit findings add`.
- `findings add` validates against the schema, rejects unknown fields, and only appends.
- `UpdateContext` and `SendMessage` from the review UI carry only finding IDs, rule IDs, statuses, and fixed button text, never text taken from the audited page.

#### Agent triaging its own findings

If a host ignores app-only visibility, the model could call `set_finding_status` itself. Mitigations:

- Every status change is written to `triage.jsonl` with the surface that made it.
- `uiaudit plan` lists in its header any finding whose status was last changed by a surface other than the review UI or the CLI.

#### Staging mutation or spend

See the resolved issue "Staging policy". The MCP server exposes the same `allow_paid` flag as the CLI, defaulting to false, so an agent cannot spend money without being told to.

## Privacy

Screenshots capture whatever the page renders. On voice-resume that means resumes and voice-related UI, which are personal data. Policy:

- Staging runs use only the dedicated test account and its seeded fixture resumes.
- Run directories stay local and gitignored.
- No screenshot, DOM text, or audio leaves the machine except into the developer's own Claude session: the critique agent, or the inline review UI, which sends thumbnails and annotated screenshots to the Claude host.
- Client engagements will need a separate data-handling policy before the tool touches a client's production data. That is out of scope for v1.

## Logging

Each run writes `manifest.json` (see "Findings and run format"):

- engine version, git SHA, and dirty flag;
- environment and base URL;
- start and end time;
- cells planned and cells captured;
- per-cell duration and error.

The `--json` output repeats the summary.

Never logged:

- cookies or `storageState` contents;
- request or response bodies from mocked or real API calls;
- the full text of audited pages.

## Dependencies

### Language and packaging: Python 3.12 with uv

**Reversal cost**: high

These are the studio's server-side defaults, and they match the first consumer's backend toolchain.

### Browser driver: Playwright for Python (Chromium)

**Reversal cost**: high

It is a scripted, deterministic driver that can reach states: fake media devices, network mocks, stored sessions, and viewport and theme emulation.

Agent-driven browsers (DevTools MCP, agent-browser, Claude in Chrome) are kept for ad-hoc investigation, not capture. See Alternatives considered.

### Distribution: Copier for the app layer, uv tool / uvx for the engine

**Reversal cost**: high

The user chose this hybrid.

- Copier's three-way `update` keeps per-app edits to states and config while pulling template fixes.
- A pinned engine means two apps on the same tag measure the same way.

### Accessibility engine: axe-core via axe-playwright-python

**Reversal cost**: low

Results are normalized into findings, so the engine can be swapped behind `axe.py`.

### Review UI: Prefab (prefab-ui), pinned to an exact version

**Reversal cost**: low

It lets the views be written in Python and served three ways from one definition: as an MCP App through FastMCP, as a FastAPI page, and as a static HTML export. It is pre-1.0 and minor versions can break the API, so the engine pins an exact version. FastMCP's apps extra pulls it in with only a minimum version, so the explicit pin matters. Prefab code is confined to `views/`, so replacing it means rewriting views only.

### Local review host: FastAPI with uvicorn

**Reversal cost**: low

It is local-only and matches the studio's backend stack.

### Image annotation and diff: Pillow

**Reversal cost**: low

It draws finding boxes, makes thumbnails, and computes diff images in the engine's own Python process. The Compare view replaces the reg-cli report that was planned before, so there is no Node dependency.

### Cross-run analysis: DuckDB over JSONL

**Reversal cost**: low

It gives SQL over files with no server.

### MCP framework: FastMCP

**Reversal cost**: low

It is Python-native, supports stdio, and has an in-memory client for tests. The tools are thin wrappers, so swapping frameworks is an afternoon.

## Build order

Each stage below ships something usable and lists what it adds, what it leaves for later, and checks that prove it is done.

### First local audit of voice-resume

**Delivers**: Running `uiaudit run --env local` in voice-resume produces the full screenshot matrix and axe findings for three real states. Builds on the resolved issues "Findings and run format" and "Engine contract".

**Adds**:

- **Engine package skeleton with `schema`, `doctor`, `auth`, `run`, `findings add`, and a findings-level `diff` (new/closed/unchanged by fingerprint)**
- **`uiaudit mcp` stdio server with `doctor`, `start_run`, `get_run`, `diff`, `list_findings`, `add_findings`, `schema`; the other tools arrive with the stages that need them**
- **Config loader, state loader, fake-microphone launch, `page.route` mocks, bounding-box capture, run manifest**
- **Copier template with config, example state, skill, design-reviewer agent stub, `.mcp.json`**
- **voice-resume adoption via `copier copy`, with `recording`, `mic-denied`, and `upload-500` states**

**Not yet**:

- Review UI and its hosts, annotation, critique agent behavior, `plan`, source stamps, fix loop, `ratchet`, staging environment, design reference ("Check against the intended design")

**Done when**:

- `uv run pytest -q` passes in dmg-uiaudit, including `tests/test_mcp_parity.py`: an in-memory MCP client gets output identical to the CLI's `--json` for `doctor`, `diff`, and `schema`, and `start_run` then `get_run` reaches a completed summary.
- In voice-resume, `uiaudit doctor --json` exits 0, and `claude mcp list` shows `uiaudit` connected.
- `uiaudit run --env local --json` exits 0 or 1 with `cells_captured == cells_planned`.
- Two consecutive runs followed by `uiaudit diff --json` (latest two runs) report 0 new and 0 closed findings.
- A full run completes in under 5 minutes on the development Mac.

### Review and compare findings

**Delivers**: A reviewer browses the matrix with annotated screenshots, compares any cell before and after with a slider, and triages findings in a local browser or inline in Claude, then exports the same view to one HTML file. The inline host's image and slider handling follow the open issue "Inline review UI inside Claude", whose half-day test is this stage's first task.

**Adds**:

- Engine core, template, voice-resume adoption
- **Half-day test of the inline review UI in Claude desktop, run first; its results decide the inline host's image and slider handling**
- **`annotate.py`: annotated PNGs, thumbnails, and diff images**
- **`views/` with Runs, Matrix, Cell, Compare (slider, side by side, diff), and Plan placeholder views**
- **Three hosts: `open_audit` MCP App with app-only helper tools, `uiaudit serve`, `uiaudit report`**
- **Triage writes to `findings.jsonl`, `triage.jsonl`, and `uiaudit.ignore.toml`; `UpdateContext` and `SendMessage` in the inline host**
- **`design-reviewer` subagent that appends `source=critique` findings via `findings add`**

**Not yet**:

- Source stamps, `plan`, fix loop, `ratchet`, staging, design reference

**Done when**:

- `uv run pytest tests/views -q` passes: every view builds for all three hosts from a fixture run, and an accept request through the serve host changes `status` in `findings.jsonl` and appends to `triage.jsonl`.
- `uv run pytest tests/test_mcp_app.py -q` passes: an in-memory FastMCP client calls `open_audit` and receives a Prefab UI, and `set_finding_status`, `get_cell`, and `get_compare` carry app-only visibility.
- `uiaudit findings add --json < invalid.json` exits 2.
- `uiaudit report --run latest --out /tmp/r.html` produces a file that loads offline with no network requests, and its Compare view has a working slider.
- In Claude desktop, rejecting a finding in the inline view changes it on disk: `jq -r 'select(.id=="F-xxxxxx") | .status' .uiaudit/runs/<run_id>/findings.jsonl` prints `rejected`.

### Executable remediation plan

**Delivers**: `uiaudit plan` turns accepted findings into a spec-kit-format `tasks.md` with exact file paths. Waits on the open issue "Mapping findings to source files".

**Adds**:

- Engine core, template, voice-resume adoption, review UI and hosts, annotation, critique agent
- **Dev-only source stamping in the local environment, recorded per finding as `component`**
- **`uiaudit plan` with deterministic phases, file grouping, `[P]` markers, finding IDs, and done-checks**

**Not yet**:

- Fix loop, `ratchet`, staging, design reference

**Done when**:

- On voice-resume, every accepted axe finding has a `component` file path or is explicitly listed as unassigned in the plan.
- Running `uiaudit plan` twice produces byte-identical skeletons (`diff` of the two outputs is empty).
- Each task line matches `^- \[ \] T\d{3}( \[P\])? \[US\d+\] .+ (src|app)/\S+`.

### Fix loop and regression tests

**Delivers**: Claude Code can execute the plan one commit per task, confirm closure on re-run, and lock each fix in with a generated regression test.

**Adds**:

- Everything from the first local audit, review and compare, and the remediation plan
- **`--only` partial re-runs; after a re-run, the Compare view opens on the re-captured cells with the pre-fix run selected**
- **`uiaudit ratchet` emitting pytest guards (axe rule assertions per cell; screenshot baselines with a pixel threshold) into the consumer repo**
- **Skill instructions for the fix loop**

**Not yet**:

- Staging environment, design reference, regression tests in CI (see "Where regression tests run")

**Done when**: In voice-resume, after one fix commit plus `uiaudit ratchet`, `uv run pytest tests/uiaudit -q` passes. `git revert` of the fix commit makes `uv run pytest tests/uiaudit -q` fail.

### Audit staging on demand

**Delivers**: The same audit runs against staging when someone asks for it, read-only and without spending money unless told to. Follows the resolved issue "Staging policy".

**Adds**:

- Everything from the earlier stages through the fix loop
- **`staging` environment behavior per "Staging policy", `--allow-paid` gate**

**Not yet**:

- Second consumer app, client-facing report template

**Done when**:

- `uiaudit run --env staging --json` completes, and a SQL count of the test account's rows in staging Postgres is identical before and after.
- Without `--allow-paid`, the run summary lists every Replicate-calling cell as skipped with reason `paid`, and no Replicate call appears in the run's network log.

### Check against the intended design

**Delivers**: When a consumer repo supplies design tokens, every audit also flags off-palette colors, off-scale type, spacing, and radii, and any drift between the shipped theme and the design; reference screens can be compared against the live app with the slider. It needs only the first local audit and review and compare, and can be built any time after them.

**Adds**:

- Everything from the first local audit and review and compare
- **`[design]` config section and token loader (DTCG JSON and CSS custom properties)**
- **Computed-style capture per visible element and the token detector with `design-drift` collapsing**
- **Reference screens as a third Compare source and as critique-agent input, with critique findings capped below confidence 1 and excluded from `ratchet`**
- **voice-resume adoption: a token file exported or hand-written from its Claude Design system, and two reference screens**

**Not yet**:

- Figma or other design-tool imports, perceptual or layout-level comparison of reference screens

**Done when**:

- `uv run pytest tests/test_design_tokens.py -q` passes, including a fixture page with one off-palette color and one off-scale font size that yields exactly those two detector findings, and a fixture theme that disagrees on one token used by ten elements that yields exactly one `design-drift` finding.
- In voice-resume, `uiaudit run --env local --json` with `[design]` configured completes, and removing the `[design]` section produces no token findings.
- `uiaudit ratchet` on a run containing a reference-screen critique finding emits no test for it.

## Open issues

### Mapping findings to source files

**Reversal cost**: high

**Problem**: Plan quality depends on mapping each finding to the exact source file and line. Older inspector tools relied on React's `_debugSource`, which React 19 removed. voice-resume's React version, and whether it uses the Babel or SWC Vite plugin, are unverified.

**Options**:

- **Our own tiny dev-only Vite plugin, shipped in the template.** It adds `data-uiaudit-src="file:line"` to host JSX elements at transform time, and the harness reads the attribute from each flagged element. It does not depend on React internals.
- **A third-party inspector plugin** (react-dev-inspector or a click-to-component style plugin). Nothing to write, but compatibility with React 19 and SWC must be checked per app.
- **No stamping.** The agent maps selectors to files by grepping. Nothing to build, but attribution becomes a guess, and plans churn between runs.

**Proposed**: Our own plugin. Attribute injection at build time works across React versions, and the template can own it.

**Next step**: A one-hour spike in voice-resume as the first task of the remediation-plan stage, recording the React version and Vite React plugin variant. If the spike fails, fall back to the second option.

### Repository and command name

**Reversal cost**: low

**Problem**: The repo path appears in every consumer's Copier answers file and pinned `uvx` commands.

**Options**:

- `DMG-Venture-Studio/dmg-uiaudit`, command `uiaudit`
- A product-style name chosen now in case it becomes a client-facing offering

**Proposed**: `dmg-uiaudit` / `uiaudit`. Renaming before a second consumer exists is cheap.

**Next step**: Fili confirms when creating the repo.

### Where regression tests run

**Reversal cost**: low

**Problem**: The ratchet's regression tests drive the harness against a running app, so running them in CI needs an app to point at. With the nightly staging run dropped, the only automated place they would run is on pull requests.

**Options**:

- Local only in v1: the fix-loop skill runs them after every fix, plus an optional pre-push hook
- Railway PR environments for voice-resume, if enabled
- Start the app inside GitHub Actions (frontend dev server plus API with a Postgres service container)

**Proposed**: Local only in v1. Revisit when a second app adopts the tool, using Railway PR environments if they are already enabled.

**Next step**: Fili checks whether voice-resume has Railway PR environments enabled.

### Inline review UI inside Claude

**Reversal cost**: low

**Problem**: Several behaviors the inline host depends on are unverified in Claude desktop:

- how large an image payload the MCP App iframe accepts, and whether it can load images any other way;
- whether `CallTool` round trips work for triage;
- whether `UpdateContext` reaches the model;
- whether the `Embed`-based slider runs inside the host's iframe;
- whether app-only tool visibility is enforced.

**Options**:

- Spike in Claude desktop first, then build the views against the local browser host, adding the inline host on whatever the spike proved
- Build the local browser host only, and drop the inline host
- Build the inline host first

**Proposed**: Spike first. The views are shared, so the local browser host is never blocked; the spike only decides image sizing and the slider fallback for the inline host.

**Next step**: A half-day spike as the first task of the review-and-compare stage, with each result recorded under this issue.

## Resolved issues

### Findings and run format

**Decision**: Accepted as proposed (2026-10-01): custom Pydantic `Finding` and `RunManifest` with fingerprint-derived IDs. SARIF may be added later as an export only.

**Reversal cost**: high

**Problem**: Everything downstream (diff, serve, plan, ratchet, the SQL view, a future client report) reads this format. Two things are expensive to change once runs exist:

- **The field set.** Changing it after runs exist breaks history.
- **How a finding is identified across runs.** Matching the same problem from run to run is what "closed" and "new" mean.

**Options**:

- **Custom Pydantic model with a fingerprint ID** (sketched below). It fits screenshots, states, and bounding boxes exactly. It is ours to maintain.
- **Sequential per-run IDs.** These are simplest, but diffing becomes heuristic matching, and "closed" stops being trustworthy.
- **SARIF.** It is the standard static-analysis interchange format, but it is verbose and has no natural home for state, viewport, theme, or bounding boxes. An export to SARIF can be added later either way.

```python
class Finding(BaseModel):
    id: str            # "F-" + first 6 hex of sha256(fingerprint)
    fingerprint: str   # source|rule|route|state|viewport|theme|normalized_selector
    run_id: str
    source: Literal["axe", "lighthouse", "detector", "critique"]
    rule: str          # e.g. "button-name"; critique uses a short slug
    severity: Literal["critical", "high", "medium", "low"]
    route: str
    state: str
    viewport: int
    theme: Literal["light", "dark"]
    selector: str | None
    bbox: tuple[float, float, float, float] | None   # x, y, w, h in CSS px
    evidence_path: str                                # cell screenshot, relative to run dir
    component: str | None                             # "src/x.tsx:42" from source stamp
    message: str
    confidence: float = 1.0                           # < 1.0 only for critique
    status: Literal["open", "accepted", "rejected", "fixed"] = "open"

class RunManifest(BaseModel):
    run_id: str
    engine_version: str
    engine_sha: str
    engine_dirty: bool
    env: Literal["local", "staging"]
    base_url: str
    started_at: datetime
    ended_at: datetime
    cells_planned: int
    cells_captured: int
    cell_errors: list[dict]
```

`uiaudit schema` prints the JSON Schema of `Finding`. The normalized selector strips generated class hashes and nth-child indices, so a CSS rebuild does not orphan fingerprints.

**Proposed**: The custom model with fingerprint IDs. Stable identity is the property everything else needs; sequential IDs cannot provide it, and SARIF can be an export later.

**Next step**: Fili accepts or edits the field list and fingerprint recipe before the first local audit starts.

### Engine contract: CLI, MCP server, config, state files

**Decision**: Accepted the agent-first CLI and state-module rules as proposed, plus an MCP server in v1 (2026-10-01). The MCP server is a thin stdio wrapper over the same command functions the CLI calls, never a second implementation; see Interfaces > MCP server. The CLI remains the CI and human interface, and neither surface calls a model.

**Reversal cost**: high

**Problem**: Every consumer repo, every CI workflow, and every agent prompt depends on how the CLI behaves and how state modules are written. The contract also has to keep app-specific logic out of the engine, which is what keeps it reusable.

**Options**:

- **Agent-first CLI with file-loaded state modules** (detailed below). Agents and CI share one interface, and the CLI never calls a model.
- **A Python library driven through pytest-playwright fixtures.** It is familiar, but agents must parse pytest output, and the review, plan, and preview commands have no natural home.
- **An MCP server.** It gives native agent tools, but CI and humans still need a CLI, and it adds a long-lived process. An MCP wrapper over the CLI can come later.

CLI contract:

- **Every command:**
  - accepts `--json`;
  - never prompts, except `auth`, which is explicitly interactive;
  - exits 0 when clean, 1 when findings are at or above `fail_on`, 2 on a config or validation error, 3 on an environment problem (app unreachable, session expired, browser missing, version mismatch in CI);
  - includes the fixing command in every error message.
- **The CLI never calls a model.** Judgment enters only through `uiaudit findings add`.
- **Command list** (no `init`; Copier owns scaffolding): `doctor [--fix]`, `auth {env}`, `run --env {env} [--only route/state] [--allow-paid]`, `diff [run_a run_b]`, `findings add`, `schema`, `serve`, `report`, `plan`, `ratchet`.
- **`doctor --fix`** installs Chromium into the tool environment.

Config sketch:

```toml
requires = "v0.1.0"
fail_on = "high"
viewports = [375, 768, 1440]
themes = ["light", "dark"]

[env.local]
base_url = "http://localhost:5173"
mocks = true
source_stamps = true

[env.staging]
base_url = "https://staging.example.invalid"
mocks = false
read_only = true

[[routes]]
path = "/editor/{resume_id}"
states = ["default", "recording", "mic-denied", "upload-500", "empty"]
params = { resume_id = "fixture-resume-1" }
```

State module sketch, loaded by file path from `uiaudit/states/*.py`, never imported as part of the app:

```python
from uiaudit.states import state, StateContext

@state("upload-500", requires_mocks=True)
async def upload_500(ctx: StateContext) -> None:
    await ctx.page.route("**/api/uploads", lambda r: r.fulfill(status=500))
    await ctx.page.get_by_role("button", name="Upload resume").click()
```

State modules may import only the standard library, Playwright, and `uiaudit`. They may not import the app's backend packages. The rule is: nothing app-specific in the engine, nothing engine-internal in the app.

**Proposed**: The agent-first CLI with file-loaded states. It is the only option where the coding agent, CI, and a human all use the identical interface, and the import restriction is what keeps the engine reusable across apps.

**Next step**: Fili accepts or edits the exit-code table, command list, and state-module rules before the first local audit starts.

### Staging policy

**Decision**: Accepted as proposed (2026-10-01): read-only staging against a dedicated seeded test account, mock-dependent states local-only, Replicate-calling states only with `--allow-paid`, seeding via HTTP or fixture SQL.

**Reversal cost**: high

**Problem**: Staging is shared, holds personal-data-shaped content, and calls Replicate, which costs money per call. Two kinds of run can do damage:

- **A careless state** can mutate data that other people rely on.
- **A full matrix with voice-masking states** can quietly spend money every night.

**Options**:

- **Read-only, non-mocked staging against a dedicated seeded test account.** Mock-dependent states run only locally, and states that call Replicate run only with `--allow-paid`. Seeding happens via HTTP API calls or a fixture SQL file the harness executes, never through the app's ORM.
- **Full parity with mutations, against an ephemeral tenant that is reset nightly.** Coverage is greater, but it needs reset tooling built and maintained.
- **Staging limited to unauthenticated public routes.** It is safest, but loses the authenticated editor states that matter most.

**Proposed**: The first option. It covers authenticated screens and real WorkOS redirects, with spend and mutation made opt-in.

**Next step**: Fili confirms the policy and creates the staging test account plus fixture resumes before staging is audited.

### Design reference from Claude Design

**Decision**: Accepted as proposed (2026-10-08): an optional `[design]` section with a token file and reference screens, tokens built first. Token checks produce deterministic `source=detector` findings; reference screens only feed the Compare view and the critique agent, and their findings are never ratcheted.

**Reversal cost**: low

**Problem**: voice-resume is designed in Claude Design, but the audit only judges against axe rules, impeccable's general taste, and `DESIGN.md` prose. It has no record of what the screens were meant to look like, so it cannot catch drift from the intended design, such as an almost-right gray or an off-scale font size.

**Options**:

- **Tokens plus optional reference screens.** An optional `[design]` section in `uiaudit.toml` points at:
  - a token file (DTCG JSON or CSS custom properties) for colors, type scale, spacing, and radii;
  - reference screens mapped to cell keys, for example `"editor/recording@375-light" = "design/editor-recording.png"`.

  Tokens drive a deterministic detector that checks the computed styles of visible elements and emits `source=detector` findings such as `off-palette-color` and `off-scale-font-size`. Reference screens become a third source in the Compare view and an "intended" image for the critique agent. Findings from them are `source=critique` with confidence below 1 and are never ratcheted automatically.
- **Tokens only.** Cheapest, fully deterministic, and nothing goes stale.
- **Neither.** Rely on `DESIGN.md` prose and impeccable.

**Proposed**: Tokens plus optional reference screens, with tokens first.

- Tokens are the high-value part. They are deterministic and catch exactly the near-miss styling that coding agents introduce.
- Reference screens help review but go stale as soon as the app moves on, which is why they never produce hard findings.
- The app's shipped Tailwind theme is the tokens actually in effect; Claude Design's are the intent. When the two disagree, the detector raises one design-drift finding for that token, not one per element.

**Next step**: Fili exports voice-resume's design system and two screens from Claude Design to confirm what formats come out. Whether Claude Design exports tokens in a machine-readable form is unverified; if it does not, the token file is written by hand once from the design system.

## Alternatives considered

### Claude in Chrome as the capture layer

It is attractive because it drives your real logged-in browser. It lost because it requires `/login` and cannot run in CI, and because of the Claude Desktop native-host conflicts on macOS. It stays useful for ad-hoc inspection.

### Agent-driven browsers as the capture layer

The options were Chrome DevTools MCP (bundled a11y skill, Lighthouse tool, `--autoConnect` to a live session), Playwright CLI, and Vercel agent-browser. They are excellent for an agent investigating a problem, but a model choosing clicks is not a fixed instrument. Capture must be scripted so reruns are comparable.

### Unlighthouse for coverage

It crawls a sitemap and links and runs Lighthouse in parallel across a whole site. It lost as the core because it sees only routes, not states, and does not get behind auth. It may be added later for public share pages.

### gstack `/design-review` as the whole pipeline

It already does audit, fix with one commit per finding, and before/after screenshots. It lost because it insists on owning the browser layer and bundles a large opinionated suite. Its per-finding commit discipline is adopted in the fix loop.

### AccessLint as the a11y engine

It offers WCAG 2.2 live-DOM audits and branch diffing as a Claude Code plugin. It is kept as an optional consumer-side plugin rather than the engine's dependency; axe via Playwright keeps capture in one Python process.

### Other distribution models

- **Engine as a dev dependency in the app's lockfile:** it puts browser and axe dependencies into an app environment that does not need them.
- **git subtree:** it is bidirectional, but clutters history and relies on people remembering `subtree push`.
- **shadcn registry:** it can distribute any files, but means a Node CLI for a Python tool, with no merge-based update.
- **git submodule:** clones and cloud agent sandboxes skip `--recursive`.
- **Symlinked skill with a SessionStart self-heal hook:** superseded once the skill became a Copier-managed file.

### Build inside voice-resume first, extract later

This was proposed to avoid designing without a consumer. It was superseded because voice-resume is the consumer from day one, and the separate-repo choice forces the engine/app boundary early.

### Electron or Tauri desktop app for the review UI

A desktop app gives a Dock icon and a double-click install. Electron lost because Playwright already downloads Chromium, so Electron would ship a second copy plus a Node process just to manage the Python engine. Tauri lost because it still needs Python bundled as a sidecar plus macOS notarization. A local browser page installed as a Chrome app window gives the Dock icon with nothing to package, and a hosted version is the better answer for clients.

### Hand-written React bundle for the review UI

One React bundle over the command layer could run in every host. Prefab gives the same one-definition, many-hosts shape while keeping the views in Python, which matches the studio's stack.

### Nightly staging audits

A scheduled run against staging would catch regressions without anyone asking. It was dropped because UI audits matter when someone is changing UI; a scheduled run of an unchanged UI finds nothing new.

### reg-cli for before/after diffs

It produces a good single-file diff report from any two screenshot folders. The Compare view in the review UI covers the same need, with a slider, without a Node dependency.
