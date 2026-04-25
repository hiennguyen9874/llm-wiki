---
description: Find durable connections between concepts in the knowledge base
---

Activate:
- `llm-wiki-core`
- `llm-wiki-query`
- `qmd`
- `obsidian-markdown`

Load companion skills as needed:
- `llm-wiki-schema` if a durable relationship should be persisted
- `llm-wiki-governance` if the connection depends on disputed or sensitive material
- `llm-wiki-ops` if saving the result affects naming, index, log, or discoverability

Use the **Connections** variant in `llm-wiki-query` for: $ARGUMENTS

Cite pages supporting each connection. If a relationship is durable and missing from the wiki, update canonical pages instead of leaving it only in chat.
