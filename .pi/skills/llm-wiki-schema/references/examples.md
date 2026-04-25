# LLM Wiki Schema Examples

Longer examples for `llm-wiki-schema`.
Keep `SKILL.md` short; put expanded patterns here.

## Example 1: Topic page frontmatter

```yaml
---
title: Example Topic
created: 2026-04-25
last_updated: 2026-04-25
source_count: 2
status: reviewed
page_type: topic
aliases: []
tags: []
domain: general
importance: medium
review_status: active
related_sources:
  - [[source-example-a]]
  - [[source-example-b]]
confidence_score: 0.78
quality_score: 0.82
evidence_count: 2
first_seen: 2026-04-20
last_confirmed: 2026-04-25
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - [[related-entity]]
---
```

## Example 2: Source page frontmatter

```yaml
---
title: Source Example
created: 2026-04-25
last_updated: 2026-04-25
source_count: 1
status: draft
page_type: source
aliases: []
tags: []
domain: general
importance: medium
review_status: active
related_sources: []
confidence_score: 0.70
quality_score: 0.75
evidence_count: 1
first_seen: 2026-04-25
last_confirmed: 2026-04-25
claim_status: active
retention_class: working
visibility: private
supersedes: []
superseded_by: []
related_entities: []
source_file: raw/articles/example.md
source_type: article
canonical_url: https://example.com/article
author: Example Author
published: 2026-04-20
---
```

## Example 3: Claim block

```md
## Evidence / claims

#### Claim
- Statement: Example Topic reduces onboarding time for repeated tasks.
- Status: active
- Confidence: 0.78
- Evidence: [[source-example-a]], [[source-example-b]]
- Last confirmed: 2026-04-25
- Notes: Supported by two independent observations; likely to change if workflow changes materially.
- Supersedes: []
```

## Example 4: Topic page shape

```md
## Summary
Short synthesis of what the page is about and why it matters.

## Key points
- Point one
- Point two

## Relationships
- Related to [[related-entity]]
- Supports [[other-topic]]

## Evidence / claims
(Claim blocks here when needed)

## Open questions
- What is still uncertain?

## Related pages
- [[other-topic]]
- [[source-example-a]]

## Sources
- [[source-example-a]]
- [[source-example-b]]
```
