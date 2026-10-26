---
type: Concept
title: WeKnora automatic wiki compilation and revisions
description: Durable ingest/finalize lanes, concurrent page convergence, citation extraction, link graphs, and revision-preserving rewrite guards.
tags: [ml, weknora, wiki]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a258
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora's automatic wiki is a durable, asynchronous document-to-page workflow with separate local page updates and knowledge-base-wide convergence. **Observed:** ingest/finalize lanes, identity and slug coordination, versioned page writes, and table-row loss guards address different failure modes. This product's generated wiki is separate from the Markdown knowledge base in which this concept is stored.[^weknora]

## Ingest and global convergence

**Observed defaults and declared coordination mechanisms** in `service/wiki_ingest.go`:[^weknora]

| Mechanism | Purpose/default |
| --- | --- |
| `wiki:ingest` / `wiki:finalize` | Separate durable pending-operation lanes; dead letters retain failed work |
| Batch size / document retries | 5 documents; 5 failed-operation retries before dead-letter archival |
| Debounce / follow-up | 30 seconds initially; 5 seconds follow-up; 60 seconds after rate limiting |
| Concurrent standard mode | Disjoint row claims plus per-slug reduce locks; Lite serializes by KB |
| Claim expiry | 90 minutes, deliberately longer than the stated 60-minute ingest task timeout |
| Identity claim | 2-hour reservation to converge different proposed slugs for the same normalized identity |
| Per-KB in-flight cap | Default 4, leaving room in the default 8-worker wiki pool |
| Finalize | 20-second debounce; drains up to 5,000 rows then reschedules |

Finalize coalesces index-intro rebuilding, stale-link cleanup, cross-link injection, and folder-prune work. Folder deletion is deferred because taxonomy may create folders before parallel reducers materialize pages. **Synthesis:** separating local reduction from global convergence avoids rebuilding the entire KB index at the tail of every small batch.[^weknora]

Selected extraction code shows skeleton candidates followed by chunk-grounded citation batches (12,000 runes, concurrency 4), batch taxonomy planning, and a trigram/Jaccard candidate prefilter before LLM deduplication. LLM generation defaults include a 32,768-token completion budget and three attempts; page-body continuation is distinct from JSON parse recovery. These are static mechanisms, not measured wiki quality or throughput.[^weknora]

## Revision and rewrite safety

**Observed implementation:** `wikiPageService.UpdatePage` bumps versions for user-visible changes (including aliases) but persists metadata-only changes without a version bump. `repository/wiki_page.go::UpdateWithRevision` snapshots the superseded page and updates the versioned row in one transaction; optimistic conflicts are explicit errors.[^weknora]

A machine whole-page rewrite can be refused if table-row identities disappear. Agent rewrites tolerate no identity loss; ingest refuses loss **strictly greater than 20%**. Human edits, reverts, and explicitly permitted shrink operations are exempt. This is an identity heuristic, not proof that all columns or prose survive. Retention constants keep 50 recent revisions with a hard cap of 200, while only pipeline-authored snapshots are ordinarily prunable, protecting human/agent/revert history from routine pipeline churn.[^weknora]

## Wiki graph versus GraphRAG

**Observed:** wiki graph views subset page/link relationships by degree or ego traversal. Link injection avoids existing links, images, code, and unsuitable one-character Han matches. Lint issue types include orphans, broken links, stale references, missing cross-references, empty content, and duplicate slugs. These are wiki-page relationships, **not** the separately indexed document entity graph used by [GraphRAG](weknora-graph-multimodal-retrieval.md).[^weknora]

## Relationships

- Uses [worker pools](weknora-task-queues.md) and [domain persistence](weknora-persistence.md).
- Produces a different retrieval surface from [chunk-based hybrid search](weknora-hybrid-retrieval.md).
- The [agent](weknora-agent-runtime.md) can operate on wiki pages through tools; full tool-write paths remain pending.

## Coverage limits

Queue constants, selected orchestration/extraction sections, page updates, repository transactions, linkification sections, and test names were inspected. Full map/reduce, cancellation, link-maintenance atomicity, taxonomy quality, frontend graph grouping, and revision tests were not executed or exhaustively reviewed. No “40k documents” scale claim was reproduced. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a258`: `internal/application/service/wiki_ingest.go` constants and lane/coordination comments; `wiki_ingest_batch.go::ProcessWikiIngest`; `wiki_ingest_cite.go::maxRunesPerCitationBatch`, `maxCitationBatchConcurrency`, `extractCandidateSlugs`; `wiki_ingest_taxonomy.go::planBatchTaxonomy`, `resolvePlannedFolders`; `wiki_ingest_dedup.go::selectDedupCandidatePages`; `wiki_page.go::UpdatePage`, `pruneRevisions`, `RevertPageToVersion`, `GetGraph`, `computeGraphSubset`; `wiki_write_row_guard.go::wikiWriteIngestRowIdentityLossLimit`, `ErrWikiWriteDroppedTableRows`; `wiki_linkify.go::linkifyContent`; `wiki_lint.go` issue/report declarations; `internal/application/repository/wiki_page.go::UpdateWithRevision`, `updateWikiPageRow`; `internal/types/wiki_page.go::WikiMaxRevisionsPerPage`, `WikiMaxRevisionsHardCap`, `WikiPrunableEditSources`. Package entry: [README](../raw/WeKnora/README.md), “Automatic wiki.”
