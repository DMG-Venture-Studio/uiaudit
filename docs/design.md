# uiaudit

Role: what the product is, who it is for, and what it deliberately is not. Current state only;
rationale for each choice lives in the decision records, and pending work lives in the roadmap.

## What it is

An agent-driven UI audit that captures every screen state of an app, critiques it for accessibility and for look, feel and flow, and turns that into recommendations and a fix plan a coding agent can execute.

## Who uses it

Fili and the studio's coding agents, auditing the studio's own frontends, starting with voice-resume.

## What they do today instead

Working by hand through huge indexes of UI and UX guidance to find what is wrong, then working out the right feel and flow. Both are hard; the feel and flow part is hardest.

## What failure looks like

It does not improve throughput, or it does not give good advice on how to fix things or make them look and feel better.

## Goals

- A UI pass takes minutes of review, not hours of hunting through screens, so more UI ships each week.
- Every finding carries a concrete recommendation on how to fix it or make it look and feel better, not just what is wrong.
- A coding agent with no context in the audited repo can implement the plan from its file paths and done-checks.
- Before and after previews of every proposal let Fili decide by looking, and fixes stay fixed.

## Not this

- Not a Lighthouse score or a site-wide crawler; it audits the states that matter.
- Not scheduled audits; it runs when someone is changing UI.
- Not a hosted service in this version.
- Not a designer replacement: it adds critique and proposals with an actionable plan for a naive coding agent in the audited repo, with before and after previews where possible, and the human makes the call.

## How it is built

- Python 3.12 with uv, every tool pinned, because one command reproduces any machine.
- No database yet; adding one is a spec change.
- Ways in: cli, http, mcp, each generated from one catalog of operations, so they cannot disagree.

Deployables:

- The `uiaudit` service, reached through cli, http, mcp.
