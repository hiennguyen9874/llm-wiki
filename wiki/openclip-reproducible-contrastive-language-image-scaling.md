---
type: Concept
title: OpenCLIP reproducible contrastive language–image scaling
description: A public-data and open-code scaling study finding task- and dataset-dependent power-law trends for CLIP-style models across zero-shot classification, retrieval, linear probing, and fine-tuning.
tags: [multimodal-learning, contrastive-learning, scaling-laws, reproducibility, web-scale-training, zero-shot-transfer]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:40:22Z }
sources:
  - id: cherti-2022-openclip-scaling
    resource: ../raw/2212.07143_OpenCLIP-Scaling/main.tex
    title: Reproducible scaling laws for contrastive language-image learning
  - id: cherti-2022-openclip-scaling-appendix
    resource: ../raw/2212.07143_OpenCLIP-Scaling/appendix.tex
    title: "Supplementary: Reproducible scaling laws for contrastive language-image learning"
---

# OpenCLIP reproducible contrastive language–image scaling

This study trains CLIP-style OpenCLIP models with public LAION data and open tooling while varying model size, dataset size, and samples seen. It reports power-law-like improvements across zero-shot classification, retrieval, linear probing, and fine-tuning, but finds that the fitted trend depends on both task type and the pre-training dataset: its LAION/OpenCLIP models scale more favorably for retrieval, while the compared WIT-trained OpenAI CLIP models scale more favorably for ImageNet classification and the evaluated robustness suite.[^cherti-2022-openclip-scaling]

## Experimental design

- The main grid uses ViT-B/32, B/16, and L/14 image towers with matched text towers; it varies LAION-80M, LAION-400M, and the 2.32B-example English LAION-5B subset called LAION-2B, alongside 3B, 13B, and 34B samples seen. H/14 and g/14 measurements cover only LAION-2B at 34B and 13B samples respectively, so the largest scales are sparsely sampled.[^cherti-2022-openclip-scaling]
- Training uses CLIP's contrastive InfoNCE objective, AdamW, independently scheduled full runs for each samples-seen budget, and global batches generally around 86–88K. The authors report that loss spikes in L/14, H/14, and g/14 runs were resolved by switching mixed precision from float16 to bfloat16; this is an empirical implementation observation, not a universal stability guarantee.[^cherti-2022-openclip-scaling]
- Distributed loss sharding computes local-feature versus all-feature similarities, reducing per-worker similarity storage from an $N \times N$ matrix to two $n \times N$ matrices while requiring differentiable all-gather for correct gradients. The reported ViT-L/14 data-parallel run retained about 84% efficiency at 1,024 GPUs.[^cherti-2022-openclip-scaling-appendix]

## Reported scaling behavior

- On a Pareto frontier over total pre-training compute, the source fits ImageNet zero-shot error exponents of -0.11 for OpenCLIP and -0.16 for the compared OpenAI CLIP models; for the five-image-dataset robustness average, the exponents are -0.13 and -0.24. Those fitted comparisons are observational: WIT is private and the data pipelines differ, so they do not isolate a causal property of either dataset.[^cherti-2022-openclip-scaling]
- The direction reverses for retrieval: the reported MS-COCO Recall@5 error exponents are -0.08 (OpenCLIP) and -0.05 (OpenAI CLIP), and Flickr30K exponents are -0.19 and -0.10. The authors hypothesize that pre-training-data composition drives the task-specific difference, but do not establish that explanation.[^cherti-2022-openclip-scaling]
- Scaling one dimension in isolation can hide gains. For B/32 and B/16 models at 3B or 13B samples seen, moving from LAION-400M to LAION-2B did not reliably help ImageNet; at 34B samples it did. Conversely, L/14 saw little retrieval gain from 13B to 34B samples on LAION-400M, while LAION-2B revealed gains at that additional training exposure.[^cherti-2022-openclip-scaling]
- The largest measured configuration, LAION-2B ViT-H/14 at 34B samples, reached 77.97% zero-shot ImageNet top-1 accuracy and 73.43% MS-COCO image-retrieval Recall@5. Linear probes and the selected fine-tuning experiments also generally improved with scale, though per-task results varied.[^cherti-2022-openclip-scaling-appendix]
- Extrapolations are predictions rather than measurements: the fitted frontier predicts 81.92% ImageNet top-1 and 76.99% MS-COCO Recall@5 for an untrained ViT-G/14 at 68B samples seen. The authors explicitly note possible saturation outside the measured range.[^cherti-2022-openclip-scaling-appendix]

## Evidence limits and governance

- The study reports limited scale-point density, incomplete hyperparameter tuning at high compute, and no ability to generate additional comparable OpenAI CLIP data points because WIT is private. Its deduplication check uses pHash and found roughly 1% overlap for many downstream sets, but 3.80% for ImageNet-R and 5.15% for ImageNet-Sketch; it can miss duplicates and produce false positives.[^cherti-2022-openclip-scaling][^cherti-2022-openclip-scaling-appendix]
- The authors state that public release enables analysis and reuse but should not be read as endorsement for sensitive medical-imaging or surveillance deployments. They also identify potential inherited bias from largely uncurated web data, teacher-based LAION filtering, and the contrastive objective.[^cherti-2022-openclip-scaling-appendix]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by preserving CLIP-style contrastive dual encoders while systematically scaling open models, public LAION data, and training exposure.[^cherti-2022-openclip-scaling]

[^cherti-2022-openclip-scaling]: Cherti et al., “Reproducible scaling laws for contrastive language-image learning” (2022), [source manuscript](../raw/2212.07143_OpenCLIP-Scaling/main.tex).

[^cherti-2022-openclip-scaling-appendix]: Cherti et al., “Supplementary: Reproducible scaling laws for contrastive language-image learning” (2022), [source appendix](../raw/2212.07143_OpenCLIP-Scaling/appendix.tex).
