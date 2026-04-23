---
title: Source - GitHub QinYang79 - RDE
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - QinYang79/RDE
  - RDE code repository
  - RDE implementation
tags:
  - source
  - code
  - github
  - multimodal
  - retrieval
  - clip
  - robustness
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2308-09911-rde
  - source-arxiv-2303-12501-irra
confidence_score: 0.91
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
  - RDE
  - noisy correspondence
  - CLIP
  - BGE
  - TSE
  - CCD
  - TAL
  - GaussianMixture
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
  - IRRA
source_file: raw/codes/RDE
source_type: code
canonical_url: https://github.com/QinYang79/RDE
author:
  - QinYang79
entrypoint: raw/codes/RDE/README.md
---

# Source - GitHub QinYang79 - RDE

## Source snapshot
- Repository: `QinYang79/RDE`
- Repository URL: [https://github.com/QinYang79/RDE](https://github.com/QinYang79/RDE)
- Raw artifacts preserved at:
  - `raw/codes/RDE/`
- Primary entrypoints:
  - `raw/codes/RDE/README.md`
  - `raw/codes/RDE/2024-CVPR-RDE/train.py`
  - `raw/codes/RDE/2024-CVPR-RDE/test.py`
  - `raw/codes/RDE/2024-CVPR-RDE/model/build.py`
  - `raw/codes/RDE/2024-CVPR-RDE/processor/processor.py`
- Execution script:
  - `raw/codes/RDE/2024-CVPR-RDE/run_rde.sh`

## Why it matters
This repository is the public implementation companion to [[source-arxiv-2308-09911-rde]]. It makes the paper's robustness story concrete: the code shows how noisy correspondence is injected or replayed from saved index files, how the dual branches are trained, how clean/noisy pair selection is operationalized with consensus over two per-sample loss models, and how inference combines the global and token-selection branches.

## Summary
The repo implements RDE as an IRRA-derived CLIP training stack with RDE-specific dual-branch robustness logic:
1. **Backbone and embeddings**: a CLIP vision/text backbone feeds a **Basic Global Embedding (BGE)** path plus **Token Selection Embedding (TSE)** layers that pool top-attended image patches and text tokens.
2. **Noise injection and replay**: the training dataset can either load precomputed noise indices from `noiseindex/*.npy` or synthesize caption shuffles at a requested noise rate, preserving a `real_correspondences` mask internally for analysis.
3. **Consensus clean/noisy splitting**: `processor.py` computes per-sample losses separately for BGE and TSE, normalizes them, fits a two-component `GaussianMixture` to each branch, then forms a consensus clean mask (`label_hat`) from the two predicted splits before weighting losses.
4. **Training and evaluation**: the default launch script trains for 60 epochs with TAL, `select_ratio=0.3`, `tau=0.015`, and `margin=0.1`; evaluation reports BGE, TSE, and averaged `BGE+TSE` retrieval scores.

The implementation also reveals several concrete caveats not obvious from the paper alone: the codebase is based on [[irra]], some scripts contain hardcoded local filesystem paths, `processor.py` still carries an unused `BetaMixture1D` helper while the active path uses Gaussian mixtures, and the README documents a post-release issue note that the `model.train()` call around line 217 can trade correctness of a bug fix against degraded noisy-scene performance.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and personal sensitive material before promotion.
- Result: no actionable secrets found.
- The repo does contain developer-local filesystem paths (for example under `/home/qinyang/...`) and a public contact email in inherited utility metadata. These are not promoted as canonical knowledge beyond noting that local-path assumptions exist in the scripts.

## Extracted entities
- **RDE codebase** — public GitHub implementation companion
- **BGE** — global embedding branch
- **TSE** — token-selection embedding branch
- **CCD** — consensus clean/noisy pair division implemented via dual branch loss modeling
- **TAL** — triplet alignment loss used in the default run script
- **GaussianMixture** — active clean/noisy splitter used in `processor.py`
- **BetaMixture1D** — unused helper retained in the training processor
- **noiseindex files** — precomputed synthetic correspondence-noise permutations for CUHK-PEDES, ICFG-PEDES, and RSTPReid
- **IRRA scaffold** — upstream implementation base acknowledged by the repository
- **BGE+TSE averaging** — evaluation-time score fusion strategy

## Typed relationships
- [[source-github-qinyang79-rde]] `supports` [[rde]].
- [[source-github-qinyang79-rde]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-qinyang79-rde]] `supports` [[noisy-correspondence]].
- [[source-github-qinyang79-rde]] `related_to` [[source-arxiv-2308-09911-rde]].
- [[source-github-qinyang79-rde]] `related_to` [[source-arxiv-2303-12501-irra]].
- [[rde]] `uses` BGE and TSE branches in the public implementation.
- [[rde]] `uses` two Gaussian-mixture fits to derive a consensus clean-pair mask.
- [[rde]] `uses` packaged noise-index files for reproducible synthetic-noise experiments.
- [[rde]] `depends_on` a CLIP/IRRA-style training scaffold.
- [[rde]] `uses` BGE+TSE score averaging at inference.
- [[irra]] `supports` the implementation lineage of [[rde]] through the acknowledged codebase dependency.

