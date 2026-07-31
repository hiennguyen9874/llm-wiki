# LLM Wiki Contract

This file is the single source of truth for storing and retrieving this repository's knowledge. The human curates sources and questions; the agent maintains the compiled wiki.

## Scope

- **Identity:** A personal knowledge base about LLM-assisted knowledge systems.
- **Focus:** knowledge storage and retrieval; agent skills and workflows; portable knowledge formats, provenance, and trust.
- **Exclusions:** transient chat, uncited claims, and generated artifacts without durable reuse value.

Revise this scope when the human changes the knowledge base's domain.

## Layout

```text
raw/                     Immutable source artifacts
wiki/                    OKF v0.2 knowledge bundle
  index.md               Complete retrieval map
  log.md                 Newest-first change history
  <group>/               Optional only when a flat wiki becomes hard to scan
    index.md              Complete map for that group
    <concept>.md          One durable concept
outputs/                 Disposable or requested query deliverables
.pi/skills/
  wiki-ingest/            Compile sources into the wiki
  wiki-query/             Retrieve and synthesize knowledge
  wiki-lint/              Audit and repair wiki health
```

Keep `wiki/` flat initially. Add a group only when it makes `index.md` materially easier to scan; use plain, plural domain names such as `people/`, `concepts/`, or `projects/`. Paths are stable IDs, so prefer moving a page only when its current path is misleading.

## Ownership

- `raw/` is read-only after a source lands. Corrections arrive as new source files.
- `wiki/` is the persistent, agent-maintained synthesis and the default query surface.
- `outputs/` holds requested artifacts, not canonical knowledge. Durable insights belong in `wiki/`.
- Git history supplies diffs and rollback; `wiki/log.md` supplies a human-readable operational history.
- The repository—not `wiki/` alone—is the distribution unit. This keeps `sources[].resource` links into `raw/` resolvable; use `wiki/references/` only when a standalone OKF bundle is required.

## Concept contract

Every non-reserved Markdown file under `wiki/` is one concept and starts with parseable YAML:

```yaml
---
type: Concept
title: Human-readable title
description: One sentence suitable for an index entry.
tags: [optional, lowercase-tags]
status: stable
created: 2026-01-31
generated: { by: llm-wiki-agent/1, at: 2026-01-31T12:00:00Z }
sources:
  - id: stable-source-key
    resource: ../raw/source-file.md
    title: Source title
---
```

Rules:

- `type` is required. Use a small, domain-shaped vocabulary; default to `Concept`. Preserve unknown types.
- `title` and `description` are required locally because they make the index sufficient for first-pass retrieval.
- `status` is `draft`, `stable`, or `deprecated`; an absent value means `stable` under OKF.
- `created` never changes. `generated.at` changes only after a meaningful content change.
- `verified`, `stale_after`, source credibility signals, and attested-computation fields follow OKF v0.2 when applicable. Omit empty metadata.
- `source_count`, `last_updated`, and confidence scores are derived or duplicative and aren't stored.
- Write structured headings, concise prose, lists, and tables. Put the one-paragraph synthesis first.
- Attribute source-dependent claims with keyed footnotes whose labels match `sources[].id`.
- Link concepts with standard Markdown relative links such as `[Title](concept.md)` or `[Title](../concept.md)` so they work in both Obsidian and ordinary Markdown renderers. Describe the relationship in prose.
- Represent disagreement in context under `## Contradictions`; state each claim and its source without silently choosing one. Resolve it only when evidence supports the resolution.

Reserved `index.md` and `log.md` files follow their contracts below and aren't concepts.

## Index contract

`wiki/index.md` is the complete catalog and primary retrieval map. It may contain only `okf_version` frontmatter:

```yaml
---
okf_version: "0.2"
---
```

Group entries by useful domain or concept type:

```markdown
## Concepts
- [Concept title](concept-title.md) — Exact frontmatter description.
```

Every live concept appears exactly once in its nearest index. A root entry for a subdirectory summarizes and links its `index.md`. Sort entries alphabetically for stable diffs. Update affected index entries in the same change as concepts.

## Log contract

`wiki/log.md` is immutable history arranged newest first. Reuse today's date heading when present; otherwise insert one below the title. Use one bullet per operation:

```markdown
## 2026-01-31
- **Ingest**: Compiled [Source title](../raw/source.md); created X and updated Y.
- **Query**: Answered “question”; filed [durable result](result.md).
- **Lint**: Repaired N issues; report saved to [output](../outputs/report.md).
- **Update**: Corrected or deprecated [concept](concept.md).
```

Log only completed state changes. Read-only queries need no entry.

## Retrieval policy

1. Read `wiki/index.md`; follow relevant group indexes and concept descriptions.
2. Select candidates by title, description, type, tags, and named relationships. Use text search when the index isn't enough.
3. Read the selected concepts and follow only links needed to answer the question.
4. Check `status`, `stale_after`, `verified`, contradictions, and cited sources. Treat missing verification as unverified, not false.
5. Answer from the wiki with links to concept pages and distinguish documented facts, synthesis, uncertainty, and missing knowledge.
6. Consult `raw/` only to verify a disputed citation, fill a provenance gap, or when the user explicitly requests source-level research.
7. File an answer only when it adds reusable synthesis; transient answers stay in chat or `outputs/`.

## Idempotency

A source is identified by its normalized `sources[].resource` path because files in `raw/` are immutable. Before ingesting, find every concept already citing that resource. Reconcile the source against those concepts and create a mutation only for missing, changed, or newly connected knowledge. If coverage is complete, report a no-op and leave concept metadata, indexes, and log unchanged. Corrections use a new raw file and therefore a new source identity.

## Mutation invariants

A wiki-changing operation is complete only when:

- every changed claim has provenance or is explicitly labeled synthesis;
- every affected concept and contradiction is updated;
- links resolve where targets exist, and bidirectional context is added when useful rather than mechanically;
- each changed concept's metadata and nearest index entry agree;
- `wiki/index.md` still reaches every live concept through indexes;
- exactly one operation entry records the completed mutation in `wiki/log.md`.

## Structural check

Run `python3 tools/wiki_check.py` after wiki mutations and during lint when command execution is available. It enumerates concepts independently of the indexes and checks required metadata, lifecycle values, index coverage, duplicate index entries, and local Markdown link targets. Semantic provenance and contradiction checks remain agent work.

## Scale trigger

Use indexes and ordinary text search first. Add a local lexical/vector search tool only after measured retrieval failures caused by corpus size; generated search indexes are caches, never sources of truth.
