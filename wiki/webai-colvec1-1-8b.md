---
type: Concept
title: webAI-ColVec1.1-8b
description: An 8.40B-parameter Qwen3.5-based multilingual visual-document retriever producing 640-dimensional token embeddings for ColBERT-style MaxSim late interaction.
tags: [embedding, visual-document-retrieval, late-interaction, multimodal, multilingual, qwen, webai]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:08:42Z }
sources:
  - id: webai-colvec1-1-8b-card
    resource: ../raw/webAI-ColVec1.1-8b.md
    title: webAI-ColVec1.1-8b model card
---

# webAI-ColVec1.1-8b

webAI-ColVec1.1-8b is an 8.40B-parameter multimodal embedding model for retrieving document images or rendered PDF pages from text queries. Based on Qwen3.5-9B, it uses one unified encoder to produce L2-normalized, 640-dimensional token vectors and ranks query-document pairs through ColBERT-style MaxSim late interaction.[^webai-colvec1-1-8b-card]

## Benchmarks

On the model card's ViDoRe V3 comparison, webAI-ColVec1.1-8b reports **64.95 final mean**, **65.32 public mean**, and **63.47 private mean** in percentage-form nDCG@10. It ranks first among the eight supplied models by final mean, ahead of VultronRetriever Prime at 64.26 and the 4B webAI-ColVec1.1 sibling at 63.90.[^webai-colvec1-1-8b-card]

| ViDoRe V3 task | nDCG@10 |
|---|---:|
| Computer Science | 80.08 |
| Energy | 70.12 |
| Finance, English | 71.90 |
| Finance, French | 54.87 |
| HR | 68.55 |
| Industrial | 57.65 |
| Nuclear | 53.66 |
| Pharmaceuticals | 67.88 |
| Physics | 51.50 |
| Telecom | 73.29 |

Each task score is the mean of six language subsets. The final mean is the unweighted mean over all ten tasks; the public mean covers eight tasks and the private mean covers Nuclear and Telecom. The reported run used BF16 encoding, SDPA, a 1,792-token visual budget, batch size 32, and CPU FP32 MaxSim scoring. Comparator values were copied from the live ViDoRe V3 MTEB leaderboard on July 31, 2026, whereas this model's values came from submitted MTEB artifacts, so ranks are time-bound and the results were not independently reproduced here.[^webai-colvec1-1-8b-card]

## Model size and architecture

- **Released parameters:** 8,395,317,104 (about 8.40B); the released BF16 checkpoint removes the unused language-model head, explaining the difference from the Qwen3.5-9B backbone label.[^webai-colvec1-1-8b-card]
- **Backbone:** Qwen3.5-9B vision-language model, whose hybrid stack combines full-attention and GatedDeltaNet linear-attention layers.[^webai-colvec1-1-8b-card]
- **Retrieval design:** the same encoder processes text queries and document images, producing one L2-normalized 640-dimensional vector per token. MaxSim aggregates token-level similarities for late-interaction retrieval.[^webai-colvec1-1-8b-card]
- **Attention:** the full-attention layers operate bidirectionally for retrieval. SDPA, FlashAttention 2, and FlashAttention 3 are interchangeable execution kernels and do not change that attention mode.[^webai-colvec1-1-8b-card]
- **Projection:** a learned 640-dimensional linear head without an activation function.[^webai-colvec1-1-8b-card]
- **Adaptation:** training used LoRA adapters plus a fully trained projection layer; the adapters were merged into the released weights.[^webai-colvec1-1-8b-card]
- **Document granularity:** the released processor allows 1,792 visual tokens per image by default; lowering this budget reduces memory but can alter retrieval scores.[^webai-colvec1-1-8b-card]

## Language support

The model card labels the model and its curated training mixture **multilingual** and reports each ViDoRe V3 task as an average over six language subsets. It does not name those six languages or provide a complete supported-language list. English and French appear explicitly as finance task labels, but this alone does not establish the boundaries or proficiency of language support. The card's claim of strong non-English performance therefore remains broad and author-reported.[^webai-colvec1-1-8b-card]

## Training data

The model card reports training on a curated **750,000-sample subset**, plus synthetically generated data. It describes the source subsets as filtered, balanced, and multilingual, but does not disclose per-dataset counts, language proportions, filtering criteria, balancing procedure, deduplication, or the amount and generation method of the additional synthetic data.[^webai-colvec1-1-8b-card]

The six named public sources are:

- `vidore/colpali_train_set`
- `Tevatron/docmatix-ir`
- `openbmb/VisRAG-Ret-Train-In-domain-data`
- `openbmb/VisRAG-Ret-Train-Synthetic-data`
- `llamaindex/vdr-multilingual-train`
- `Tevatron/wiki-ss-nq`

[^webai-colvec1-1-8b-card]: [webAI-ColVec1.1-8b model card](../raw/webAI-ColVec1.1-8b.md). Model specifications, training data, language claims, and benchmark results are author-reported. Linked datasets, submitted MTEB artifacts, the live leaderboard, base-model documentation, and external license were not inspected. The referenced local `evaluation-requirements-cu128.txt` attachment was not present, so the pinned evaluation environment could not be checked against the card.
