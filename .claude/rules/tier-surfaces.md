---
paths:
  - "src/uiaudit/surfaces/**"
  - "tests/surfaces/**"
  - "docs/api/**"
---

# surfaces, the ways in

Each is a projection of the catalog with no logic of its own; nothing imports a surface but `__main__`, and surfaces never import each other. Surfaces declared: cli, http, mcp. The committed projections under `docs/api/` are rendered by `tools/render_surfaces.py`.

| Role | Module | What it is | May import |
|---|---|---|---|
| surface | `src/uiaudit/surfaces/cli.py` | The command line: `uiaudit <noun> <verb> --json`, one command per operation in the catalog. | boot, the catalog, the kernel, a noun's `model` for types |
| surface | `src/uiaudit/surfaces/http.py` | The HTTP surface: one route per operation, generated from the catalog; OpenAPI is committed. | boot, the catalog, the kernel, a noun's `model` for types |
| surface | `src/uiaudit/surfaces/mcp.py` | The MCP surface: one tool per operation an agent may call, generated from the catalog. | boot, the catalog, the kernel, a noun's `model` for types |


Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
