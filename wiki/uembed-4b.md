---
type: Concept
title: UEmbed-4B
description: A 4B-parameter Qwen3.5-based decoder-only multimodal embedding model producing dense and SPLADE-style sparse vectors, with reported MMEB-v3 results.
tags: [embedding, retrieval, multimodal, dense-retrieval, sparse-retrieval, splade, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T09:58:08Z }
sources:
  - id: uembed-4b-card
    resource: ../raw/UEmbed-4B.md
    title: UEmbed-4B model card
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
---

# UEmbed-4B

UEmbed-4B is a 4B-parameter, decoder-only multimodal embedding model built on Qwen3.5. A single causal forward pass produces both normalized dense embeddings and interpretable SPLADE-style sparse lexical embeddings for text, image, video, and mixed-modal retrieval. Its model card reports state-of-the-art results on MMEB-v3's text and agent tracks for the UEmbed family, but does not provide model-specific benchmark tables or establish that the 4B variant itself leads those tracks.[^uembed-4b-card]

## Model size and architecture

- **Parameters:** 4B.[^uembed-4b-card]
- **Backbone:** decoder-only Qwen3.5 multimodal model; the sparse design retains causal serving compatibility rather than converting the backbone into a bidirectional encoder.[^uembed-4b-card]
- **Inputs:** text, images, videos, and mixed-modal combinations represented in a shared retrieval space.[^uembed-4b-card]
- **Dense output:** the hidden state of the EOS token immediately before the appended sparse special tokens, returned as a normalized dense vector. The card does not state its dimensionality.[^uembed-4b-card]
- **Sparse output:** 16 appended special tokens, each with a subset-specific linear head. Their outputs cover a canonical sparse vocabulary compressed from 248,320 tokenizer entries to 184,016 entries, using `log(1 + ReLU(logits))` activation.[^uembed-4b-card]
- **Objective:** dense InfoNCE plus sparse InfoNCE, with query and document FLOPS regularization.[^uembed-4b-card]

## Language support

The model card does not state which languages UEmbed-4B supports, how many languages occur in training, or whether performance was evaluated by language. Its use of E5, MLDR, MMEB, and a Qwen3.5 backbone may imply multilingual exposure, but the supplied evidence is insufficient for a specific multilingual-support claim.[^uembed-4b-card]

## Training data

UEmbed was trained on 3.94 million public samples drawn from E5 training data for broad text retrieval, the MLDR subset of M3 training data, and MMEB training sets containing multimodal query-document pairs. For multimodal examples, hard negatives were mined using Qwen3-VL-Embedding-8B as the teacher retriever. The card does not report the allocation among datasets, language or modality distribution, filtering and deduplication procedures, or whether all family sizes used exactly the same mixture.[^uembed-4b-card]

## Reported benchmarks

The model card announces that UEmbed achieved state-of-the-art results on MMEB-v3's text and agent tracks and ranked behind only the Qwen3-VL-Embedding series among open-source models on MMEB-v2. These are family-level, author-reported claims without tables in the supplied card, so they do not establish UEmbed-4B's exact MMEB-v2 scores or rank.[^uembed-4b-card]

A separate local [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) reports the following UEmbed-4B entries:[^mmeb-v3-ranking]

| Output mode | Reported rank | Overall | Overall-V3 | Text | Audio | Agent |
|---|---:|---:|---:|---:|---:|---:|
| Dense | 6 | 50.10 | 35.86 | 42.00 | 0.00 | 37.33 |
| Sparse | 7 | 49.98 | 36.12 | 41.92 | 0.00 | 38.04 |

Within that snapshot, sparse output is slightly higher on Overall-V3 and Agent, while dense output is slightly higher on Overall and Text. The artifact does not define metrics, evaluation configuration, or whether zero Audio means missing evaluation or measured zero; these values support only comparisons within the supplied snapshot and are not independently verified.[^mmeb-v3-ranking]

[^uembed-4b-card]: [UEmbed-4B model card](../raw/UEmbed-4B.md). Model size, architecture, data, and benchmark claims are author-reported. The card links a paper, website, and repository, but those remote resources were not persisted or inspected for this ingest.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This supplied ranking artifact does not document metric definitions or evaluation provenance; values are reproduced as reported.
