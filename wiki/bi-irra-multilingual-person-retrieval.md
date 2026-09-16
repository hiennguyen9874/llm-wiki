---
type: Concept
title: Bi-IRRA multilingual text-to-image person retrieval
description: Bi-IRRA extends IRRA to multilingual person retrieval with bidirectional masked reconstruction and global alignment over English and translated Chinese, French, and German descriptions.
tags: [cross-modal-retrieval, multilingual, masked-modeling, person-reidentification]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:36:02Z }
sources:
  - id: arxiv-2510.17685v1
    resource: ../raw/papers/arXiv-2510.17685v1/main.tex
    title: Multilingual Text-to-Image Person Retrieval via Bidirectional Relation Reasoning and Aligning
  - id: bi-irra-code
    resource: ../raw/codes/Bi-IRRA/README.md
    title: Official Bi-IRRA PyTorch implementation
---

# Bi-IRRA multilingual text-to-image person retrieval

Bi-IRRA extends IRRA from English-only retrieval to English and translated Chinese, French, and German descriptions. Its Bi-directional Implicit Relation Reasoning (Bi-IRR) module reconstructs masked content in both modalities, while Multi-dimensional Global Alignment (Md-GA) aligns unimodal and fused representations.[^arxiv-2510.17685v1] The released code operationalizes one English–target-language pair per training run and implements two-stage retrieval: global cosine similarity selects 256 images per query, then a fusion encoder and binary image-text-matching head re-rank only that shortlist.[^bi-irra-code]

## Architecture and objectives

- A 12-layer image encoder and 12-layer text encoder produce patch/token sequences; a six-layer multimodal interaction encoder applies cross-attention. Parameters are initialized from X²-VLM multilingual multimodal pretraining.[^arxiv-2510.17685v1]
- **Bi-lingual MLM:** source- and target-language tokens are independently masked, then predicted from unmasked text and image features through a shared interaction encoder. This generalizes IRRA's text-side implicit relation reasoning to both languages.[^arxiv-2510.17685v1]
- **Cross-lingual D-MIM:** an unmasked image paired with the higher-quality English source text forms a stop-gradient teacher target. A shared-weight student receives a block-masked image and translated target text, then reconstructs the teacher's fused feature sequence using cosine similarity. This provides image-side masked reconstruction and cross-language distillation without a separate teacher network.[^arxiv-2510.17685v1]
- **Bi-lingual ITC:** bidirectional contrastive losses separately align each image with its English and target-language global embeddings.[^arxiv-2510.17685v1]
- **Bi-lingual A-ITM:** a fused-representation classifier predicts image-text matching for both languages. Only images paired with generated target text are masked; the authors frame this asymmetry as regularization against residual translation noise.[^arxiv-2510.17685v1]
- The joint objective is $\mathcal{L}_{itc}+\lambda_1\mathcal{L}_{a-itm}+\mathcal{L}_{mlm}+\lambda_2\mathcal{L}_{d-mim}$, with both reported loss weights set to 4.[^arxiv-2510.17685v1]

**Synthesis:** the design assigns English two trust roles: it anchors the image-reconstruction teacher and remains a parallel supervised retrieval language. The translated branch receives asymmetric corruption where the authors expect weaker correspondence. This is a source-aware training heuristic, but not a calibrated estimate of translation reliability per example.

## Reported evidence

Without person-domain pretraining, the paper reports these Bi-IRRA results after multilingual training:[^arxiv-2510.17685v1]

| Dataset | Query language | Rank-1 | mAP |
|---|---|---:|---:|
| CUHK-PEDES(M) | English | 78.82 | 69.68 |
| CUHK-PEDES(M) | Chinese | 76.43 | 67.79 |
| CUHK-PEDES(M) | French | 76.46 | 67.26 |
| CUHK-PEDES(M) | German | 75.57 | 67.07 |
| ICFG-PEDES(M) | English | 68.53 | 41.82 |
| RSTPReid(M) | English | 72.85 | 55.60 |
| UFineBench(M) | English | 90.45 | 89.66 |

On CUHK-PEDES(M), removing both masked-reconstruction tasks lowers English/Chinese Rank-1 from 78.82/76.43 to 76.97/74.81. Replacing Md-GA with IRRA's SDM while retaining both reconstruction tasks lowers them to 66.89/64.36. The latter comparison changes both the objective and inference scoring path, so it does not isolate global-alignment quality alone.[^arxiv-2510.17685v1]

