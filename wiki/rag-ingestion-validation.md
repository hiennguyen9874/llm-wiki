---
type: Concept
title: RAG ingestion validation and version currency
description: Post-conversion integrity checks, worst-document regression sets, and the stale-version ambiguity that hash deduplication cannot resolve.
tags: [rag, ingestion, evaluation, deduplication]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:29:20Z }
stale_after: 2027-10-26
sources:
  - id: rag-hardest-part
    resource: ../raw/the-hardest-part-of-building-a-rag-knowledge-base/index.md
    scope: ../raw/the-hardest-part-of-building-a-rag-knowledge-base/
    kind: article
    title: "The hardest part of building a RAG knowledge base happens before embeddings (r/Rag discussion)"
---

# RAG ingestion validation and version currency

**Reported:** cleaning before conversion is not sufficient, because a structurally broken extraction can look perfectly clean afterwards; and deduplication by hash cannot establish which of several near-identical documents is current. Commenters on the source post describe both gaps as checks that belong inside the [pre-embedding preparation pipeline](rag-data-preparation.md), not in a later retriever-tuning loop.[^rag-hardest-part]

## Post-conversion integrity checks

The proposed check runs on the converted output, after cleaning, and asks three questions per record:

1. Do table totals still reconcile?
2. Does every value still sit under its own column header?
3. Does every extracted number appear on the source page?

The motivation is that cleaning removes formatting noise without detecting lost structure: a table whose column headers were dropped during extraction reads as clean text, is embedded, and is then cited confidently for the wrong meaning. The second commenter supplies the concrete failure — a PDF table continuing onto a second page whose headers disappear during extraction — and states the resulting principle: a citation to badly extracted data is still a wrong answer. Citation machinery therefore does not repair conversion errors, and provenance alone does not detect them.[^rag-hardest-part]

## Worst-document regression set

The same commenter recommends keeping a small set of the ugliest documents — scans, merged headers, tables spanning pages — and re-running that set whenever any stage changes. The purpose is diagnostic rather than statistical: after a stage edit, the set shows whether a defect was fixed or merely moved to a different artifact. This is the cheapest available guard for iterative cleaning work, and it composes with the source post's advice to checkpoint every stage so intermediate output stays inspectable.[^rag-hardest-part]

## Version currency before deduplication

A third gap sits upstream of the stage-8 deduplication step. Shared drives accumulate near-identical revisions (`v2_final`, `v3_final_really`), and because they differ by only a few lines, hash-based deduplication keeps all of them. Both the current and the superseded policy are then embedded, retrieved, and answered with the same apparent confidence. **Synthesis:** the failure is not duplicate storage but unresolved supersession — deduplication answers "are these bytes the same material" while the corpus needs "which artifact is authoritative now", a judgement that requires version metadata, ownership, or document lineage rather than similarity.[^rag-hardest-part]

This is the same problem the curated repository solves by treating `raw/` as immutable evidence and recording supersession explicitly; platform-level analogues appear in [LightRAG document ingestion](lightrag-ingestion.md) (document identity and deduplication), [RAGFlow connectors and incremental synchronization](ragflow-connectors.md) (fingerprint skips), and [WeKnora external datasource synchronization](weknora-datasource-sync.md) (resumable checkpoints).

## Retrieval-side claims worth testing

Two further comments concern validating retrieval rather than conversion, and are recorded because they constrain how any pipeline change should be judged:

- **Same-time comparison.** Search results are temporal, so a side-by-side A/B at the same moment is recommended instead of before/after runs at different times.
- **Search mode for heterogeneous corpora.** k-Nearest-Neighbor search is easy to stand up but described as the wrong mode for complex, heterogeneous corpora; adaptive search with more parameters is claimed to be generally more appropriate, with scores needing rescaling because raw scores say little, and `k+n` candidates able to surface lexical matches missing from the top `k`.

Both are single-person reports with no protocol, sample, or measurement; neither is corroborated inside this wiki.[^rag-hardest-part]

## What the discussion leaves unsettled

- No acceptance criteria: nothing states how much table drift, header loss, or numeric mismatch is tolerable, or who signs off.
- No automation: whether the three integrity checks can be measured at scale, or must stay a sampled manual review, is left open.
- No evidence: no measurement shows that these checks improve answer quality, only that their absence hides defects.
- No mechanism for currency: the discussion names current-version determination as a problem without proposing metadata, ownership, or lineage rules.
- No treatment of non-document sources: the same questions for database rows, images, and chart descriptions are unaddressed.

## Relationships

- **Depends on:** [RAG data preparation before embedding](rag-data-preparation.md), specifically stages 3 and 8 where cleaning and deduplication decisions are made.
- **Contradicts:** the top-k counter-claim recorded on that page, which treats data quality as a limited factor for retrieval quality.
- **Related to:** platform-specific deduplication and sync behavior in [LightRAG ingestion](lightrag-ingestion.md), [RAGFlow connectors](ragflow-connectors.md), and [WeKnora datasource synchronization](weknora-datasource-sync.md).

## Evidence and limits

Every claim is **Reported** from comments under a mutable social-media post captured 2026-10-26, with no pinned revision. Some commenters disclose commercial interest in document-conversion products; their product recommendations are excluded as promotion while their technical observations are retained as unverified reports. Nothing here was reproduced: no conversion run, no table-integrity check, and no retrieval comparison was executed. The claim that a "citation to badly extracted data is still a wrong answer" is recorded as a community assertion, not a finding from an inspected citation implementation.

[^rag-hardest-part]: [The hardest part of building a RAG knowledge base happens before embeddings](../raw/the-hardest-part-of-building-a-rag-knowledge-base/index.md), r/Rag discussion captured 2026-10-26, no revision. Locators: comment `/pgwh7me/` (post-conversion checks: table totals, values under headers, numbers traceable to the source page; worst-document regression set; disclosure of a document-to-fields vendor); comment `/ph8a0wq/` (page-spanning table with lost column headers, citation of bad extraction); comment `/ph3tmn0/` (near-identical current-versus-stale revisions, hash dedup limit); comment `/pgvslz4/` (same-time A/B for search); comment `/ph2lqhe/` (kNN versus adaptive search, score rescaling, `k+n` lexical finds); post body, stage 8 of the pipeline (dedup by rules, fingerprints, or semantic similarity).
