---
title: Text-to-Image Person Retrieval
created: 2026-04-23
last_updated: 2026-04-23
source_count: 7
status: draft
page_type: topic
aliases:
  - text image person retrieval
  - person text retrieval
  - text-based person search
tags:
  - machine-learning
  - multimodal
  - retrieval
  - computer-vision
domain: machine-learning
importance: medium
review_status: active
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-arxiv-2308-10045-tbps-clip
  - source-arxiv-2407-04287-mars
  - source-arxiv-2507-10195-mra
  - source-arxiv-2509-09118-ga-dms
  - source-arxiv-2601-18625-conquer
confidence_score: 0.84
quality_score: 0.87
evidence_count: 7
first_seen: 2026-04-23
last_confirmed: 2026-04-23
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - IRRA
  - RDE
  - MARS
  - MRA
  - GA-DMS
  - CONQUER
  - CARE
  - IQE
  - WebPerson
  - TBPS-CLIP
  - DaD
  - SDA
  - noisy correspondence
  - GASS
  - CLIP
  - augmentation pool
  - attribute loss
  - masked autoencoder
  - visual reconstruction loss
  - Optimal Transport
  - N-ITC
  - R-ITC
  - C-ITC
  - few-shot learning
  - model compression
  - CUHK-PEDES
  - ICFG-PEDES
  - RSTPReid
---

# Text-to-Image Person Retrieval

Text-to-image person retrieval is a multimodal retrieval task where a system receives a natural-language description of a person and must retrieve matching images from a gallery. The main challenge is aligning language and visual appearance despite modality mismatch, viewpoint/pose variation, ambiguity in textual descriptions, and potentially incorrect image-text pairings.

## Current in-vault view
The vault currently has seven directly relevant sources:
- [[source-arxiv-2303-12501-irra]] presents [[irra]] as a CLIP-based method that improves retrieval through training-time implicit relation reasoning and similarity distribution matching.
- [[source-arxiv-2308-09911-rde]] presents [[rde]] as a later robustness-oriented method that explicitly models [[noisy-correspondence]] and reports stronger historical benchmark results than IRRA.
- [[source-arxiv-2308-10045-tbps-clip]] presents [[tbps-clip]] as a lightweight CLIP recipe study showing that common training tricks, augmentation pools, and retrieval losses can make plain CLIP surprisingly strong for TBPS.
- [[source-arxiv-2407-04287-mars]] presents [[mars]] as an attribute-focused TBPS method that adds masked reconstruction and chunk-level supervision over visual attributes.
- [[source-arxiv-2507-10195-mra]] presents [[mra]] as a still later method that tackles the synthetic-to-real **pretraining gap** through [[domain-aware-diffusion]] and the [[synthetic-domain-aligned-dataset]], then adds explicit region-phrase alignment during pretraining.
- [[source-arxiv-2509-09118-ga-dms]] presents [[ga-dms]] and [[webperson]] as a paired method-plus-dataset advance that targets noisy text tokens directly while scaling curated real-image pretraining.
- [[source-arxiv-2601-18625-conquer]] presents [[conquer]] as a two-stage method that combines training-time alignment refinement with inference-time query enhancement for ambiguous or incomplete descriptions.

Together, these sources suggest a broader in-vault progression: CLIP-based retrieval became a strong baseline, later work emphasized robustness to pair-level noise, a separate recipe study showed that careful training/augmentation/loss design can make a simple CLIP baseline highly competitive, MARS added attribute salience plus text-conditioned reconstruction, MRA argued that synthetic pretraining improves when the corpus is domain-aligned to pedestrian imagery, GA-DMS plus WebPerson shifted the picture again toward token-level noise handling plus large-scale curated web data, and CONQUER added explicit inference-time query refinement as another route to stronger retrieval.

## Key points
- The task sits at the intersection of image-text retrieval and person re-identification.
- CLIP-initialized dual encoders appear as a strong backbone family across the current in-vault method line.
- A key design tension is balancing fine-grained cross-modal alignment against inference-time simplicity.
- [[irra]] emphasizes implicit relation learning and efficient global retrieval.
- [[rde]] adds the claim that noisy image-text pairings are common enough to require explicit robustness mechanisms such as CCD and TAL.
- [[tbps-clip]] shows that training tricks, augmentation pools, and retrieval-oriented losses can substantially lift a plain CLIP baseline without adding a bespoke multimodal interaction encoder.
- [[mars]] shows that attribute-level supervision and text-conditioned masked reconstruction can also improve TBPS.
- [[mra]] adds a data-centric argument: synthetic pretraining works better when the generated corpus is domain-aligned to real pedestrian data and carries region-phrase supervision.
- [[ga-dms]] adds a token-level robustness argument: retrieval improves when models explicitly separate noisy versus informative caption tokens during training.
- [[webperson]] adds a competing data-centric argument: large-scale curated real web images plus MLLM captioning can be a strong pretraining route beside synthetic-domain alignment.
- [[conquer]] adds an inference-time argument: retrieval can improve by actively enriching vague or incomplete user queries rather than treating the original text as fixed.
- Current vault evidence is still narrow, so benchmark conclusions should be treated as historical-within-vault rather than field-final.

