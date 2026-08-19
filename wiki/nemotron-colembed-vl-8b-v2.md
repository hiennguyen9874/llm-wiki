---
type: Concept
title: Nemotron-ColEmbed-VL-8B-v2
description: An approximately 8.8B-parameter Qwen3-VL-based multilingual visual-document retriever producing 4,096-dimensional token embeddings for ColBERT-style late interaction.
tags: [embedding, visual-document-retrieval, late-interaction, multimodal, multilingual, qwen, nemotron, nvidia]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:02:54Z }
sources:
  - id: nemotron-colembed-vl-8b-v2-card
    resource: ../raw/nemotron-colembed-vl-8b-v2.md
    title: Nemotron ColEmbed VL 8B v2 model card
---

# Nemotron-ColEmbed-VL-8B-v2

Nemotron-ColEmbed-VL-8B-v2 is NVIDIA's multimodal late-interaction embedding model for retrieving page images from text queries. It is an approximately 8.8B-parameter Qwen3-VL-8B-Instruct-based transformer that emits one 4,096-dimensional vector per input token for ColBERT-style multi-vector scoring. [^nemotron-colembed-vl-8b-v2-card]

## Benchmarks

The model card reports these average visual-document retrieval results. ViDoRe V1 and V2 use nDCG@5, while V3 uses nDCG@10. [^nemotron-colembed-vl-8b-v2-card]

| Benchmark | Average | Position within supplied table |
|---|---:|---:|
| ViDoRe V1 | **92.65** | 1st of 7 |
| ViDoRe V2 | 65.16 | 3rd of 7 |
| ViDoRe V3 | **63.54** | 1st of 7 |

For ViDoRe V3's eight tasks, the card reports 79.30 Computer Science, 69.82 Energy, 67.29 English Finance, 51.54 French Finance, 66.32 HR, 56.03 Industrial, 67.19 Pharma, and 50.84 Physics. It claims the model ranked first on the overall ViDoRe V3 leaderboard as of January 26, 2026. This is a time-bound model-card claim, and none of the results were independently reproduced here. The card also notes that MTEB leaderboard rank is based on Borda points across tasks, rather than solely on the displayed average metric. [^nemotron-colembed-vl-8b-v2-card]

## Model size and architecture

- **Reported size:** approximately 8.8B parameters; the “8B” name understates the model card's total parameter estimate. [^nemotron-colembed-vl-8b-v2-card]
- **Backbone:** `Qwen3-VL-8B-Instruct`-based transformer encoder. Its three modules are a vision encoder—defaulting to a SigLIP2-SO-400M variant—an MLP vision-language merger, and an LLM. [^nemotron-colembed-vl-8b-v2-card]
- **Retrieval design:** text queries and page-image documents are encoded as ColBERT-style multi-vector representations for late-interaction scoring. [^nemotron-colembed-vl-8b-v2-card]
- **Output:** a 4,096-dimensional floating-point embedding per input token. [^nemotron-colembed-vl-8b-v2-card]
- **Evaluated input limits:** up to 10,240 tokens; images are resized into 512×512 tiles, with tested settings of at most eight tiles plus one thumbnail and 256 tokens per tile. [^nemotron-colembed-vl-8b-v2-card]
- **v2 construction:** post-training model merging combines multiple fine-tuned checkpoints; the card says this aims for ensemble-like accuracy stability without additional inference latency. [^nemotron-colembed-vl-8b-v2-card]

## Language support

The card labels the model **multilingual** and attributes improved cross-language semantic alignment to a training mixture enriched with multilingual synthetic data. It does not enumerate supported languages, define proficiency levels, or report broad language-level results. The ViDoRe V3 table separately includes English- and French-finance tasks, but those two tasks do not establish comprehensive support for either language or any wider language set. [^nemotron-colembed-vl-8b-v2-card]

## Training data

The card reports vision fine-tuning on approximately **500,000 image samples**, with fewer than one million images overall, using hybrid automated, human, and synthetic collection and labeling. Named public datasets are: [^nemotron-colembed-vl-8b-v2-card]

- DocMatix-IR
- VDR multilingual training
- ViDoRe ColPali training
- VisRAG retrieval synthetic data
- VisRAG retrieval in-domain data
- Wiki-SS-NQ

The training mixture was enriched with diverse multilingual synthetic data for cross-language alignment and complex document types. The source does not disclose dataset mixture proportions, language distribution, synthetic-data generation procedures, filtering or deduplication details, or whether the approximately 500K count includes every listed source. [^nemotron-colembed-vl-8b-v2-card]

[^nemotron-colembed-vl-8b-v2-card]: [Nemotron ColEmbed VL 8B v2 model card](../raw/nemotron-colembed-vl-8b-v2.md). Architecture, data, language, and benchmark statements are reported by the model card; its externally linked paper, datasets, evaluation code, and live leaderboards were not inspected. The card's referenced local example notebook and license file were not present alongside the supplied raw source.
