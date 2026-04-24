---
title: Source - GitHub yinhao1102 - FMFA
created: 2026-04-25
last_updated: 2026-04-25
source_count: 1
status: reviewed
page_type: source
aliases:
  - yinhao1102/FMFA
  - FMFA code repository
  - FMFA implementation
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
  - source-arxiv-2509-13754-fmfa
  - source-arxiv-2303-12501-irra
  - source-github-anosorae-irra
confidence_score: 0.90
quality_score: 0.86
evidence_count: 1
first_seen: 2026-04-25
last_confirmed: 2026-04-25
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - FMFA
  - IRRA
  - A-SDM
  - EFA
  - CLIP
  - ViT-B/16
  - CLIP-Xformer
  - masked language modeling
  - identity loss
  - global similarity retrieval
  - NAM
  - HAM
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/codes/FMFA
source_type: code
canonical_url: https://github.com/yinhao1102/FMFA
author:
  - yinhao1102
entrypoint: raw/codes/FMFA/README.md
---

# Source - GitHub yinhao1102 - FMFA

## Source snapshot
- Repository: `yinhao1102/FMFA`
- Repository URL: [https://github.com/yinhao1102/FMFA](https://github.com/yinhao1102/FMFA)
- Raw artifacts preserved at:
  - `raw/codes/FMFA/`
- Primary entrypoints:
  - `raw/codes/FMFA/README.md`
  - `raw/codes/FMFA/run.sh`
  - `raw/codes/FMFA/finetune.sh`
  - `raw/codes/FMFA/train.py`
  - `raw/codes/FMFA/finetune.py`
  - `raw/codes/FMFA/model/build.py`
  - `raw/codes/FMFA/model/build_finetune.py`
  - `raw/codes/FMFA/model/objectives.py`
  - `raw/codes/FMFA/processor/processor.py`
  - `raw/codes/FMFA/processor/processor_finetune.py`
  - `raw/codes/FMFA/utils/options.py`
  - `raw/codes/FMFA/utils/metrics.py`
- Execution scripts:
  - `raw/codes/FMFA/run.sh`
  - `raw/codes/FMFA/finetune.sh`

## Why it matters
This repository is the public implementation companion to [[source-arxiv-2509-13754-fmfa]]. It confirms that FMFA remains an IRRA-family CLIP retrieval stack in practice: the public code keeps global-feature ranking at inference, implements A-SDM and EFA explicitly, and exposes the two training regimes discussed in the paper (without versus with ReID-domain pretraining).

## Summary
The repo implements FMFA as a modest extension of the IRRA scaffold rather than a wholesale architecture replacement:
1. **Backbone and geometry**: `utils/options.py` keeps the familiar CLIP `ViT-B/16` default, `img_size=(384, 128)`, `stride_size=16`, text length 77, and the same three benchmark datasets.
2. **A-SDM realization**: `model/objectives.py` extends SDM with optional weighting for unmatched positives by comparing the highest batch similarity against the aligned positive-pair similarity, then scaling the loss roughly as `diff * 0.1 + 1` when the best match is not the ground-truth pair.
3. **EFA realization**: `model/build_finetune.py` computes token-patch similarities, min-max normalizes them, applies a fixed sparsity threshold of `1 / num_patches`, row-normalizes the surviving weights, aggregates patch embeddings per token, and optimizes the aggregated representation with `compute_minmax_info_loss`.
4. **Inference path**: `utils/metrics.py` and the `encode_image` / `encode_text` methods confirm that evaluation still uses one normalized global image embedding and one normalized global text embedding with direct similarity ranking, not local matching at retrieval time.
5. **Public recipes**: `run.sh` trains for 60 epochs with `a-sdm+mlm+id+efa`, batch size 64, and image augmentation; `finetune.sh` keeps the same loss stack for 60 epochs but uses batch size 128 and loads a NAM/HAM-style ReID-domain checkpoint.

The inspected snapshot also exposes a practical caveat: the `train.py` / `processor/processor.py` pretraining path appears to call `model(image, text, ori_text)` and then later reference `ret.get(...)` without defining `ret`, so the no-ReID-pretraining branch may require validation before treating the repository as reproduction-ready.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and personal sensitive material before promotion.
- Result: no actionable secrets found.
- The repository does contain local/default filesystem paths (for example in `utils/options.py`, `test.py`, and `datasets/luperson.py`), placeholder checkpoint/data paths in shell scripts, and a public contact email in `utils/iotools.py`. These were not promoted as canonical knowledge beyond noting that local-path assumptions exist.

## Extracted entities
- **FMFA codebase** — public GitHub implementation companion
- **A-SDM** — weighted SDM variant that upweights unmatched positives
- **EFA** — sparse token-patch aggregation and min-max information alignment path
- **IRRA scaffold** — upstream CLIP/MLM/ID implementation family reused by FMFA
- **Global similarity evaluator** — direct normalized text-image ranking at inference
- **NAM / HAM checkpoint route** — ReID-domain pretraining path for finetuning
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — supported datasets

## Typed relationships
- [[source-github-yinhao1102-fmfa]] `supports` [[fmfa]].
- [[source-github-yinhao1102-fmfa]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-yinhao1102-fmfa]] `related_to` [[source-arxiv-2509-13754-fmfa]].
- [[source-github-yinhao1102-fmfa]] `related_to` [[source-github-anosorae-irra]].
- [[fmfa]] `extends` [[irra]] through an implementation that keeps the CLIP/MLM/ID scaffold while adding A-SDM and EFA.
- [[fmfa]] `uses` direct normalized global similarity at inference.
- [[fmfa]] `uses` A-SDM and EFA in the public implementation.
- [[fmfa]] `depends_on` NAM or HAM checkpoints for the published finetuning route.

