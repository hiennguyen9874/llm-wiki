---
description: Query the knowledge base
---

Activate:
- `llm-wiki-core`
- `llm-wiki-query`
- `qmd`
- `obsidian-markdown`

Load companion skills as needed:
- `llm-wiki-schema` if saving a reusable answer or updating canonical pages
- `llm-wiki-governance` if disputed, stale, superseded, or sensitive material matters
- `llm-wiki-ops` if saving the result affects naming, `wiki/index.md`, `wiki/log.md`, or discoverability

Answer the request using the **Query Workflow** in `llm-wiki-query`.
Cite pages used, distinguish fact from inference, and persist only if the result creates durable reusable value.

User request: $ARGUMENTS
