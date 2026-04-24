---
title: Source - GitHub - Shuyu-XJTU/MRA
created: 2026-04-24
last_updated: 2026-04-24
source_count: 1
status: reviewed
page_type: source
aliases:
  - Shuyu-XJTU/MRA
  - MRA GitHub
  - MRA code
  - Multi-granularity Relation Alignment implementation
tags:
  - source
  - github
  - code
  - machine-learning
  - multimodal
  - retrieval
  - domain-adaptation
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2507-10195-mra
confidence_score: 0.86
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-24
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - MRA
  - SDA
  - DaD
  - Swin Transformer
  - BERT
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/codes/MRA/README.md
source_type: code
canonical_url: https://github.com/Shuyu-XJTU/MRA
author:
  - Shuyu Yang
  - Yaxiong Wang
  - Yongrui Li
  - Li Zhu
  - Zhedong Zheng
published: 2025-07
---

# Source - GitHub - Shuyu-XJTU/MRA

## Source snapshot
- Public repository: [https://github.com/Shuyu-XJTU/MRA](https://github.com/Shuyu-XJTU/MRA)
- Raw local source: `raw/codes/MRA/`
- Companion paper page: [[source-arxiv-2507-10195-mra]]
- README title: *MRA: Multi-granularity Relation Alignment framework for text-based person retrieval pretraining*
- License file: MIT-style license in `raw/codes/MRA/LICENSE`.

## Privacy / sensitivity screen
- Screened text source files for secrets, credentials, tokens, passwords, private keys, and sensitive non-public operational data before promotion.
- Result: no actionable secrets found. Matches on `token` were tokenizer variable names in code, not credentials.
- Downstream notes preserve public repository/dataset/checkpoint links only at a high level and avoid treating access codes or local dataset paths as private facts.

## What the code adds beyond the paper
This source is an implementation companion for [[mra]]. It confirms that the published method is packaged as a PyTorch training/evaluation repository using a Swin Transformer visual encoder, BERT text/fusion encoder, ITC/ITM/MLM losses, optional EDA text augmentation, and an optional region-level loss path for SDA pretraining.

## Extracted entities
- **`Retrieval` model** — training wrapper intended to extend the MRA/APTM backbone and return ITC, ITM, MLM, and region losses.
- **Swin Transformer Base** — vision backbone initialized from `swin_base_patch4_window7_224_22k.pth`.
- **BERT base uncased** — text encoder / masked-language modeling component loaded from `data/bert-base-uncased`.
- **SDA config** — pretraining configuration over `images/SDA` with region annotations from `data/sda/*.json`.
- **CUHK / ICFG / RSTP configs** — fine-tuning/evaluation configurations for standard TBPS benchmarks.
- **EDA augmentation** — text augmentation enabled in fine-tuning configs and implemented under `dataset/eda.py`.

## Typed relationships
- [[source-github-shuyu-xjtu-mra]] `supports` [[mra]].
- [[source-github-shuyu-xjtu-mra]] `supports` [[synthetic-domain-aligned-dataset]].
- [[source-github-shuyu-xjtu-mra]] `implements` the paper's Swin+BERT retrieval recipe.
- [[source-github-shuyu-xjtu-mra]] `related_to` [[domain-aware-diffusion]] through SDA usage, but does not implement DaD generation itself in the inspected code.
- [[mra]] `depends_on` SDA region annotations for the region-level pretraining branch.

## Candidate claims from the source
#### Claim
- Statement: The released MRA repository implements the retrieval side of the paper with a Swin Transformer image encoder, BERT text/fusion encoder, ITC, ITM, and MLM objectives.
- Status: active
- Confidence: 0.88
- Evidence: [[source-github-shuyu-xjtu-mra]], [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-24
- Notes: Directly supported by `models/mra.py`, `models/model_retrieval.py`, and the README usage path.

#### Claim
- Statement: The SDA pretraining path adds region-level supervision by pairing masked visual regions with region-phrase text and applying contrastive plus matching losses.
- Status: active
- Confidence: 0.84
- Evidence: [[source-github-shuyu-xjtu-mra]], [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-24
- Notes: Confirmed by `configs/sda.yaml`, `dataset/pretrain_dataset.py`, and the `region > 0` branch in `models/model_retrieval.py`.

#### Claim
- Statement: The public code release reinforces MRA as a reproducible implementation companion, but the inspected raw snapshot contains apparent implementation hazards that should be checked before local execution.
- Status: active
- Confidence: 0.78
- Evidence: [[source-github-shuyu-xjtu-mra]]
- Last confirmed: 2026-04-24
- Notes: The inspected snapshot imports `MRA` from `models/mra.py` even though that file defines `APTM`, references `new_mlp` inside `build_itc_mlp`, and imports `dataset.trieval_dataset` in `Retrieval.py`; these may be snapshot typos, packaging drift, or untested paths rather than paper-level contradictions.

## Reinforcement / contradiction / supersession assessment
- Reinforces [[source-arxiv-2507-10195-mra]] on architecture and training losses: the code operationalizes global ITC/ITM/MLM plus region-level contrastive/matching supervision.
- Reinforces [[synthetic-domain-aligned-dataset]] as an implementation dependency: pretraining config expects SDA JSON shards with region annotations.
- Does not supersede any benchmark claims. It adds reproducibility and implementation detail rather than new reported results.
- Potential code hazards are implementation caveats, not contradictions of the paper's conceptual claims.

## Related pages updated
- [[mra]]
- [[synthetic-domain-aligned-dataset]]
- [[domain-aware-diffusion]]
- [[text-to-image-person-retrieval]]
- [[source-arxiv-2507-10195-mra]]

## Ingest notes
- Read the repository README, configs, primary training/evaluation entrypoints, datasets, model wrappers, and supporting utilities from `raw/codes/MRA/`; binary images, bytecode caches, and large vendored BERT/Swin internals were treated as implementation artifacts rather than promoted content.
- Quick static check flagged likely execution hazards for future reproduction work.
- Considered Base/Canvas updates; deferred because the existing TBPS method graph remains navigable through linked markdown pages.
