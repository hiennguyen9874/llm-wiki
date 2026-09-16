---
type: Concept
title: MARS attribute-aware text-based person search
description: MARS extends a RaSa/ALBEF person-search model with adjective–noun attribute supervision, text-guided masked image reconstruction, and deeper cross-modal attention.
tags: [cross-modal-retrieval, attribute-learning, masked-autoencoder, person-reidentification, reranking]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:08:28Z }
sources:
  - id: arxiv-2407.04287v1
    resource: ../raw/papers/arXiv-2407.04287v1/main.tex
    title: "MARS: Paying more attention to visual attributes for text-based person search"
---

# MARS attribute-aware text-based person search

MARS (MAE-Attribute-Relation-Sensitive) extends the ALBEF-initialized RaSa architecture for text-based person search with three coupled changes: explicit matching supervision for adjective–noun attribute chunks, text-conditioned reconstruction of masked image patches, and cross-attention throughout all 12 BERT blocks of its cross-modal encoder. It retains RaSa's relation-aware, sensitivity-aware, and contrastive objectives, then reranks the top 128 dual-encoder candidates with the cross-modal encoder. The strongest reported gains are in mean average precision (mAP), but the evidence is author-reported on three person-retrieval benchmarks and was not independently reproduced here.[^arxiv-2407.04287v1]

## Architecture and objectives

- A 12-block ViT image encoder and the first six BERT blocks as a text encoder produce unimodal patch/token embeddings. An exponential-moving-average copy supports RaSa's contrastive and replaced-token objectives.
- The cross-modal encoder uses all 12 BERT blocks with visual cross-attention, rather than adding cross-attention only to the last six. Its `[CLS]` representation supports global image–text matching and reranking.
- **Attribute loss:** spaCy extracts chunks comprising a noun and its associated adjectives, such as “white long shirt.” For every positive or sampled-negative image–caption pair, MARS averages the cross-modal token representations in each chunk and applies the same binary matching head used by the global relation-aware objective. Averaging the loss across chunks is intended to prevent one salient attribute from dominating a long description.[^arxiv-2407.04287v1]
- **Text-guided masked-autoencoder loss:** 75% of image patches are removed. A four-block Transformer decoder receives the remaining visual states, learned mask tokens, and text states through cross-attention, then minimizes mean-squared reconstruction error on removed patches. The decoder is training-only; it is intended to force the unimodal encoders to preserve mutually informative local detail.
- The complete objective combines RaSa's probabilistic image–text matching and positive-relation detection, masked-language modeling and momentum replaced-token detection, inter- and intra-modal contrastive losses, masked image reconstruction, and attribute matching. The reported weights are 0.5 for positive-relation detection, replaced-token detection, and contrastive loss; 1 for reconstruction; and 2 for attribute loss.[^arxiv-2407.04287v1]

**Synthesis:** the attribute objective supplies explicit local supervision, while masked reconstruction and full-depth cross-attention improve the representations on which that supervision operates. This coupling is supported by the paper's ablation: attribute loss alone improves mAP but not Rank-1 over the length-matched baseline, whereas combining it with either reconstruction or full cross-attention improves both measures.

## Retrieval and reported evidence

Inference first ranks every image by cosine similarity between unimodal class tokens, then applies the cross-modal matching head only to the top $k=128$ images. The paper's sweep shows accuracy saturating beyond 128 while whole-test-set reranking time rises sharply; exact timing hardware/protocol beyond the stated single RTX 4090 is not detailed enough for cross-system comparison.[^arxiv-2407.04287v1]

Author-reported results are:[^arxiv-2407.04287v1]

| Dataset | Rank-1 | Rank-5 | Rank-10 | mAP |
|---|---:|---:|---:|---:|
| CUHK-PEDES | 77.62 | 90.63 | 94.27 | 71.41 |
| ICFG-PEDES | 67.60 | 81.47 | 85.79 | 44.93 |
| RSTPReid | 67.55 | 86.65 | 91.35 | 52.92 |

