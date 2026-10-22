---
type: Concept
title: pplx-embed-v2-late-0.6b
description: A 594M-stored-parameter (340M active) MIT-licensed Qwen3.5-based multimodal ColBERT retriever from Perplexity that emits 128-dimensional token vectors scored with MaxSim and shares an embedding space with the 9B sibling.
tags: [embedding, retrieval, late-interaction, colbert, multimodal, visual-document, multilingual, perplexity]
status: draft
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T18:00:00Z }
stale_after: 2027-01-20
sources:
  - id: pplx-late-06b-page
    resource: ../raw/perplexity-ai-pplx-embed-v2-late-0.6b.md
    kind: web
    title: perplexity-ai/pplx-embed-v2-late-0.6b Hugging Face page capture
---

# pplx-embed-v2-late-0.6b

pplx-embed-v2-late-0.6b is the smaller member of Perplexity's `pplx-embed-v2-late` family of **multimodal late-interaction (ColBERT) retrievers** for text, images, and visual documents. It is built on Qwen3.5 with bidirectional attention, produces one 128-dimensional vector per token, and scores query–document pairs with MaxSim.[^pplx-late-06b-page] The 0.6B and 9B models share one embedding space, so the 0.6B model can query an index built with the 9B model ([pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md)).[^pplx-late-06b-page]

## Specification

| Field | Value | Evidence |
|---|---|---|
| Publisher | Perplexity (`perplexity-ai`) | Reported |
| Active parameters | 340M (card table) | Reported |
| Stored parameters | 594,321,600 (about 0.6B), F32 safetensors, 2.38 GB, unsharded | Observed (Hub metadata) |
| Architecture | `Qwen3_5Model`, `model_type` `qwen3_5`; bidirectional attention; vision encoder present (chat template carries image tokens) | Reported / Observed |
| Output | One 128-dimensional vector per token; MaxSim scoring | Reported |
| Modalities | Text queries; text or image (visual-document) documents. Mixed text+image batches are unsupported | Reported |
| License | MIT | Observed |
| Languages | Tagged `multilingual`; no language list | Observed |
| Library | Sentence Transformers (`MultiVectorEncoder`), needs `sentence-transformers>=6.0.0` and `transformers>=5.4.0`; native modules, no custom code | Reported |
| Context / token limits | Not stated on the page | Limit |

The gap between 340M "active" and 594M stored parameters is not explained on the page. A likely cause is that part of the stored weights (for example the large token-embedding table and vision/projection modules) does not count as active compute, but the card does not say so.[^pplx-late-06b-page] *(Synthesis, unverified.)*

## Reported results

Perplexity-reported nDCG@10 on the **public ViDoRe v3** set, under two document input forms:[^pplx-late-06b-page]

| Model | Active params | Dim | ViDoRe v3, Image | ViDoRe v3, Markdown |
|---|---:|---:|---:|---:|
| pplx-embed-v2-late-0.6b | 340M | 128 | 62.3% | 61.2% |
| pplx-embed-v2-late-9b | 7.4B | 128 | 65.2% | 64.7% |

The 9B model leads by about 2.9 points (Image) and 3.5 points (Markdown) with roughly 22× the active parameters. These are vendor-reported, unreproduced figures; the evaluation protocol, visual-token budget, and baselines are in a linked blog post and technical report that were not supplied. They should not be ranked against other wiki ViDoRe numbers (for example [EVIE-Preview-4.5B](evie-preview-4-5b.md) or [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md)) without confirming the same subset (public vs. all), metric, and token budget.

## Training

Both sizes were distilled from an **internal 18B ColBERT teacher** trained on pair and triplet data, using a token-level **LEAF-style** distillation objective. The 0.6B model was fully fine-tuned; for the 9B model, the last eight transformer layers were fully fine-tuned and the rest of the transformer plus the vision encoder were adapted with LoRA.[^pplx-late-06b-page] Training data, data size, and hyperparameters are not stated on the page.

## Usage procedure

1. Install `sentence-transformers>=6.0.0` and `transformers>=5.4.0`.
2. Load `MultiVectorEncoder("perplexity-ai/pplx-embed-v2-late-0.6b")` (the 9B repo id is a drop-in replacement).
3. Encode queries with `encode_query` and documents with `encode_document`; documents may be text strings or RGB `PIL` images.
4. Score with `model.similarity(queries, documents)`, which applies MaxSim.
5. Encode text-only and image-only batches in separate calls.
6. When using PyLate, note the card's warning: PyLate inserts the Q/D markers at the second position, whereas this model expects them first.[^pplx-late-06b-page]

## Hub metadata at capture

Created 2026-08-03, last modified 2026-10-22; 2,003 downloads in the last month, 61 likes; HF Inference live for `feature-extraction`; model tree lists 1 adapter, 5 finetunes, and 2 quantizations; member of the `pplx-embed-v2` collection ("second set of text embedding models", 3 items); linked paper arXiv:2610.29523, "pplx-embed-v2-late Technical Report".[^pplx-late-06b-page]

## Limits

- The technical report (arXiv:2610.29523) and the Perplexity blog post with benchmarks were not supplied, so training details, protocol, ablations, and visual-token settings are unknown.
- Only ViDoRe v3 public results are given; no MTEB, text-only, or multilingual results appear, although the Hub tags include `mteb`.
- 9B figures here come from this card's table; the sibling's own page is compiled in [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md) and repeats the same table.
- The page is a rendered HTML snapshot; the Files tab and model-tree children were not captured, and no code was executed.

## Relationships

- **Shares embedding space with:** [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md), enabling cheap query-side encoding against a 9B-built index.
- **Same collection as:** [pplx-embed-v2-context-9b-preview](pplx-embed-v2-context-9b-preview.md), a single-vector contextual-chunk model from the same vendor; the two use different representations and are not interchangeable.
- **Comparable late-interaction retrievers:** [LFM2.5-ColBERT-350M](lfm2-5-colbert-350m.md) and [mLateOn](mlateon.md) (text), and [EVIE-Preview-4.5B](evie-preview-4-5b.md), [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md), and [webAI-ColVec1.1-4b](webai-colvec1-1-4b.md) (visual-document, also Qwen3.5-based); see [Current embedding-model architecture taxonomy](embedding-model-architecture-taxonomy.md).

[^pplx-late-06b-page]: [perplexity-ai/pplx-embed-v2-late-0.6b Hugging Face page capture](../raw/perplexity-ai-pplx-embed-v2-late-0.6b.md). Locators: rendered model card sections "pplx-embed-v2-late: Multimodal Late-Interaction Embeddings", "Models" table, "Training", "Usage (Sentence Transformers)", and "Citation"; embedded Hub JSON keys `config`, `cardData`, `safetensors`, `tags`, `downloads`, `likes`, `createdAt`, and `lastModified`; sidebar "Model tree" and "Collection" panels. Vendor-reported; no independent verification. Page chrome, SVG download chart, and chat template were excluded as boilerplate; linked blog, paper, and Files tab were not followed.