## Evidence / claims
#### Claim
- Statement: The public RDE code implements CCD by computing per-sample losses for the BGE and TSE branches separately, fitting a two-component Gaussian mixture to each normalized loss distribution, and taking a consensus clean mask to weight subsequent training losses.
- Status: active
- Confidence: 0.92
- Evidence: [[source-github-qinyang79-rde]]
- Last confirmed: 2026-04-23
- Notes: Directly supported by `processor/processor.py`, `model/build.py`, and `model/objectives.py`.

#### Claim
- Statement: The repository operationalizes noisy correspondence through caption-shuffle permutations, including bundled `noiseindex/*.npy` files for CUHK-PEDES, ICFG-PEDES, and RSTPReid.
- Status: active
- Confidence: 0.89
- Evidence: [[source-github-qinyang79-rde]]
- Last confirmed: 2026-04-23
- Notes: Supported by `datasets/bases.py`, the shipped `noiseindex/` directory, and `run_rde.sh`.

#### Claim
- Statement: The public implementation keeps inference simple by evaluating the BGE branch, the TSE branch, and their average rather than introducing a heavier late-stage reranker.
- Status: active
- Confidence: 0.87
- Evidence: [[source-github-qinyang79-rde]]
- Last confirmed: 2026-04-23
- Notes: Supported by `utils/metrics.py`.

#### Claim
- Statement: The repository is implementation-wise derived from IRRA rather than being a ground-up training system rewrite.
- Status: active
- Confidence: 0.85
- Evidence: [[source-github-qinyang79-rde]], [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-23
- Notes: README explicitly acknowledges IRRA as the code base; the option schema and CLIP-style scaffolding are consistent with that lineage.

#### Claim
- Statement: The shipped code includes an implementation caveat where the README says the post-release fix for issue 8 can hurt noisy-scene performance and may be bypassed by commenting out `model.train()` in `processor.py`.
- Status: active
- Confidence: 0.83
- Evidence: [[source-github-qinyang79-rde]]
- Last confirmed: 2026-04-23
- Notes: Treat as a repository-specific operational caveat, not as a general field claim.

## Reinforcement / supersession assessment
- This repository strongly reinforces the paper-level account of [[rde]] as a dual-branch robustness method rather than a purely conceptual proposal.
- It adds implementation-level detail missing from the paper summary, especially the exact consensus procedure, the packaged noise-index artifacts, and the evaluation-time BGE/TSE averaging.
- It also reinforces [[irra]] as an implementation ancestor: RDE's public code extends an IRRA-like training scaffold rather than replacing the CLIP baseline family entirely.
- No benchmark contradiction or supersession issue was introduced by the code itself; the main new information is operational detail plus the README's post-release caveat.

## Open questions
- The code keeps an unused `BetaMixture1D` helper beside the active Gaussian-mixture path; was beta-mixture filtering part of an earlier ablation or abandoned variant?
- The README's issue-8 note suggests the training/eval mode transition affects robustness; which results in the paper or repo releases correspond to the pre-fix versus post-fix behavior?
- How sensitive are the reported results to the hardcoded default hyperparameters in `run_rde.sh` versus broader sweeps?

## Related pages updated
- [[source-arxiv-2308-09911-rde]]
- [[rde]]
- [[noisy-correspondence]]
- [[text-to-image-person-retrieval]]
- [[irra]]

## Ingest notes
- Read the repository README, launch scripts, training/evaluation entrypoints, dataset loaders, embedding modules, objectives, evaluator, and selected CLIP backbone code.
- Screened the repository for sensitive material before promotion; found local paths and a public email but no actionable secrets.
- Considered Base/Canvas updates but deferred because the method cluster remains navigable through linked markdown pages and the new source adds implementation detail rather than a new structural branch.
