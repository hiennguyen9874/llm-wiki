---
type: Concept
title: GELATO
description: A frozen-tower method for extending an existing text embedding space to image, video, and audio using small, task-specific modality projectors.
tags: [embedding, multimodal, retrieval, alignment, efficient-training]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T20:04:02+07:00 }
sources:
  - id: jina-v5-omni-report
    resource: ../raw/2605.08384_jina-embeddings-v5-omni/main.tex
    title: jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers
---

# GELATO

GELATO (Geometry-preserving Embeddings via Locked Aligned TOwers) extends a pretrained text embedding model with frozen vision and audio towers, training only compact modality projectors and delimiter-token embeddings. The report applies it to Jina Embeddings v5 Text Nano and Small, preserving their text path bit-for-bit while mapping text, image, video, and audio into the text-aligned embedding space; it reports that the trained connecting components are 0.35% of joint-model weights. [^jina-v5-omni-report]

## Method

- Non-text encoder states are projected into the text backbone's hidden space and inserted into a serialized token sequence at modality-placeholder positions. The frozen text transformer then produces a last-token-pooled, L2-normalized embedding. Video is serialized as sampled visual-frame segments, with an extracted audio segment preceding them when present. [^jina-v5-omni-report]
- For vision, the retained Qwen visual merger applies LayerNorm, a fixed 2×2 spatial merge, a frozen first fully connected layer, GELU, and a trainable second layer. Audio uses one trainable linear projection from the frozen Qwen2.5-Omni audio encoder's 1,280-dimensional states. [^jina-v5-omni-report]
- Training is independent for each modality and for retrieval, text matching, clustering, and classification. The model selects the corresponding inherited text LoRA adapter together with task-specific projector and delimiter weights; modality towers can be omitted when unused. [^jina-v5-omni-report]

## Training recipe and disclosure

The reported recipe uses bidirectional in-batch InfoNCE at temperature 0.02, summed over Matryoshka prefixes. It trains 16 projector runs (two scales × four tasks × two modalities), each for 15,000 steps with AdamW, bf16 distributed data parallelism on four H100 GPUs, global batch size 256, and a 2e-4 learning rate after 500 warmup steps. [^jina-v5-omni-report]

The paper discloses semantic mixture proportions but not source dataset names, licenses, sample counts, filtering, deduplication, or contamination controls. Image tokens are reported as 35.5% natural photos, 30.3% medical imagery, and 23.7% documents/OCR; audio tokens are 55.0% music and 25.5% environmental sounds, with 14.2% English and 3.1% multilingual speech. These are authors' reported proportions, not a reproducible corpus specification. [^jina-v5-omni-report]

## Reported efficiency and limits

For the paper's 15k-step measurements, projector-only vision training was reported as 1.8× faster than full training and audio projector-only training as 3.2–3.9× faster, with lower peak GPU memory in every compared configuration. The authors' ablations found that unfreezing an encoder from a randomly initialized projector regressed on their short runs; an audio-encoder continuation after projector convergence improved their 8-task MAEB subset by 0.022. This is report-specific evidence, not a general guarantee for frozen-tower alignment. [^jina-v5-omni-report]

The report also finds weaker video performance and weaker Matryoshka preservation for video than for text, images, and audio at small prefix dimensions. Its multimodal benchmark and geometry results are author-reported and not independently reproduced. [^jina-v5-omni-report]

## Relationships

- **Implemented by:** [Jina Embeddings v5 Omni Nano](jina-embeddings-v5-omni-nano.md) and [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md). [^jina-v5-omni-report]
- **Extends:** [Jina Embeddings v5 Text Nano](jina-embeddings-v5-text-nano.md) and [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md) without changing their text-encoder weights. [^jina-v5-omni-report]

[^jina-v5-omni-report]: [jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers](../raw/2605.08384_jina-embeddings-v5-omni/main.tex). Author technical report; architectural, training, efficiency, and benchmark claims are reported by its authors and were not independently reproduced. Embedded PDF charts were not rendered; compiled performance claims come from the report's prose and tables.
