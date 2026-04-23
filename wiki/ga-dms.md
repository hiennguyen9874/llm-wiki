---
title: GA-DMS
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: draft
page_type: concept
aliases:
  - Gradient-Attention Guided Dual-Masking Synergetic
  - Gradient-Attention Guided Dual-Masking Synergic
tags:
  - machine-learning
  - multimodal
  - retrieval
  - robustness
  - paper-method
  - clip
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2509-09118-ga-dms
confidence_score: 0.84
quality_score: 0.83
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes:
  - mra
superseded_by: []
related_entities:
  - text-to-image person retrieval
  - WebPerson
  - CONQUER
  - GASS
  - IRRA
  - RDE
  - MRA
  - CLIP
---

# GA-DMS

GA-DMS (*Gradient-Attention Guided Dual-Masking Synergetic*) is a 2025 method for [[text-to-image-person-retrieval]] introduced in [[source-arxiv-2509-09118-ga-dms]]. It combines noise-aware token masking with informative-token reconstruction to improve CLIP-based person retrieval.

## Summary
GA-DMS centers on a **Gradient-Attention Similarity Score (GASS)** that estimates which text tokens are likely noisy versus semantically informative for image-text alignment. It then applies two complementary training actions:
- **Noise token masking** reduces the influence of likely irrelevant or hallucinated caption tokens.
- **Masked informative token prediction** forces the model to reconstruct semantically important masked tokens through cross-modal interaction.

In the current vault, GA-DMS matters because it strengthens the noise-robustness story opened by [[rde]] while staying closer to CLIP/IRRA-style retrieval pipelines than the synthetic-domain pretraining route of [[mra]]. It also arrives with a companion dataset, [[webperson]], which the paper argues is a major part of the gain.

## Relationships
- `uses` GASS for token relevance scoring
- `uses` noise token masking
- `uses` masked token prediction
- `uses` [[webperson]] as a large-scale pretraining corpus
- `supports` [[text-to-image-person-retrieval]]
- `related_to` [[rde]]
- `related_to` [[mra]]
- `related_to` [[irra]]
- `related_to` [[conquer]]
- `supersedes` [[mra]] on publication-time benchmark leadership

## Evidence / claims
#### Claim
- Statement: GA-DMS improves person retrieval by jointly suppressing noisy text tokens and reconstructing informative ones during training.
- Status: active
- Confidence: 0.88
- Evidence: [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Direct architecture claim from the source.

#### Claim
- Statement: GASS is more effective than cosine-similarity-only token scoring in the paper's ablations.
- Status: active
- Confidence: 0.82
- Evidence: [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Source-local ablation result; useful design hint rather than a universal rule.

#### Claim
- Statement: In the current vault, GA-DMS supersedes MRA's publication-time benchmark leadership with later reported Rank-1 scores of 77.60, 69.51, and 71.25 on CUHK-PEDES, ICFG-PEDES, and RSTPReid respectively.
- Status: active
- Confidence: 0.86
- Evidence: [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Historical in-vault comparison only.
- Supersedes: [[mra]]

## Open questions
- How much of the gain comes from [[webperson]] scale and quality versus the GA-DMS objective itself?
- Does token-level masking remain effective when captions are cleaner and more human-authored?
- Can GA-DMS-style token scoring be combined with region-phrase supervision from [[mra]]?
- Can GA-DMS's token-noise handling be combined with [[conquer]]'s inference-time query enhancement without introducing MLLM-driven attribute hallucination?

## Sources
- [[source-arxiv-2509-09118-ga-dms]]
