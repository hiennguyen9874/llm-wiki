---
type: Concept
title: ColPali vision-space document retrieval
description: A late-interaction retriever that indexes document-page images as VLM multi-vector embeddings, avoiding OCR, layout parsing, and chunking at ingestion.
tags: [document-retrieval, multimodal-retrieval, late-interaction, vision-language-models, rag]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:50:37Z }
sources:
  - id: faysse-2024-colpali
    resource: ../raw/2407.01449_ColPali.md
    title: Efficient Document Retrieval with Vision Language Models
  - id: faysse-2025-colqwen2
    resource: ../raw/2407.01449_ColQwen2.md
    title: Efficient Document Retrieval with Vision Language Models
  - id: teiletche-2025-modernvbert
    resource: ../raw/2510.01149_ColModernVBert.md
    title: ModernVBERT: Towards Smaller Visual Document Retrievers
---

# ColPali vision-space document retrieval

ColPali retrieves document pages directly from page images: a PaliGemma-3B vision-language model produces multi-vector page and text-query representations, and a ColBERT-style late-interaction score ranks pages. By avoiding OCR, layout detection, chunking, and optional captioning during ingestion, it provides an end-to-end trainable alternative for visually rich document retrieval; its reported advantage is contingent on the ViDoRe evaluation and tested baselines.[^faysse-2024-colpali]

## Method

- A projection maps every PaliGemma output token embedding—image-patch or text—to 128 dimensions. Page images are indexed as their image-patch vectors; queries are represented by their text-token vectors.[^faysse-2024-colpali]
- The late-interaction score sums, for each query vector, its maximum dot product against all page vectors. This retains fine-grained query-to-patch matching while page embeddings are precomputed offline.[^faysse-2024-colpali]
- Training uses query–page pairs and a pairwise contrastive objective that compares the positive page against the hardest in-batch negative. The reported training set contains 118,695 pairs, 63% from academic datasets and 37% synthetic VLM-generated questions; the training data are English-only.[^faysse-2024-colpali]

## Reported trade-offs and findings

- On ViDoRe, the reported aggregate nDCG@5 was 81.3 for ColPali, compared with 67.0 for the strongest listed Unstructured-plus-captioning BGE-M3 pipeline and 58.8 for the PaliGemma single-vector variant. These are benchmark results, not a guarantee for other document collections.[^faysse-2024-colpali]
- The paper reports approximately 30 ms to encode one query and about 1 ms of additional late-interaction time per 1,000 pages for smaller corpora on its tested hardware. It also reports 257.5 KB of uncompressed embedding storage per page, materially more than single-vector approaches.[^faysse-2024-colpali]
- Hierarchical mean token pooling with a factor of three reduced stored vectors by 66.7% while retaining 97.8% of reported original performance; text-dense pages were a noted outlier with greater degradation risk.[^faysse-2024-colpali]
- A higher-resolution, 1,024-patch configuration outperformed a 512-patch variant but consumes more memory; stronger VLM backbones and the patch count create accuracy, latency, and index-size trade-offs.[^faysse-2024-colpali]

## Relationships

- Uses: [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md) as the vision encoder within its PaliGemma backbone.[^faysse-2024-colpali]
- Evaluated by: [ViDoRe visual document retrieval benchmark](vidore-visual-document-retrieval-benchmark.md).[^faysse-2024-colpali]
- Extended by: [ColQwen2 vision-space document retrieval](colqwen2-vision-space-document-retrieval.md), which retains the late-interaction retrieval strategy with a Qwen2-VL backbone.[^faysse-2025-colqwen2]
- Builds on: [ModernVBERT small visual document retriever](modernvbert-small-visual-document-retriever.md), which applies the late-interaction retrieval pattern to a natively bidirectional early-fusion encoder.[^teiletche-2025-modernvbert]

[^faysse-2024-colpali]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2024), [source](../raw/2407.01449_ColPali.md).
[^faysse-2025-colqwen2]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2025 version), [source](../raw/2407.01449_ColQwen2.md).
[^teiletche-2025-modernvbert]: Teiletche et al., “ModernVBERT: Towards Smaller Visual Document Retrievers” (2025), [source](../raw/2510.01149_ColModernVBert.md).
