---
type: Concept
title: Nemotron-3.5-Embed-1B-BF16
description: A 1.55B-parameter multilingual text-and-image document embedding model that distills an 8B teacher into a frozen Nemotron-3-Embed-1B text tower plus a Pixtral vision encoder, with 2,048-dimensional mean-pooled outputs.
tags: [embedding, retrieval, multimodal, visual-document, multilingual, nemotron, nvidia, ministral, distillation]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T03:14:39Z }
sources:
  - id: nemotron-3-5-embed-1b-card
    resource: ../raw/Nemotron-3.5-Embed-1B-BF16.md
    kind: model-card
    title: Nemotron-3.5-Embed-1B-BF16 model card
---

# Nemotron-3.5-Embed-1B-BF16

Nemotron-3.5-Embed-1B-BF16 is NVIDIA's single-vector (bi-encoder) embedding model for multilingual question-answering retrieval over text and document-page images. Queries are text only; documents may be an image, text, or image plus text. It has 1.55B parameters, pairs a Pixtral vision encoder with a language model initialized from [Nemotron-3-Embed-1B-BF16](nemotron-3-embed-1b-bf16.md), and emits one mean-pooled, L2-normalized 2,048-dimensional vector per input. All claims below are reported by the vendor card (Reported) unless marked otherwise. [^nemotron-3-5-embed-1b-card]

## Architecture and training

- **Components:** a Pixtral vision encoder initialized from `mistralai/Ministral-3-3B-Instruct-2512-BF16` and a language model initialized from `nvidia/Nemotron-3-Embed-1B-BF16`; 1.55B parameters total. [^nemotron-3-5-embed-1b-card] (Model Architecture)
- **Distillation:** trained from the Nemotron-3.5-Embed-8B-BF16 teacher with combined cosine-distance and MSE losses on multilingual text and image retrieval data. [^nemotron-3-5-embed-1b-card] (Model Architecture)
- **Frozen text tower:** the language model stays frozen during distillation, so the model shares its text embedding space with Nemotron-3-Embed-1B-BF16 and adds image retrieval; only the vision encoder and multimodal projection were fine-tuned on image and image-text data. [^nemotron-3-5-embed-1b-card] (Model Architecture)
- **Training data:** 2.3M samples containing images (with or without text) and 8.5M+ text-only samples; public, commercially permissible, and synthetic data. Text data follows the Nemotron-3-Embed-1B card. Image datasets named: ArxivQA, ColPali-PDF, InfoVQA, docmatix-ir, Docmatix, wiki-ss-nq. Seed corpora for synthetic data: FinePdfs, CentralActs, BRIGHT, MultiHiertt, Digital Corpora, Vdr-multilingual; generator LLMs include Nemotron-3 Super/Ultra, several Qwen, Gemma-4, Pixtral-12B and gpt-oss models. Mixture proportions and filtering are not stated. [^nemotron-3-5-embed-1b-card] (Training Dataset)

## Interface and constraints

| Property | Value |
|---|---|
| Output | Mean pooling over token hidden states, then L2 normalization; 2,048 dims |
| Matryoshka-style truncation | Truncate from the end (e.g. first 1,024 or 512 dims), then re-normalize |
| Context | 32,768 tokens, shared by text and image tokens |
| Image resolution | Default `longest_edge` 1,120 px, adjustable up to 1,540 px |
| Prefixes | System prompt `query:` for queries, `passage:` for documents (applied by `encode_query`/`encode_document` in Sentence Transformers and by `input_type` in vLLM) |
| Runtimes | Transformers (`5.20.0` tested), Sentence Transformers (>5.4), vLLM `0.32.0` (needs transformers `>=5.16.1,<5.20.0`, so use a separate environment) |
| Hardware / OS | NVIDIA Ampere, Hopper, Blackwell; Linux |
| License | OpenMDW-1.1; Ministral base models are Apache-2.0 |
| Released | Hugging Face, 2026-10-20 |

Source: [^nemotron-3-5-embed-1b-card] (Input, Output, Installation, vLLM Usage, Software Integration, License/Terms of Use, Release Date).

