---
paths:
  - "src/uiaudit/catalog/**"
  - "tests/catalog/**"
---

# catalog, the index of operations

Every built operation by name: what it is, who may call it, where it is exposed.

Every operation enters here when its slice is built, with its grant, effect, resources and surfaces; the catalog is the only module above the nouns that imports a noun's `ops`. May import: every noun's `ops` and `model`, the kernel.

Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
