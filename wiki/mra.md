---
title: MRA
created: 2026-04-23
last_updated: 2026-04-24
source_count: 3
status: draft
page_type: concept
aliases:
  - Multi-granularity Relation Alignment
tags:
  - machine-learning
  - multimodal
  - retrieval
  - domain-adaptation
  - synthetic-data
  - paper-method
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2507-10195-mra
  - source-github-shuyu-xjtu-mra
  - source-arxiv-2509-09118-ga-dms
confidence_score: 0.83
quality_score: 0.82
evidence_count: 3
first_seen: 2026-04-23
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes:
  - rde
superseded_by:
  - ga-dms
related_entities:
  - text-to-image person retrieval
  - DaD
  - SDA
  - RPC
  - RPM
  - IRRA
  - MARS
  - RDE
  - WebPerson
  - GA-DMS
  - Swin Transformer
  - BERT
---

# MRA

MRA (*Multi-granularity Relation Alignment*) is a 2025 method for [[text-to-image-person-retrieval]] introduced in [[source-arxiv-2507-10195-mra]]. It combines data-centric synthetic pretraining with explicit region-phrase alignment to reduce the gap between synthetic pretraining corpora and real pedestrian retrieval benchmarks.

## Summary
MRA sits on top of a broader pipeline:
- [[domain-aware-diffusion]] generates more target-domain-like synthetic pedestrian images,
- [[synthetic-domain-aligned-dataset]] provides image-text pairs plus region-phrase annotations,
- MRA then pretrains a retrieval model using both coarse and fine-grained alignment objectives.

Its method stack includes:
- global image-text alignment through ITC, ITM, and MLM,
- **Region-Phrase Contrastive (RPC)** learning,
- **Region-Phrase Matching (RPM)** learning with hard negatives,
- shared vision, text, and fusion encoders for multi-granularity supervision.

The public implementation companion [[source-github-shuyu-xjtu-mra]] confirms a Swin Transformer + BERT PyTorch recipe, SDA pretraining configs, fine-tuning configs for CUHK-PEDES / ICFG-PEDES / RSTPReid, and an optional region-level branch in the retrieval model. It also introduces a practical caveat: the inspected raw snapshot contains apparent code-level hazards that should be resolved before using it as a local reproduction baseline.

In the current vault, MRA matters both as a former historical benchmark leader and as a design argument that better pretraining data plus phrase-level supervision can outperform earlier objective-only improvements. That benchmark-leadership role is now later superseded in-vault by [[ga-dms]], but MRA remains the clearest source here for synthetic-domain alignment as a distinct lever.

## Relationships
- `uses` [[domain-aware-diffusion]]
- `uses` [[synthetic-domain-aligned-dataset]]
- `uses` RPC and RPM for fine-grained supervision
- `supports` [[text-to-image-person-retrieval]]
- `implemented_by` [[source-github-shuyu-xjtu-mra]]
- `depends_on` [[synthetic-domain-aligned-dataset]] region annotations during SDA pretraining
- `related_to` [[irra]]
- `related_to` [[mars]]
- `related_to` [[rde]]
- `related_to` [[ga-dms]]
- `supersedes` [[rde]] on publication-time benchmark leadership
- `is_superseded_by` [[ga-dms]] on later publication-time benchmark leadership

## Evidence / claims
#### Claim
- Statement: MRA jointly optimizes image-text alignment and region-phrase alignment during pretraining to improve downstream person-text retrieval.
- Status: active
- Confidence: 0.84
- Evidence: [[source-arxiv-2507-10195-mra]], [[source-github-shuyu-xjtu-mra]]
- Last confirmed: 2026-04-24
- Notes: Direct architecture summary from the paper, reinforced by the released Swin+BERT implementation.

#### Claim
- Statement: MRA frames phrase-level grounding as a productive middle ground: stronger than global-only alignment but more stable than over-fragmented object-word alignment.
- Status: active
- Confidence: 0.79
- Evidence: [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Source-supported via ablation discussion; keep as a design heuristic, not a universal rule.

#### Claim
- Statement: The released MRA code operationalizes the paper's retrieval-side method as Swin+BERT training with ITC, ITM, MLM, optional EDA augmentation, and a region-level SDA branch.
- Status: active
- Confidence: 0.84
- Evidence: [[source-github-shuyu-xjtu-mra]], [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-24
- Notes: Implementation-level reinforcement. The code companion does not add new benchmark evidence and has apparent snapshot hazards that should be checked before execution.

#### Claim
- Statement: MRA supersedes RDE's historical best-reported benchmark results in this vault, but is later superseded by GA-DMS's 2025 reported results.
- Status: superseded
- Confidence: 0.81
- Evidence: [[source-arxiv-2507-10195-mra]], [[source-arxiv-2308-09911-rde]], [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Preserve as historical provenance only; MRA still matters as the strongest synthetic-domain-alignment reference currently in-vault.
- Supersedes: [[rde]]
- Superseded_by: [[ga-dms]]

## Open questions
- How much of MRA's gains come from SDA itself versus the MRA objective stack?
- Does region-phrase supervision transfer beyond person retrieval into broader image-text retrieval domains?
- How does MRA behave when training data also contain meaningful [[noisy-correspondence]]?
- Which parts of [[ga-dms]]'s gains come from token-level masking versus [[webperson]] scale and curation, relative to MRA's synthetic-domain-alignment story?

## Sources
- [[source-arxiv-2507-10195-mra]]
- [[source-github-shuyu-xjtu-mra]]
- [[source-arxiv-2509-09118-ga-dms]]
