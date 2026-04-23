---
title: Source - arXiv 2509.09118 - GA-DMS
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - Gradient-Attention Guided Dual-Masking Synergetic Framework for Robust Text-based Person Retrieval
  - arXiv 2509.09118
  - GA-DMS paper
tags:
  - source
  - paper
  - arxiv
  - multimodal
  - retrieval
  - robust-training
  - dataset
  - person-retrieval
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-arxiv-2407-04287-mars
  - source-arxiv-2507-10195-mra
  - source-arxiv-2510-17685-bi-irra
confidence_score: 0.93
quality_score: 0.89
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes:
  - source-arxiv-2507-10195-mra
superseded_by:
  - source-arxiv-2510-17685-bi-irra
related_entities:
  - GA-DMS
  - WebPerson
  - GASS
  - noise token masking
  - masked token prediction
  - CLIP
  - IRRA
  - RDE
  - MRA
  - LUPerson-MLLM
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/web-clips/arxiv-2509-09118v1-gradient-attention-guided-dual-masking-synergetic-framework-for-robust-text-based-person-retrieval.md
source_type: paper
canonical_url: https://arxiv.org/html/2509.09118v1
author:
  - Tianlu Zheng
  - Yifan Zhang
  - Xiang An
  - Ziyong Feng
  - Kaicheng Yang
  - Qichuan Ding
published: 2025-09-11
---

# Source - arXiv 2509.09118 - GA-DMS

