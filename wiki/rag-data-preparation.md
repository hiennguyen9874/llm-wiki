---
type: Concept
title: RAG data preparation before embedding
description: Reported eight-stage pipeline that converts, cleans, and validates heterogeneous sources into provenance-bearing retrieval-ready records before any embedding runs.
tags: [rag, ingestion, parsing, chunking, provenance]
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

# RAG data preparation before embedding

**Reported:** the hardest work in a RAG knowledge base is converting and cleaning heterogeneous source data *before* the first embedding, not selecting an embedding model. The post argues that poor answers get blamed on the embedding model while the real defect is duplicated, artifact-ridden, context-stripped source records pushed straight into the vector store. The argument is one practitioner's post in r/Rag with no dataset, measurement, or experiment attached, so it reads as design guidance rather than a demonstrated effect.[^rag-hardest-part]

## Why flattening to plain text loses retrieval signal

Enterprise knowledge is spread across PDFs, Word files, spreadsheets, slide decks, scanned pages, images, tables, and databases that share no structure. The post names four concrete context losses that plain-text conversion causes:

| Source form | Context that flattening removes |
| --- | --- |
| PDF | headers, footers, paragraph boundaries; tables whose meaning depends on surrounding text |
| Chart or image | labels and visual relationships, which can carry more meaning than the caption |
| Database row | schema and business context, without which an accurate value is meaningless |
| Any format | extraction artifacts: duplicates, formatting debris, missing values, partial records |

The consequence chain is: artifacts enter the vector store → the retriever searches noise → the answer looks like an embedding-model failure. The post's remedy is to make conversion and cleaning an explicit engineering stage with its own outputs.[^rag-hardest-part]

## The eight-stage pipeline

| # | Stage | Output the pipeline requires |
| --- | --- | --- |
| 1 | Ingest source data | file name, page number, section, table, image, database, and record identifiers preserved as provenance |
| 2 | Convert each format to a structured representation | content-plus-metadata records for document text, tables, chart descriptions, images, and database records |
| 3 | Clean and normalize | repeated headers and footers, invalid characters, broken fragments, empty fields, and formatting artifacts removed |
| 4 | Preserve relationships and context | table headers stay attached to values, chart labels stay attached to visual content, database rows retain schema |
| 5 | Chunk meaningfully | boundaries from document structure, sections, records, or semantic breaks rather than fixed character length alone |
| 6 | Generate retrieval-ready data | question–answer pairs, summaries, explanations, or context-enriched passages |
| 7 | Evaluate and filter | completeness, source consistency, language, length, and relevance checked per record |
| 8 | Deduplicate and export | rules, fingerprints, or semantic similarity remove duplicates and near-duplicates; validated data exported for embedding and indexing |

Stage 5 is the point where this generic pipeline meets the platform-specific chunkers: compare [LightRAG chunking strategies and provenance](lightrag-chunking.md), [RAGFlow document ingestion](ragflow-ingestion.md), [WeKnora document parsing and adaptive chunking](weknora-document-ingestion.md), and [UltraRAG corpus processing and chunking](ultrarag-corpus.md). The post does not compare these strategies or say which boundary rule fits which corpus.[^rag-hardest-part]

## Per-stage artifacts and format branches

Two operational requirements ride alongside the stages:

- **Checkpoint after each major step.** Persisting intermediate output lets a failed extraction or an over-aggressive filter be inspected and corrected without rebuilding the whole dataset.
- **Branch by format, converge downstream.** PDFs, images, tables, and structured database data may need different processing branches, but every branch must emit the same downstream record shape so cleaning, filtering, deduplication, and export stay shared.

Both are design claims; the post reports no implementation, run, or measured benefit from checkpointing.[^rag-hardest-part]

## Contradictions

The discussion does not settle how decisive data preparation is:

- **Dominant-factor claim (post author):** source-data defects are the main cause of bad retrieval, so preparation deserves the front of the schedule.
- **Top-k counter-claim (commenter):** because RAG retrieves only a top-k window, data quality is reported as a limited factor while chunk strategy carries more weight; the same commenter reports company use cases moving away from RAG toward an AI document parser plus SQL agent, which raises the up-front data-quality bar because queries then run across the whole dataset.
- **Parsing-and-chunking-first claim (another commenter):** parsing and inventive chunking control everything, and data cleanliness is a boring prerequisite rather than the differentiator.

Neither side offers measurements, so the page records the disagreement instead of choosing: preparation quality plausibly bounds retrieval quality, but the size of that bound relative to chunking, retrieval mode, and model choice is unestablished.[^rag-hardest-part]

## Relationships

- **Depends on:** [ingestion validation and version currency](rag-ingestion-validation.md) for post-conversion checks, worst-document regression sets, and current-version determination.
- **Used by:** any platform ingestion path — see [RAG-Anything document ingestion](rag-anything-ingestion.md), [OpenRAG document ingestion](openrag-document-ingestion.md), and [RAGFlow document ingestion](ragflow-ingestion.md) for code-grounded variants of stages 1–5.
- **Related to:** [LightRAG chunking strategies and provenance](lightrag-chunking.md) for the contract between chunk provenance and source spans.

## Evidence and limits

Every claim here is **Reported**, from a pseudonymous social-media discussion captured on 2026-10-26. Limits:

- No pinned revision exists; the capture is a point-in-time copy of a mutable Reddit thread, so edits and later comments are invisible.
- No data, metric, or ablation supports the stage ordering, the checkpointing advice, or the effect on answer quality.
- The author names `OpenDCAI/DataFlow` as an implementation of the design. That repository is not present under `raw/` and was not inspected, so the claim is unverified and no stage is confirmed to exist in code.
- Commenter disclosures that promote commercial products were excluded as promotion, not knowledge.
- Practitioner handles are omitted deliberately; the permalinks under [the source post](../raw/the-hardest-part-of-building-a-rag-knowledge-base/index.md) remain the resolvable provenance.

[^rag-hardest-part]: [The hardest part of building a RAG knowledge base happens before embeddings](../raw/the-hardest-part-of-building-a-rag-knowledge-base/index.md), r/Rag discussion captured 2026-10-26, no revision. Locators: post body ¶1–3 (collection assumption, format heterogeneity, context loss), ¶4 (misattribution to the embedding model); section *A practical pipeline can be designed around several stages*, numbered items 1–8; the paragraph following it on intermediate outputs and per-format branches; closing paragraph naming `OpenDCAI/DataFlow`; comments `/pgvslz4/` (parsing and chunking control everything), `/ph0oepj/` (top-k framing, parser-plus-SQL-agent shift), and `/ph2lqhe/` (search-mode and score-rescaling claims).
