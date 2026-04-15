---
description: Run a retention and decay review across the knowledge base
---

"Read AGENTS.md. Then activate `llm-wiki-core`, `llm-wiki-maintenance`, `qmd`, and `obsidian-markdown`. Run the retention workflow across $ARGUMENTS or the most relevant knowledge areas if no scope is given. Use retention class plus `last_confirmed` to find pages or claims that may be stale, lower confidence modestly or mark status as stale/needs_update when justified, preserve provenance, and never delete solely because content is old. Update affected pages, note important retention decisions in `wiki/log.md`, and produce a durable report only if the pass reveals reusable patterns or follow-up work."