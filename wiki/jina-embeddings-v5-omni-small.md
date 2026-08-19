---
type: Concept
title: Jina Embeddings v5 Omni Small
description: A reported 1.74B-parameter multimodal embedding model with locked aligned modality towers, 1,024-dimensional last-token-pooled vectors, and text, image, video, and audio support.
tags: [embedding, retrieval, multimodal, multilingual, matryoshka, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:00:46Z }
sources:
  - id: jina-v5-omni-small-card
    resource: ../raw/jina-embeddings-v5-omni-small.md
    title: jina-embeddings-v5-omni-small model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# Jina Embeddings v5 Omni Small

Jina Embeddings v5 Omni Small embeds text, images, video, and audio into a shared 1,024-dimensional space aligned with Jina Embeddings v5 Text Small. The card reports approximately 1.74B parameters, a 32,768-token limit, last-token pooling, Matryoshka truncation, and adapters for retrieval, classification, clustering, and text matching. [^jina-v5-omni-small-card]

## Benchmarks

The model card claims that Omni Small and Omni Nano define the open-weight efficiency frontier by average score versus parameter count across MIEB-Lite for images, MMEB-V for video, and MAEB for audio. It provides no numeric results in the Markdown. Its referenced `omni_frontier.png` is absent from `raw/`, and the linked external report was not supplied, so the exact results, evaluation setup, and comparison set cannot be audited from this artifact. [^jina-v5-omni-small-card]

The local MTEB Multilingual v2 snapshot ranks Omni Small **4th of 45**, with Mean (Task) **67.00** and Mean (TaskType) **58.90**. It reports bitext mining 69.71, classification 71.32, clustering 53.41, instruction reranking 1.35, multilabel classification 41.97, pair classification 82.93, reranking 65.66, retrieval 64.88, and STS 78.85. These equal the snapshot's Text Small values; the artifact does not explain whether the omni model was evaluated independently or shares its text tower's submission. The snapshot is unauthenticated and omits evaluation protocol details. [^mteb-multilingual-v2-summary]

## Model size and architecture

- **Size:** the model card reports approximately **1.74B parameters**. The local leaderboard instead records **1.626B total**, **1.471B active**, and 3,102 MB memory. [^jina-v5-omni-small-card] [^mteb-multilingual-v2-summary]
- **Modality architecture:** separate vision and audio towers operate alongside a text encoder; unused towers can be omitted at load time. The model citation describes “locked aligned towers,” with every modality mapped into a text-aligned shared vector space. The referenced `architecture.png` is not available beside this source, so component identities, layer counts, fusion details, and projection topology are not established by the supplied artifact. [^jina-v5-omni-small-card]
- **Task adaptation:** the base repository contains separate adapters for retrieval, classification, clustering, and text matching; pre-merged task variants are also offered. [^jina-v5-omni-small-card]
- **Output:** 1,024-dimensional, L2-normalized, last-token embeddings, truncatable to 32, 64, 128, 256, 512, or 768 dimensions with re-normalization. [^jina-v5-omni-small-card]
- **Input limits:** 32,768 text tokens, with 256–1,280 vision tokens stated as configuration defaults. [^jina-v5-omni-small-card]
- **Modalities:** text, image, video, and audio, including fused multimodal inputs. PDFs are accepted by rendering pages as visual inputs. [^jina-v5-omni-small-card]

## Language support

The model card labels Omni Small “multilingual” but does not enumerate languages, give a language count, define support criteria, or report per-language results. Alignment with the multilingual Jina Embeddings v5 Text Small model supports the claimed multilingual text compatibility, but the card does not establish language coverage for speech or language-dependent image and video tasks. [^jina-v5-omni-small-card]

## Training data and procedure

The supplied model card does not identify training datasets, sample counts, language or modality distributions, licenses, filtering, deduplication, synthetic-data use, or contamination controls. It establishes text-space alignment and task-specific adapters but does not describe training stages or losses. The local leaderboard separately marks training data and training code as unavailable. Training-data composition and reproducibility therefore remain undocumented in the supplied sources. [^jina-v5-omni-small-card] [^mteb-multilingual-v2-summary]

## Contradictions

The card's approximate **1.74B** parameter count differs from the leaderboard's **1.626B total** count. This may reflect rounding or different counting conventions, but neither source explains the discrepancy. [^jina-v5-omni-small-card] [^mteb-multilingual-v2-summary]

## Relationships

- **Aligned with:** [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md); their vectors share a space, allowing text indexed with Text Small to be queried using Omni Small media embeddings without reindexing. [^jina-v5-omni-small-card]
- **Evaluated in:** [MTEB Multilingual v2 leaderboard snapshot](mteb-multilingual-v2-leaderboard-snapshot.md). [^mteb-multilingual-v2-summary]

[^jina-v5-omni-small-card]: [jina-embeddings-v5-omni-small model card](../raw/jina-embeddings-v5-omni-small.md). Model, architecture, language, benchmark, and training-coverage statements are reported by the card. Its referenced benchmark and architecture images are unavailable for this source, and its external technical report was not supplied.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied, unauthenticated leaderboard metadata and scores; the artifact does not document its evaluation protocol.
