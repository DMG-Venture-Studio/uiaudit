---
paths:
  - "src/uiaudit/kernel/**"
  - "tests/kernel/**"
---

# kernel, the floor

Principals, the result envelope, errors, the resource protocols, ids and the clock. Its member list is closed: principals, envelope, errors, resources, ids, clock. It imports nothing of this project. Members not built yet: ids, clock.

| Role | Module | What it is | May import |
|---|---|---|---|
| kernel | `src/uiaudit/kernel/principals.py` | Who is calling, and which operation grants they hold. | the standard library |
| kernel | `src/uiaudit/kernel/envelope.py` | The one result shape every surface returns: data, or an error and the next step. | the standard library |
| kernel | `src/uiaudit/kernel/errors.py` | The errors every package shares; a noun's own errors live in its model. | the standard library |
| kernel | `src/uiaudit/kernel/resources.py` | The protocols operations ask for; boot builds the adapters that implement them. | the standard library |


Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
