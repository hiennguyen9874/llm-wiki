---
type: Concept
title: UEmbed-4B
description: A 4B-parameter Qwen3.5-based decoder-only multimodal embedding model producing dense and SPLADE-style sparse vectors, with reported MMEB-v3 results.
tags: [embedding, retrieval, multimodal, dense-retrieval, sparse-retrieval, splade, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:30:37Z }
sources:
  - id: uembed-tech-report
    resource: ../raw/2608.02583_UEmbed/main.tex
    title: UEmbed technical-report LaTeX source
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

The paper describes 3.94 million public samples: 1.55M text, 1.07M image, 0.84M video, and 0.48M visual-document examples. It names Echo-embedding, MLDR from M3-Embedding, and MMEB training sets; for multimodal examples, it uses Qwen3-VL-Embedding-8B to mine hard negatives.[^uembed-tech-report]

## Contradictions

- The model card calls the broad text source “E5 training data,” while the technical report calls it “Echo-embedding training data.” Both agree on 3.94M public samples, MLDR/M3, MMEB data, and Qwen3-VL-Embedding-8B hard-negative mining, but the supplied sources do not explain the naming difference.[^uembed-4b-card][^uembed-tech-report]

## Reported benchmarks

The technical report supplies model-specific MMEB-v2 scores: UEmbed-4B reports 70.4 dense and 69.7 sparse overall across 78 datasets. Its dense/sparse scores are 71.4/70.6 for Image, 57.0/56.0 for Video, and 78.8/78.6 for VisDoc. These are author-reported results; the paper's comparison table excludes Qwen3-VL-Embedding from bolded best-score selection because it is described as trained on large-scale proprietary data.[^uembed-tech-report]

On nine BEIR datasets, UEmbed-4B reports mean nDCG@10 of 56.0 dense and 53.6 sparse. On BrowseComp-Plus, it reports dense/sparse accuracy of 51.57%/45.54%, recall of 61.03%/60.10%, and average search rounds of 38.47/31.85; this supports a trade-off between accuracy and search rounds rather than an unconditional sparse advantage.[^uembed-tech-report]

The model card separately announces family-level state-of-the-art results on MMEB-v3's text and agent tracks and a ranking behind only Qwen3-VL-Embedding among open-source models on MMEB-v2. Those broader statements remain author-reported.[^uembed-4b-card]

A separate local [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) reports the following UEmbed-4B entries:[^mmeb-v3-ranking]

| Output mode | Reported rank | Overall | Overall-V3 | Text | Audio | Agent |
|---|---:|---:|---:|---:|---:|---:|
| Dense | 6 | 50.10 | 35.86 | 42.00 | 0.00 | 37.33 |
| Sparse | 7 | 49.98 | 36.12 | 41.92 | 0.00 | 38.04 |

Within that snapshot, sparse output is slightly higher on Overall-V3 and Agent, while dense output is slightly higher on Overall and Text. The artifact does not define metrics, evaluation configuration, or whether zero Audio means missing evaluation or measured zero; these values support only comparisons within the supplied snapshot and are not independently verified.[^mmeb-v3-ranking]

## Relationships

- **Variant of:** [UEmbed](uembed.md).

[^uembed-tech-report]: [UEmbed technical-report LaTeX source](../raw/2608.02583_UEmbed/main.tex). Architecture, training, and evaluation results are author-reported; tables and relevant chart attachments were inspected, but no independent reproduction was available.
[^uembed-4b-card]: [UEmbed-4B model card](../raw/UEmbed-4B.md). Model-card claims are author-reported.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This supplied ranking artifact does not document metric definitions or evaluation provenance; values are reproduced as reported.
