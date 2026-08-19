---
type: Concept
title: Qwen3-VL-Reranker-2B
description: An Apache-2.0 2B-parameter, 28-layer instruction-aware multimodal cross-encoder reranker with a 32K context limit and binary yes/no relevance scoring.
tags: [reranker, retrieval, multimodal, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:13:34Z }
sources:
  - id: qwen3-vl-reranker-2b-card
    resource: ../raw/Qwen3-VL-Reranker-2B.md
    title: Qwen3-VL-Reranker-2B model card
  - id: qwen3-vl-retrieval-report
    resource: ../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex
    title: "Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking"
---

# Qwen3-VL-Reranker-2B

Qwen3-VL-Reranker-2B is an Apache-2.0, instruction-aware, pointwise multimodal reranker built from Qwen3-VL-2B-Instruct. Unlike the family’s bi-encoder embedding models, it jointly processes a query and candidate document with causal attention and scores fine-grained relevance from the next-token probabilities of `yes` and `no`. It accepts text, images, screenshots, video, or mixed-modality query-document pairs.[^qwen3-vl-reranker-2b-card][^qwen3-vl-retrieval-report]

## Architecture and scoring

- **Scale:** 2B parameters, 28 layers, and a 32K-token sequence limit.[^qwen3-vl-retrieval-report]
- **Input:** a system prompt constrains the answer to `yes` or `no`; the user message contains the task-specific relevance instruction, query, and document.[^qwen3-vl-retrieval-report]
- **Objective:** binary next-token cross-entropy for positive and negative pairs.[^qwen3-vl-retrieval-report]
- **Score:** $\operatorname{sigmoid}(\operatorname{logit}(\text{yes})-\operatorname{logit}(\text{no}))$.[^qwen3-vl-retrieval-report]

## Deployment and prompting

The model card lists support for more than 30 languages and task-specific instructions; it recommends English instructions for multilingual use because most training instructions were originally written in English. It supplies integrations through Sentence Transformers `CrossEncoder`, the Qwen Transformers implementation, and vLLM’s pooling runner. The Sentence Transformers interface accepts text, image URLs, or dictionaries combining text and image fields; its default prompt uses the instruction “Retrieve text relevant to the user's query.” The card recommends FlashAttention 2 for acceleration and reduced memory use in the Transformers path.[^qwen3-vl-reranker-2b-card]

## Training

The reranker is initialized from Qwen3-VL-Instruct and trained with LoRA during the second stage of the family pipeline. Its data is the retrieval-specific portion of newly mined public, proprietary, and synthetic multimodal relevance data, including image, video, moment, and visual-document retrieval. The report does not quantify dataset size or the public/proprietary split.[^qwen3-vl-retrieval-report]

## Reported evaluation

With Qwen3-VL-Embedding-2B retrieving the top 100 candidates, the authors report 75.2 average on MMEB-v2 retrieval, 70.0 on MMTEB retrieval, 80.9 on JinaVDR, and 60.8 on ViDoRe v3. These are author-run results rather than independent reproductions; the report does not specify every metric or benchmark revision needed for cross-publication comparison.[^qwen3-vl-retrieval-report]

## Contradictions

- The technical report lists a 75.2 MMEB-v2 retrieval average for the 2B reranker, while the model card lists 75.1; neither source explains the 0.1-point difference. Both give 70.0 MMTEB, 80.9 JinaVDR, and 60.8 ViDoRe v3.[^qwen3-vl-retrieval-report][^qwen3-vl-reranker-2b-card]

## Relationships

- **Reranks candidates from:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) in the report’s evaluation pipeline.
- **Smaller variant of:** [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md).
- **Distills into:** the Qwen3-VL embedding family during its third training stage.

[^qwen3-vl-reranker-2b-card]: [Qwen3-VL-Reranker-2B model card](../raw/Qwen3-VL-Reranker-2B.md). License, deployment, language, modality, and benchmark claims are author-reported.
[^qwen3-vl-retrieval-report]: [Qwen3-VL retrieval technical report](../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex). Architecture, training, and evaluation claims are author-reported; proprietary training data prevents full auditability.
