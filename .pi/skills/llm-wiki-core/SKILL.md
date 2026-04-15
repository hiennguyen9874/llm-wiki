---
name: llm-wiki-core
description: "Shared operating rules for this second-brain repository: architecture, lifecycle, metadata, citations, linking, logging, naming, and governance. Use before any task that materially reads or writes raw/, wiki/, or outputs/."
---

# LLM Wiki Core

Activate this skill before any meaningful second-brain task.
It defines the shared rules that all other workflow skills depend on.

## Identity and Mission
- This repo is a personal second brain maintained by an LLM agent.
- The human curates sources, asks questions, and steers direction.
- The agent handles capture, triage, ingestion, synthesis, cross-linking, retrieval, crystallization, review, and maintenance.
- Optimize for persistent, compounding memory rather than one-off answers.

## Implementation Stance
- This repository is currently **manual-first, human-steered, and prompt-driven**.
- Prefer explicit workflows and scheduled reviews over pretending hidden automation already exists.
- Design prompts and skills so they can later support hooks or scheduled jobs.
- Do not claim automation, graph infrastructure, or lifecycle enforcement that the repo does not yet actually have.

## Memory Architecture
- `raw/` → immutable capture layer
- `wiki/` → semantic knowledge layer for durable pages
- `wiki/bases/` → operational dashboard layer
- `wiki/canvases/` → visual synthesis layer
- `outputs/` → derived deliverables, analyses, reports, answers, briefings, and crystallizations

## Memory Lifecycle
### Working memory
- Mainly `raw/inbox/` and `raw/captures/`
- New, unresolved, low-confidence material
- Do not treat as settled knowledge

### Episodic memory
- Mainly `outputs/crystallizations/`, `outputs/analyses/`, and saved session digests
- Captures what happened in a research/debugging/investigation thread
- More structured than raw, but not yet canonical by default

### Semantic memory
- Mainly `wiki/`
- Durable concepts, entities, people, projects, timelines, and synthesized conclusions
- Update when multiple episodes or sources reinforce or revise a fact

### Procedural memory
- Lives in `AGENTS.md`, `.pi/prompts/`, `.pi/skills/`, and durable workflow/procedure pages
- Captures how the system should operate

### Promotion rule
- Do not promote every observation directly into `wiki/`.
- Crystallize exploratory work when needed.
- Consolidate only durable, evidence-backed knowledge into canonical wiki pages.
- Promote repeated process lessons into procedural memory when they are stable enough to guide future sessions.

## Tool Selection Policy
- Use **QMD** as the primary local search/retrieval tool for markdown in `wiki/`, `raw/`, and `outputs/`.
- Use **Defuddle** for standard web URLs before saving into `raw/web-clips/`.
- Use **Obsidian Markdown** conventions for all `.md` files in `wiki/` and `outputs/`.
- Use **JSON Canvas** when a topic benefits from visual mapping or relationships.
- Use **Obsidian Bases** for dashboards, queues, inventories, and review workflows.
- Use **Obsidian CLI** when live vault interaction helps validate rendering, search, backlinks, or discoverability.

## Repository Layout
### `raw/`
- `raw/inbox/` → newly dropped files awaiting triage
- `raw/articles/` → saved articles and essays
- `raw/books/` → book notes, chapters, excerpts
- `raw/papers/` → papers and technical reports
- `raw/web-clips/` → cleaned web pages saved as markdown
- `raw/captures/` → quick captures, fleeting notes, copied snippets
- `raw/assets/` → downloaded images and attachments

### `wiki/`
- `wiki/index.md` → browsable catalog of important pages and artifacts
- `wiki/log.md` → append-only operational log
- `wiki/home.md` → high-level overview
- `wiki/bases/` → `.base` dashboard files
- `wiki/canvases/` → `.canvas` synthesis files
- Other `wiki/*.md` pages → topics, concepts, sources, people, projects, decisions, syntheses, timelines, procedures

### `outputs/`
- `outputs/answers/` → durable answers worth keeping
- `outputs/analyses/` → comparisons, memos, research notes
- `outputs/reports/` → lint reports, audits, reviews
- `outputs/briefings/` → reusable summaries and briefings
- `outputs/crystallizations/` → structured digests from completed investigations

## Global Rules
- Treat the wiki as a persistent compiled artifact, not ephemeral chat output.
- Prefer updating existing pages over creating redundant near-duplicates.
- Preserve uncertainty explicitly.
- Every factual claim must cite a source.
- Distinguish clearly between supported facts, reasonable inference, and open speculation.
- When new evidence conflicts with old evidence, preserve provenance and mark the relationship.
- Add internal links aggressively when pages are related.
- Keep important insights in durable markdown artifacts, not only in chat.
- A strong ingest usually updates many related pages, not just one summary file.
- Keep the vault usable in Obsidian, not only machine-readable.

