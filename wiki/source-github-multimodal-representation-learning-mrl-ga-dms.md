---
title: Source - GitHub Multimodal-Representation-Learning-MRL - GA-DMS
created: 2026-04-24
last_updated: 2026-04-24
source_count: 1
status: reviewed
page_type: source
aliases:
  - Multimodal-Representation-Learning-MRL/GA-DMS
  - GA-DMS code repository
  - GA-DMS implementation
  - WebPerson code companion
tags:
  - source
  - code
  - github
  - multimodal
  - retrieval
  - clip
  - robustness
  - dataset
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2509-09118-ga-dms
  - source-arxiv-2303-12501-irra
confidence_score: 0.90
quality_score: 0.86
evidence_count: 1
first_seen: 2026-04-24
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - GA-DMS
  - WebPerson
  - GASS
  - CLIP
  - IRRA
  - SDM
  - MLM
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/codes/GA-DMS
source_type: code
canonical_url: https://github.com/Multimodal-Representation-Learning-MRL/GA-DMS
author:
  - Tianlu Zheng
  - Yifan Zhang
  - Xiang An
  - Ziyong Feng
  - Kaicheng Yang
  - Qichuan Ding
entrypoint: raw/codes/GA-DMS/README.md
---

# Source - GitHub Multimodal-Representation-Learning-MRL - GA-DMS

## Source snapshot
- Repository: `Multimodal-Representation-Learning-MRL/GA-DMS`
- Repository URL: [https://github.com/Multimodal-Representation-Learning-MRL/GA-DMS](https://github.com/Multimodal-Representation-Learning-MRL/GA-DMS)
- Raw artifacts preserved at: `raw/codes/GA-DMS/`
- Primary entrypoints: `README.md`, `train.py`, `finetune.py`, `model/build.py`, `model/build_finetune.py`, `datasets/bases.py`, `datasets/build.py`, `processor/processor.py`, `processor/processor_finetune.py`
- Launch scripts: `run_ddp.sh`, `finetune.sh`
- License: repository contains `LICENSE`; implementation acknowledges [[irra]] and MLLM4Text-ReID as code bases.

## Why it matters
This repository is the public implementation companion to [[source-arxiv-2509-09118-ga-dms]]. It turns the paper's token-level robustness story into an IRRA-derived CLIP training scaffold: pretraining first computes gradient-attention token-importance maps, stores those maps on training samples, then rebuilds the dataloader so text tokens can be masked differently for the noisy-text path and the informative-token reconstruction path.

## Summary
The codebase implements [[ga-dms]] as a CLIP/IRRA-style dual-encoder training stack with three implementation-level details worth preserving:
1. **Gradient-attention map generation**: `model/build.py` extracts Q/K/V and attention outputs from the last text-transformer layers, computes image-text similarity, and backpropagates through attention outputs to create a token-level importance map.
2. **Two masking paths**: `datasets/bases.py` has a standard random MLM dataset plus `FilterDataset`, which uses the stored similarity/importance vector to produce `noise_text` and `mlm_ids` with different sigmoid thresholds.
3. **Two-stage training loop**: `processor/processor.py` first trains/evaluates a pretraining loop, then after early epochs creates a filtered dataset with the current `grad_emap` values through `build_filter_loader`.

The README also confirms the public-facing artifacts: WebPerson 1M/5M dataset download, pretrained checkpoints, EMNLP 2025 acceptance, and downstream dataset preparation for CUHK-PEDES, ICFG-PEDES, and RSTPReid.

## Sensitive material screen
- Screened the code repository for secrets, credentials, tokens, passwords, API keys, and sensitive non-public data before promotion.
- Result: no actionable secret found.
- Downstream notes intentionally avoid copying public author profile links, a Baidu checkpoint extraction key, local storage paths such as `/mnt/data`, generated `__pycache__` artifacts, and raw code comments that do not add canonical knowledge.

## Extracted entities
- **GA-DMS codebase** — public implementation companion for [[ga-dms]].
- **IRRA2** — main model class in `model/build.py`, extending a CLIP/IRRA scaffold with gradient-attention mapping and MLM heads.
- **Gradient-attention map / GASS-like importance map** — token relevance signal computed by gradients through text attention and Q/K similarity.
- **FilterDataset** — dataset wrapper that applies similarity-guided token masking after the first stage has produced per-sample maps.
- **ImageTextMLMDataset** — standard BERT-style random token masking dataset used before similarity-guided filtering.
- **SDM / SDM-DDP** — similarity distribution matching loss implemented for single-process and distributed training.
- **WebPerson** — pretraining dataset target exposed by the README and dataset factory.
- **CUHK-PEDES, ICFG-PEDES, RSTPReid** — downstream evaluation datasets in the zero-shot and fine-tune loaders.

## Typed relationships
- [[source-github-multimodal-representation-learning-mrl-ga-dms]] `supports` [[ga-dms]].
- [[source-github-multimodal-representation-learning-mrl-ga-dms]] `supports` [[webperson]].
- [[source-github-multimodal-representation-learning-mrl-ga-dms]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-multimodal-representation-learning-mrl-ga-dms]] `related_to` [[source-arxiv-2509-09118-ga-dms]].
- [[source-github-multimodal-representation-learning-mrl-ga-dms]] `related_to` [[source-arxiv-2303-12501-irra]].
- [[ga-dms]] `depends_on` a CLIP/IRRA-style training scaffold in this implementation.
- [[ga-dms]] `uses` gradient-through-attention token maps to guide later masking.
- [[ga-dms]] `uses` SDM plus MLM losses in the public pretraining script.
- [[webperson]] `supports` GA-DMS pretraining through the dataset factory and README workflow.

