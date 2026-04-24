---
title: Source - GitHub Flame-Chasers - Bi-IRRA
created: 2026-04-24
last_updated: 2026-04-24
source_count: 1
status: reviewed
page_type: source
aliases:
  - Flame-Chasers/Bi-IRRA
  - Bi-IRRA code repository
  - Bi-IRRA implementation
tags:
  - source
  - code
  - github
  - multimodal
  - retrieval
  - multilingual
  - person-retrieval
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2510-17685-bi-irra
  - source-arxiv-2303-12501-irra
  - source-github-flame-chasers-tbps-clip
confidence_score: 0.89
quality_score: 0.88
evidence_count: 1
first_seen: 2026-04-24
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Bi-IRRA
  - text-to-image person retrieval
  - multilingual TIPR
  - X2-VLM
  - CCLM-X2VLM
  - XLM-RoBERTa
  - BEiT v2
  - TBPS-CLIP
  - bi-lingual ITC
  - bi-lingual A-ITM
  - bi-lingual MLM
  - cross-lingual D-MIM
  - masked image modeling
  - cross-encoder reranking
  - CUHK-PEDES(M)
  - ICFG-PEDES(M)
  - RSTPReid(M)
  - UFineBench(M)
source_file: raw/codes/Bi-IRRA
source_type: code
canonical_url: https://github.com/Flame-Chasers/Bi-IRRA
author:
  - Flame-Chasers
entrypoint: raw/codes/Bi-IRRA/README.md
---

# Source - GitHub Flame-Chasers - Bi-IRRA

## Source snapshot
- Repository: `Flame-Chasers/Bi-IRRA`
- Repository URL: [https://github.com/Flame-Chasers/Bi-IRRA](https://github.com/Flame-Chasers/Bi-IRRA)
- Raw artifacts preserved at: `raw/codes/Bi-IRRA/`
- Primary entrypoints:
  - `raw/codes/Bi-IRRA/README.md`
  - `raw/codes/Bi-IRRA/main.py`
  - `raw/codes/Bi-IRRA/models/model_retrieval.py`
  - `raw/codes/Bi-IRRA/models/xvlm.py`
  - `raw/codes/Bi-IRRA/misc/caption_dataset.py`
  - `raw/codes/Bi-IRRA/misc/eval.py`
- Execution script: `raw/codes/Bi-IRRA/shell/train.sh`
- Configs:
  - `raw/codes/Bi-IRRA/config/config.yaml` for CUHK-PEDES, ICFG-PEDES, and RSTPReid-style runs.
  - `raw/codes/Bi-IRRA/config/config_UFine.yaml` for UFineBench-style longer-text runs.

## Why it matters
This repository is the public implementation companion to [[source-arxiv-2510-17685-bi-irra]]. It makes [[bi-irra]] concrete as an X2-VLM/CCLM-style multilingual retrieval system rather than just a paper architecture: the code shows how source-language and target-language captions are loaded as paired supervision, how bi-lingual ITC/ITM and MLM losses are computed, how cross-lingual D-MIM is represented as distillation between unmasked-source and masked-target fusion features, and how inference uses top-k cross-encoder ITM reranking after global similarity retrieval.

## Summary
The implementation has five important pieces:
1. **Dataset pairing**: `ps_train_dataset` loads `train_reid_{source_language}.json` and `train_reid_{target_language}.json` in parallel, expecting aligned annotation order and pairing each image with source/target captions.
2. **Backbone stack**: `Bi_IRRA` extends `XVLMBase`; the default configs use BEiT v2 vision settings, XLM-RoBERTa text encoding, and CCLM-X2VLM or LUPerson-pretrained checkpoints.
3. **Training objectives**: `models/model_retrieval.py` averages source-language and target-language image-text contrastive losses, averages source/target matching losses with an ITM weight of `4.0`, adds bi-lingual MLM when enabled, and adds cross-lingual D-MIM with weight `4.0` when masked image modeling is enabled.
4. **Multilingual configs**: the standard config uses text length `77`, batch size `32`, source language `en`, target language `ch`, image resolution `224`, text mask probability `0.4`, image mask ratio `0.5`, and 10 training epochs; the UFine config raises text length to `168` and lowers batch size to `16`.
5. **Evaluation path**: `misc/eval.py` first computes text/image embeddings and a similarity matrix, then reranks each text query's top `k_test=256` images through the cross encoder and ITM head before computing Rank-1/5/10 and mAP.

## Sensitive material screen
- Screened for secrets, credentials, private keys, tokens, PII, private operational data, and local filesystem paths before promotion.
- Result: no actionable secret or sensitive personal material found.
- Downstream notes omit IDE metadata and placeholder local paths such as `/path/to/...`; those placeholders are not sensitive but are not useful durable knowledge.

## Extracted entities
- **Bi-IRRA codebase** — public PyTorch implementation of the multilingual TIPR method.
- **Bi_IRRA model class** — `XVLMBase` subclass implementing multilingual retrieval losses.
- **X2-VLM / CCLM-X2VLM** — inherited vision-language pretraining stack and checkpoint lineage.
- **XLM-RoBERTa tokenizer/encoder** — multilingual text component used throughout data preprocessing, training, and evaluation.
- **BEiT v2 vision encoder** — default vision backbone selected by config.
- **Source/target caption pair loader** — dataset contract requiring aligned multilingual annotation JSON files.
- **Cross-lingual D-MIM** — code-level masked-image distillation loss between source-text unmasked-image fusion and target-text masked-image fusion.
- **Bi-lingual MLM** — source and target masked-token reconstruction with shared multimodal interaction.
- **Bi-lingual ITC/ITM** — source and target global contrastive/matching objectives.
- **Top-k cross-encoder reranking** — inference stage that reranks globally retrieved candidates with the ITM head.

## Typed relationships
- [[source-github-flame-chasers-bi-irra]] `supports` [[bi-irra]].
- [[source-github-flame-chasers-bi-irra]] `supports` [[source-arxiv-2510-17685-bi-irra]].
- [[source-github-flame-chasers-bi-irra]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-flame-chasers-bi-irra]] `related_to` [[source-github-flame-chasers-tbps-clip]] because the README says the repository is partially based on TBPS-CLIP.
- [[bi-irra]] `depends_on` aligned source/target multilingual annotation JSON files in the public training loader.
- [[bi-irra]] `uses` X2-VLM/CCLM-style pretraining through `XVLMBase`.
- [[bi-irra]] `uses` XLM-RoBERTa for multilingual tokenization and text encoding.
- [[bi-irra]] `uses` BEiT v2 as the default vision encoder in the shipped configs.
- [[bi-irra]] `uses` top-k cross-encoder ITM reranking at evaluation time.
- [[bi-irra]] `related_to` [[tbps-clip]] through inherited augmentation and codebase acknowledgement.