## Naming Rules
- Use lowercase kebab-case for filenames.
- Name pages by stable concept/entity/topic, not vague prose titles.
- Source pages usually start with `source-`.
- Synthesis pages can start with `synthesis-`.
- Comparisons can start with `compare-`.
- Timelines can start with `timeline-`.
- Procedures can start with `procedure-`.
- Bases live in `wiki/bases/` and use `.base`.
- Canvases live in `wiki/canvases/` and use `.canvas`.

## Obsidian Markdown Conventions
For markdown in `wiki/` and `outputs/`:
- Use YAML frontmatter at the top of every wiki page.
- Use `[[wikilinks]]` for internal references.
- Use `![[embed]]` when embedding is useful.
- Use callouts for contradictions, open questions, review notes, or next actions.
- Use normal markdown links only for external URLs.
- Prefer structures that render cleanly in Obsidian reading mode.

## Required Wiki Frontmatter
Use this minimum schema unless the evidence does not support a field.

```yaml
---
title: Topic Name
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
source_count: 0
status: draft
page_type: topic
aliases: []
tags: []
domain: general
importance: medium
review_status: active
related_sources: []
---
```

## Recommended Lifecycle Fields
```yaml
confidence_score: 0.70
quality_score: 0.80
evidence_count: 3
first_seen: YYYY-MM-DD
last_confirmed: YYYY-MM-DD
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities: []
```

### Allowed `status`
- `draft`
- `reviewed`
- `needs_update`

### Common `page_type`
- `home`
- `index`
- `log`
- `topic`
- `concept`
- `entity`
- `source`
- `synthesis`
- `timeline`
- `decision`
- `person`
- `project`
- `procedure`
- `dashboard`
- `canvas`
- `episode`

### Recommended lifecycle meanings
- `confidence_score` → current confidence in the claims on the page
- `quality_score` → quality of the page itself
- `evidence_count` → number of distinct supporting observations/sources
- `first_seen` → when the claim or page first entered the system
- `last_confirmed` → most recent reinforcing evidence/review
- `claim_status` → `active | stale | superseded | disputed | hypothesis`
- `retention_class` → `transient | working | episodic | durable | foundational`
- `visibility` → `private | shared | publishable`

### Page-level vs claim-level lifecycle
- Frontmatter fields apply to the page as a whole by default.
- For pages with multiple important or contested claims, also maintain lightweight claim-level records in the body.
- Use claim-level tracking when a page contains materially different confidence levels, ongoing disputes, or supersession chains.

## Lightweight Scoring Heuristics
Use these heuristics unless a page needs a more specific domain rubric.

### Confidence scoring
- Start around `0.50` for a plausible but weakly supported claim.
- Raise confidence with independent reinforcement, recency, direct evidence, and specificity.
- Lower confidence for unresolved contradiction, stale confirmation, indirect evidence, or vague sourcing.
- Rough guide:
  - `0.30–0.49` → tentative / hypothesis
  - `0.50–0.69` → plausible but still weak or narrow
  - `0.70–0.84` → well supported
  - `0.85–0.95` → strong, repeatedly reinforced
- Small updates are enough; avoid fake precision.

### Quality scoring
Evaluate whether the page:
- cites sources clearly
- distinguishes fact from inference
- links to related pages
- uses clean structure/frontmatter
- reflects the current known state

Rough guide:
- `< 0.60` → needs review or rewrite
- `0.60–0.79` → usable but incomplete
- `0.80+` → strong, reusable page

## Retention and Review Expectations
Use `retention_class` to shape review cadence and decay behavior.

- `transient` → review quickly; can go stale within days or weeks
- `working` → review within weeks; often tied to active investigations
- `episodic` → review during crystallization or periodic review
- `durable` → review when reinforced, contradicted, or during broader maintenance
- `foundational` → review slowly, but keep highly visible and well sourced

Decay guidance:
- Do not delete purely because something is old.
- If a claim has not been reinforced within a plausible window for its retention class, lower confidence modestly or mark it `stale`.
- When new evidence reaffirms a claim, refresh `last_confirmed` and raise confidence if justified.
- Preserve provenance even when downgrading confidence.

## Visibility Semantics
- `private` → personal notes, preferences, sensitive synthesis, or material not meant for sharing
- `shared` → safe for normal collaboration inside the project/team context
- `publishable` → sanitized and appropriate for external reuse

Rules:
- Default to `private` unless there is a clear reason to widen scope.
- Do not mark material `publishable` unless it is sanitized and source-safe.
- When promoting content from `private` toward `shared`, review whether any sensitive details should be removed first.

## Source Page Schema
Source pages usually also include:

