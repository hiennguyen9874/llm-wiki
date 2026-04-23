---
title: Source - GitHub anosorae - IRRA
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - anosorae/IRRA
  - IRRA code repository
  - IRRA implementation
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
  - source-arxiv-2303-12501-irra
  - source-github-qinyang79-rde
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
  - IRRA
  - CLIP
  - similarity distribution matching
  - masked language modeling
  - cross-modal transformer
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
  - ViT-B/16
  - global similarity retrieval
source_file: raw/codes/IRRA
source_type: code
canonical_url: https://github.com/anosorae/IRRA
author:
  - anosorae
entrypoint: raw/codes/IRRA/README.md
---

# Source - GitHub anosorae - IRRA

## Source snapshot
- Repository: `anosorae/IRRA`
- Repository URL: [https://github.com/anosorae/IRRA](https://github.com/anosorae/IRRA)
- Raw artifacts preserved at:
  - `raw/codes/IRRA/`
- Primary entrypoints:
  - `raw/codes/IRRA/README.md`
  - `raw/codes/IRRA/train.py`
  - `raw/codes/IRRA/test.py`
  - `raw/codes/IRRA/model/build.py`
  - `raw/codes/IRRA/model/objectives.py`
  - `raw/codes/IRRA/processor/processor.py`
  - `raw/codes/IRRA/datasets/build.py`
- Execution script:
  - `raw/codes/IRRA/run_irra.sh`

## Why it matters
This repository is the public implementation companion to [[source-arxiv-2303-12501-irra]]. It confirms that IRRA is operationalized as a CLIP-based dual-encoder retrieval system whose extra reasoning module is used during training, while inference still relies on normalized global image/text embeddings and direct similarity ranking.

## Summary
The repo implements IRRA as a compact CLIP-centered training stack:
1. **Backbone and resolution adaptation**: `model/clip_model.py` loads an OpenAI CLIP checkpoint, resizes positional embeddings for person-retrieval image geometry, and uses `ViT-B/16` by default with `img_size=(384, 128)` and `stride_size=16`.
2. **Training objectives**: `model/objectives.py` implements **SDM** as a KL-style similarity-distribution matching loss, optional InfoNCE/CMPM alternatives, an auxiliary identity-classification loss, and MLM loss for masked caption-token prediction.
3. **Implicit relation reasoning path**: `model/build.py` adds a cross-attention layer plus a small cross-modal transformer over masked text features conditioned on image tokens, then predicts masked tokens with an MLM head.
4. **Data and evaluation pipeline**: the loaders support CUHK-PEDES, ICFG-PEDES, and RSTPReid; evaluation normalizes text/image embeddings and ranks gallery images by a single dot-product similarity matrix without a heavier reranking stage.
5. **Practical training recipe**: the provided `run_irra.sh` trains for 60 epochs with `sdm+mlm+id`, image augmentation enabled, and default batch size 64.

The code also clarifies lineage and reuse: the bundled tokenizer and CLIP implementation are adapted from OpenAI CLIP, the README acknowledges code borrowing from CLIP, TextReID, and TransReID, and later in-vault work such as [[source-github-qinyang79-rde]] builds on this implementation family.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and personal sensitive material before promotion.
- Result: no actionable secrets found.
- The repository includes public academic contact emails in the README and standard dependency / download URLs only; these were not promoted as canonical knowledge beyond the existence of the public code companion.

## Extracted entities
- **IRRA codebase** — public GitHub implementation companion
- **CLIP backbone** — OpenAI CLIP initialization with resized positional embeddings
- **SDM** — similarity distribution matching objective
- **MLM branch** — masked language modeling path over masked caption tokens
- **Cross-modal transformer** — training-time interaction stack after cross-attention
- **Identity classifier** — auxiliary person-ID loss head
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — supported datasets
- **Global similarity retrieval** — evaluation via normalized text-image dot products

## Typed relationships
- [[source-github-anosorae-irra]] `supports` [[irra]].
- [[source-github-anosorae-irra]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-anosorae-irra]] `related_to` [[source-arxiv-2303-12501-irra]].
- [[source-github-anosorae-irra]] `related_to` [[source-github-qinyang79-rde]].
- [[irra]] `uses` OpenAI CLIP initialization with resized positional embeddings for person retrieval.
- [[irra]] `uses` SDM, MLM, and ID losses in the public implementation.
- [[irra]] `uses` a cross-attention plus cross-modal-transformer MLM branch during training.
- [[irra]] `supports` efficient [[text-to-image-person-retrieval]] through global embedding similarity at inference.
- [[source-github-qinyang79-rde]] `depends_on` the IRRA implementation lineage.

