---
type: Concept
title: PromptAlign test-time distribution alignment
description: A test-time CLIP prompt-adaptation method that aligns visual-token mean and variance to offline proxy-source statistics alongside entropy minimization.
tags: [test-time-adaptation, prompt-learning, distribution-alignment, zero-shot-transfer, multimodal-learning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:57:27Z }
sources:
  - id: hassan-2023-promptalign
    resource: ../raw/2311.01459_TDA/Manuscript.tex
    title: "Align Your Prompts: Test-Time Prompting with Distribution Alignment for Zero-Shot Generalization"
---

# PromptAlign test-time distribution alignment

PromptAlign adapts MaPLe-style multimodal prompts for each test image while CLIP's encoder weights remain frozen. It combines TPT-style entropy minimization over augmented views with an L1 loss that aligns visual-token mean and variance at prompted encoder layers to statistics precomputed from a proxy source dataset.[^hassan-2023-promptalign]

## Method

- The method obtains multiple augmented views of one test image, computes prompted visual-token means and variances at each selected vision-transformer layer, and penalizes their L1 distance from offline source statistics. The final objective is entropy loss plus a scaled alignment loss; optimizing it updates the text and visual prompts for that test sample.[^hassan-2023-promptalign]
- CLIP's unreleased pre-training data prevents direct source-statistic estimation. The reported default uses ImageNet as a proxy; the paper motivates this choice by CLIP's ImageNet-oriented tuning and reports a separate LAION400M-proxy ablation.[^hassan-2023-promptalign]
- In the reported ViT-B/16 configuration, MaPLe is trained on 16-shot ImageNet with two prompt tokens at depths 1–3. At test time, PromptAlign uses 63 randomized crop/flip views plus the original image, keeps the lowest-entropy 10% of predictions for the entropy objective, applies the alignment loss across all 64 images, and takes one AdamW update with $\beta=100$.[^hassan-2023-promptalign]

## Reported findings

- On four ImageNet distribution-shift targets, PromptAlign averaged 63.55% top-1 accuracy, compared with 62.31% for MaPLe plus entropy-based TPT and 60.28% for MaPLe alone. It was higher than MaPLe+TPT on all four targets in this table.[^hassan-2023-promptalign]
- On the paper's ten cross-dataset targets, PromptAlign averaged 66.92%, a 0.42-point improvement over MaPLe+TPT (66.50%). It was best or tied for best on seven of the ten target columns in that comparison; the reported average is evidence for this benchmark suite, not a general robustness guarantee.[^hassan-2023-promptalign]
- On ImageNet-A, alignment alone scored 50.85%, essentially matching MaPLe's 50.90%; adding it to entropy minimization reached 59.37%, versus 58.08% for MaPLe+TPT. This ablation supports alignment as a complement or regularizer rather than a discriminative adaptation objective by itself.[^hassan-2023-promptalign]
- Replacing ImageNet proxy statistics with those from a two-million-image LAION400M subset increased the ten-dataset average from 66.92% to 67.17% in the reported ablation. A five-image same-class bag (not the standard single-sample setting) reached 69.59%, showing that more representative test statistics can help under that altered protocol.[^hassan-2023-promptalign]

## Limits and trade-offs

- The source statistics are a prerequisite and their quality matters: ImageNet is an unverified proxy for CLIP's undisclosed pre-training distribution, while the stronger LAION result still uses only a subset. The method does not eliminate this source-distribution assumption.[^hassan-2023-promptalign]
- Evidence is confined to zero-shot image classification, principally an ImageNet-trained ViT-B/16 MaPLe configuration, specified augmentations, and the paper's domain-shift, cross-dataset, and base-to-novel suites. The paper also evaluates ViT-B/32, but does not establish transfer to retrieval, detection, or segmentation.[^hassan-2023-promptalign]
- Test-time optimization adds augmented-view encoder passes. The paper reports 0.216 seconds per sample for PromptAlign versus 0.197 for its MaPLe+TPT comparison, under its hardware and implementation; this is not a deployment-independent latency claim.[^hassan-2023-promptalign]

## Relationships

- Extends: [MaPLe multimodal prompt learning](maple-multimodal-prompt-learning.md) by adapting its coupled visual and text prompts at inference, rather than only learning them from downstream training examples.[^hassan-2023-promptalign]
- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) through frozen-encoder, prompt-based test-time adaptation for zero-shot classification.[^hassan-2023-promptalign]

[^hassan-2023-promptalign]: Hassan et al., “Align Your Prompts: Test-Time Prompting with Distribution Alignment for Zero-Shot Generalization” (2023), [complete manuscript source](../raw/2311.01459_TDA/Manuscript.tex). The supplied appendix, all result tables, and all supplied figures were inspected; bibliography and LaTeX style files were excluded as non-claim-bearing support files.
