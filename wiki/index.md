---
title: Index
created: 2026-04-14
last_updated: 2026-04-24
source_count: 14
status: draft
page_type: index
aliases: [Catalog]
tags: [system, navigation]
---

Master catalog of the second brain. Use this file for human orientation and browsing; rely on QMD, metadata, and relationships for deeper retrieval as the wiki grows.

## Core
- [[home]] — high-level overview of the knowledge base and how it is organized.
- [[index]] — master catalog of pages by category.
- [[log]] — append-only operational timeline of ingests, queries, lint runs, and updates.

## Dashboards and Visual Maps
- `wiki/bases/inbox.base` — Base view for markdown items waiting in `raw/inbox/`.
- `wiki/bases/review.base` — Base view for pages that are drafts, stale, or need review.
- `wiki/canvases/home.canvas` — starter visual map of the second-brain workflow.

## Crystallizations and Durable Outputs
- `outputs/crystallizations/` — structured digests distilled from completed research, debugging, or exploration sessions.
- `outputs/answers/` — durable saved answers worth promoting when they become recurring knowledge.
- `outputs/analyses/text-to-image-person-retrieval-unexplored-connections.md` — cross-topic gap scan on the TBPS lever families and likely follow-up comparisons.

## Sources
- [[source-arxiv-2303-12501-irra]] — arXiv source page for the IRRA paper, preserved from LaTeX source rather than PDF.
- [[source-github-anosorae-irra]] — GitHub source page for the public IRRA implementation companion, including the CLIP `ViT-B/16` recipe, `(384, 128)` input geometry, and direct global-similarity evaluator.
- [[source-arxiv-2308-09911-rde]] — arXiv source page for the RDE paper on noisy correspondence in text-to-image person re-identification.
- [[source-github-qinyang79-rde]] — GitHub source page for the public RDE implementation companion, including dual-branch loss modeling, synthetic-noise indices, and consensus filtering details.
- [[source-arxiv-2308-10045-tbps-clip]] — arXiv source page for the CLIP-in-TBPS empirical study and lightweight baseline recipe.
- [[source-github-flame-chasers-tbps-clip]] — GitHub source page for the public TBPS-CLIP implementation and simplified preset.
- [[source-arxiv-2407-04287-mars]] — arXiv source page for the MARS paper on attribute-aware TBPS with masked reconstruction.
- [[source-github-ergastialex-mars]] — GitHub source page for the public MARS implementation companion, including the seven-loss training stack, full-cross-attention reranking, and spaCy-derived attribute masking.
- [[source-arxiv-2507-10195-mra]] — arXiv source page for the MRA paper on domain-aligned synthetic pretraining and region-phrase alignment.
- [[source-arxiv-2509-09118-ga-dms]] — arXiv source page for the GA-DMS paper and its companion WebPerson dataset for robust text-based person retrieval.
- [[source-github-multimodal-representation-learning-mrl-ga-dms]] — GitHub source page for the public GA-DMS implementation, including gradient-attention token-map generation and staged similarity-guided dual masking.
- [[source-arxiv-2601-18625-conquer]] — arXiv source page for the CONQUER paper on context-aware alignment plus inference-time query enhancement for text-based person search.
- [[source-arxiv-2510-17685-bi-irra]] — arXiv source page for the Bi-IRRA paper on multilingual text-to-image person retrieval and multilingual benchmark construction.
- [[source-arxiv-2604-18376-mvr]] — arXiv source page for the MVR paper on training-free multi-view semantic compensation for robust text-to-image person retrieval.

## Topics and Concepts
- [[text-to-image-person-retrieval]] — task-level topic page linking CLIP-based retrieval methods, robustness concerns, recipe tuning, and data-centric pretraining strategies.
- [[irra]] — method page for the IRRA architecture, claims, and now its public code companion.
- [[tbps-clip]] — method page for the lightweight CLIP recipe baseline and its benchmark / few-shot findings.
- [[mars]] — method page for attribute-aware TBPS with masked reconstruction and its public code companion.
- [[rde]] — method page for Robust Dual Embedding and its robustness-oriented design.
- [[mra]] — method page for Multi-granularity Relation Alignment and its benchmark progression.
- [[ga-dms]] — method page for gradient-attention-guided dual masking in CLIP-based person retrieval.
- [[conquer]] — method page for the two-stage CARE + IQE framework that refines both embeddings and user queries.
- [[bi-irra]] — method page for the multilingual IRRA extension with bidirectional multilingual relation reasoning and LDAT-backed benchmark construction.
- [[mvr]] — method page for training-free LLM-assisted multi-view reformulation and semantic compensation.
- [[webperson]] — dataset page for the 5M-scale curated web person image-text corpus.
- [[domain-aware-diffusion]] — concept page for synthetic-to-real image-level domain adaptation in the MRA pipeline.
- [[synthetic-domain-aligned-dataset]] — concept page for the SDA synthetic pretraining corpus.
- [[noisy-correspondence]] — concept page for pair-level image-text misalignment noise.

## Projects
<!-- Add project pages here -->

## People
<!-- Add person pages here -->

## Timelines
<!-- Add timeline pages here -->

## Syntheses and Comparisons
- [[text-to-image-person-retrieval-research-agenda]] — prioritized next-research gaps and synthesis for the current text-to-image person retrieval cluster.

## Outputs Worth Promoting into Wiki
- [[text-based-person-search-methods-models-briefing]] — reusable briefing on the current in-vault design space for text-based person search.
- [[text-based-person-search-methods-models-session-crystallization]] — episodic summary of the retrieval-and-benchmark session that produced the briefing and table.
- `outputs/answers/tbps-method-synthesis-and-hybrid-recommendation.md` — recommendation-oriented synthesis on how to combine the TBPS levers into a practical hybrid and when to prefer MVR, Bi-IRRA, or CONQUER.
- `outputs/answers/tbps-hybrid-architecture-spec.md` — more concrete hybrid architecture proposal with training stack, data strategy, inference gates, and multilingual branch.
- `outputs/crystallizations/tbps-hybrid-architecture-session-crystallization.md` — episodic crystallization of the hybrid-architecture session, including the 5-axis framing and modular stack recommendation.

