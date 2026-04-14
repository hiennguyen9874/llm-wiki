# Second Brain Knowledge Base Schema

## Identity
This repository is a personal second brain maintained by an LLM agent.
The human curates sources, asks questions, and steers direction.
The LLM handles capture, triage, ingestion, synthesis, cross-linking, retrieval, crystallization, review, and maintenance.

## Mission
Turn raw documents, notes, transcripts, URLs, analyses, and exploratory sessions into a persistent, compounding memory system.
Do not re-derive knowledge from scratch when it can be compiled once, strengthened over time, and revised as evidence changes.

## Core Architecture
This system has five primary layers:
- `raw/` → immutable capture layer
- `wiki/` → semantic knowledge layer for durable pages
- `wiki/bases/` → operational dashboard layer for Obsidian Bases
- `wiki/canvases/` → visual synthesis layer for JSON Canvas
- `outputs/` → derived deliverables, analyses, reports, and crystallizations

## Memory Lifecycle
Not all information is equally mature or equally permanent.
Treat knowledge as moving through tiers.

### Working memory
- Lives mainly in `raw/inbox/` and `raw/captures/`
- Includes newly dropped files, fleeting notes, copied snippets, and unresolved observations
- Low confidence by default
- Should not be treated as settled knowledge

### Episodic memory
- Lives mainly in `outputs/crystallizations/`, `outputs/analyses/`, and saved session digests
- Captures what happened in a session, investigation, research thread, or debugging arc
- More structured than raw material, but not yet canonical

### Semantic memory
- Lives in `wiki/`
- Represents durable cross-source concepts, entities, projects, people, timelines, and synthesized conclusions
- Should be updated when multiple episodes or sources reinforce or revise a fact

### Procedural memory
- Lives in `AGENTS.md`, prompt files, and durable workflow/procedure pages
- Captures how the system should operate, not just what it knows
- Promoted from repeated successful patterns

Promotion rule:
- Do not promote every observation directly into semantic memory.
- First crystallize exploratory work when needed, then consolidate only the durable parts into `wiki/`.

## Tool Selection Policy
Use the best local tool for the job.

- Use **QMD** as the primary local search/retrieval tool for markdown in `wiki/`, `raw/`, and `outputs/`.
- Use **Defuddle** for standard web URLs before saving them into `raw/web-clips/`.
- Use **Obsidian Markdown** conventions for all `.md` files in the vault.
- Use **JSON Canvas** when a topic benefits from visual mapping, relationships, timelines, or cluster synthesis.
- Use **Obsidian Bases** for dashboards, queues, inventories, and review workflows.
- Use **Obsidian CLI** when interacting with a running Obsidian vault helps validate rendering, search, or note behavior.

## Repository Layout
### raw/
- `raw/inbox/` → newly dropped files awaiting triage
- `raw/articles/` → saved articles and essays
- `raw/books/` → book notes, chapter files, excerpts
- `raw/papers/` → papers and technical reports
- `raw/web-clips/` → cleaned web pages saved as markdown
- `raw/captures/` → quick captures, fleeting notes, rough observations, copied snippets
- `raw/assets/` → downloaded images and attachments

### wiki/
- `wiki/index.md` → human-readable catalog of wiki pages and important artifacts
- `wiki/log.md` → append-only operational log
- `wiki/home.md` → high-level overview of the knowledge base
- `wiki/bases/` → `.base` dashboard files
- `wiki/canvases/` → `.canvas` visual maps
- all other `wiki/*.md` files → topic, concept, entity, source, person, project, timeline, decision, procedure, and synthesis pages

### outputs/
- `outputs/answers/` → durable answers worth saving
- `outputs/analyses/` → comparisons, memos, research notes
- `outputs/reports/` → lint reports, reviews, audits
- `outputs/briefings/` → summaries and briefings prepared for later reuse
- `outputs/crystallizations/` → structured digests distilled from completed research, debugging, or exploration sessions

## Focus Areas
This second brain currently spans these default areas:
1. Projects and work
2. Research and learning
3. Ideas and writing
4. People and relationships
5. Health, habits, and personal systems

Adjust these areas over time as the repository becomes more domain-specific.

