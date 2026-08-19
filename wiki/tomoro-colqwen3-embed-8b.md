---
type: Concept
title: Tomoro ColQwen3 Embed 8B
description: An 8B-class Qwen3-VL-based multilingual multimodal late-interaction retriever with 320-dimensional token embeddings and self-reported ViDoRe and video-retrieval results.
tags: [embedding, retrieval, multimodal, multilingual, late-interaction, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:06:30Z }
sources:
  - id: tomoro-colqwen3-8b-card
    resource: ../raw/tomoro-colqwen3-embed-8b.md
    title: TomoroAI/tomoro-colqwen3-embed-8b model card
---

# Tomoro ColQwen3 Embed 8B

Tomoro ColQwen3 Embed 8B is a multilingual multimodal embedding model for retrieving visual documents and short videos from text. It merges Qwen3-VL-8B-Instruct with Qwen3-Embedding-8B, preserves the vision stack, and produces L2-normalized 320-dimensional token vectors scored through ColPali-style MaxSim late interaction. Its model card reports leading aggregate results within its listed comparison set on ViDoRe V2 and V3, while its video capability transfers from image-text training rather than dedicated video-text fine-tuning.[^tomoro-colqwen3-8b-card]

## Model size and architecture

- **Size:** The model name and both merged base checkpoints identify it as 8B-class, but the card does not state an exact parameter count for the merged model.[^tomoro-colqwen3-8b-card]
- **Base models:** `Qwen/Qwen3-VL-8B-Instruct` merged with `Qwen/Qwen3-Embedding-8B`; the resulting Qwen3-VL 8B model is described as an encoder-only variant with its full vision stack preserved.[^tomoro-colqwen3-8b-card]
- **Retrieval design:** ColPali-style multi-vector late interaction. A custom projection head maps each text or visual token to a 320-dimensional L2-normalized vector, and retrieval uses MaxSim scoring.[^tomoro-colqwen3-8b-card]
- **Inputs:** Text queries, RGB images and rendered documents, plus short videos processed through the vision stack. The budget is up to 1,280 visual tokens per page or 5,120 per video.[^tomoro-colqwen3-8b-card]
- **Context and precision:** 32K inherited context, typically under 2K tokens in use; BF16 weights with FlashAttention 2 support.[^tomoro-colqwen3-8b-card]
- **Storage claim:** The card estimates about 0.82 TB per million images at 1,280 tokens × 320 dimensions, versus about 10.3 TB for a Nemo-3B baseline at 1,802 × 3,072, describing the footprint as 13× smaller. This is an author estimate, not an independently reproduced measurement.[^tomoro-colqwen3-8b-card]

## Language support

The card labels the model multilingual and evaluates separate multilingual ViDoRe V2 and V3 splits, but does not enumerate supported languages or state a language count. The V3 table labeled “English” includes a `FinanceFr` subset, so those table headings do not establish a definitive supported-language inventory.[^tomoro-colqwen3-8b-card]

## Training data

The model was fine-tuned on a curated image-text retrieval mixture containing:[^tomoro-colqwen3-8b-card]

- `vdr-multilingual-train`
- `vidore/colpali_train_set`
- `openbmb/VisRAG-Ret-Train-Synthetic-data`
- `openbmb/VisRAG-Ret-Train-In-domain-data`

The card provides no sample counts, language distribution, mixture weights, filtering details, epochs, or optimization settings. Its license-and-data summary additionally mentions “ViDoRe/MTEB corpora” without identifying an MTEB dataset beyond the four named resources. It explicitly says the Tomoro models use image-text data and receive no video-text fine-tuning.[^tomoro-colqwen3-8b-card]

## Reported benchmarks

All results are model-card-authored and were not independently reproduced here.[^tomoro-colqwen3-8b-card]

| Benchmark | Metric | Tomoro 8B result | Comparison stated by supplied table |
|---|---|---:|---|
| ViDoRe V3 English | Avg nDCG@5 | 0.6113 | Highest aggregate among the five listed models; ColNomic 7B leads CompSci and Tomoro 4B leads Industrial |
| ViDoRe V3 multilingual, excluding English subsets | Avg nDCG@5 | 0.5866 | Highest aggregate among the five listed models; ColNomic 7B leads CompSci |
| ViDoRe V2 English | Avg nDCG@5 | 0.6772 | Highest aggregate among the five listed models; Nemo-3B leads Economics |
| ViDoRe V2 multilingual | Avg nDCG@5 | 0.6085 | Highest aggregate by 0.0005 over Tomoro 4B; Tomoro 4B leads BioMed and ESG Reports |
| ViDoRe V1 English | Avg nDCG@5 | 0.9076 | Below Nemo-3B (0.9100), above Tomoro 4B (0.9057), Jina v4, and ColNomic 7B |
| CareBench text-to-video | Recall@1 / @5 / @10 | 0.867 / 0.959 / 0.985 | Leads Tomoro 4B and Care7B at R@1 and R@5; Care7B leads at R@10 |
| MMEB-V2 `video_ret` | Avg Hit@1 | 51.2 | Below Tomoro 4B and IFM-TTE-7B (51.7) and Seed-1.6 (51.3) |

The tables support competitive performance and aggregate leadership in the listed ViDoRe V2–V3 comparisons, not universal state of the art: the model does not lead every subset, and its ViDoRe V1 aggregate trails Nemo-3B. Video comparisons also mix training regimes because IFM-TTE-7B and Seed-1.6 use video-text fine-tuning whereas Tomoro 8B does not.[^tomoro-colqwen3-8b-card]

## Relationships

- **Built from:** [Qwen3-Embedding-8B](qwen3-embedding-8b.md), merged with Qwen3-VL-8B-Instruct to add text-retrieval capability while retaining vision processing.
- **Larger variant of:** [Tomoro ColQwen3 Embed 4B](tomoro-colqwen3-embed-4b.md), sharing the retrieval architecture, embedding width, training-data description, and benchmark suite.

[^tomoro-colqwen3-8b-card]: [TomoroAI/tomoro-colqwen3-embed-8b model card](../raw/tomoro-colqwen3-embed-8b.md). Architecture, training, storage, language, and benchmark claims are self-reported; the source contains no local attachments requiring separate inspection.
