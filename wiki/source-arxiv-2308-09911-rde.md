---
title: Source - arXiv 2308.09911 - RDE
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - Noisy-Correspondence Learning for Text-to-Image Person Re-identification
  - arXiv 2308.09911
  - RDE paper
tags:
  - source
  - paper
  - arxiv
  - multimodal
  - retrieval
  - clip
  - robustness
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
confidence_score: 0.91
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
  - RDE
  - noisy correspondence
  - text-to-image person retrieval
  - CLIP
  - CCD
  - TAL
source_file: raw/papers/arxiv-2308.09911-source.tar.gz
source_archive_dir: raw/papers/arxiv-2308.09911-source
source_type: paper
canonical_url: https://arxiv.org/abs/2308.09911
author:
  - Yang Qin
  - Yingke Chen
  - Dezhong Peng
  - Xi Peng
  - Joey Tianyi Zhou
  - Peng Hu
published: 2023-08-19
entrypoint: raw/papers/arxiv-2308.09911-source/main.tex
---

# Source - arXiv 2308.09911 - RDE

## Source snapshot
- Title: *Noisy-Correspondence Learning for Text-to-Image Person Re-identification*
- Authors: Yang Qin, Yingke Chen, Dezhong Peng, Xi Peng, Joey Tianyi Zhou, Peng Hu
- Published: 2023-08-19
- Original URL: [https://arxiv.org/abs/2308.09911](https://arxiv.org/abs/2308.09911)
- Normalized source URL: [https://arxiv.org/src/2308.09911](https://arxiv.org/src/2308.09911)
- Raw artifacts preserved at:
  - `raw/papers/arxiv-2308.09911-source.tar.gz`
  - `raw/papers/arxiv-2308.09911-source/`
  - LaTeX entrypoint: `raw/papers/arxiv-2308.09911-source/main.tex`
- Code URL: [https://github.com/QinYang79/RDE](https://github.com/QinYang79/RDE)

## Why it matters
This paper is directly relevant to [[text-to-image-person-retrieval]] because it argues that the task's usual clean-pair assumption is often false in practice. It introduces [[noisy-correspondence]] as a distinct failure mode, uses [[irra]] as a key baseline/reference point, and proposes [[rde]] as a robustness-oriented extension that improves historical benchmark results while reducing overfitting under synthetic noise.

## Summary
The paper studies text-to-image person re-identification under **noisy correspondence (NC)**: image-text pairs that are treated as positives even though they are mismatched. The authors argue this is distinct from class-label noise because the failure happens at the cross-modal pair level.

The proposed method is **RDE** (*Robust Dual Embedding*), built from three main ideas:
1. **Dual embeddings**: a Basic Global Embedding (BGE) and Token Selection Embedding (TSE) built on CLIP image/text encoders.
2. **Confident Consensus Division (CCD)**: uses loss-based clean/noisy splits from both embeddings, then takes their consensus to identify reliable clean pairs and likely noisy pairs.
3. **Triplet Alignment Loss (TAL)**: replaces hardest-negative-only triplet ranking with a log-sum-exp upper bound over all negatives, aiming to preserve hard-negative pressure without destabilizing training under noise.

The paper reports publication-time improvements over prior TIReID baselines on CUHK-PEDES, ICFG-PEDES, and RSTPReid both at 0% synthetic noise and under 20%/50% noise. In-vault, this acts as newer evidence than [[source-arxiv-2303-12501-irra]] for historical benchmark leadership and for the importance of robustness to pair-level annotation errors.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and personal sensitive material before promotion.
- Result: no actionable sensitive material found beyond standard public academic metadata, public code URL, and grant acknowledgments already present in the public paper.
- Downstream notes intentionally avoid reproducing unnecessary personal contact or grant-administration detail.

## Extracted entities
- **RDE** — robust TIReID method/framework
- **Noisy correspondence** — mismatched image-text pairs treated as positives
- **CCD** — consensus-based clean/noisy pair division module
- **TAL** — triplet alignment loss using log-sum-exp over negatives
- **BGE** — basic global embedding branch
- **TSE** — token selection embedding branch
- **IRRA** — prior CLIP-based TIReID baseline referenced and outperformed historically
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — benchmark datasets

## Typed relationships
- [[rde]] `uses` CLIP image and text encoders.
- [[rde]] `uses` CCD for clean/noisy pair filtering.
- [[rde]] `uses` TAL for robust alignment under noisy pairs.
- [[rde]] `supports` [[text-to-image-person-retrieval]].
- [[rde]] `supports` [[noisy-correspondence]].
- [[rde]] `related_to` [[irra]].
- [[rde]] `supersedes` [[irra]] on publication-time benchmark leadership claims in this vault.
- [[source-arxiv-2308-09911-rde]] `supports` [[rde]].
- [[source-arxiv-2308-09911-rde]] `supports` [[text-to-image-person-retrieval]].
- [[source-arxiv-2308-09911-rde]] `supports` [[noisy-correspondence]].
- [[source-arxiv-2308-09911-rde]] `supersedes` [[source-arxiv-2303-12501-irra]] for historical best-reported benchmark results.

## Candidate claims from the source
#### Claim
- Statement: Noisy correspondence is a practically important TIReID failure mode where mismatched image-text pairs are incorrectly treated as positive supervision.
- Status: active
- Confidence: 0.90
- Evidence: [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Central framing claim of the paper and supported by both motivation text and case-study examples.

#### Claim
- Statement: RDE combines dual-granularity embeddings, CCD-based clean-pair consensus filtering, and TAL to improve robustness against pair-level annotation noise.
- Status: active
- Confidence: 0.89
- Evidence: [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Directly supported by the method section and ablations.

#### Claim
- Statement: Relative to IRRA, the paper reports stronger publication-time benchmark results on CUHK-PEDES, ICFG-PEDES, and RSTPReid at 0% synthetic noise.
- Status: active
- Confidence: 0.86
- Evidence: [[source-arxiv-2308-09911-rde]], [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-23
- Notes: Historical comparison only. In the paper's main table, RDE reports Rank-1 gains over IRRA of +2.56 on CUHK-PEDES, +4.22 on ICFG-PEDES, and +5.15 on RSTPReid.
- Supersedes: [[source-arxiv-2303-12501-irra]]

#### Claim
- Statement: RDE reduces apparent overfitting under 20% and 50% synthetic noisy correspondence compared with ordinary TIReID baselines.
- Status: active
- Confidence: 0.84
- Evidence: [[source-arxiv-2308-09911-rde]]
- Last confirmed: 2026-04-23
- Notes: Supported by best-vs-last checkpoint comparisons and the robustness plots; broader real-world generalization remains limited to the paper's datasets and setup.

## Reinforcement / supersession assessment
- [[source-arxiv-2303-12501-irra]] is reinforced as an important CLIP-based TIReID baseline and design reference.
- The earlier in-vault claim that [[irra]] held publication-time benchmark leadership is now **superseded** by this newer 2023 source.
- The new source does **not** invalidate IRRA's architectural importance; it mainly weakens IRRA's historical best-results status and adds a stronger argument that robustness to pair-level noise matters.
- No in-vault contradiction was found on the existence of pair-level annotation noise; rather, this source deepens the task framing.

## Related pages updated
- [[rde]]
- [[noisy-correspondence]]
- [[text-to-image-person-retrieval]]
- [[irra]]

## Ingest notes
- Read from LaTeX source rather than PDF.
- Normalized the user-provided arXiv URL to `/src/`, reused the local cache path policy, and preserved stable raw copies under `raw/papers/`.
- Did **not** create the skill-default `knowledge/summary_*.md` file.
- Considered Base/Canvas changes but deferred because the topic remains small enough to navigate through linked markdown pages.