The paper reports advantages over reproduced multilingual TIPR and multilingual image-text retrieval baselines. These are author-run comparisons and were not independently reproduced here. English comparisons also mix Bi-IRRA trained on four-language corpora with many published baselines trained only on English, so gains cannot be attributed solely to architecture.[^arxiv-2510.17685v1]

## Implementation and limitations

The reported setup uses $224\times224$ images, 10 epochs, AdamW, and four A40 GPUs. Text length is 77 with batch size 32 for CUHK-PEDES(M), ICFG-PEDES(M), and RSTPReid(M), and 168 with batch size 16 for UFineBench(M). Text and image mask ratios are 0.4 and 0.5; blockwise image masking performs best in the reported comparison.[^arxiv-2510.17685v1]

- Evaluation covers only translated versions of four person-retrieval datasets and four languages; it does not establish behavior for native non-English descriptions, code-switching, unseen languages, or general image-text retrieval.[^arxiv-2510.17685v1]
- The manuscript reports no repeated-run variance, significance tests, independent reproduction, parameter count, or inference latency. The code confirms that fusion is applied only to the global top-256 shortlist, but the operational cost and scalability of that fixed-depth re-ranking remain unreported.[^arxiv-2510.17685v1][^bi-irra-code]
- The manuscript's ambiguous learning-rate wording is resolved by the code: one warm-up epoch linearly increases $10^{-6}$ to $5\times10^{-5}$, followed by cosine decay toward $5\times10^{-6}$ across the remaining epochs.[^arxiv-2510.17685v1][^bi-irra-code]
- Two manuscript passages appear to contain source/target notation slips. The code confirms the intended implementation: D-MIM uses unmasked image plus source text as a no-gradient teacher and masked image plus target text as the student; target-language A-ITM also uses target text with the masked image.[^arxiv-2510.17685v1][^bi-irra-code]
- The release is not self-contained: `README.md` instructs installation from an absent `requirements.txt`, while both supplied YAML files reference an absent `config/config_beit2_base.json`. It declares an MIT license but includes no license text. The code snapshot therefore cannot reproduce the reported experiments without reconstructing dependencies and configuration.[^bi-irra-code]
- Training and evaluation are hard-wired to distributed execution: `is_using_distributed()` always returns true, training later accesses `model.module`, and evaluation unconditionally calls distributed barriers and reduction. The documented four-process launcher fits these assumptions, but no standalone single-device evaluation or trained-checkpoint loading command is supplied.[^bi-irra-code]

## Relationships

- **Builds on:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) is the English-only conference predecessor; Bi-IRRA replaces SDM/identity alignment with Md-GA and adds target-language MLM plus cross-lingual image reconstruction.[^arxiv-2510.17685v1]
- **Uses:** [LDAT multilingual person-retrieval benchmark](ldat-multilingual-person-retrieval-benchmark.md) supplies its translated training and evaluation corpora.[^arxiv-2510.17685v1]
- **Uses:** [TBPS-CLIP empirical person-search baseline](tbps-clip-empirical-person-search-baseline.md) supplies the stated image augmentations.[^arxiv-2510.17685v1]

[^arxiv-2510.17685v1]: Min Cao, Xinyu Zhou, Ding Jiang, Bo Du, Mang Ye, and Min Zhang, “Multilingual Text-to-Image Person Retrieval via Bidirectional Relation Reasoning and Aligning,” arXiv:2510.17685v1, 2025, [`main.tex`](../raw/papers/arXiv-2510.17685v1/main.tex). Included result tables and the LDAT, Bi-IRRA, and translation-rewrite figures in the same source bundle were also inspected.
[^bi-irra-code]: Cao et al., [`Bi-IRRA`](../raw/codes/Bi-IRRA/README.md), official PyTorch implementation snapshot. Code audit covered the README, both supplied YAML configurations, training entry point, dataset pipeline, retrieval model, XVLM loss/projection implementation, evaluator, and launcher. Static Python compilation of the principal entry, model, data, and evaluation modules passed; experiments were not executed because required dependencies, the referenced vision configuration, datasets, and checkpoints are absent.
