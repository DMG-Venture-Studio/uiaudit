---
paths:
  - "src/uiaudit/flows/**"
  - "tests/flows/**"
---

# flows, use cases across nouns

One module per flow, calling operations through the catalog, never a noun's `ops` directly. Flows declared: audit, verify_fix.

| Role | Module | What it is | May import |
|---|---|---|---|
| flow | `src/uiaudit/flows/audit.py` | Capture the matrix, check it against the design reference, and record the findings. Calls run.start, design_reference.check, finding.add. | the catalog, nouns' `model`, the kernel |
| flow | `src/uiaudit/flows/verify_fix.py` | Recapture the cells a fix touched, confirm its findings closed, and lock the fix with regression tests. Calls run.start, finding.diff, regression_test.create. | the catalog, nouns' `model`, the kernel |


Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
