---
type: Concept
title: Meta CLIP 2 worldwide CLIP scaling
description: A CLIP training recipe that curates native-language worldwide web image–text pairs with per-language metadata and balancing, then scales training exposure and capacity to improve English and multilingual transfer jointly.
tags: [multimodal-learning, vision-language-models, contrastive-learning, multilingual, data-curation, web-scale-training]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:55:29Z }
sources:
  - id: chuang-2025-meta-clip-2
    resource: ../raw/2507.22062_MetaCLIP 2/paper.tex
    title: "Meta CLIP 2: A Worldwide Scaling Recipe"
---

# Meta CLIP 2 worldwide CLIP scaling

Meta CLIP 2 extends the Meta CLIP curation approach to native-language, worldwide web image–text data. Its recipe builds language-specific concept metadata, curates pairs with per-language matching and balancing, and scales both the number of seen pairs and model capacity; the authors report that its ViT-H/14 configuration improved their English and multilingual evaluations simultaneously.[^chuang-2025-meta-clip-2]

## Worldwide curation

- The metadata is maintained independently by language to avoid cross-language string ambiguity. It combines multilingual WordNet synsets (31 languages), Wikipedia unigrams and bigrams (329 languages, from May 2024 dumps), and Wikipedia titles; the authors use community tokenizers for languages that do not use spaces when processing Wikipedia text.[^chuang-2025-meta-clip-2]
- Language identification selects metadata for each alt-text. The pipeline substring-matches concepts, counts matches by language, and samples pairs to balance head and tail concepts rather than filtering pairs through an existing CLIP teacher or translating captions.[^chuang-2025-meta-clip-2]
- Instead of using one global cutoff, it derives each language’s count threshold so that its fraction of matches from tail concepts matches the English proportion. The reported implementation uses per-language Aho–Corasick automata with lazy loading and memory-mapped count/probability data to make curation feasible at this scale.[^chuang-2025-meta-clip-2]
- In the paper’s ViT-B/32 ablation, routing alt-text to language-specific metadata and replacing a shared threshold with per-language thresholds improved ImageNet from 61.1% to 64.7% and multilingual scores relative to the shared-threshold configuration. This supports those design choices in that experimental setting, not a claim that they alone eliminate multilingual trade-offs.[^chuang-2025-meta-clip-2]
- The source reports removing NSFW content with a safety classifier, using a face detector to remove human biometrics and PII, and deduplicating ImageNet evaluation sets with hashed similarity embeddings. These are described pipeline mitigations, not evidence that the resulting dataset is free of harmful content, PII, or benchmark leakage.[^chuang-2025-meta-clip-2]

## Training and reported results

- Worldwide data made up 56% of the curated training pairs in the paper’s setup. To preserve English exposure, the authors increased global batch size and seen pairs by 2.3× (from 12.8B to 29B seen pairs); changing the multilingual tokenizer was the only stated architectural change.[^chuang-2025-meta-clip-2]
- In the reported ablations, ViT-L/14 still lost English ImageNet accuracy when trained on worldwide data, while ViT-H/14 at the scaled exposure was the observed capacity inflection point: ImageNet increased from 80.5% for the English-only counterpart to 81.3% for the worldwide model.[^chuang-2025-meta-clip-2]
- The same ViT-H/14 worldwide configuration reported 50.2% on Babel-ImageNet, 64.3% image-to-text recall@1 on XM3600, and 57.4% local-language accuracy on CVQA. These are paper-reported, benchmark-specific comparisons; model, data, exposure, and evaluation choices limit their generality.[^chuang-2025-meta-clip-2]
- On the paper’s cultural-diversity evaluations, replacing 13B English seen pairs with 13B worldwide pairs improved GLDv2 accuracy from 52.8% to 65.8% and GeoDE from 93.4% to 94.3%; scaling worldwide exposure to 29B further improved GLDv2 but not GeoDE. The authors note that multilingual and geographically diverse benchmarks retain coverage and collection biases: XM3600 inherits selection bias from Open Images, while GeoDE’s crowdsourced images can vary with worker demographics and collection quality.[^chuang-2025-meta-clip-2]

## Relationships

- Extends: [MetaCLIP metadata-curated language–image pre-training](metaclip-metadata-curated-language-image-pretraining.md) by generalizing its metadata matching and balancing approach from English Common Crawl to native-language worldwide web data.[^chuang-2025-meta-clip-2]
- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by retaining the CLIP-style dual-encoder setting while changing metadata, curation, tokenization, and training scale for worldwide data.[^chuang-2025-meta-clip-2]
- Related: [SigLIP 2 multilingual vision–language encoders](siglip2-multilingual-vision-language-encoders.md) is a competing multilingual vision–language encoder evaluated against Meta CLIP 2 in this source; the systems differ in objective, data pipeline, and auxiliary training, so the reported comparison does not isolate a single cause.[^chuang-2025-meta-clip-2]

[^chuang-2025-meta-clip-2]: Chuang et al., “Meta CLIP 2: A Worldwide Scaling Recipe” (2025), [source manuscript](../raw/2507.22062_MetaCLIP%202/paper.tex).
