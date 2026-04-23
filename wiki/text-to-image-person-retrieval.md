---
title: Text-to-Image Person Retrieval
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: draft
page_type: topic
aliases:
  - text image person retrieval
  - person text retrieval
tags:
  - machine-learning
  - multimodal
  - retrieval
  - computer-vision
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
confidence_score: 0.73
quality_score: 0.74
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - IRRA
  - CLIP
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
---

# Text-to-Image Person Retrieval

Text-to-image person retrieval is a multimodal retrieval task where a system receives a natural-language description of a person and must retrieve matching images from a gallery. The main challenge is aligning language and visual appearance despite modality mismatch, viewpoint/pose variation, and ambiguity in textual descriptions.

## Current in-vault view
The first ingested source on this topic is [[source-arxiv-2303-12501-irra]], which presents [[irra]] as a CLIP-based retrieval method that emphasizes **implicit** token-level relation learning during training rather than **explicit** local part alignment during inference.

## Key points
- The task sits at the intersection of image-text retrieval and person re-identification.
- Earlier methods often used separately pretrained visual/text encoders and explicit local alignment.
- The IRRA paper argues that full-model CLIP transfer plus MLM-based implicit reasoning can improve alignment quality while keeping inference simple.
- Current vault evidence on this topic is still sparse; benchmark and design conclusions should be treated as provisional until reinforced by more sources.

## Evidence / claims
#### Claim
- Statement: A key design tension in text-to-image person retrieval is balancing fine-grained cross-modal alignment against inference-time efficiency.
- Status: active
- Confidence: 0.72
- Evidence: [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-23
- Notes: Framed directly in the source through the contrast between global matching, explicit local matching, and implicit relation reasoning.

#### Claim
- Statement: As represented by [[irra]], CLIP-initialized dual encoders can serve as a strong baseline for this task and can be improved with additional cross-modal reasoning objectives.
- Status: active
- Confidence: 0.74
- Evidence: [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-23
- Notes: Supported by the paper's baseline and final results; broader field generality still needs reinforcement.

#### Claim
- Statement: Publication-time SOTA claims in this topic area should be stored as historical claims unless newer reinforcement or contradiction enters the vault.
- Status: active
- Confidence: 0.80
- Evidence: [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-23
- Notes: This is an ingest-policy interpretation applied to benchmark-heavy sources.

## Related pages
- [[irra]]
- [[source-arxiv-2303-12501-irra]]

## Sources
- [[source-arxiv-2303-12501-irra]]
