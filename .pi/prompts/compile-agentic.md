---
description: Compile sources/outputs with read-only subagent scouting and review
---

Read `AGENTS.md`. Activate `llm-wiki-core`, `llm-wiki-ingest`, `llm-wiki-query`, `llm-wiki-maintenance`, `qmd`, `obsidian-markdown`, `ask-user`, and `pi-subagents` before acting.

Use a single-writer agentic compile workflow for: $ARGUMENTS

Workflow:
1. Parent determines compile scope (`incremental` unless user requests `full`). If scope is unclear, ask one focused question before editing.
2. Run `wiki-source-scout` over the selected raw sources, outputs, and existing wiki context to produce a read-only compile reconnaissance handoff.
3. Run `wiki-ingest-planner` with the scout handoff and compile scope to produce a compile/integration plan: affected sources/outputs, canonical pages to update/create, traceability updates, contradictions/supersession, overview/index/log updates, and human review items.
4. Parent writes all canonical updates.
5. Run `wiki-ingest-reviewer` on the plan and changed files.
6. Parent applies safe fixes, asks before risky structural changes, and summarizes results.

Do not use parallel writers. Do not claim graph/vector/automation behavior that was not actually used.
