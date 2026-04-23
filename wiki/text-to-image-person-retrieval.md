---
title: Text-to-Image Person Retrieval
created: 2026-04-23
last_updated: 2026-04-23
source_count: 2
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
  - source-arxiv-2308-09911-rde
confidence_score: 0.79
quality_score: 0.82
evidence_count: 2
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - IRRA
  - RDE
  - noisy correspondence
  - CLIP
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
---

# Text-to-Image Person Retrieval

Text-to-image person retrieval is a multimodal retrieval task where a system receives a natural-language description of a person and must retrieve matching images from a gallery. The main challenge is aligning language and visual appearance despite modality mismatch, viewpoint/pose variation, ambiguity in textual descriptions, and potentially incorrect image-text pairings.

## Current in-vault view
The vault currently has two directly relevant sources:
- [[source-arxiv-2303-12501-irra]] presents [[irra]] as a CLIP-based method that improves retrieval through training-time implicit relation reasoning and similarity distribution matching.
- [[source-arxiv-2308-09911-rde]] presents [[rde]] as a later robustness-oriented method that explicitly models [[noisy-correspondence]] and reports stronger historical benchmark results than IRRA.

Together, these sources suggest a useful in-vault progression: CLIP-based global retrieval became a strong baseline, then later work argued that pair-level annotation noise is important enough to change both the task framing and the training objective design.

## Key points
- The task sits at the intersection of image-text retrieval and person re-identification.
- CLIP-initialized dual encoders appear as a strong backbone family in both in-vault sources.
- A key design tension is balancing fine-grained cross-modal alignment against inference-time simplicity.
- [[irra]] emphasizes implicit relation learning and efficient retrieval.
- [[rde]] adds the claim that noisy image-text pairings are common enough to require explicit robustness mechanisms such as CCD and TAL.
- Current vault evidence is still narrow, so benchmark conclusions should be treated as historical-within-vault rather than field-final.

## Evidence / claims
#### Claim
- Statement: A key design tension in text-to-image person retrieval is balancing fine-grained cross-modal alignment against inference-time efficiency.
- Status: active
- Confidence: 0.76
- Evidence: [[source-arxiv-2303-12501-irra]], [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Reinforced by both sources, which improve alignment differently while preserving efficient retrieval structure.

#### Claim
- Statement: CLIP-initialized dual encoders are a strong backbone family for this task and can be improved with additional cross-modal reasoning or robustness objectives.
- Status: active
- Confidence: 0.81
- Evidence: [[source-arxiv-2303-12501-irra]], [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Directly reinforced across both ingested papers.

#### Claim
- Statement: Noisy correspondence is an important practical failure mode for this task because mismatched image-text pairs can mislead visual-semantic alignment learning.
- Status: active
- Confidence: 0.79
- Evidence: [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Currently supported by one in-vault source, but it materially changes how the task should be interpreted.

#### Claim
- Statement: IRRA's in-vault historical benchmark leadership claim is superseded by RDE's later reported results.
- Status: active
- Confidence: 0.77
- Evidence: [[source-arxiv-2303-12501-irra]], [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Historical benchmark claim only; future sources may supersede both.
- Supersedes: [[irra]]

## Related pages
- [[irra]]
- [[rde]]
- [[noisy-correspondence]]
- [[source-arxiv-2303-12501-irra]]
- [[source-arxiv-2308-09911-rde]]

## Sources
- [[source-arxiv-2303-12501-irra]]
- [[source-arxiv-2308-09911-rde]]
