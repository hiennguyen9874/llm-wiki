---
title: Synthetic Domain-Aligned Dataset
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: draft
page_type: concept
aliases:
  - SDA
tags:
  - machine-learning
  - dataset
  - synthetic-data
  - domain-adaptation
  - retrieval
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2507-10195-mra
confidence_score: 0.80
quality_score: 0.79
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - MRA
  - DaD
  - MALS
  - text-to-image person retrieval
  - BLIP2
  - Grounding DINO
---

# Synthetic Domain-Aligned Dataset

The Synthetic Domain-Aligned dataset (*SDA*) is the synthetic pretraining corpus introduced in [[source-arxiv-2507-10195-mra]]. It is built to be closer to real pedestrian retrieval benchmarks than earlier synthetic corpora and adds region-phrase annotations for fine-grained supervision.

## Summary
According to the source, SDA is created by:
- generating target-domain-like images with [[domain-aware-diffusion]],
- diversifying text descriptions with BLIP2,
- adding region-phrase annotations using Grounding DINO.

The resulting dataset contains roughly 1.22M image-text pairs and often multiple region-phrase annotations per image. In-vault, SDA matters less as a standalone benchmark than as the data substrate that enables [[mra]].

## Relationships
- `uses` [[domain-aware-diffusion]]
- `supports` [[mra]]
- `related_to` MALS as an earlier synthetic pretraining dataset
- `supports` [[text-to-image-person-retrieval]] through pretraining

## Evidence / claims
#### Claim
- Statement: SDA is designed to reduce the synthetic-to-real pretraining gap by making synthetic pedestrian images visually closer to the downstream domain.
- Status: active
- Confidence: 0.80
- Evidence: [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Supported by the benchmark-construction section and the FID comparison.

#### Claim
- Statement: SDA's region-phrase annotations are important because they enable phrase-level grounding during pretraining rather than only image-level supervision.
- Status: active
- Confidence: 0.78
- Evidence: [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Supported by the method design and ablation discussion.

## Open questions
- How reliable are the automatically produced captions and region annotations?
- Which parts of SDA matter most: domain alignment, data scale, or phrase-level labels?
- How much of SDA's utility survives transfer beyond the person-retrieval setting?

## Sources
- [[source-arxiv-2507-10195-mra]]
