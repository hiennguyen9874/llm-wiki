---
description: Scan notes and artifacts for sensitive-information handling issues
---

Activate:
- `llm-wiki-core`
- `llm-wiki-maintenance`
- `llm-wiki-governance`
- `llm-wiki-ops`
- `qmd`
- `obsidian-markdown`

Run the **Privacy Scan Workflow** in `llm-wiki-maintenance` on: $ARGUMENTS
If no scope is given, inspect recent downstream artifacts.

Do not silently change raw-source retention policy. Ask before destructive cleanup.
