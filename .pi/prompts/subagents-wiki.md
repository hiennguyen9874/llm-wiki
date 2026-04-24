---
description: Explain the current llm-wiki subagent design and usage
---

Read `AGENTS.md`. Activate `llm-wiki-core` and `pi-subagents`.

Explain the current llm-wiki subagent design:
- Single-writer parent/orchestrator.
- Read-only project agents in `.pi/agents/`: `wiki-source-scout`, `wiki-ingest-planner`, `wiki-ingest-reviewer`.
- Agentic prompts: `/ingest-agentic`, `/ingest-url-agentic`, `/ingest-batch-agentic`, `/compile-agentic`.
- Handoffs are temporary unless parent selectively persists audit-worthy plans/reports.
- Existing non-agentic prompts remain unchanged.

If the user asks to modify the design, use `ask_user` before structural changes.

User request: $ARGUMENTS
