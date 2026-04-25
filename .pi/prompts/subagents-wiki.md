---
description: Explain the current llm-wiki subagent design and usage
---

Activate:
- `llm-wiki-core`
- `pi-subagents`

Load companion skills as needed:
- `llm-wiki-governance` if the user asks to modify subagent architecture or decision boundaries
- `ask-user` before high-stakes structural changes

Explain the current llm-wiki subagent design:
- single-writer parent or orchestrator
- read-only project agents in `.pi/agents/`: `wiki-source-scout`, `wiki-ingest-planner`, `wiki-ingest-reviewer`
- agentic prompts: `/ingest-agentic`, `/ingest-url-agentic`, `/ingest-batch-agentic`, `/compile-agentic`
- handoffs are temporary unless the parent selectively persists audit-worthy plans or reports
- non-agentic prompts remain available for manual-first work

If the user asks to modify the design, use `ask_user` before structural changes.

User request: $ARGUMENTS
