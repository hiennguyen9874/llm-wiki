---
type: Concept
title: ColPali vision-space document retrieval
description: A late-interaction retriever that indexes document-page images as VLM multi-vector embeddings, avoiding OCR, layout parsing, and chunking at ingestion.
tags: [document-retrieval, multimodal-retrieval, late-interaction, vision-language-models, rag]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:45:00Z }
sources:
  - id: faysse-2024-colpali
    resource: ../raw/2407.01449_ColPali.md
    title: Efficient Document Retrieval with Vision Language Models
  - id: faysse-2025-colpali-camera-ready
    resource: ../raw/2407.01449_ColPali/iclr2025_conference.tex
    title: ColPali: Efficient Document Retrieval with Vision Language Models
  - id: faysse-2025-colqwen2
    resource: ../raw/2407.01449_ColQwen2.md
    title: Efficient Document Retrieval with Vision Language Models
  - id: teiletche-2025-modernvbert
    resource: ../raw/2510.01149_ColModernVBert.md
    title: ModernVBERT: Towards Smaller Visual Document Retrievers
---

# ColPali vision-space document retrieval

ColPali retrieves document pages directly from page images: a PaliGemma-3B vision-language model produces multi-vector page and text-query representations, and a ColBERT-style late-interaction score ranks pages. By avoiding OCR, layout detection, chunking, and optional captioning during ingestion, it provides an end-to-end trainable alternative for visually rich document retrieval; its reported advantage is contingent on the ViDoRe evaluation and tested baselines.[^faysse-2025-colpali-camera-ready]

## Architecture and training

- A projection maps every PaliGemma output token embedding—image patch or text—to 128 dimensions. Page images retain projected image-patch vectors; queries retain projected text-token vectors, and each query term scores against its maximum-similarity page vector before those maxima are summed.[^faysse-2025-colpali-camera-ready]
- The reported reference run trains for one epoch on 118,695 query-page pairs: 63% from academic datasets and 37% from web-crawled PDFs with Claude-3-Sonnet-generated questions. The authors reserve 2% for validation, use English-only training data, and state that no multipage PDF spans the train and ViDoRe sets.[^faysse-2025-colpali-camera-ready]
- Training applies LoRA ($r = \alpha = 32$) to language-model transformer layers and the new projection layer, with a pairwise objective against the hardest in-batch negative. Five special tokens are appended to each query as learnable query expansion or reweighting buffers.[^faysse-2025-colpali-camera-ready]

## Reported findings and limits

- On ViDoRe, the reference ColPali scored 81.3 aggregate nDCG@5, versus 67.0 for the listed Unstructured-plus-captioning BGE-M3 pipeline and 58.8 for the PaliGemma single-vector variant. These are results on the supplied benchmark and baselines, not a deployment guarantee.[^faysse-2025-colpali-camera-ready]
- On the paper's NVIDIA L4 setup, document-page encoding took 0.39 s for ColPali versus 7.22 s for the Unstructured-plus-captioning pipeline. Query encoding took about 30 ms, with roughly 1 ms additional late interaction per 1,000 pages for smaller corpora; measurements depend on the stated hardware, batching, corpus, and implementation.[^faysse-2025-colpali-camera-ready]
- Storing projected vectors for all image patches plus six prompt tokens required 257.5 KB per page in float16. Hierarchical mean pooling by a factor of three reduced vectors by 66.7% while retaining 97.8% of reported performance, but the text-dense Shift task degraded more sharply.[^faysse-2025-colpali-camera-ready]
- In reported ablations, the 512-patch model trailed the 1,024-patch reference by 24.8 nDCG@5. Training the vision encoder reduced the aggregate score by 0.7, and replacing the hard-negative pairwise objective with in-batch negatives reduced it by 1.6; these are limited experimental findings rather than general rules.[^faysse-2025-colpali-camera-ready]
- The training set is English-only and the benchmark covers English and French PDF-like pages. Its practical-task queries are partly VLM-generated, and candidate corpus sizes are limited to make expensive baselines feasible; neither broad language coverage nor large-corpus behavior is directly established.[^faysse-2025-colpali-camera-ready]

## Relationships

- Uses: [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md) as the vision encoder within its PaliGemma backbone.[^faysse-2024-colpali]
- Evaluated by: [ViDoRe visual document retrieval benchmark](vidore-visual-document-retrieval-benchmark.md).[^faysse-2024-colpali]
- Extended by: [ColQwen2 vision-space document retrieval](colqwen2-vision-space-document-retrieval.md), which retains the late-interaction retrieval strategy with a Qwen2-VL backbone.[^faysse-2025-colqwen2]
- Extended by: [ModernVBERT small visual document retriever](modernvbert-small-visual-document-retriever.md), which applies the late-interaction retrieval pattern to a natively bidirectional early-fusion encoder.[^teiletche-2025-modernvbert]

[^faysse-2024-colpali]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2024), [source](../raw/2407.01449_ColPali.md).
[^faysse-2025-colpali-camera-ready]: Faysse et al., “ColPali: Efficient Document Retrieval with Vision Language Models” (2025 camera-ready manuscript), [source](../raw/2407.01449_ColPali/iclr2025_conference.tex).
[^faysse-2025-colqwen2]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2025 version), [source](../raw/2407.01449_ColQwen2.md).
[^teiletche-2025-modernvbert]: Teiletche et al., “ModernVBERT: Towards Smaller Visual Document Retrievers” (2025), [source](../raw/2510.01149_ColModernVBert.md).
