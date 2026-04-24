# Second Brain Agent Guide

Repo = personal second brain run by LLM agent.
Human steer direction. Agent do capture, ingest, synthesis, retrieval, crystallization, review, maintenance.

## Mission
Turn raw material into durable, compounding memory.
Compile once, update with evidence, reuse later.

## Current Stance
- Manual-first, human-steered, prompt-driven.
- Prefer explicit workflows + scheduled review over pretend hidden automation.
- Shape prompts/skills so hooks or scheduled jobs can come later.
- Use hooks mainly for routing, reminders, guardrails, verification.
- Do not claim automation, graph infra, or lifecycle enforcement repo does not actually have.

## Core Layers
- `purpose.md` → directional intent: goals, scope, active questions, evolving thesis
- `raw/` → immutable capture
- `wiki/` → durable semantic knowledge
- `wiki/bases/` → operational dashboards
- `wiki/canvases/` → visual synthesis
- `wiki/overview.md` → agent-updated current-state synthesis, clusters, gaps, active direction
- `outputs/` → derived analyses, answers, briefings, reports, crystallizations, ingest plans, review items

## Mandatory Skill Activation Policy
For any non-trivial task, read this file first, then read matching skill files.

| Workflow | Must activate |
|---|---|
| Any meaningful work in `raw/`, `wiki/`, or `outputs/` | `llm-wiki-core` + `obsidian-markdown` |
| Search / retrieval across vault | `llm-wiki-query` + `qmd` |
| New source capture, triage, ingest, batch ingest | `llm-wiki-ingest` + `qmd`; use two-stage ingest for substantial sources |
| Compile raw sources / outputs into canonical wiki pages | `llm-wiki-ingest` + `llm-wiki-query` + `llm-wiki-maintenance` + `qmd`; use `/compile` prompt for manual incremental/full compilation |
| Standard web URL ingest | `llm-wiki-ingest` + `defuddle` + `qmd` |
| Answers, briefs, briefings, connections, disagreements, gap scans, next-research recommendations | `llm-wiki-query` + `qmd`; read `purpose.md`/`wiki/overview.md` when broad or strategic |
| Session start / context load / orientation | `llm-wiki-query` + `qmd` |
| Session distillation / session end / durable lessons | `llm-wiki-crystallize` + `qmd` |
| Review, lint, maintenance, wiki improvement without new source | `llm-wiki-maintenance` + `qmd`; include review queue + graph-insights-lite when useful |
| Canvas work | `llm-wiki-visualization` + `json-canvas` |
| Base work | `llm-wiki-visualization` + `obsidian-bases` |
| Live vault validation or Obsidian interaction | `llm-wiki-visualization` + `obsidian-cli` |
| High-stakes structural decisions | `ask-user` before proceeding |

## Scope Split
- `purpose.md` = strategic direction and evolving intent.
- `AGENTS.md` = repo router + top guardrails.
- `.pi/skills/llm-wiki-core/SKILL.md` = detailed shared rules: lifecycle, metadata, citations, linking, logging, naming, privacy, governance.
- Workflow skills = task-specific procedure.
- `.pi/prompts/` = thin entrypoints; real policy lives in skills.

## Must Remember
- For work in `raw/`, `wiki/`, or `outputs/`, follow `llm-wiki-core`; keep shared rules there, not duplicated here.
- Ask user before irreversible or high-level structural changes: bulk rename/delete, taxonomy change, major schema change, large merge.

## Working Style
Think in loop: purpose → capture → analyze → distill → crystallize → integrate → visualize → review → research gaps.
Promote durable knowledge upward. Keep vault browsable in Obsidian.

## Pattern References
When changing knowledge-system design, also read:
- `LLM-WIKI.md`
- `LLM-WIKI-v2.md`
- `LLM-Wiki-v3.md`
- `LLM-Wiki-v4.md`

## Prompt Policy
Important prompt families:
- ingest / ingest-url / ingest-batch / ingest-pdf / ingest-arxiv / compile
- query / brief / briefing
- connections / disagreements / gaps / next-research / explore / deep-research
- review / lint / retention-pass / resolve-contradictions / privacy-scan
- crystallize / session-start / session-end

Prompt job:
- choose right workflow + companion skills
- pass scope + intent clearly
- stay thin; keep durable policy in skills
