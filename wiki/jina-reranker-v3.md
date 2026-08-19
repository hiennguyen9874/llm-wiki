---
type: Concept
title: jina-reranker-v3
description: A deprecated 0.6B-parameter multilingual listwise document reranker that jointly scores a query and up to 64 documents in a 131K-token context.
tags: [reranking, retrieval, multilingual, listwise, jina, deprecated]
status: deprecated
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:20:00Z }
sources:
  - id: jina-reranker-v3-card
    resource: ../raw/jina-reranker-v3.md
    title: jina-reranker-v3 model card
  - id: jina-reranker-v3-5-report
    resource: ../raw/2607.18152_jina-reranker-v3.5.tar.gz
    title: jina-reranker-v3.5 technical-report LaTeX archive (arXiv:2607.18152)
---

# jina-reranker-v3

jina-reranker-v3 is a 0.6B-parameter multilingual listwise document reranker built on Qwen3-0.6B. It jointly processes a query and candidate documents in one causal-attention context and returns relevance-ranked results. The publisher recommends [jina-reranker-v3.5](jina-reranker-v3-5.md) instead for new projects; this concept is therefore deprecated as of 2026-08-19. [^jina-reranker-v3-card]

## Architecture and limits

Unlike a ColBERT-style independently encoded multi-vector retriever, v3 uses causal self-attention across the query and documents in one context window, then extracts contextual embeddings from each document's final token. The model has a 28-layer Qwen3-0.6B backbone and a lightweight 1,024→512→256 MLP projector. [^jina-reranker-v3-card]

The model card states that it can process up to 64 documents simultaneously within a 131K-token context. This limit is a publisher-provided capability claim; its effective capacity depends on the combined query and document lengths. [^jina-reranker-v3-card]

## Interface and licensing

The local `transformers` interface is `model.rerank(query, documents, top_n=None, return_embeddings=False)`. It returns dictionaries containing each original document, its higher-is-better relevance score, its input index, and optionally its embedding. A hosted reranking API accepts the model identifier, query, candidate documents, and optional document-return behavior. [^jina-reranker-v3-card]

The model card lists the license as CC BY-NC 4.0 and directs commercial-use inquiries to Jina AI. [^jina-reranker-v3-card]

## Reported evaluation

The model card reports 61.94 BEIR nDCG@10, with additional reported scores of 66.83 on MIRACL, 67.92 on MKQA, and 70.64 on CoIR. It describes the BEIR result as state of the art and the model as 10× smaller than generative listwise rerankers. These are publisher-reported comparisons, not independently reproduced results. [^jina-reranker-v3-card]

## Contradictions

- The v3 model card reports 61.94 BEIR nDCG@10, while the v3.5 technical report reports 62.10 for v3 under its unified top-100 reranking protocol using Jina Embeddings v5 Text Small as the first-stage retriever. Because the v3 card does not specify its evaluation protocol, the discrepancy cannot be resolved from these sources and may be protocol-dependent. Both are author-reported. [^jina-reranker-v3-card] [^jina-reranker-v3-5-report]

## Supersession

The v3 model card recommends v3.5 as a drop-in upgrade with the same API and stronger domain, multilingual, structured-ranking, and listwise-inference claims. The card does not give an effective date; the wiki records v3 as deprecated on 2026-08-19, when this recommendation was compiled. [^jina-reranker-v3-card]

## Relationships

- **Superseded by:** [jina-reranker-v3.5](jina-reranker-v3-5.md) for new projects, according to the v3 model card. [^jina-reranker-v3-card]

[^jina-reranker-v3-card]: [jina-reranker-v3 model card](../raw/jina-reranker-v3.md). Architecture, interface, licensing, benchmark, and successor claims are publisher-authored.
[^jina-reranker-v3-5-report]: [jina-reranker-v3.5 technical-report LaTeX archive](../raw/2607.18152_jina-reranker-v3.5.tar.gz), arXiv:2607.18152. Its v3 comparison result uses a stated top-100 reranking protocol.