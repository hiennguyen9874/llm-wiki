---
type: Concept
title: GeeVec-Embeddings-mm-1.0
description: A 9.41B-parameter Qwen3.5-9B-based multimodal embedding model producing 4,096-dimensional last-token vectors for text, image, video, and visual-document retrieval, with a self-reported 78.78 average on the 44 retrieval datasets of MMEB-v2.
tags: [embedding, retrieval, multimodal, visual-document, qwen, mmeb]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:59:58Z }
stale_after: 2027-01-20
sources:
  - id: geevec-page
    resource: ../raw/geevec-ai-geevec-embeddings-mm-1.0.md
    kind: model-card
    title: geevec-ai/geevec-embeddings-mm-1.0 Hugging Face model page (HTML capture)
---

# GeeVec-Embeddings-mm-1.0

GeeVec-Embeddings-mm-1.0 is a dense multimodal embedding model from `geevec-ai`, built on Qwen3.5-9B (about 9.41B parameters). It maps text, images (and image-text inputs), video (sampled frames), and visual-document page images into one 4,096-dimensional space scored with cosine similarity, using last-token pooling.[^geevec-page] The card's only evidence is a table on the 44 retrieval datasets of MMEB-v2, where it reports an equal-weighted AVG of 78.78: the best Image (81.82) and VisDoc (83.63) scores in that table, but the weakest Video/moment score (59.66) among the 9B-class entries. Everything here is **Reported** (author text on the page); there is no paper, training description, or independent reproduction.[^geevec-page]

## Model facts

| Field | Value |
|---|---|
| Hub repo | `geevec-ai/geevec-embeddings-mm-1.0`; created 2026-10-22, last modified 2026-10-22; 2 likes; downloads not tracked; not gated |
| Backbone | Qwen3.5-9B |
| Parameters | approximately 9.41B |
| Output | 4,096-dimensional; cosine similarity; last-token pooling |
| Sequence length | 8,192 tokens "in the current embedding pipeline" |
| Modalities | text, image, video (sampled frames), visual document (page images incl. charts, tables, slides) |
| License | Apache-2.0 (Hub metadata) |
| Hub tags / pipeline | `feature-extraction`, `sentence-similarity`, `transformers`, `multimodal`; library `transformers`; tag `arxiv:2608.02148` |
| Not stated | languages, Matryoshka/truncation support, training data or method, instruction list beyond examples, audio support |

Locators: Introduction (technical highlights), header metadata (`cardData`, `createdAt`, `lastModified`, `likes`, `tags`).[^geevec-page]

## Usage

- **Environment:** `torch`, `transformers==5.8.0`, `accelerate`, `qwen-vl-utils`, `pillow`, `decord`.[^geevec-page]
- **Loading:** the card imports `GeeVecEmbedding` from a local `modeling` module with `from_pretrained(model_path, dtype=torch.bfloat16, device_map="cuda:0")`; the module is not part of the captured page. The Hub's own snippet generically shows `AutoModel` / `pipeline("feature-extraction")`, which is not the documented path (Observed discrepancy; whether `AutoModel` works is not established).[^geevec-page]
- **Encoding:** `model.encode(list_of_dicts)` where a query dict has `text` plus an `instruction` (for example "Find an image that matches the given description.", "Retrieve a document page that answers the question.", "Retrieve a video that matches the given description."); documents are dicts with `image` or `video` (plus `fps`). Similarity is `query_embeddings @ doc_embeddings.T`.[^geevec-page]
- **Notes:** all modalities yield 4,096-d vectors; use task-specific instructions and the corresponding evaluation configuration when reproducing benchmarks; convert PDFs to page images first; video is decoded by `qwen-vl-utils` at the requested `fps`, and pre-sampled frame lists are also accepted.[^geevec-page]
- **API:** the card points to hosted API documentation at geevec.com (not captured).[^geevec-page]

## Evaluation

Protocol as stated: 44 retrieval datasets of MMEB-v2 (12 image retrieval, 5 video retrieval, 3 moment retrieval, 24 visual-document retrieval); image and video tasks use Hit@1, visual-document tasks NDCG@5; percentages. "Video" includes moment retrieval; AVG weights the 44 datasets equally.[^geevec-page]

