---
title: Source - arXiv 2601.18625 - CONQUER
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - CONQUER: Context-Aware Representation with Query Enhancement for Text-Based Person Search
  - arXiv 2601.18625
  - CONQUER paper
tags:
  - source
  - paper
  - arxiv
  - multimodal
  - retrieval
  - query-refinement
  - optimal-transport
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
confidence_score: 0.92
quality_score: 0.88
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - CONQUER
  - CARE
  - IQE
  - Optimal Transport
  - Qwen2.5-VL-7B
  - text-to-image person retrieval
  - ambiguous queries
  - incomplete queries
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/web-clips/arxiv-2601-18625v1-conquer-context-aware-representation-with-query-enhancement-for-text-based-person-search.md
source_type: paper
canonical_url: https://arxiv.org/html/2601.18625v1
author:
  - Zequn Xie
published: 2026-01-26
---

# Source - arXiv 2601.18625 - CONQUER

## Source snapshot
- Title: *CONQUER: Context-Aware Representation with Query Enhancement for Text-Based Person Search*
- Authors: Zequn Xie
- Published: 2026-01-26
- Original URL: [https://arxiv.org/html/2601.18625v1](https://arxiv.org/html/2601.18625v1)
- Cleaned web clip preserved at: `raw/web-clips/arxiv-2601-18625v1-conquer-context-aware-representation-with-query-enhancement-for-text-based-person-search.md`
- Code URL: [https://github.com/zqxie77/CONQUER](https://github.com/zqxie77/CONQUER)

## Why it matters
This paper extends the vault's [[text-to-image-person-retrieval]] thread with a new argument: strong TBPS systems should not only learn better training-time alignment, but should also improve vague or incomplete user queries at inference time. Relative to current in-vault methods, [[conquer]] matters because it combines a training-time alignment stack with a plug-and-play query-refinement stage, broadening the design space beyond recipe tuning ([[tbps-clip]]), pair-level robustness ([[rde]]), attribute-focused supervision ([[mars]]), synthetic/domain-aligned pretraining ([[mra]]), and token-level noise handling with curated web data ([[ga-dms]]).

## Summary
The paper proposes a two-stage framework:
1. **CARE** (*Context-Aware Representation Enhancement*) improves training-time alignment through multi-granularity encoding, complementary pair mining, and context-guided optimal matching with Optimal Transport.
2. **IQE** (*Interactive Query Enhancement*) improves inference-time retrieval by selecting anchor images, extracting higher-confidence visual attributes through an MLLM-based question-answer loop, and fusing those attributes back into the original query for reranking.

The source's central claim is that TBPS suffers both from cross-modal mismatch during training and from ambiguous, underspecified user queries during inference. CONQUER addresses both sides at once rather than treating retrieval as a purely passive matching problem.

## Sensitive material screen
- Screened for secrets, credentials, tokens, PII, and sensitive non-public operational data before promotion.
- Result: no actionable sensitive material found beyond standard public academic metadata and a public code URL.
- Downstream wiki notes avoid copying unnecessary implementation-specific threshold detail unless it supports durable claims.

## Extracted entities
- **CONQUER** — two-stage TBPS framework
- **CARE** — training-time context-aware representation enhancement module
- **IQE** — inference-time interactive query enhancement module
- **Optimal Transport** — alignment mechanism used inside CARE
- **Complementary pair mining** — hard-negative mining strategy for refinable pairs
- **Anchor identification** — selects candidate images for inference-time query enrichment
- **Attribute-driven enrichment** — uses anchor-derived attributes to refine incomplete queries
- **Qwen2.5-VL-7B** — multimodal reasoning model used in the paper's IQE setup
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — evaluation benchmarks

## Typed relationships
- [[conquer]] `uses` CARE.
- [[conquer]] `uses` IQE.
- [[care]] `uses` Optimal Transport.
- [[iqe]] `uses` anchor identification.
- [[iqe]] `uses` attribute-driven enrichment.
- [[conquer]] `supports` [[text-to-image-person-retrieval]].
- [[source-arxiv-2601-18625-conquer]] `supports` [[conquer]].
- [[source-arxiv-2601-18625-conquer]] `supports` [[text-to-image-person-retrieval]].
- [[source-arxiv-2601-18625-conquer]] `related_to` [[mars]].
- [[source-arxiv-2601-18625-conquer]] `related_to` [[rde]].
- [[source-arxiv-2601-18625-conquer]] `related_to` [[ga-dms]].
- [[source-arxiv-2601-18625-conquer]] `related_to` [[mra]].

## Candidate claims from the source
#### Claim
- Statement: CONQUER improves TBPS by combining training-time context-aware alignment with inference-time query refinement for ambiguous or incomplete descriptions.
- Status: active
- Confidence: 0.90
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Direct framing and architecture claim from the source.

#### Claim
- Statement: CARE strengthens cross-modal embeddings through multi-granularity encoding, complementary pair mining, and context-guided Optimal Transport matching.
- Status: active
- Confidence: 0.86
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Method-specific training claim.

#### Claim
- Statement: IQE is a plug-and-play inference module that can refine vague or incomplete text queries without retraining the backbone.
- Status: active
- Confidence: 0.88
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Durable design claim because it changes where adaptation happens in the retrieval pipeline.

#### Claim
- Statement: CONQUER reports 77.13 Rank-1 / 68.75 mAP on CUHK-PEDES, 67.70 Rank-1 / 40.36 mAP on ICFG-PEDES, and 68.40 Rank-1 / 51.73 mAP on RSTPReid.
- Status: active
- Confidence: 0.89
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Source-specific benchmark report from the main comparison table.

#### Claim
- Statement: CONQUER shows especially meaningful robustness gains in cross-domain and incomplete-query settings relative to strong baselines.
- Status: active
- Confidence: 0.82
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Supported by the cross-domain table and the paper's incomplete-query framing; keep as source-local rather than field-general.

## Reinforcement / supersession assessment
- [[source-arxiv-2407-04287-mars]] is reinforced on the value of explicit attribute information, but CONQUER shifts that emphasis toward inference-time query enrichment rather than only training-time attribute supervision.
- [[source-arxiv-2308-09911-rde]] and [[source-arxiv-2509-09118-ga-dms]] are reinforced on the broader idea that passive alignment alone is insufficient; CONQUER adds ambiguity-handling at query time instead of only noise-aware training.
- [[source-arxiv-2509-09118-ga-dms]] remains the current in-vault benchmark leader; this paper broadens the design space without superseding that historical benchmark position.
- No material contradiction was found that requires a disputed state. The main update is an additional method family emphasizing inference-time adaptability.

## Related pages updated
- [[conquer]]
- [[text-to-image-person-retrieval]]
- [[ga-dms]]
- [[mars]]

## Ingest notes
- Read from the arXiv HTML page with Defuddle and saved a cleaned web clip under `raw/web-clips/`.
- Preserved the original URL in source metadata via `canonical_url`.
- Did **not** create the skill-default `knowledge/summary_*.md` file.
- Considered Base/Canvas updates but deferred because the current topic graph remains navigable through linked markdown pages.
