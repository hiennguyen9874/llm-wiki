---
type: Concept
title: zerank-2
description: A 4B-parameter Apache-2.0 Qwen3-4B-based text reranker with a 32,768-token context limit and raw-logit Sentence Transformers scoring.
tags: [reranking, retrieval, cross-encoder, qwen, sentence-transformers]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:23:02Z }
sources:
  - id: zerank-2-model-card
    resource: ../raw/zerank-2-reranker.md
    title: zeroentropy/zerank-2 model card
---

# zerank-2

zerank-2 is an Apache-2.0, 4B-parameter text reranker based on Qwen/Qwen3-4B, with a 32,768-token context limit. The publisher describes a multi-stage training pipeline that models query–document relevance as adjusted Elo ratings, but this source provides no further training details. [^zerank-2-model-card]

## Scoring and use

The documented Sentence Transformers interface loads `CrossEncoder("zeroentropy/zerank-2")`. `model.predict()` scores query–document pairs and, since a May 2026 breaking change, returns raw `Yes` logits rather than sigmoid probabilities; ranking order is unchanged. To produce the previous 0–1-style score, apply `sigmoid(score / 5)`. `model.rank(query, documents)` returns documents sorted by those raw scores. [^zerank-2-model-card]

The model can also be served through ZeroEntropy’s `/models/rerank` API endpoint or AWS Marketplace. This source does not document languages, throughput, hardware requirements, or a reproducible training procedure. [^zerank-2-model-card]

## Reported evaluation

The publisher evaluates reranking after retrieving the top 100 candidate documents with OpenAI `text-embedding-3-small`; these NDCG@10 values are reranking-pipeline results, not end-to-end retrieval scores.

| Domain | zerank-2 | zerank-1 | Gemini 2.5 Flash (listwise) | Cohere rerank-3.5 |
|---|---:|---:|---:|---:|
| Web | 0.6346 | 0.6069 | 0.5765 | 0.5594 |
| Conversational | 0.6140 | 0.5801 | 0.6021 | 0.5648 |
| STEM & Logic | 0.6521 | 0.6283 | 0.5447 | 0.5418 |
| Code | 0.6528 | 0.6310 | 0.6128 | 0.5364 |
| Legal | 0.6644 | 0.6222 | 0.5565 | 0.5257 |
| Biomedical | 0.7217 | 0.6967 | 0.5371 | 0.6246 |
| Finance | 0.7600 | 0.7539 | 0.7694 | 0.7402 |
| Average | 0.6714 | 0.6456 | 0.5999 | 0.5847 |

In this publisher-reported table, zerank-2 leads the named models in every listed domain except Finance, where Gemini 2.5 Flash scores 0.7694 versus 0.7600. [^zerank-2-model-card]

[^zerank-2-model-card]: [zeroentropy/zerank-2 model card](../raw/zerank-2-reranker.md). Architecture, training, interface, licensing, deployment, and evaluation claims are publisher-authored.