---
description: Compile raw sources or durable outputs into canonical wiki pages
---

"Read AGENTS.md. Then activate `llm-wiki-core`, `llm-wiki-ingest`, `llm-wiki-query`, `llm-wiki-maintenance`, `qmd`, and `obsidian-markdown`. Use this prompt for manual compilation: synthesizing accumulated `raw/` sources and/or durable `outputs/` artifacts into canonical `wiki/` pages.

Determine scope from the user request. If unclear, ask one focused question before editing.

Workflow:
1. Classify mode as `incremental` unless the user requests `full`.
   - `incremental`: process new, changed, or explicitly scoped sources/outputs since the last relevant log/review.
   - `full`: re-read all relevant sources/pages in scope and update broader synthesis.
2. Read `purpose.md`, `wiki/overview.md`, and `wiki/index.md` when scope is broad or strategic.
3. Use QMD for exact and conceptual retrieval across `wiki/`, `outputs/`, and relevant `raw/` paths.
4. Read actual selected files before synthesis; do not compile from snippets or index summaries alone.
5. Produce a concise compile plan in chat before editing. Include affected sources/outputs, canonical pages to create/update, `related_sources` updates, contradictions/supersession, overview/index/log updates, and human review items.
6. Ask before high-stakes taxonomy/schema/bulk move/delete/merge changes. Queue non-blocking judgments in `outputs/review-queue/`.
7. Update or create canonical wiki pages. Prefer integration into existing pages over isolated summaries.
8. Refresh `related_sources`, claim/evidence blocks, confidence/quality, retention, visibility, contradictions, and supersession where justified.
9. Update `wiki/overview.md` and `wiki/index.md` when global state or browsable catalog changes.
10. Append a `wiki/log.md` entry with action `update` or `ingest` as appropriate, explaining what was compiled and why.
11. If the compile plan itself has durable audit value, save it under `outputs/analyses/` or `outputs/ingest-plans/`.

Do not claim automated queue, graph engine, vector database, or auto-ingest behavior unless those tools are actually available and used."

User Request: $ARGUMENTS
