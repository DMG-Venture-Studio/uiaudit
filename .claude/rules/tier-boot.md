---
paths:
  - "src/uiaudit/boot.py"
  - "src/uiaudit/__main__.py"
---

# boot, the composition root

The one place adapters are built and handed to the catalog as resources. Nouns: environment, run, finding, plan, regression_test, design_reference.

| Role | Module | What it is | May import |
|---|---|---|---|
| boot | `src/uiaudit/boot.py` | The composition root: builds each adapter once and hands the resources to the catalog. | the adapters, the kernel |
| entry | `src/uiaudit/__main__.py` | `python -m uiaudit`: the cli surface. | the surfaces |


Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
