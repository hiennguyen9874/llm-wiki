---
type: Concept
title: pplx-embed-v2-late-9b
description: An 8.39B-stored-parameter (7.4B active) MIT-licensed Qwen3.5-based multimodal ColBERT retriever from Perplexity that emits 128-dimensional token vectors scored with MaxSim and is the larger, higher-scoring sibling of the 0.6B model.
tags: [embedding, retrieval, late-interaction, colbert, multimodal, visual-document, multilingual, perplexity]
status: draft
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T18:00:00Z }
stale_after: 2027-01-20
sources:
  - id: pplx-late-9b-page
    resource: ../raw/perplexity-ai-pplx-embed-v2-late-9b.md
    kind: web
    title: perplexity-ai/pplx-embed-v2-late-9b Hugging Face page capture
---

# pplx-embed-v2-late-9b

pplx-embed-v2-late-9b is the larger member of Perplexity's `pplx-embed-v2-late` family of **multimodal late-interaction (ColBERT) retrievers** for text, images, and visual documents. It is built on Qwen3.5 with bidirectional attention, produces one 128-dimensional vector per token, and scores query–document pairs with MaxSim.[^pplx-late-9b-page] It shares an embedding space with [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md), so the small model can query an index built by this one.[^pplx-late-9b-page]

## Specification

| Field | Value | Evidence |
|---|---|---|
| Publisher | Perplexity (`perplexity-ai`) | Reported |
| Active parameters | 7.4B (card table) | Reported |
| Stored parameters | 8,392,695,024 (about 8.39B), F32 safetensors, 33.57 GB, unsharded | Observed (Hub metadata) |
| Architecture | `Qwen3_5Model`, `model_type` `qwen3_5`; bidirectional attention; vision encoder present (chat template carries image tokens) | Reported / Observed |
| Output | One 128-dimensional vector per token; MaxSim scoring | Reported |
| Modalities | Text queries; text or image (visual-document) documents. Mixed text+image batches are unsupported | Reported |
| License | MIT | Observed |
| Languages | Tagged `multilingual`; no language list | Observed |
| Library | Sentence Transformers (`MultiVectorEncoder`), needs `sentence-transformers>=6.0.0` and `transformers>=5.4.0`; native modules, no custom code | Reported |
| Context / token limits | Not stated on the page | Limit |

The gap between 7.4B "active" and 8.39B stored parameters is not explained on the page; as with the 0.6B model, it plausibly reflects weights that do not count toward active compute (for example the token-embedding table), but the card does not say so.[^pplx-late-9b-page] *(Synthesis, unverified.)* The F32 checkpoint is large (33.57 GB); the Hub flags that quantized variants exist, but their identity was not captured.[^pplx-late-9b-page]

## Reported results

Perplexity-reported nDCG@10 on the **public ViDoRe v3** set, under two document input forms:[^pplx-late-9b-page]

| Model | Active params | Dim | ViDoRe v3, Image | ViDoRe v3, Markdown |
|---|---:|---:|---:|---:|
| pplx-embed-v2-late-9b | 7.4B | 128 | 65.2% | 64.7% |
| pplx-embed-v2-late-0.6b | 340M | 128 | 62.3% | 61.2% |

The 9B model leads by 2.9 points (Image) and 3.5 points (Markdown), the same gap the [0.6B page](pplx-embed-v2-late-0-6b.md) reports (*Synthesis* from the table). These are vendor-reported, unreproduced figures; the protocol, visual-token budget, and baselines are in a linked blog post and technical report that were not supplied. Do not rank them against other wiki ViDoRe numbers (for example [EVIE-Preview-4.5B](evie-preview-4-5b.md), [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md), or [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md)) without confirming the same subset (public vs. all), metric, and token budget.

## Training

Both sizes were distilled from an **internal 18B ColBERT teacher** trained on pair and triplet data, using a token-level **LEAF-style** distillation objective. For the 9B model, the final eight transformer layers were fully fine-tuned, while the remaining transformer layers and the vision encoder were adapted with LoRA; the 0.6B model was fully fine-tuned.[^pplx-late-9b-page] Training data, data size, and hyperparameters are not stated on the page.

## Usage procedure

1. Install `sentence-transformers>=6.0.0` and `transformers>=5.4.0`.
2. Load `MultiVectorEncoder("perplexity-ai/pplx-embed-v2-late-9b", device="cuda")`; the 0.6B repo id is a drop-in replacement.
3. Encode queries with `encode_query` and documents with `encode_document`; documents may be text strings or RGB `PIL` images.
4. Score with `model.similarity(queries, documents)`, which applies MaxSim.
5. Encode text-only and image-only batches in separate calls.
6. When using PyLate, note the card's warning: PyLate inserts the Q/D markers at the second position, whereas this model expects them first.[^pplx-late-9b-page]

The Hub page also offers a generic single-vector `SentenceTransformer(...).encode` snippet; that is the Hub's auto-generated "Use this model" boilerplate, and the card's own procedure is the `MultiVectorEncoder` path above (*Synthesis*).[^pplx-late-9b-page]

## Hub metadata at capture

Created 2026-07-20, last modified 2026-10-22; 1,021 downloads in the last month (1,042 all time), 39 likes; no inference providers; linked paper arXiv:2610.29523, "pplx-embed-v2-late Technical Report" (Krimmel et al., 2026).[^pplx-late-9b-page]

## Limits

- The technical report (arXiv:2610.29523) and the Perplexity blog post with benchmarks were not supplied, so training data, protocol, ablations, and visual-token settings are unknown.
- Only ViDoRe v3 public results are given; no MTEB, text-only, or multilingual results appear, although the Hub tags include `mteb`.
- The page is a rendered HTML snapshot; the Files tab, model-tree children, and quantization details were not captured, and no code was executed.

## Relationships

- **Shares embedding space with:** [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md), enabling cheap query-side encoding against a 9B-built index.
- **Same collection family as:** [pplx-embed-v2-context-9b-preview](pplx-embed-v2-context-9b-preview.md), a single-vector contextual-chunk model from the same vendor; the representations differ and are not interchangeable.
- **Comparable late-interaction retrievers:** [LFM2.5-ColBERT-350M](lfm2-5-colbert-350m.md) and [mLateOn](mlateon.md) (text), and [EVIE-Preview-4.5B](evie-preview-4-5b.md), [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md), [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md) (visual-document, also Qwen3.5-based); see [Current embedding-model architecture taxonomy](embedding-model-architecture-taxonomy.md) and the [multimodal embedding model comparison](multimodal-embedding-model-comparison.md).

[^pplx-late-9b-page]: [perplexity-ai/pplx-embed-v2-late-9b Hugging Face page capture](../raw/perplexity-ai-pplx-embed-v2-late-9b.md). Locators: rendered model card intro, "Models" table, "Training", "Usage (Sentence Transformers)", and "Citation" sections; embedded Hub JSON keys `config`, `cardData`, `safetensors`, `tags`, `downloads`, `downloadsAllTime`, `likes`, `createdAt`, `lastModified`, `hasQuantizations`; "Use this model" snippet. Vendor-reported; no independent verification. Page chrome, SVG download chart, and chat template were excluded as boilerplate; linked blog, paper, and Files tab were not followed.
