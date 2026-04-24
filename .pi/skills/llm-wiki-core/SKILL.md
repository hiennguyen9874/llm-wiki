---
name: llm-wiki-core
description: "Shared operating rules for this second-brain repository: architecture, lifecycle, metadata, citations, linking, logging, naming, and governance. Use before any task that materially reads or writes raw/, wiki/, or outputs/."
---

# LLM Wiki Core

Activate before meaningful second-brain work.
This skill holds detailed repo-wide rules. `AGENTS.md` only routes work.

## Identity and Mission
- Repo = personal second brain run by LLM agent.
- Human choose sources, questions, direction.
- Agent do capture, triage, ingest, synthesis, cross-linking, retrieval, crystallization, review, maintenance.
- Optimize for durable, compounding memory, not one-off answers.

## Implementation Stance
- Manual-first, human-steered, prompt-driven.
- Prefer explicit workflows + scheduled reviews over fake hidden automation.
- Design prompts/skills so hooks or scheduled jobs can come later.
- Adopt v4 ideas only as manual, executable conventions unless tooling exists.
- Do not claim automation, graph infra, vector DB, desktop app, persistent queue, derived-index tooling, or lifecycle enforcement repo does not actually have.

## Memory Architecture
- `purpose.md` → directional intent: goals, scope, key questions, active themes, evolving thesis
- `raw/` → immutable capture layer
- `wiki/` → durable semantic knowledge
- `wiki/bases/` → operational dashboards
- `wiki/canvases/` → visual synthesis
- `outputs/` → derived deliverables, analyses, reports, answers, briefings, crystallizations

## Memory Lifecycle
### Working memory
- Mainly `raw/inbox/` + `raw/captures/`
- New, unresolved, low-confidence material
- Not settled knowledge

### Episodic memory
- Mainly `outputs/crystallizations/`, `outputs/analyses/`, saved session digests
- What happened in research / debugging / investigation threads
- More structured than raw, not canonical by default

### Semantic memory
- Mainly `wiki/`
- Durable concepts, entities, people, projects, timelines, synthesized conclusions
- Update when multiple episodes or sources reinforce or revise fact

### Procedural memory
- `AGENTS.md`, `.pi/prompts/`, `.pi/skills/`, workflow/procedure pages
- How system should operate

### Promotion rule
- Do not push every observation straight into `wiki/`.
- Crystallize exploratory work when needed.
- Canonical wiki gets durable, evidence-backed knowledge.
- Stable process lessons go into procedural memory.


## Manual Compile Workflow
Compilation means synthesizing accumulated `raw/` sources and/or durable `outputs/` artifacts into canonical `wiki/` pages. It is distinct from capture and single-source ingest.

Use compile when:
- several sources cover the same topic and should update shared concept/entity/synthesis pages
- saved answers, analyses, or crystallizations should be promoted into semantic memory
- a topic needs a full consistency pass rather than another isolated source summary

Modes:
- `incremental` → process new or changed sources/outputs since the last relevant review/log entry
- `full` → re-read all relevant sources/pages in scope and rewrite/update synthesis more broadly

Rules:
- Read actual files before synthesizing; do not compile from index summaries alone.
- Preserve raw sources unchanged.
- Update canonical pages, `related_sources`, claims, contradictions, confidence/quality, overview, index, and log where justified.
- If the compile plan implies taxonomy/schema/bulk moves/deletes, ask user first.
- If decisions can wait, create review queue items rather than blocking safe compilation.

## Tool Selection Policy
- Use **QMD** as primary local markdown search/retrieval tool for `wiki/`, `raw/`, `outputs/`.
- Use **Defuddle** for standard web URLs before saving into `raw/web-clips/`.
- Use **Obsidian Markdown** conventions for `.md` in `wiki/` and `outputs/`.
- Use **JSON Canvas** when topic needs visual mapping.
- Use **Obsidian Bases** for dashboards, queues, inventories, review flows.
- Use **Obsidian CLI** when live vault interaction helps validate rendering, search, backlinks, discoverability.

