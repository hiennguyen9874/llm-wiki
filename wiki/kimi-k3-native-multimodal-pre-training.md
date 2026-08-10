---
type: Concept
title: Kimi K3 native multimodal pre-training
description: Kimi K3 jointly pre-trains text and a from-scratch vision encoder with next-token prediction, then progressively extends context from 8K to one million tokens using cleaned and synthetic long-range data.
tags: [kimi-k3, pre-training, multimodal, long-context]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-10T14:03:17Z }
sources:
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: kimi-k3-modeling-2026
    resource: ../raw/kimi-k3-sources/modeling_kimi_k3.py
    title: "Kimi K3 multimodal reference modeling code"
  - id: kimi-k3-processor-2026
    resource: ../raw/kimi-k3-sources/kimi_k3_processor.py
    title: "Kimi K3 multimodal processor reference code"
---

# Kimi K3 native multimodal pre-training

Kimi K3 jointly optimizes language, images, and video from the start under one next-token objective rather than attaching and aligning a pretrained vision encoder after language pre-training. Its curriculum begins at 8K context, extends to 64K during pre-training, and reaches 256K then 1M during cooldown.[^kimi-k3-2026]

## Data and objective

Text spans web, code, mathematics, and knowledge data, filtered with heuristics, classifiers, and deduplication. The report also rephrases knowledge and mathematics material with diverse prompts and fidelity checks. Vision data includes captions, interleaved documents, OCR, perception, video, and code paired with rendered SVG, 3D, webpage, game, and CAD artifacts.[^kimi-k3-2026]

Visual and textual tokens share one next-token objective and backbone. This supports code–render–inspect loops without a cross-model handoff, but the report does not disclose corpus sizes, mixture weights, rights analysis, or enough provenance to independently audit data governance.[^kimi-k3-2026]

## From-scratch vision pathway

MoonViT-V2 is a 27-layer, approximately 401M-parameter vision transformer trained from scratch with next-token prediction. Images and videos share parameters; attention separates spatial within-frame and temporal across-frame passes. Temporal pooling and $2\times2$ pixel shuffle reduce token count, with reported support for inputs up to $3584\times3584$ pixels.[^kimi-k3-2026]

The report shows lower, less spiky gradient norms than a SigLIP-initialized baseline and says the two match across its vision evaluations. This supports the claim that contrastive initialization was unnecessary in this setup, not that from-scratch vision is universally preferable.[^kimi-k3-2026]

In the released reference path, a strided 2D convolution creates patches; learnable interpolated spatial embeddings and fixed sinusoidal time embeddings are added; and repeated 2D RoPE is applied to vision queries and keys. After encoding, all frames are mean-pooled temporally while each $2\times2$ spatial group is concatenated and projected into language width. Each media placeholder token is then expanded into the corresponding projected visual-token sequence, with attention masks, labels, padding, and position IDs rebuilt around the inserted features.[^kimi-k3-modeling-2026]

## Contradictions

The technical report says MoonViT-V2 factorizes attention into intra-frame spatial and inter-frame temporal passes.[^kimi-k3-2026] The released `modeling_kimi_k3.py` instead flattens each complete $t\times h\times w$ visual grid into one sequence and applies full non-causal self-attention within that media item; temporal identity enters through additive time embeddings, while 2D RoPE is repeated across frames.[^kimi-k3-modeling-2026] The code labels itself a reference architecture implementation and points to the model card for production deployment, so the repository does not establish whether the difference is a simplified public path, a production divergence, or a documentation mismatch.

The public `KimiK3Processor` prepares image media and raises `ValueError` for every other media type, even though the vision configuration retains time-related parameters and the model card describes video capability. The released Transformers processor therefore establishes image-only input support for that path, not usable video inference or a resolution of the attention-structure discrepancy.[^kimi-k3-processor-2026]

## Long-context curriculum

NoPE MLA avoids position-embedding modification during extension; KDA supplies learned positional and recency behavior. The long-context pipeline cleans near-duplicates, binary or malformed files, truncated data, invalid logs, and low-quality video, then upsamples genuinely long documents and videos.[^kimi-k3-2026]

Because length alone may permit local shortcuts, the team also permutes and concatenates multimodal documents and subtasks so answers require evidence scattered across the intended context. Expensive long sequences occupy only a small part of the training budget through progressive extension.[^kimi-k3-2026]

## Optimization

Matrix parameters use Per-Head Muon, with Q/K/V momentum orthogonalized separately by attention head to reduce cross-head scale domination. Training uses weight clipping, Quantile Balancing, cosine decay with 1% warmup, and weight decay 0.1. Independent scaling-law searches favored cosine over warmup-stable-decay under each schedule’s own optimized peak learning rate and batch size.[^kimi-k3-2026]

## Relationships

- **Trains:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) in a per-head form.
- **Uses:** [Stable LatentMoE and Quantile Balancing](stable-latentmoe-and-quantile-balancing.md).

## Evidence limits

The report’s approximately $2.5\times$ scaling-efficiency claim combines architecture, data, and optimization changes and is based on fitted held-out validation loss, so it cannot be assigned to this recipe alone. Long-context support and extrapolation are reported model behavior, not proof of reliable use of every token or every modality across one million positions.[^kimi-k3-2026]

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.4–2.5 and 3.

[^kimi-k3-modeling-2026]: Moonshot AI Team and Hugging Face, “Kimi K3 multimodal reference modeling code,” 2025–2026, [source](../raw/kimi-k3-sources/modeling_kimi_k3.py), especially `MoonVision3dPatchEmbed`, `MoonViT3dEncoder`, `tpool_patch_merger`, the projector classes, and `KimiK3ForConditionalGeneration`.

[^kimi-k3-processor-2026]: Moonshot AI Team and Hugging Face, “Kimi K3 multimodal processor reference code,” [source](../raw/kimi-k3-sources/kimi_k3_processor.py), especially `preprocess_medias`.
