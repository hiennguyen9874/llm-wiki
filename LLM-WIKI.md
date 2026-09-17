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
  qmd-setup/              Set up the optional project-local search cache
  qmd-retrieval/          Rank query candidates with the search cache
```

## Wiki states

Classify repository state before retrieval or mutation:

- **Valid empty:** `wiki/index.md` and `wiki/log.md` satisfy their contracts and no concept pages exist.
- **Populated:** the reserved files are valid and their indexes reach every concept.
- **Uninitialized:** no concept pages exist and `wiki/` or either reserved file is absent.
- **Damaged:** any other structurally invalid state, especially existing concepts with a missing, malformed, or incomplete index or log.

An empty candidate set is valid in an initialized wiki. The first successful ingest may atomically create the reserved files, concepts, index entries, and one `Ingest` log entry. A source that is unsafe, unreadable, out of scope, duplicative, or yields no durable knowledge leaves an uninitialized wiki unchanged unless the human explicitly requests an empty scaffold. Repair a damaged wiki through lint before ingestion.

Keep `wiki/` flat initially. Add a group only when it makes `index.md` materially easier to scan; use plain, plural domain names such as `people/`, `concepts/`, or `projects/`. Paths are stable IDs, so prefer moving a page only when its current path is misleading.

## Ownership

- `raw/` is read-only after a source lands and is the evidentiary source of truth. Corrections arrive as new source files.
- `wiki/` is the persistent, agent-maintained operational synthesis and the default query surface. When wiki content conflicts with raw evidence, preserve the evidence and correct, qualify, or mark the wiki claim as disputed.
- `outputs/` holds requested artifacts, not canonical knowledge. Durable insights belong in `wiki/`.
- Git history supplies diffs and rollback; `wiki/log.md` supplies a human-readable operational history.
- The repository—not `wiki/` alone—is the distribution unit. This keeps `sources[].resource` links into `raw/` resolvable; use `wiki/references/` only when a standalone OKF bundle is required.

## Interaction mode

In `guided` mode, the agent presents an ingest synthesis and update plan before mutating the wiki. In `autonomous` mode, it proceeds without routine approval and pauses only for consequential ambiguity, contradiction, privacy risk, or unclear scope. The human may select either mode per operation; when no preference is given, use `autonomous`.

## Contract evolution

`LLM-WIKI.md` defines policy; `.pi/skills/` implements its workflows. Evolve both from observed retrieval misses, maintenance friction, trust failures, or explicit human preference rather than speculative complexity. Contract changes that alter semantics, governance, or human control require human approval. After changing the contract, review affected skills for drift; workflow optimization must not silently change knowledge meaning or provenance.

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
    resource: ../raw/source-package/README.md
    scope: ../raw/source-package/
    kind: code
    revision: immutable-revision-if-known
    title: Source title
---
```

Rules:

- `type` is required. Use a small, domain-shaped vocabulary; default to `Concept`. Preserve unknown types.
- `title` and `description` are required locally because they make the index sufficient for first-pass retrieval.
- `status` is `draft`, `stable`, or `deprecated`; an absent value means `stable` under OKF. `draft` has material coverage, provenance, interpretation, or attachment work outstanding. `stable` means intended synthesis coverage is complete and auditable, not that source claims are true or independently verified.
- `created` never changes. `generated.at` changes only after a meaningful content change.
- `verified`, `stale_after`, source credibility signals, and attested-computation fields follow OKF v0.2 when applicable. Use `verified` only for an actual verification event, and use `stale_after` for time-sensitive APIs, compatibility, prices, or operational guidance. Omit empty metadata.
- `source_count`, `last_updated`, and confidence scores are derived or duplicative and aren't stored.
- Write structured headings, concise prose, lists, and tables. Put the one-paragraph synthesis first.
- Attribute source-dependent claims with keyed footnotes whose labels match `sources[].id`. Put the best available locator in the footnote or adjacent prose: document section, page, equation, figure, or table; immutable revision plus code path and symbol; configuration key; dataset field or query; media region or timestamp; or archived web heading.
- Link concepts with standard Markdown relative links such as `[Title](concept.md)` or `[Title](../concept.md)` so they work in both Obsidian and ordinary Markdown renderers. Describe the relationship in prose.
- When relationship semantics aid retrieval, use `## Relationships` bullets labeled with a small open vocabulary such as `Depends on`, `Uses`, `Owned by`, `Caused`, `Fixed by`, `Contradicts`, or `Supersedes`. Add a label only when the source or synthesis supports it.
- Represent unresolved disagreement under `## Contradictions`; state each claim and its source without silently choosing one.
- Represent resolved replacement under `## Supersession`. Mark the old concept `deprecated`, link it to the current concept with the effective date and evidence, and link the current concept back with `Supersedes`. Preserve both histories.

