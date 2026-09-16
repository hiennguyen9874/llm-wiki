---
type: Concept
title: RDE for noisy-correspondence person retrieval
description: RDE combines dual-grained consensus filtering with a softened triplet loss to train text-to-image person retrieval models under mismatched image-text pairs.
tags: [cross-modal-retrieval, noisy-correspondence, clip, person-reidentification, robust-learning]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:04:07Z }
sources:
  - id: arxiv-2308.09911
    resource: ../raw/papers/arxiv-2308.09911/main.tex
    title: Noisy-Correspondence Learning for Text-to-Image Person Re-identification
---

# RDE for noisy-correspondence person retrieval

Robust Dual Embedding (RDE) addresses *noisy correspondence* in text-to-image person re-identification: training pairs in which an unmatched image and description are incorrectly treated as a positive pair. It combines coarse and fine-grained CLIP embeddings, consensus-based sample filtering, and a softened triplet objective. The authors report that this design resists severe synthetic pair corruption, but the evidence is confined to three person-retrieval datasets and has not been independently reproduced here.[^arxiv-2308.09911]

## Method

- **Basic Global Embedding (BGE):** cosine similarity between CLIP's global image `[CLS]` and text `[EOS]` representations.
- **Token Selection Embedding (TSE):** selects the highest-attention image and text tokens from the final encoder blocks, transforms them with an MLP-plus-linear residual module, and max-pools them into separate embeddings. Training sums separate BGE and TSE losses; inference averages their similarity scores.[^arxiv-2308.09911]
- **Confident Consensus Division (CCD):** fits separate two-component Gaussian mixture models to per-pair BGE and TSE losses. A pair is considered confidently clean only when both views assign it to their low-loss component; agreement on noisy status marks it noisy, and disagreement marks it uncertain. The implementation uses a 0.5 posterior threshold, drops consensus-noisy pairs, and randomly assigns binary labels to uncertain pairs.[^arxiv-2308.09911]
- **Triplet Alignment Loss (TAL):** replaces the single hardest-negative term in conventional triplet ranking with a temperature-scaled log-sum-exp over all negatives. This is an upper bound on the hardest-negative term; temperature controls how closely it approaches hard-negative mining. The intended effect is to retain emphasis on difficult negatives without allowing one potentially corrupted negative to dominate optimization.[^arxiv-2308.09911]

**Synthesis:** CCD and TAL address complementary failure modes. CCD attempts to reduce false-positive supervision before each epoch, while TAL reduces the sensitivity of each remaining update to a single hard negative. Dual embeddings make the filter conservative by requiring agreement between signals at different granularities.

## Reported evidence

The paper injects synthetic noise by randomly shuffling a specified proportion of training descriptions. Its strongest evidence is the gap between the best validation-selected and final checkpoints: RDE remains comparatively stable while ordinary baselines increasingly overfit as corruption rises. Selected author-reported Rank-1 results are:[^arxiv-2308.09911]

| Synthetic noise | CUHK-PEDES | ICFG-PEDES | RSTPReid |
|---:|---:|---:|---:|
| 0% | 75.94 | 67.68 | 65.35 |
| 50% | 71.33 | 63.76 | 62.85 |
| 80% | 64.99 | 56.02 | 53.40 |

On CUHK-PEDES with 50% noise, the component table reports Rank-1 of 71.33 for full RDE, 63.11 without CCD, 69.33 when TAL is replaced by similarity-distribution matching, 67.38 with an all-negative summed triplet loss, and 6.40 with hardest-negative triplet ranking. At 80% noise, the corresponding full, no-CCD, and hardest-negative results are 64.99, 41.03, and 2.18.[^arxiv-2308.09911]

These comparisons are author-reported. The noisy-pair examples visually inspected in the source bundle support the existence of mismatched or semantically weak descriptions, but they are outputs selected by CCD rather than an independently labeled audit of natural noise. Synthetic random shuffling may also be easier to detect than realistic partial, ambiguous, or systematic annotation errors.

## Implementation details

The reported setup fine-tunes CLIP ViT-B/16 for 60 epochs with Adam, cosine decay, batch size 64, $384\times128$ images, and text sequences up to 77 tokens. CLIP parameters start at a $10^{-5}$ learning rate and TSE parameters at $10^{-3}$. TAL uses margin $m=0.1$ and temperature $\tau=0.015$; TSE selects 30% of tokens. The authors provide code at <https://github.com/QinYang79/RDE>.[^arxiv-2308.09911]

## Limitations and source inconsistencies

- Evaluation is limited to CUHK-PEDES, ICFG-PEDES, and RSTPReid. It does not establish robustness for general image-text retrieval, non-random correspondence noise, or modern encoder families.
- CCD relies on the early-learning assumption that clean pairs have lower loss and models the distribution with two Gaussian components. The source does not establish that this partition remains calibrated when clean examples are intrinsically hard or when noise is semantically plausible.
- Randomly labeling the uncertain set can inject additional noise; the manuscript does not isolate this choice against alternatives such as exclusion or soft weighting.
- The appendix's simplified TAL equation subtracts similarity to the hardest negative, while the main definition and the subsequent gradient derivation subtract positive-pair similarity. This appears to be a notation error and should be checked against the released code before implementing the loss literally.
- Broad “state-of-the-art” claims depend on comparator eligibility. A supplementary table lists RaSa at 66.90 Rank-1 on RSTPReid, above RDE's 65.35, but visually de-emphasizes it because it uses a different pretrained backbone.

## Relationships

- **Uses:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) supplies the referenced CLIP setup, similarity-distribution baseline, dataset splits, and a principal comparison point.

[^arxiv-2308.09911]: Yang Qin, Yingke Chen, Dezhong Peng, Xi Peng, Joey Tianyi Zhou, and Peng Hu, “Noisy-Correspondence Learning for Text-to-Image Person Re-identification,” CVPR 2024 manuscript and supplementary material, [`main.tex`](../raw/papers/arxiv-2308.09911/main.tex). The architecture, loss-behavior plots, and representative CCD-selected noisy-pair figure in the same source bundle were also visually inspected.
