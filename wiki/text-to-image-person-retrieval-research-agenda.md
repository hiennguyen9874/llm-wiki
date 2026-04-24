---
title: Text-to-Image Person Retrieval Research Agenda
created: 2026-04-23
last_updated: 2026-04-24
source_count: 10
status: reviewed
page_type: synthesis
aliases:
  - TBPS research agenda
  - text-based person search research agenda
tags:
  - machine-learning
  - multimodal
  - retrieval
  - synthesis
  - research-agenda
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-arxiv-2308-10045-tbps-clip
  - source-arxiv-2407-04287-mars
  - source-arxiv-2507-10195-mra
  - source-arxiv-2509-09118-ga-dms
  - source-arxiv-2601-18625-conquer
  - source-arxiv-2510-17685-bi-irra
  - source-arxiv-2604-18376-mvr
  - source-arxiv-2509-13754-fmfa
confidence_score: 0.86
quality_score: 0.84
evidence_count: 10
first_seen: 2026-04-23
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - text-to-image person retrieval
  - IRRA
  - RDE
  - TBPS-CLIP
  - MARS
  - MRA
  - GA-DMS
  - CONQUER
  - Bi-IRRA
  - MVR
  - FMFA
  - A-SDM
  - EFA
  - WebPerson
  - noisy correspondence
  - expression drift
  - domain-aware diffusion
  - synthetic domain-aligned dataset
---

# Text-to-Image Person Retrieval Research Agenda

This page captures the most useful next research directions suggested by the current vault. The goal is not novelty for its own sake, but to strengthen the existing page set by filling gaps that matter for [[text-to-image-person-retrieval]], [[irra]], [[rde]], [[tbps-clip]], [[mars]], [[mra]], [[ga-dms]], [[conquer]], [[bi-irra]], and [[mvr]].

## Priority 1: gaps that would most strengthen existing pages

### 1) Explain why benchmark leadership is dataset-dependent
**Why this is the biggest gap:** the vault already shows mixed leadership across CUHK-PEDES, ICFG-PEDES, and RSTPReid, but it does not yet explain *why* each dataset favors different methods. That makes the current benchmark story useful but incomplete.

**Pages this would strengthen:** [[text-to-image-person-retrieval]], [[bi-irra]], [[mvr]], [[ga-dms]], [[conquer]], [[rde]], [[tbps-clip]]

**What to research next:**
- dataset-level annotation style, caption length, and language diversity
- how much visible noise or ambiguity each benchmark contains
- whether methods win because of training objectives, data curation, or test-set characteristics
- whether leader changes are driven by robustness, multilinguality, or inference-time adaptation

**Best output artifact:** a benchmark-diagnostics page or comparison note for [[CUHK-PEDES]], [[ICFG-PEDES]], and [[RSTPReid]] once enough evidence is gathered.

### 2) Unify the different kinds of robustness problems
**Why this matters:** the current vault splits robustness across several pages, but the failure modes are related: [[noisy-correspondence]] in [[rde]], token-level noise in [[ga-dms]], query ambiguity in [[conquer]], and expression drift in [[mvr]]. A unified taxonomy would make the whole cluster easier to reason about.

**Pages this would strengthen:** [[noisy-correspondence]], [[rde]], [[ga-dms]], [[conquer]], [[mvr]], [[text-to-image-person-retrieval]]

**What to research next:**
- whether pair noise, token noise, and query ambiguity are distinct or overlapping failure modes
- which robustness levers generalize across all three
- whether one method can handle training-time noise and inference-time drift together

### 3) Compare synthetic-domain alignment against real web-scale pretraining
**Why this matters:** [[mra]] and [[webperson]] represent two different data-centric bets. MRA argues for target-domain-like synthetic pretraining plus region-phrase labels; WebPerson argues for large curated real web data plus MLLM captions. The vault would benefit from a clean comparison of these routes under matched model and objective choices.

**Pages this would strengthen:** [[mra]], [[domain-aware-diffusion]], [[synthetic-domain-aligned-dataset]], [[webperson]], [[ga-dms]]

