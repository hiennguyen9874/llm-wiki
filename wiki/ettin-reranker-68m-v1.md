---
type: Concept
title: ettin-reranker-68m-v1
description: A 68.6M-parameter English cross-encoder reranker with a 7,999-token maximum sequence length, trained on 143.4M query–document pairs.
tags: [reranking, retrieval, cross-encoder, english, sentence-transformers]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:16:35Z }
sources:
  - id: ettin-reranker-68m-v1-model-card
    resource: ../raw/ettin-reranker-68m-v1.md
    title: ettin-reranker-68m-v1 model card
---

# ettin-reranker-68m-v1

ettin-reranker-68m-v1 is an Apache-2.0 English text cross-encoder that assigns a relevance score to each query–document pair for reranking or semantic-search pipelines. The model card reports 68.6M parameters and a 7,999-token maximum sequence length.[^ettin-reranker-68m-v1-model-card]

## Architecture and use

- **Base model:** `jhu-clsp/ettin-encoder-68m` at revision `ac19ae4bc51093b31c475665ac872a936d056cc2`.[^ettin-reranker-68m-v1-model-card]
- **Architecture:** ModernBERT transformer, CLS pooling, a 512-dimensional GELU projection and layer normalization, then a single-output identity-activated dense scoring head.[^ettin-reranker-68m-v1-model-card]
- **Interface:** Sentence Transformers `CrossEncoder` accepts query–passage pairs through `predict`; `rank` orders a passage collection for one query. Returned scores are model relevance scores, not documented as calibrated probabilities.[^ettin-reranker-68m-v1-model-card]
- **Acceleration:** The supplied loading example uses `bfloat16` and FlashAttention 2 as optional model settings.[^ettin-reranker-68m-v1-model-card]

## Training

The model was fine-tuned for one epoch with identity-activated MSE loss on `cross-encoder/ettin-reranker-v1-data`. The card reports 143,393,475 training samples with `query`, `document`, and float `label` columns; training used a batch size of 16, learning rate `3e-5`, 3% warmup, and bfloat16. Reported training time was 11.2 hours, plus 9.2 minutes of evaluation.[^ettin-reranker-68m-v1-model-card]

## Reported evaluation and throughput

The model card reports mean NDCG@10 of 0.5915 on MTEB(eng, v2) Retrieval, averaged across six embedding-model candidate generators with the top 100 candidates reranked. Its training-time NanoBEIR R100 mean was MAP 0.6347, MRR@10 0.7499, and NDCG@10 0.6895; the card notes that its release blog reports 0.6915 NDCG@10 from fp32 evaluation instead of the card's bfloat16 evaluation.[^ettin-reranker-68m-v1-model-card]

At `max_length=512`, the card reports 4,913 pairs/s on an NVIDIA H100 80GB and 1,916 pairs/s on an RTX 3090, both using FlashAttention 2; it reports 31.2 pairs/s on an Intel Core i7-13700K using SDPA. These are publisher benchmarks on `sentence-transformers/natural-questions`, not deployment guarantees.[^ettin-reranker-68m-v1-model-card]

[^ettin-reranker-68m-v1-model-card]: [ettin-reranker-68m-v1 model card](../raw/ettin-reranker-68m-v1.md). Architecture, training, evaluation, and throughput are publisher-authored claims.
