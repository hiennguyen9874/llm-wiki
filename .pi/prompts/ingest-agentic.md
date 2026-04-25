---
description: Ingest a source using read-only subagents for scouting, planning, and review
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

Use the single-writer agentic ingest workflow for: $ARGUMENTS

Decisions already adopted for this repo:
- single-writer default: subagents do not edit files; parent/orchestrator performs all writes
- custom project agents only: `.pi/agents/wiki-source-scout.md`, `.pi/agents/wiki-ingest-planner.md`, `.pi/agents/wiki-ingest-reviewer.md`
- handoffs stay temporary unless the parent decides a Stage-1 plan has durable audit value and saves it under `outputs/ingest-plans/`

Workflow:
1. Orient: read the source and decide whether `purpose.md`, `wiki/overview.md`, or `wiki/index.md` are needed.
2. Run `wiki-source-scout` for a read-only source/context handoff.
3. Run `wiki-ingest-planner` on that handoff for a formal Stage-1 ingest plan.
4. Parent inspects the plan. If it raises high-stakes taxonomy, schema, destructive, or privacy decisions, use `ask_user` before editing. Queue non-blocking review items when appropriate.
5. Parent executes Stage-2 generation/integration from `llm-wiki-ingest`.
6. Run `wiki-ingest-reviewer` on the plan and changed files.
7. Parent applies safe fixes from the review and asks before risky structural changes.
8. Finish with a concise summary: subagents used, files changed, review verdict, and unresolved review items.

Do not use parallel writers. Do not claim automated queues, graph engines, vector DBs, or lifecycle enforcement beyond what was actually done.
