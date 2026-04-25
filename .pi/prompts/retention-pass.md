---
description: Run a retention and decay review across the knowledge base
---

Activate:
- `llm-wiki-core`
- `llm-wiki-maintenance`
- `llm-wiki-governance`
- `llm-wiki-schema`
- `llm-wiki-ops`
- `qmd`
- `obsidian-markdown`

Run the **Retention Workflow** in `llm-wiki-maintenance` across: $ARGUMENTS
If no scope is given, review the most relevant knowledge areas.

Prefer repair, review, or explicit downgrade over deletion. Ask before destructive cleanup or major consolidation.