## Repository Layout
### `raw/`
- `raw/inbox/` → new files awaiting triage
- `raw/articles/` → saved articles, essays
- `raw/books/` → book notes, chapters, excerpts
- `raw/papers/` → papers, technical reports
- `raw/web-clips/` → cleaned web pages saved as markdown
- `raw/captures/` → quick captures, fleeting notes, copied snippets
- `raw/assets/` → downloaded images, attachments

### `wiki/`
- `wiki/index.md` → browsable catalog of key pages + artifacts
- `wiki/log.md` → append-only operational log
- `wiki/home.md` → stable human landing page
- `wiki/overview.md` → agent-updated current-state synthesis, major clusters, gaps, active direction
- `wiki/bases/` → `.base` dashboards
- `wiki/canvases/` → `.canvas` syntheses
- other `wiki/*.md` → topics, concepts, sources, people, projects, decisions, syntheses, timelines, procedures

### `outputs/`
- `outputs/answers/` → durable answers worth keeping
- `outputs/analyses/` → comparisons, memos, research notes
- `outputs/reports/` → lint reports, audits, reviews
- `outputs/briefings/` → reusable summaries + briefings
- `outputs/crystallizations/` → structured digests from completed investigations
- `outputs/ingest-plans/` → selectively saved stage-1 ingest plans for non-trivial decisions
- `outputs/review-queue/` → one markdown note per human judgment item

## Purpose and Overview Rules
- `purpose.md` answers why the wiki exists; keep strategic direction there, not in workflow policy.
- Read `purpose.md` when broad ingest/query/review/research planning needs goal context.
- `wiki/home.md` is stable human orientation.
- `wiki/overview.md` is the agent-updated current-state synthesis; update it after meaningful ingests, major reviews, or important crystallizations.
- Do not over-read purpose/overview for narrow exact lookups.

## Global Rules
- Wiki = persistent compiled artifact, not chat scratch.
- Keep `related_sources: []` current on wiki pages when sources materially support the page.
- Do not introduce parallel `sources: []` schema unless the human explicitly approves a schema migration.
- Use compile passes to turn multiple raw sources or reusable outputs into canonical semantic pages when one-off ingest would fragment knowledge.
- Prefer updates over redundant near-duplicates.
- Preserve uncertainty explicitly.
- Every factual claim cites source.
- Separate supported fact, inference, speculation.
- If new evidence conflicts with old, preserve provenance + mark relationship.
- Add internal links aggressively when pages relate.
- Keep important insight in durable markdown, not only chat.
- Strong ingest usually updates many related pages, not one summary.
- Keep vault usable in Obsidian.

## Naming Rules
- Use lowercase kebab-case filenames.
- Name pages by stable concept/entity/topic, not vague prose.
- Source pages usually start `source-`.
- Synthesis pages can start `synthesis-`.
- Comparisons can start `compare-`.
- Timelines can start `timeline-`.
- Procedures can start `procedure-`.
- Bases live in `wiki/bases/` and use `.base`.
- Canvases live in `wiki/canvases/` and use `.canvas`.

## Obsidian Markdown Conventions
For markdown in `wiki/` and `outputs/`:
- Use YAML frontmatter at top of every wiki page.
- Use `[[wikilinks]]` for internal refs.
- Use `![[embed]]` when embedding helps.
- Use callouts for contradictions, open questions, review notes, next actions.
- Use normal markdown links only for external URLs.
- Prefer structures that render cleanly in Obsidian reading mode.

## Required Wiki Frontmatter
Use this minimum schema unless evidence does not support field.

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
- `overview`
- `purpose`
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
- `ingest_plan`
- `review_item`