## Evidence / claims
#### Claim
- Statement: The public FMFA code keeps inference simple by extracting one global text embedding and one global image embedding, normalizing them, and ranking with a single similarity matrix.
- Status: active
- Confidence: 0.92
- Evidence: [[source-github-yinhao1102-fmfa]]
- Last confirmed: 2026-04-25
- Notes: Directly supported by `model/build.py`, `model/build_finetune.py`, and `utils/metrics.py`.

#### Claim
- Statement: The repository operationalizes A-SDM as a weighted SDM objective that adds extra loss pressure when the highest-similarity batch match is not the aligned positive pair.
- Status: active
- Confidence: 0.89
- Evidence: [[source-github-yinhao1102-fmfa]], [[source-arxiv-2509-13754-fmfa]]
- Last confirmed: 2026-04-25
- Notes: Supported by `model/objectives.py`; the exact weighting heuristic is implementation-specific.

#### Claim
- Statement: The repository operationalizes EFA through token-patch similarity normalization, fixed-threshold sparsification, row-normalized patch aggregation, and `compute_minmax_info_loss` over the aggregated representation.
- Status: active
- Confidence: 0.89
- Evidence: [[source-github-yinhao1102-fmfa]], [[source-arxiv-2509-13754-fmfa]]
- Last confirmed: 2026-04-25
- Notes: Supported by `model/build_finetune.py` and `model/objectives.py`.

#### Claim
- Statement: The default public FMFA recipes use CLIP `ViT-B/16`, person-retrieval image size `(384, 128)`, 60 epochs, image augmentation, and the `a-sdm+mlm+id+efa` objective stack, with separate no-pretraining and checkpoint-finetuning scripts.
- Status: active
- Confidence: 0.88
- Evidence: [[source-github-yinhao1102-fmfa]]
- Last confirmed: 2026-04-25
- Notes: Supported by `README.md`, `run.sh`, `finetune.sh`, and `utils/options.py`.

## Reinforcement / supersession assessment
- This repository strongly reinforces the paper-level account of [[fmfa]] as an IRRA-family global retrieval method whose extra grounding machinery lives in training rather than inference.
- It adds implementation-specific detail absent from the paper ingest: the concrete A-SDM weighting heuristic, the fixed `1 / num_patches` EFA threshold, the public run scripts, and the continued use of the familiar `(384, 128)` CLIP recipe.
- It also strengthens the vault-level view that FMFA is a middle route between plain global retrieval and heavy local reranking: the code keeps evaluation global while making local alignment explicit only in the loss path.
- The inspected snapshot introduces one reproduction caveat: the no-ReID-pretraining branch appears to contain an unresolved implementation hazard in `processor/processor.py`, so the repository should not yet be treated as fully reproduction-verified.

## Open questions
- Does the apparent `processor/processor.py` pretraining-path hazard affect the released results, or is it only a snapshot-specific bug?
- How sensitive are FMFA results to the fixed EFA threshold of `1 / num_patches` versus an adaptive sparsity strategy?
- Are the NAM/HAM checkpoint dependencies sufficient to reproduce the paper's pretrained setting exactly, or do they require additional unpublished preprocessing assumptions?

## Related pages updated
- [[source-arxiv-2509-13754-fmfa]]
- [[fmfa]]
- [[irra]]
- [[text-to-image-person-retrieval]]

## Ingest notes
- Read the repository README, shell entrypoints, training/evaluation entrypoints, model builders, loss functions, option schema, evaluator, and selected dataset code.
- Screened the repository for sensitive material before promotion; found local-path assumptions, placeholders, and public contact metadata but no actionable secrets.
- Saved a Stage-1 audit artifact at `outputs/ingest-plans/ingest-plan-2026-04-25-fmfa-code.md` because this ingest closes a previously queued follow-up and introduces a durable reproduction caveat worth preserving.
- Considered Base/Canvas updates but deferred because the TBPS method cluster remains navigable through linked markdown pages and this source mainly adds implementation detail.
