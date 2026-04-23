---
title: Noisy Correspondence
created: 2026-04-23
last_updated: 2026-04-23
source_count: 2
status: draft
page_type: concept
aliases:
  - NC
  - pair-level correspondence noise
tags:
  - machine-learning
  - multimodal
  - robustness
  - data-quality
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2308-09911-rde
  - source-github-qinyang79-rde
confidence_score: 0.77
quality_score: 0.77
evidence_count: 2
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - RDE
  - text-to-image person retrieval
  - false positive pairs
  - noisy labels
---

# Noisy Correspondence

Noisy correspondence is a pair-level supervision problem where a cross-modal pair is treated as matched even though the two items are not truly aligned. In [[source-arxiv-2308-09911-rde]], the paper studies this for [[text-to-image-person-retrieval]] and describes such cases as **false positive pairs**.

## Summary
The key distinction from ordinary label noise is that the identity/class labels of the underlying items may still be valid while the *cross-modal pairing* is wrong. In TIReID, this means an image and a text description can be incorrectly treated as a positive pair, which can teach the model the wrong visual-semantic association. The companion implementation [[source-github-qinyang79-rde]] operationalizes this by shuffling captions against images at configurable rates or replaying precomputed noise-index files, then trying to recover likely clean pairs through dual-branch consensus filtering.

## Relationships
- `related_to` noisy labels
- `supports` [[rde]] as a robustness target
- `affects` [[text-to-image-person-retrieval]]
- `contradicts` the assumption that all training image-text pairs are clean

## Evidence / claims
#### Claim
- Statement: In TIReID, noisy correspondence can arise when mismatched image-text pairs are used as positive pairs during training.
- Status: active
- Confidence: 0.79
- Evidence: [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Source-specific framing grounded in the paper's introduction and case-study examples.

#### Claim
- Statement: Pair-level correspondence noise can cause overfitting to incorrect visual-semantic associations even when the broader task setup and model family remain unchanged.
- Status: active
- Confidence: 0.75
- Evidence: [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Supported by the paper's robustness framing and comparison plots.

#### Claim
- Statement: In the public RDE implementation, noisy correspondence is operationalized as caption-shuffle permutations over otherwise valid training items, with optional precomputed permutation files for reproducible 20% / 50% / 80% synthetic-noise experiments.
- Status: active
- Confidence: 0.86
- Evidence: [[source-github-qinyang79-rde]]
- Last confirmed: 2026-04-23
- Notes: Useful implementation-level clarification of what the paper's synthetic noise setting means in practice.

## Open questions
- What fraction of common TIReID datasets contain meaningful real noisy correspondence?
- How much synthetic-shuffle noise matches real annotation failure patterns?
- Which robustness techniques transfer best to other multimodal retrieval tasks?

## Sources
- [[source-arxiv-2308-09911-rde]]
- [[source-github-qinyang79-rde]]
