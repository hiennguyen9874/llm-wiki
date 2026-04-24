---
description: Capture a web URL, then ingest it using read-only wiki subagents
---

Read `AGENTS.md`. Activate `llm-wiki-core`, `llm-wiki-ingest`, `llm-wiki-query`, `llm-wiki-maintenance`, `defuddle`, `qmd`, `obsidian-markdown`, `ask-user`, and `pi-subagents` before acting.

Use the single-writer agentic URL ingest workflow for: $ARGUMENTS

Workflow:
1. Parent/orchestrator performs URL capture first using the URL Ingest Workflow in `llm-wiki-ingest`.
   - Use Defuddle unless the URL ends with `.md`.
   - Save clean markdown to `raw/web-clips/` with source metadata including `canonical_url`.
   - Preserve raw capture and screen for sensitive material.
2. After the local raw web clip exists, run the same single-writer subagent pipeline as `/ingest-agentic`:
   - `wiki-source-scout` for read-only source/context handoff.
   - `wiki-ingest-planner` for formal Stage-1 ingest plan.
   - Parent writes Stage-2 integration.
   - `wiki-ingest-reviewer` audits the plan and changed files.
3. Parent applies safe review fixes and summarizes changed files, citations/provenance, index/log/overview updates, and unresolved review items.

Subagents must not write files. The parent is the only writer.
