---
type: Concept
title: WiSE-FT robust zero-shot fine-tuning
description: A fine-tuning method that interpolates zero-shot and fine-tuned weights to retain distribution-shift accuracy without adding inference cost.
tags: [multimodal-learning, transfer-learning, fine-tuning, distributional-robustness, weight-averaging]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:07:36Z }
sources:
  - id: wortsman-2021-wise-ft
    resource: ../raw/2109.01903_WiSE-FT/main.tex
    title: Robust fine-tuning of zero-shot models
---

# WiSE-FT robust zero-shot fine-tuning

WiSE-FT (weight-space ensembling for fine-tuning) first fine-tunes a zero-shot model on a target distribution, then linearly interpolates every compatible parameter with its original zero-shot checkpoint. In the paper's image-classification experiments, this often improved both target and natural-distribution-shift accuracy versus conventional fine-tuning while retaining a single model for inference.[^wortsman-2021-wise-ft]

## Method

- Given zero-shot parameters $\theta_0$, fine-tuned parameters $\theta_1$, and a mixing coefficient $\alpha \in [0,1]$, WiSE-FT evaluates $f(x, (1-\alpha)\theta_0 + \alpha\theta_1)$. The checkpoints must have matching parameter keys and shapes.[^wortsman-2021-wise-ft]
- The method applies after either end-to-end fine-tuning or linear-classifier-only fine-tuning. When only the classifier changes and the encoder is fixed, interpolating weights is exactly an output/logit-space ensemble; for end-to-end tuning it is not generally equivalent because the network is nonlinear in its parameters.[^wortsman-2021-wise-ft]
- Unlike output-space ensembling, the interpolated checkpoint has the inference and storage profile of one model. The paper cautions implicitly through its empirical scope: arbitrary independently trained networks are not expected to interpolate well; the reported useful paths join a pretrained checkpoint and its fine-tuned descendant.[^wortsman-2021-wise-ft]
- The authors recommend $\alpha=0.5$ when no domain knowledge is available. Selecting a different $\alpha$ requires no retraining, but the paper's per-metric “optimal” values are selected using the corresponding evaluation metric, so they are not a deployment-time selection procedure by themselves.[^wortsman-2021-wise-ft]

## Reported evidence

- For CLIP ViT-L/14@336px fine-tuned end-to-end on ImageNet, $\alpha=0.5$ raised ImageNet top-1 from 86.2% to 86.8% and the mean of five natural ImageNet-derived shifts from 68.6% to 76.9%. The five shifts were ImageNet-V2, ImageNet-R, ImageNet Sketch, ObjectNet, and ImageNet-A; these are results for this backbone, protocol, and evaluation set.[^wortsman-2021-wise-ft]
- Across six additional reported shifts, fixed-$\alpha$ WiSE-FT improved shifted performance by 1.7 to 23.2 percentage points over the fine-tuned endpoint while reference performance fell by at most 0.3 points in those experiments. The tasks span video perturbations, CIFAR reproductions, and WILDS geographic/temporal settings, with task-specific metrics.[^wortsman-2021-wise-ft]
- Fine-tuning hyperparameters with similar ImageNet accuracy could differ by as much as eight points on shifted accuracy in the reported CLIP study. Weight interpolation formed a higher accuracy--shift-accuracy frontier than varying the shown learning rates, epochs, optimizers, or regularization settings; this is comparative empirical evidence, not a guarantee for other model families.[^wortsman-2021-wise-ft]
- The authors observed diverse predictions between zero-shot and fine-tuned classifiers. On most examined shifts, the zero-shot classifier had the larger logit margin and more often determined the ensemble's prediction when the two disagreed; ImageNet was generally the reverse. They offer this complementarity, along with a low-error linear path between endpoints, as an explanation rather than a proven causal mechanism.[^wortsman-2021-wise-ft]

## Limits

- The evaluation is limited to image classification. It does not establish benefits for detection, natural-language processing, or arbitrary fine-tuning tasks, and it leaves target-specific selection of $\alpha$ open.[^wortsman-2021-wise-ft]
- WiSE-FT inherits the biases and misuse risks of its zero-shot base models, including potential bias and surveillance-related harms identified for CLIP-like systems.[^wortsman-2021-wise-ft]
- The source manuscript was read in full. Its 31 local figure PDFs were enumerated; the central method, hyperparameter, and diversity figures were visually inspected, while claims here rely on the manuscript text, tables, and captions rather than uninspected visual-only details.

## Relationships

- Adapts: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by fine-tuning its zero-shot classifier and/or encoders, then interpolating with the original checkpoint.[^wortsman-2021-wise-ft]
- Evaluated with: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md); the paper reports similar interpolation trends for ALIGN, but this does not modify ALIGN pre-training.[^wortsman-2021-wise-ft]
- Compared with: [CoOp context optimization](coop-context-optimization.md) in a 16-shot-per-class ImageNet experiment; WiSE-FT and CoOp change different parts of a CLIP system and could in principle be combined, but the source does not evaluate that combination.[^wortsman-2021-wise-ft]

[^wortsman-2021-wise-ft]: Wortsman et al., “Robust fine-tuning of zero-shot models” (2021), [source manuscript](../raw/2109.01903_WiSE-FT/main.tex).