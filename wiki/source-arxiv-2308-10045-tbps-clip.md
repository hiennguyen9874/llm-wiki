---
title: Source - arXiv 2308.10045 - TBPS-CLIP
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - An Empirical Study of CLIP for Text-based Person Search
  - arXiv 2308.10045
  - TBPS-CLIP paper
tags:
  - source
  - paper
  - arxiv
  - multimodal
  - retrieval
  - clip
  - person-retrieval
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-arxiv-2507-10195-mra
confidence_score: 0.89
quality_score: 0.86
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - TBPS-CLIP
  - text-to-image person retrieval
  - CLIP
  - augmentation pool
  - training tricks
  - N-ITC
  - R-ITC
  - C-ITC
  - few-shot learning
  - model compression
source_file: raw/papers/arxiv-2308.10045-source.tar.gz
source_archive_dir: raw/papers/arxiv-2308.10045-source
source_type: paper
canonical_url: https://arxiv.org/abs/2308.10045
author:
  - Min Cao
  - Yang Bai
  - Ziyin Zeng
  - Mang Ye
  - Min Zhang
published: 2023-08-19
entrypoint: raw/papers/arxiv-2308.10045-source/arxiv.tex
---

# Source - arXiv 2308.10045 - TBPS-CLIP

## Source snapshot
- Title: *An Empirical Study of CLIP for Text-based Person Search*
- Authors: Min Cao, Yang Bai, Ziyin Zeng, Mang Ye, Min Zhang
- Published: 2023-08-19
- Original URL: [https://arxiv.org/abs/2308.10045](https://arxiv.org/abs/2308.10045)
- Normalized source URL: [https://arxiv.org/src/2308.10045](https://arxiv.org/src/2308.10045)
- Raw artifacts preserved at:
  - `raw/papers/arxiv-2308.10045-source.tar.gz`
  - `raw/papers/arxiv-2308.10045-source/`
  - LaTeX entrypoint: `raw/papers/arxiv-2308.10045-source/arxiv.tex`
- Code URL: [https://github.com/Flame-Chasers/TBPS-CLIP](https://github.com/Flame-Chasers/TBPS-CLIP)

## Why it matters
This paper is a direct source on [[text-to-image-person-retrieval]] that argues a careful CLIP recipe can be a strong TBPS baseline without adding a bespoke multimodal interaction encoder. It broadens the in-vault story: performance gains come not only from architecture changes such as [[irra]] or robustness modules like [[rde]], but also from training tricks, data augmentation, loss design, and evaluation of model efficiency.

## Summary
The paper studies CLIP for text-based person search through four lenses: practical training tricks, data augmentation, loss functions, and model generalization/compression.

Its main recipe, **TBPS-CLIP**, stays close to the original CLIP dual-encoder setup while adding:
1. **Training tricks** such as global-gradient backpropagation, dropout, locking bottom layers, and soft labels.
2. **Image and text augmentations**, including an augmentation pool for images, back translation, and random deletion for text.
3. **Retrieval-oriented losses**, notably normalized image-text contrastive loss (N-ITC), reversed image-text contrastive loss (R-ITC), and cyclic image-text contrastive loss (C-ITC), plus self-supervision and multi-view supervision variants in the ablations.
4. **Generalization and compression probes**, including few-shot TBPS and layer-freezing observations for the text encoder.

The paper reports that TBPS-CLIP with ViT-B/16 reaches **73.54 / 65.05 / 61.95 Rank-1** on CUHK-PEDES, ICFG-PEDES, and RSTPReid respectively, while training in only **5 epochs** and remaining simpler than IRRA. It also shows that common augmentations and losses can lift vanilla CLIP substantially, and that TBPS-CLIP transfers better than prompt/adaptor-style CLIP variants in the paper's few-shot setting.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and personal sensitive material before promotion.
- Result: no actionable sensitive material found beyond standard public academic metadata and public code links.

## Extracted entities
- **TBPS-CLIP** — lightweight CLIP-based TBPS baseline/recipe
- **CLIP** — dual-encoder vision-language backbone
- **Training tricks** — global gradients backpropagation, dropout, locked bottom layers, soft labels
- **Augmentation pool** — image augmentation strategy that samples two effective augmentations per iteration
- **N-ITC / R-ITC / C-ITC** — retrieval-oriented contrastive losses
- **Self-supervision / multi-view supervision** — auxiliary losses for data efficiency
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — person retrieval benchmarks
- **CoOp / CLIP-Adapter** — few-shot CLIP baselines used for comparison

## Typed relationships
- [[tbps-clip]] `uses` CLIP dual encoders.
- [[tbps-clip]] `uses` training tricks to improve optimization and regularization.
- [[tbps-clip]] `uses` augmentation pool, back translation, and random deletion for data augmentation.
- [[tbps-clip]] `uses` N-ITC, R-ITC, and C-ITC as retrieval-oriented objectives.
- [[tbps-clip]] `supports` [[text-to-image-person-retrieval]].
- [[tbps-clip]] `related_to` [[irra]].
- [[tbps-clip]] `related_to` [[rde]].
- [[source-arxiv-2308-10045-tbps-clip]] `supports` [[tbps-clip]].
- [[source-arxiv-2308-10045-tbps-clip]] `supports` [[text-to-image-person-retrieval]].

## Candidate claims from the source
#### Claim
- Statement: A careful CLIP recipe can be a strong TBPS baseline without adding a bespoke multimodal interaction module.
- Status: active
- Confidence: 0.92
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Core thesis of the paper.

#### Claim
- Statement: TBPS-CLIP (ViT-B/16) reports 73.54 Rank-1 on CUHK-PEDES, 65.05 on ICFG-PEDES, and 61.95 on RSTPReid, while training in only 5 epochs.
- Status: active
- Confidence: 0.89
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Source-specific benchmark claim; later in-vault sources still shift the benchmark frontier.

#### Claim
- Statement: The paper's ablations show that all four training tricks improve the CLIP baseline on CUHK-PEDES, with global-gradient backpropagation providing the largest single-trick gain.
- Status: active
- Confidence: 0.83
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Reinforced by the training-trick table and the appendix explanation.

#### Claim
- Statement: TBPS-CLIP improves few-shot TBPS and can be compressed by freezing part of the text encoder with limited performance loss.
- Status: active
- Confidence: 0.78
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Supported by the few-shot table and the compression discussion.

## Reinforcement / supersession assessment
- This paper reinforces the in-vault view that CLIP is a strong starting point for [[text-to-image-person-retrieval]] when the training recipe is carefully designed.
- It does **not** replace the architectural contributions of [[irra]] or the robustness framing of [[rde]]; instead, it shows that some gains can come from recipe tuning alone.
- Its reported results are competitive with IRRA and slightly better on some benchmark settings, but later in-vault work still pushes benchmark leadership further.
- No sensitive material or contradiction issues were found, and the paper fits cleanly as a lightweight baseline study rather than a new taxonomy branch.

## Related pages updated
- [[tbps-clip]]
- [[text-to-image-person-retrieval]]
- [[irra]]
- [[rde]]
- [[mra]]

## Ingest notes
- Read from LaTeX source rather than PDF.
- Normalized the user-provided arXiv URL to `/src/`, reused the cached source bundle, and preserved stable raw copies under `raw/papers/`.
- Preserved the original arXiv URL in source metadata.
- Did **not** create the skill-default `knowledge/summary_*.md` file.
- No Base or Canvas update was necessary; the topic is still navigable through linked markdown pages.