### Recommended lifecycle meanings
- `confidence_score` → current confidence in page claims
- `quality_score` → quality of page itself
- `evidence_count` → distinct supporting observations/sources
- `first_seen` → when claim or page entered system
- `last_confirmed` → most recent reinforcing evidence/review
- `claim_status` → `active | stale | superseded | disputed | hypothesis`
- `retention_class` → `transient | working | episodic | durable | foundational`
- `visibility` → `private | shared | publishable`
- review item `action_type` → `approve_edit | create_page | deep_research | skip | ask_user | resolve_contradiction`

### Page-level vs claim-level lifecycle
- Frontmatter fields apply to page as whole by default.
- For pages with multiple important or contested claims, also track lightweight claim-level records in body.
- Use claim-level tracking when claims have materially different confidence, active dispute, or supersession chains.

## Lightweight Scoring Heuristics
Use unless page needs domain-specific rubric.

### Confidence scoring
- Start near `0.50` for plausible but weakly supported claim.
- Raise with independent reinforcement, recency, direct evidence, specificity.
- Lower for unresolved contradiction, stale confirmation, indirect evidence, vague sourcing.
- Rough guide:
  - `0.30–0.49` → tentative / hypothesis
  - `0.50–0.69` → plausible but still weak or narrow
  - `0.70–0.84` → well supported
  - `0.85–0.95` → strong, repeatedly reinforced
- Small updates enough. Avoid fake precision.

### Quality scoring
Evaluate whether page:
- cites sources clearly
- separates fact from inference
- links related pages
- uses clean structure/frontmatter
- reflects current known state

Rough guide:
- `< 0.60` → needs review or rewrite
- `0.60–0.79` → usable but incomplete
- `0.80+` → strong, reusable

## Retention and Review Expectations
Use `retention_class` to shape review cadence + decay.

- `transient` → review fast; can go stale in days/weeks
- `working` → review within weeks; often tied to active investigations
- `episodic` → review during crystallization or periodic review
- `durable` → review when reinforced, contradicted, or during broader maintenance
- `foundational` → review slowly, keep highly visible + well sourced

Decay guidance:
- Do not delete just because old.
- If claim lacks reinforcement within plausible window for its class, lower confidence modestly or mark `stale`.
- When new evidence reaffirms claim, refresh `last_confirmed` + raise confidence if justified.
- Preserve provenance even when downgrading confidence.

## Visibility Semantics
- `private` → personal notes, preferences, sensitive synthesis, or material not meant for sharing
- `shared` → safe for normal collaboration inside project/team context
- `publishable` → sanitized and appropriate for external reuse

Rules:
- Default `private` unless clear reason to widen.
- Do not mark `publishable` unless sanitized and source-safe.
- Before moving `private` toward `shared`, review for sensitive detail removal.

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
Use when helpful:
- Summary
- Key points
- Relationships
- Evidence / claims
- Open questions
- Related pages
- Sources

### Source pages
Capture:
- what source is
- why it matters
- key claims
- notable evidence/examples
- entities + relationships extracted from it
- pages updated because of it
- contradictions, supersession, uncertainty
- whether downstream redaction/sanitization happened

## Claim and Evidence Model
For high-value, disputed, or easily stale knowledge, prefer lightweight claim blocks inside `Evidence / claims`.

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

Use when:
- page mixes strong + weak claims
- claim is disputed or recently superseded
- claim is important enough that future maintenance should revisit it directly

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
- Canonical knowledge layer stays markdown-first.
- Typed relationships live mainly in prose pages, frontmatter, structured sections.
- Canvases + Bases are overlays for navigation/review, not sole source of truth.
- Until separate graph artifact exists, query + maintenance should traverse page content, links, frontmatter, related entities.

## Supersession and Contradiction Policy
When newer or stronger evidence updates older claim:
- preserve old provenance
- mark `stale`, `disputed`, or `superseded`
- link replacements with `supersedes` / `superseded_by`
- update `last_confirmed`, `evidence_count`, `confidence_score` when justified

