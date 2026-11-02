---
type: Concept
title: pplx-embed-v2-context-0.6b
description: A multilingual 0.6B-class multimodal contextual embedding model producing 1,024-dimensional chunk vectors for text and visual-document retrieval.
tags: [embedding, retrieval, contextual-embeddings, multimodal, visual-document, multilingual, perplexity]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:13:34Z }
stale_after: 2027-01-31
sources:
  - id: pplx-context-06b-card
    resource: ../raw/perplexity-ai-pplx-embed-v2-context-0.6b.md
    kind: model-card
    title: perplexity-ai/pplx-embed-v2-context-0.6b model card
---

# pplx-embed-v2-context-0.6b

Perplexity reports a vision-language retrieval model that encodes document chunks together so each chunk reflects surrounding context, or encodes text chunks independently. It produces 1,024-dimensional vectors per text chunk or image band, suitable for dense ANN retrieval. The card claims alignment with the 1,024-dimensional Matryoshka prefix of `pplx-embed-v2-context-9b`; it does not establish compatibility with the separate 9B preview.[^pplx-context-06b-card]

## Specification

| Field | Card information |
|---|---|
| Size | 0.6B class in model name; exact and active parameter counts not stated |
| Base | Frontmatter declares a fine-tune of [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md); further architecture and training details not stated |
| Modalities | Text queries; text chunks or images/visual documents as indexed content |
| Dimensions | 1,024; smaller trained prefixes not specified |
| Output and scoring | Native unnormalized INT8; cosine, or dot product after L2 normalization |
| Pooling | Image bands pool only visual content; text pooling not specified |
| Language | Tagged multilingual; languages and coverage not specified |
| Context and license | Configured input length is not quantified; license not stated in this card |

All model behavior above is **Reported** by the vendor, not independently verified.[^pplx-context-06b-card]

## Text retrieval

- Group non-overlapping chunks by document and call `encode`; outputs are one `(chunk_count, 1024)` array per document. To encode chunks independently, batch each chunk as a singleton list. A singleton also gives one embedding per document.
- Call `encode_queries` on single-chunk query rows, not `encode`: the card warns that distinct query/document prefixes make the latter silently degrade query quality.
- The text API does not truncate: split or truncate inputs exceeding the configured length yourself. Both methods default to batch size 32, no normalization, NumPy output, no progress bar, and no device move; CPU tensors are available with `convert_to_numpy=False`.[^pplx-context-06b-card]

## Visual document retrieval

`encode_images` processes each image in a contextual forward pass and divides merged visual tokens into whole-row horizontal bands. Only visual tokens are pooled; prefix, wrapper, and separator tokens are excluded. The card describes preserved three-axis MRoPE and midpoint-based separator positions. It returns `(actual_chunks, 1024)` per image, capped by the number of merged image rows. Score each band by cosine and take the maximum for a page. Defaults are 8 requested bands, 16,384 minimum and 1,800,000 maximum pixels, and batch size 1; `prepare_images` exposes tensors, spans, masks, and position IDs without a forward pass.[^pplx-context-06b-card]

## Setup and limits

The card specifies `transformers>=5.4.0`, PyTorch, NumPy, safetensors, tqdm, Pillow and torchvision; `flash-linear-attention` and `causal-conv1d` enable the fast linear-attention path. Loading requires `trust_remote_code=True`: review and pin remote code before execution. No model code, weights or commands were executed or independently verified.[^pplx-context-06b-card]

The supplied standalone card has no revision, publication/capture date, explicit license, numeric context limit, benchmark results, or training/evaluation details. Its linked [technical report](https://arxiv.org/abs/2610.38854) was not inspected; the linked [9B model card](pplx-embed-v2-context-9b.md) has since been compiled separately, without its implementation; the decorative logo was excluded. No performance ranking or preview compatibility follows from this card. Status is draft pending those material details.[^pplx-context-06b-card]

## Relationships

- **Fine-tuned from:** [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md), according to card metadata; the latter outputs token vectors rather than contextual dense chunks.[^pplx-context-06b-card]
- **Shares embedding space with:** [pplx-embed-v2-context-9b](pplx-embed-v2-context-9b.md), at its 1,024-dimensional prefix, according to this card.[^pplx-context-06b-card]
- **Related to:** [pplx-embed-v2-context-9b-preview](pplx-embed-v2-context-9b-preview.md), another contextual-chunk model; the compatibility claim names the non-preview 9B model, not this preview.
- **Uses:** contextual chunk retrieval in the [architecture taxonomy](embedding-model-architecture-taxonomy.md); compare multimodal options in the [model comparison](multimodal-embedding-model-comparison.md).

[^pplx-context-06b-card]: [Perplexity model card](../raw/perplexity-ai-pplx-embed-v2-context-0.6b.md), frontmatter and introduction, “Text Embeddings”, “Image Embeddings”, and “Citation”. Vendor-reported; no independent verification. The linked report and model implementation were not inspected.
