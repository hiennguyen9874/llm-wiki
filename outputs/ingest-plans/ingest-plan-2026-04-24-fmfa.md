---
title: Ingest Plan - FMFA Paper
created: 2026-04-24
last_updated: 2026-04-24
status: reviewed
page_type: ingest_plan
aliases:
  - FMFA ingest plan
  - Cross-modal Full-Mode Fine-grained Alignment ingest plan
tags:
  - ingest-plan
  - machine-learning
  - multimodal
  - retrieval
visibility: private
related_sources:
  - source-arxiv-2509-13754-fmfa
---

# Ingest Plan - FMFA Paper

## Decision summary
- Recommendation: proceed.
- Save this plan durably: yes, because this non-trivial paper affects the active TBPS cluster, creates a new method page, and qualifies IRRA-family benchmark/design-space claims.
- Immediate blockers: none.

## Source
- Source: `raw/web-clips/cross-modal-full-mode-fine-grained-alignment-text-to-image-person-retrieval.md`
- Type: arXiv HTML web clip / paper source.
- Identity metadata: likely arXiv `2509.13754v2`; title *Cross-modal Full-Mode Fine-grained Alignment for Text-to-Image Person Retrieval*; authors Hao Yin, Xin Man, Feiyu Chen, Jie Shao, Heng Tao Shen; source date placeholder `(XX XXX 2025)`; code URL `https://github.com/yinhao1102/FMFA`.
- Purpose relevance: strengthens the active research-and-learning cluster around [[text-to-image-person-retrieval]].

## Safety / privacy
- Disposition: clear.
- Downstream exclusion: omit public author emails from canonical summaries unless needed for source provenance.

## Knowledge extraction
- FMFA combines a CLIP/IRRA-style global matching framework with A-SDM, EFA, IRR, and ID loss while retaining global-feature inference.
- A-SDM adapts SDM to upweight unmatched positive image-text pairs rather than only emphasizing hard negatives.
- EFA computes token-patch similarities, sparsifies a normalized similarity matrix, aggregates image patches into language-grouped vision embeddings, and applies hard coding alignment losses.
- FMFA reports best results among compared global matching methods on CUHK-PEDES, ICFG-PEDES, and RSTPReid, but not necessarily over all local methods.
- FMFA's fixed sparsity threshold is an author-stated limitation because it may discard useful semantic information.

## Integration plan
- Create `wiki/source-arxiv-2509-13754-fmfa.md`.
- Create `wiki/fmfa.md`.
- Update `wiki/text-to-image-person-retrieval.md`, `wiki/irra.md`, `wiki/text-to-image-person-retrieval-research-agenda.md`, and `wiki/synthesis-tbps-hybrid-design-space.md`.
- Update `wiki/index.md`, `wiki/overview.md`, and append `wiki/log.md`.

## Review items
- Non-blocking: verify live arXiv metadata before treating date/version as final.
- Non-blocking: ingest `https://github.com/yinhao1102/FMFA` as a code companion if implementation/reproducibility matters.
- Non-blocking: later normalize FMFA against MRA/GA-DMS/CONQUER/Bi-IRRA/MVR under a benchmark taxonomy.
