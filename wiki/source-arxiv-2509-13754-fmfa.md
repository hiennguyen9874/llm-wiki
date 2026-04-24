---
title: Source - arXiv 2509.13754 - FMFA
created: 2026-04-24
last_updated: 2026-04-25
source_count: 1
status: reviewed
page_type: source
aliases:
  - Cross-modal Full-Mode Fine-grained Alignment for Text-to-Image Person Retrieval
  - arXiv 2509.13754
  - FMFA paper
tags:
  - source
  - paper
  - arxiv
  - multimodal
  - retrieval
  - clip
  - person-retrieval
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2407-04287-mars
  - source-arxiv-2507-10195-mra
  - source-arxiv-2509-09118-ga-dms
  - source-github-yinhao1102-fmfa
confidence_score: 0.88
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-24
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - FMFA
  - A-SDM
  - EFA
  - IRRA
  - SDM
  - IRR
  - CLIP-ViT-B/16
  - CLIP-Xformer
  - text-to-image person retrieval
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/web-clips/cross-modal-full-mode-fine-grained-alignment-text-to-image-person-retrieval.md
source_type: paper
canonical_url: https://arxiv.org/html/2509.13754v2
author:
  - Hao Yin
  - Xin Man
  - Feiyu Chen
  - Jie Shao
  - Heng Tao Shen
published: 2025
---

# Source - arXiv 2509.13754 - FMFA

## Source snapshot
- Title: *Cross-modal Full-Mode Fine-grained Alignment for Text-to-Image Person Retrieval*
- Authors: Hao Yin, Xin Man, Feiyu Chen, Jie Shao, Heng Tao Shen
- Date: 2025 in the captured source; exact arXiv publication date not verified in this ingest.
- Original URL inferred from embedded figure URLs: [https://arxiv.org/html/2509.13754v2](https://arxiv.org/html/2509.13754v2)
- Code URL: [https://github.com/yinhao1102/FMFA](https://github.com/yinhao1102/FMFA)
- Raw clip preserved at: `raw/web-clips/cross-modal-full-mode-fine-grained-alignment-text-to-image-person-retrieval.md`

## Why it matters
This paper adds a later [[irra]]-family method to the [[text-to-image-person-retrieval]] cluster. It keeps the efficient global retrieval shape of CLIP/IRRA-style methods, but adds explicit training-time fine-grained alignment and an adaptive global-matching loss. That makes it directly relevant to the vault's current synthesis that strong TBPS designs often combine efficient global inference with richer training-time alignment modules.

## Summary
FMFA, or **Full-Mode Fine-grained Alignment**, targets two limitations in prior TIPR methods:
1. global matching losses such as SDM can focus on hard negatives while neglecting positive pairs that are still incorrectly matched;
2. attention-based local alignment can improve representations but usually does not expose or verify the actual local correspondences.

The method combines:
- **A-SDM** (*Adaptive Similarity Distribution Matching*), which increases the loss weight for unmatched positive image-text pairs based on their similarity gap;
- **EFA** (*Explicit Fine-grained Alignment*), which explicitly aggregates token-patch interactions through a sparse similarity matrix and then aligns the aggregated joint embeddings with text/image embeddings using hard coding;
- the [[irra]]-style **IRR** masked-language interaction and **ID loss** training stack;
- CLIP-ViT-B/16 and CLIP-Xformer encoders with global-feature retrieval at inference.

## Key claims
#### Claim
- Statement: FMFA improves a CLIP/IRRA-style global matching framework by combining A-SDM, EFA, IRR, and ID loss during training while retaining efficient global-feature inference.
- Status: active
- Confidence: 0.84
- Evidence: this source, Sections 3.2-3.4 and Table 9.
- Last confirmed: 2026-04-24
- Notes: Architecture and runtime claim are source-reported.

#### Claim
- Statement: A-SDM adapts SDM by upweighting unmatched positive image-text pairs; when a positive pair is already correctly matched, the adaptive weight defaults to 1 and the loss reduces toward SDM behavior.
- Status: active
- Confidence: 0.86
- Evidence: this source, Section 3.2.
- Last confirmed: 2026-04-24
- Notes: The paper frames this as correcting SDM's hard-negative emphasis.

#### Claim
- Statement: EFA provides explicit training-time token-patch alignment using sparse similarity matrix aggregation and hard coding alignment.
- Status: active
- Confidence: 0.84
- Evidence: this source, Section 3.3.
- Last confirmed: 2026-04-24
- Notes: Treat as an explicit-local-alignment mechanism within a global retrieval framework.

#### Claim
- Statement: FMFA reports the best results among compared global matching methods on CUHK-PEDES, ICFG-PEDES, and RSTPReid, but does not uniformly beat all local methods in the comparison tables.
- Status: active
- Confidence: 0.78
- Evidence: this source, Tables 3-5 and Section 4.2.
- Last confirmed: 2026-04-24
- Notes: Keep the benchmark claim scoped to the paper's compared global-method category.

## Benchmark and ablation evidence
The paper evaluates on CUHK-PEDES, ICFG-PEDES, and RSTPReid. In its reported no-ReID-pretraining setting, FMFA improves over the reimplemented IRRA baseline on the main metrics across those datasets. With NAM or HAM ReID-domain pretraining, the reported gains over IRRA remain but become smaller.

Ablations report that A-SDM improves over SDM and that EFA usually improves the baseline, though the paper notes that EFA's sparse hard selection can sometimes lose information. This nuance matters because it makes FMFA evidence for explicit fine-grained alignment, but not proof that harder sparsity is always preferable.

## Limitations and cautions
- The source itself states that the fixed sparsity threshold in EFA may discard semantically useful patches.
- Exact arXiv publication metadata was not verified during this ingest; the raw clip has a placeholder date.
- The public GitHub repository has now been ingested separately as [[source-github-yinhao1102-fmfa]], which confirms the core global-inference/A-SDM/EFA implementation story but also introduces an apparent pretraining-path reproduction caveat in the inspected snapshot.
- Benchmark leadership should be stated as *among compared global matching methods*, not as an overall field-final SOTA claim.

## Relationships
- `supports` [[text-to-image-person-retrieval]]
- `introduces` [[fmfa]]
- `extends` [[irra]]
- `uses` A-SDM, EFA, IRR, ID loss, CLIP-ViT-B/16, CLIP-Xformer
- `evaluated_on` CUHK-PEDES, ICFG-PEDES, RSTPReid
- `reinforces` [[synthesis-tbps-hybrid-design-space]]
- `informs` [[text-to-image-person-retrieval-research-agenda]]

## Pages updated
- [[fmfa]]
- [[text-to-image-person-retrieval]]
- [[irra]]
- [[text-to-image-person-retrieval-research-agenda]]
- [[synthesis-tbps-hybrid-design-space]]

## Follow-up
- Verify the live arXiv metadata/date if the source becomes citation-critical.
- Validate whether the apparent `processor/processor.py` pretraining-path hazard in [[source-github-yinhao1102-fmfa]] is snapshot-specific or affects practical reproduction.
- Compare FMFA against newer in-vault methods under a normalized benchmark taxonomy rather than relying on one paper's category labels.
