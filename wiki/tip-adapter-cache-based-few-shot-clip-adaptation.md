---
type: Concept
title: Tip-Adapter cache-based few-shot CLIP adaptation
description: A training-free few-shot CLIP adapter that adds cache retrieval over labeled image embeddings to zero-shot class logits and optionally fine-tunes the cache keys.
tags: [multimodal-learning, few-shot-learning, efficient-adaptation, cache-models, transfer-learning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:13:40Z }
sources:
  - id: zhang-2022-tip-adapter
    resource: ../raw/2111.03930_Tip-Adapter/ReviewTemplate.tex
    title: "Tip-Adapter: Training-free CLIP-Adapter for Better Vision-Language Modeling"
---

# Tip-Adapter cache-based few-shot CLIP adaptation

Tip-Adapter adapts a frozen CLIP classifier to $K$-shot, $N$-class image classification without back-propagation: it retrieves from a cache of labeled CLIP image embeddings and adds the retrieved class scores to CLIP's text-derived zero-shot logits. Tip-Adapter-F uses that cache as initialization, then fine-tunes only its embedding keys.[^zhang-2022-tip-adapter]

## Method

- The method L2-normalizes CLIP visual features for all $NK$ labeled training images as cache keys $F_{train}$ and stores their one-hot class labels $L_{train}$ as values. For a normalized test feature $f$, it computes an affinity to every key as $A = \exp(-\beta(1-fF_{train}^{T}))$ and forms cache logits $A L_{train}$.[^zhang-2022-tip-adapter]
- Final logits combine cache retrieval with CLIP's text classifier: $\alpha A L_{train} + fW_c^T$. Here $\alpha$ balances few-shot visual-cache evidence against CLIP's zero-shot text-classifier evidence and $\beta$ controls affinity sharpness.[^zhang-2022-tip-adapter]
- The cache can be expressed as a two-layer adapter with first-layer weights from the cached visual features, second-layer weights from transposed one-hot labels, zero biases, and the exponential affinity activation. The training-free variant sets those weights directly rather than learning them with gradient descent.[^zhang-2022-tip-adapter]
- Tip-Adapter-F keeps both CLIP encoders and the one-hot label values fixed, but updates the cached feature keys with cross-entropy supervision. The authors report 20 fine-tuning epochs, compared with 200 for their CLIP-Adapter baseline.[^zhang-2022-tip-adapter]

## Reported findings

- On the paper's ResNet-50 ImageNet protocol with CLIP-style preprocessing and 16 labeled examples per class, zero-shot CLIP scored 60.33%, Tip-Adapter 62.03%, CLIP-Adapter 63.59%, CoOp 62.95%, and Tip-Adapter-F 65.51%. These are reported benchmark results, not a general performance ordering.[^zhang-2022-tip-adapter]
- The paper evaluates 1-, 2-, 4-, 8-, and 16-shot classification across ImageNet plus ten additional image-classification datasets. Its rendered result figures show the reported Tip-Adapter-F curve above the compared curves for the displayed settings, while training-free Tip-Adapter varies relative to CLIP-Adapter as shots and datasets change.[^zhang-2022-tip-adapter]
- In the reported ImageNet 16-shot timing on one RTX 3090, training-free Tip-Adapter required no adapter-training time, while Tip-Adapter-F took five minutes for 20 epochs; the table reports 50 minutes for 200-epoch CLIP-Adapter and 14 hours 40 minutes for 200-epoch CoOp. Hardware, implementation, preprocessing, and prompt choices constrain that comparison.[^zhang-2022-tip-adapter]
- On the source's 16-shot ImageNet ablation, performance increased as the per-class cache grew from 1 to 16 stored entries. For more shots, the authors also compressed groups of examples into averaged feature prototypes while holding cache size at 16 per class; that experiment does not establish scaling behavior for arbitrary cache sizes or domains.[^zhang-2022-tip-adapter]

## Limits and trade-offs

- The cache has one entry per labeled example unless it is compressed, so inference retrieval and adapter width grow with the few-shot set. The paper studies prototype averaging only in its ImageNet setup.[^zhang-2022-tip-adapter]
- The authors select $\alpha$ and $\beta$ per dataset; the reported best values are therefore not a parameter-free deployment recipe. In their ImageNet ablation, increasing $\alpha$ beyond the tested optimum reduced accuracy.[^zhang-2022-tip-adapter]
- The evaluation concerns few-shot image classification with CLIP-derived features. It does not establish retrieval, generation, distribution-shift robustness, or performance with non-CLIP encoders.[^zhang-2022-tip-adapter]
- Tip-Adapter-F is no longer training-free, and the source reports that unfreezing label values can hurt or collapse the shown few-shot training setup. That observation is limited to the paper's experiments.[^zhang-2022-tip-adapter]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by preserving its visual encoder and text-derived classifier while adding few-shot visual-key retrieval to its logits.[^zhang-2022-tip-adapter]
- Compared with: [CoOp context optimization](coop-context-optimization.md) in the paper's few-shot image-classification experiments; CoOp learns continuous text-prompt context, whereas Tip-Adapter uses labeled visual-feature cache retrieval.[^zhang-2022-tip-adapter]

[^zhang-2022-tip-adapter]: Zhang et al., “Tip-Adapter: Training-free CLIP-Adapter for Better Vision-Language Modeling” (2022), [source manuscript](../raw/2111.03930_Tip-Adapter/ReviewTemplate.tex). The complete manuscript was read. Its three central PNG figures and 12 result-plot PDFs were visually inspected; the remaining local PDF is an unrelated, marked CVPR rebuttal-template artifact and was excluded.
