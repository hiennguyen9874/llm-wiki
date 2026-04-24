---
title: FMFA
created: 2026-04-24
last_updated: 2026-04-25
source_count: 2
status: draft
page_type: concept
aliases:
  - Full-Mode Fine-grained Alignment
  - Cross-modal Full-Mode Fine-grained Alignment
  - A-SDM and EFA
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
  - source-arxiv-2509-13754-fmfa
  - source-github-yinhao1102-fmfa
confidence_score: 0.85
quality_score: 0.85
evidence_count: 2
first_seen: 2026-04-24
last_confirmed: 2026-04-25
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - text-to-image person retrieval
  - IRRA
  - A-SDM
  - EFA
  - SDM
  - IRR
  - CLIP
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
---

# FMFA

FMFA (*Full-Mode Fine-grained Alignment*) is a method for [[text-to-image-person-retrieval]] introduced in [[source-arxiv-2509-13754-fmfa]] and clarified implementation-wise by [[source-github-yinhao1102-fmfa]]. It extends a CLIP/[[irra]]-style global matching framework with two training-time additions: **A-SDM**, which adaptively emphasizes unmatched positive pairs, and **EFA**, which makes token-patch alignment more explicit through sparse similarity aggregation and hard coding alignment.

## Summary
FMFA is best read as an IRRA-family global retrieval method. It uses CLIP-ViT-B/16 and CLIP-Xformer encoders, retains IRRA-style implicit relation reasoning and ID loss, but changes the alignment pressure in two ways:

1. **Global alignment:** A-SDM modifies SDM so incorrectly matched positive image-text pairs receive stronger loss weight.
2. **Fine-grained alignment:** EFA explicitly aggregates image patches for each text token using a sparse similarity matrix, then aligns the resulting joint embeddings with text and image embeddings.

The design goal is to get better local cross-modal grounding during training without turning inference into a heavy local matching or cross-attention reranking pipeline. The code companion reinforces this reading: the public evaluator still ranks with normalized global text/image embeddings, while the new local structure lives in the loss path.

## Architecture and training objective
FMFA's training objective combines:
- ID loss for identity-level global grouping;
- IRR loss from [[irra]] for masked-language-style implicit cross-modal relation reasoning;
- A-SDM loss for adaptive global image-text distribution matching;
- EFA loss for explicit local token-patch alignment.

At inference, the paper presents FMFA as a global matching method that computes global image/text features rather than using local features for every retrieval comparison. The public repo confirms this through `encode_image`, `encode_text`, and a direct similarity-matrix evaluator in `utils/metrics.py`.

## A-SDM
A-SDM (*Adaptive Similarity Distribution Matching*) is a modification of SDM. The paper argues that SDM's temperature-controlled distribution matching can overemphasize hard negatives while undercorrecting positives that should match but are ranked behind another image or text.

A-SDM estimates whether a positive pair is unmatched by comparing the maximum batch similarity against the similarity of the corresponding positive pair. When the positive pair is already correctly matched, the adaptive weight defaults to 1; when it is not, the weight rises and pulls the positive pair closer in the joint embedding space. The code companion makes this concrete by scaling the mismatch gap with a lightweight heuristic (`diff * 0.1 + 1`) inside `compute_sdm(..., use_weight=True)`.

## EFA
EFA (*Explicit Fine-grained Alignment*) targets the opacity of attention-only local alignment. It:
- computes similarities between text-token hidden states and image-patch hidden states;
- min-max normalizes and sparsifies the token-patch similarity matrix;
- aggregates high-similarity patches into language-grouped vision embeddings;
- applies hard coding alignment and LSE pooling to align joint embeddings with original text and image embeddings.

The code companion sharpens the implementation details: the token-patch matrix is min-max normalized, sparsified with a fixed threshold of `1 / num_patches`, row-normalized, and then optimized with `compute_minmax_info_loss` over the aggregated patch representation.

This makes FMFA useful evidence for a middle route in the TBPS design space: explicit local grounding during training while preserving global retrieval at inference.

## Benchmark position
The source reports FMFA as the best method among compared **global matching** methods on CUHK-PEDES, ICFG-PEDES, and RSTPReid. It improves over the paper's IRRA reimplementation in the no-ReID-pretraining setting and shows smaller gains when NAM or HAM ReID-domain pretraining is used. The code companion aligns with this split by shipping separate `run.sh` and `finetune.sh` recipes for the two regimes.

The claim should stay scoped: the paper's tables include local methods that beat FMFA on some metrics, so FMFA should not be treated as overall field-final SOTA across all method categories.

## Relationships
- `extends` [[irra]] by refining SDM into A-SDM and adding EFA.
- `supports` [[text-to-image-person-retrieval]].
- `reinforces` [[synthesis-tbps-hybrid-design-space]] by showing a training-time alignment module can keep global inference.
- `informs` [[text-to-image-person-retrieval-research-agenda]] by adding a sparse explicit-alignment rung to the fine-grained grounding ladder.
- `is_implemented_by` [[source-github-yinhao1102-fmfa]].

## Evidence / claims
#### Claim
- Statement: FMFA is an IRRA-family global matching method that combines A-SDM, EFA, IRR, and ID loss while preserving global-feature inference.
- Status: active
- Confidence: 0.88
- Evidence: [[source-arxiv-2509-13754-fmfa]], [[source-github-yinhao1102-fmfa]]
- Last confirmed: 2026-04-25
- Notes: The code companion confirms that inference still runs through normalized global embeddings and direct similarity ranking.

#### Claim
- Statement: A-SDM focuses additional optimization pressure on unmatched positive image-text pairs, complementing the hard-negative focus of prior SDM-style training.
- Status: active
- Confidence: 0.88
- Evidence: [[source-arxiv-2509-13754-fmfa]], [[source-github-yinhao1102-fmfa]]
- Last confirmed: 2026-04-25
- Notes: The repo exposes a concrete weighting heuristic for this idea inside `compute_sdm`.

#### Claim
- Statement: EFA provides explicit fine-grained token-patch aggregation but can lose information when fixed sparsity discards semantically useful patches.
- Status: active
- Confidence: 0.86
- Evidence: [[source-arxiv-2509-13754-fmfa]], [[source-github-yinhao1102-fmfa]]
- Last confirmed: 2026-04-25
- Notes: The code confirms a fixed sparsity threshold of `1 / num_patches`, making the limitation implementation-concrete rather than purely conceptual.

#### Claim
- Statement: FMFA reports stronger results than IRRA among compared global matching methods on CUHK-PEDES, ICFG-PEDES, and RSTPReid.
- Status: active
- Confidence: 0.78
- Evidence: [[source-arxiv-2509-13754-fmfa]], [[source-github-yinhao1102-fmfa]]
- Last confirmed: 2026-04-25
- Notes: Benchmark claim remains paper-scoped and category-scoped; the code companion mainly confirms the matching training/evaluation scaffold and the split between no-pretraining versus NAM/HAM finetuning.

## Open questions
- Does the apparent `processor/processor.py` pretraining-path hazard affect actual reproduction, or is it a snapshot-specific bug?
- Would an adaptive sparsity strategy improve EFA without discarding semantically useful patches?
- How should FMFA be normalized against later data-centric, multilingual, and inference-time adaptation methods in the vault?

## Sources
- [[source-arxiv-2509-13754-fmfa]]
- [[source-github-yinhao1102-fmfa]]
