---
title: Source - arXiv 2507.10195 - MRA
created: 2026-04-23
last_updated: 2026-04-24
source_count: 2
status: reviewed
page_type: source
aliases:
  - Minimizing the Pretraining Gap: Domain-aligned Text-Based Person Retrieval
  - arXiv 2507.10195
  - MRA paper
tags:
  - source
  - paper
  - arxiv
  - multimodal
  - retrieval
  - synthetic-data
  - domain-adaptation
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-github-shuyu-xjtu-mra
confidence_score: 0.92
quality_score: 0.88
evidence_count: 1
first_seen: 2026-04-23
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes:
  - source-arxiv-2308-09911-rde
superseded_by: []
related_entities:
  - MRA
  - DaD
  - SDA
  - text-to-image person retrieval
  - CLIP
  - Swin Transformer
  - BERT
source_file: raw/papers/arxiv-2507.10195-source.tar.gz
source_archive_dir: raw/papers/arxiv-2507.10195-source
source_type: paper
canonical_url: https://arxiv.org/abs/2507.10195?utm_source=chatgpt.com
author:
  - Shuyu Yang
  - Yaxiong Wang
  - Yongrui Li
  - Li Zhu
  - Zhedong Zheng
published: 2025-07-14
entrypoint: raw/papers/arxiv-2507.10195-source/main.tex
---

# Source - arXiv 2507.10195 - MRA

