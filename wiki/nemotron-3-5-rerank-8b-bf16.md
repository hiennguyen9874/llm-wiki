---
type: Concept
title: Nemotron-3.5-Rerank-8B-BF16
description: An 8.38B-parameter Ministral-3-8B-based multilingual multimodal cross-encoder reranker that scores a text query against text, page-image, or image-plus-text documents with a raw logit and a 32,768-token context.
tags: [reranking, cross-encoder, multimodal, visual-document, multilingual, nemotron, nvidia, ministral]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T03:16:00Z }
sources:
  - id: nemotron-3-5-rerank-8b-card
    resource: ../raw/Nemotron-3.5-Rerank-8B-BF16.md
    kind: model-card
    title: Nemotron-3.5-Rerank-8B-BF16 model card
---

# Nemotron-3.5-Rerank-8B-BF16

Nemotron-3.5-Rerank-8B-BF16 is NVIDIA's pointwise cross-encoder reranker for multilingual question-answering retrieval over text and document-page images. Each input is one text query paired with one document, which may be text, an image, or both. The model returns one raw relevance logit per pair; higher means more relevant. It has 8.38B parameters, a Pixtral-based vision encoder, and a bidirectional Ministral3 language tower derived from Ministral-3-8B-Instruct-2512. All claims below are vendor-reported (Reported) unless marked otherwise. [^nemotron-3-5-rerank-8b-card]

## Architecture and training

- **Components:** a Pixtral-based vision encoder plus a bidirectional Ministral3 language-model tower; 8.38B parameters; scoring mode is pointwise (one query, one document per forward pass). [^nemotron-3-5-rerank-8b-card] (Model Architecture; Input)
- **Two-stage training:** stage 1 trained an 8B reranker derived from Ministral-3-8B-Instruct-2512-BF16 on text-only data; stage 2 initialized from stage 1 and trained on image and combined image-text data. [^nemotron-3-5-rerank-8b-card] (Model Architecture)
- **Training data:** 21M text-only samples and 2.3M samples containing images (with or without text); public, commercially permissible, and synthetic data. Text data sources are deferred to the [Nemotron-3-Embed-8B-BF16](nemotron-3-embed-8b-bf16.md) card. Image datasets named: ArxivQA, ColPali-PDF, InfoVQA, TAT-DQA, docmatix-ir, Docmatix, wiki-ss-nq. Synthetic data came from queries or QA pairs generated from seed corpora (FinePdfs, CentralActs, BRIGHT, MultiHiertt, Digital Corpora, Vdr-multilingual) by LLMs including Nemotron-3 Super/Ultra, several Qwen models, Gemma-4-31B, Pixtral-12B, and gpt-oss. Mixture proportions and filtering are not stated. [^nemotron-3-5-rerank-8b-card] (Training Dataset)

## Interface and constraints

| Property | Value |
|---|---|
| Scoring | Pointwise cross-encoder; raw logit (vLLM: `use_activation=False`, mean sequence pooling, `classify` task) |
| Input | Text query (chat role `query`); document (role `document`) as text, one image, or both |
| Context | 32,768 tokens, shared by text and image tokens |
| Image resolution | Default `longest_edge` 1,120 px, adjustable up to 1,540 px; at most one image per document in vLLM |
| Runtimes | Transformers (`5.20.0` tested, `AutoModelForSequenceClassification`, `trust_remote_code=True`), Sentence Transformers `CrossEncoder` (6.1.0), vLLM `0.32.0` (needs transformers `>=5.16.1,<5.20.0`; use a separate environment) |
| Hardware / OS | NVIDIA Ampere (A100 80GB), Hopper (H100 80GB), Blackwell (GB200); Linux |
| License | OpenMDW-1.1; Ministral base is Apache-2.0 |
| Released | Hugging Face, 2026-10-20 |

Source: [^nemotron-3-5-rerank-8b-card] (Input, Output, Installation, vLLM Usage, Software Integration, License/Terms of Use, Release Date).

Caveats stated by the card:

- With vLLM, use `/classify` with structured `query`/`document` messages for multimodal inputs; the `/score` and `/rerank` request-rendering paths can mishandle this checkpoint's image placeholders. In the online example, `probs[0]` is the raw logit, not a probability.
- Flash Attention 2 can cause CUDA errors or wrong outputs with image inputs in Transformers 5.17–5.19; upgrade to 5.20.0.
- Inputs over 32,768 tokens must be truncated or images downsized; the model does not always guarantee a meaningful ranking.
- Example scores in the card (about −1.8 to −3.0) are illustrative, hardware-dependent, and sit on an unbounded logit scale, so do not treat them as probabilities or thresholds. [^nemotron-3-5-rerank-8b-card] (Troubleshooting; vLLM Online Serving; Explainability)

