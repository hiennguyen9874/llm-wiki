---
type: Dataset
title: MonkeyDoc v2
description: MonkeyDoc v2 is a 113-million-sample, 17-language document-image corpus used to pretrain MonkeyOCRv2 for page-level and cropped-element document tasks.
tags: [dataset, document-ai, ocr, multilingual, pretraining]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:39:23Z }
sources:
  - id: monkeyocrv2-paper
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI"
---

# MonkeyDoc v2

MonkeyDoc v2 is the author-described pretraining corpus for [MonkeyOCRv2](monkeyocrv2.md): 113M document-image samples in 17 languages, comprising 8M page images and 105M cropped elements. The authors report 61M real or expert-labeled samples and 52M synthetic samples.[^monkeyocrv2-paper]

## Composition and construction

The corpus covers simplified and traditional Chinese, English, Arabic, German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Korean, Dutch, Portuguese, Russian, Thai, and Vietnamese. English accounts for 19M samples and the two Chinese variants together 13M; coverage is therefore not balanced across languages.[^monkeyocrv2-paper]

The page subset supports layout, end-to-end, and layout-aware recognition, while cropped elements support text, table, and formula recognition. For real documents, the stated pipeline detects and crops layout elements, transcribes each with multiple expert recognizers, and retains the prediction with highest mean pairwise agreement. It filters incomplete layout annotations by testing whether a document VLM reads residual text after masking detected regions, and filters suspect reading order using an LLM judgement of concatenated text.[^monkeyocrv2-paper]

Synthetic examples render sampled multilingual-corpus text and complete character sets using varied fonts, styles, and resolutions; table synthesis fills real templates and generated structures, and approximately 0.8M formula samples are rendered from arXiv formulas. The source states that only official training splits from named public datasets were used and that downstream validation and test splits were excluded, but this cannot be audited from the local bundle.[^monkeyocrv2-paper]

## Trust limits

- The local bundle contains the manuscript, bibliography, source figures, and three appendix PDFs of example images, but no sample manifest, data records, licenses, dataset cards, filtering outputs, expert predictions, code, or release artifact. Corpus scale, split exclusion, provenance, and annotation-quality claims are author-reported and not independently reproducible here.[^monkeyocrv2-paper]
- The source identifies the collection as skewed toward high-resource scripts and does not provide per-source deduplication, consent, copyright, or language-quality audits. It should not be treated as an auditable or balanced multilingual training set.[^monkeyocrv2-paper]

## Relationships

- **Used by:** [MonkeyOCRv2](monkeyocrv2.md), whose three visual encoder variants are pretrained from scratch on this corpus.[^monkeyocrv2-paper]

[^monkeyocrv2-paper]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, local LaTeX source at [monkeyocr.tex](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex), including visually reviewed [model overview](../raw/2607.11562_MonkeyOCRv2/images/figfig.pdf), [pretraining overview](../raw/2607.11562_MonkeyOCRv2/images/pretrain.pdf), [data distribution](../raw/2607.11562_MonkeyOCRv2/images/data_dis.pdf), [MDPBench comparison](../raw/2607.11562_MonkeyOCRv2/images/fig1_mdpbench_bubble_svg-raw.pdf), and [reconstruction analysis](../raw/2607.11562_MonkeyOCRv2/images/resolution.pdf) (accessed 2026-08-17).
