---
name: llm-wiki-governance
description: Use when handling privacy, visibility, contradiction, supersession, review-queue decisions, migration boundaries, or other risky judgment calls in the wiki.
---

# LLM Wiki Governance

Use when a task involves judgment, safety, provenance, or conflict handling.
Always activate `llm-wiki-core` first.

This skill owns safety and decision boundaries.
It does not define workflow procedure or page schema mechanics.

## What This Skill Owns
- privacy and sensitive-content boundaries
- visibility decisions
- contradiction and supersession handling
- review queue policy
- migration/change-risk boundaries
- ask-user triggers for risky changes

## Privacy and Sensitive Material
- Do not promote secrets, credentials, tokens, PII, or unsafe private material into `wiki/` or broad `outputs/`.
- Screen new material before promoting it downstream.
- If a raw file itself is unsafe to retain, stop and ask user before proceeding.
- Sanitize downstream summaries when needed.
- Preserve provenance without leaking sensitive details into reusable artifacts.
- Note important downstream redactions when they materially affect interpretation.

## Visibility Policy
- `private` = personal, sensitive, or not intended for sharing
- `shared` = safe for collaboration in normal project/team context
- `publishable` = sanitized and appropriate for external reuse

Rules:
- Default to `private` unless there is a clear reason to widen.
- Do not mark material `publishable` unless it is sanitized and source-safe.
- Review carefully before widening visibility from `private` to `shared`.

## Contradiction and Supersession Policy
When stronger or newer evidence changes older claims:
- preserve prior provenance
- mark claims or pages `stale`, `disputed`, or `superseded`
- use `supersedes` and `superseded_by` where helpful
- update confidence and support fields when justified
- explain reasoning briefly; do not silently flatten tension

Use these factors:
- recency
- authority or directness
- number of supporting sources
- specificity of evidence

Default resolution:
- if one side is clearly stronger, mark weaker knowledge `superseded` or `stale`
- if evidence remains mixed, keep both visible and mark it `disputed`

## Review Queue Rules
- Use one markdown note per review item in `outputs/review-queue/`.
- Queue items when human judgment is needed but safe progress can continue.
- Ask user immediately when the decision is high-stakes, irreversible, or blocks safe progress.
- Keep review items constrained and action-oriented.
- Use allowed action types from `llm-wiki-schema`.
- Include enough context, recommendation, options, and status for later review.

## Retention Governance
When evidence goes stale:
- do not delete knowledge only because it is old
- lower confidence modestly when justified
- mark `stale` or `needs_update` when warranted
- preserve provenance
- prefer repair, review, or explicit downgrade over silent decay

Meaning of retention classes lives in `llm-wiki-schema`.
This skill governs action and judgment around those classes.

## Lint-as-Migration Boundary
Prefer safe repair rules in maintenance/lint instead of one-off migrations, but apply conservatively.

Safe automatic repairs include:
- missing required frontmatter with obvious defaults
- index/catalog drift
- obvious broken internal links
- unambiguous backlinks
- explicitly documented legacy aliases
- small metadata normalization that preserves provenance

Ask user before:
- major schema migration
- taxonomy or folder changes
- bulk renames, moves, or deletes
- large merges
- changes that could remove provenance or private context

## Decision Hygiene
Ask user before:
- renaming large sets of pages
- deleting pages
- changing folder taxonomy
- changing metadata schema significantly
- merging many pages into one canonical structure
- performing bulk privacy cleanup that could remove source info
- other costly-to-undo structural decisions

## Interaction With Workflow Skills
- `llm-wiki-ingest` uses this for privacy, contradiction, review-item, and risky integration choices
- `llm-wiki-maintenance` uses this heavily
- `llm-wiki-query` and `llm-wiki-crystallize` use this when persisting disputed or sensitive material

## Minimal Example

### Review item shape, high level
A good review item should capture:
- the decision needed
- the scope/context
- recommendation
- available options
- current status
