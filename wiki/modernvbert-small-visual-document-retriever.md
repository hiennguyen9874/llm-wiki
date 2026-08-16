---
type: Concept
title: ModernVBERT small visual document retriever
description: A 250M-parameter early-fusion vision–language encoder and late-interaction variant designed for efficient visual document retrieval.
tags: [document-retrieval, multimodal-retrieval, late-interaction, vision-language-models, efficient-models]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:50:37Z }
sources:
  - id: teiletche-2025-modernvbert
    resource: ../raw/2510.01149_ColModernVBert.md
    title: ModernVBERT: Towards Smaller Visual Document Retrievers
---

# ModernVBERT small visual document retriever

ModernVBERT is a 250M-parameter early-fusion visual encoder that combines a bidirectional ModernBERT text encoder with a SigLIP2 vision encoder. Its ColModernVBERT late-interaction variant is trained specifically for visual document retrieval; the authors report a 68.6 average nDCG@5 across ViDoRe v1 and English ViDoRe v2, close to much larger late-interaction VLM retrievers at 20 ms CPU query-encoding latency on their benchmark hardware.[^teiletche-2025-modernvbert]

## Architecture and training

- Image-patch representations from a SigLIP2 vision tower are projected into the language-model embedding space and processed jointly with text in an early-fusion architecture. The final model pairs a 150M bidirectional text encoder with a roughly 100M vision encoder.[^teiletche-2025-modernvbert]
- Modality alignment uses masked-language modeling and bidirectional attention, followed by contrastive post-training. The final model receives 10B alignment tokens plus a 2B-token, 2,048-pixel-resolution cooldown stage.[^teiletche-2025-modernvbert]
- ColModernVBERT retains query and document token vectors and scores them with late interaction (sum of each query token’s maximum dot product over document tokens). Its document-specialization mix combines document-image/query pairs with text-only retrieval pairs at a 2:1 text-to-image ratio and uses hard negatives.[^teiletche-2025-modernvbert]

## Reported findings and limits

- In the paper’s controlled setup, native bidirectional attention produced a 10.6 nDCG@5 late-interaction improvement over causal attention; merely removing the causal mask during later training did not recover that result. Single-vector results differed much less.[^teiletche-2025-modernvbert]
- Higher image resolution and a high-resolution alignment cooldown improved document retrieval, while the reported natural-image retrieval and classification results did not improve in parallel. Interleaved text-only pairs improved the reported document-retrieval score, illustrating cross-modal transfer in the jointly aligned representation space.[^teiletche-2025-modernvbert]
- On the reported ViDoRe results, ColModernVBERT scored 81.2 on v1 and 56.0 on English v2 (68.6 average), versus 81.6 and 56.8 (69.2 average) for ColPali; the model’s advantage is primarily the performance-size/latency trade-off, not the highest absolute score.[^teiletche-2025-modernvbert]
- The study is English-only and focuses on relatively small models, so its conclusions about language coverage and scaling to larger architectures remain untested.[^teiletche-2025-modernvbert]

## Relationships

- Uses: [SigLIP 2 multilingual vision–language encoders](siglip2-multilingual-vision-language-encoders.md) as its vision tower.[^teiletche-2025-modernvbert]
- Builds on: [ColPali vision-space document retrieval](colpali-vision-space-document-retrieval.md) by applying the same late-interaction retrieval pattern to a natively bidirectional early-fusion encoder.[^teiletche-2025-modernvbert]
- Evaluated by: [ViDoRe visual document retrieval benchmark](vidore-visual-document-retrieval-benchmark.md), including English ViDoRe v2 splits.[^teiletche-2025-modernvbert]

[^teiletche-2025-modernvbert]: Teiletche et al., “ModernVBERT: Towards Smaller Visual Document Retrievers” (2025), [source](../raw/2510.01149_ColModernVBert.md).
