---
type: Concept
title: Qwen3-VL-Reranker-8B
description: An Apache-2.0 8B-parameter, 36-layer instruction-aware multimodal cross-encoder reranker with a 32K context limit and binary yes/no relevance scoring.
tags: [reranker, retrieval, multimodal, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:13:34Z }
sources:
  - id: qwen3-vl-reranker-8b-card
    resource: ../raw/Qwen3-VL-Reranker-8B.md
    title: Qwen3-VL-Reranker-8B model card
  - id: qwen3-vl-retrieval-report
    resource: ../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex
    title: "Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking"
---

# Qwen3-VL-Reranker-8B

Qwen3-VL-Reranker-8B is an Apache-2.0, instruction-aware, pointwise multimodal reranker built from Qwen3-VL-8B-Instruct. Unlike the family’s bi-encoder embedding models, it jointly processes a query and candidate document with causal attention and scores fine-grained relevance from the next-token probabilities of `yes` and `no`. It accepts text, images, screenshots, video, or mixed-modality query-document pairs.[^qwen3-vl-reranker-8b-card][^qwen3-vl-retrieval-report]

## Architecture and scoring

- **Scale:** 8B parameters, 36 layers, and a 32K-token sequence limit.[^qwen3-vl-retrieval-report]
- **Input:** a system prompt constrains the output to `yes` or `no`; the user message supplies the relevance instruction, query, and document.[^qwen3-vl-retrieval-report]
- **Objective:** binary next-token cross-entropy for positive and negative pairs.[^qwen3-vl-retrieval-report]
- **Score:** $\operatorname{sigmoid}(\operatorname{logit}(\text{yes})-\operatorname{logit}(\text{no}))$.[^qwen3-vl-retrieval-report]

## Deployment and prompting

The model card lists support for more than 30 languages and task-specific instructions; it recommends English instructions for multilingual use because most training instructions were originally written in English. It supplies integrations through Sentence Transformers `CrossEncoder`, the Qwen Transformers implementation, and vLLM’s pooling runner. The Sentence Transformers interface accepts text, image URLs, or dictionaries combining text and image fields; its default prompt uses the instruction “Retrieve text relevant to the user's query.” The card recommends FlashAttention 2 for acceleration and reduced memory use in the Transformers path.[^qwen3-vl-reranker-8b-card]

## Training

The reranker is initialized from Qwen3-VL-Instruct and trained with LoRA during the second stage of the family pipeline. Training uses a retrieval-specific subset of mined public, proprietary, and synthetic multimodal relevance data spanning image, video, moment, and visual-document retrieval. The report does not provide dataset size or composition counts.[^qwen3-vl-retrieval-report]

## Reported evaluation

After top-100 retrieval by Qwen3-VL-Embedding-2B, the authors report 79.2 average on MMEB-v2 retrieval, 74.9 on MMTEB retrieval, 83.6 on JinaVDR, and 66.7 on ViDoRe v3. It outperforms the 2B reranker on each reported aggregate. These are author-run results rather than independent reproductions, and complete metric and benchmark-revision details are not supplied for every aggregate.[^qwen3-vl-retrieval-report]

## Relationships

- **Reranks candidates from:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) in the report’s evaluation pipeline.
- **Larger variant of:** [Qwen3-VL-Reranker-2B](qwen3-vl-reranker-2b.md).
- **Distills into:** the Qwen3-VL embedding family during its third training stage.

[^qwen3-vl-reranker-8b-card]: [Qwen3-VL-Reranker-8B model card](../raw/Qwen3-VL-Reranker-8B.md). License, deployment, language, modality, and benchmark claims are author-reported.
[^qwen3-vl-retrieval-report]: [Qwen3-VL retrieval technical report](../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex). Architecture, training, and evaluation claims are author-reported; proprietary training data prevents full auditability.
