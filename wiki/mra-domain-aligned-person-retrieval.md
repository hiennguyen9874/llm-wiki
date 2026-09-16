---
type: Concept
title: MRA domain-aligned text-based person retrieval
description: MRA combines target-style synthetic pretraining data with explicit region-phrase and global image-text alignment for text-based person retrieval.
tags: [cross-modal-retrieval, domain-adaptation, synthetic-data, region-phrase-alignment, person-reidentification]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:52:04Z }
sources:
  - id: arxiv-2507.10195
    resource: ../raw/papers/arxiv-2507.10195/main.tex
    title: "Minimizing the Pretraining Gap: Domain-aligned Text-Based Person Retrieval"
  - id: mra-code
    resource: ../raw/codes/MRA/README.md
    title: Official MRA code snapshot
---

# MRA domain-aligned text-based person retrieval

This pipeline adapts synthetic pretraining data at two levels: Domain-aware Diffusion (DaD) generates images styled toward the CUHK-PEDES training domain, while Multi-granularity Relation Alignment (MRA) jointly learns global image-text and local region-phrase correspondences. The resulting Synthetic Domain-Aligned (SDA) corpus contains 1,217,750 image-text pairs, most with automatically generated region boxes and phrases. After SDA pretraining, MRA is fine-tuned on each retrieval benchmark and uses a fusion encoder to rerank dual-encoder candidates. Reported improvements support the combined pipeline, but evidence for the individual mechanisms is more limited and all results are author-reported.[^arxiv-2507.10195] The released snapshot exposes the intended model and data flow, but its documented launcher cannot run unchanged because of multiple independent name errors, and the release omits DaD construction code and required data and weights.[^mra-code]

## DaD and SDA construction

- **Target-style generator:** DaD starts from Stable Diffusion 1.5 and adds ControlNet-style trainable copies of its 12 encoder blocks and middle block. Original diffusion blocks remain frozen; copied outputs enter corresponding skip connections through zero-initialized $1\times1$ convolutions. Training uses CUHK-PEDES training image-caption pairs, a white control image, $384\times256$ inputs, mean-squared error, and three epochs.[^arxiv-2507.10195]
- **Prompt expansion and generation:** each of 68,126 CUHK-PEDES training captions yields 19 EDA variants plus the original caption. Random seeds add visual variation. Filtering removes grayscale-like outputs by channel-difference statistics and malformed people with OpenPose; 10.63% of generated images are removed.[^arxiv-2507.10195]
- **New captions and local annotations:** BLIP2 recaptions retained images to reduce duplicated language inherited from prompt augmentation. Grounding DINO then produces phrase-conditioned boxes using text and box thresholds of 0.35; most pairs have more than two regions, although pairs with no detected region are retained.[^arxiv-2507.10195]
- **Scale and domain proximity:** SDA has 1,217,750 pairs, about 18 times the CUHK-PEDES training set. Against CUHK-PEDES, the paper reports FID 56.56 for SDA, versus 92.25 for MALS and 111.41 for images generated directly with Stable Diffusion 1.5 from CUHK captions. This measures proximity to one chosen target dataset, not general realism or cross-domain coverage.[^arxiv-2507.10195]

**Synthesis:** SDA is not domain-neutral synthetic data. Its generator, prompt vocabulary, and FID target all derive from CUHK-PEDES training data, while recaptioning and detection introduce BLIP2 and Grounding DINO biases. The construction avoids collecting additional real pedestrian images but does not by itself remove privacy, representation, or deployment concerns inherited from the target corpus and pretrained tools.

## Multi-granularity Relation Alignment

MRA shares a Swin-Base vision encoder and a BERT-Base text stack split into a six-layer text encoder and six-layer cross-attentive fusion encoder.[^arxiv-2507.10195]

- **Region encoding:** a $224\times224$ image is represented as 49 visual patches. Patches overlapping a detected box form its region representation; their mean becomes a region class token, retaining full-image context instead of independently resizing each crop.
- **Region-Phrase Contrastive learning (RPC):** separately projected region and phrase representations receive symmetric, temperature-scaled contrastive supervision within the batch.
- **Region-Phrase Matching (RPM):** similarity-weighted hard negatives from RPC create binary matched/unmatched pairs. Phrase states query region states through the fusion encoder.
- **Global alignment:** image-text contrastive learning, image-text matching, and masked-language modeling provide coarse supervision. MLM selects 25% of tokens, using an 80/10/10 mask-random-unchanged split.
- **Objective:** $\mathcal{L}_{MRA}=\mathcal{L}_{ITC}+\mathcal{L}_{ITM}+\mathcal{L}_{MLM}+\beta(\mathcal{L}_{RPC}+\mathcal{L}_{RPM})$, with $\beta=0.8$ selected from the reported sweep. Fine-tuning drops RPC and RPM and optimizes only the three global objectives.

