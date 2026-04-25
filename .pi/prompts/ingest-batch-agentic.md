---
description: Sequentially batch-ingest sources using read-only subagents and a single writer
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
- `ask-user`
- `pi-subagents`

Use the single-writer sequential batch ingest workflow for: $ARGUMENTS

Rules:
- Process sources sequentially unless the user explicitly approves a different design.
- For each source, run the `/ingest-agentic` pattern: `wiki-source-scout` → `wiki-ingest-planner` → parent writes → `wiki-ingest-reviewer`.
- Reuse and update shared canonical pages; avoid duplicate one-off summaries.
- After each source, reassess whether later sources should trigger a compile pass instead of isolated integration.
- Ask before high-stakes taxonomy, schema, bulk move, delete, or merge changes.
- Create review queue items for non-blocking human judgments.

Finish with a per-source summary plus batch-level changes to `wiki/index.md`, `wiki/log.md`, `wiki/overview.md`, the review queue, and any recommended later `/compile` pass.
