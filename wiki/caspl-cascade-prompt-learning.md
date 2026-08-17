---
type: Concept
title: CasPL cascade prompt learning
description: A two-phase CLIP prompt-adaptation framework that distills domain knowledge into frozen boosting prompts before learning task-specific adapting prompts.
tags: [multimodal-learning, prompt-learning, knowledge-distillation, few-shot-learning, efficient-adaptation]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T04:00:00Z }
sources:
  - id: wu-2024-caspl
    resource: ../raw/2409.17805_CasPL/main.tex
    title: Cascade Prompt Learning for Vision-Language Model Adaptation
---

# CasPL cascade prompt learning

Cascade Prompt Learning (CasPL) splits CLIP prompt adaptation into a domain-general distillation stage and a task-specific few-shot stage. It first learns multimodal boosting prompts for a frozen smaller CLIP student from a larger frozen CLIP teacher using unlabeled domain images, then freezes those prompts and cascades them with a baseline method's learnable adapting prompts.[^wu-2024-caspl]

## Method

- In the boosting phase, CasPL attaches learnable prompts to the student's text and vision encoders and minimizes KL divergence between student and teacher class-logit distributions over unlabeled domain images. The reported student is OpenAI CLIP ViT-B/16 and the teacher ViT-L/14; all CLIP weights remain frozen.[^wu-2024-caspl]
- In the adapting phase, the fixed boosting prompts are combined with new, trainable adapting prompts and optimized on labeled few-shot data using the integrated baseline's original loss. The paper instantiates this plug-in for CoOp, CoCoOp, MaPLe, and PromptSRC.[^wu-2024-caspl]
- The reported default boosting configuration uses depth 12, eight prompt tokens, SGD at learning rate 0.0025, a distillation temperature of 1, and 20 epochs. These are experimental settings, not method requirements.[^wu-2024-caspl]

## Reported findings

- On the reported 11-dataset, 16-shot base-to-novel benchmark, PromptSRC + CasPL averaged 86.11% base accuracy, 79.54% novel accuracy, and 82.69% harmonic mean, versus PromptSRC's 84.26%, 76.10%, and 79.97%. This is a result for the paper's protocol, not a general ranking.[^wu-2024-caspl]
- Across the same suite, the source reports harmonic-mean increases when CasPL wraps CoOp (+7.64), CoCoOp (+4.95), MaPLe (+3.41), and PromptSRC (+2.72). Its few-shot figure reports that the PromptSRC-based configuration was higher than the compared methods at each of 1, 2, 4, 8, and 16 shots.[^wu-2024-caspl]
- In the ImageNet source-to-shift experiment, PromptSRC + CasPL increased the reported target average from 63.90% to 64.44%, while individual target results were mixed. The source also reports that in-domain unlabeled data outperformed its ImageNet out-of-domain variant on a 10-dataset few-shot comparison.[^wu-2024-caspl]
- In ablations, freezing the boosting prompts in phase two outperformed keeping them learnable at matched prompt lengths, and the best reported 10-dataset harmonic mean (83.51%) used eight prompts in each phase. Increasing prompted depth in either phase improved the source's reported average.[^wu-2024-caspl]

## Limits and trade-offs

- CasPL needs unlabeled images from each target domain and an additional first-stage teacher-distillation run; its negligible *inference* overhead does not mean adaptation is training-free.[^wu-2024-caspl]
- The evidence is limited mainly to frozen CLIP ViT-B/16 students, a ViT-L/14 teacher, few-shot image classification, and selected distribution shifts. It does not establish behavior for retrieval, generation, other model families, or arbitrary domains.[^wu-2024-caspl]
- Results are averages over three runs, but the source gives no uncertainty intervals or significance tests for the reported method differences. Small gains should therefore not be treated as conclusive.[^wu-2024-caspl]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by retaining frozen CLIP encoders while learning added prompts for domain distillation and downstream adaptation.[^wu-2024-caspl]
- Extends: [CoOp context optimization](coop-context-optimization.md), [CoCoOp conditional context optimization](cocoop-conditional-context-optimization.md), and [MaPLe multimodal prompt learning](maple-multimodal-prompt-learning.md) by prepending a trained, frozen boosting-prompt module to their adapting prompts.[^wu-2024-caspl]
- Extends: [PromptSRC self-regulating prompts](promptsrc-self-regulating-prompts.md) with the same frozen boosting-prompt module while retaining PromptSRC's adapting-phase losses.[^wu-2024-caspl]

[^wu-2024-caspl]: Wu et al., “Cascade Prompt Learning for Vision-Language Model Adaptation” (ECCV 2024), [complete source manuscript](../raw/2409.17805_CasPL/main.tex) and its local `suppl.tex`. The supplied framework, comparison, ablation, and few-shot figures were rendered and visually inspected.
