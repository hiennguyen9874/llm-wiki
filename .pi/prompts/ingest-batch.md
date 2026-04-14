---
description: Ingest batch of documents
---

"Read AGENTS.md. Then activate `llm-wiki-core`, `llm-wiki-ingest`, `qmd`, and `obsidian-markdown`. Process all unprocessed files from $ARGUMENTS in raw/ sequentially. For each source, follow the ingest skill exactly: read fully, use `wiki/index.md` only when orientation is needed, extract entities and relationships, assess reinforcement or supersession, create or update the source page, update the relevant wiki pages, add backlinks and contradictions, refresh lifecycle metadata where justified, update the index, and log the ingest. Periodically consider whether a Base or Canvas should be updated for major structural changes. Use `ask-user` before any high-level taxonomy decision."