At retrieval time, global image-text similarity selects candidates per text query and the fusion encoder reranks them. The manuscript specifies 512 candidates, while the released configurations use 512 for CUHK-PEDES and ICFG-PEDES, 1,000 for RSTPReid, and 128 when evaluating SDA pretraining against CUHK-PEDES. Downstream evaluation also averages original and horizontally flipped image matching scores, then adds global similarity with weight 0.002.[^arxiv-2507.10195][^mra-code] This is more expensive than pure dual-encoder retrieval, and neither source reports reranking latency.

## Released implementation

The PyTorch snapshot implements Swin-Base image encoding, the split BERT text/fusion stack, global ITC/ITM/MLM objectives, region-phrase contrastive and matching losses, EDA caption augmentation during downstream fine-tuning, random erasing, test-time horizontal flipping, and fusion reranking. Its supplied configurations use 56-token inputs and batch size 40. SDA pretraining is configured for 32 epochs at $224\times224$ with a 2,048-dimensional projection; CUHK-PEDES and ICFG-PEDES fine-tuning use 30 epochs at $384\times256$ with the same projection, while RSTPReid instead uses a 256-dimensional projection and 10 epochs.[^mra-code]

The snapshot is not executable as released without repairs:

- `run.py` interpolates `args.re`, but its parser defines `args.region`; the README commands therefore terminate with `AttributeError` before launching distributed training. This failure was reproduced locally.
- `dataset/__init__.py` imports `pre_dataset`, `ft_train_dataset`, and `ft_test_dataset` but calls undefined names `RegionTextJsonDataset`, `re_train_dataset`, and `re_test_dataset`, blocking dataset construction.
- `build_itc_mlp` creates `mlp` but initializes undefined `new_mlp`. This blocks model construction for the 2,048-dimensional SDA, CUHK-PEDES, and ICFG-PEDES configurations; the 256-dimensional RSTPReid branch does not call that function.
- The region objective is weighted twice during SDA training: `Retrieval.forward` returns $0.8(L_{RPC}+L_{RPM})$, then the training loop multiplies it by the configured `region: 0.8`, yielding an effective coefficient of 0.64 rather than the manuscript's $\beta=0.8$.

Training evaluates the test split after every epoch and selects the saved downstream checkpoint by test Rank-1; it does not use the loaded validation split for selection. This makes ordinary runs test-set-tuned and means their reported best checkpoint is not a validation-selected estimate.[^mra-code] The code is MIT-licensed, but the README separately restricts the downloadable SDA dataset to research and forbids commercial use, so the dataset and implementation have different usage boundaries.

## Reported evidence

The fully pretrained and fine-tuned model reports:[^arxiv-2507.10195]

| Dataset | Rank-1 | Rank-5 | Rank-10 | mAP |
|---|---:|---:|---:|---:|
| CUHK-PEDES | 77.21 | 90.66 | 94.46 | 68.50 |
| ICFG-PEDES | 68.93 | 83.46 | 88.07 | 41.38 |
| RSTPReid | 68.15 | 86.30 | 91.10 | 53.77 |

The paper's own comparison table does not support an unqualified best-on-every-metric claim: RaSa has higher CUHK-PEDES mAP and RSTPReid Rank-5/Rank-10, APTM has higher RSTPReid Rank-10, and SAMC has higher ICFG-PEDES mAP. The authors report CUHK-PEDES mAP of 72.14 when adding RaSa's mixed strong/weak-positive fine-tuning, but do not use that variant for the main comparison.[^arxiv-2507.10195]

Ablations provide several distinct levels of evidence:

