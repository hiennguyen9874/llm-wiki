---
title: Source - GitHub Flame-Chasers - TBPS-CLIP
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - Flame-Chasers/TBPS-CLIP
  - TBPS-CLIP code repository
  - TBPS-CLIP implementation
tags:
  - source
  - code
  - github
  - multimodal
  - retrieval
  - clip
  - person-retrieval
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2308-10045-tbps-clip
confidence_score: 0.90
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
  - CLIP
  - augmentation pool
  - back translation
  - random deletion
  - SimCLR
  - MixGen
  - MLM
  - N-ITC
  - R-ITC
  - C-ITC
  - soft labels
  - AllGather
  - original CLIP checkpoint
  - simplified preset
source_file: raw/codes/TBPS-CLIP
source_type: code
canonical_url: https://github.com/Flame-Chasers/TBPS-CLIP
author:
  - Flame-Chasers
entrypoint: raw/codes/TBPS-CLIP/README.md
---

# Source - GitHub Flame-Chasers - TBPS-CLIP

## Source snapshot
- Repository: `Flame-Chasers/TBPS-CLIP`
- Repository URL: [https://github.com/Flame-Chasers/TBPS-CLIP](https://github.com/Flame-Chasers/TBPS-CLIP)
- Raw artifacts preserved at:
  - `raw/codes/TBPS-CLIP/`
- Primary entrypoints:
  - `raw/codes/TBPS-CLIP/README.md`
  - `raw/codes/TBPS-CLIP/main.py`
  - `raw/codes/TBPS-CLIP/eval.py`
- Execution scripts:
  - `raw/codes/TBPS-CLIP/shell/train.sh`
  - `raw/codes/TBPS-CLIP/shell/eval.sh`

## Why it matters
This repository is the public implementation companion to [[source-arxiv-2308-10045-tbps-clip]]. It makes the paper's TBPS-CLIP recipe concrete: the code spells out the distributed CLIP training loop, the image/text augmentation stack, the optional auxiliary losses, the original-CLIP checkpoint loading path, and the simplified preset used by the provided shell scripts.

## Summary
The repo implements a CLIP-based text-based person search model with a modular training stack:
1. **Data and augmentation**: an image augmentation pool, self-supervised views, back translation, random deletion, and optional MixGen.
2. **Modeling**: CLIP-style visual and text transformers, distributed `AllGather`, a SimCLR projection head, an optional MLM cross-modal branch, and an identity classifier.
3. **Objectives**: normalized image-text contrastive loss, reversed ITC, cyclic ITC, SimCLR self-supervision, MLM, and ID loss, with soft-label mixing driven by `softlabel_ratio`.
4. **Practical plumbing**: Torch JIT loading for original CLIP checkpoints, positional-embedding interpolation, token-vocab expansion with `<|mask|>`, and `--simplified` configs for a leaner launch path.

The implementation confirms that TBPS-CLIP is not just a paper recipe in abstract; it is a configurable training system with several optional branches that can be turned on or off depending on the experiment.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and personal sensitive material before promotion.
- Result: no actionable sensitive material found. The repository contains public code, config paths, and dependency metadata only.

## Extracted entities
- **TBPS-CLIP codebase** — public GitHub implementation
- **CLIP** — dual-encoder backbone
- **AllGather** — custom autograd distributed gather op for contrastive training
- **Augmentation pool** — `Choose`-based image augmentation sampler
- **EDA** — text random deletion and related augmentation helper
- **Back translation** — caption substitution via `captions_bt`
- **SimCLR** — optional image self-supervision
- **MixGen** — optional mixed image-text augmentation
- **MLM** — masked language modeling support
- **N-ITC / R-ITC / C-ITC** — retrieval-oriented contrastive losses
- **Soft labels** — contrastive target mixing via `softlabel_ratio`
- **Original CLIP checkpoint** — Torch JIT-loaded pretrained weights
- **Simplified preset** — the `--simplified` launch path

## Typed relationships
- [[source-github-flame-chasers-tbps-clip]] `supports` [[tbps-clip]].
- [[source-github-flame-chasers-tbps-clip]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-flame-chasers-tbps-clip]] `related_to` [[source-arxiv-2308-10045-tbps-clip]].
- [[source-github-flame-chasers-tbps-clip]] `related_to` [[tbps-clip]].
- [[source-github-flame-chasers-tbps-clip]] `related_to` [[clip]].
- [[tbps-clip]] `uses` CLIP-style dual encoders.
- [[tbps-clip]] `uses` augmentation pool, back translation, random deletion, MixGen, SimCLR self-supervision, MLM, and ID loss in its modular recipe.
- [[tbps-clip]] `uses` N-ITC, R-ITC, and C-ITC as retrieval-oriented losses.
- [[tbps-clip]] `depends_on` distributed training and CLIP checkpoint loading for the public implementation.

## Evidence / claims
#### Claim
- Statement: The public TBPS-CLIP codebase implements a modular CLIP-based person retrieval training system with optional MixGen, SimCLR self-supervision, MLM, and ID-loss branches.
- Status: active
- Confidence: 0.91
- Evidence: [[source-github-flame-chasers-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Directly visible in `main.py`, `model/tbps_model.py`, and the auxiliary modules.

#### Claim
- Statement: The repository's provided `--simplified` launch path disables some auxiliary components, exposing a leaner TBPS-CLIP configuration for quick runs and ablations.
- Status: active
- Confidence: 0.88
- Evidence: [[source-github-flame-chasers-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Supported by `shell/train.sh`, `shell/eval.sh`, and `config/s.config.yaml`.

#### Claim
- Statement: The implementation extends CLIP's tokenizer with a `<|mask|>` token and supports masked language modeling in the code, even though MLM is off in the default config.
- Status: active
- Confidence: 0.86
- Evidence: [[source-github-flame-chasers-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Source-specific implementation detail from `text_utils/simple_tokenizer.py` and `text_utils/tokenizer.py`.

## Reinforcement / supersession assessment
- This repository reinforces the paper's claim that TBPS-CLIP is primarily a recipe-driven baseline rather than a bespoke multimodal-architecture jump.
- It also clarifies that the public implementation is more modular than the paper's high-level summary alone: multiple losses and augmentations are gated by config switches.
- No contradiction or supersession issue was found; the code is a direct implementation companion to the paper source.

## Open questions
- The optimizer references `schedule_config.ratio_factor`; the shipped YAML configs do not define it, so the optional cross/classifier/MLM parameter-group scaling path may need an extra config field when those branches are enabled.
- The visual transformer freezes `conv1` by default, which partially matches the paper's "locking bottom layers" idea but may not cover every layer-freezing interpretation.

## Related pages updated
- [[source-arxiv-2308-10045-tbps-clip]]
- [[tbps-clip]]
- [[text-to-image-person-retrieval]]

## Ingest notes
- Read the README, training/evaluation entrypoints, configs, data pipeline, transformers, loss code, tokenizer, and accompanying figures/scripts.
- Screened the repository for sensitive material before promotion; none found.
- No Base or Canvas update was necessary because the topic still fits cleanly in linked markdown pages.
