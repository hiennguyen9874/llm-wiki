---
description: Ingest a PDF document into the second brain
---

Activate:
- `llm-wiki-core`
- `llm-wiki-ingest`
- `llm-wiki-schema`
- `llm-wiki-governance`
- `llm-wiki-ops`
- `pdf`
- `qmd`
- `obsidian-markdown`

Process $ARGUMENTS as a PDF source.
Preserve or copy the raw PDF into the appropriate `raw/` location, use the `pdf` skill for extraction or rendering when layout matters, then continue with the normal **Ingest Workflow** in `llm-wiki-ingest`.