## Source snapshot
- Title: *Gradient-Attention Guided Dual-Masking Synergetic Framework for Robust Text-based Person Retrieval*
- Authors: Tianlu Zheng, Yifan Zhang, Xiang An, Ziyong Feng, Kaicheng Yang, Qichuan Ding
- Published: 2025-09-11
- Original URL: [https://arxiv.org/html/2509.09118v1](https://arxiv.org/html/2509.09118v1)
- Cleaned web clip preserved at: `raw/web-clips/arxiv-2509-09118v1-gradient-attention-guided-dual-masking-synergetic-framework-for-robust-text-based-person-retrieval.md`
- Code URL: [https://github.com/Multimodal-Representation-Learning-MRL/GA-DMS](https://github.com/Multimodal-Representation-Learning-MRL/GA-DMS)
- Data URL: [https://huggingface.co/datasets/Kaichengalex/WebPerson-5M](https://huggingface.co/datasets/Kaichengalex/WebPerson-5M)

## Why it matters
This paper extends the vault's [[text-to-image-person-retrieval]] thread along two fronts at once. On the data side, it introduces [[webperson]], a 5M real-image web dataset intended to reduce dependence on smaller manually annotated pedestrian corpora and earlier synthetic-only pretraining sets. On the method side, it introduces [[ga-dms]], a CLIP-based training framework that explicitly separates noisy from informative text tokens during training. Relative to the current vault, this paper matters because it both reinforces [[rde]]'s noise-aware framing and partially supersedes [[mra]]'s historical benchmark-leadership position with later reported results.

## Summary
The paper contributes two coupled artifacts:
1. **[[webperson]]**: a 5M image / 10M description person-centric dataset constructed from COYO-700M via person filtering, pose checks, template induction, and MLLM caption generation.
2. **[[ga-dms]]**: a retrieval framework built on CLIP-style image/text encoders plus IRRA-style masked token prediction machinery, with two complementary masking paths driven by a gradient-attention similarity score.

Its central claim is that person retrieval improves when the training data become both larger and more person-centric, and when training explicitly suppresses noisy text tokens while forcing reconstruction of informative ones.

## Sensitive material screen
- Screened for secrets, credentials, tokens, PII, and sensitive non-public operational data before promotion.
- Result: no actionable sensitive material found that should block ingest.
- The raw clip contains public academic contact emails from the paper header, but downstream wiki notes intentionally avoid copying those addresses.

## Extracted entities
- **GA-DMS** — retrieval framework using gradient-attention-guided dual masking
- **WebPerson** — 5M-scale web-sourced person-centric image-text dataset
- **GASS** — Gradient-Attention Similarity Score used to score token relevance
- **Noise token masking** — masks likely noisy textual tokens during training
- **Masked token prediction** — predicts masked informative tokens after cross-modal interaction
- **COYO-700M** — upstream web image-text source pool
- **YOLOv11 / YOLOv11-Pose** — used for person filtering and pose-quality checks
- **Qwen2.5-72B-Instruct / Qwen2.5-VL** — used for template induction and caption generation
- **IRRA** — downstream fine-tuning recipe/baseline reused in comparisons
- **LUPerson-MLLM / SYNTH-PEDES / MALS / LUPerson-T** — comparison pretraining datasets

## Typed relationships
- [[ga-dms]] `uses` GASS.
- [[ga-dms]] `uses` noise token masking.
- [[ga-dms]] `uses` masked token prediction.
- [[ga-dms]] `supports` [[text-to-image-person-retrieval]].
- [[webperson]] `supports` [[ga-dms]].
- [[webperson]] `related_to` [[synthetic-domain-aligned-dataset]].
- [[webperson]] `uses` COYO-700M as the raw image pool.
- [[source-arxiv-2509-09118-ga-dms]] `supports` [[ga-dms]].
- [[source-arxiv-2509-09118-ga-dms]] `supports` [[webperson]].
- [[source-arxiv-2509-09118-ga-dms]] `supports` [[text-to-image-person-retrieval]].
- [[source-arxiv-2509-09118-ga-dms]] `related_to` [[rde]].
- [[source-arxiv-2509-09118-ga-dms]] `related_to` [[mra]].
- [[source-arxiv-2509-09118-ga-dms]] `supersedes` [[source-arxiv-2507-10195-mra]] on publication-time benchmark leadership claims in this vault.
- [[source-arxiv-2509-09118-ga-dms]] `is_superseded_by` [[source-arxiv-2510-17685-bi-irra]] on later in-vault historical English-benchmark leadership.

## Candidate claims from the source
#### Claim
- Statement: WebPerson creates a large real-image person-centric pretraining corpus by filtering COYO-700M and generating caption diversity with MLLMs plus template induction.
- Status: active
- Confidence: 0.89
- Evidence: [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Direct dataset-construction claim from Sections 3.1 and 3.2.

#### Claim
- Statement: GA-DMS improves CLIP-based person retrieval by combining gradient-attention-guided noise token masking with masked informative token prediction.
- Status: active
- Confidence: 0.90
- Evidence: [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Direct method claim from the architecture and ablation sections.

#### Claim
- Statement: Relative to earlier in-vault sources, this paper reports later historical benchmark leadership with Rank-1 scores of 77.60 on CUHK-PEDES, 69.51 on ICFG-PEDES, and 71.25 on RSTPReid for the 5M setting, but that role is later superseded in-vault by Bi-IRRA.
- Status: superseded
- Confidence: 0.88
- Evidence: [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2507-10195-mra]], [[source-arxiv-2407-04287-mars]], [[source-arxiv-2308-09911-rde]], [[source-arxiv-2510-17685-bi-irra]]
- Last confirmed: 2026-04-23
- Notes: Historical comparison only; preserve as provenance rather than current frontier.
- Supersedes: [[source-arxiv-2507-10195-mra]]
- Superseded_by: [[source-arxiv-2510-17685-bi-irra]]

#### Claim
- Statement: The paper reinforces the view that noisy textual supervision is a major bottleneck in person retrieval and that token-level mitigation can matter alongside pair-level robustness and data curation.
- Status: active
- Confidence: 0.84
- Evidence: [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Cross-source synthesis grounded in this paper's framing plus RDE's earlier noise-oriented argument.

#### Claim
- Statement: WebPerson pretraining appears more transferable than several earlier pretraining corpora, with especially strong gains at larger data scales.
- Status: active
- Confidence: 0.82
- Evidence: [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Supported by the direct-transfer and fine-tuning tables; keep as source-local rather than field-general.

## Reinforcement / supersession assessment
- [[source-arxiv-2308-09911-rde]] is reinforced on the importance of noise-aware learning, but this paper shifts the locus from pair-level filtering alone toward token-level noise handling plus larger-scale curated pretraining.
- [[source-arxiv-2507-10195-mra]] is reinforced on the importance of data quality and pretraining strategy, but its in-vault benchmark-leadership role is **superseded** by this later 2025 paper.
- [[source-arxiv-2407-04287-mars]] remains a useful attribute-focused comparison point; this paper does not contradict MARS so much as propose a different route to fine-grained alignment.
- [[source-arxiv-2510-17685-bi-irra]] later supersedes this source on historical English-benchmark leadership while leaving GA-DMS's token-noise and web-pretraining contributions intact.
- No material contradiction was found that requires a disputed state; the main update is a broadened design space plus a later benchmark point.

## Related pages updated
- [[ga-dms]]
- [[webperson]]
- [[text-to-image-person-retrieval]]
- [[mra]]
- [[rde]]

## Ingest notes
- Read from the arXiv HTML page with Defuddle and saved a cleaned web clip under `raw/web-clips/`.
- Preserved the original URL in source metadata via `canonical_url`.
- Did **not** create the skill-default `knowledge/summary_*.md` file.
- Considered Base/Canvas updates but deferred because the current topic graph remains navigable through linked markdown pages.