## Evidence / claims
#### Claim
- Statement: The public Bi-IRRA implementation realizes the paper's multilingual supervision by loading aligned source-language and target-language caption JSON files and training on paired `(image, source text, target text)` triples.
- Status: active
- Confidence: 0.90
- Evidence: [[source-github-flame-chasers-bi-irra]]
- Last confirmed: 2026-04-24
- Notes: Directly supported by `misc/caption_dataset.py` and the `source_language` / `target_language` config fields.

#### Claim
- Statement: The released code implements Bi-IRRA as an X2-VLM/CCLM-derived stack using XLM-RoBERTa text encoding, default BEiT v2 vision encoding, and configurable CCLM-X2VLM or LUPerson-pretrained checkpoint initialization.
- Status: active
- Confidence: 0.88
- Evidence: [[source-github-flame-chasers-bi-irra]], [[source-arxiv-2510-17685-bi-irra]]
- Last confirmed: 2026-04-24
- Notes: Supported by README checkpoint instructions, configs, and `models/xvlm.py`.

#### Claim
- Statement: In this implementation, Bi-IRRA inference is not pure global-similarity retrieval; it computes global similarities first and then reranks each text query's top candidates with a cross-encoder ITM head.
- Status: active
- Confidence: 0.89
- Evidence: [[source-github-flame-chasers-bi-irra]]
- Last confirmed: 2026-04-24
- Notes: `misc/eval.py` builds `sims_matrix`, selects `topk_idx`, calls `get_cross_embeds`, and fills `score_matrix_t2i` with ITM-head scores.

#### Claim
- Statement: The inspected snapshot appears to require distributed `torchrun` execution for the main path, because `misc/utils.py` hardcodes `is_using_distributed()` to `True` and `main.py` evaluates through `model.module`.
- Status: active
- Confidence: 0.82
- Evidence: [[source-github-flame-chasers-bi-irra]]
- Last confirmed: 2026-04-24
- Notes: Practical reproduction caveat; consistent with the README and `shell/train.sh` using four-process `torchrun`.

#### Claim
- Statement: The inspected raw snapshot references `config/config_beit2_base.json`, but that file is not present under `raw/codes/Bi-IRRA/config/`.
- Status: active
- Confidence: 0.86
- Evidence: [[source-github-flame-chasers-bi-irra]]
- Last confirmed: 2026-04-24
- Notes: Reproduction caveat specific to the captured raw folder, not necessarily a claim about the live upstream repository.

## Reinforcement / supersession assessment
- This code source reinforces [[source-arxiv-2510-17685-bi-irra]] on the main architecture and training setup: paired multilingual data, bi-lingual MLM, cross-lingual D-MIM, bi-lingual ITC, and bi-lingual ITM are all visible in the implementation.
- It changes the operational understanding of [[bi-irra]] by making the inference path more explicit: the code performs global retrieval followed by top-k cross-encoder ITM reranking.
- It reinforces the paper's statement that the project is connected to [[tbps-clip]], but the code route is closer to X2-VLM/CCLM than to the lightweight CLIP-only TBPS-CLIP recipe.
- No benchmark contradiction was found. The source is implementation evidence, not a new results source.

## Open questions
- Is the missing `config/config_beit2_base.json` expected to come from an upstream checkpoint/config download, or is it absent from this captured raw snapshot?
- Does the live upstream repository include additional scripts for annotation download or evaluation-only runs that are not present in this raw folder?
- How expensive is the top-k cross-encoder reranking stage compared with the IRRA-family direct global-similarity path?

## Related pages updated
- [[bi-irra]]
- [[source-arxiv-2510-17685-bi-irra]]
- [[text-to-image-person-retrieval]]
- [[tbps-clip]]

## Ingest notes
- Read the README, configs, training entrypoint, data loader, evaluation path, retrieval model, X2-VLM support code, and model utility files; inspected larger inherited model files by structure and symbol outline.
- Screened the codebase before promotion; no actionable sensitive material found.
- Considered Base/Canvas updates but deferred because the TBPS method graph remains navigable through linked markdown pages without a new visual overlay.
