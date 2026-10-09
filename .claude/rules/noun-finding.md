---
paths:
  - "src/uiaudit/finding/**"
  - "tests/finding/**"
---

# finding, a noun

One problem in one cell, with its recommendation, triage status and identity across runs.

Operations: finding.add, finding.list, finding.accept, finding.reject, finding.diff. Each is one function in `ops`, declared once in the catalog; a surface is a projection of that declaration.

Depends on: no other noun. Never imports environment, run, plan, regression_test, design_reference or an adapter: an outside service arrives as a resource the catalog hands in.

| Role | Module | What it is | May import |
|---|---|---|---|
| ops | `src/uiaudit/finding/ops.py` | The finding's operations, one function each, named finding_<verb>. | render, rules, model; the kernel |
| render | `src/uiaudit/finding/render.py` | Outward forms of a finding: message bodies, exports, files, reports. | rules, model; the kernel |
| rules | `src/uiaudit/finding/rules.py` | Decisions about a finding: whether something is allowed, and what is wrong with it. | model; the kernel |
| model | `src/uiaudit/finding/model.py` | The finding's records and its own errors. | nothing in this noun; the kernel |


Roles it does not declare are not created; a new role is added to this noun's `roles` in the spec first. Tests: `tests/finding/test_<role>.py`.

Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
