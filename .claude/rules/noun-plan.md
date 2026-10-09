---
paths:
  - "src/uiaudit/plan/**"
  - "tests/plan/**"
---

# plan, a noun

The task plan built from accepted findings that a coding agent executes in the audited repo.

Operations: plan.create, plan.show. Each is one function in `ops`, declared once in the catalog; a surface is a projection of that declaration.

Depends on: finding. Never imports environment, run, regression_test, design_reference or an adapter: an outside service arrives as a resource the catalog hands in.

| Role | Module | What it is | May import |
|---|---|---|---|
| ops | `src/uiaudit/plan/ops.py` | The plan's operations, one function each, named plan_<verb>: plan.create, plan.show. | render, rules, model; the kernel; `finding.ops` and `finding.model` |
| render | `src/uiaudit/plan/render.py` | Outward forms of a plan: message bodies, exports, files, reports. | rules, model; the kernel; `finding.model` |
| rules | `src/uiaudit/plan/rules.py` | Decisions about a plan: whether something is allowed, and what is wrong with it. | model; the kernel; `finding.model` |
| model | `src/uiaudit/plan/model.py` | The plan's records and its own errors. | nothing in this noun; the kernel; `finding.model` |


Roles it does not declare are not created; a new role is added to this noun's `roles` in the spec first. Tests: `tests/plan/test_<role>.py`.

Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