## Evidence / claims
#### Claim
- Statement: A carefully tuned CLIP recipe can be a strong TBPS baseline without adding a bespoke multimodal interaction module.
- Status: active
- Confidence: 0.84
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Reinforces the idea that recipe design matters alongside architecture.

#### Claim
- Statement: CLIP-initialized dual encoders are a strong backbone family for this task and can be improved with additional cross-modal reasoning or robustness objectives.
- Status: active
- Confidence: 0.81
- Evidence: [[source-arxiv-2303-12501-irra]], [[source-arxiv-2308-09911-rde]], [[source-arxiv-2308-10045-tbps-clip]], [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Directly reinforced across multiple in-vault sources.

#### Claim
- Statement: Noisy correspondence is an important practical failure mode for this task because mismatched image-text pairs can mislead visual-semantic alignment learning.
- Status: active
- Confidence: 0.79
- Evidence: [[source-arxiv-2308-09911-rde]], [[source-arxiv-2509-09118-ga-dms]]
- Last confirmed: 2026-04-23
- Notes: Later GA-DMS reinforces the broader noise-aware framing at token level.

#### Claim
- Statement: The current vault's latest historical benchmark leadership is held by [[source-arxiv-2509-09118-ga-dms]], which reports Rank-1 scores of 77.60 on CUHK-PEDES, 69.51 on ICFG-PEDES, and 71.25 on RSTPReid for its 5M setting.
- Status: active
- Confidence: 0.86
- Evidence: [[source-arxiv-2303-12501-irra]], [[source-arxiv-2308-09911-rde]], [[source-arxiv-2308-10045-tbps-clip]], [[source-arxiv-2407-04287-mars]], [[source-arxiv-2507-10195-mra]], [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Historical synthesis only; this is a vault-local comparison, not a claim about the entire field.

#### Claim
- Statement: The vault now shows multiple routes to strong TBPS performance: IRRA and RDE establish CLIP-based baselines, TBPS-CLIP strengthens a recipe-only line, MARS adds attribute-aware reranking, MRA adds domain-aligned synthetic pretraining, GA-DMS plus WebPerson combine token-level noise handling with large-scale curated web pretraining, and CONQUER adds inference-time query refinement for ambiguous descriptions.
- Status: active
- Confidence: 0.84
- Evidence: [[source-arxiv-2303-12501-irra]], [[source-arxiv-2308-09911-rde]], [[source-arxiv-2308-10045-tbps-clip]], [[source-arxiv-2407-04287-mars]], [[source-arxiv-2507-10195-mra]], [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Synthesis claim that helps position the method family.

#### Claim
- Statement: Later in-vault evidence suggests inference-time query refinement is a distinct and practically relevant TBPS lever, especially for vague or incomplete user descriptions.
- Status: active
- Confidence: 0.80
- Evidence: [[source-arxiv-2601-18625-conquer]]
- Last confirmed: 2026-04-23
- Notes: Keep as a design-space claim rather than a broad field law until more sources reinforce it.

#### Claim
- Statement: TBPS-CLIP is a separate lightweight baseline study that strengthens the case for recipe design rather than defining the benchmark frontier.
- Status: active
- Confidence: 0.80
- Evidence: [[source-arxiv-2308-10045-tbps-clip]]
- Last confirmed: 2026-04-23
- Notes: Kept as a narrower claim after the broader benchmark synthesis above.

## Related pages
- [[irra]]
- [[rde]]
- [[tbps-clip]]
- [[mars]]
- [[mra]]
- [[ga-dms]]
- [[conquer]]
- [[webperson]]
- [[domain-aware-diffusion]]
- [[synthetic-domain-aligned-dataset]]
- [[noisy-correspondence]]
- [[source-arxiv-2303-12501-irra]]
- [[source-arxiv-2308-09911-rde]]
- [[source-arxiv-2308-10045-tbps-clip]]
- [[source-arxiv-2407-04287-mars]]
- [[source-arxiv-2507-10195-mra]]
- [[source-arxiv-2509-09118-ga-dms]]
- [[source-arxiv-2601-18625-conquer]]

## Sources
- [[source-arxiv-2303-12501-irra]]
- [[source-arxiv-2308-09911-rde]]
- [[source-arxiv-2308-10045-tbps-clip]]
- [[source-arxiv-2407-04287-mars]]
- [[source-arxiv-2507-10195-mra]]
- [[source-arxiv-2509-09118-ga-dms]]
- [[source-arxiv-2601-18625-conquer]]
