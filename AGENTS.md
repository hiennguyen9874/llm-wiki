# LLM Wiki Contract

The single source of truth for how this repository stores knowledge. The human curates sources and questions; the agent maintains the compiled wiki. The `wiki-*` skills implement the workflows; this file is the reference they apply.

## Scope

This contract is domain-agnostic. [`SCOPE.md`](SCOPE.md) configures the instance: identity, inclusion test, exclusions, domains, domain rules, and conventions. This file is auto-loaded; read `SCOPE.md` before any retrieval or mutation.

- `SCOPE.md` only refines this contract; on conflict this contract wins and the agent reports the conflict.
- Without `SCOPE.md`, anything the human supplies or requests that yields durable knowledge is in scope.
- Domains are open. Cross-domain knowledge stays one concept, connected by links and `## Relationships`.
- One repository holds one knowledge base. An unrelated subject that needs its own privacy boundary or never shares links gets its own repository with this contract, the skills, and its own `SCOPE.md`.

**Durable** knowledge is reusable and attributable: it improves future retrieval, verification, reuse, comparison, or a decision. Transient chat, uncited claims, and generated artifacts without reuse value fail the test; length alone never passes it.

## Layout

```text
AGENTS.md              Shared base contract
SCOPE.md                 Instance scope, domains, and conventions
raw/                     Immutable source artifacts
wiki/                    OKF v0.2 knowledge bundle
  index.md               Complete retrieval map
  log.md                 Newest-first change history
  <group>/               Optional, only when a flat wiki becomes hard to scan
    index.md             Complete map for that group
    <concept>.md         One durable concept
outputs/                 Disposable or requested deliverables
tools/wiki_check.py      Structural check
```

Keep `wiki/` flat initially. Add a group only when it makes `index.md` materially easier to scan; use a plain plural name matching a domain registered in `SCOPE.md` or a broad concept family (`people/`, `projects/`, `technology/`). Paths are stable IDs: move a page only when its path is misleading.

## Wiki states

Classify the **wiki state** before retrieval or mutation:

- **Valid empty:** `wiki/index.md` and `wiki/log.md` satisfy their contracts and no concept pages exist.
- **Populated:** the reserved files are valid and their indexes reach every concept.
- **Uninitialized:** no concept pages exist and `wiki/` or either reserved file is absent.
- **Damaged:** any other structurally invalid state, especially concepts with a missing, malformed, or incomplete index or log.

The first successful ingest may atomically create the reserved files, concepts, index entries, and one `Ingest` log entry. A source that yields nothing durable, or is unsafe, unreadable, out of scope, or duplicative, leaves an uninitialized wiki unchanged unless the human explicitly requests an empty scaffold. Repair a damaged wiki through lint before ingestion.

## Ownership and privacy

- `raw/` is read-only once a source lands and is the evidentiary source of truth. Corrections arrive as new source files.
- `wiki/` is the agent-maintained synthesis and the default query surface. When it conflicts with raw evidence, preserve the evidence and correct, qualify, or mark the wiki claim disputed.
- `outputs/` holds requested artifacts, never canonical knowledge. Durable insights belong in `wiki/`.
- Git history supplies diffs and rollback; `wiki/log.md` supplies the human-readable operational history. Bulk mutations stay reviewable through Git with one log entry stating reason and scope.
- The repository, not `wiki/` alone, is the distribution unit, so `sources[].resource` links into `raw/` resolve; use `wiki/references/` only when a standalone OKF bundle is required.
- **Sensitive values** (credentials, private keys, tokens, PII, and confidential or disclosure-restricted material) are screened in every input before compilation. Wiki pages, outputs, and log entries carry only the minimum useful redacted description, with provenance still resolvable. A likely live credential or an unclear disclosure boundary pauses the mutation and alerts the human; `raw/` stays in place, and remediation or rotation is the human's call.

## Interaction mode

In `guided` mode, the agent presents an ingest synthesis and update plan before mutating the wiki. In `autonomous` mode, it proceeds and pauses only for consequential ambiguity, contradiction, privacy risk, or unclear scope. The human may pick either per operation; otherwise use the `SCOPE.md` default, or `autonomous` when none is set.

## Contract evolution

`AGENTS.md` defines shared policy, `SCOPE.md` configures the instance, and `.pi/skills/` implements workflows. Evolve them from observed retrieval misses, maintenance friction, trust failures, or explicit human preference. Changes that alter semantics, governance, or human control need human approval. After a contract change, review affected skills for drift; workflow optimization keeps knowledge meaning and provenance intact.

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

### Metadata

- `type` is required; keep a small, domain-shaped vocabulary, default `Concept`, and preserve unknown types.
- `title` and `description` are required so the index suffices for first-pass retrieval.
- `status` is `draft`, `stable`, or `deprecated` (absent means `stable` under OKF). `draft` has coverage, provenance, interpretation, or attachment work outstanding. `stable` means the intended synthesis is complete and auditable, not that its claims are verified.
- `created` never changes. `generated.at` changes only after a meaningful content change.
- `verified`, `stale_after`, source credibility, and attested-computation fields follow OKF v0.2. Set `verified` only for an actual verification event; set `stale_after` for time-sensitive APIs, compatibility, prices, or operational guidance. Omit empty metadata.
- Derived fields (`source_count`, `last_updated`, confidence scores) stay unstored.