- **Whole pretraining pipeline:** on CUHK-PEDES, SDA pretraining raises the MRA architecture from 71.23 to 77.21 Rank-1 and from 92.43 to 94.46 Rank-10.
- **SDA under a fixed external architecture:** reimplemented IVT reaches 65.35/89.90 Rank-1/Rank-10 with SDA, versus 64.85/89.99 with MALS and 63.56/88.86 with 4M general image-caption pairs. SDA's controlled advantage over MALS is therefore small and metric-dependent.
- **Local alignment under reduced data:** with 68,126 SDA pairs, adding the full region-phrase objective to global alignment raises Rank-1 from 73.99 to 74.76 and Rank-10 from 93.57 to 93.97. Object-word variants perform worse, supporting phrase-level context over finer fragmentation within this setup.
- **Scale:** using 5% of SDA reports 74.76 Rank-1 versus 71.23 without pretraining and 77.21 with all data; gains continue but diminish at 50% and 100%.
- **Transfer:** the SDA-pretrained vision encoder reports 94.39 Rank-1 and 84.26 mAP on Market-1501, compared with 91.12 and 76.31 for ImageNet-1K pretraining under the stated common fine-tuning setup.

These experiments do not cleanly isolate DaD, recaptioning, filtering, region annotations, and corpus scale in one factorial study. The principal MRA-versus-APTM comparison also changes both architecture and pretraining data, so it cannot attribute the gain solely to SDA or local alignment.[^arxiv-2507.10195]

## Training and limitations

Pretraining uses four RTX 3090 GPUs for 32 epochs, batch size 40, AdamW with weight decay 0.01, and a linearly decayed learning rate from $5\times10^{-5}$ to $5\times10^{-6}$ after 2,600 warm-up iterations; the paper reports roughly four days and 226.5M trainable parameters. Fine-tuning uses four A100 40 GB GPUs for 30 epochs, batch size 40, $384\times256$ images, image augmentation, and EDA text augmentation.[^arxiv-2507.10195]

- Evaluation covers three related person-retrieval datasets; the pipeline's transfer beyond pedestrian retrieval is represented only by the Market-1501 vision-encoder experiment.
- DaD is fitted to CUHK-PEDES training data. The study does not compare independently adapted generators for ICFG-PEDES or RSTPReid, and target-specific generation may need repeating for a materially different deployment domain.
- Filtering does not eliminate oversaturation, while generated captions and boxes can propagate BLIP2 and Grounding DINO errors or biases. Annotation precision and subgroup coverage are not quantified.
- Reranking 512 candidates requires cross-modal fusion at inference, but compute, latency, and memory are not compared with dual-encoder methods.
- Qualitative retrieval and region examples are illustrative rather than systematic evidence.

## Source inconsistencies

- The Market-1501 table reports SDA-pretrained mAP of **84.26**, while the prose says **82.46**. The stated improvement of 7.95 points over 76.31 agrees with 84.26, so the table value is internally consistent but remains unverified.
- The parameter-sensitivity prose says $\beta$ was tested at $\{0,0.4,0.8,1,2\}$, while the figure and its caption show $\{0,0.4,0.8,1.2\}$. The selected value 0.8 appears in both the plot and prose.

## Relationships

- **Compared with:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) keeps its cross-modal interaction branch training-only, whereas MRA uses a fusion encoder to rerank 512 candidates at inference; MRA's source reports higher Rank-1 on all three shared benchmarks.[^arxiv-2507.10195]
- **Related approach:** [MARS attribute-aware text-based person search](mars-attribute-aware-person-search.md) also introduces local attribute supervision and inference-time cross-modal reranking, but MRA obtains local supervision from synthetic region-phrase boxes during pretraining.

[^arxiv-2507.10195]: Shuyu Yang, Yaxiong Wang, Yongrui Li, Li Zhu, and Zhedong Zheng, “Minimizing the Pretraining Gap: Domain-aligned Text-Based Person Retrieval,” arXiv:2507.10195, ICCV 2025 manuscript, [`main.tex`](../raw/papers/arxiv-2507.10195/main.tex). All included section files and the seven referenced PDF figures were inspected; results were not independently reproduced.
[^mra-code]: Shuyu Yang et al., official MRA implementation, [`README.md`](../raw/codes/MRA/README.md) and associated source snapshot. All 30 files were inventoried; the README, license, configurations, principal execution/model/data/evaluation paths, and three referenced assets were inspected. The vendored BERT and Swin implementations and utility modules were not audited line by line. Python syntax compilation succeeded, and the launcher failure was reproduced; end-to-end training and evaluation were not attempted because the external datasets, pretrained weights, checkpoints, and GPU environment are absent.
