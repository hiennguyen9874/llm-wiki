---
type: Concept
title: Querit-Reranker
description: A multilingual MoE text reranker with 4.92B total parameters, 0.43B active parameters, 24 layers, and a 128K-token context limit.
tags: [reranking, retrieval, multilingual, moe]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:09:02Z }
sources:
  - id: querit-reranker-model-card
    resource: ../raw/Querit-Reranker.md
    title: Querit-Reranker model card
---

# Querit-Reranker

Querit-Reranker is a multilingual text-ranking model based on Querit's self-developed mixture-of-experts foundation model. The model card reports 4.92B total parameters, with 0.43B active parameters, and a 128K-token context limit.[^querit-reranker-model-card]

## Architecture and coverage

- **Task:** text reranking.
- **Architecture:** MoE foundation-model derivative with 24 layers and 16 attention heads; the card reports 4.79B non-embedding parameters.[^querit-reranker-model-card]
- **Languages:** Chinese, English, Spanish, French, German, Russian, Korean, and Japanese.[^querit-reranker-model-card]

## Training and evidence limits

The model card says the model received ranking-specific post-training using open-source and proprietary data, but does not identify datasets, training procedure, scoring interface, evaluation benchmarks, or quantitative results. Its cited paper is *Querit-Reranker: Training Compact Multilingual Rerankers via Efficient Label-Free Distribution Adaptation* (arXiv:2606.19037); that paper was not included in this source and has not been independently compiled.[^querit-reranker-model-card]

[^querit-reranker-model-card]: [Querit-Reranker model card](../raw/Querit-Reranker.md). Architecture, language coverage, training, and citation details are model-card claims.
