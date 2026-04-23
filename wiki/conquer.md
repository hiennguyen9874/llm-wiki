---
title: CONQUER
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: draft
page_type: concept
aliases:
  - Context-Aware Representation with Query Enhancement
  - Context-Aware Representation with Query Enhancement for Text-Based Person Search
tags:
  - machine-learning
  - multimodal
  - retrieval
  - query-refinement
  - optimal-transport
  - paper-method
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2601-18625-conquer
  - source-arxiv-2510-17685-bi-irra
confidence_score: 0.85
quality_score: 0.84
evidence_count: 2
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - text-to-image person retrieval
  - CARE
  - IQE
  - Optimal Transport
  - MARS
  - GA-DMS
  - RDE
  - MRA
  - Bi-IRRA
  - Qwen2.5-VL-7B
---

# CONQUER

CONQUER (*Context-Aware Representation with Query Enhancement for Text-Based Person Search*) is a 2026 method for [[text-to-image-person-retrieval]] introduced in [[source-arxiv-2601-18625-conquer]]. It combines training-time representation refinement with inference-time query enhancement so the retrieval system can better handle both cross-modal mismatch and ambiguous user descriptions.

## Summary
CONQUER has two main components:
- **CARE** improves the learned embedding space through multi-granularity encoding, complementary pair mining, and context-guided Optimal Transport matching.
- **IQE** is a plug-and-play reranking module that selects anchor images, extracts likely missing attributes with an MLLM, and fuses them into an improved query without retraining the backbone.

In the current vault, CONQUER matters because it adds a distinct design route: instead of only improving data quality, loss design, or token/pair robustness during training, it treats ambiguity in the user's original query as a first-class retrieval bottleneck. That makes it a useful comparison point beside [[mars]], [[rde]], [[mra]], [[ga-dms]], [[irra]], and [[tbps-clip]].

## Relationships
- `uses` CARE for training-time alignment refinement
- `uses` IQE for inference-time query enhancement
- `uses` multi-granularity encoding
- `uses` complementary pair mining
- `uses` context-guided Optimal Transport matching
- `uses` anchor-based attribute enrichment for reranking
- `supports` [[text-to-image-person-retrieval]]
- `related_to` [[mars]]
- `related_to` [[rde]]
- `related_to` [[mra]]
- `related_to` [[ga-dms]]
- `related_to` [[irra]]
- `related_to` [[tbps-clip]]

## Evidence / claims
#### Claim
- Statement: CONQUER improves TBPS by combining training-time context-aware alignment with inference-time query refinement for ambiguous or incomplete descriptions.
- Status: active
- Confidence: 0.90
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Direct source framing and architecture claim.

#### Claim
- Statement: IQE is useful because it can refine vague or underspecified queries without retraining the main retrieval backbone.
- Status: active
- Confidence: 0.87
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Important durable design idea even if future benchmark leadership changes.

#### Claim
- Statement: CONQUER reports 77.13 Rank-1 / 68.75 mAP on CUHK-PEDES, 67.70 Rank-1 / 40.36 mAP on ICFG-PEDES, and 68.40 Rank-1 / 51.73 mAP on RSTPReid.
- Status: active
- Confidence: 0.89
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Source-specific benchmark report.

#### Claim
- Statement: In the current vault, CONQUER broadens the method landscape but is later outperformed on historical benchmark reporting by both GA-DMS and then Bi-IRRA.
- Status: active
- Confidence: 0.84
- Evidence: [[source-arxiv-2601-18625-conquer]], [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2510-17685-bi-irra]]
- Last confirmed: 2026-04-23
- Notes: Historical in-vault comparison only.

## Open questions
- How much of CONQUER's gains come from CARE versus IQE when evaluated under realistic ambiguous-query distributions?
- How reliable is MLLM-based attribute extraction when anchors are themselves slightly wrong?
- Can CONQUER's query-enhancement idea combine productively with token-noise handling from [[ga-dms]], multilingual supervision from [[bi-irra]], or data-centric pretraining from [[mra]]?

## Sources
- [[source-arxiv-2601-18625-conquer]]
- [[source-arxiv-2510-17685-bi-irra]]
