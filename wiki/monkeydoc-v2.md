---
type: Dataset
title: MonkeyDoc v2
description: MonkeyDoc v2 is a 113-million-sample, 17-language document-image corpus used to pretrain MonkeyOCRv2 for page-level and cropped-element document tasks.
tags: [dataset, document-ai, ocr, multilingual, pretraining]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:32:14Z }
stale_after: 2027-01-25
sources:
  - id: monkeyocrv2-paper
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI"
  - id: monkeyocrv2-model-card
    resource: ../raw/zenosai-MonkeyOCRv2-B-Parsing.md
    kind: model-card
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI (model card and repository README)"
---

# MonkeyDoc v2

MonkeyDoc v2 is the author-described pretraining corpus for [MonkeyOCRv2](monkeyocrv2.md): 113M document-image samples in 17 languages, comprising 8M page images and 105M cropped elements. The authors report 61M real or expert-labeled samples and 52M synthetic samples.[^monkeyocrv2-paper]

## Composition and construction

The corpus covers simplified and traditional Chinese, English, Arabic, German, Spanish, French, Hindi, Indonesian, Italian, Japanese, Korean, Dutch, Portuguese, Russian, Thai, and Vietnamese. English accounts for 19M samples and the two Chinese variants together 13M; coverage is therefore not balanced across languages.[^monkeyocrv2-paper]

The page subset supports layout, end-to-end, and layout-aware recognition, while cropped elements support text, table, and formula recognition. For real documents, the stated pipeline detects and crops layout elements, transcribes each with multiple expert recognizers, and retains the prediction with highest mean pairwise agreement. It filters incomplete layout annotations by testing whether a document VLM reads residual text after masking detected regions, and filters suspect reading order using an LLM judgement of concatenated text.[^monkeyocrv2-paper]

Synthetic examples render sampled multilingual-corpus text and complete character sets using varied fonts, styles, and resolutions; table synthesis fills real templates and generated structures, and approximately 0.8M formula samples are rendered from arXiv formulas. The source states that only official training splits from named public datasets were used and that downstream validation and test splits were excluded, but this cannot be audited from the local bundle.[^monkeyocrv2-paper]

## Expert labeling toolchain

The card names the models behind the real-document annotation pipeline, which the paper describes only in general terms. Structure detection and reading-order prediction use [dots.ocr](dots-ocr.md); each cropped text, table, or formula block is then recognized independently by dots.ocr, [PaddleOCR-VL](paddleocr-vl.md), and Qwen3-VL; low-agreement blocks are dropped, and a retained block keeps the prediction with the highest mean agreement against the other two. Page-level control discards every page containing a filtered block, uses Qwen3 to judge whether the predicted reading order is reasonable, and uses Qwen3-VL to check whether structure detection missed any region.[^monkeyocrv2-model-card] The card presents this multi-expert agreement step as reducing model-specific annotation error; it publishes no agreement thresholds, disagreement rates, retained-block ratios, or per-labeler accuracy, so the amount of filtering and its effect on corpus composition are unknown.[^monkeyocrv2-model-card]

## Release status

MonkeyDoc v2 is distributed through ModelScope as a still-incomplete release under a stated total of 113M images in 17 languages, described by the card as the largest document image–text pair dataset. The card estimates roughly 10 TB of disk for the processed and compressed download and recommends at least 11 TB free, so training on the corpus starts from a partial, multi-terabyte transfer rather than a fixed snapshot.[^monkeyocrv2-model-card]

## Contradictions

The card gives two different real-world release counts for the same dataset. Its News section and its first MonkeyDoc v2 section state that 52M synthetic and 52M real-world samples have been released, while the later MonkeyDoc v2 section states that all 52M synthetic samples and 41M real-world samples derived from FinePDF have been released, with further real-world data still being organized. Neither figure reconciles item-by-item with the paper's accounting of 61M real or expert-labeled samples and 52M synthetic samples, and the bundle contains no release manifest. The released real-world total is therefore unresolved, and any specific released split should be treated as provisional.[^monkeyocrv2-model-card][^monkeyocrv2-paper]

## Trust limits

- The local bundle contains the manuscript, bibliography, source figures, and three appendix PDFs of example images, but no sample manifest, data records, licenses, dataset cards, filtering outputs, expert predictions, code, or release artifact. Corpus scale, split exclusion, provenance, and annotation-quality claims are author-reported and not independently reproducible here.[^monkeyocrv2-paper]
- The source identifies the collection as skewed toward high-resource scripts and does not provide per-source deduplication, consent, copyright, or language-quality audits. It should not be treated as an auditable or balanced multilingual training set.[^monkeyocrv2-paper]

## Relationships

- **Used by:** [MonkeyOCRv2](monkeyocrv2.md), whose three visual encoder variants are pretrained from scratch on this corpus.[^monkeyocrv2-paper]
- **Labeled with:** [dots.ocr](dots-ocr.md) for structure detection and reading order, plus [PaddleOCR-VL](paddleocr-vl.md) and Qwen3-VL as co-recognizers, and Qwen3 for reading-order verification.[^monkeyocrv2-model-card]

[^monkeyocrv2-model-card]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, model card and repository README captured at [zenosai-MonkeyOCRv2-B-Parsing.md](../raw/zenosai-MonkeyOCRv2-B-Parsing.md), locators: § News entry dated 2026.07.21; § MonkeyDoc v2 (both occurrences, lines 54 and 1293 of the capture); § MonkeyDoc v2 › Expert Model Labeling Toolchain (accessed 2026-10-25).

[^monkeyocrv2-paper]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, local LaTeX source at [monkeyocr.tex](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex), including visually reviewed [model overview](../raw/2607.11562_MonkeyOCRv2/images/figfig.pdf), [pretraining overview](../raw/2607.11562_MonkeyOCRv2/images/pretrain.pdf), [data distribution](../raw/2607.11562_MonkeyOCRv2/images/data_dis.pdf), [MDPBench comparison](../raw/2607.11562_MonkeyOCRv2/images/fig1_mdpbench_bubble_svg-raw.pdf), and [reconstruction analysis](../raw/2607.11562_MonkeyOCRv2/images/resolution.pdf) (accessed 2026-08-17).