## Global Rules
- Treat the wiki as a persistent compiled artifact, not ephemeral chat output.
- Prefer updating existing pages over creating redundant near-duplicates.
- Preserve uncertainty explicitly.
- Every factual claim must cite a source.
- When new evidence conflicts with old evidence, preserve provenance and mark the relationship between old and new claims.
- Add internal links aggressively when pages are related.
- Use durable markdown artifacts instead of leaving important insights only in chat.
- A strong ingest usually updates many related pages, not just one summary file.
- Promote repeated and reinforced observations upward through the memory tiers.
- Keep the vault usable in Obsidian, not only machine-readable.

## File Naming
- Use lowercase kebab-case for filenames.
- Name pages by stable concept/entity/topic, not by vague prose titles.
- Source pages usually start with `source-`.
- Synthesis pages can start with `synthesis-`.
- Comparisons can start with `compare-`.
- Timelines can start with `timeline-`.
- Procedures can start with `procedure-` when helpful.
- Bases live in `wiki/bases/` and use `.base`.
- Canvases live in `wiki/canvases/` and use `.canvas`.

## Obsidian Markdown Conventions
All markdown in `wiki/` and `outputs/` should be valid Obsidian Flavored Markdown.

Rules:
- Use YAML frontmatter at the top of every wiki page.
- Use `[[wikilinks]]` for internal references.
- Use `![[embed]]` syntax when embedding related notes, canvases, or files is useful.
- Use callouts when highlighting contradictions, open questions, review notes, or next actions.
- Use markdown links only for external URLs.
- Prefer Obsidian-friendly structure that renders cleanly in reading mode.

## Wiki Metadata Schema
Use a minimal required schema plus optional lifecycle fields.
Do not invent fake precision; only populate fields the current evidence supports.

### Minimum frontmatter
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

### Recommended extended lifecycle fields
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
- `confidence_score` → 0.0 to 1.0 estimate of current confidence
- `quality_score` → quality of the page itself, not truth of the claims
- `evidence_count` → count of distinct supporting observations/sources
- `first_seen` → when the claim or page first entered the system
- `last_confirmed` → latest date the claim was reinforced by evidence or review
- `claim_status` → `active | stale | superseded | disputed | hypothesis`
- `retention_class` → `transient | working | episodic | durable | foundational`
- `visibility` → `private | shared | publishable`
- `supersedes` / `superseded_by` → explicit links to outdated or replacing knowledge

## Source Page Schema
Source pages should usually include:

