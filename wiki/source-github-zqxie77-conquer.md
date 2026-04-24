---
title: Source - GitHub zqxie77/CONQUER
created: 2026-04-24
last_updated: 2026-04-24
source_count: 1
status: reviewed
page_type: source
aliases:
  - CONQUER GitHub
  - zqxie77/CONQUER
  - CONQUER code
  - CONQUER public implementation
tags:
  - source
  - code
  - github
  - multimodal
  - retrieval
  - person-retrieval
  - query-refinement
  - optimal-transport
domain: machine-learning
importance: high
review_status: active
related_sources:
  - source-arxiv-2601-18625-conquer
confidence_score: 0.88
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-24
last_confirmed: 2026-04-24
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - CONQUER
  - CARE
  - IQE
  - RDE
  - CLIP
  - Qwen2.5-VL-7B
  - text-to-image person retrieval
  - noisy correspondence
  - Optimal Transport
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/codes/CONQUER
source_type: code
canonical_url: https://github.com/zqxie77/CONQUER
author:
  - Zequn Xie
published: 2025-09-20
---

# Source - GitHub zqxie77/CONQUER

## Source snapshot
- Repository: [https://github.com/zqxie77/CONQUER](https://github.com/zqxie77/CONQUER)
- Local raw source: `raw/codes/CONQUER/`
- Companion paper page: [[source-arxiv-2601-18625-conquer]]
- README states the code and pretrained models were released on 2025-09-20 and that the paper was accepted by ICASSP 2026.
- Main entry points: `train.py`, `test.py`, `IQE.py`, `run_CONQUER.sh`, `run_IQE.sh`.

## Why it matters
This source is the public implementation companion for [[conquer]]. It reinforces the paper's two-stage design while making several implementation choices explicit: the training model is a CLIP-derived dual-encoder with additional token/patch-selected embeddings, the training loop borrows heavily from the RDE/noisy-correspondence family, and the inference-time IQE module is implemented as a separate MLLM-assisted reranking script rather than as part of the retrieval backbone.

## Sensitive material screen
- Screened for secrets, credentials, tokens, passwords, private keys, actionable PII, and non-public operational data before promotion.
- Result: no actionable secrets found.
- Downstream notes omit developer-local filesystem paths from `test.py` and avoid copying machine-specific script details that are not durable knowledge.
- `token` hits are tokenizer/model variables, not credentials.

## Extracted entities
- **CONQUER** — public implementation of the CARE + IQE TBPS method.
- **CARE / RDE class** — implemented in `model/build.py` as an `RDE` class despite the repository branding; wraps CLIP and adds visual/textual selected-embedding branches.
- **TexualEmbeddingLayer / VisualEmbeddingLayer** — attention-guided top-k token/patch selection modules in `model/tokenselection.py`.
- **IQE** — implemented in `IQE.py` as a separate inference-time loop over anchor selection, MLLM visual Q&A, query aggregation, and score interpolation.
- **Qwen2.5-VL-7B / vLLM** — MLLM stack used by IQE.
- **Noisy-correspondence filtering** — training loop uses per-sample losses, GMM clean-pair estimation, consensus labels, and rematching for noisy pairs.
- **Optimal Transport rematching** — implemented through POT Sinkhorn transport over noisy-pair similarities inside `processor/processor.py`.
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — dataset loaders and run scripts cover the three standard TBPS benchmarks.

## Typed relationships
- [[source-github-zqxie77-conquer]] `supports` [[conquer]].
- [[source-github-zqxie77-conquer]] `supports` [[source-arxiv-2601-18625-conquer]].
- [[conquer]] `uses` CLIP-derived image and text encoders.
- [[conquer]] `uses` attention-guided token and patch selection.
- [[conquer]] `uses` per-sample loss modeling and GMM-based clean-pair filtering.
- [[conquer]] `uses` Optimal Transport rematching for likely noisy samples.
- [[conquer]] `uses` Qwen2.5-VL-7B through vLLM for IQE.
- [[conquer]] `related_to` [[rde]] because the implementation keeps the `RDE` model class name and reuses the noisy-correspondence training pattern.
- [[source-github-zqxie77-conquer]] `supports` [[text-to-image-person-retrieval]].

## Candidate claims from the source
#### Claim
- Statement: The released CONQUER training code implements the CARE-side representation stack as a CLIP-derived dual encoder with both global BGE embeddings and selected token/patch TSE embeddings.
- Status: active
- Confidence: 0.88
- Evidence: [[source-github-zqxie77-conquer]], [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-24
- Notes: `model/build.py` exposes `encode_image`, `encode_text`, `encode_image_tse`, and `encode_text_tse`; `IQE.py` averages BGE and TSE similarities for CONQUER inference.

#### Claim
- Statement: The released CONQUER code operationalizes noisy-correspondence robustness with GMM-based clean-pair estimation, consensus labels from two loss branches, context/contrastive regularization, and Optimal Transport rematching for likely noisy pairs.
- Status: active
- Confidence: 0.86
- Evidence: [[source-github-zqxie77-conquer]]
- Last confirmed: 2026-04-24
- Notes: This is stronger implementation-level evidence than the README but should be kept distinct from paper-level novelty claims because several mechanics resemble the RDE family.

#### Claim
- Statement: IQE is implemented as an external inference script that first uses base retrieval to choose anchors, then asks an MLLM yes/no and attribute questions, aggregates new captions, re-embeds them, and interpolates refined similarities with original similarities.
- Status: active
- Confidence: 0.90
- Evidence: [[source-github-zqxie77-conquer]], [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-24
- Notes: `IQE.py` provides direct code support for the paper's plug-and-play query-enhancement claim.

#### Claim
- Statement: The public repository is best treated as a reproduction-oriented research codebase rather than a clean reusable library.
- Status: active
- Confidence: 0.78
- Evidence: [[source-github-zqxie77-conquer]]
- Last confirmed: 2026-04-24
- Notes: Evidence includes hard-coded/default paths, global variables in `IQE.py`, scripts with dataset-specific presets, and a model class named `RDE`; this is a practical reproducibility caveat, not a critique of the method.

## Reinforcement / change / supersession assessment
- **Reinforces [[source-arxiv-2601-18625-conquer]]:** the code supports the paper's main two-stage story: CARE-style training followed by IQE query enhancement.
- **Sharpens [[conquer]]:** the implementation shows that the training scaffold is close to the CLIP/RDE noisy-correspondence line, while the distinctive CONQUER contribution is clearer in the IQE script and selected-embedding/query-enhancement integration.
- **Reinforces [[text-to-image-person-retrieval]]:** adds another code-level example of the field's recurring pattern: CLIP-style dual encoders remain central, but methods add robustness, selected local evidence, or inference-time adaptation around them.
- **No benchmark supersession:** this source is an implementation companion, not a newer result source. It should not replace the paper's benchmark claims or the later Bi-IRRA/MVR benchmark comparison already represented in the wiki.
- **No material contradiction:** the only tension is nomenclature/lineage: the code uses an `RDE` class name and RDE-like mechanisms under the CONQUER release. This is recorded as an implementation lineage/caveat rather than a contradiction.

## Related pages updated
- [[conquer]]
- [[source-arxiv-2601-18625-conquer]]
- [[text-to-image-person-retrieval]]
- [[index]]

## Ingest notes
- Read the README and inspected the Python/shell source tree under `raw/codes/CONQUER/`, including model, objective, token-selection, processor/training, IQE, dataset, metric, option, and run-script files.
- The compressed BPE vocabulary file is preserved in raw but not promoted as semantic knowledge.
- Considered Base/Canvas updates; deferred because this adds another source node to an already navigable TBPS method graph rather than changing the graph structure.