```yaml
source_file: raw/path/to/file.md
source_type: article
canonical_url:
author:
published:
```

Common `source_type` values:
- `article`
- `paper`
- `book`
- `chapter`
- `note`
- `transcript`
- `documentation`
- `interview`
- `podcast`
- `video`
- `capture`
- `session`

## Standard Page Shapes
### Topic / concept / entity / person / project pages
Use these sections when helpful:
- Summary
- Key points
- Relationships
- Evidence / claims
- Open questions
- Related pages
- Sources

### Source pages
Capture:
- what the source is
- why it matters
- key claims
- notable evidence/examples
- entities and relationships extracted from it
- pages updated because of it
- contradictions, supersession, or uncertainty
- whether any downstream redaction/sanitization was applied

## Claim and Evidence Model
For high-value, disputed, or easily stale knowledge, prefer lightweight claim blocks inside `Evidence / claims` sections.

Suggested shape:

```md
#### Claim
- Statement: ...
- Status: active
- Confidence: 0.78
- Evidence: [[source-a]], [[source-b]]
- Last confirmed: YYYY-MM-DD
- Notes: why this is believed, what could change it
- Supersedes: [[older-page-or-claim]]
```

Use this pattern when:
- a page mixes strong and weak claims
- a claim is disputed or recently superseded
- the claim is important enough that future maintenance should revisit it directly

## Entity and Relationship Extraction
At minimum identify:
- important entities
- entity type
- key attributes if known
- typed relationships between entities or pages

Preferred relationship verbs:
- `uses`
- `depends_on`
- `owned_by`
- `caused`
- `fixed`
- `supports`
- `contradicts`
- `supersedes`
- `related_to`

## Graph Representation Stance
- The canonical knowledge layer is still markdown-first.
- Typed relationships live primarily in prose pages, frontmatter fields, and structured sections.
- Canvases and Bases are overlays for navigation and review, not the sole source of truth.
- Until a separate graph artifact exists, query and maintenance work should traverse relationships through page content, links, frontmatter, and related entities.

## Supersession and Contradiction Policy
When newer or stronger evidence updates an older claim:
- preserve the old claim's provenance
- mark it as `stale`, `disputed`, or `superseded`
- link replacements with `supersedes` / `superseded_by`
- update `last_confirmed`, `evidence_count`, and `confidence_score` when justified

Use these factors to assess likely-current truth:
- recency
- authority/directness
- number of supporting sources
- specificity of evidence

Default resolution behavior:
- if one side is clearly stronger, mark the weaker claim/page as `superseded` or `stale`
- if evidence is mixed, keep both visible and mark the issue `disputed`
- explain the reasoning briefly instead of silently overwriting tension

## Index and Log Rules
### `wiki/index.md`
- Exists for human orientation and browsing
- Keep it concise and browsable
- Include notable bases and canvases
- Update on every ingest and whenever important pages/artifacts are added or materially changed

### `wiki/log.md`
- Append-only chronological record
- Never rewrite prior entries except tiny formatting repairs
- Entry format:
  `## [YYYY-MM-DD] action | Description`
- Allowed actions:
  - `setup`
  - `capture`
  - `ingest`
  - `query`
  - `lint`
  - `update`
  - `review`
  - `visualize`
  - `crystallize`
- For meaningful updates, include enough detail to recover intent later:
  - why the change happened
  - which important pages/artifacts were touched
  - whether the change resolved contradiction, retention, privacy, or quality issues
- For bulk or structural changes, make the scope and rule explicit.

## Focus Areas
Default domains currently emphasized:
1. Projects and work
2. Research and learning
3. Ideas and writing
4. People and relationships
5. Health, habits, and personal systems

## Privacy and Governance
- Do not commit secrets, credentials, tokens, or private data into the wiki.
- Screen new material for secrets, PII, or private content before promoting it into `wiki/` or `outputs/`.
- If a raw file contains active secrets or highly sensitive material that should not remain in the repo, stop and ask the user before proceeding.
- Sanitize sensitive source material before adding downstream summaries.
- Note important downstream redactions in the source page when relevant.
- Keep provenance and auditability through `wiki/log.md` and saved outputs.
- Prefer reversible bulk changes and document why they were made.

## Decision Hygiene
Ask the user before:
- renaming large sets of pages
- deleting pages
- changing folder taxonomy
- changing metadata schema significantly
- merging many pages into one canonical structure
- performing bulk privacy cleanup that could remove source information

## Working Style
- Be proactive about structure.
- Prefer durable markdown artifacts over chat-only summaries.
- Optimize for long-term compounding usefulness.
- Think in the loop: capture → distill → crystallize → integrate → visualize → review.

## Pattern References
Read `LLM-WIKI.md` and `LLM-WIKI-v2.md` when changing the system design or lifecycle rules.