```yaml
---
title: Source Title
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
source_count: 1
status: draft
page_type: source
aliases: []
tags: [source]
domain: general
importance: medium
review_status: processed
related_sources: []
confidence_score: 0.60
quality_score: 0.80
evidence_count: 1
first_seen: YYYY-MM-DD
last_confirmed: YYYY-MM-DD
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities: []
source_file: raw/path/to/file.md
source_type: article
canonical_url:
author:
published:
---
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

## Standard Page Structure
### Topic / concept / entity / person / project pages
Use this shape when helpful:
- Summary
- Key points
- Relationships
- Evidence / claims
- Open questions
- Related pages
- Sources

### Source pages
Source pages should capture:
- what the source is
- why it matters
- key claims
- notable evidence/examples
- entities and relationships extracted from it
- pages updated because of it
- contradictions, supersession, or uncertainty

## Entity and Relationship Extraction
During ingest and crystallization, extract structure in addition to prose.

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

For now, store this structure lightly inside markdown pages and frontmatter.
Do not overbuild a separate graph system until the wiki size demands it.

## Supersession Policy
Contradictions are not enough by themselves.
When newer or stronger evidence updates an older claim:
- preserve the old claim's provenance
- mark the old claim as `stale`, `disputed`, or `superseded`
- link the replacement using `supersedes` / `superseded_by`
- update `last_confirmed`, `evidence_count`, and `confidence_score` where appropriate

Use these factors when deciding likely-current truth:
- recency of the source
- authority/directness of the source
- number of supporting sources
- specificity of the evidence

If unresolved, keep both claims visible and mark the uncertainty clearly.

## Index and Log
### `wiki/index.md`
- Exists primarily for human orientation and browsing.
- Keep it concise and browsable.
- Include notable bases and canvases.
- Update on every ingest and whenever significant new pages are created.
- Do not rely on it as the only search mechanism once the wiki grows.

### `wiki/log.md`
- Append-only chronological record.
- Never rewrite prior entries except to repair formatting mistakes.
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

## Search Policy
Use hybrid retrieval behavior even if QMD remains the primary tool.

### Human orientation
- Read `wiki/index.md` when broad orientation is useful.
- Do not force index-first reading for every narrow lookup.

### Retrieval strategy
1. Use QMD lexical search for exact names and terms.
2. Use QMD semantic or expanded search when vocabulary is uncertain.
3. Use metadata-aware filtering mentally or via Bases when status, recency, or type matters.
4. Expand outward from key entities and relationships mentioned in the first results.
5. Read the actual files before editing or synthesizing.
6. Re-index/embed after large updates if search quality becomes stale.

## Capture and Triage Workflow
Use this when new material appears in `raw/inbox/`, `raw/captures/`, or arrives through chat.

1. Review the new item.
2. Classify it as one of:
   - article
   - paper
   - book/chapter
   - note/capture
   - transcript
   - documentation
   - reference
   - session artifact
3. Move or save it into the appropriate raw subfolder when needed.
4. Preserve the raw source unchanged.
5. Record meaningful intake activity in `wiki/log.md` as `capture` when appropriate.
6. Then run the ingest workflow.

## URL Ingest Workflow
When the user provides a standard web URL:
1. Use Defuddle to extract clean markdown.
2. Save the cleaned result into `raw/web-clips/` with a stable kebab-case filename.
3. Preserve the original URL in source metadata (`canonical_url`).
4. Then ingest it like any other source.
5. Do not use Defuddle for URLs ending in `.md`; fetch/read those directly.

## Ingest Workflow
When processing a new source:
1. Read the full source document.
2. Read `wiki/index.md` only if broad orientation is needed.
3. Use QMD to find relevant existing wiki pages and prior sources.
4. Extract key entities, attributes, and typed relationships.
5. Assess whether the source introduces new facts, reinforces existing ones, or supersedes older claims.
6. Create or update a dedicated source page in `wiki/`.
7. Update all relevant topic, concept, entity, project, person, and timeline pages.
8. Add backlinks from existing pages to the new material.
9. Flag contradictions explicitly and mark supersession when justified.
10. Update lifecycle metadata when the evidence supports it.
11. Update `wiki/index.md`.
12. Append an `ingest` entry to `wiki/log.md`.
13. If the ingest produces durable standalone analysis, save it to `outputs/`.
14. If the topic has become structurally complex, consider creating or updating a canvas or base.
15. Aim for broad integration across the wiki, not isolated summaries.

## Crystallization Workflow
Exploration itself is a source.
When a research thread, debugging session, or analysis produced durable insight:
1. Distill the session into a structured digest in `outputs/crystallizations/` or `outputs/analyses/`.
2. Capture:
   - original question
   - what was investigated
   - key findings
   - affected files/entities/pages
   - unresolved questions
   - reusable lessons
3. Promote durable lessons into `wiki/` pages or update existing ones.
4. Add links from the crystallization artifact back to canonical pages.
5. Log meaningful work as `crystallize` or `update`.

## Query Workflow
When answering a question:
1. Use `wiki/index.md` for orientation when helpful, not by reflex.
2. Use QMD to find relevant pages across `wiki/`, `outputs/`, and optionally `raw/`.
3. Expand from the first results using entities, metadata, and typed relationships.
4. Read the relevant pages before synthesizing.
5. Answer with citations to the pages that informed the answer.
6. Mention confidence, staleness, dispute, or supersession when it materially affects the answer.
7. If raw sources are needed to resolve ambiguity, read them directly.
8. If the answer creates durable value, save it in `outputs/answers/` or promote it into `wiki/`.
9. If a visual or dashboard artifact would help, create/update a canvas or base.
10. Append a `query` entry when a saved artifact is produced.

## Visual Synthesis Workflow
Use JSON Canvas when a topic is relational, ambiguous, or benefits from spatial organization.

Good use cases:
- concept maps
- source relationship maps
- project strategy maps
- timelines and causal maps
- people/projects/ideas relationship maps

Workflow:
1. Decide the canvas purpose.
2. Create or update a `.canvas` file in `wiki/canvases/`.
3. Use nodes for concepts, source notes, projects, prompts, or lifecycle stages.
4. Connect them with labeled edges where useful.
5. Keep layout readable and validate JSON integrity.
6. Add the canvas to `wiki/index.md`.
7. Log meaningful work as `visualize` or `update`.

## Bases Workflow
Use Obsidian Bases for operational dashboards and review queues.

Good use cases:
- inbox queue
- source inventory
- stale-page review queue
- project tracker
- reading list
- outputs-to-promote queue
- pages with low confidence or low quality

Workflow:
1. Create or update `.base` files in `wiki/bases/`.
2. Use filters over folders, tags, and metadata.
3. Add formulas only when they materially improve review or triage.
4. Validate YAML carefully.
5. Add important bases to `wiki/index.md`.

## Review Workflow
### Weekly review
- Process `raw/inbox/` and `raw/captures/`
- Review recent ingests and crystallizations
- Promote durable outputs into `wiki/`
- Review stale drafts and pages marked `needs_update`
- Refresh lifecycle metadata when evidence changed
- Check whether any new canvas or base should be created

### Monthly review
- Run the lint workflow
- Refresh major topic pages
- Check orphan pages and weakly linked areas
- Review stale or low-confidence knowledge
- Update at least one major synthesis page or canvas
- Identify top knowledge gaps and next-source targets
- Record review activity in `wiki/log.md` as `review`

## Lint Workflow
Run monthly or on request.
Check for:
- contradictions between pages
- stale claims superseded by newer sources
- orphan pages with no inbound links
- concepts mentioned but never explained
- duplicate pages that should be merged
- missing cross-references
- claims without source attribution
- source pages not integrated into broader topic pages
- missing lifecycle metadata on important pages
- low-confidence or low-quality pages that need review
- unresolved supersession chains
- bases or canvases that no longer reflect the current wiki state

Self-heal automatically when safe:
- repair obvious broken internal links
- mark stale pages as `needs_update`
- add missing backlinks when they are unambiguous
- propose merges for near-duplicates

Output format:
- Save to `outputs/reports/lint-report-[date].md`
- Use severity levels:
  - 🔴 errors
  - 🟡 warnings
  - 🔵 info

Also propose:
- 3 important knowledge gaps
- 3 possible next sources to ingest
- 3 pages or artifacts that need consolidation

## Update Workflow
When asked to improve the wiki without a new source:
1. Use `wiki/index.md` for orientation if needed.
2. Use QMD to find weakly connected, stale, disputed, or duplicate areas.
3. Merge duplicates, add links, improve summaries, and strengthen citations.
4. Refresh lifecycle metadata and supersession links where justified.
5. Update bases/canvases when they are out of sync with the markdown layer.
6. Record meaningful changes in `wiki/log.md` as `update`.

## Privacy and Governance
- Do not commit secrets, credentials, tokens, or private data into the wiki.
- If a source contains sensitive information, sanitize before adding it to the repository.
- Keep provenance and auditability for meaningful changes through `wiki/log.md` and saved outputs.
- Prefer reversible bulk changes and document why they were made.

## Target Automation Direction
Design the system so these can eventually be automated:
- on new source → triage + ingest
- on session end → crystallize durable findings
- on wiki write → contradiction/supersession check
- on schedule → lint, review, and stale-knowledge scan

Automation is a goal, but the manual workflow should already reflect these behaviors.

## Vault Interaction Policy
If Obsidian is open and the task benefits from live vault interaction, use Obsidian CLI to:
- search the vault
- inspect backlinks or properties
- create/open notes
- validate that notes render or exist as expected

Use this especially for:
- checking note discoverability
- validating Bases or Canvas behavior
- supporting plugin/theme/vault workflows

## Decision Hygiene
Ask the user before irreversible or high-level structural changes.
Examples:
- renaming large sets of pages
- deleting pages
- changing folder taxonomy
- changing metadata schema significantly
- merging many pages into one canonical structure

## Working Style
- Be proactive about structure.
- Prefer durable markdown artifacts over chat-only summaries.
- Keep the vault browseable by a human in Obsidian.
- Think in the loop: capture → distill → crystallize → integrate → visualize → review.
- Optimize for long-term compounding usefulness.

## Full Pattern Reference
Read `LLM-WIKI.md` and `LLM-WIKI-v2.md` for the pattern and the lifecycle-oriented extensions behind this system.