**What to research next:**
- scale vs curation vs domain alignment
- synthetic captions versus MLLM-generated web captions
- whether phrase-level supervision helps more on synthetic or real corpora
- which route transfers better across datasets

## Priority 2: natural extensions of well-developed topics

### 4) Build a fine-grained grounding ladder
**Why this is a natural extension:** [[mars]] emphasizes attribute-level supervision, [[mra]] uses region-phrase alignment, [[ga-dms]] targets token-level noise, and [[fmfa]] adds explicit sparse token-patch alignment inside a global retrieval framework. These are different granularity choices around the same basic question: how fine-grained should the alignment signal be?

**Pages this would strengthen:** [[mars]], [[mra]], [[ga-dms]], [[conquer]]

**What to research next:**
- a shared taxonomy of attribute-, token-, phrase-, and region-level supervision
- when fine-grained grounding helps ranking versus only reranking
- whether the gains compose cleanly or interfere with one another
- whether FMFA-style fixed sparsity should be replaced by adaptive token-patch aggregation so useful local semantics are not discarded

### 5) Treat inference-time adaptation as a family, not isolated tricks
**Why this is a natural extension:** [[conquer]] and [[mvr]] both improve retrieval without changing the backbone in the same way training-time methods do. They suggest an emerging family of inference-time adaptation methods: query enhancement, semantic compensation, and multi-view aggregation.

**Pages this would strengthen:** [[conquer]], [[mvr]], [[bi-irra]], [[ga-dms]]

**What to research next:**
- when inference-time adaptation adds value over better training
- whether query enhancement and semantic compensation are complementary
- how these methods behave when captions are already clean

### 6) Expand multilingual coverage beyond the current language set
**Why this is a natural extension:** [[bi-irra]] makes multilingual TIPR first-class, but the current vault still lacks a broader multilingual program. There is also an open question about whether Bi-IRRA’s gains transfer to other language sets and how multilingual supervision interacts with query enhancement or robustness methods.

**Pages this would strengthen:** [[bi-irra]], [[irra]], [[conquer]], [[mvr]]

**What to research next:**
- more languages and less curated translation pipelines
- whether LDAT-style benchmark construction works beyond the current paper’s language set
- multilingual transfer plus inference-time adaptation

## Priority 3: adjacent but currently absent areas

### 7) Add canonical benchmark pages for the core datasets
**Why this is adjacent but missing:** the method pages mention CUHK-PEDES, ICFG-PEDES, and RSTPReid constantly, but the vault does not yet have dedicated benchmark pages. That makes it hard to summarize protocol differences, annotation style, and why dataset-specific leaders differ.

**Pages this would strengthen:** [[text-to-image-person-retrieval]], [[bi-irra]], [[mvr]], [[ga-dms]], [[conquer]], [[tbps-clip]], [[mars]]

### 8) Measure caption quality and hallucination directly
**Why this is adjacent but missing:** [[webperson]], [[conquer]], and [[mvr]] all depend on generated or reformulated language. The vault would benefit from a page or study on caption quality, hallucination, and attribute fidelity, because those factors likely affect both training data and inference-time reformulations.

**Pages this would strengthen:** [[webperson]], [[conquer]], [[mvr]], [[ga-dms]]

### 9) Track deployment-oriented constraints separately from benchmark gains
**Why this is adjacent but missing:** the current cluster is benchmark-rich, but the vault has not yet separated benchmark performance from practical constraints such as compute cost, query latency, sensitivity to clean captions, and privacy concerns.

**Pages this would strengthen:** [[tbps-clip]], [[conquer]], [[mvr]], [[bi-irra]]

## Bottom line
If the next research pass can only answer one question, make it this: **which lever matters most under which dataset and noise regime?** That single question would clarify the apparent competition between recipe tuning, robustness, data-centric pretraining, multilingual supervision, and inference-time compensation, and it would make the existing page set much more reusable.