Use these factors to assess likely-current truth:
- recency
- authority/directness
- number of supporting sources
- specificity of evidence

Default resolution:
- if one side clearly stronger, mark weaker claim/page `superseded` or `stale`
- if evidence mixed, keep both visible + mark issue `disputed`
- explain reasoning briefly; do not silently overwrite tension

## Review Queue Rules
- Use one markdown note per review item in `outputs/review-queue/`.
- Create review items when a workflow needs human judgment but can continue safely without immediate blocking.
- Use constrained actions: `approve_edit`, `create_page`, `deep_research`, `skip`, `ask_user`, `resolve_contradiction`.
- Include source/context links, recommendation, options, and status (`open | decided | done | skipped`).
- Ask user immediately instead of queueing when the decision is high-stakes, irreversible, or blocks safe progress.


## Index as Rebuildable Catalog
`wiki/index.md` remains a required human/agent catalog and should be updated on meaningful writes. Treat it as a rebuildable cache, not the source of truth. The source of truth is the actual markdown files, frontmatter, wikilinks, `related_sources`, and log.

If index drift is suspected during query, ingest, compile, or maintenance:
1. Prefer actual file/frontmatter evidence over stale index rows.
2. Repair the index during maintenance/lint or as part of the current write if safe.
3. Log meaningful rebuilds or repairs.

Do not skip index updates by default just because it is rebuildable; until tooling exists, update it explicitly.

## Index and Log Rules
### `wiki/index.md`
- Human orientation + browsing
- Keep concise + browsable
- Include notable bases + canvases
- Update on every ingest and whenever important pages/artifacts are added or materially changed

### `wiki/log.md`
- Append-only chronological record
- Never rewrite prior entries except tiny formatting repairs
- Entry format: `## [YYYY-MM-DD] action | Description`
- Allowed actions:
  - `setup`
  - `capture`
  - `ingest`
  - `query`
  - `lint`
  - `update`
  - `review`
  - `research`
  - `visualize`
  - `crystallize`
- For meaningful updates, include:
  - why change happened
  - which important pages/artifacts changed
  - whether change resolved contradiction, retention, privacy, or quality issue
- For bulk or structural changes, make scope + rule explicit.

## Focus Areas
Default domains:
1. Projects and work
2. Research and learning
3. Ideas and writing
4. People and relationships
5. Health, habits, and personal systems

## Privacy and Governance
- Do not commit secrets, credentials, tokens, or private data into wiki.
- Screen new material for secrets, PII, or private content before promoting into `wiki/` or `outputs/`.
- If raw file contains active secrets or highly sensitive material that should not remain in repo, stop and ask user before proceeding.
- Sanitize sensitive source material before downstream summaries.
- Note important downstream redactions in source page when relevant.
- Keep provenance + auditability through `wiki/log.md` and saved outputs.
- Prefer reversible bulk changes and document why.


## Lint-as-Migration Principle
When workflow schema evolves, prefer encoding safe repair rules in maintenance/lint rather than one-off migrations. Apply this conservatively.

Safe automatic repairs include:
- missing required frontmatter with obvious defaults
- index/catalog drift
- clear broken internal links or unambiguous backlinks
- legacy field aliases explicitly documented in policy
- minor metadata normalization with provenance preserved

Ask user before:
- major schema migration
- taxonomy/folder changes
- bulk moves/renames/deletes
- merging many pages
- changes that could remove provenance or private context

## Decision Hygiene
Ask user before:
- renaming large sets of pages
- deleting pages
- changing folder taxonomy
- changing metadata schema significantly
- merging many pages into one canonical structure
- performing bulk privacy cleanup that could remove source info

## Working Style
- Be proactive about structure.
- Prefer durable markdown artifacts over chat-only summaries.
- Optimize for long-term compounding usefulness.
- Think in loop: capture → distill → crystallize → integrate → visualize → review.
