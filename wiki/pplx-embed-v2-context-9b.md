---
type: Concept
title: pplx-embed-v2-context-9b
description: A multilingual 9B-class multimodal contextual embedding model with 2,048-dimensional chunk vectors and a 1,024-dimensional prefix shared with its 0.6B sibling.
tags: [embedding, retrieval, contextual-embeddings, multimodal, visual-document, multilingual, perplexity]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:13:34Z }
stale_after: 2027-01-31
sources:
  - id: pplx-context-9b-card
    resource: ../raw/perplexity-ai-pplx-embed-v2-context-9b.md
    kind: model-card
    title: perplexity-ai/pplx-embed-v2-context-9b model card
---

# pplx-embed-v2-context-9b

Perplexity **reports** a vision-language retrieval model that embeds text chunks with surrounding document context or separately, and encodes image pages as contextual horizontal bands. It returns one dense vector per chunk for ANN retrieval, with a 1,024-dimensional prefix sharing a space with [pplx-embed-v2-context-0.6b](pplx-embed-v2-context-0-6b.md). These are vendor claims, not independently verified.[^pplx-context-9b-card]

## Specification

| Field | Card information |
|---|---|
| Size and base | 9B class by name; exact and active counts unstated. Frontmatter declares a fine-tune of [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md). |
| Modalities | Text queries against text chunks or image/visual-document bands. |
| Dimensions | 2,048; Matryoshka training at 1,024 and 2,048 only. |
| Output and scoring | Native unnormalized INT8; cosine similarity, or dot product after L2 normalization. |
| Pooling | Visual bands pool visual tokens only; text pooling is not specified. |
| Language and license | Multilingual tag without language list; frontmatter declares MIT. |
| Context | Configured input length not quantified. |

These specifications are **Reported** by the card; its metadata and examples were inspected, not the weights or implementation.[^pplx-context-9b-card]

## Text retrieval

Group **non-overlapping** chunks by document and use `encode`; it returns one `(chunk_count, 2048)` array per document. Singleton chunk lists encode without document context; one singleton per document yields a document vector. Use `encode_queries` for single-chunk query rows: the card warns that `encode` uses the wrong prefix and silently degrades retrieval. The API does not truncate; split or truncate inputs exceeding its configured limit yourself. Defaults include batch size 32, no normalization, NumPy output, no progress bar, and no device move; `convert_to_numpy=False` yields CPU tensors.[^pplx-context-9b-card]

For 1,024 dimensions, take the first 1,024 values of each **unnormalized** text, image and query vector, then normalize; use this width for cross-model comparisons with the 0.6B sibling. Other prefix widths were not trained, according to the card.[^pplx-context-9b-card]

## Visual document retrieval

`encode_images` processes each image in a contextual forward pass, dividing merged visual tokens into whole-row horizontal bands. It preserves three-axis MRoPE and image wrappers, positions separators at adjacent-row midpoints and the horizontal center, and excludes prefixes, wrappers and separators from pooling. The `(actual_chunks, 2048)` output per image is capped by the number of merged image rows. Score chunks by cosine and take the maximum for page retrieval. Defaults: eight requested bands, 16,384 minimum and 1,800,000 maximum pixels, and image batch size one. `prepare_images` exposes input tensors, chunk spans, masks and positions without running the model.[^pplx-context-9b-card]

## Setup and evidence limits

The card requires `transformers>=5.4.0`, PyTorch, NumPy, safetensors, tqdm, Pillow and torchvision; `flash-linear-attention` and `causal-conv1d` enable the fast linear-attention path. It requires `trust_remote_code=True`: review and pin remote code before execution.[^pplx-context-9b-card]

The standalone card supplies no immutable revision, publication or capture date, numerical context limit, benchmark scores, detailed training protocol, or exact parameter count. The linked technical report and model code/weights were not inspected; the logo is decorative and unavailable locally. Examples were inspected statically, not executed. Status is draft pending material evidence. The separate [9B preview](pplx-embed-v2-context-9b-preview.md) is not named in the shared-space claim; neither compatibility with it nor supersession is established.[^pplx-context-9b-card]

## Relationships

- **Fine-tuned from:** [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md), per card metadata; the base uses token-level late interaction rather than dense contextual chunks.[^pplx-context-9b-card]
- **Shares embedding space with:** [pplx-embed-v2-context-0.6b](pplx-embed-v2-context-0-6b.md), at the 1,024-dimensional prefix, as reported by the vendor.[^pplx-context-9b-card]
- **Related to:** [9B preview](pplx-embed-v2-context-9b-preview.md), another contextual model; see the [architecture taxonomy](embedding-model-architecture-taxonomy.md) and [multimodal comparison](multimodal-embedding-model-comparison.md).

[^pplx-context-9b-card]: [Perplexity model card](../raw/perplexity-ai-pplx-embed-v2-context-9b.md), frontmatter and introduction, “Text Embeddings”, “Matryoshka dimensions”, “Image Embeddings”, and “Citation”. Vendor-reported; report and implementation not inspected.
