---
type: Concept
title: Tomoro ColQwen3 Embed 4B
description: A 4B-class Qwen3-VL-based multilingual multimodal late-interaction retriever with 320-dimensional token embeddings and reported ViDoRe and video-retrieval results.
tags: [embedding, retrieval, multimodal, multilingual, late-interaction, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:05:16Z }
sources:
  - id: tomoro-colqwen3-4b-card
    resource: ../raw/tomoro-colqwen3-embed-4b.md
    title: TomoroAI/tomoro-colqwen3-embed-4b model card
---

# Tomoro ColQwen3 Embed 4B

Tomoro ColQwen3 Embed 4B is a multilingual multimodal embedding model for retrieving visual documents and short videos from text. It combines Qwen3-VL-4B-Instruct with Qwen3-Embedding-4B, retains the vision stack, and produces L2-normalized 320-dimensional token vectors scored through ColPali-style MaxSim late interaction. Its model card reports competitive or leading ViDoRe V2–V3 results among the compared models, while its video ability is transfer from image-text training rather than dedicated video fine-tuning.[^tomoro-colqwen3-4b-card]

## Model size and architecture

- **Size:** The name and both merged base checkpoints identify the model as 4B-class, but the card does not state an exact parameter count for the merged model.[^tomoro-colqwen3-4b-card]
- **Base models:** `Qwen/Qwen3-VL-4B-Instruct` merged with `Qwen/Qwen3-Embedding-4B`; the resulting Qwen3-VL 4B model is described as an encoder-only variant with its full vision stack preserved.[^tomoro-colqwen3-4b-card]
- **Retrieval design:** ColPali-style multi-vector late interaction. Every text or visual token is projected through a custom 320-dimensional head, L2-normalized, and compared with MaxSim scoring.[^tomoro-colqwen3-4b-card]
- **Inputs:** text queries, RGB images and rendered documents, plus short videos processed frame-wise. The budget is up to 1,280 visual tokens per page or 5,120 per video.[^tomoro-colqwen3-4b-card]
- **Context and precision:** 32K inherited context, typically under 2K tokens in use; BF16 weights with FlashAttention 2 support.[^tomoro-colqwen3-4b-card]
- **Storage claim:** The card estimates about 0.82 TB per million images at 1,280 tokens × 320 dimensions, versus about 10.3 TB for its NVIDIA Nemo-3B baseline at 1,802 × 3,072, characterizing this as a 13× reduction. This is an author estimate, not an independently reproduced measurement.[^tomoro-colqwen3-4b-card]

## Language support

The card labels the model multilingual and reports separate multilingual ViDoRe V2 and V3 evaluations, but does not enumerate supported languages or provide a claimed language count. The V3 English table nevertheless includes a `FinanceFr` subset, so the table labels should not be interpreted as a definitive modality-language inventory.[^tomoro-colqwen3-4b-card]

## Training data

The model was fine-tuned on a curated image-text retrieval mixture containing:[^tomoro-colqwen3-4b-card]

- `vdr-multilingual-train`
- `vidore/colpali_train_set`
- `openbmb/VisRAG-Ret-Train-Synthetic-data`
- `openbmb/VisRAG-Ret-Train-In-domain-data`

The card gives no sample counts, language distribution, mixture weights, filtering details, epochs, or optimization procedure. A later summary broadly says training includes “ViDoRe/MTEB corpora,” but names no MTEB dataset beyond the four-item list above. It explicitly says the Tomoro ColQwen models used only image-text data and did not receive video-text fine-tuning.[^tomoro-colqwen3-4b-card]

## Reported benchmarks

All results below are model-card-authored and were not independently reproduced here.[^tomoro-colqwen3-4b-card]

| Benchmark | Metric | Tomoro 4B result | Comparison stated by supplied table |
|---|---|---:|---|
| ViDoRe V3 English | Avg nDCG@5 | 0.5934 | Second to Tomoro 8B (0.6113); above Nemo-3B (0.5769), Jina v4 (0.5680), and ColNomic 7B (0.5651) |
| ViDoRe V3 multilingual, excluding English subsets | Avg nDCG@5 | 0.5708 | Second to Tomoro 8B (0.5866); above the other three listed baselines |
| ViDoRe V2 English | Avg nDCG@5 | 0.6598 | Below Nemo-3B (0.6676) and Tomoro 8B (0.6772); above Jina v4 and ColNomic 7B |
| ViDoRe V2 multilingual | Avg nDCG@5 | 0.6080 | Slightly below Tomoro 8B (0.6085) and above the other listed baselines |
| ViDoRe V1 English | Avg nDCG@5 | 0.9057 | Below Nemo-3B (0.9100) and Tomoro 8B (0.9076); above Jina v4 and ColNomic 7B |
| CareBench text-to-video | Recall@1 / @5 / @10 | 0.862 / 0.957 / 0.980 | Better than Care7B at R@1, nearly tied at R@5, lower at R@10 |
| MMEB-V2 `video_ret` | Avg Hit@1 | 51.7 | Tied IFM-TTE-7B and above Seed-1.6 (51.3) in the supplied table |

The strongest broad claim supported by these tables is competitive ViDoRe performance, especially on V2 multilingual and V3. The source's “state of the art” wording requires qualification: its own tables show the 4B model does not lead every aggregate, and its V1 average trails Nemo-3B. Video comparisons also differ in training regime because IFM-TTE-7B and Seed-1.6 use video-text fine-tuning while this model does not.[^tomoro-colqwen3-4b-card]

## Relationships

- **Built from:** [Qwen3-Embedding-4B](qwen3-embedding-4b.md), merged with Qwen3-VL-4B-Instruct to add strong text retrieval while retaining vision processing.

[^tomoro-colqwen3-4b-card]: [TomoroAI/tomoro-colqwen3-embed-4b model card](../raw/tomoro-colqwen3-embed-4b.md). Architecture, training, storage, language, and benchmark claims are self-reported; the source contains no local attachments requiring separate inspection.