Against the manuscript's RaSa baseline, these correspond to mAP gains of 2.03, 3.64, and 0.61 percentage points respectively. MARS does not lead every reported metric: CADA has higher Rank-1 on RSTPReid (67.70), IRRA has slightly higher Rank-10 on ICFG-PEDES (85.82), and RaSa ties MARS at 91.35 Rank-10 on RSTPReid.[^arxiv-2407.04287v1]

On CUHK-PEDES, increasing the caption cap from 50 to 70 tokens raises the RaSa baseline from 76.51/69.38 to 77.03/70.03 Rank-1/mAP. Relative to that stronger baseline:

- attribute loss alone reports 76.92/70.92;
- masked reconstruction plus attribute loss reports 77.63/71.35;
- attribute loss plus full cross-attention reports 77.45/71.46;
- all three components report 77.62/71.41.

The final configuration shares the global and attribute matching head. A frequency-reweighted attribute variant reaches higher Rank-1 (77.84) but lower mAP (71.19), so the authors choose the unweighted objective as the broader metric trade-off. Grad-CAM examples visually show more consistent localization across words in selected chunks, and random chunk-removal experiments usually favor MARS in mAP, especially for captions containing four or five chunks. These diagnostics are suggestive rather than causal proof: they compare selected visualizations and evaluate corruption derived from the same chunking scheme used for training.[^arxiv-2407.04287v1]

## Implementation details

The paper reports 30 epochs on one Nvidia RTX 4090, batch size 8, AdamW with weight decay 0.02, and learning rates of $10^{-4}$ for positive-relation/replaced-token parameters and $10^{-5}$ elsewhere. Images are resized to $384\times384$ with optional horizontal flip, captions are capped at 70 tokens, the momentum coefficient is 0.995, contrastive temperature is 0.07, and the queue contains 65,536 samples. The code link is <https://github.com/ErgastiAlex/MARS>.[^arxiv-2407.04287v1]

## Limitations and source inconsistencies

- Results cover only CUHK-PEDES, ICFG-PEDES, and RSTPReid, with ablation choices made on CUHK-PEDES. Generalization to ordinary image–text retrieval, other attribute parsers/languages, or newer backbones is untested.
- The top-$k$ cross-encoder reranking improves accuracy but forfeits pure dual-encoder retrieval efficiency. Reported runtime rises from roughly 70 seconds at $k=2$ to about 1,000 seconds at $k=128$ and 2,000 seconds at $k=256$ in the plotted test, without enough protocol detail for external comparison.
- Chunk extraction assumes adjective–noun structure and averages subrepresentations uniformly. Captions without recognized chunks, relational attributes, negation, and parsing errors are not separately evaluated; the authors report weakness after removing most attribute chunks.
- The source is an arXiv v1 manuscript containing editorial comments and an obsolete commented abstract with a placeholder result. Treat the active tables and equations as draft evidence rather than a camera-ready specification.
- The displayed attribute-loss equations omit the leading minus sign expected for cross-entropy, although the prose calls the objective cross-entropy. Implementation should be checked against released code.
- “State-of-the-art” language is metric- and comparator-dependent, as the source table itself contains the exceptions noted above.

## Relationships

- **Builds on:** RaSa supplies MARS's ALBEF initialization, momentum model, relation-aware objective, sensitivity-aware objective, and contrastive losses.[^arxiv-2407.04287v1]
- **Compared with:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) is a dual-encoder-oriented CLIP baseline whose interaction branch is training-only, unlike MARS's inference-time cross-modal reranker.
- **Compared with:** [TBPS-CLIP empirical person-search baseline](tbps-clip-empirical-person-search-baseline.md) provides a simpler CLIP fine-tuning baseline without MARS's attribute-chunk supervision or cross-encoder reranking.

[^arxiv-2407.04287v1]: Alex Ergasti, Tomaso Fontanini, Claudio Ferrari, Massimo Bertozzi, and Andrea Prati, “MARS: Paying more attention to visual attributes for text-based person search,” arXiv:2407.04287v1, 2024, [`main.tex`](../raw/papers/arXiv-2407.04287v1/main.tex). The architecture, attribute-loss schematic, Grad-CAM comparison, and top-$k$ timing/accuracy plot in the same source bundle were also visually inspected.
