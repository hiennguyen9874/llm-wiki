---
type: Concept
title: MaPLe multimodal prompt learning
description: A parameter-efficient CLIP adaptation method that couples deep language prompts to vision prompts, adapting both frozen encoder branches for few-shot image classification.
tags: [multimodal-learning, prompt-learning, few-shot-learning, transfer-learning, efficient-adaptation]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T04:00:00Z }
sources:
  - id: khattak-2023-maple
    resource: ../raw/2210.03117_MaPLe/PaperForReview.tex
    title: "MaPLe: Multi-modal Prompt Learning"
  - id: khattak-2023-promptsrc
    resource: ../raw/2307.06948_PromptSRC/egpaper_final.tex
    title: "Self-regulating Prompts: Foundational Model Adaptation without Forgetting"
  - id: hassan-2023-promptalign
    resource: ../raw/2311.01459_TDA/Manuscript.tex
    title: "Align Your Prompts: Test-Time Prompting with Distribution Alignment for Zero-Shot Generalization"
  - id: wu-2024-caspl
    resource: ../raw/2409.17805_CasPL/main.tex
    title: Cascade Prompt Learning for Vision-Language Model Adaptation
---

# MaPLe multimodal prompt learning

MaPLe adapts a frozen CLIP Vision Transformer by learning prompts in both its text and image encoders. At each prompted depth, a learned linear coupling projects the language prompts into vision-prompt space, so the two branches are optimized through linked rather than independent prompt parameters.[^khattak-2023-maple]

## Method

- MaPLe inserts separate learnable context tokens into the first $J$ transformer layers of CLIP's text and vision encoders. The remaining pretrained encoder parameters stay frozen; training updates the prompts and their coupling functions.[^khattak-2023-maple]
- At a prompted layer $k$, the vision prompts are $\tilde{P}_k = \mathcal{F}_k(P_k)$, where $P_k$ are language prompts and $\mathcal{F}_k$ is a learned linear map from text-embedding to vision-embedding dimensionality. This gives gradients a direct path between the prompt branches.[^khattak-2023-maple]
- In the reported ViT-B/16 configuration, text, vision, and shared multimodal embedding dimensions are 512, 768, and 512; the authors use $J=9$ and two prompt tokens in each branch. They initialize only the first-layer language prompts from “a photo of a <category>” and randomly initialize later-layer prompts.[^khattak-2023-maple]
- Independent vision and language prompts are an ablation, not the proposed coupling: their 11-dataset harmonic mean was 77.90%, versus 78.55% for coupled MaPLe under the paper's base-to-novel protocol.[^khattak-2023-maple]

## Reported findings

- Across 11 few-shot base-to-novel classification datasets (16 labeled examples per base class), MaPLe averaged 82.28% base accuracy, 75.14% novel accuracy, and a 78.55% harmonic mean. In the same reported protocol, CoCoOp averaged 80.47%, 71.69%, and 75.83%, respectively.[^khattak-2023-maple]
- With prompts learned on ImageNet and directly transferred to ten target datasets, MaPLe averaged 66.30% accuracy, compared with 65.74% for CoCoOp and 63.88% for CoOp. On ImageNet-based domain-shift targets, it was highest among the compared methods on Sketch, A, and R, while CoOp was higher on ImageNetV2 (64.20% versus 64.07%).[^khattak-2023-maple]
- The source reports its largest base-to-novel gains over CoCoOp on EuroSAT, FGVCAircraft, and DTD. Its per-class and embedding visualizations support a hypothesis that coupled prompts help on less generic or more distribution-shifted categories; they do not identify a causal mechanism or establish the effect outside the evaluated benchmarks.[^khattak-2023-maple]
- In ablations, harmonic-mean performance peaked at nine prompted layers for the reported configuration. Increasing prompt length generally preserved base accuracy but reduced novel-class accuracy, which the authors interpret as overfitting.[^khattak-2023-maple]

## Limits and trade-offs

- The evidence is confined to few-shot image classification with a frozen ViT-B/16 CLIP model, 16-shot training, and the paper's 11-dataset transfer and domain-generalization suites. It does not establish benefits for retrieval, generation, other backbones, or arbitrary downstream shifts.[^khattak-2023-maple]
- MaPLe adds learned prompt and coupling parameters: the reported $J=9$ version has 3.55M trainable parameters (2.85% of CLIP), versus 35,360 for the paper's CoCoOp configuration. A shared-coupling variant with 0.41M parameters scored 78.11% harmonic mean, but this controlled comparison does not eliminate all implementation or hyperparameter effects.[^khattak-2023-maple]
- The reported efficiency advantage over CoCoOp depends on avoiding its per-image text-prompt conditioning. MaPLe still requires its own prompted encoder computation and evaluation protocol; the paper's FLOPS, frames-per-second, and epoch comparisons are implementation- and hardware-specific.[^khattak-2023-maple]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by retaining frozen dual encoders and its text-derived zero-shot classifier while learning downstream prompt parameters in both branches.[^khattak-2023-maple]
- Extends: [CoOp context optimization](coop-context-optimization.md) from shallow, text-only continuous context to deep prompts in both CLIP branches; MaPLe's deep language prompting reduces to CoOp when $J=1$.[^khattak-2023-maple]
- Compared with: [CoCoOp conditional context optimization](cocoop-conditional-context-optimization.md). CoCoOp makes text prompts image-instance-specific through a Meta-Net, whereas MaPLe links static language and vision prompts through per-layer projections.[^khattak-2023-maple]
- Compared with: [PromptSRC self-regulating prompts](promptsrc-self-regulating-prompts.md), which learns independent deep prompts and regularizes their features against frozen CLIP rather than coupling the two prompt branches. PromptSRC's paper reports a higher 11-dataset harmonic mean under its stated protocol; this is not a general ranking.[^khattak-2023-promptsrc]
- Extended by: [PromptAlign test-time distribution alignment](promptalign-test-time-distribution-alignment.md), which updates MaPLe's multimodal prompts for each test sample using entropy minimization and proxy-source visual-token distribution alignment.[^hassan-2023-promptalign]
- Extended by: [CasPL cascade prompt learning](caspl-cascade-prompt-learning.md), which first learns frozen multimodal boosting prompts through unlabeled-domain teacher distillation, then cascades them with MaPLe's adapting prompts.[^wu-2024-caspl]

[^khattak-2023-maple]: Khattak et al., “MaPLe: Multi-modal Prompt Learning” (2023), [complete source manuscript](../raw/2210.03117_MaPLe/PaperForReview.tex). All supplied architecture, comparison, embedding, and ablation figures were visually inspected.

[^khattak-2023-promptsrc]: Khattak et al., “Self-regulating Prompts: Foundational Model Adaptation without Forgetting” (2023), [complete manuscript source](../raw/2307.06948_PromptSRC/egpaper_final.tex).

[^hassan-2023-promptalign]: Hassan et al., “Align Your Prompts: Test-Time Prompting with Distribution Alignment for Zero-Shot Generalization” (2023), [complete manuscript source](../raw/2311.01459_TDA/Manuscript.tex).

[^wu-2024-caspl]: Wu et al., “Cascade Prompt Learning for Vision-Language Model Adaptation” (2024), [complete source manuscript](../raw/2409.17805_CasPL/main.tex).