Caveats stated by the card: Flash Attention 2 can give CUDA errors or wrong outputs with image inputs in Transformers 5.17–5.19 (upgrade to 5.20.0); embeddings truncated by dimension must be re-normalized; inputs beyond 32,768 tokens must be truncated or images downsized; retrieval of the correct document is not guaranteed. [^nemotron-3-5-embed-1b-card] (Troubleshooting, Explainability)

## Languages

Text retrieval was evaluated on 34 languages (same list as [Nemotron-3-Embed-1B-BF16](nemotron-3-embed-1b-bf16.md)). Image retrieval was evaluated on 18: Arabic, Bengali, Chinese, English, Persian, Finnish, French, German, Hindi, Indonesian, Japanese, Korean, Russian, Spanish, Swahili, Telugu, Thai, and Yoruba. Additional languages may work but are not evaluated. [^nemotron-3-5-embed-1b-card] (Description)

## Benchmarks (Reported, NDCG@10)

Vendor-run comparison on ViDoRe V3 (8 public and 2 private datasets) and MIRACL-VISION (18 languages). The card evaluated Nemotron models at the default 1,120 px `longest_edge` and Qwen3-VL-Embedding models at `max_pixels` 1,843,200. [^nemotron-3-5-embed-1b-card] (Evaluation Dataset)

| Model | ViDoRe V3 image | ViDoRe V3 text | ViDoRe V3 image+text | MIRACL-VISION image |
|---|---:|---:|---:|---:|
| Qwen3-VL-Embedding-2B | 52.89 | 48.31 | 51.97 | 58.42 |
| **Nemotron-3.5-Embed-1B-BF16** | 58.02 | 57.80 | 58.82 | 68.93 |
| Qwen3-VL-Embedding-8B | 58.29 | 53.69 | 57.03 | 68.33 |
| Nemotron-3.5-Embed-8B-BF16 (teacher) | 60.39 | 60.65 | 61.47 | 72.64 |

Reading (Synthesis): the 1B model beats Qwen3-VL-Embedding-2B on every column and Qwen3-VL-Embedding-8B on three of four (it trails by 0.27 on ViDoRe V3 image), while the 8B teacher leads all columns. Do not compare the 57.80 ViDoRe V3 text figure directly with the 57.74 "ViDoRe-V3 text" figure in [Nemotron-3-Embed-1B-BF16](nemotron-3-embed-1b-bf16.md): that page's figure comes from a different card with 4,096-token chunk retrieval over OCR text, and the protocols are not shown to match. The card gives no variance, per-dataset results, or independent reproduction; the usage snippets' example similarity scores are illustrative and vary with hardware (Unverified as benchmarks).

## Relationships

- Derived from / shares text space with: [Nemotron-3-Embed-1B-BF16](nemotron-3-embed-1b-bf16.md), whose text tower is reused frozen. [^nemotron-3-5-embed-1b-card]
- Distilled from: Nemotron-3.5-Embed-8B-BF16 (no local raw card; the related [Nemotron-3-Embed-8B-BF16](nemotron-3-embed-8b-bf16.md) is the text-only predecessor family). [^nemotron-3-5-embed-1b-card]
- Compared against: [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) and [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) in the vendor table. [^nemotron-3-5-embed-1b-card]
- Reranked by: [Nemotron-3.5-Rerank-8B-BF16](nemotron-3-5-rerank-8b-bf16.md), whose card uses this model as the first-stage retriever in its top-50 evaluation.
- Related (Synthesis): a text-and-image single-vector model without audio/video input, relevant to the [multimodal embedding model comparison](multimodal-embedding-model-comparison.md); that page now includes it in its selection, ≤2B, and architecture tables.

## Coverage and limits

Entry point inspected statically in full (front matter, description, architecture, I/O, installation and Transformers/Sentence Transformers/vLLM examples, training data, evaluation table, ethics and subcards). No code was executed. Linked sibling cards (NVFP4 1B, 8B BF16), the blog post, datasets, and benchmarks were not inspected. The NVFP4 1B variant is only mentioned as a sibling checkpoint. The card's Bias, Privacy, and Safety subcards contain no measured bias metrics ("None"/"Not Applicable") and are excluded as boilerplate.

[^nemotron-3-5-embed-1b-card]: [Nemotron-3.5-Embed-1B-BF16 model card](../raw/Nemotron-3.5-Embed-1B-BF16.md). Reported by the vendor card at the section locators given inline; not independently reproduced.
