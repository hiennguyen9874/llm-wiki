---
description: Compile sources or outputs into canonical wiki pages using read-only subagents and a single writer
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

Use the single-writer agentic compile workflow for: $ARGUMENTS

Workflow:
1. Determine compile scope: `incremental` unless the user explicitly requests `full`.
2. If scope is unclear, ask one focused question before editing.
3. Run subagent `wiki-source-scout` for read-only compile reconnaissance over relevant `raw/`, `outputs/`, and existing `wiki/` context.
4. Run subagent `wiki-ingest-planner` on the scout handoff to produce a compile plan: affected sources/outputs, canonical pages to update/create, `related_sources`, contradictions/supersession, overview/index/log updates, and human review items.
5. Parent/orchestrator is the only writer and performs all canonical updates.
6. Run subagent `wiki-ingest-reviewer` on the plan and changed files.
7. Parent applies safe fixes, asks before risky structural changes, and summarizes results.

Do not use parallel writers. Do not claim graph engine, vector DB, automated queues, or lifecycle enforcement unless actually used.
