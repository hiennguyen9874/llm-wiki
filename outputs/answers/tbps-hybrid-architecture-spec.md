---
title: TBPS Hybrid Architecture Spec
created: 2026-04-23
last_updated: 2026-04-23
source_count: 9
status: reviewed
page_type: answer
aliases:
  - TBPS hybrid stack
  - text-based person search hybrid architecture
tags:
  - machine-learning
  - multimodal
  - retrieval
  - answer
  - architecture
  - person-retrieval
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
confidence_score: 0.83
quality_score: 0.85
evidence_count: 9
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - IRRA
  - TBPS-CLIP
  - RDE
  - MARS
  - MRA
  - GA-DMS
  - CONQUER
  - Bi-IRRA
  - MVR
  - CLIP
  - noisy correspondence
  - expression drift
---

# TBPS Hybrid Architecture Spec

## Recommendation
Build a **modular hybrid** instead of choosing one paper. The best vault-local design is:

**CLIP/IRRA backbone + TBPS-CLIP recipe + RDE/GA-DMS robustness + MARS/MRA grounding + CONQUER/MVR inference-time adaptation + Bi-IRRA multilingual branch**.

This is a synthesis, not a tested single paper. It is the most plausible way to combine the strongest levers currently represented in the vault.

## Concrete architecture

### 1) Core encoder
- **Image encoder:** CLIP ViT backbone.
- **Text encoder:** CLIP text encoder.
- **Optional IRRA-style interaction:** add implicit relation reasoning during training, but keep the final retrieval path globally efficient.

Why this base:
- [[tbps-clip]] shows a tuned CLIP recipe can already be strong.
- [[irra]] shows IRRA-style implicit relation reasoning is a durable CLIP-era baseline.

### 2) Training stack
Use a multi-loss training schedule with four layers:

#### Layer A: retrieval recipe loss
- Use TBPS-CLIP-style augmentations and retrieval losses.
- Include the N-ITC / R-ITC / C-ITC family.
- Keep the regularization tricks: dropout, locked bottom layers, soft labels, and augmentation pool.

**Supported by:** [[tbps-clip]], [[source-arxiv-2308-10045-tbps-clip]]

#### Layer B: pair-noise robustness
- Add an RDE-style clean/noisy pair split.
- Use consensus filtering to downweight suspicious image-text pairs.
- Use TAL-like robust alignment instead of hard-negative-only triplet pressure.

**Supported by:** [[rde]], [[source-arxiv-2308-09911-rde]]

#### Layer C: token/phrase grounding
- Add GA-DMS-style token scoring to identify likely noisy vs informative words.
- Mask noisy tokens.
- Reconstruct informative tokens.
- Add MARS attribute loss so adjective-noun chunks get explicit supervision.
- Add MRA region-phrase alignment for stronger fine-grained grounding.

**Supported by:** [[ga-dms]], [[mars]], [[mra]], [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2407-04287-mars]], [[source-arxiv-2507-10195-mra]]

#### Layer D: identity and global alignment
- Keep an IRRA-style identity classification loss or equivalent identity grouping.
- Preserve a global similarity head for efficient retrieval.
- If using MRA, pretrain on domain-aligned synthetic data first, then fine-tune on real benchmarks.

**Supported by:** [[irra]], [[mra]]

### 3) Data strategy
Choose one of two pretraining routes:

#### Route 1: synthetic-aligned
- Build on [[domain-aware-diffusion]] + [[synthetic-domain-aligned-dataset]].
- Best if you can control data generation and want a strong domain-matched pretraining set.

#### Route 2: real web-scale
- Build on [[webperson]] and GA-DMS-style large curated web pretraining.
- Best if scale and diversity matter more than synthetic control.

**Supported by:** [[mra]], [[ga-dms]], [[webperson]]

## Inference stack

### 4) Default retrieval
- Run the dual encoder on the raw query.
- Retrieve top-k by global similarity.

### 5) Query adaptation gate
Only invoke extra inference modules when the query is likely underspecified.

Trigger examples:
- short query
- low top-1 / top-2 score margin
- weak attribute density
- multilingual query

### 6) Query enhancement branch
If triggered:
- Use **CONQUER-style IQE** to pick anchor images, extract likely missing attributes, and rewrite the query.
- Use **MVR-style multi-view reformulation** to generate several semantically equivalent views and aggregate them.
- Score the original query and reformulated queries jointly.

### 7) Multilingual branch
If the deployment is multilingual:
- Use **Bi-IRRA-style multilingual training objectives** instead of translation-only inference.
- Keep separate multilingual validation sets if possible.

## Practical implementation order

### Minimal viable hybrid
1. Start with **TBPS-CLIP** recipe.
2. Add **RDE** clean/noisy filtering.
3. Add **MARS** attribute loss.
4. Add **CONQUER** query enhancement only for low-confidence queries.

This is the smallest hybrid that already combines recipe, robustness, grounding, and inference-time adaptation.

### Full hybrid
1. TBPS-CLIP recipe.
2. IRRA-style implicit relation reasoning.
3. RDE pair-noise robustness.
4. GA-DMS token denoising.
5. MARS attribute loss.
6. MRA region-phrase alignment + domain-aligned synthetic pretraining.
7. CONQUER IQE.
8. MVR multi-view reformulation.
9. Bi-IRRA multilingual branch if needed.

## Supported facts vs inference

### Supported facts
- CLIP recipe tuning is strong on TBPS ([[tbps-clip]]).
- Pair-level noisy correspondence matters ([[rde]]).
- Token-level noise matters too ([[ga-dms]]).
- Attribute/phrase/region grounding helps ([[mars]], [[mra]]).
- Query enhancement and multi-view reformulation help at inference time ([[conquer]], [[mvr]]).
- Multilingual TBPS is a real extension, not a side task ([[bi-irra]]).

### Inference
- These levers are mostly complementary if staged rather than piled on all at once.
- The most stable hybrid is likely to put **robustness and grounding in training** and **query compensation in inference**.
- A query-confidence gate will reduce compute and avoid unnecessary hallucination from MLLM-based enrichment.

### Uncertainty
- No source in the vault proves this full hybrid is globally optimal.
- Benchmark leadership is dataset-dependent; [[bi-irra]] and [[mvr]] are mixed rather than one replacing the other everywhere.
- [[mvr]] benchmark readings should be treated conservatively because the source table had rendering noise.
- Historical SOTA claims for [[irra]], [[rde]], [[mra]], and [[ga-dms]] are superseded.

## Bottom line
If you want the most concrete hybrid answer: **train a CLIP-based dual encoder with RDE + GA-DMS + MARS/MRA losses, then add CONQUER + MVR only when the query is uncertain; use Bi-IRRA when multilinguality matters.**

## Informed by
[[text-to-image-person-retrieval]], [[irra]], [[tbps-clip]], [[rde]], [[mars]], [[mra]], [[ga-dms]], [[conquer]], [[bi-irra]], [[mvr]]
