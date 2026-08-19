---
type: Concept
title: Jina Embeddings v5 Omni Nano
description: An approximately 1B-parameter multimodal embedding model with locked aligned modality towers, 768-dimensional last-token-pooled vectors, and text, image, video, and audio support.
tags: [embedding, retrieval, multimodal, multilingual, matryoshka, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T09:59:15Z }
sources:
  - id: jina-v5-omni-nano-card
    resource: ../raw/jina-embeddings-v5-omni-nano.md
    title: jina-embeddings-v5-omni-nano model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# Jina Embeddings v5 Omni Nano

Jina Embeddings v5 Omni Nano is an approximately 1B-parameter model that embeds text, images, video, and audio into a shared 768-dimensional space aligned with Jina Embeddings v5 Text Nano. It supports retrieval, classification, clustering, and text matching through task adapters, uses last-token pooling, and allows Matryoshka-style output truncation. [^jina-v5-omni-nano-card]

## Benchmarks

The model card claims that Omni Nano and Omni Small define the open-weight efficiency frontier by average score versus parameter count across MIEB-Lite for images, MMEB-V for video, and MAEB for audio. It supplies no numeric scores or per-benchmark results in the Markdown. Its referenced `omni_frontier.png` image is absent from `raw/`, and the linked external report was not supplied, so the exact results, evaluation setup, and comparison set cannot be audited from this artifact. [^jina-v5-omni-nano-card]

The local MTEB Multilingual v2 snapshot ranks Omni Nano **10th of 45**, with Mean (Task) **65.52** and Mean (TaskType) **57.66**. It reports bitext mining 67.70, classification 69.18, clustering 52.73, instruction reranking 0.05, multilabel classification 41.31, pair classification 81.94, reranking 64.63, retrieval 63.26, and STS 78.17. These equal the snapshot's Text Nano values; the artifact does not explain whether the omni model was evaluated independently or shares its text tower's submission. The snapshot is unauthenticated and omits evaluation protocol details. [^mteb-multilingual-v2-summary]

## Model size and architecture

- **Size:** the card reports approximately **1.04B parameters**. The local leaderboard instead records **0.986B total**, **0.887B active**, and 1,881 MB memory. [^jina-v5-omni-nano-card] [^mteb-multilingual-v2-summary]
- **Modality architecture:** separate vision and audio towers operate alongside a text encoder; unused towers can be omitted at load time. The model's title and citation describe these as “locked aligned towers,” and all modalities map into a text-aligned shared vector space. The referenced local architecture image is missing, so component identities, layer counts, fusion details, and projection topology are not established by the available artifact. [^jina-v5-omni-nano-card]
- **Task adaptation:** the base repository contains separate adapters for retrieval, classification, clustering, and text matching; pre-merged task variants are also available. [^jina-v5-omni-nano-card]
- **Output:** 768-dimensional, L2-normalized, last-token embeddings; dimensions can be truncated with re-normalization. [^jina-v5-omni-nano-card]
- **Input limits:** 8,192 tokens, with 256–1,280 vision tokens stated as configuration defaults. [^jina-v5-omni-nano-card]
- **Modalities:** text, image, video, and audio, including fused multimodal inputs. PDFs are accepted by rendering their pages as visual inputs. [^jina-v5-omni-nano-card]

## Language support

The model card labels Omni Nano “multilingual” but does not enumerate languages, state a language count, define support criteria, or provide per-language results. Because its shared space is aligned with the multilingual Jina Embeddings v5 Text Nano model, multilingual text compatibility is claimed, but the card does not establish whether speech, images, or video were trained or evaluated across particular languages. [^jina-v5-omni-nano-card]

## Training data and procedure

The supplied model card does not identify training datasets, sample counts, language or modality distributions, licenses, filtering, deduplication, synthetic-data use, or contamination controls. It establishes text-space alignment and task-specific adapters but does not describe the training stages or losses. The local leaderboard independently marks training data and training code as unavailable. Consequently, training-data composition and reproducibility are not established by the available sources. [^jina-v5-omni-nano-card] [^mteb-multilingual-v2-summary]

## Contradictions

The model card's approximate **1.04B** parameter count differs from the leaderboard's **0.986B total** count. This may reflect rounding or different counting conventions, but neither source explains the discrepancy. [^jina-v5-omni-nano-card] [^mteb-multilingual-v2-summary]

## Relationships

- **Aligned with:** [Jina Embeddings v5 Text Nano](jina-embeddings-v5-text-nano.md); their vectors share a space, allowing text indexed with Text Nano to be queried using Omni Nano media embeddings without reindexing. [^jina-v5-omni-nano-card]
- **Evaluated in:** [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md). [^mteb-multilingual-v2-summary]

[^jina-v5-omni-nano-card]: [jina-embeddings-v5-omni-nano model card](../raw/jina-embeddings-v5-omni-nano.md). Model, architecture, language, benchmark, and training-coverage statements are reported by the card. Its referenced local benchmark and architecture images are missing, and its external technical report was not supplied.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied, unauthenticated leaderboard metadata and scores; the artifact does not document its evaluation protocol.