## Source snapshot
- Title: *Minimizing the Pretraining Gap: Domain-aligned Text-Based Person Retrieval*
- Authors: Shuyu Yang, Yaxiong Wang, Yongrui Li, Li Zhu, Zhedong Zheng
- Published: 2025-07-14
- Original URL: [https://arxiv.org/abs/2507.10195?utm_source=chatgpt.com](https://arxiv.org/abs/2507.10195?utm_source=chatgpt.com)
- Normalized source URL: [https://arxiv.org/src/2507.10195](https://arxiv.org/src/2507.10195)
- Raw artifacts preserved at:
  - `raw/papers/arxiv-2507.10195-source.tar.gz`
  - `raw/papers/arxiv-2507.10195-source/`
  - LaTeX entrypoint: `raw/papers/arxiv-2507.10195-source/main.tex`
- Code URL: [https://github.com/Shuyu-XJTU/MRA](https://github.com/Shuyu-XJTU/MRA)
- Code companion page: [[source-github-shuyu-xjtu-mra]]

## Why it matters
This paper extends the vault's [[text-to-image-person-retrieval]] thread beyond both [[irra]] and [[rde]]. Instead of focusing mainly on inference-efficient alignment or robustness to [[noisy-correspondence]], it argues that **synthetic pretraining only helps fully when the synthetic data are domain-aligned to the downstream pedestrian domain**. It contributes both a synthetic benchmark construction pipeline and a new method, making it relevant to method design, data-centric training strategy, and historical benchmark progression.

## Summary
The paper proposes a two-level domain adaptation pipeline for text-based person retrieval:
1. **Domain-aware Diffusion (DaD)** fine-tunes a text-to-image diffusion model toward the target pedestrian domain so synthetic images better match real benchmark style.
2. **Synthetic Domain-Aligned dataset (SDA)** uses DaD-generated images, BLIP2 caption diversification, and Grounding DINO region-phrase annotation to create a large synthetic pretraining set with both image-text and region-phrase supervision.
3. **Multi-granularity Relation Alignment (MRA)** pretrains retrieval models using both global image-text alignment and explicit region-phrase alignment, then fine-tunes on real datasets.

Relative to prior in-vault sources, this paper adds a different explanatory frame: not only can TIReID methods improve through better alignment objectives or noise robustness, but **the pretraining corpus itself can be engineered to reduce the synthetic-to-real domain gap**. The paper reports later historical benchmark improvements over both [[irra]] and [[rde]] on CUHK-PEDES, ICFG-PEDES, and RSTPReid.

## Sensitive material screen
- Screened for secrets, credentials, tokens, PII, and sensitive non-public operational data before promotion.
- Result: no actionable sensitive material found beyond public academic metadata, public code URL, and funding acknowledgments already present in the public paper.
- Downstream notes avoid reproducing unnecessary contact and grant-administration detail.

## Extracted entities
- **MRA** — retrieval framework using image-text and region-phrase alignment during pretraining
- **DaD** — Domain-aware Diffusion module for image-level synthetic-to-real style adaptation
- **SDA** — Synthetic Domain-Aligned dataset used for pretraining
- **Region-Phrase Contrastive (RPC) Learning** — fine-grained contrastive objective
- **Region-Phrase Matching (RPM) Learning** — fine-grained binary matching objective with hard negatives
- **BLIP2** — image captioner used to diversify synthetic text descriptions
- **Grounding DINO** — open-set detector used to annotate region-phrase pairs
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — evaluation benchmarks
- **MALS** — earlier synthetic pretraining dataset used as comparison baseline

## Typed relationships
- [[mra]] `uses` [[domain-aware-diffusion]].
- [[mra]] `uses` [[synthetic-domain-aligned-dataset]].
- [[mra]] `uses` region-phrase alignment objectives RPC and RPM.
- [[domain-aware-diffusion]] `supports` [[synthetic-domain-aligned-dataset]].
- [[synthetic-domain-aligned-dataset]] `supports` [[mra]].
- [[mra]] `supports` [[text-to-image-person-retrieval]].
- [[mra]] `related_to` [[rde]].
- [[mra]] `related_to` [[irra]].
- [[mra]] `supersedes` [[rde]] on publication-time benchmark leadership claims in this vault.
- [[source-arxiv-2507-10195-mra]] `supports` [[mra]].
- [[source-arxiv-2507-10195-mra]] `supports` [[domain-aware-diffusion]].
- [[source-arxiv-2507-10195-mra]] `supports` [[synthetic-domain-aligned-dataset]].
- [[source-arxiv-2507-10195-mra]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-shuyu-xjtu-mra]] `implements` the retrieval-side MRA method described by this paper.
- [[source-arxiv-2507-10195-mra]] `supersedes` [[source-arxiv-2308-09911-rde]] for historical best-reported benchmark results.

## Candidate claims from the source
#### Claim
- Statement: A major bottleneck in synthetic pretraining for text-based person retrieval is the domain gap between generated images and real pedestrian benchmarks, including differences in illumination, color, and viewpoint.
- Status: active
- Confidence: 0.91
- Evidence: [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Central framing claim supported by the introduction, benchmark-construction discussion, and FID comparison.

#### Claim
- Statement: Domain-aware Diffusion and the resulting SDA dataset improve synthetic pretraining by making generated person images visually closer to the target domain than earlier synthetic data such as MALS.
- Status: active
- Confidence: 0.88
- Evidence: [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Supported by the dataset-construction section and the reported FID comparison; broad transfer beyond the reported datasets remains source-local.

#### Claim
- Statement: MRA improves retrieval by jointly optimizing global image-text alignment and explicit region-phrase alignment during pretraining.
- Status: active
- Confidence: 0.89
- Evidence: [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Direct method claim reinforced by ablations against image-text-only pretraining.

#### Claim
- Statement: Relative to earlier in-vault methods, the paper reports stronger publication-time benchmark results on CUHK-PEDES, ICFG-PEDES, and RSTPReid.
- Status: active
- Confidence: 0.87
- Evidence: [[source-arxiv-2507-10195-mra]], [[source-arxiv-2308-09911-rde]], [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-23
- Notes: Historical comparison only. The paper reports Rank-1 scores of 77.21 on CUHK-PEDES, 68.93 on ICFG-PEDES, and 68.15 on RSTPReid.
- Supersedes: [[source-arxiv-2308-09911-rde]]

#### Claim
- Statement: Region-phrase alignment appears more effective than using only global image-text alignment, while even finer object-word alignment can become counterproductive.
- Status: active
- Confidence: 0.82
- Evidence: [[source-arxiv-2507-10195-mra]]
- Last confirmed: 2026-04-23
- Notes: Supported by the ablation table and discussion; useful as an in-vault design heuristic rather than a field-wide law.

## Reinforcement / supersession assessment
- [[source-arxiv-2303-12501-irra]] is reinforced as an important CLIP-era baseline and early benchmark leader.
- [[source-arxiv-2308-09911-rde]] is reinforced on the importance of better training objectives and richer task framing, but its historical benchmark-leadership claim is now **superseded** in-vault by this 2025 paper.
- This source does **not** directly contradict [[noisy-correspondence]]; instead it adds a separate data-centric explanation for why pretraining may fail.
- The new evidence broadens the vault's picture of progress: benchmark gains came from at least three levers across sources—better alignment objectives ([[irra]]), robustness to pair noise ([[rde]]), and synthetic-to-real domain alignment with region-phrase supervision ([[mra]]).

## Related pages updated
- [[mra]]
- [[domain-aware-diffusion]]
- [[synthetic-domain-aligned-dataset]]
- [[text-to-image-person-retrieval]]
- [[rde]]
- [[irra]]
- [[source-arxiv-2308-09911-rde]]

## Ingest notes
- Read from LaTeX source rather than PDF after normalizing the user-provided arXiv URL to `/src/`.
- Reused/downloaded the cached source bundle under `~/.cache/nanochat/knowledge/2507.10195*`, then preserved stable raw copies under `raw/papers/`.
- Did **not** create the skill-default `knowledge/summary_*.md` file.
- Considered Base/Canvas updates but deferred because the topic remains navigable through linked markdown pages and does not yet need a dedicated visual overlay.
