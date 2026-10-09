---
paths:
  - "src/uiaudit/regression_test/**"
  - "tests/regression_test/**"
---

# regression_test, a noun

A generated test in the audited repo that fails if a closed finding comes back.

Operations: regression_test.create, regression_test.list. Each is one function in `ops`, declared once in the catalog; a surface is a projection of that declaration.

Depends on: finding. Never imports environment, run, plan, design_reference or an adapter: an outside service arrives as a resource the catalog hands in.

| Role | Module | What it is | May import |
|---|---|---|---|
| ops | `src/uiaudit/regression_test/ops.py` | The regression_test's operations, one function each, named regression_test_<verb>. | render, model; the kernel; `finding.ops` and `finding.model` |
| render | `src/uiaudit/regression_test/render.py` | Outward forms of a regression_test: message bodies, exports, files, reports. | model; the kernel; `finding.model` |
| model | `src/uiaudit/regression_test/model.py` | The regression_test's records and its own errors. | nothing in this noun; the kernel; `finding.model` |


Roles it does not declare are not created; a new role is added to this noun's `roles` in the spec first. Tests: `tests/regression_test/test_<role>.py`.

Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
