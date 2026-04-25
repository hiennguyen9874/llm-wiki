---
description: Load compact working context at the start of a session
---

Activate:
- `llm-wiki-core`
- `llm-wiki-query`
- `qmd`
- `obsidian-markdown`

Load companion skills only if the session start creates or updates durable artifacts:
- `llm-wiki-schema`
- `llm-wiki-governance`
- `llm-wiki-ops`

Use the **Query Workflow** in `llm-wiki-query` to load compact working context for: $ARGUMENTS
If no scope is given, use recent activity.

Include current focus, key relevant pages, important recent changes, unresolved questions, and suggested next steps. Do not create or update durable artifacts unless explicitly asked.