## Evidence / claims
#### Claim
- Statement: The public IRRA code keeps inference simple by extracting one global text embedding and one global image embedding, normalizing them, and ranking with a single similarity matrix rather than explicit part-level matching or reranking.
- Status: active
- Confidence: 0.92
- Evidence: [[source-github-anosorae-irra]]
- Last confirmed: 2026-04-23
- Notes: Directly supported by `model/build.py` and `utils/metrics.py`.

#### Claim
- Statement: The repository implements IRRA's implicit relation reasoning as an MLM branch built from cross-attention over image tokens followed by a small cross-modal transformer and MLM head.
- Status: active
- Confidence: 0.90
- Evidence: [[source-github-anosorae-irra]], [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-23
- Notes: Code-level confirmation of the paper's architecture description from `model/build.py`.

#### Claim
- Statement: The default public training recipe uses CLIP `ViT-B/16`, person-retrieval image size `(384, 128)`, stride 16, 60 epochs, image augmentation, and the `sdm+mlm+id` objective stack.
- Status: active
- Confidence: 0.88
- Evidence: [[source-github-anosorae-irra]]
- Last confirmed: 2026-04-23
- Notes: Supported by `utils/options.py`, `run_irra.sh`, and the README.

#### Claim
- Statement: The IRRA repository functions as an implementation ancestor for later CLIP-based TBPS repositories in the vault, especially [[source-github-qinyang79-rde]].
- Status: active
- Confidence: 0.85
- Evidence: [[source-github-anosorae-irra]], [[source-github-qinyang79-rde]]
- Last confirmed: 2026-04-23
- Notes: Reinforced by code-structure similarity and the RDE repository's explicit acknowledgment of IRRA as a base code scaffold.

## Reinforcement / supersession assessment
- This repository strongly reinforces the paper-level account of [[irra]] as a CLIP-based dual-encoder system whose extra fine-grained reasoning machinery lives in the training path rather than the inference path.
- It adds implementation-specific detail absent from the paper summary, especially the exact default hyperparameters, the cross-attention-plus-transformer MLM realization, the dataset plumbing, and the direct normalized-similarity evaluator.
- It also reinforces IRRA's downstream historical importance by clarifying why later repositories such as [[source-github-qinyang79-rde]] could extend the same scaffold.
- No contradiction or supersession issue was introduced by the code itself; the new information is mainly concrete operational detail and implementation lineage.

## Open questions
- The code converts model weights to fp16 broadly; how sensitive are reproduction results to mixed-precision behavior on newer PyTorch/CUDA stacks?
- The repository ships a `visualize.py` helper that expects dataset fields like `gt_img_paths`; does that script reflect the current dataset classes fully or an earlier local debugging variant?
- How much of IRRA's reported gain comes from SDM versus the MLM branch under controlled ablations using this exact public recipe?

## Related pages updated
- [[source-arxiv-2303-12501-irra]]
- [[irra]]
- [[text-to-image-person-retrieval]]

## Ingest notes
- Read the full repository source tree relevant to training, evaluation, datasets, utilities, shell entrypoints, tokenizer, and CLIP backbone implementation.
- Screened the codebase for sensitive material before promotion; found public contact emails and standard model-download URLs but no actionable secrets.
- Considered Base/Canvas updates but deferred because the current TBPS method cluster remains navigable through linked markdown pages and this source mainly adds implementation detail rather than a new structural branch.