## Evidence / claims
#### Claim
- Statement: The public GA-DMS code operationalizes token relevance by extracting text-transformer attention internals, computing image-text similarity, and backpropagating gradients through attention outputs to build per-token importance maps.
- Status: active
- Confidence: 0.88
- Evidence: [[source-github-multimodal-representation-learning-mrl-ga-dms]], [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-24
- Notes: Directly supported by `IRRA2.clip_encode_text_dense`, `grad_eclip_enhanced_batched`, and the forward pass in `model/build.py`.

#### Claim
- Statement: The implementation realizes dual masking by using similarity-guided probabilities to create both a noise-masked text input and an MLM reconstruction input after initial map generation.
- Status: active
- Confidence: 0.87
- Evidence: [[source-github-multimodal-representation-learning-mrl-ga-dms]]
- Last confirmed: 2026-04-24
- Notes: `FilterDataset` computes `mlm_ids` from `sim` and `noise_text` from `1 - sim` with different sigmoid thresholds.

#### Claim
- Statement: The repository is closer to an IRRA-style CLIP training scaffold than a standalone new retrieval stack.
- Status: active
- Confidence: 0.86
- Evidence: [[source-github-multimodal-representation-learning-mrl-ga-dms]], [[source-arxiv-2303-12501-irra]]
- Last confirmed: 2026-04-24
- Notes: README acknowledgements, class naming, SDM/MLM machinery, and CLIP model structure all reinforce the implementation lineage.

#### Claim
- Statement: The README publicly confirms WebPerson as both 1M and 5M downloadable scales and links released pretrained model checkpoints.
- Status: active
- Confidence: 0.84
- Evidence: [[source-github-multimodal-representation-learning-mrl-ga-dms]], [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-24
- Notes: Keep as a code-repository availability claim, not a guarantee about future hosting reliability.

## Reinforcement / supersession assessment
- Reinforces [[source-arxiv-2509-09118-ga-dms]] on the core architecture: gradient/attention token scoring, noisy-token masking, informative-token reconstruction, and CLIP/IRRA lineage.
- Adds implementation specificity not present in the paper source page: staged map generation, `FilterDataset` masking thresholds, DDP SDM implementation, and concrete training scripts.
- Does not supersede benchmark claims. Later benchmark supersession in the vault remains governed by [[bi-irra]] and [[mvr]] evidence, not this code companion.
- No contradictions found requiring disputed status. Minor caveat: variable names such as `IRRA2` and `nose_tokens` reveal inherited/prototype code style but do not alter the method claim.

## Pages updated because of this source
- [[ga-dms]]
- [[webperson]]
- [[text-to-image-person-retrieval]]
- [[source-arxiv-2509-09118-ga-dms]]
- [[index]]

## Quality self-check
- Source read: README and code entrypoints examined, with repository-wide textual scan and secret scan.
- Privacy: no actionable secret promoted; public links and checkpoint key not copied as durable operational detail.
- Citations: claims cite this source page and paper/source pages where needed.
- Links: backlinks added to affected canonical pages.
- Visual artifacts: Base/Canvas update considered and deferred; the TBPS method graph remains navigable through linked markdown pages.
