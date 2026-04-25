---
description: Compile raw sources or durable outputs into canonical wiki pages
---

Activate:
- `llm-wiki-core`
- `llm-wiki-ingest`
- `llm-wiki-query`
- `llm-wiki-maintenance`
- `llm-wiki-schema`
- `llm-wiki-governance`
- `llm-wiki-ops`
- `qmd`
- `obsidian-markdown`

Use the **Compile Workflow** in `llm-wiki-ingest` for: $ARGUMENTS

Determine scope from the request. Default to `incremental` unless the user explicitly requests `full`. If scope is unclear, ask one focused question before editing. Keep the prompt thin; keep durable policy in the skills.
