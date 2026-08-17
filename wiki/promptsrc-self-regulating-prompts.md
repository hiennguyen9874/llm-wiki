---
type: Concept
title: PromptSRC self-regulating prompts
description: A CLIP prompt-learning framework that regularizes deep vision and language prompts against frozen CLIP features, prompt history, and text-template diversity.
tags: [multimodal-learning, prompt-learning, few-shot-learning, transfer-learning, efficient-adaptation, regularization]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T04:00:00Z }
sources:
  - id: khattak-2023-promptsrc
    resource: ../raw/2307.06948_PromptSRC/egpaper_final.tex
    title: "Self-regulating Prompts: Foundational Model Adaptation without Forgetting"
  - id: wu-2024-caspl
    resource: ../raw/2409.17805_CasPL/main.tex
    title: Cascade Prompt Learning for Vision-Language Model Adaptation
---

# PromptSRC self-regulating prompts

PromptSRC adapts frozen CLIP encoders with independent, deep vision and language prompt tokens while explicitly retaining agreement with the unprompted CLIP representation. It combines feature- and logit-level self-consistency, Gaussian-weighted aggregation of prompt states across training, and a text-template ensemble used as frozen text-side supervision.[^khattak-2023-promptsrc]

## Method

- The baseline, Independent Vision-Language Prompting (IVLP), learns separate visual and text prompt tokens at each selected transformer layer while keeping CLIP's encoders frozen. PromptSRC uses four visual and four text tokens; in the reported ViT-B/16 base-to-novel and few-shot configurations, it prompts the first nine transformer layers.[^khattak-2023-promptsrc]
- Alongside classification cross-entropy on prompted image and text features, self-consistency loss applies $L1$ feature matching to prompted versus unprompted image and text features and KL divergence to their prompted versus unprompted similarity-logit distributions. The reported loss weights are 10 for the image term and 25 for the text term.[^khattak-2023-promptsrc]
- For text-side matching, it averages frozen CLIP text features over 60 templates per class during training. This is distinct from using a prompt ensemble to classify at inference: PromptSRC uses the learned prompted features for inference.[^khattak-2023-promptsrc]
- Gaussian weighted prompt aggregation (GPA) accumulates prompt vectors over training, downweighting early, immature prompts and later, task-specialized prompts; the final aggregate is used for inference. The source implements it as a moving aggregate rather than retaining all prompt checkpoints.[^khattak-2023-promptsrc]

## Reported findings

- On the paper's 11-dataset, 16-shot base-to-novel benchmark with ViT-B/16 CLIP, PromptSRC reports 84.26% base accuracy, 76.10% novel accuracy, and 79.97% harmonic mean. The reported MaPLe comparison is 82.28%, 75.14%, and 78.55%, respectively; these are experiment-specific results rather than a general ranking.[^khattak-2023-promptsrc]
- In the component ablation, IVLP's 77.51% harmonic mean increased to 79.55% with self-consistency, 79.70% after GPA, and 79.97% after textual diversity. An $L1$ feature match produced the highest harmonic mean among the source's cosine, MSE, and $L1$ variants.[^khattak-2023-promptsrc]
- For ImageNet-trained domain transfer, the source reports a 60.65% average across ImageNetV2, Sketch, A, and R, compared with 60.27% for MaPLe. Its direct transfer to ten other datasets averages 65.81%, below the reported MaPLe average of 66.30%; results therefore do not support a uniform transfer advantage.[^khattak-2023-promptsrc]
- The paper also reports higher average few-shot accuracy than the compared methods across 1, 2, 4, 8, and 16 shots on the same 11 datasets, and a 2.09-point harmonic-mean gain over IVLP on EVA-CLIP ViT-B/16. These results extend the evidence beyond one backbone but remain within the authors' image-classification evaluation designs.[^khattak-2023-promptsrc]

## Limits and trade-offs

- The primary evidence covers frozen ViT-B/16 CLIP or EVA-CLIP, image classification, and selected video action recognition. It does not establish effects for retrieval, generation, full fine-tuning, other prompt architectures, or arbitrary distribution shifts.[^khattak-2023-promptsrc]
- The reported gains are averages over three runs, while the source does not provide uncertainty intervals or significance tests for the method comparisons. Small differences should not be interpreted as established differences.[^khattak-2023-promptsrc]
- Relative to IVLP on SUN397, PromptSRC adds a frozen-image-encoder pass and precomputed text features: the source reports 179.6 versus 162.8 training GFLOPs and 13.13 versus 12.01 minutes for ten epochs on one A100, with identical reported inference GFLOPs and throughput. These costs are implementation-, dataset-, and hardware-specific.[^khattak-2023-promptsrc]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by retaining both frozen encoders while learning prompt tokens and using unprompted CLIP features as regularization targets.[^khattak-2023-promptsrc]
- Related: [CoOp context optimization](coop-context-optimization.md) and [CoCoOp conditional context optimization](cocoop-conditional-context-optimization.md) are frozen-CLIP prompt-learning baselines; PromptSRC instead uses static deep prompts in both branches plus self-regularization.[^khattak-2023-promptsrc]
- Compared with: [MaPLe multimodal prompt learning](maple-multimodal-prompt-learning.md). MaPLe couples language prompts to visual prompts with learned projections, whereas PromptSRC learns independent prompts and anchors their representations to frozen CLIP features.[^khattak-2023-promptsrc]
- Extended by: [CasPL cascade prompt learning](caspl-cascade-prompt-learning.md), which learns frozen multimodal boosting prompts through unlabeled-domain teacher distillation before PromptSRC learns its adapting prompts with the original losses.[^wu-2024-caspl]

[^khattak-2023-promptsrc]: Khattak et al., “Self-regulating Prompts: Foundational Model Adaptation without Forgetting” (2023), [complete manuscript source](../raw/2307.06948_PromptSRC/egpaper_final.tex). All supplied tables and PNG figures were inspected; the supplied few-shot comparison PDF was rendered and visually inspected.

[^wu-2024-caspl]: Wu et al., “Cascade Prompt Learning for Vision-Language Model Adaptation” (2024), [complete source manuscript](../raw/2409.17805_CasPL/main.tex).
