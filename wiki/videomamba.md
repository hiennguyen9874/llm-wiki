---
type: Concept
title: VideoMamba
description: An isotropic video backbone that replaces self-attention with bidirectional selective state-space blocks over flattened spatiotemporal patch sequences.
tags: [video, state-space-models, backbones, long-context, representation-learning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:38:10+07:00 }
sources:
  - id: videomamba-paper
    resource: ../raw/2403.06977_VideoMamba/main.tex
    title: "VideoMamba: State Space Model for Efficient Video Understanding"
---

# VideoMamba

VideoMamba is a pure state-space video backbone built in an isotropic ViT-like layout. It turns each frame into non-overlapping 16×16 spatial patches, adds separate spatial and temporal position embeddings plus a class token, and processes the flattened video sequence with stacked bidirectional Mamba blocks. Its selective-scan operator scales linearly with token-sequence length rather than using quadratic self-attention, but the paper demonstrates bounded sparse-frame video processing—not persistent memory or hour-level understanding.[^videomamba-paper]

## Architecture

- A `1×16×16` 3D convolution preserves the input frame count while patchifying each frame spatially.
- Separate learned spatial and temporal embeddings retain position because the state-space scan is order-sensitive.
- Every encoder layer is a bidirectional Mamba block; there are no attention layers, hierarchical downsampling stages, middle class token, or rotary position embeddings.
- The selected **spatial-first** scan orders all spatial tokens frame by frame, then runs forward and backward selective scans. On the paper's Something-Something V2 ablation, it reports 65.1% top-1 versus 62.4% for temporal-first scanning; this supports the chosen ordering under ImageNet initialization, not universal scan optimality.
- Tiny, Small, and Middle variants contain 7M, 26M, and 74M parameters. A 98M Base variant was excluded after suboptimal optimization.

## Training regimes

The paper evaluates three distinct regimes that should not be conflated:

1. **Image initialization and supervised video fine-tuning:** models are pretrained on ImageNet-1K, then fine-tuned on action datasets. To reduce overfitting while scaling the isotropic image model, a trained Small model distills final feature maps into the Middle model with an L2 loss.
2. **Masked video alignment:** a Middle model learns from a frozen CLIP ViT-B teacher for 800 epochs, aligning only final-layer outputs from unmasked tokens. Its Mamba-specific ablation favors continuity-preserving row or attention masks; 80% masking and final-layer-only alignment perform best in the reported setup.
3. **Multimodal pretraining:** the visual encoder is combined with BERT-based text and cross-modal modules and trained with contrastive, matching, masked-language, and unmasked-token-alignment objectives. The largest reported corpus combines about 25.68M image/video samples and 26.81M texts; this stage is therefore not a purely video-only or data-light result.

## Reported evidence

These values are paper-specific and are not directly comparable without matching data, views, input sizes, and training recipes.

| Setting | Reported result | Evidence boundary |
| --- | --- | --- |
| Supervised VideoMamba-M, 64×384² | Kinetics-400 83.3% top-1 | ImageNet-1K initialization; 2,368 GFLOPs per view and 3×4 inference views |
| Mask-aligned VideoMamba-M, 16×288² | Something-Something V2 71.4% top-1 | CLIP ViT-B teacher inherits CLIP-400M pretraining |
| VideoMamba-Ti, 32 sparse frames | LVU: best reported row on 7/9 tasks, tied on one | End-to-end video-level classification/regression over 1–3 minute clips; no boundary localization |
| Mask-aligned VideoMamba-M | Breakfast 97.9% with 32 frames; COIN 90.4% with 64 frames | Kinetics-400-pretrained, end-to-end video-level classification |
| 25M multimodal corpus | ActivityNet zero-shot text-to-video R@1 41.0 | Whole-video retrieval, not temporal grounding |

## Efficiency and long-context limits

On the authors' A100-80GB test with 224×224 inputs, PyTorch 2.1, CUDA 11.8, and batch size 128, the paper reports that a 64-frame VideoMamba variant runs 6× faster and uses 40× less GPU memory than a joint-attention TimeSformer-Ti baseline. This supports an implementation-specific scaling advantage over that baseline; it does not establish the same ratio against factorized, local-attention, convolutional, or newer state-space models.[^videomamba-paper]

The long-video evaluations sparsely sample raw videos in the TSN style and process only 32 or 64 frames. VideoMamba therefore increases the feasible direct token sequence and supports end-to-end training on minute-scale benchmarks, but it can still miss unsampled short events and supplies neither external memory nor arbitrary-duration retrieval. The paper explicitly leaves larger models, audio, LLM integration, and hour-level understanding unvalidated.

## Multimodal scope

VideoMamba improves zero-shot whole-video text retrieval over the paper's similarly trained UMT baselines on several datasets, especially ActivityNet, DiDeMo, and LSMDC. Because those experiments retrieve complete videos and do not output start/end times or test explicit event relations, they demonstrate video-text representation alignment rather than temporal grounding or reasoning.

## Relationships

- **Part of:** [Video temporal representation learning](video-temporal-representation-learning.md) as a selective state-space visual backbone with supervised, teacher-aligned masked, and multimodal pretraining regimes.
- **Supports:** [Temporal action understanding](temporal-action-understanding.md) through clip- and long-video-level classification; it does not directly localize or segment actions.
- **Used for:** [Long-video temporal modeling](long-video-temporal-modeling.md) as a linear-sequence-complexity bounded-context encoder over sparsely sampled frames.
- **Compared in:** [Video backbones and encoders comparison](video-backbones-and-encoders-comparison.md).
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) only as a possible aligned feature encoder; the cited paper demonstrates whole-video retrieval, not temporal grounding.

[^videomamba-paper]: [VideoMamba: State Space Model for Efficient Video Understanding](../raw/2403.06977_VideoMamba/main.tex)
