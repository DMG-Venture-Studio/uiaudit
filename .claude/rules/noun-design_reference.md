---
paths:
  - "src/uiaudit/design_reference/**"
  - "tests/design_reference/**"
---

# design_reference, a noun

Optional design tokens and reference screens for the audited app, and the check of captured styles against them.

Operations: design_reference.load, design_reference.check. Each is one function in `ops`, declared once in the catalog; a surface is a projection of that declaration.

Depends on: no other noun. Never imports environment, run, finding, plan, regression_test or an adapter: an outside service arrives as a resource the catalog hands in.

| Role | Module | What it is | May import |
|---|---|---|---|
| ops | `src/uiaudit/design_reference/ops.py` | The design_reference's operations, one function each, named design_reference_<verb>. | rules, model; the kernel |
| rules | `src/uiaudit/design_reference/rules.py` | Decisions about a design_reference: whether something is allowed, and what is wrong with it. | model; the kernel |
| model | `src/uiaudit/design_reference/model.py` | The design_reference's records and its own errors. | nothing in this noun; the kernel |


Roles it does not declare are not created; a new role is added to this noun's `roles` in the spec first. Tests: `tests/design_reference/test_<role>.py`.

Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
