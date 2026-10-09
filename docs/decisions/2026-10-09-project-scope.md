# uiaudit: what it is, the first slice, and where things live

Date: 2026-10-09. Decided by Fili in the scoping interview. Source: the interview,
recorded verbatim under decision sources as `scoping-interview-2026-10-09`.

## Decided

**uiaudit: uiaudit is an agent-driven UI audit that captures every screen state of an app and turns accessibility and look-and-feel findings into recommendations and a fix plan a coding agent can execute. It removes hours of hunting by hand through UI guidance and screens.**

**The first gate is capture-one-cell**, built on the operation `run.start`.

**Built from nouns and one operation catalog** (see `architecture`).

## Rejected

- The alternatives to the nouns and the ways in are in the architecture record (see `architecture`); one fact, one place.

## Reopens if

The same conditions as the architecture record (see `architecture`): a second app the capture matrix cannot express, or findings that need concurrent writers.
