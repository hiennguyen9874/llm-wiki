---
type: Concept
title: pplx-embed-v2-context-9b-preview
description: An 8.40B-parameter MIT-licensed multilingual contextual embedding preview from Perplexity that encodes a document's chunks together and returns one 2,048-dimensional, mean-pooled, natively INT8 embedding per chunk.
tags: [embedding, retrieval, contextual-embeddings, multilingual, matryoshka, rag, perplexity, preview]
status: draft
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T16:20:00Z }
stale_after: 2027-01-20
sources:
  - id: pplx-context-9b-page
    resource: ../raw/perplexity-ai-pplx-embed-v2-context-9b-preview.md
    kind: web
    title: perplexity-ai/pplx-embed-v2-context-9b-preview Hugging Face page capture
---

# pplx-embed-v2-context-9b-preview

pplx-embed-v2-context-9b-preview is a **contextual embedding** model for document chunks in RAG systems. A document is passed as a list of chunks; the chunks are encoded together, so each chunk's embedding reflects its surrounding context, and one embedding is returned per chunk.[^pplx-context-9b-page] It is explicitly a **preview**: weights, embeddings, and the interface may change without backward compatibility, and preview embeddings should not be mixed with those of a future release.[^pplx-context-9b-page]

## Specification

| Field | Value | Evidence |
|---|---|---|
| Publisher | Perplexity (`perplexity-ai`) | Reported |
| Parameters | 8,401,083,632 (about 8.40B), F32 safetensors, 33.6 GB sharded | Observed (Hub metadata) |
| Architecture | `PplxContextualModel`, `model_type` `pplx_contextual_qwen3_5`, loaded via custom code (`trust_remote_code=True`) | Observed |
| Backbone | Qwen3.5 family implied by `model_type`; the card does not name the base checkpoint | Synthesis |
| Output | 2,048 dimensions; Matryoshka losses at 1,024 and 2,048 only | Reported |
| Quantization | Natively unnormalized INT8 embeddings | Reported |
| Pooling | Mean | Reported |
| Instructions | None; fixed query/document prefixes | Reported |
| License | MIT | Observed |
| Languages | Tagged `multilingual`; no language list | Observed |
| Requirements | `transformers>=5.4.0`, `torch`, `numpy`, `safetensors`, `tqdm` | Reported |

The "9b" in the name does not match the 8.40B stored parameters; the card does not explain the difference.[^pplx-context-9b-page] Hub activity at capture: created 2026-09-25, last modified 2026-10-08, 1,830 downloads, 74 likes, one fine-tune listed in the model tree, no Inference Provider deployment, and membership in the three-item `pplx-embed-v2` collection.[^pplx-context-9b-page]

## Usage procedure

1. Group each document as a list of chunk strings; queries are single-chunk rows (`[["query"]]`).
2. Encode documents with `model.encode(doc_chunks)`, which returns one `(chunk_count, 2048)` array per document.
3. Encode queries with `model.encode_queries(queries)`. The model is trained with separate query and document prefixes, so encoding queries with `encode` **silently degrades retrieval quality**.
4. Compare with cosine similarity, or pass `normalize_embeddings=True` and use the dot product.
5. For 1,024 dimensions, take the first 1,024 values of each unnormalized embedding and normalize afterwards. Other truncation sizes were not trained.

Both methods accept `batch_size` (default 32), `normalize_embeddings` (default `False`), `convert_to_numpy` (default `True`), `show_progress_bar`, and `device`.[^pplx-context-9b-page]

## Relationship to the predecessor

The card states that, like `pplx-embed-context-v1`, the model natively produces unnormalized INT8 embeddings, which marks `pplx-embed-context-v1` as the earlier contextual release. That predecessor has no source in this wiki.[^pplx-context-9b-page] A community translation-memory test in the wiki reports a non-contextual "PPLX Embed V1 4B"; it is a different model line and says nothing about this checkpoint (see [translation-memory pairing benchmark](translation-memory-embedding-reranker-pairing-benchmark.md)).

## Limits

- **No benchmark results** appear in the captured page, so the model cannot be ranked against other wiki models. The page cites a Perplexity blog post, "Contextual embedding beyond the gold passage" (2026-09-30), which was not supplied or inspected.[^pplx-context-9b-page]
- The maximum chunk length, maximum number of chunks per document, and total context window are not stated.
- Training data, training procedure, and how chunk context is injected into each chunk's embedding are undisclosed on the page.
- The code is custom (`modeling_pplx_contextual.PplxContextualModel`); it was not inspected, and no command was executed.
- The captured page is a rendered HTML snapshot; its Files tab was not captured, so the file list and checkpoint contents are unverified.

## Relationships

- **Contrasts with:** [Qwen3-Embedding-8B](qwen3-embedding-8b.md) and other independent-chunk dense bi-encoders, which embed each chunk without its neighbours; see [Current embedding-model architecture taxonomy](embedding-model-architecture-taxonomy.md).
- **Sibling in the `pplx-embed-v2` collection:** [pplx-embed-v2-late-0.6b](pplx-embed-v2-late-0-6b.md) and [pplx-embed-v2-late-9b](pplx-embed-v2-late-9b.md), multi-vector late-interaction models with a different output representation.
- **Comparable scale:** [webAI-ColVec1.1-8b](webai-colvec1-1-8b.md) is also an 8.40B-parameter Qwen3.5-derived retriever, but a multi-vector visual-document model, so the two are not interchangeable.

[^pplx-context-9b-page]: [perplexity-ai/pplx-embed-v2-context-9b-preview Hugging Face page capture](../raw/perplexity-ai-pplx-embed-v2-context-9b-preview.md). Locators: rendered model card sections "pplx-embed-v2-context-9b-preview", "Model" table, "Usage", "Options", "Matryoshka dimensions", and "Citation"; embedded Hub JSON keys `config`, `safetensors`, `cardData`, `tags`, `downloads`, `likes`, `createdAt`, and `lastModified`. Vendor-reported; no independent verification. The inline chat template and page chrome were excluded as boilerplate; the `.../tree/main`, discussion, and blog links were not followed.
