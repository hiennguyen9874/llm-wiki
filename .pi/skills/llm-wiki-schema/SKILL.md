---
name: llm-wiki-schema
description: Use when creating or updating wiki/output markdown with frontmatter, lifecycle fields, source metadata, claim blocks, page shapes, or structured relationships.
---

# LLM Wiki Schema

Use when editing structured markdown in `wiki/` or `outputs/`.
Always activate `llm-wiki-core` first.

This skill owns note structure, shared metadata, and canonical page shapes.
It does not own privacy/risk judgments or repo-ops rules.
Longer examples belong in `.pi/skills/llm-wiki-schema/examples.md` if needed.

## What This Skill Owns
- required frontmatter
- recommended lifecycle fields
- allowed enums
- source-page metadata
- claim/evidence structure
- standard page shapes
- markdown conventions that materially affect note structure

## Markdown Authoring Conventions
For markdown in `wiki/` and `outputs/`:
- use YAML frontmatter on wiki pages
- use `[[wikilinks]]` for internal references
- use `![[embed]]` only when embedding materially helps
- use callouts for contradictions, open questions, review notes, or next actions
- use normal markdown links for external URLs
- prefer structures that render cleanly in Obsidian reading mode

## Required Wiki Frontmatter
Use this minimum schema unless evidence does not support a field.

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

## Allowed and Recommended Enums
- `status` = `draft | reviewed | needs_update`
- `page_type` = `home | overview | purpose | index | log | topic | concept | entity | source | synthesis | timeline | decision | person | project | procedure | dashboard | canvas | episode | ingest_plan | review_item`
- `claim_status` = `active | stale | superseded | disputed | hypothesis`
- `retention_class` = `transient | working | episodic | durable | foundational`
- `visibility` = `private | shared | publishable`
- review item `action_type` = `approve_edit | create_page | deep_research | skip | ask_user | resolve_contradiction`

## Field Meanings
- `confidence_score` = current confidence in page claims
- `quality_score` = quality of page structure and usefulness
- `evidence_count` = count of distinct supporting observations/sources
- `first_seen` = when claim or page entered the system
- `last_confirmed` = most recent reinforcing evidence or review
- `claim_status` = active, stale, disputed, superseded, or tentative state
- `retention_class` = expected durability / review cadence class
- `visibility` = intended sharing scope
- `related_sources` = source pages materially supporting the page
- `related_entities` = important linked entities or concepts

## Page-Level vs Claim-Level Tracking
- Use frontmatter lifecycle fields for page-level state by default.
- Add claim-level tracking in the body when a page contains multiple important claims with different confidence, staleness, or dispute states.
- Prefer claim-level blocks for high-value, contested, or fast-changing knowledge.

## Lightweight Scoring Heuristics
### Confidence scoring
- Start around `0.50` for plausible but weakly supported claims.
- Raise with independent reinforcement, direct evidence, recency, and specificity.
- Lower for unresolved contradiction, stale confirmation, indirect evidence, or vague sourcing.
- Rough guide: `0.30–0.49` tentative, `0.50–0.69` plausible, `0.70–0.84` well supported, `0.85–0.95` strong.
- Avoid fake precision.

### Quality scoring
Evaluate whether the page cites sources clearly, separates fact from inference, links related pages, uses clean structure/frontmatter, and reflects current known state.
- Rough guide: `<0.60` needs review, `0.60–0.79` usable but incomplete, `0.80+` strong and reusable.

## Retention Semantics
- `transient` = short-lived, review quickly
- `working` = tied to active investigations, review within weeks
- `episodic` = revisit during crystallization or review cycles
- `durable` = revise when reinforced, contradicted, or during maintenance
- `foundational` = long-lived, highly visible, should stay well sourced

This section defines meaning only. Governance and maintenance decide what actions to take when content goes stale.

## Source Page Schema
Source pages usually also include:

```yaml
source_file: raw/path/to/file.md
source_type: article
canonical_url:
author:
published:
```

Common `source_type` values: `article | paper | book | chapter | note | transcript | documentation | interview | podcast | video | capture | session`

## Standard Page Shapes
### Topic / concept / entity / person / project
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
- what the source is
- why it matters
- key claims
- notable evidence or examples
- entities and relationships extracted from it
- pages updated because of it
- contradictions, supersession, or uncertainty
- whether downstream redaction or sanitization happened

## Claim / Evidence Block
Use for high-value, disputed, or easily stale claims.

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
- a page mixes strong and weak claims
- a claim is disputed or recently superseded
- future maintenance should revisit a claim directly

## Entity and Relationship Capture
At minimum identify important entities, entity type, important attributes if known, and typed relationships between entities or pages.
Preferred verbs: `uses | depends_on | owned_by | caused | fixed | supports | contradicts | supersedes | related_to`

## Minimal Example
```yaml
---
title: Example Topic
created: 2026-04-25
last_updated: 2026-04-25
source_count: 1
status: draft
page_type: topic
aliases: []
tags: []
domain: general
importance: medium
review_status: active
related_sources: [[source-example]]
---
```

For fuller examples, see `.pi/skills/llm-wiki-schema/examples.md`.

## See Also
- `llm-wiki-governance` for privacy, contradiction, retention action, and risky judgment
- `llm-wiki-ops` for naming, layout, index, and log rules
