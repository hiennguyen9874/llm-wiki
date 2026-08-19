---
type: Concept
title: Tianmu-Emb-Uni-8B
description: An 8B-scale unified multimodal embedding model combining a Qwen3-VL embedding backbone with a Qwen2.5-Omni audio tower, producing 3,584-dimensional vectors and reporting 53.27 across 190 MMEB-V3 tasks.
tags: [embedding, retrieval, multimodal, multilingual, audio, qwen, mmeb]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T09:56:53Z }
sources:
  - id: tianmu-emb-uni-8b-card
    resource: ../raw/Tianmu-Emb-Uni-8B.md
    title: Tianmu-Emb-Uni-8B model card
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
---

# Tianmu-Emb-Uni-8B

Tianmu-Emb-Uni-8B is a unified embedding model for text, images, video, visual documents, audio, and agent tasks. It aligns an audio branch initialized from Qwen2.5-Omni-7B with a Qwen3-VL-Embedding-8B representation space. The release is not a standalone full 8B checkpoint: it supplies trained audio-side, connector, projection, adapter, and prototype modules while requiring the two base models separately.[^tianmu-emb-uni-8b-card]

## Model size and architecture

- **Declared scale:** The card expands “8B” as the model scale and names Qwen3-VL-Embedding-8B as the vision-language backbone. It does not report an exact total parameter count for the assembled system, which also uses a Qwen2.5-Omni-7B audio tower.[^tianmu-emb-uni-8b-card]
- **Architecture:** A Qwen3-VL embedding backbone provides the shared embedding space. An audio branch initialized from the Qwen2.5-Omni audio tower connects to that space through trainable connector, projection, adapter, and prototype modules.[^tianmu-emb-uni-8b-card]
- **Output:** 3,584-dimensional embeddings.[^tianmu-emb-uni-8b-card]
- **Released checkpoint:** `stage1b_adapter_proto_retrieval`. The package includes the trained audio-side and alignment modules, not the full Qwen3-VL-Embedding-8B or Qwen2.5-Omni-7B weights, and does not support native `AutoModel.from_pretrained` loading.[^tianmu-emb-uni-8b-card]

## Language support

The model-card metadata declares Chinese and English. It does not enumerate broader language coverage, explain whether support differs by modality, or report language-specific benchmark results. Multilingual capability beyond Chinese and English is therefore not established by this source.[^tianmu-emb-uni-8b-card]

## Training data

The card does not identify training datasets, sample counts, language or modality distributions, filtering, objectives, or training schedule. It identifies the released checkpoint as a stage-1b adapter/prototype retrieval checkpoint and lists which modules are trained, but that is not enough to characterize its training data.[^tianmu-emb-uni-8b-card]

## Reported benchmarks

The model card reports evaluation on a 190-task MMEB-V3 setting: 37 image tasks including MCMR, 18 video, 24 visual-document, 11 audio, 53 text, and 47 agent tasks. Metrics differ by group, so the reported all-task aggregate combines mixed primary metrics. These are author-reported results without an independent reproduction in the local source.[^tianmu-emb-uni-8b-card]

| Modality | Tasks | Primary metric | Score |
|---|---:|---|---:|
| Image | 37 | hit@1 | 73.83 |
| Video | 18 | hit@1 | 59.37 |
| Visual document | 24 | ndcg_linear@5 | 72.03 |
| Audio | 11 | hit@1 | 38.94 |
| Text | 53 | ndcg_linear@5 | 43.62 |
| Agent | 47 | hit@1 | 39.42 |
| **All** | **190** | mixed primary metrics | **53.27** |

The card identifies the evaluated checkpoint and evaluation script but gives no comparator table, confidence intervals, or per-task results. It therefore supports reporting these scores, not a benchmark-leadership claim.[^tianmu-emb-uni-8b-card]

## Contradictions

- The model card reports an all-task MMEB-V3 score of **53.27** over 190 tasks.[^tianmu-emb-uni-8b-card] The separate [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) reports Tianmu-Emb-Uni at **52.83 Overall** and **40.50 Overall-V3**, with matching Audio (**38.94**) and Agent (**39.42**) but a different Text value (**41.77** rather than **43.62**).[^mmeb-v3-ranking] The ranking artifact does not define its metrics or task composition, so the discrepancy cannot be resolved from the persisted evidence.

## Relationships

- **Uses:** [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) as its vision-language embedding backbone.
- **Evaluated in:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md), subject to the score discrepancy above.

[^tianmu-emb-uni-8b-card]: [Tianmu-Emb-Uni-8B model card](../raw/Tianmu-Emb-Uni-8B.md). Architecture, language, release, and benchmark claims are author-reported; its remote image was not needed to cover the requested fields.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This unauthenticated snapshot does not define its metric semantics or evaluation configuration.
