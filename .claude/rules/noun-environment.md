---
paths:
  - "src/uiaudit/environment/**"
  - "tests/environment/**"
---

# environment, a noun

An app under audit in one environment, local or staging: its config, stored sign-in and health.

Operations: environment.check, environment.sign_in. Each is one function in `ops`, declared once in the catalog; a surface is a projection of that declaration.

Depends on: no other noun. Never imports run, finding, plan, regression_test, design_reference or an adapter: an outside service arrives as a resource the catalog hands in.

| Role | Module | What it is | May import |
|---|---|---|---|
| ops | `src/uiaudit/environment/ops.py` | The environment's operations, one function each, named environment_<verb>. | rules, model; the kernel |
| rules | `src/uiaudit/environment/rules.py` | Decisions about a environment: whether something is allowed, and what is wrong with it. | model; the kernel |
| model | `src/uiaudit/environment/model.py` | The environment's records and its own errors. | nothing in this noun; the kernel |


Roles it does not declare are not created; a new role is added to this noun's `roles` in the spec first. Tests: `tests/environment/test_<role>.py`.

Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