### Body

- Put the one-paragraph synthesis first; then structured headings, concise prose, lists, and tables.
- Attribute every source-dependent claim with a keyed footnote labeled by its `sources[].id` and carrying a **locator**: the most precise available pointer into the source (section, page, equation, figure, or table; revision plus `path::symbol`; configuration key; dataset field or query; media region or timestamp; archived web heading). Record an unavailable locator as a limit.
- The **citation join** holds when every `sources[].id` is cited in the body, every body citation has a footnote definition, and every footnote matches a declared source.
- Link concepts with relative Markdown links (`[Title](concept.md)`, `[Title](../concept.md)`) so they render in Obsidian and plain Markdown, and describe the relationship in prose.
- When relationship semantics aid retrieval, add `## Relationships` bullets with a small open vocabulary (`Depends on`, `Uses`, `Owned by`, `Caused`, `Fixed by`, `Contradicts`, `Supersedes`), each supported by the source or synthesis.
- Record unresolved disagreement under `## Contradictions`: each claim with its source, neither chosen.
- Record resolved replacement under `## Supersession`: mark the old concept `deprecated` and link it to the current one with effective date and evidence; the current concept links back with `Supersedes`. Both histories remain.

### Evidence class

Label a consequential claim with its **evidence class**:

- **Reported:** asserted by a source without independent checking.
- **Observed:** confirmed by static inspection of an artifact.
- **Reproduced:** confirmed by an executed command, test, or measurement under stated conditions.
- **Synthesis:** inferred by the agent from cited evidence.
- **Unverified:** lacking a verification event, which is not the same as false.

Independent corroboration supports OKF `verified` metadata when its method and date are recorded.

### Sources and idempotency

**Source identity** is the normalized `scope` when present, else the normalized `resource`, plus `revision` when it distinguishes snapshots. `resource` is the canonical resolvable entry point; `scope` is the optional package root of a composite source; `kind` is its source class. Every concept compiled from a package cites its entry point, and a supporting file inside an existing scope reconciles against that package rather than becoming a new source.

A source's **coverage ledger** accounts for its entry point and every material include, import, attachment, and supporting artifact as inspected, executed, excluded with reason (generated, cached, duplicated, vendored, decorative, irrelevant), unreadable, or pending. Persist consequential limits in affected concepts. A large multipart collection may keep its ledger in a `type: SourceMap` concept when future idempotency needs it; small sources keep coverage with their concepts.

**Idempotency:** before ingesting, find every concept citing the source identity, its entry point, or a resource inside its scope, and reconcile against the coverage ledger. Mutate only for missing, changed, or newly connected knowledge; complete coverage is a no-op that leaves concepts, indexes, and log unchanged.

Concepts are knowledge-shaped, not source-shaped. Split a page when its parts answer independently retrievable questions, carry distinct constraints or relationships, or will be maintained from different sources. Keep an overview only when it improves navigation.

## Index contract

`wiki/index.md` is the complete catalog and primary retrieval map. Its only frontmatter is:

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

Every concept, deprecated history included, appears exactly once in its nearest index; group deprecated concepts separately when that aids scanning. A root entry for a group summarizes and links its `index.md`. Sort entries alphabetically and update them in the same change as their concepts.

## Log contract

`wiki/log.md` is immutable, newest-first history. Reuse today's date heading when present; otherwise insert one below the title. One bullet per completed state change; read-only queries log nothing.

```markdown
## 2026-01-31
- **Ingest**: Compiled [Source title](../raw/source.md); created X and updated Y.
- **Query**: Answered “question”; filed [durable result](result.md).
- **Lint**: Repaired N issues; report saved to [output](../outputs/report.md).
- **Update**: Corrected or deprecated [concept](concept.md).
```

## Mutation invariants

A wiki-changing operation is complete only when:

- the wiki state is valid empty or populated;
- every changed material claim holds its citation join with a practical locator, or is visibly labeled synthesis;
- every declared source supports body content, and local `resource` and `scope` paths resolve;
- consequential coverage limits are visible, and evidence class and `status` reflect how the knowledge was established and how complete it is;
- every affected concept, contradiction, typed relationship, and supersession edge is updated, and deprecated concepts name their replacement when one exists;
- sensitive values are absent from wiki pages, outputs, and log entries;
- links resolve where targets exist, with bidirectional context added where useful;
- each changed concept's metadata matches its nearest index entry, and `wiki/index.md` reaches every concept exactly once;
- exactly one log entry records the operation;
- the structural check passes and the semantic invariants above are confirmed. Repair or revert an incomplete mutation before reporting success.

**Structural check:** run `python3 tools/wiki_check.py`. It covers frontmatter and required metadata, `status` values, index coverage and reachability, and local Markdown links. Verify the rest directly: both reserved files, root `okf_version: "0.2"`, source paths and scopes, and the citation join.

## Scale trigger

Below roughly 100 concepts, indexes, glob, and text search suffice. Around 100–200, measure index size, query cost, and missed retrieval, and enable the project-local QMD BM25 cache when lexical ranking measurably fails. Add QMD hybrid retrieval only for observed semantic misses, and a graph engine only when Markdown relationship traversal is the bottleneck. QMD and graph indexes are caches: retrieval keeps working when they are absent or stale.
