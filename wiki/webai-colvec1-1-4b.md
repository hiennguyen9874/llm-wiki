---
type: Concept
title: webAI-ColVec1.1-4b
description: A 4.54B-parameter Qwen3.5-based multilingual visual-document retriever producing 640-dimensional token embeddings for ColBERT-style MaxSim late interaction.
tags: [embedding, visual-document-retrieval, late-interaction, multimodal, multilingual, qwen, webai]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:07:37Z }
sources:
  - id: webai-colvec1-1-4b-card
    resource: ../raw/webAI-ColVec1.1-4b.md
    title: webAI-ColVec1.1-4b model card
---

# webAI-ColVec1.1-4b

webAI-ColVec1.1-4b is a 4.54B-parameter multimodal embedding model for retrieving document images or rendered PDF pages from text queries. Based on Qwen3.5-4B, it uses one unified encoder to produce L2-normalized, 640-dimensional token vectors and ranks query-document pairs through ColBERT-style MaxSim late interaction.[^webai-colvec1-1-4b-card]

## Benchmarks

On the model card's ViDoRe V3 comparison, webAI-ColVec1.1-4b reports **63.90 final mean**, **64.24 public mean**, and **62.53 private mean** in percentage-form nDCG@10. It ranks third among the eight supplied models by final mean and first among the listed 4B/4.5B-class models, ahead of VultronRetriever Core at 63.57 and the prior webAI-ColVec1-4b at 62.22. The 8B webAI-ColVec1.1 model leads the table at 64.95.[^webai-colvec1-1-4b-card]

| ViDoRe V3 task | nDCG@10 |
|---|---:|
| Computer Science | 80.34 |
| Energy | 69.50 |
| Finance, English | 69.18 |
| Finance, French | 53.13 |
| HR | 66.90 |
| Industrial | 56.36 |
| Nuclear | 53.30 |
| Pharmaceuticals | 67.25 |
| Physics | 51.24 |
| Telecom | 71.76 |

Each task score is the mean of six language subsets. The final mean is the unweighted mean over all ten tasks; the public mean covers eight tasks and the private mean covers Nuclear and Telecom. The reported run used BF16 encoding, SDPA, a 1,792-token visual budget, batch size 32, and CPU FP32 MaxSim scoring. Comparator values were copied from the live ViDoRe V3 MTEB leaderboard on July 31, 2026, whereas this model's values came from submitted MTEB artifacts, so ranks are time-bound and the results were not independently reproduced here.[^webai-colvec1-1-4b-card]

## Model size and architecture

- **Released parameters:** 4,540,904,576 (about 4.54B); the released BF16 checkpoint removes the unused language-model head.[^webai-colvec1-1-4b-card]
- **Backbone:** Qwen3.5-4B vision-language model, whose hybrid stack combines full-attention and GatedDeltaNet linear-attention layers.[^webai-colvec1-1-4b-card]
- **Retrieval design:** the same encoder processes text queries and document images, producing one L2-normalized 640-dimensional vector per token. MaxSim aggregates token-level similarities for late-interaction retrieval.[^webai-colvec1-1-4b-card]
- **Attention:** the full-attention layers operate bidirectionally for retrieval. SDPA, FlashAttention 2, and FlashAttention 3 are interchangeable execution kernels and do not change that attention mode.[^webai-colvec1-1-4b-card]
- **Projection:** a learned 640-dimensional linear head without an activation function.[^webai-colvec1-1-4b-card]
- **Adaptation:** training used LoRA adapters plus a fully trained projection layer; the adapters were merged into the released weights.[^webai-colvec1-1-4b-card]
- **Document granularity:** the released processor allows 1,792 visual tokens per image by default; lowering this budget reduces memory but can alter retrieval scores.[^webai-colvec1-1-4b-card]

## Language support

The model card labels the model and its curated training mixture **multilingual** and reports each ViDoRe V3 task as an average over six language subsets. It does not name those six languages or provide a complete supported-language list. English and French appear explicitly as finance task labels, but this alone does not establish the boundaries or proficiency of language support. The card's claim of strong non-English performance therefore remains broad and author-reported.[^webai-colvec1-1-4b-card]

## Training data

The model card reports training on a curated **500,000-sample subset**, plus synthetically generated data. It describes the source subsets as filtered, balanced, and multilingual, but does not disclose per-dataset counts, language proportions, filtering criteria, balancing procedure, deduplication, or the amount and generation method of the additional synthetic data.[^webai-colvec1-1-4b-card]

The six named public sources are:

- `vidore/colpali_train_set`
- `Tevatron/docmatix-ir`
- `openbmb/VisRAG-Ret-Train-In-domain-data`
- `openbmb/VisRAG-Ret-Train-Synthetic-data`
- `llamaindex/vdr-multilingual-train`
- `Tevatron/wiki-ss-nq`

[^webai-colvec1-1-4b-card]: [webAI-ColVec1.1-4b model card](../raw/webAI-ColVec1.1-4b.md). Model specifications, training data, language claims, and benchmark results are author-reported. Linked datasets, submitted MTEB artifacts, the live leaderboard, base-model documentation, and external license were not inspected. The referenced local `evaluation-requirements-cu128.txt` attachment was not present, so the pinned evaluation environment could not be checked against the card.
