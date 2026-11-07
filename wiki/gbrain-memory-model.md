---
type: Concept
title: GBrain memory model
description: The remember/recall/forget verb protocol and how facts, takes, beliefs, pages and core memory differ, including corrections, withdrawal and the compiled-truth plus timeline convention.
tags: [agent-memory, gbrain, facts, takes, memory-verbs]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: verbs-doc
    resource: ../raw/gbrain/docs/protocol/MEMORY_VERBS_v1.md
    kind: code
    revision: 27f8b9d
    title: Memory verbs protocol v1
  - id: verbs-ts
    resource: ../raw/gbrain/src/core/verbs.ts
    kind: code
    revision: 27f8b9d
    title: Frozen memory verbs
  - id: takes-vs-facts
    resource: ../raw/gbrain/docs/takes-vs-facts.md
    kind: code
    revision: 27f8b9d
    title: Takes vs facts
  - id: fence-format
    resource: ../raw/gbrain/docs/guides/fence-format.md
    kind: code
    revision: 27f8b9d
    title: Fence format guide
  - id: compiled-truth
    resource: ../raw/gbrain/docs/guides/compiled-truth.md
    kind: code
    revision: 27f8b9d
    title: Compiled truth guide
  - id: core-memory-ts
    resource: ../raw/gbrain/src/core/core-memory.ts
    kind: code
    revision: 27f8b9d
    title: Core memory
  - id: withdrawal-ts
    resource: ../raw/gbrain/src/core/facts/withdrawal.ts
    kind: code
    revision: 27f8b9d
    title: Fact withdrawal
  - id: facts-migration
    resource: ../raw/gbrain/src/core/schema-migrations/v045-facts-hot-memory-v0-31.ts
    kind: code
    revision: 27f8b9d
    title: Facts migration v045
  - id: takes-migration
    resource: ../raw/gbrain/src/core/schema-migrations/v037-takes-and-synthesis-evidence.ts
    kind: code
    revision: 27f8b9d
    title: Takes migration v037
---

GBrain exposes memory to agents through a frozen wire protocol of seven verbs — `recall`, `remember`, `entity`, `synthesize`, `forget` plus the additive `context_pack` and `delta` — and stores what they write as **facts** (hot, owner-scoped claims), **takes** (cold, "who believes what" with weight) and Markdown **pages** (compiled truth plus timeline). Provenance is mandatory on every fact, and corrections use supersession or withdrawal rather than silent overwrite. This page covers semantics; trust and egress are in [memory trust and egress](gbrain-memory-trust-and-egress.md), and the page layout is in the [data model](gbrain-data-model-and-system-of-record.md). The README frames the whole system as "explicit facts with their sources, supports corrections and withdrawal".[^readme]

## The verbs

| Verb | Semantics | Evidence |
| --- | --- | --- |
| `remember` | Write one fact. `provenance` required (≤ 500 chars, stored verbatim); `kind` frozen to `event|preference|commitment|belief|fact`; `visibility` defaults `world`; batch ≤ 20 items. Response `status` is `inserted|duplicate|superseded`; a duplicate returns the existing id; `fact_id` is opaque. | Reported (`MEMORY_VERBS_v1.md`); frozen set Observed in `verbs.ts` |
| `recall` | Read. `entity` scopes facts; `question` ranks active facts by cosine plus a whole-word bonus; `query` runs the page hybrid arm; token-budget policies `facts_first`/`query_first`; `limit` 50 default, 100 cap. Remote callers see `world` facts only. | Reported |
| `forget` | Expire by fact id (idempotent); audit trail kept. | Reported |
| `context_pack`, `delta` | Session-start pack and "what changed since I last woke"; world-only, cursor-deduped. | Reported |
| `entity`, `synthesize` | Zero-LLM entity card; expensive cited cross-page answer with gap analysis. | Reported |

Adjacent operations: `gbrain think` ([knowledge graph](gbrain-knowledge-graph.md)), `find_experts` (CLI `whoknows`), `find_contradictions`, `find_trajectory`, `volunteer_context`. `gbrain beliefs` is the belief-ledger audit subsystem, not epistemology.[^verbs-doc][^verbs-ts]

## Facts, takes, beliefs, pages, core memory

