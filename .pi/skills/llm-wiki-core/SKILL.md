---
name: llm-wiki-core
description: "Shared constitutional rules for this second-brain repo: mission, stance, memory architecture, lifecycle, and non-negotiable global invariants. Use before any meaningful work in raw/, wiki/, or outputs/."
---

# LLM Wiki Core

Activate before meaningful second-brain work.

This skill defines repo identity and non-negotiable invariants.
- Routing and tool-selection policy live in `AGENTS.md`.
- Detailed schema rules live in `llm-wiki-schema`.
- Privacy, contradiction, review, and risky-change rules live in `llm-wiki-governance`.
- Naming, layout, index, and log rules live in `llm-wiki-ops`.

## Identity and Mission
- Repo = personal second brain run by LLM agent.
- Human chooses direction, sources, and priorities.
- Agent supports capture, ingest, synthesis, retrieval, crystallization, review, and maintenance.
- Optimize for durable, compounding memory rather than one-off chat answers.

## Implementation Stance
- Manual-first, human-steered, prompt-driven.
- Prefer explicit workflows and review loops over pretend hidden automation.
- Shape prompts and skills so hooks or scheduled jobs can exist later.
- Do not claim automation, graph infra, vector DB, lifecycle enforcement, or other systems the repo does not actually have.

## Memory Architecture
- `purpose.md` = directional intent, goals, active questions, evolving thesis
- `raw/` = immutable capture layer
- `wiki/` = durable semantic knowledge
- `outputs/` = derived analyses, answers, briefings, reports, crystallizations
- `wiki/bases/` and `wiki/canvases/` = Obsidian-first overlays for dashboards and visual synthesis

## Memory Lifecycle

### Working memory
- Mainly `raw/inbox/` and `raw/captures/`
- New, unresolved, exploratory, or low-confidence material
- Not canonical knowledge

### Episodic memory
- Mainly `outputs/crystallizations/`, `outputs/analyses/`, and similar artifacts
- Structured records of investigations, sessions, and research episodes
- More durable than raw, but not canonical by default

### Semantic memory
- Mainly `wiki/`
- Durable concepts, entities, projects, timelines, syntheses, and conclusions
- Update when evidence reinforces, revises, or supersedes prior knowledge

### Procedural memory
- `AGENTS.md`, skills, prompts, and other workflow/procedure artifacts
- How the system should operate

### Promotion rule
- Do not push every observation directly into `wiki/`.
- Crystallize exploratory work when needed.
- Promote only durable, evidence-backed knowledge into canonical wiki pages.
- Promote stable process lessons into procedural memory.

## Strategic Notes
- `purpose.md` defines why the repo exists and what direction matters.
- `wiki/overview.md` is the current-state synthesis of themes, clusters, gaps, and active direction.
- Keep strategic meaning here; workflow skills decide when to read or update those files.

## Global Invariants
- Wiki = durable compiled artifact, not chat scratchpad.
- Prefer updating existing pages over creating redundant near-duplicates.
- Preserve uncertainty explicitly.
- Separate supported fact, inference, and speculation.
- Factual claims require evidence.
- Preserve provenance when evidence changes.
- Use compile-style integration when isolated ingests would fragment knowledge.
- Keep important insights in durable markdown, not only in chat.
- Strong work usually improves surrounding context, not only one isolated page.
- Keep the vault browsable and useful in Obsidian.

## Decision Gate
Ask user before:
- destructive or costly-to-undo changes
- major structural or taxonomy changes
- significant metadata-schema changes
- large merges, renames, or deletions
- other high-stakes decisions where preference or judgment materially affects the result

## Companion Skill Map
- `llm-wiki-schema` → frontmatter, lifecycle fields, note shapes, claim blocks, structured relationships
- `llm-wiki-governance` → privacy, visibility, contradiction, supersession, review queue, risky judgments
- `llm-wiki-ops` → naming, layout, index/log, catalog operations

## Working Style
- Think in loop: capture → distill → crystallize → integrate → visualize → review.
- Optimize for long-term compounding usefulness.
- Prefer reversible changes and explicit reasoning.
