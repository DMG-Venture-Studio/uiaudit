---
paths:
  - "src/uiaudit/adapters/**"
  - "tests/adapters/**"
---

# adapters, one outside service each

Each implements a protocol from `kernel/resources.py`; boot builds it once and the catalog hands it to the operations that name it. No noun imports an adapter. Adapters declared: browser, accessibility, images, views.

| Role | Module | What it is | May import |
|---|---|---|---|
| adapter | `src/uiaudit/adapters/browser.py` | Drives Chromium to reach each state and capture screenshots, element boxes and computed styles. Wraps `playwright`, implements `Browser`. | the kernel; the wrapped package inside the one function that needs it |
| adapter | `src/uiaudit/adapters/accessibility.py` | Runs axe-core on a captured page and returns its raw results. Wraps `axe_playwright_python`, implements `AccessibilityScanner`. | the kernel; the wrapped package inside the one function that needs it |
| adapter | `src/uiaudit/adapters/images.py` | Draws finding boxes, makes thumbnails and computes diff images. Wraps `PIL`, implements `ImageKit`. | the kernel; the wrapped package inside the one function that needs it |
| adapter | `src/uiaudit/adapters/views.py` | Builds the review UI views served inline in Claude, in the local browser and as a static report. Wraps `prefab_ui`, implements `ReviewViews`. | the kernel; the wrapped package inside the one function that needs it |


Rendered by `tools/render_rules.py` from `project-spec.toml` and the module docstrings; never edited by hand.
