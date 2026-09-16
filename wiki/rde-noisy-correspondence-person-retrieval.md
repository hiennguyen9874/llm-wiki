---
type: Concept
title: RDE for noisy-correspondence person retrieval
description: RDE combines dual-grained consensus filtering with a softened triplet loss to train text-to-image person retrieval models under mismatched image-text pairs.
tags: [cross-modal-retrieval, noisy-correspondence, clip, person-reidentification, robust-learning]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:54:53Z }
sources:
  - id: arxiv-2308.09911
    resource: ../raw/papers/arxiv-2308.09911/main.tex
    title: Noisy-Correspondence Learning for Text-to-Image Person Re-identification
  - id: rde-code
    resource: ../raw/codes/RDE/README.md
    title: Official RDE code snapshot
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

The paper injects synthetic noise by randomly shuffling a specified proportion of training descriptions. Its strongest evidence is the gap between author-designated “Best” and final checkpoints: RDE remains comparatively stable while ordinary baselines increasingly overfit as corruption rises. The released launcher, however, evaluates the test split every epoch by default and saves “best” according to test Rank-1, so these best-checkpoint comparisons are not validation-independent.[^arxiv-2308.09911][^rde-code] Selected author-reported Rank-1 results are:[^arxiv-2308.09911]

| Synthetic noise | CUHK-PEDES | ICFG-PEDES | RSTPReid |
|---:|---:|---:|---:|
| 0% | 75.94 | 67.68 | 65.35 |
| 50% | 71.33 | 63.76 | 62.85 |
| 80% | 64.99 | 56.02 | 53.40 |

On CUHK-PEDES with 50% noise, the component table reports Rank-1 of 71.33 for full RDE, 63.11 without CCD, 69.33 when TAL is replaced by similarity-distribution matching, 67.38 with an all-negative summed triplet loss, and 6.40 with hardest-negative triplet ranking. At 80% noise, the corresponding full, no-CCD, and hardest-negative results are 64.99, 41.03, and 2.18.[^arxiv-2308.09911]

These comparisons are author-reported. The noisy-pair examples visually inspected in the source bundle support the existence of mismatched or semantically weak descriptions, but they are outputs selected by CCD rather than an independently labeled audit of natural noise. Synthetic random shuffling may also be easier to detect than realistic partial, ambiguous, or systematic annotation errors.

## Released implementation

The official launcher fine-tunes OpenAI CLIP ViT-B/16 for 60 epochs with Adam, five warm-up epochs followed by cosine decay, batch size 64, $384\times128$ images, and 77-token text sequences. CLIP parameters use a $10^{-5}$ base learning rate while the two TSE modules are explicitly assigned $10^{-3}$. It enables image augmentation and a custom text corruption transform; TAL uses margin $m=0.1$ and temperature $\tau=0.015$, and TSE selects 30% of image and text tokens.[^rde-code]

Before each training epoch, the code switches to evaluation mode, computes min-max-normalized per-pair BGE and TSE losses over the training set, fits independent two-component Gaussian mixtures, retains consensus-clean pairs, drops consensus-noisy pairs, and randomly labels disagreements. GMM regularization and iteration counts change for noise above 40% and for RSTPReid. The provided index files are full permutations with realized changed-pair rates within 0.01 percentage points of their nominal 20%, 50%, and 80% settings. Evaluation averages BGE and TSE cosine-similarity matrices, while also logging each view separately.[^rde-code]

The launcher restores `model.train()` before optimization. A 2024-11-28 README warning says this fix can degrade performance in noisy settings and suggests commenting out that line. The snapshot therefore exposes a consequential mismatch between correct training-mode behavior and at least some expected noisy-scene performance, without identifying which mode produced every published result.[^rde-code]

## Limitations and source inconsistencies

- Evaluation is limited to CUHK-PEDES, ICFG-PEDES, and RSTPReid. It does not establish robustness for general image-text retrieval, non-random correspondence noise, or modern encoder families.
- The default `val_dataset` is `test`; training evaluates it after every epoch and saves `best.pth` by test Rank-1. The standalone evaluator also contains a hard-coded author-local run path. Reported “Best” results should therefore not be interpreted as performance from validation-only checkpoint selection.[^rde-code]
- The repository has no pinned environment or packaged datasets and checkpoints. Its README delegates requirements to IRRA and links externally hosted weights; the launcher contains an author-local dataset root. The README states Apache-2.0 licensing, but this snapshot contains no license file.[^rde-code]
- Multi-GPU support is not a reliable reproduction path in this snapshot: random sampling explicitly lacks a distributed branch, and the per-epoch loss pass calls a model-specific method through the distributed wrapper. Runtime behavior was not validated here.[^rde-code]
- TAL and TRL losses are summed over retained samples rather than normalized, so gradient scale varies with the number CCD accepts. The alternative InfoNCE and SDM paths do normalize by the accepted count.[^rde-code]
- CCD relies on the early-learning assumption that clean pairs have lower loss and models the distribution with two Gaussian components. The source does not establish that this partition remains calibrated when clean examples are intrinsically hard or when noise is semantically plausible.
- Randomly labeling the uncertain set can inject additional noise; the manuscript does not isolate this choice against alternatives such as exclusion or soft weighting.
- The appendix's simplified TAL equation subtracts similarity to the hardest negative, while the main definition and the subsequent gradient derivation subtract positive-pair similarity. This appears to be a notation error and should be checked against the released code before implementing the loss literally.
- Broad “state-of-the-art” claims depend on comparator eligibility. A supplementary table lists RaSa at 66.90 Rank-1 on RSTPReid, above RDE's 65.35, but visually de-emphasizes it because it uses a different pretrained backbone.

## Relationships

- **Uses:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) supplies the referenced CLIP setup, similarity-distribution baseline, dataset splits, and a principal comparison point.

[^arxiv-2308.09911]: Yang Qin, Yingke Chen, Dezhong Peng, Xi Peng, Joey Tianyi Zhou, and Peng Hu, “Noisy-Correspondence Learning for Text-to-Image Person Re-identification,” CVPR 2024 manuscript and supplementary material, [`main.tex`](../raw/papers/arxiv-2308.09911/main.tex). The architecture, loss-behavior plots, and representative CCD-selected noisy-pair figure in the same source bundle were also visually inspected.
[^rde-code]: Yang Qin et al., [official RDE code snapshot](../raw/codes/RDE/README.md), including the launcher, dataset pipeline, model, objectives, training/evaluation code, supplied noise-index arrays, paper PDF, result table, and posters. The Python files passed syntax compilation, and representative pages of both PDFs plus all PNG/JPEG attachments were visually inspected; training and evaluation were not executed because the snapshot omits datasets, checkpoints, a pinned environment, and the required runtime dependencies and GPU setup.
