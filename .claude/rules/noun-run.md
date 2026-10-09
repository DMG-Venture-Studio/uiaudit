---
paths:
  - "src/uiaudit/run/**"
  - "tests/run/**"
---

# run, a noun

One capture of the route, state, viewport and theme matrix, and cell-by-cell comparison across runs.

Operations: run.start, run.show, run.list, run.compare. Each is one function in `ops`, declared once in the catalog; a surface is a projection of that declaration.

Depends on: environment. Never imports finding, plan, regression_test, design_reference or an adapter: an outside service arrives as a resource the catalog hands in.

| Role | Module | What it is | May import |
|---|---|---|---|
| ops | `src/uiaudit/run/ops.py` | The run's operations, one function each, named run_<verb>: run.start, run.show, run.list, run.compare. | render, rules, model; the kernel; environment's `ops` and `model` |
| render | `src/uiaudit/run/render.py` | Outward forms of a run: message bodies, exports, files, reports. | rules, model; the kernel; environment's `model` |
| rules | `src/uiaudit/run/rules.py` | Decisions about a run: whether something is allowed, and what is wrong with it. | model; the kernel; environment's `model` |
| model | `src/uiaudit/run/model.py` | The run's records and its own errors. | nothing in this noun; the kernel; environment's `model` |


Roles it does not declare are not created; a new role is added to this noun's `roles` in the spec first. Tests: `tests/run/test_<role>.py`.

Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
