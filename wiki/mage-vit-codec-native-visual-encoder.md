---
type: Concept
title: Mage-ViT codec-native visual encoder
description: A 316M video-first Vision Transformer trained from scratch that retains codec-selected patches and their 3D positions for sparse visual encoding.
tags: [vision-encoders, video-understanding, visual-tokenization, efficient-inference, self-supervised-learning]
status: draft
created: 2026-08-18
generated: { by: llm-wiki-agent/1, at: 2026-08-18T11:22:31Z }
sources:
  - id: microsoft-mage-vit-checkpoint-2026
    resource: ../raw/Mage-ViT.md
    title: "Mage-ViT: A Codec-Native Visual Encoder Trained from Scratch"
---

# Mage-ViT codec-native visual encoder

Mage-ViT is a 316M-parameter, video-first Vision Transformer trained from scratch with a cluster-discrimination objective on approximately 100M unlabeled image/video samples. It uses codec-aligned sparse patch selection—retaining all I-frame patches and motion-salient P-frame patches—and shared 3D rotary positions so a variable-length sequence retains its original temporal and spatial coordinates. The supplied checkpoint is the visual encoder only, before joint language-model training.[^microsoft-mage-vit-checkpoint-2026]

## Architecture and sparse representation

- The encoder has 24 pre-norm ViT layers, hidden size 1,024, 16 attention heads, a GELU MLP expanded to 4,096 dimensions, 16×16 patches, and learned-probe multi-head attention pooling. It emits 1,024-dimensional patch and pooled features.[^microsoft-mage-vit-checkpoint-2026]
- Its shared 3D rotary encoding allocates dimensions in a 4:6:6 temporal:height:width split. For video, callers supply a `(t, h, w)` grid coordinate for every input patch, allowing sampled frames to be positioned across a target timeline.[^microsoft-mage-vit-checkpoint-2026]
- The stated HEVC/H.265 selector derives each P-frame patch's importance from motion vectors and residual energy; the DCVC-RT variant uses a learned codec rate map. A 64-frame clip retains all I-frame patches and the top-ranked P-frame patches within a 4,096-token budget, which the card describes as roughly a 75% reduction from its dense grid.[^microsoft-mage-vit-checkpoint-2026]

## Training and interface

- Pretraining proceeds from variable-resolution image training at 224–448 pixels to joint image/video training at 256-pixel video resolution with 64-frame clips and a 4,096-token budget, in bf16.[^microsoft-mage-vit-checkpoint-2026]
- The checkpoint interface accepts image tensors shaped `[B, 3, H, W]` or video tensors shaped `[B, C, T, H, W]`; video additionally accepts `patch_positions` shaped `[B, T * tokens_per_frame, 3]`. Its outputs are `last_hidden_state` shaped `[B, num_patches, 1024]` and `pooler_output` shaped `[B, 1024]`.[^microsoft-mage-vit-checkpoint-2026]
- The card states that codec-driven patch selection occurs upstream in the Mage-VL data pipeline. Thus the standalone interface documents pixels and patch positions, but not an in-model codec parser or a complete selection-pipeline API.[^microsoft-mage-vit-checkpoint-2026]

## Limits and evidence boundaries

- This is a model card for a checkpoint, not an evaluation report: it provides architectural and usage specifications but no benchmark protocol, results table, code snapshot, training-data documentation, or independent replication. Its parameter, data-scale, token-reduction, and codec claims are therefore checkpoint-card assertions.[^microsoft-mage-vit-checkpoint-2026]
- Loading the shown checkpoint requires remote model code and a stated `transformers>=5.7` runtime. The card says scaled-dot-product attention is the default and FlashAttention is optional, but this source does not measure runtime, memory use, or compatibility across systems.[^microsoft-mage-vit-checkpoint-2026]

## Relationships

- Used by: [Mage-VL codec-native streaming vision-language model](mage-vl-codec-native-streaming-vision-language-model.md) as its visual encoder before joint vision-language training.[^microsoft-mage-vit-checkpoint-2026]

[^microsoft-mage-vit-checkpoint-2026]: Microsoft, “Mage-ViT: A Codec-Native Visual Encoder Trained from Scratch” (checkpoint card, accessed 2026-08-18), [supplied source](../raw/Mage-ViT.md).
