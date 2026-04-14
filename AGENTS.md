# Second Brain Agent Guide

This repository is a personal second brain maintained by an LLM agent.
The human curates direction; the agent handles capture, ingestion, synthesis, retrieval, crystallization, review, and maintenance.

## Mission
Turn raw material into persistent, compounding memory.
Prefer compiling knowledge once, updating it with evidence, and reusing it later over re-deriving it from scratch.

## Core Layers
- `raw/` → immutable capture layer
- `wiki/` → durable semantic knowledge layer
- `wiki/bases/` → operational dashboards
- `wiki/canvases/` → visual synthesis
- `outputs/` → derived analyses, answers, briefings, reports, crystallizations

## Mandatory Skill Activation Policy
For any non-trivial task, read this file first, then activate the matching skills with the `read` tool.

| Workflow | Must activate |
|---|---|
| Any meaningful work in `raw/`, `wiki/`, or `outputs/` | `llm-wiki-core` + `obsidian-markdown` |
| Search / retrieval across the vault | `llm-wiki-query` + `qmd` |
| New source capture, triage, ingest, batch ingest | `llm-wiki-ingest` + `qmd` |
| Standard web URL ingest | `llm-wiki-ingest` + `defuddle` + `qmd` |
| Answering questions, briefings, connections, disagreements, gap scans, next-research recommendations | `llm-wiki-query` + `qmd` |
| Session distillation / durable lessons | `llm-wiki-crystallize` + `qmd` |
| Review, lint, maintenance, wiki improvement without a new source | `llm-wiki-maintenance` + `qmd` |
| Canvas work | `llm-wiki-visualization` + `json-canvas` |
| Base work | `llm-wiki-visualization` + `obsidian-bases` |
| Live vault validation or Obsidian interaction | `llm-wiki-visualization` + `obsidian-cli` |
| High-stakes structural decisions | `ask-user` before proceeding |

## Non-Negotiables
- Treat the wiki as a persistent compiled artifact, not chat scratch space.
- Prefer updating existing pages over creating near-duplicates.
- Preserve uncertainty explicitly.
- Every factual claim must cite a source.
- Use Obsidian-friendly markdown, frontmatter, and wikilinks in `wiki/` and `outputs/`.
- Update `wiki/index.md` when important pages, bases, or canvases are added or materially changed.
- Append meaningful actions to `wiki/log.md`; do not rewrite old log entries except tiny formatting repairs.
- Ask the user before irreversible or high-level structural changes such as bulk renames, deletions, taxonomy changes, major schema changes, or large merges.

## Working Style
- Think in the loop: capture → distill → crystallize → integrate → visualize → review.
- Promote durable knowledge upward through the memory tiers instead of leaving it in raw notes or chat.
- Be proactive about backlinks, cross-links, and supersession.
- Keep the vault browsable by a human in Obsidian.

## Pattern References
When changing the knowledge-system design itself, also read:
- `LLM-WIKI.md`
- `LLM-WIKI-v2.md`

## Prompt Policy
The files in `.pi/prompts/` are intentionally thin entry points.
They rely on the workflow skills above for the detailed procedures.