- **Facts (hot):** `facts` table; kinds `event|preference|commitment|belief|fact|idea` — the DB and extractor carry `idea` while the `remember` enum stays at five. Columns include `entity_slug`, `visibility`, `notability`, `valid_from/until`, `expired_at`, `superseded_by`, `consolidated_at/into`, `source`, `confidence`. Entity facts are also written as rows of the page's `## Facts` fence; unattributed facts live on `memory/unattributed`.[^facts-migration][^fence-format][^takes-vs-facts]
- **Takes (cold):** `takes` table — `kind` fact|take|bet|hunch, `holder` (`world|brain|people/<slug>|companies/<slug>`), `weight` 0–1 on a 0.05 grid, dates, `superseded_by`, resolution fields (`correct|incorrect|partial|unresolvable`). Hot facts reach cold takes only through the dream `consolidate` phase; "never dump one into the other" (Reported).[^takes-migration][^takes-vs-facts]
- **Beliefs:** in the user-facing sense, `kind=belief` facts or `holder=brain` takes; the separate belief ledger (`belief_events`) is DB-only audit state.[^takes-vs-facts]
- **Core memory:** pages with `always_load: true` (and `core_priority`) rendered as title plus compiled truth only, never timeline, zero-LLM and remote-safe. Opt-in (`memory.core.enabled` false by default), brain-wide budget 4,000 chars (500–6,000) over at most 50 pages; marking is owner-only.[^core-memory-ts]

## Corrections and withdrawal (no single "correct" verb)

- `remember --replaces <fact_id>`: caller-directed supersession with zero model calls; refused for withdrawn, superseded, expired, cross-entity, cross-page or cross-visibility targets (Reported).
- `takes supersede|update|resolve|remove`; `put_page` rewrite with a `reason` (recorded as `replaced_because` and a `gbrain-reason:` git trailer); `gbrain trust confirm|revert`; accepting a `decide` proposal is the only automated supersede write.
- Withdrawal strikes the fence row and expires the DB row; re-remembering a withdrawn claim is refused with `fact_withdrawn` ("remember it in new words"). Purge removes text, unlike expire. `forget` while the source writer is unavailable is accepted-but-pending and the fact is still recalled meanwhile.[^verbs-doc][^withdrawal-ts]

## Compiled truth and timeline

Each page has a rewritten compiled-truth zone and an append-only timeline, split at the first sentinel in precedence `<!-- timeline -->` > `--- timeline ---` > bare `---` followed by `## Timeline`/`## History`. Timeline rows live in the DB and are materialized back with a `<!-- gbrain:materialized v1 <hash> -->` marker. Hazards (Reported): dated citations *above* the sentinel mint timeline rows, and there is no timeline-remove command. The guide's pseudocode (`gbrain timeline-add`, `put … { compiled_truth: … }`) does not match the live `put_page` signature, which takes a full `content` string (Observed by subagent).[^compiled-truth]

## Defaults worth remembering (Reported)

`question` ≤ 2,000 chars; TTL shorthand `30d` (ISO `P30D` rejected); no embedder → keyword-only with `facts_degraded.reason` rather than an error; core over budget → `core_budget_exceeded` (shrinking writes always pass).[^verbs-doc][^core-memory-ts]

## Relationships

- Depends on: [data model](gbrain-data-model-and-system-of-record.md).
- Feeds: [memory trust and egress](gbrain-memory-trust-and-egress.md), [dream cycle](gbrain-dream-cycle-and-autopilot.md) (`consolidate`, `extract_facts`).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` intro paragraph.
[^verbs-doc]: `docs/protocol/MEMORY_VERBS_v1.md` lines 1–8, 118–226 (recall), 227–330 (remember), 340–380 (`--replaces`); `docs/mcp/TOOL_REFERENCE.md` lines 131–139, 351–391.
[^verbs-ts]: `src/core/verbs.ts` lines 44 (`VERB_NAMES`), 55–70 (kinds).
[^takes-vs-facts]: `docs/takes-vs-facts.md`.
[^fence-format]: `docs/guides/fence-format.md` "Facts columns", "Holders".
[^compiled-truth]: `docs/guides/compiled-truth.md` §4–§5; `src/core/markdown.ts:851,938,1034`; `src/core/timeline-marker.ts:1-14` (via subagent).
[^core-memory-ts]: `src/core/core-memory.ts` lines 1–15, 52–64; `docs/guides/core-memory.md`.
[^withdrawal-ts]: `src/core/facts/withdrawal.ts` lines 25–30.
[^facts-migration]: `src/core/schema-migrations/v045-facts-hot-memory-v0-31.ts` lines 113–140.
[^takes-migration]: `src/core/schema-migrations/v037-takes-and-synthesis-evidence.ts` lines 25–50.
