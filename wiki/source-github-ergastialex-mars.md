---
title: Source - GitHub ErgastiAlex - MARS
created: 2026-04-23
last_updated: 2026-04-23
source_count: 1
status: reviewed
page_type: source
aliases:
  - ErgastiAlex/MARS
  - MARS code repository
  - MARS implementation
tags:
  - source
  - code
  - github
  - multimodal
  - retrieval
  - attribute-learning
  - masked-autoencoder
  - person-retrieval
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2407-04287-mars
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
  - MARS
  - ALBEF
  - RaSa
  - full cross-attention
  - attribute loss
  - visual reconstruction loss
  - Positive Relation Detection
  - Momentum-based Replaced Token Detection
  - spaCy
  - Grad-CAM
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
source_file: raw/codes/MARS
source_type: code
canonical_url: https://github.com/ErgastiAlex/MARS
author:
  - ErgastiAlex
entrypoint: raw/codes/MARS/README.md
---

# Source - GitHub ErgastiAlex - MARS

## Source snapshot
- Repository: `ErgastiAlex/MARS`
- Repository URL: [https://github.com/ErgastiAlex/MARS](https://github.com/ErgastiAlex/MARS)
- Raw artifacts preserved at:
  - `raw/codes/MARS/`
- Primary entrypoints:
  - `raw/codes/MARS/README.md`
  - `raw/codes/MARS/Retrieval.py`
  - `raw/codes/MARS/models/model_person_search.py`
  - `raw/codes/MARS/models/xbert.py`
  - `raw/codes/MARS/dataset/ps_dataset.py`
  - `raw/codes/MARS/generate_cross_map.py`
- Execution scripts:
  - `raw/codes/MARS/shell/cuhk-train.sh`
  - `raw/codes/MARS/shell/icfg-train.sh`
  - `raw/codes/MARS/shell/rstp-train.sh`
  - `raw/codes/MARS/shell/cuhk-eval.sh`
  - `raw/codes/MARS/shell/icfg-eval.sh`
  - `raw/codes/MARS/shell/rstp-eval.sh`

## Why it matters
This repository is the public implementation companion to [[source-arxiv-2407-04287-mars]]. It confirms that MARS is not just a paper-level idea about attributes and reconstruction: the code realizes it as an ALBEF-style retrieval stack with a seven-loss training objective, spaCy-driven attribute-chunk masking, masked-image reconstruction through a cross-transformer decoder, and full-cross-attention reranking during evaluation.

## Summary
The repo implements MARS as a RaSa/ALBEF-family training system with several concrete code-level choices:
1. **Seven-loss training stack**: `Retrieval.py` and `models/model_person_search.py` jointly optimize contrastive alignment, probabilistic image-text matching, masked language modeling, positive relation detection, momentum-based replaced token detection, masked autoencoding, and attribute loss.
2. **Attribute supervision in code**: `Retrieval.py` builds `attribute_masks` from spaCy noun chunks, keeping adjective+noun groups only when at least one adjective and one noun are present, then `model_person_search.py` averages token embeddings per chunk and applies ITM-style supervision to both positive and sampled negative pairs.
3. **Masked reconstruction path**: `model_person_search.py` reuses the ViT encoder for patch embeddings, applies random masking with `mask_ratio=0.75`, restores masked positions with a learned mask token plus positional embeddings, and decodes with `models/cross_transformer.py` conditioned on text features before patch-level reconstruction loss.
4. **Full cross-attention reranking**: `configs/config_bert-fullca.json` sets `full_ca: true`, and the patched `models/xbert.py` enables cross-attention in every BERT layer rather than only after `fusion_layer=6`; evaluation still starts with dual-encoder retrieval, then reranks top-`k_test=128` candidates with the multimodal ITM head.
5. **Shared practical recipe across datasets**: all three dataset YAMLs use `image_res: 384`, batch size 8 for training, 30 epochs, AdamW with `lr: 1e-5`, queue size 65536, and loss weights `[0.5, 1, 1, 0.5, 0.5, 1, 2]`, while the shell scripts expose dataset-specific launch commands and pretrained-checkpoint placeholders.
6. **Qualitative analysis helper**: `generate_cross_map.py` uses saved cross-attention maps and gradients to produce Grad-CAM-style visualizations comparing a baseline config against the full MARS model.

The code also clarifies lineage and caveats. It inherits large parts of tokenizer/BERT/optimizer/scheduler infrastructure from upstream libraries, depends on `bert-base-uncased`, timm, and spaCy, and several shell or visualization scripts contain developer-local CUDA-device choices, checkpoint paths, or dataset paths that should be treated as repository-local execution assumptions rather than canonical method facts.

## Sensitive material screen
- Screened for secrets, credentials, tokens, and personal sensitive material before promotion.
- Result: no actionable secrets found.
- The repository contains public model URLs, public benchmark/model-share links, and developer-local filesystem or GPU-device settings in scripts. Those local path details were not promoted as canonical knowledge beyond noting that the public scripts assume local environment setup.

## Extracted entities
- **MARS codebase** — public GitHub implementation companion
- **ALBEF/RaSa scaffold** — retrieval backbone family extended by the repository
- **Attribute masks** — spaCy-derived adjective-noun chunk labels used for chunk-level supervision
- **Visual decoder** — cross-transformer decoder for text-conditioned masked patch reconstruction
- **Full cross-attention BERT** — patched multimodal encoder with `full_ca: true`
- **Positive Relation Detection (PRD)** — auxiliary head trained on weakly augmented positive captions
- **Momentum-based Replaced Token Detection (MRTD)** — token corruption detection branch
- **Probabilistic ITM** — positive/negative image-text matching branch with sampled negatives
- **CUHK-PEDES / ICFG-PEDES / RSTPReid** — supported datasets
- **Grad-CAM cross-map generator** — qualitative analysis utility

## Typed relationships
- [[source-github-ergastialex-mars]] `supports` [[mars]].
- [[source-github-ergastialex-mars]] `supports` [[text-to-image-person-retrieval]].
- [[source-github-ergastialex-mars]] `related_to` [[source-arxiv-2407-04287-mars]].
- [[source-github-ergastialex-mars]] `related_to` [[irra]].
- [[mars]] `uses` a seven-loss ALBEF-style training stack in the public implementation.
- [[mars]] `uses` spaCy-derived adjective-noun chunk masks for attribute supervision.
- [[mars]] `uses` full cross-attention across all multimodal BERT layers in the public implementation.
- [[mars]] `uses` top-k reranking with the multimodal ITM head after dual-encoder retrieval.
- [[mars]] `related_to` [[irra]] through shared ALBEF-style multimodal retrieval scaffolding.

## Evidence / claims
#### Claim
- Statement: The public MARS implementation optimizes seven losses together: contrastive alignment, PITM, MLM, PRD, MRTD, masked autoencoding, and attribute loss.
- Status: active
- Confidence: 0.92
- Evidence: [[source-github-ergastialex-mars]]
- Last confirmed: 2026-04-23
- Notes: Directly supported by `Retrieval.py` and `models/model_person_search.py`.

#### Claim
- Statement: The code operationalizes attribute supervision by extracting adjective-noun chunks with spaCy and supervising averaged chunk embeddings with the same ITM head used for positive and negative image-text matching.
- Status: active
- Confidence: 0.90
- Evidence: [[source-github-ergastialex-mars]], [[source-arxiv-2407-04287-mars]]
- Last confirmed: 2026-04-23
- Notes: Supported by `Retrieval.py`, `generate_cross_map.py`, and `models/model_person_search.py`.

#### Claim
- Statement: The public repository implements MARS's stronger reranking by enabling full cross-attention across all BERT layers and reranking the top 128 gallery candidates with the ITM head after an embedding-similarity retrieval pass.
- Status: active
- Confidence: 0.89
- Evidence: [[source-github-ergastialex-mars]], [[source-arxiv-2407-04287-mars]]
- Last confirmed: 2026-04-23
- Notes: Supported by `configs/config_bert-fullca.json`, `models/xbert.py`, and `Retrieval.py`.

#### Claim
- Statement: The shared public training recipe uses square `384x384` image resizing, 30 epochs, batch size 8, AdamW at `1e-5`, and the same loss-weight vector across CUHK-PEDES, ICFG-PEDES, and RSTPReid.
- Status: active
- Confidence: 0.87
- Evidence: [[source-github-ergastialex-mars]]
- Last confirmed: 2026-04-23
- Notes: Directly supported by the three dataset YAMLs and shell scripts; this is a repository-level implementation fact, not a broader field claim.

## Reinforcement / supersession assessment
- This repository strongly reinforces the paper-level account of [[mars]] as an attribute-aware plus reconstruction-aware TBPS method.
- It adds implementation detail absent from the paper summary, especially the exact seven-loss stack, the concrete spaCy chunk-to-loss path, the top-128 reranking routine, and the `full_ca` encoder patch.
- It also sharpens MARS's position relative to [[irra]]: the code shows that MARS keeps an ALBEF/IRRA-adjacent retrieval scaffold while adding heavier auxiliary objectives and a stronger multimodal reranking path.
- No benchmark contradiction or supersession issue was introduced by the code itself; the new information mainly reinforces and operationalizes the paper's claims.

## Open questions
- The config resizes person images to square `384x384`; how much of MARS's public-repo behavior depends on this geometry versus a more typical tall person-retrieval aspect ratio?
- `generate_cross_map.py` and some shell scripts rely on hardcoded local paths and device IDs; how closely do these scripts reflect the exact environment used for the reported qualitative figures?
- The repo vendors large modified `xbert.py` and tokenizer code; which parts are strictly necessary for MARS versus inherited from ALBEF-style scaffolding?

## Related pages updated
- [[source-arxiv-2407-04287-mars]]
- [[mars]]
- [[text-to-image-person-retrieval]]

## Ingest notes
- Read the full repository tree relevant to README, configs, dataset processing, dataset loaders, training/evaluation entrypoints, model definitions, shell scripts, and the large modified BERT/tokenizer support files.
- Screened the codebase for sensitive material before promotion; found no actionable secrets.
- Considered Base/Canvas updates but deferred because this source adds implementation detail to an already navigable TBPS method cluster rather than introducing a new structural branch.
