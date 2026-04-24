---
description: Ingest a local/raw source using read-only wiki subagents for scout, planning, and review
---

Read `AGENTS.md`. Activate `llm-wiki-core`, `llm-wiki-ingest`, `llm-wiki-query`, `llm-wiki-maintenance`, `qmd`, `obsidian-markdown`, `ask-user`, and `pi-subagents` before acting.

Use the single-writer agentic ingest workflow for: $ARGUMENTS

Decisions already adopted for this repo:
- Single-writer default: subagents do not edit files; the parent/orchestrator performs all writes.
- Custom project agents only: use `.pi/agents/wiki-source-scout.md`, `.pi/agents/wiki-ingest-planner.md`, and `.pi/agents/wiki-ingest-reviewer.md`.
- Handoffs should stay in temporary chain/session context unless the parent decides a Stage-1 plan has durable audit value and saves it under `outputs/ingest-plans/`.

Workflow:
1. Orient: read relevant source scope and check whether `purpose.md`, `wiki/overview.md`, or `wiki/index.md` are needed.
2. Run `wiki-source-scout` on the requested source/scope. Ask it for a read-only source scout handoff.
3. Run `wiki-ingest-planner` with the scout handoff and source/scope. Ask it for a formal Stage-1 ingest plan.
4. As parent, inspect the plan. If it raises high-stakes taxonomy/schema/destructive/privacy decisions, use `ask_user` before editing. Queue non-blocking review items when appropriate.
5. As parent, execute Stage-2 generation/integration from `llm-wiki-ingest`: create/update source and canonical pages, refresh `related_sources`, citations, confidence/status, links, `wiki/index.md`, `wiki/log.md`, and `wiki/overview.md` when required.
6. Run `wiki-ingest-reviewer` on the plan and changed files.
7. As parent, apply safe fixes from the review. Ask before risky structural changes.
8. Finish with a concise summary: subagents used, files changed, review verdict, unresolved review items.

Do not use parallel writers. Do not claim automated queues, graph engine, vector database, or lifecycle enforcement beyond what was actually done.