Reserved `index.md` and `log.md` files follow their contracts below and aren't concepts.

### Source identity and coverage

`resource` is the canonical resolvable entry point. For a composite source, `scope` is its optional logical package root, `kind` is its optional source class, and `revision` is its immutable version when known. Source identity is the normalized `scope` when present and otherwise the normalized `resource`; a revision distinguishes snapshots where applicable. Every concept compiled from the package cites its canonical entry point. Requests naming a supporting file inside an existing scope reconcile against that package before becoming a new source.

Inventory a logical source's entry point, material includes, imports, attachments, and supporting artifacts. Distinguish inspected material; executed checks; generated, cached, duplicated, vendored, decorative, or irrelevant exclusions; unreadable or unavailable material; and pending review. Persist consequential limits in affected concepts. For a large multipart collection, a `type: SourceMap` concept may hold the package-level ledger when that record is needed for future idempotency; small sources keep coverage with their concepts.

Concepts are knowledge-shaped rather than source-shaped. Split a page when its major parts answer independently retrievable questions, have distinct constraints or relationships, or will be maintained from different future sources. Keep an overview only when it improves navigation.

### Evidence terminology

Use these labels in prose when the distinction is consequential:

- **Reported:** asserted by a source without independent checking.
- **Observed:** confirmed by static inspection of an artifact.
- **Reproduced:** confirmed by an executed command, test, or measurement under stated conditions.
- **Synthesis:** inferred from cited evidence by the agent.
- **Unverified:** lacking a verification event; this does not mean false.

Independent corroboration may support OKF `verified` metadata when its method and date are recorded.

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

Every concept, including deprecated history, appears exactly once in its nearest index; group deprecated concepts separately when that improves scanning. A root entry for a subdirectory summarizes and links its `index.md`. Sort entries alphabetically for stable diffs. Update affected index entries in the same change as concepts.

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

1. Classify the wiki state. For an uninitialized or valid empty wiki, report that no compiled knowledge exists. For a damaged wiki, independently enumerate concept files, disclose the integrity limit, and route repair through lint.
2. Read `wiki/index.md`; follow relevant group indexes and concept descriptions. Select candidates by title, description, type, tags, named relationships, and source coverage when completeness is part of the question. Use glob for structural scope and exact text search when the index isn't enough.
3. When exact retrieval produces too many candidates or misses the user's vocabulary, use the optional project-local QMD cache. Use BM25 `search` for lexical ranking and escalate to hybrid `query` only for an observed semantic miss or a clearly semantic, ambiguous, or cross-concept question. Union QMD results with catalog and exact matches; QMD absence, stale state, or low scores never remove explicit candidates or block retrieval.
4. Read the selected concepts and traverse relationship types that match the question: dependencies for impact, causes and fixes for diagnosis, supersession and contradiction for freshness, and ownership for responsibility. Respect recorded source and attachment coverage.
5. Check `status`, `stale_after`, `verified`, evidence class, contradictions, locators, and cited sources. Treat missing verification as unverified, not false; treat broken or coarse provenance as a retrieval limitation.
6. Answer with links to concept pages and distinguish documented knowledge, synthesis, uncertainty or dispute, insufficient evidence, and missing knowledge. Absence means "not compiled or not retrieved," not "false."
7. Consult `raw/` only to verify a disputed citation, fill a provenance gap, or when the user explicitly requests source-level research. Ordinary absence never silently expands into a raw-source search.
8. File an answer only when it adds reusable synthesis; transient answers stay in chat or `outputs/`.

