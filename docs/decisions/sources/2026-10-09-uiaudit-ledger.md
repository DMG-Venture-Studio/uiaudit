# Extraction ledger

Every atomic fragment of the source notes, where it landed, and on what authority. Allowed values are defined in the ramble-to-design skill's `references/extraction.md`. Do not use `|` inside cells.

Provenance note: `confirmed` marks an assistant proposal the user explicitly ratified in a later turn ("fully aligned" line 37, "i'm aligned" line 100, "you can" line 113), at gist level. Mechanism details beneath that gist stay `agent` and route to open issues.

| ID | Source | Summary | Kind | Provenance | Cost | Disposition | Target |
|---|---|---|---|---|---|---|---|
| L1 | docs/design/sources/conversation-2026-10-01.md:3-5 | Snapshot note: user turns verbatim, assistant turns condensed | context | measured | low | discard | provenance note for this snapshot, not design content |
| L2 | docs/design/sources/conversation-2026-10-01.md:8 | User wants a crawler- or Claude in Chrome-driven UI design audit plus remediation plan run from Claude Code | purpose | stated | high | background | Background |
| L3 | docs/design/sources/conversation-2026-10-01.md:11 | Audit splits into a deterministic layer and a judgment layer | context | agent | low | background | Background |
| L4 | docs/design/sources/conversation-2026-10-01.md:12 | Claude in Chrome unusable as crawler: needs /login (no CI) and conflicts with Claude Desktop native host on macOS | finding | measured | high | constraint | Constraints |
| L5 | docs/design/sources/conversation-2026-10-01.md:13 | Chrome DevTools MCP plugin bundles a11y skill; lighthouse_audit excludes performance; autoConnect reuses logged-in Chrome | finding | measured | low | background | Alternatives considered |
| L6 | docs/design/sources/conversation-2026-10-01.md:14 | Playwright CLI or agent-browser as lower-token browser layer | context | agent | low | background | Alternatives considered |
| L7 | docs/design/sources/conversation-2026-10-01.md:15 | Unlighthouse crawls and runs Lighthouse site-wide; public routes only | finding | measured | low | background | Alternatives considered |
| L8 | docs/design/sources/conversation-2026-10-01.md:16 | AccessLint offers WCAG 2.2 live-DOM audits and branch diffing | finding | measured | low | background | Alternatives considered |
| L9 | docs/design/sources/conversation-2026-10-01.md:17 | impeccable as the single judgment rubric for consumer repos | choice | agent | low | background | Background |
| L10 | docs/design/sources/conversation-2026-10-01.md:18 | gstack design-review does audit-fix loop but owns the browser layer | finding | measured | low | background | Alternatives considered |
| L11 | docs/design/sources/conversation-2026-10-01.md:19 | Crawlers see routes not states; Aside risk is concentrated in states | finding | agent | high | background | Background |
| L12 | docs/design/sources/conversation-2026-10-01.md:20 | Scripted route x state x viewport x theme matrix in playwright-python with storageState | choice | confirmed | high | decision | Interfaces |
| L13 | docs/design/sources/conversation-2026-10-01.md:21 | Group remediation by component not page | behavior | confirmed | low | scenario | Scenarios |
| L14 | docs/design/sources/conversation-2026-10-01.md:22 | Ratchet each fixed finding into a test | behavior | confirmed | high | milestone | Build order |
| L15 | docs/design/sources/conversation-2026-10-01.md:25 | User wants a reusable package across projects given frontend volume | outcome | stated | high | goal | Goals |
| L16 | docs/design/sources/conversation-2026-10-01.md:28-29 | Reusable core is the glue: runner, schema, plan and fix skills, ratchet, auth adapters | choice | confirmed | high | decision | Interfaces |
| L17 | docs/design/sources/conversation-2026-10-01.md:30 | Findings queryable with SQL across portfolio apps | outcome | confirmed | high | goal | Goals |
| L18 | docs/design/sources/conversation-2026-10-01.md:31 | Do not vendor or fork third-party skills | exclusion | confirmed | low | non-goal | Non-goals |
| L19 | docs/design/sources/conversation-2026-10-01.md:32 | Build inside Aside first then extract | choice | agent | high | discard | superseded by user choice of a separate repo at line 51 |
| L20 | docs/design/sources/conversation-2026-10-01.md:33 | Audit plus plan as fixed-fee consulting deliverable | context | confirmed | low | background | Background |
| L21 | docs/design/sources/conversation-2026-10-01.md:34 | Repo name DMG-Venture-Studio/dmg-uiaudit and command uiaudit | choice | agent | low | open-issue | Repository and command name |
| L22 | docs/design/sources/conversation-2026-10-01.md:37 | User fully aligned with turn 2 direction | context | stated | low | discard | ratification marker used to set provenance of lines 28-33 |
| L23 | docs/design/sources/conversation-2026-10-01.md:40 | Consumer prerequisites: plugins, impeccable init, WorkOS test user | instruction | agent | low | discard | consumer-repo setup, lives in template README; implementer call |
| L24 | docs/design/sources/conversation-2026-10-01.md:41 | Finding field list | contract | confirmed | high | open-issue | Findings and run format |
| L25 | docs/design/sources/conversation-2026-10-01.md:42 | uiaudit.toml fields and default viewports | contract | confirmed | high | open-issue | Engine contract |
| L26 | docs/design/sources/conversation-2026-10-01.md:43 | States as Python setup functions; fake mic flags; page.route mocks | choice | confirmed | high | open-issue | Engine contract |
| L27 | docs/design/sources/conversation-2026-10-01.md:44 | Phase 1 acceptance: count equals matrix; identical reruns; under 5 minutes | behavior | confirmed | low | open-issue | Engine contract |
| L28 | docs/design/sources/conversation-2026-10-01.md:45 | Critique subagent appends findings; plan groups by component; human triage; rejects become ignore rules | behavior | confirmed | high | milestone | Build order |
| L29 | docs/design/sources/conversation-2026-10-01.md:46 | One commit per fix; rerun affected cells; guard per fix; revert fails CI | behavior | confirmed | high | milestone | Build order |
| L30 | docs/design/sources/conversation-2026-10-01.md:47 | Second app then extract | choice | agent | low | discard | superseded by separate-repo-first at line 51 |
| L31 | docs/design/sources/conversation-2026-10-01.md:48 | Asked local vs staging vs both | question | agent | low | discard | answered by user at line 51 |
| L32 | docs/design/sources/conversation-2026-10-01.md:51 | Separate repo | choice | stated | high | decision | Interfaces |
| L33 | docs/design/sources/conversation-2026-10-01.md:51 | CLI driven by an agent, installed into the consuming repo | choice | stated | high | decision | Interfaces |
| L34 | docs/design/sources/conversation-2026-10-01.md:51 | Dogfood on voice-resume | choice | stated | high | milestone | Build order |
| L35 | docs/design/sources/conversation-2026-10-01.md:51 | Support both local and staging environments | choice | stated | high | decision | Interfaces |
| L36 | docs/design/sources/conversation-2026-10-01.md:54 | Nothing voice-resume-specific in the engine | behavior | confirmed | high | open-issue | Engine contract |
| L37 | docs/design/sources/conversation-2026-10-01.md:55-56 | Agent CLI contract: --json, no prompts, exit codes 0-3, fix in error text | contract | confirmed | high | open-issue | Engine contract |
| L38 | docs/design/sources/conversation-2026-10-01.md:57 | uiaudit schema prints findings JSON Schema | contract | confirmed | low | open-issue | Findings and run format |
| L39 | docs/design/sources/conversation-2026-10-01.md:58 | CLI stays model-free; agent appends via findings add with validation | contract | confirmed | high | open-issue | Engine contract |
| L40 | docs/design/sources/conversation-2026-10-01.md:59-61 | Staging non-mocked, read-only, dedicated seeded test account; mocked states local only | behavior | confirmed | high | open-issue | Staging policy |
| L41 | docs/design/sources/conversation-2026-10-01.md:62 | Paid Replicate states behind --allow-paid | behavior | confirmed | high | open-issue | Staging policy |
| L42 | docs/design/sources/conversation-2026-10-01.md:63 | CI cadence: local on demand, PR envs if enabled, nightly staging failing on new high findings | choice | agent | low | open-issue | Where regression tests run |
| L43 | docs/design/sources/conversation-2026-10-01.md:66 | User asks about symlink | question | stated | low | discard | clarified at line 72 as about install model |
| L44 | docs/design/sources/conversation-2026-10-01.md:69 | Symlinked skill plus SessionStart hook | choice | agent | low | discard | superseded by Copier-managed skill at line 109 |
| L45 | docs/design/sources/conversation-2026-10-01.md:72 | User meant symlink for the install model | question | stated | low | discard | answered by hybrid decision at line 100 |
| L46 | docs/design/sources/conversation-2026-10-01.md:75-76 | Editable tool install; requires pin in config; CI via uvx at a git tag | choice | confirmed | high | decision | Dependencies |
| L47 | docs/design/sources/conversation-2026-10-01.md:77 | Run manifest records harness SHA and dirty flag | contract | confirmed | low | open-issue | Findings and run format |
| L48 | docs/design/sources/conversation-2026-10-01.md:78 | States loaded by file path; only stdlib, Playwright, uiaudit API | contract | confirmed | high | open-issue | Engine contract |
| L49 | docs/design/sources/conversation-2026-10-01.md:79 | Seed via HTTP or fixture SQL, never app ORM | choice | confirmed | high | open-issue | Staging policy |
| L50 | docs/design/sources/conversation-2026-10-01.md:80 | doctor --fix installs Chromium into tool env | behavior | agent | low | discard | low reversal cost, implementer call; listed under the engine contract |
| L51 | docs/design/sources/conversation-2026-10-01.md:83 | User considering copying the repo locally | question | stated | low | discard | answered by hybrid decision at line 100 |
| L52 | docs/design/sources/conversation-2026-10-01.md:83 | User wants local previews of audit results | outcome | stated | high | goal | Goals |
| L53 | docs/design/sources/conversation-2026-10-01.md:83 | User wants a solid plan the source repo can implement | outcome | stated | high | goal | Goals |
| L54 | docs/design/sources/conversation-2026-10-01.md:86-89 | Distribution options: Copier, subtree, shadcn registry, submodule | context | measured | low | background | Alternatives considered |
| L55 | docs/design/sources/conversation-2026-10-01.md:90 | Hybrid: engine installed and pinned; app layer scaffolded by Copier | choice | confirmed | high | decision | Dependencies |
| L56 | docs/design/sources/conversation-2026-10-01.md:91 | uiaudit serve: local matrix grid with finding boxes from captured bounding boxes | behavior | confirmed | low | decision | Interfaces |
| L57 | docs/design/sources/conversation-2026-10-01.md:92 | Browser triage writes status back to findings | behavior | confirmed | low | scenario | Scenarios |
| L58 | docs/design/sources/conversation-2026-10-01.md:93 | uiaudit report exports a static single-file HTML view | contract | confirmed | low | decision | Interfaces |
| L59 | docs/design/sources/conversation-2026-10-01.md:94 | Visual diff via reg-cli | choice | confirmed | low | discard | superseded by the Compare view with slider requested at line 150 |
| L60 | docs/design/sources/conversation-2026-10-01.md:95 | Deterministic file attribution via dev-only source stamping; React 19 compatibility unverified | choice | confirmed | high | open-issue | Mapping findings to source files |
| L61 | docs/design/sources/conversation-2026-10-01.md:96 | Plan emitted as spec-kit tasks.md format | contract | confirmed | high | decision | Interfaces |
| L62 | docs/design/sources/conversation-2026-10-01.md:97 | Plan skeleton deterministic; agent writes only story names and fix text | behavior | confirmed | high | decision | Interfaces |
| L63 | docs/design/sources/conversation-2026-10-01.md:100 | User chooses the hybrid distribution first | choice | stated | high | decision | Dependencies |
| L64 | docs/design/sources/conversation-2026-10-01.md:100 | User asks why the harness matters | question | stated | low | discard | answered in conversation; rationale captured in Background |
| L65 | docs/design/sources/conversation-2026-10-01.md:103-104 | Harness is the measuring instrument; its coverage gaps are invisible downstream | context | agent | high | background | Background |
| L66 | docs/design/sources/conversation-2026-10-01.md:105 | Harness is the differentiated sellable part | context | agent | low | background | Background |
| L67 | docs/design/sources/conversation-2026-10-01.md:106 | Harness holds staging credentials and executes code | finding | agent | high | background | Background |
| L68 | docs/design/sources/conversation-2026-10-01.md:107 | One repo: engine in src, Copier template subdirectory, shared version tag | choice | confirmed | high | decision | Interfaces |
| L69 | docs/design/sources/conversation-2026-10-01.md:108 | Editable local engine; doctor warns on requires mismatch; CI uses uvx at tag | choice | confirmed | low | decision | Dependencies |
| L70 | docs/design/sources/conversation-2026-10-01.md:109 | Skill shipped as Copier-managed file | choice | confirmed | low | decision | Interfaces |
| L71 | docs/design/sources/conversation-2026-10-01.md:110 | Scaffold order engine, template, voice-resume adoption with three states | choice | confirmed | high | milestone | Build order |
| L72 | docs/design/sources/conversation-2026-10-01.md:113 | User asks for a spec to hand to Claude Code in a separate repo | instruction | stated | low | discard | determined this deliverable; scaffold approval at this line sets provenance of lines 107-110 |
| L73 | docs/design/sources/aside-memory.md:3 | Aside lets candidates narrate resume sections and publish a shareable page | purpose | stated | high | background | Background |
| L74 | docs/design/sources/aside-memory.md:4 | voice-resume stack: React Tailwind, FastAPI uv Pydantic, WorkOS, Doppler, Postgres RLS, Railway, Replicate | limit | stated | high | constraint | Constraints |
| L75 | docs/design/sources/aside-memory.md:5 | Design via Claude Design then build with Claude Code | context | stated | low | background | Background |
| L76 | docs/design/sources/aside-memory.md:6 | Python and SQL server-side; develops on a Mac | limit | stated | high | constraint | Constraints |
| L77 | docs/design/sources/conversation-2026-10-01.md:28 | Reimplementing browser automation, an a11y engine, or a design rubric is out of scope | exclusion | confirmed | high | non-goal | Non-goals |
| L78 | docs/design/sources/aside-memory.md:7 | Three-person studio operating at low overhead | limit | stated | high | constraint | Constraints |
| L79 | docs/design/sources/conversation-2026-10-01.md:116 | Findings contract accepted as proposed | choice | stated | high | open-issue | Findings and run format |
| L80 | docs/design/sources/conversation-2026-10-01.md:117 | Agent-first CLI accepted and an MCP server added in v1 | choice | stated | high | open-issue | Engine contract |
| L81 | docs/design/sources/conversation-2026-10-01.md:118 | Staging policy accepted as proposed | choice | stated | high | open-issue | Staging policy |
| L82 | docs/design/sources/conversation-2026-10-01.md:121 | User asks what Replicate is | question | stated | low | discard | answered in conversation; context only |
| L83 | docs/design/sources/conversation-2026-10-01.md:122 | User asks what a frontend to drive the tool would look like | question | stated | high | discard | answered by the choice at line 136 |
| L84 | docs/design/sources/conversation-2026-10-01.md:125 | Replicate is a pay-per-compute model API owned by Cloudflare | context | agent | low | discard | not design content; Replicate spend is covered by the staging policy |
| L85 | docs/design/sources/conversation-2026-10-01.md:126 | Electron rejected: duplicate Chromium and a Node runtime | context | agent | low | background | Alternatives considered |
| L86 | docs/design/sources/conversation-2026-10-01.md:127 | Local browser host grown from uiaudit serve | choice | confirmed | low | decision | Interfaces |
| L87 | docs/design/sources/conversation-2026-10-01.md:128 | Same views as an MCP App inline in Claude | choice | confirmed | high | decision | Interfaces |
| L88 | docs/design/sources/conversation-2026-10-01.md:129 | No packaged desktop app; hosted is the client answer later | exclusion | confirmed | low | non-goal | Non-goals |
| L89 | docs/design/sources/conversation-2026-10-01.md:130 | One frontend over the command layer served by several hosts | choice | confirmed | high | decision | Interfaces |
| L90 | docs/design/sources/conversation-2026-10-01.md:131 | Any launch-Claude-Code button lives in the UI layer not the engine | behavior | agent | low | background | Interfaces |
| L91 | docs/design/sources/conversation-2026-10-01.md:134 | User wants to drive the audit from Claude (Cowork capabilities) | outcome | stated | high | scenario | Scenarios |
| L92 | docs/design/sources/conversation-2026-10-01.md:135 | User proposes Prefab for the UI layer | choice | stated | low | decision | Dependencies |
| L93 | docs/design/sources/conversation-2026-10-01.md:136 | User prefers option 1 (local browser) and option 2 (inline MCP App) | choice | stated | high | decision | Interfaces |
| L94 | docs/design/sources/conversation-2026-10-01.md:139 | Prefab views returned from FastMCP app tools | choice | confirmed | low | decision | Dependencies |
| L95 | docs/design/sources/conversation-2026-10-01.md:140 | One view module, three hosts: MCP App, FastAPI page, static export | contract | confirmed | high | decision | Interfaces |
| L96 | docs/design/sources/conversation-2026-10-01.md:141 | SendMessage and UpdateContext connect the UI to the conversation | behavior | confirmed | low | decision | Interfaces |
| L97 | docs/design/sources/conversation-2026-10-01.md:142 | Triage tools app-only so the model cannot triage | behavior | confirmed | high | decision | Interfaces |
| L98 | docs/design/sources/conversation-2026-10-01.md:143 | Pin prefab-ui to an exact version | limit | confirmed | low | decision | Dependencies |
| L99 | docs/design/sources/conversation-2026-10-01.md:144 | Finding boxes drawn into PNGs with Pillow at capture time | choice | confirmed | low | decision | Interfaces |
| L100 | docs/design/sources/conversation-2026-10-01.md:145 | Spike image payloads in the host iframe before the review-and-compare stage | question | confirmed | low | open-issue | Inline review UI inside Claude |
| L101 | docs/design/sources/conversation-2026-10-01.md:146 | Claude desktop renders MCP Apps; terminal Claude Code gets text only | finding | agent | low | open-issue | Inline review UI inside Claude |
| L102 | docs/design/sources/conversation-2026-10-01.md:147 | Spec changes: Prefab dependency, shared views, overlays, spike issue, no React bundle | choice | confirmed | low | decision | Interfaces |
| L103 | docs/design/sources/conversation-2026-10-01.md:150 | User approves the Prefab spec changes | context | stated | low | discard | ratification marker for lines 139-147 |
| L104 | docs/design/sources/conversation-2026-10-01.md:150 | Before/after slider is required | behavior | stated | high | decision | Interfaces |
| L105 | docs/design/sources/conversation-2026-10-01.md:151 | No nightly or scheduled UI audits | exclusion | stated | high | non-goal | Non-goals |
| L106 | docs/design/sources/conversation-2026-10-01.md:151 | Staging milestone becomes on-demand with no nightly workflow | choice | stated | low | milestone | Build order |
| L107 | docs/design/sources/conversation-2026-10-01.md:152 | User asks whether an optional Claude Design reference is worth having | question | stated | low | open-issue | Design reference from Claude Design |
| L108 | docs/design/sources/conversation-2026-10-01.md:155 | Design reference: tokens plus optional reference screens, tokens first, references never ratcheted | choice | confirmed | low | decision | Interfaces |
| L109 | docs/design/sources/conversation-2026-10-01.md:158 | User accepts the design-reference proposal | choice | stated | low | open-issue | Design reference from Claude Design |
| L110 | docs/design/sources/conversation-2026-10-01.md:158 | Flag drift from supplied design tokens as an audit outcome | outcome | confirmed | low | goal | Goals |
| L111 | docs/design/sources/conversation-2026-10-01.md:158 | Token detector and reference screens built as the stage Check against the intended design | choice | confirmed | low | milestone | Build order |
