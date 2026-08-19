---
type: Concept
title: Llama-Nemotron-ColEmbed-VL-3B-v2
description: An approximately 4.4B-parameter SigLIP2-and-Llama-3.2-based multilingual visual-document retriever producing 3,072-dimensional token embeddings for ColBERT-style late interaction.
tags: [embedding, visual-document-retrieval, late-interaction, multimodal, multilingual, llama, nemotron, nvidia]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:01:55Z }
sources:
  - id: llama-nemotron-colembed-vl-3b-v2-card
    resource: ../raw/llama-nemotron-colembed-vl-3b-v2.md
    title: Llama-Nemotron-ColEmbed-VL-3B-v2 model card
---

# Llama-Nemotron-ColEmbed-VL-3B-v2

Llama-Nemotron-ColEmbed-VL-3B-v2 is NVIDIA's multimodal late-interaction embedding model for retrieving page images from text queries. Despite the 3B name, the model card reports approximately 4.4B parameters because the system combines a SigLIP2 vision encoder with a Llama 3.2 3B language backbone; it emits one 3,072-dimensional vector per input token for ColBERT-style multi-vector scoring. [^llama-nemotron-colembed-vl-3b-v2-card]

## Benchmarks

The model card reports the following retrieval accuracy against its 3B v1 predecessor. ViDoRe V1 and V2 use nDCG@5; ViDoRe V3 uses nDCG@10. [^llama-nemotron-colembed-vl-3b-v2-card]

| Benchmark | 3B v1 | 3B v2 | Absolute change |
|---|---:|---:|---:|
| ViDoRe V1 | 0.9100 | **0.9174** | +0.0074 |
| ViDoRe V2 | 0.6332 | **0.6338** | +0.0006 |
| ViDoRe V3 | 0.5707 | **0.5970** | +0.0263 |

These are model-card results, not independently reproduced here. The source identifies ViDoRe V1–V3 as page-level visual-document retrieval suites spanning multiple domains, languages, and settings, but provides no per-task or per-language breakdown. [^llama-nemotron-colembed-vl-3b-v2-card]

## Model size and architecture

- **Reported size:** approximately 4.4B parameters; “3B” refers to the Llama backbone rather than total system size. [^llama-nemotron-colembed-vl-3b-v2-card]
- **Backbones:** `google/siglip2-giant-opt-patch16-384` vision encoder plus `meta-llama/Llama-3.2-3B`, assembled as a transformer-based vision-language model. [^llama-nemotron-colembed-vl-3b-v2-card]
- **Retrieval design:** text queries and page-image documents are encoded as ColBERT-style multi-vector representations and compared through late interaction. [^llama-nemotron-colembed-vl-3b-v2-card]
- **Output:** a 3,072-dimensional floating-point embedding per input token. [^llama-nemotron-colembed-vl-3b-v2-card]
- **Evaluated input limits:** up to 10,240 tokens; images are tiled to 512×512, with tested settings of at most eight tiles plus one thumbnail and 256 tokens per tile. [^llama-nemotron-colembed-vl-3b-v2-card]
- **v2 construction:** multiple fine-tuned checkpoints were combined with post-training model merging, intended to retain ensemble-like accuracy stability without ensemble inference latency. [^llama-nemotron-colembed-vl-3b-v2-card]

## Language support

The card labels the model **multilingual** and says multilingual synthetic queries improve cross-lingual retrieval and semantic alignment across languages. It does not enumerate supported languages, define proficiency levels, or provide language-level benchmark scores, so support for any specific language cannot be established from this source. [^llama-nemotron-colembed-vl-3b-v2-card]

## Training data

The model was trained on both text and images using public datasets plus multilingual synthetic augmentation. The card reports: [^llama-nemotron-colembed-vl-3b-v2-card]

- **Text:** semi-supervised pre-training on 12M samples and fine-tuning on 1.5M samples.
- **Vision:** fine-tuning on approximately 500K image samples; the image-data-size field says fewer than one million images.
- **Collection and labeling:** hybrid automated, human, and synthetic methods.
- **Named datasets:** HotpotQA, MIRACL, Natural Questions, Stack Exchange, SQuAD, Tiger Math/Stack (`WebInstructSub`), DocMatix-IR, VDR multilingual training, ViDoRe ColPali training, VisRAG synthetic and in-domain retrieval training, and Wiki-SS-NQ.
- **Synthetic augmentation:** diverse multilingual queries targeting complex document layouts and cross-lingual retrieval scenarios within existing image data.

The source does not disclose mixture proportions by dataset, deduplication or filtering details, the languages or generation method of the synthetic queries, or whether its sample totals overlap. [^llama-nemotron-colembed-vl-3b-v2-card]

[^llama-nemotron-colembed-vl-3b-v2-card]: [Llama-Nemotron-ColEmbed-VL-3B-v2 model card](../raw/llama-nemotron-colembed-vl-3b-v2.md). Architecture, data, language, and benchmark statements are reported by the model card; externally linked paper, datasets, code, and live leaderboards were not inspected.