## Crystallization

File a query result as `type: Synthesis` when it creates reusable multi-concept synthesis, a durable comparison, a decision or lesson, a newly supported relationship, a contradiction resolution, or a verified procedure. Cite the underlying concepts or raw sources through `sources`; transient chat isn't provenance. Integrate extracted insights into affected concepts rather than leaving the synthesis as an isolated report.

## Privacy and governance

Screen every input before compilation for credentials, private keys, tokens, PII, and private or confidential material. Store the minimum useful redacted knowledge in `wiki/`, keep provenance resolvable, and exclude sensitive values from wiki pages, outputs, and log entries. Pause the mutation and alert the human when a likely live credential or an unclear disclosure boundary is found. Preserve `raw/` in place; remediation or credential rotation is a human-governed operation. Keep bulk mutations reviewable through Git and summarize their reason and scope in one log entry.

## Idempotency

Identify a source by normalized `sources[].scope` when present and otherwise by normalized `sources[].resource`; include `revision` when it distinguishes snapshots. Before ingesting, find every concept citing the identity, canonical entry point, or a supporting resource within its scope, then reconcile the coverage ledger. Mutate only for missing, changed, or newly connected knowledge. Complete coverage produces a no-op with concept metadata, indexes, and log unchanged. Corrections use a new immutable artifact or revision.

## Mutation invariants

A wiki-changing operation is complete only when:

- the wiki is valid empty or populated, never damaged;
- every changed material claim has a matching source ID and footnote definition or is visibly labeled synthesis;
- every declared source supports body content, and local `resource` and `scope` paths resolve;
- material provenance uses a practical locator where available and consequential coverage limits are visible;
- evidence labels and concept status reflect how the knowledge was established and how complete the synthesis is;
- every affected concept, contradiction, typed relationship, and supersession edge is updated;
- deprecated concepts identify their current replacement when one exists;
- sensitive values are absent from wiki pages, outputs, and log entries;
- links resolve where targets exist, and bidirectional context is added when useful rather than mechanically;
- each changed concept's metadata and nearest index entry agree;
- `wiki/index.md` reaches every concept exactly once through indexes;
- exactly one operation entry records the completed mutation in `wiki/log.md`;
- structural and semantic validation pass. Repair or revert an incomplete mutation before reporting success.

## Structural check

Run `python3 tools/wiki_check.py` after wiki mutations and during lint when command execution is available. Structural validation requires both reserved files, root `okf_version: "0.2"`, parseable required metadata, valid lifecycle values, complete and unique index coverage, resolvable local Markdown links and source paths/scopes, and agreement among `sources[].id`, body citations, and footnote definitions. Until the checker implements every requirement, verify the remaining joins and root-state rules directly. Semantic evidence classes, source coverage, concept cohesion, maturity, contradiction, and privacy checks remain agent work.

## Scale trigger

Use indexes, glob, and ordinary text search below roughly 100 concepts. Around 100–200 concepts, measure index size, query cost, and missed retrieval; enable the project-local QMD BM25 cache when those measurements show lexical ranking failures. Use QMD hybrid/vector retrieval only for observed semantic misses, and add a graph engine only when Markdown relationship traversal is the bottleneck. Thresholds trigger evaluation, not automatic infrastructure. Generated QMD and graph indexes are caches, never sources of truth; retrieval must continue to work when they are absent or stale.