## Languages

Text retrieval was evaluated on 34 languages (English, Arabic, Assamese, Bengali, Bulgarian, Chinese, Danish, Dutch, Finnish, French, German, Hindi, Hinglish, Indonesian, Italian, Japanese, Korean, Malay, Marathi, Nepali, Norwegian, Persian, Portuguese, Romanian, Russian, Spanish, Swahili, Swedish, Tamil, Telugu, Thai, Ukrainian, Urdu, Vietnamese). Image retrieval was evaluated on 18: Arabic, Bengali, Chinese, English, Persian, Finnish, French, German, Hindi, Indonesian, Japanese, Korean, Russian, Spanish, Swahili, Telugu, Thai, and Yoruba. Further languages may work but are not evaluated. [^nemotron-3-5-rerank-8b-card] (Description)

## Benchmarks (Reported, NDCG@10)

One protocol: both rerankers rerank the **top 50** candidates retrieved by [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md). Nemotron used its default 1,120 px `longest_edge`; Qwen3-VL-Reranker-8B used its default `max_pixels` of 1,310,720. ViDoRe V3 covers 8 public and 2 private datasets; MIRACL-VISION covers 18 languages. [^nemotron-3-5-rerank-8b-card] (Evaluation Dataset)

| Model | ViDoRe V3 image | ViDoRe V3 text | ViDoRe V3 image+text | MIRACL-VISION image |
|---|---:|---:|---:|---:|
| Nemotron-3.5-Embed-1B-BF16 (first stage) | 58.02 | 57.80 | 58.82 | 68.93 |
| [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md) | 66.02 | 64.88 | 66.03 | 75.06 |
| **Nemotron-3.5-Rerank-8B-BF16** | **67.22** | **66.89** | **67.56** | **78.69** |

Reading (Synthesis): reranking lifts the first-stage 1B embedding by 8.74–9.76 points on every column, and this model leads Qwen3-VL-Reranker-8B by 1.20 (image), 2.01 (text), 1.53 (image+text), and 3.63 (MIRACL-VISION) points. The Qwen3-VL-Reranker-8B ViDoRe v3 figure of 66.7 in the [reranker comparison](reranker-model-comparison.md) uses a different first stage (top-100 from Qwen3-VL-Embedding-2B), so do not mix those numbers. The card gives no variance, per-dataset breakdown, or independent reproduction, and the margins over Qwen are small on ViDoRe V3 (Unverified beyond the vendor run). The card also asserts state-of-the-art results on the ViDoRe v3.1 Reranking leaderboard as of 2026-10-20; the leaderboard was not inspected (Reported, Unverified). [^nemotron-3-5-rerank-8b-card]

## Relationships

- **Reranks candidates from:** [Nemotron-3.5-Embed-1B-BF16](nemotron-3-5-embed-1b-bf16.md), the first stage in the card's evaluation; the card recommends pairing a multimodal embedding model for dense retrieval with this reranker. [^nemotron-3-5-rerank-8b-card]
- **Text training data shared with:** [Nemotron-3-Embed-8B-BF16](nemotron-3-embed-8b-bf16.md), whose card lists the public text sources. [^nemotron-3-5-rerank-8b-card]
- **Compared against:** [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md), the sole external baseline in the vendor table. [^nemotron-3-5-rerank-8b-card]
- **Related (Synthesis):** among the wiki's rerankers, a peer of the multimodal Qwen3-VL rerankers; see the [reranker model comparison](reranker-model-comparison.md).

## Coverage and limits

The entry point was inspected statically in full (front matter, description, architecture, I/O, installation, Transformers, Sentence Transformers and vLLM examples, training data, evaluation table, ethics, bias, explainability, privacy, safety subcards). No code was executed. The blog post, leaderboard, linked datasets, and the Nemotron-3-Embed-8B-BF16 text-data list were not inspected. The bias, privacy, and safety subcards hold no measured metrics ("None"/"Not Applicable") and are excluded as boilerplate. Latency and throughput are named as performance metrics but no figures are given.

[^nemotron-3-5-rerank-8b-card]: [Nemotron-3.5-Rerank-8B-BF16 model card](../raw/Nemotron-3.5-Rerank-8B-BF16.md). Reported by the vendor card at the section locators given inline; not independently reproduced.
