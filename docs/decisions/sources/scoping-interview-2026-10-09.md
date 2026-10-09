# Source: the scoping interview

Recorded 2026-10-09. The questions asked and Fili's answers, verbatim, with the options
offered and not chosen listed under each question. The decision record `project-scope` cites
this text; it is never edited after it is written.

---

Interview transcript, greenfield intake for uiaudit, 2026-10-08 to 2026-10-09.

Q (Design file): The Claude Design hand-off is Aside's UI (voice-resume), not uiaudit's. The scaffolder's default is to build a hand-off as the first page. How should it go in?
Options: Design reference only (Recommended); Also a test fixture; Build it as the first page.
A: sorry disregard, i'm working on 5 different projects at once

Q (Name): Repo and command name (open issue 'Repository and command name')?
Options: dmg-uiaudit / uiaudit (Recommended); uiaudit / uiaudit.
A: uiaudit / uiaudit

Proposed nouns shown as a table: environment (check, sign_in); run (start, show, list, compare; depends on environment); finding (add, list, accept, reject, diff); plan (create, show; depends on finding); regression_test (create, list; depends on finding); design_reference (load, check). Flows: audit (run.start, design_reference.check, finding.add); verify_fix (run.start, finding.diff, regression_test.create). Adapters: browser (playwright), accessibility (axe_playwright_python), images (PIL), views (prefab_ui). Database none; no web way in.

Q (Nouns): Are these the nouns?
Options: Use them (Recommended); Change the nouns; Start over.
A: Use them (Recommended)

Q (Ways in): Ways in?
Options: cli (Recommended); mcp (Recommended); http (Recommended); jobs.
A: cli (Recommended), mcp (Recommended), http (Recommended)

Q (Database): Database?
Options: none (Recommended); sqlite.
A: none (Recommended)

Q (First op): First operation (the walking skeleton)?
Options: run.start (Recommended); environment.check; finding.add.
A: run.start (Recommended)

Q (Folder): Where on your Mac?
Options: ~/Dev/uiaudit (Recommended); ~/code/uiaudit.
A: ~/Dev/uiaudit (Recommended)

Q (Remote): GitHub remote: DMG-Venture-Studio/uiaudit, public. Create it now?
Options: Create now (Recommended); First session.
A: Create now (Recommended)

Q (Add-ons): Add-ons? (Kits added automatically: better-cli for the CLI, mcp-legibility for MCP. No agent-house: nothing calls a model.)
Options: serial-build (Recommended); agent-skills (Recommended); factory.
A: serial-build (Recommended), agent-skills (Recommended)

Q (open, no options): What do the people it's for (you and the studio's agents) do today instead of a UI audit, and what does that cost?
A: manually work through huge indexes of UI / UX to figure out what's wrong - and then figure out the right feel & flow. both are hard, probably the last part is hardest

Q (open, no options): A year from now, what would failure look like for uiaudit?
A: it's just not improving throughput, or providing good advice on how to recify or make things look / feel better from a UI / UX perspective

Q (Owner): Owner name the harness uses (the person who runs each demo)?
Options: Fili (Recommended); Matt Fili.
A: Fili (Recommended)

Q (Writing): How should agents write to you in this repo?
Options: Terse, consequence first (Recommended); Terse, plus a one-line why.
A: Terse, consequence first (Recommended)

Q (Floors): Floors: what must never happen? (pick all that apply)
Options: Engine never calls a model; Same UI, same findings; Only a human triages; Staging is safe.
A: Engine never calls a model, Same UI, same findings, Only a human triages, Staging is safe, Agents not providing recommendations, or introspecting on how to improve reccomendations through research to add better skills or MCPs

Q (Not this): What is it deliberately not? (pick all that apply)
Options: Not a Lighthouse score; Not a designer replacement; Not a hosted service; Not scheduled audits.
A: Not a Lighthouse score, Not scheduled audits, Not a hosted service, On two: Not a designer replacement - right, it's additive - it helps by providing critique and propsal on UX/UI with an actionable plan to implement with a naive CC agent in the source repo (e.g., what it's auditing) with previews where possible to demonstrate before and after where the human can ultimately make the call

Q (Goals): Goals (pick all that hold):
Options: Faster UI iteration; Advice worth acting on; Plans a naive agent can run; Human makes the call.
A: Faster UI iteration, Advice worth acting on, Plans a naive agent can run, Human makes the call

Q (First gate): First gate, the walking skeleton (run.start) as you'd demo it:
Options: One voice-resume cell (Recommended); Bundled fixture page.
A: One voice-resume cell (Recommended)

Q (First stage): First stage name and goal:
Options: first-local-audit (Recommended); capture-one-cell.
A: first-local-audit (Recommended)

Q (Later gates): Later gates, in order (deselect any to drop):
Options: full-matrix + review-and-compare; critique-with-recommendations; remediation-plan + fix-loop; intended-design + staging.
A: full-matrix + review-and-compare, critique-with-recommendations, remediation-plan + fix-loop, intended-design + staging

Read-back of the vision, with the recommendation floor split: every finding carries a recommendation (enforced by the findings format); agents propose skills or MCP servers that would improve their advice after each critique, for Fili to approve, never installing anything themselves.

Q (Vision): Is this it?
Options: Yes; Change something.
A: Yes

