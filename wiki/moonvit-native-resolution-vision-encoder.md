---
type: Concept
title: MoonViT native-resolution vision encoder
description: A standalone native-resolution vision encoder initialized from and continually pre-trained on SigLIP-SO-400M, distributed separately from Kimi-VL-A3B-Instruct.
tags: [vision-encoders, image-feature-extraction, siglip, native-resolution, checkpoint]
status: draft
created: 2026-08-18
generated: { by: llm-wiki-agent/1, at: 2026-08-18T11:23:58Z }
sources:
  - id: moonshotai-moonvit-so-400m-2026
    resource: ../raw/MoonViT-SO-400M.md
    title: MoonViT-SO-400M
---

# MoonViT native-resolution vision encoder

MoonViT is a standalone native-resolution vision encoder initialized from and continually pre-trained on SigLIP-SO-400M. Its implementation and weights were separated from the Kimi-VL-A3B-Instruct release to support direct use as an image-feature extractor.[^moonshotai-moonvit-so-400m-2026]

## Documented use

- The supplied example loads the model with `AutoModel.from_pretrained` and its processor with `AutoImageProcessor.from_pretrained`; both calls set `trust_remote_code=True`.[^moonshotai-moonvit-so-400m-2026]
- The processor receives a PIL image and returns `pixel_values` and `image_grid_hws`. The example passes both to the model and receives image features; for its demonstration image, the first feature tensor has bf16 dtype and shape `[1092, 4, 1152]`.[^moonshotai-moonvit-so-400m-2026]

## Limits and evidence boundaries

- The source is a brief model card. It identifies the model lineage and provides a loading example, but does not specify architecture, parameter count, pretraining data, training procedure, benchmarks, licensing terms beyond a `mit` metadata field, or evaluation results. Claims beyond the documented interface and lineage are unsupported by this source.[^moonshotai-moonvit-so-400m-2026]
- The shown feature shape is an example-specific output, not a documented fixed output contract for every image or preprocessing configuration.[^moonshotai-moonvit-so-400m-2026]

## Relationships

- Initialized from: [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md), specifically the SigLIP-SO-400M checkpoint named by the model card.[^moonshotai-moonvit-so-400m-2026]

[^moonshotai-moonvit-so-400m-2026]: Moonshot AI, “MoonViT-SO-400M” (checkpoint card, accessed 2026-08-18), [supplied source](../raw/MoonViT-SO-400M.md).
