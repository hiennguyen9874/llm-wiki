---
title: Source - arXiv 2407.04287 - MARS
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - MARS: Paying more attention to visual attributes for text-based person search
  - arXiv 2407.04287
  - MARS paper
tags:
  - source
  - paper
  - arxiv
  - multimodal
  - retrieval
  - attribute-learning
  - mask-autoencoder
  - person-retrieval
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-github-ergastialex-mars
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-arxiv-2308-10045-tbps-clip
  - source-arxiv-2507-10195-mra
confidence_score: 0.92
quality_score: 0.87
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - MARS
  - RaSa
  - ALBEF
  - visual reconstruction loss
  - attribute loss
  - masked autoencoder
  - spaCy
  - Grad-CAM
  - text-to-image person retrieval
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/web-clips/arxiv-2407-04287v1-mars-paying-more-attention-to-visual-attributes-for-text-based-person-search.md
source_type: paper
canonical_url: https://arxiv.org/html/2407.04287v1
author:
  - Alex Ergasti
  - Tomaso Fontanini
  - Claudio Ferrari
  - Massimo Bertozzi
  - Andrea Prati
published: 2024-07-05
---

# Source - arXiv 2407.04287 - MARS

## Source snapshot
- Title: *MARS: Paying more attention to visual attributes for text-based person search*
- Authors: Alex Ergasti, Tomaso Fontanini, Claudio Ferrari, Massimo Bertozzi, Andrea Prati
- Published: 2024-07-05
- Original URL: [https://arxiv.org/html/2407.04287v1](https://arxiv.org/html/2407.04287v1)
- Cleaned web clip preserved at: `raw/web-clips/arxiv-2407-04287v1-mars-paying-more-attention-to-visual-attributes-for-text-based-person-search.md`
- Code URL: [https://github.com/ErgastiAlex/MARS](https://github.com/ErgastiAlex/MARS)

## Why it matters
This paper adds a third explanatory frame to the vault's [[text-to-image-person-retrieval]] story. Instead of focusing primarily on CLIP recipe tuning ([[tbps-clip]]), implicit relation learning ([[irra]]), noisy-pair robustness ([[rde]]), or synthetic pretraining/domain alignment ([[mra]]), it argues that TBPS improves when models pay explicit attention to visual attributes and reconstruct masked image patches using text-conditioned supervision. The companion code source [[source-github-ergastialex-mars]] now confirms the exact public realization of that idea.

## Summary
The paper proposes **MARS** (*Mae-Attribute-Relation-Sensitive*), a TBPS architecture built on a RaSa/ALBEF-style retrieval stack with two main additions:
1. **Visual Reconstruction Loss**: a masked autoencoder reconstructs masked image patches with help from text embeddings.
2. **Attribute Loss**: adjective-noun chunks are extracted from captions and matched against the image so each attribute contributes explicitly to retrieval.

A third implementation choice strengthens reranking: the cross-modal encoder is equipped with cross-attention in all 12 blocks rather than only the last few. The paper argues that these changes reduce the tendency to ignore discriminative attributes and make the system more robust to vague captions and intra-identity variation.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and sensitive private information before promotion.
- Result: no actionable sensitive material found beyond standard public author contact info, a public code URL, and the paper's public academic metadata.

## Extracted entities
- **MARS** — TBPS architecture and method
- **RaSa** — baseline framework the paper extends
- **ALBEF** — pretrained initialization family used by the paper
- **Visual Reconstruction Loss** — text-conditioned masked autoencoder objective
- **Attribute Loss** — chunk-level supervision over adjective-noun phrases
- **Cross-Modal Encoder** — reranking encoder with full cross-attention
- **spaCy** — used to extract attribute chunks
- **Grad-CAM** — used for qualitative attention-map analysis
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — benchmark datasets

## Typed relationships
- [[mars]] `uses` text-conditioned masked autoencoding.
- [[mars]] `uses` attribute loss over adjective-noun chunks.
- [[mars]] `uses` full cross-attention reranking.
- [[mars]] `supports` [[text-to-image-person-retrieval]].
- [[source-arxiv-2407-04287-mars]] `supports` [[mars]].
- [[source-arxiv-2407-04287-mars]] `supports` [[text-to-image-person-retrieval]].
- [[source-arxiv-2407-04287-mars]] `related_to` [[tbps-clip]].
- [[source-arxiv-2407-04287-mars]] `related_to` [[irra]].
- [[source-arxiv-2407-04287-mars]] `related_to` [[rde]].
- [[source-arxiv-2407-04287-mars]] `related_to` [[mra]].
- [[source-arxiv-2407-04287-mars]] `related_to` [[source-github-ergastialex-mars]].

## Candidate claims from the source
#### Claim
- Statement: MARS improves TBPS by combining visual reconstruction, attribute-level supervision, and stronger cross-modal reranking.
- Status: active
- Confidence: 0.88
- Evidence: [[source-arxiv-2407-04287-mars]]
- Last confirmed: 2026-04-23
- Notes: Direct summary of the paper's architecture and motivation.

#### Claim
- Statement: The attribute loss is most effective when paired with masked autoencoding or expanded cross-attention, and it mainly improves ranking quality rather than raw top-1 alone.
- Status: active
- Confidence: 0.82
- Evidence: [[source-arxiv-2407-04287-mars]]
- Last confirmed: 2026-04-23
- Notes: Supported by the ablation table and discussion.

#### Claim
- Statement: MARS reports 77.62 Rank-1 / 71.41 mAP on CUHK-PEDES, 67.60 Rank-1 / 44.93 mAP on ICFG-PEDES, and 67.55 Rank-1 / 52.92 mAP on RSTPReid.
- Status: active
- Confidence: 0.90
- Evidence: [[source-arxiv-2407-04287-mars]]
- Last confirmed: 2026-04-23
- Notes: Source-specific benchmark report from the main results table.

#### Claim
- Statement: The paper's best gain signal is mAP, which suggests attribute-aware supervision helps ranking consistency even when top-1 gains are smaller or dataset-dependent.
- Status: active
- Confidence: 0.79
- Evidence: [[source-arxiv-2407-04287-mars]]
- Last confirmed: 2026-04-23
- Notes: Interpretation grounded in the results and ablation sections.

## Reinforcement / supersession assessment
- MARS reinforces the vault view that TBPS performance can come from more than one lever: recipe tuning ([[tbps-clip]]), implicit relation learning ([[irra]]), robustness to noisy pairs ([[rde]]), synthetic domain alignment ([[mra]]), and now explicit attribute salience plus text-conditioned reconstruction.
- The companion code source [[source-github-ergastialex-mars]] reinforces rather than contradicts the paper, adding exact implementation detail around the seven-loss objective, full-cross-attention encoder configuration, and top-128 reranking path.
- It partially supersedes earlier publication-time benchmark claims on CUHK-PEDES from [[irra]], [[rde]], and [[tbps-clip]], but it does not flatten the whole benchmark story because [[mra]] later remains stronger on ICFG-PEDES and RSTPReid.
- No contradiction or sensitive-material issue was found; the main result is a broadened design space, not a conflict.

## Related pages updated
- [[mars]]
- [[text-to-image-person-retrieval]]
- [[tbps-clip]]
- [[irra]]
- [[rde]]
- [[mra]]
- [[source-github-ergastialex-mars]]

## Ingest notes
- Read from the arXiv HTML page with Defuddle and saved a cleaned web clip under `raw/web-clips/`.
- Preserved the original URL in source metadata via `canonical_url`.
- Did **not** create the skill-default `knowledge/summary_*.md` file.
- Base/Canvas changes were considered but deferred; the topic remains navigable through linked markdown pages.
- Later code ingest via [[source-github-ergastialex-mars]] added implementation-level confirmation without changing the paper-level claim structure.
