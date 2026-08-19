---
type: Concept
title: jina-reranker-v3.5
description: A 0.6B-parameter multilingual listwise reranker with 131K-token context, 3L2G hybrid attention, and reported gains in general, domain, structured, and multilingual retrieval.
tags: [reranking, retrieval, multilingual, listwise, hybrid-attention, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T14:19:28Z }
sources:
  - id: jina-reranker-v3-5-card
    resource: ../raw/jina-reranker-v3.5.md
    title: jina-reranker-v3.5 model card
  - id: jina-reranker-v3-5-report
    resource: ../raw/2607.18152_jina-reranker-v3.5/main.tex
    title: jina-reranker-v3.5 technical-report LaTeX source (arXiv:2607.18152)
  - id: jina-reranker-v3-card
    resource: ../raw/jina-reranker-v3.md
    title: jina-reranker-v3 model card
---

# jina-reranker-v3.5

jina-reranker-v3.5 is a CC BY-NC 4.0, 0.6B-parameter multilingual listwise document reranker and a drop-in successor to jina-reranker-v3. It jointly ranks a query and candidate list in one causal-attention pass, supporting up to 131K tokens of context. [^jina-reranker-v3-5-card] [^jina-reranker-v3-5-report]

## Architecture and scoring

The model uses a 28-layer Qwen3-0.6B backbone with a 3L2G attention schedule: 17 sliding-window layers and 11 global layers, with a 1,024-token local window. Its final layer remains global so the trailing query representation can attend to every candidate; a two-layer 1024→512→512 MLP projects the query and document token representations, whose cosine similarities provide relevance scores. [^jina-reranker-v3-5-card] [^jina-reranker-v3-5-report]

The local `transformers` interface is `model.rerank(query, documents, top_n=None, return_embeddings=False)`, returning relevance-sorted documents, scores, input indices, and optionally document embeddings. The hosted API preserves the jina-reranker-v3 request schema; switching the model identifier is the documented upgrade path. [^jina-reranker-v3-5-card]

## Training

The technical report describes a failure-mode-focused mixture spanning legal, medical, financial, multilingual, and semi-structured retrieval. It trains a full-attention teacher, adapts an equal-sized student to 3L2G attention (first attention projections, then all parameters), then applies multi-level teacher-guided distillation over rankings, scores, hidden states, and projected embeddings. These are author-reported training details, not an independent reproduction. [^jina-reranker-v3-5-report]

## Reported evaluation and efficiency

The authors evaluate top-100 candidates from [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md), except that Struct-IR uses a controlled pool containing gold documents and 30 hard distractors. The report's scores therefore characterize reranking in those candidate-generation regimes, not end-to-end retrieval. [^jina-reranker-v3-5-report]

| Evaluation (nDCG@10, %) | v3.5 | v3 | Qwen3-Reranker-4B |
|---|---:|---:|---:|
| BEIR | 63.20 | 62.10 | 62.28 |
| MIRACL | 74.11 | 72.20 | 76.56 |
| RTEB (excludes MIRACL average) | 70.95 | 68.01 | 77.68 |
| Struct-IR controlled pool | 48.3 | 38.7 | 55.6 |

On STARK, the report renders entity attributes with relational context and reranks the top 100 candidates from Jina Embeddings v5 Text Small under the benchmark's official protocol. It reports 45.0 Hit@1, 65.4 Hit@5, and 53.8 MRR for v3.5, versus 43.4, 63.6, and 53.2 for v3; these are author-reported reranking results in that stated candidate-generation regime. [^jina-reranker-v3-5-report]

On an NVIDIA A100 with batch size 1, FlashAttention-2, and top-100 listwise reranking, the report measures 1.22× lower-latency execution than v3 on short Natural Questions inputs (305.3 ms vs. 371.1 ms) and 1.56× on long AILACasedocs inputs (10.29 s vs. 16.06 s). These are report-specific benchmark results rather than deployment guarantees. [^jina-reranker-v3-5-report]

## Contradictions

- The v3 model card reports 61.94 BEIR nDCG@10, whereas this report records 62.10 for v3 under a unified top-100 reranking protocol with [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md) as the first-stage retriever. The v3 card does not specify its protocol, so the difference remains unresolved and may be protocol-dependent. Both values are author-reported. [^jina-reranker-v3-card] [^jina-reranker-v3-5-report]

## Relationships

- **Uses:** [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md) as the first-stage retriever in the reported top-100 reranking evaluations. [^jina-reranker-v3-5-report]
- **Supersedes:** [jina-reranker-v3](jina-reranker-v3.md) for new projects. The v3 model card describes v3.5 as a drop-in upgrade with the same API; v3 is recorded as deprecated in this wiki on 2026-08-19. [^jina-reranker-v3-card]

[^jina-reranker-v3-5-card]: [jina-reranker-v3.5 model card](../raw/jina-reranker-v3.5.md). Model-card architecture, interface, licensing, and benchmark claims are publisher-authored.
[^jina-reranker-v3-5-report]: [jina-reranker-v3.5 technical-report LaTeX source](../raw/2607.18152_jina-reranker-v3.5/main.tex), arXiv:2607.18152. Architecture, training, evaluation, and efficiency claims are author-reported and not independently reproduced.
[^jina-reranker-v3-card]: [jina-reranker-v3 model card](../raw/jina-reranker-v3.md). The publisher's successor and API-compatibility claim supports this relationship.
