---
title: WebPerson
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: draft
page_type: concept
aliases:
  - Web-Person
  - WebPerson-5M
tags:
  - machine-learning
  - dataset
  - multimodal
  - retrieval
  - synthetic-captions
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2509-09118-ga-dms
confidence_score: 0.82
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
  - GA-DMS
  - text-to-image person retrieval
  - COYO-700M
  - LUPerson-MLLM
  - SYNTH-PEDES
  - MALS
  - LUPerson-T
---

# WebPerson

WebPerson is a 2025 large-scale person-centric image-text dataset introduced in [[source-arxiv-2509-09118-ga-dms]]. The paper describes it as a 5M image / 10M description corpus built from web images and MLLM-generated captions for person representation learning.

## Summary
WebPerson is constructed by filtering COYO-700M for high-quality person-centric images, checking pose completeness, then generating diverse captions through a template-and-MLLM pipeline. In the current vault, it matters because it provides a real-image, web-scale alternative to smaller manual TBPS datasets and a different data story from the synthetic-domain-aligned route represented by [[synthetic-domain-aligned-dataset]].

## Relationships
- `supports` [[ga-dms]]
- `supports` [[text-to-image-person-retrieval]]
- `related_to` [[synthetic-domain-aligned-dataset]]
- `related_to` LUPerson-MLLM, LUPerson-T, MALS, and SYNTH-PEDES as comparison corpora
- `uses` COYO-700M as upstream image source

## Evidence / claims
#### Claim
- Statement: WebPerson uses automated person filtering, pose verification, template induction, and MLLM captioning to produce a large person-centric pretraining corpus.
- Status: active
- Confidence: 0.85
- Evidence: [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Direct dataset construction summary from the source.

#### Claim
- Statement: WebPerson is intended to be both larger-scale and more transferable than several earlier pretraining datasets used in TBPS.
- Status: active
- Confidence: 0.80
- Evidence: [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Supported by source-reported direct-transfer and fine-tuning comparisons; keep source-local.

#### Claim
- Statement: In the current vault, WebPerson broadens the pretraining design space beyond synthetic-domain alignment by emphasizing curated real web images plus MLLM caption generation.
- Status: active
- Confidence: 0.78
- Evidence: [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Cross-source synthesis comparing this dataset line with [[synthetic-domain-aligned-dataset]].

## Open questions
- How noisy are WebPerson captions in practice after template-guided MLLM generation?
- How much of WebPerson's reported transferability comes from scale versus filtering quality?
- How does WebPerson compare to [[synthetic-domain-aligned-dataset]] under matched model and objective choices?

## Sources
- [[source-arxiv-2509-09118-ga-dms]]
