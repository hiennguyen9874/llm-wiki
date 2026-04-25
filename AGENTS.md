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
| Any meaningful work in `raw/`, `wiki/`, or `outputs/` | `llm-wiki-core` + `obsidian-markdown`; then load companion skills as needed: `llm-wiki-schema` for structured note updates, `llm-wiki-governance` for privacy/contradiction/risky judgment, `llm-wiki-ops` for naming/layout/index/log |
| Search / retrieval across vault | `llm-wiki-query` + `qmd`; add `llm-wiki-schema` when persisting structured outputs, `llm-wiki-governance` when disputed/sensitive material matters |
| New source capture, triage, ingest, batch ingest | `llm-wiki-ingest` + `qmd`; usually add `llm-wiki-schema`, add `llm-wiki-governance` for privacy/contradiction/review items, add `llm-wiki-ops` for naming/folder/index/log; use two-stage ingest for substantial sources |
| Compile raw sources / outputs into canonical wiki pages | `llm-wiki-ingest` + `llm-wiki-query` + `llm-wiki-maintenance` + `qmd`; usually add `llm-wiki-schema` + `llm-wiki-governance`, and `llm-wiki-ops` when catalog/index/log updates matter; use `/compile` prompt for manual incremental/full compilation |
| Standard web URL ingest | `llm-wiki-ingest` + `defuddle` + `qmd`; usually add `llm-wiki-schema`, and `llm-wiki-governance` if privacy/sanitization/supersession issues arise |
| Answers, briefs, briefings, connections, disagreements, gap scans, next-research recommendations | `llm-wiki-query` + `qmd`; read `purpose.md`/`wiki/overview.md` when broad or strategic; add `llm-wiki-schema` for saved artifacts and `llm-wiki-governance` for disputed/sensitive material |
| Session start / context load / orientation | `llm-wiki-query` + `qmd`; add companion skills only if the session creates or updates durable artifacts |
| Session distillation / session end / durable lessons | `llm-wiki-crystallize` + `qmd`; usually add `llm-wiki-schema`, add `llm-wiki-governance` for sensitive/disputed lessons, and `llm-wiki-ops` when naming/index/log changes matter |
| Review, lint, maintenance, wiki improvement without new source | `llm-wiki-maintenance` + `qmd`; usually add `llm-wiki-governance` + `llm-wiki-ops`, and `llm-wiki-schema` when repairing metadata/page shapes; include review queue + graph-insights-lite when useful |
| Canvas work | `llm-wiki-visualization` + `json-canvas`; add `llm-wiki-ops` for placement/index/log and `llm-wiki-schema` if linked markdown structure or metadata alignment matters |
| Base work | `llm-wiki-visualization` + `obsidian-bases`; add `llm-wiki-ops` for placement/index/log and `llm-wiki-schema` if metadata alignment matters |
| Live vault validation or Obsidian interaction | `llm-wiki-visualization` + `obsidian-cli`; add `llm-wiki-ops` if discoverability/catalog validation is part of the task |
| High-stakes structural decisions | `ask-user` before proceeding; usually alongside `llm-wiki-governance` |

## Tool Selection Policy
- `AGENTS.md` owns top-level routing and tool-selection guidance.
- Use **QMD** as primary local markdown search/retrieval tool for `wiki/`, `raw/`, and `outputs/`.
- Use **Defuddle** for standard web URLs before saving into `raw/web-clips/`.
- Use **Obsidian Markdown** conventions when editing `.md` files in `wiki/` and `outputs/`.
- Use **JSON Canvas** when a topic benefits from spatial/relational visualization.
- Use **Obsidian Bases** for dashboards, queues, inventories, and review flows.
- Use **Obsidian CLI** when live vault interaction helps validate rendering, search, backlinks, or discoverability.

## Scope Split
- `purpose.md` = strategic direction and evolving intent.
- `AGENTS.md` = repo router, tool-selection policy, and top guardrails.
- `llm-wiki-core` skill = constitutional rules: mission, stance, architecture, lifecycle, and global invariants.
- `llm-wiki-schema` skill = shared note structure, frontmatter, lifecycle fields, and page-shape rules.
- `llm-wiki-governance` skill = privacy, visibility, contradiction/supersession, review-queue, and risky-change policy.
- `llm-wiki-ops` skill = naming, layout, index/log, and catalog-operation rules.
- Workflow skills = task-specific procedure.
- `prompts` = thin entrypoints; real policy lives in skills.

## Must Remember
- For work in `raw/`, `wiki/`, or `outputs/`, always follow `llm-wiki-core` first, then load matching companion skills (`llm-wiki-schema`, `llm-wiki-governance`, `llm-wiki-ops`) as needed.
- Ask user before irreversible or high-level structural changes: bulk rename/delete, taxonomy change, major schema change, large merge.

## Working Style
Think in loop: purpose → capture → analyze → distill → crystallize → integrate → visualize → review → research gaps.
Promote durable knowledge upward. Keep vault browsable in Obsidian.

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