| Model | Size | AVG | Image | Video | VisDoc |
|---|---|---:|---:|---:|---:|
| Sentio | 10.20B | **79.57** | 81.58 | **65.45** | 83.28 |
| WeMM-Embedding-9B | 9B | 79.38 | 81.70 | 64.03 | 83.34 |
| Ovis-VL-Embedding-9B | 9B | 78.94 | 81.03 | 63.45 | 83.06 |
| **GeeVec-Embeddings-mm-1.0** | 9.41B | 78.78 | **81.82** | 59.66 | **83.63** |
| DME-Large | – | 78.76 | 79.64 | 63.63 | 83.36 |
| WeMM-Embedding-4B | 4.54B | 78.19 | 80.80 | 62.71 | 82.04 |
| Wianmu-5B-v0 | 5.25B | 77.89 | 80.68 | 61.42 | 81.99 |
| octen-vl-embedding-large | – | 77.76 | 80.62 | 65.13 | 80.54 |
| Qwen3-VL-Embedding-8B | 8B | 77.28 | 80.16 | 57.74 | 82.36 |
| DME-Medium | 9.4B | 77.00 | 78.23 | 60.07 | 82.02 |
| seed1.6-embedding | – | 77.02 | 79.33 | 57.48 | 82.38 |

Rows are the card's; order here is by AVG (the card lists GeeVec last and bolds column maxima).[^geevec-page]

**Interpretation (Synthesis):**
- GeeVec ranks fourth of the eleven rows by AVG, about 0.8 points behind Sentio and 0.6 behind WeMM-9B, whose Video (64.03/65.45) is 4–6 points higher than its 59.66. Its edge is static content: Image +0.1 and VisDoc +0.3 over WeMM-9B. For a corpus of page images or photos it is on par with the leaders; for video or moment retrieval it trails them and several smaller models, including WeMM-4B and Wianmu-5B-v0.
- Internal consistency check (Reproduced arithmetic on the card's numbers): the 12/8/24 weighting of Image/Video(+moment)/VisDoc gives (12·81.82 + 8·59.66 + 24·83.63)/44 = 78.78, matching the reported AVG, so the AVG is consistent with the stated 44-dataset composition; per-dataset scores were not supplied.
- These 44 retrieval-only AVG values must not be merged with the 78-task MMEB-v2 "All" scores (WeMM-9B 80.6 in [WeMM-Embedding](wemm-embedding.md)) or with MMEB-v3 scores; WeMM-9B appears here as 79.38 because the subset excludes classification, QA, and other task types. No MMEB-v3, MTEB/MMTEB, or ViDoRe score is reported, and audio is not listed.

## Limitations and open questions

- Self-reported; baselines' numbers are copied from unspecified sources and some entries have no size (proprietary or unstated). No per-dataset results, seeds, or evaluation code are linked.
- No training data, loss, or distillation details; the Hub tag `arxiv:2608.02148` is the same paper the card links for DME-Medium/Large, and DME-Medium has a similar size (9.4B), but the page does not say the two are related and their scores differ (77.00 vs 78.78). Treat any relationship as **Unverified**.
- Loading requires a `modeling.py` that is not in the captured page; the `AutoModel` snippet on the Hub is generic.
- Coverage: the entry is an HTML page capture. The file tree, weights metadata (safetensors parameter breakdown, dtype), model tree, and the linked API documentation and arXiv paper were not supplied or inspected. Site navigation, scripts, widgets, and the downloads panel were excluded as non-substantive.

## Relationships

- **Shares backbone and width with:** [WeMM-Embedding](wemm-embedding.md) 9B (Qwen3.5-9B, 4,096-d) and the 9B tier of [UEmbed](uembed.md); it is not documented as derived from either.
- **Compared against (in the card's table):** [WeMM-Embedding](wemm-embedding.md) 4B/9B, [Sentio](sentio.md), [Wianmu-5B](wianmu-5b.md) (as Wianmu-5B-v0), [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md), and Ovis-VL-Embedding-9B (sibling of [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md)).
- **Compared in:** [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md).

[^geevec-page]: [geevec-ai/geevec-embeddings-mm-1.0 model page](../raw/geevec-ai-geevec-embeddings-mm-1.0.md), HTML capture; sections Introduction (technical highlights), Usage (Transformers, Visual-Document Retrieval, Text-to-Video Retrieval), Notes, Evaluation → MMEB-v2 Retrieval table; embedded Hub metadata (`cardData`, `createdAt`, `lastModified`, `likes`, `tags`, `transformersInfo`). Author-reported; capture date not recorded (Hub `lastModified` 2026-10-22).
