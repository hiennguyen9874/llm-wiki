---
title: TBPS-CLIP
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: draft
page_type: concept
aliases:
  - Text-based Person Search CLIP baseline
  - CLIP for TBPS
tags:
  - machine-learning
  - multimodal
  - retrieval
  - clip
  - paper-method
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2308-10045-tbps-clip
confidence_score: 0.84
quality_score: 0.81
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - CLIP
  - text-to-image person retrieval
  - IRRA
  - RDE
  - MARS
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
  - training tricks
  - augmentation pool
  - few-shot learning
  - model compression
---

# TBPS-CLIP

TBPS-CLIP is a 2023 CLIP-based baseline for [[text-to-image-person-retrieval]] introduced in [[source-arxiv-2308-10045-tbps-clip]]. Unlike architecture-heavy methods, it keeps CLIP's original dual-encoder structure and improves TBPS largely through training recipe design.

## Summary
TBPS-CLIP combines several practical ingredients:
- training tricks such as global-gradient backpropagation, dropout, locked bottom layers, and soft labels;
- data augmentation for both images and text, including an image augmentation pool, back translation, and random deletion;
- retrieval-oriented objectives such as N-ITC, R-ITC, and C-ITC;
- additional probes for few-shot learning and model compression.

The core lesson is that a tuned CLIP baseline can be competitive on TBPS without a custom multimodal interaction encoder. In the current vault, TBPS-CLIP is important as a lightweight reference point that complements [[irra]] and [[rde]] rather than replacing them.

## Relationships
- `uses` CLIP dual encoders
- `uses` training tricks for optimization and regularization
- `uses` augmentation pool, back translation, and random deletion
- `uses` N-ITC, R-ITC, and C-ITC
- `supports` [[text-to-image-person-retrieval]]
- `related_to` [[irra]]
- `related_to` [[rde]]
- `related_to` [[mars]]
- `related_to` [[mra]]

## Evidence / claims
#### Claim
- Statement: TBPS-CLIP is a lightweight CLIP-based TBPS baseline that gains most of its strength from recipe design rather than a bespoke cross-modal module.
- Status: active
- Confidence: 0.91
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Core framing of the paper.

#### Claim
- Statement: TBPS-CLIP (ViT-B/16) reaches 73.54 Rank-1 on CUHK-PEDES, 65.05 on ICFG-PEDES, and 61.95 on RSTPReid, while training in 5 epochs.
- Status: active
- Confidence: 0.88
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Source-specific benchmark report.

#### Claim
- Statement: TBPS-CLIP improves few-shot TBPS and can be compressed by freezing part of the text encoder with limited performance loss.
- Status: active
- Confidence: 0.78
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Supported by the paper's model-generalization and model-compression experiments.

## Open questions
- How much of TBPS-CLIP's gain comes from retrieval losses versus the augmentation pool and training tricks?
- Does the recipe transfer to other fine-grained cross-modal retrieval tasks beyond person search?
- Can TBPS-CLIP-style training be combined cleanly with later robustness or domain-alignment methods?

## Sources
- [[source-arxiv-2308-10045-tbps-clip]]
