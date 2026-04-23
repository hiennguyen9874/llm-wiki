---
title: Text-based Person Search Methods and Models Briefing
created: 2026-04-23
last_updated: 2026-04-23
source_count: 9
status: reviewed
page_type: briefing
aliases:
  - TBPS methods and models briefing
  - text-based person search briefing
tags:
  - machine-learning
  - multimodal
  - retrieval
  - briefing
  - person-retrieval
visibility: private
related_sources:
  - source-arxiv-2303-12501-irra
  - source-arxiv-2308-09911-rde
  - source-arxiv-2308-10045-tbps-clip
  - source-arxiv-2407-04287-mars
  - source-arxiv-2507-10195-mra
  - source-arxiv-2509-09118-ga-dms
  - source-arxiv-2601-18625-conquer
  - source-arxiv-2510-17685-bi-irra
  - source-arxiv-2604-18376-mvr
---

# Text-based Person Search Methods and Models Briefing

## One-sentence summary
Text-based person search in this vault has evolved from a CLIP-based retrieval problem into a multi-lever design space where gains come from recipe tuning, noise robustness, attribute awareness, domain-aligned synthetic pretraining, multilingual supervision, and inference-time query compensation ([[text-to-image-person-retrieval]], [[source-arxiv-2308-10045-tbps-clip]], [[source-arxiv-2308-09911-rde]], [[source-arxiv-2407-04287-mars]], [[source-arxiv-2507-10195-mra]], [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2601-18625-conquer]], [[source-arxiv-2510-17685-bi-irra]], [[source-arxiv-2604-18376-mvr]]).

## Current state
The vault’s baseline story starts with [[irra]], which uses CLIP initialization plus implicit relation reasoning and similarity distribution matching to get efficient global retrieval without explicit local alignment at inference time ([[source-arxiv-2303-12501-irra]], [[irra]]). [[tbps-clip]] then shows that a well-designed CLIP recipe can be highly competitive on TBPS without a bespoke multimodal interaction module, using training tricks, augmentation, and retrieval-oriented losses ([[source-arxiv-2308-10045-tbps-clip]], [[tbps-clip]]). [[rde]] shifts the focus to [[noisy-correspondence]], arguing that pair-level annotation noise is a real failure mode and adding consensus filtering plus robust alignment objectives ([[source-arxiv-2308-09911-rde]], [[rde]], [[noisy-correspondence]]). [[mars]] adds a different lever: attribute-level supervision and text-conditioned masked reconstruction, suggesting that models improve when they pay attention to visual attributes rather than only global caption-image similarity ([[source-arxiv-2407-04287-mars]], [[mars]]).

The later sources broaden the picture further. [[mra]] argues that synthetic pretraining only pays off when the synthetic corpus is domain-aligned to pedestrian data, so data construction becomes part of the method itself ([[source-arxiv-2507-10195-mra]], [[mra]], [[domain-aware-diffusion]], [[synthetic-domain-aligned-dataset]]). [[ga-dms]] and [[webperson]] extend that data-centric line with large-scale real web data and token-level noise handling, reinforcing that robustness can be won both by better data and by explicitly suppressing noisy text tokens ([[source-arxiv-2509-09118-ga-dms]], [[ga-dms]], [[webperson]]). On the inference side, [[conquer]] and [[mvr]] show that retrieval can improve without retraining the backbone: CONQUER refines queries with anchor-derived attributes, while MVR compensates for expression drift through multi-view reformulation and semantic aggregation ([[source-arxiv-2601-18625-conquer]], [[conquer]], [[source-arxiv-2604-18376-mvr]], [[mvr]]). Finally, [[bi-irra]] widens the task definition by treating multilingual retrieval as a first-class setting and extending IRRA-style reasoning across languages ([[source-arxiv-2510-17685-bi-irra]], [[bi-irra]]).

## Key tensions
The main tension is where to spend the modeling budget: training-time fixes versus inference-time fixes. [[rde]], [[mra]], and [[ga-dms]] invest in training, while [[conquer]] and [[mvr]] adapt the query or features at inference time ([[source-arxiv-2308-09911-rde]], [[source-arxiv-2507-10195-mra]], [[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2601-18625-conquer]], [[source-arxiv-2604-18376-mvr]]). A second tension is architecture versus recipe: [[irra]] and [[mars]] modify the model, whereas [[tbps-clip]] argues that recipe design alone can already be strong ([[source-arxiv-2303-12501-irra]], [[source-arxiv-2407-04287-mars]], [[source-arxiv-2308-10045-tbps-clip]]). A third tension is the bottleneck definition itself: some sources emphasize pair-level noise ([[rde]]), others token-level noise ([[ga-dms]]), others data domain mismatch ([[mra]]), and others multilingual transfer ([[bi-irra]]) or expression drift at inference time ([[mvr]]).

## Open questions
What is the best combination of levers when methods are composed: better alignment, better data, or better inference-time adaptation ([[source-arxiv-2308-10045-tbps-clip]], [[source-arxiv-2507-10195-mra]], [[source-arxiv-2601-18625-conquer]])? How much of each reported gain is benchmark-specific versus transferable across datasets and languages ([[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2510-17685-bi-irra]], [[source-arxiv-2604-18376-mvr]])? Can token-denoising, multilingual supervision, and query enhancement coexist cleanly without overfitting to a single benchmark recipe ([[source-arxiv-2509-09118-ga-dms]], [[source-arxiv-2510-17685-bi-irra]], [[source-arxiv-2601-18625-conquer]])? And does inference-time semantic compensation still help when captions are already high-quality and low-noise ([[source-arxiv-2604-18376-mvr]])?

## Recommended next steps
1. Keep [[text-to-image-person-retrieval]] as the landing page for the method family and update it whenever a new branch appears.
2. Compare future models by lever class: backbone/recipe, robustness, data curation, multilinguality, or inference-time refinement.
3. Preserve dataset-specific benchmark history instead of forcing a single global winner, because the current vault already shows mixed leadership across [[bi-irra]], [[mvr]], [[conquer]], and earlier sources ([[source-arxiv-2510-17685-bi-irra]], [[source-arxiv-2604-18376-mvr]], [[source-arxiv-2601-18625-conquer]]).
