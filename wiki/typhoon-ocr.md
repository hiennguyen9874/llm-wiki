---
type: Model System
title: Typhoon OCR
description: Typhoon OCR is an open Thai-and-English document-extraction VLM family whose 2B V1.5 revision uses a single image-only prompt to emit Markdown, HTML tables, figure descriptions, equations, and page markers.
tags: [ocr, document-parsing, vision-language-models, thai, multilingual, structured-output]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:45:38Z }
sources:
  - id: typhoon-ocr-report
    resource: ../raw/2601.14722_TyphoonOCR/main.tex
    title: "Typhoon OCR: Open Vision-Language Model For Thai Document Extraction"
  - id: typhoon-ocr-model-card
    resource: ../raw/2601.14722_TyphoonOCR/README.md
    title: Typhoon-OCR-1.5-2B model card
---

# Typhoon OCR

Typhoon OCR is an open vision-language model family for Thai and English document extraction. Version 1 fine-tunes Qwen2.5-VL 3B and 7B models with separate default and structure-output modes; V1.5 instead fine-tunes Qwen3-VL 2B, removes PDF-metadata dependence, and uses one prescribed prompt to produce a common structured representation.[^typhoon-ocr-report][^typhoon-ocr-model-card]

## Inputs and structured outputs

V1.5 is intended to infer structure from document images, including scanned PDFs and photographs, rather than depend on PDF text layers or layout metadata. It targets government documents, handwriting, formulas, infographics, charts and tables, financial statements, and long-form books/documents.[^typhoon-ocr-report]

The supplied prompt requires clean Markdown only, using HTML `<table>` elements for tables, LaTeX for equations, `<figure>` tags with **Thai-language** image descriptions, `<page_number>` tags, and Unicode checked/unchecked boxes. The model card warns that the model is task-specific: it should be used only with the provided prompt, has no guardrails or VQA capability, and may hallucinate.[^typhoon-ocr-model-card]

## Data and training

For V1, the authors report a 77,029-document Thai-and-English corpus: 54.4% Structure Mode and 45.6% Default Mode. Structure Mode combines Markdown narrative text, HTML complex tables, and figure tags; the corpus is built by conventional OCR or text-layer extraction, VLM restructuring, automated consistency checks, and sampled human review. Its listed sources include general infographics (45.6%), CoSyn-400K (8.3%), Thai financial reports (7.2%), Thai books (5.6%), and Thai handwriting (5.5%).[^typhoon-ocr-report]

V1.5 retains 53.7% of the V1 corpus, adds 2.2% Thai-translated Cauldron VQA data and 6.4% DocLayNet-v1.2, and uses 37.6% synthetic documents, for 155,403 total samples. The synthetic pipeline combines Thai vocabulary and diverse typography with Southeast Asian imagery, charts, mathematical expressions, and Augraphy degradation (blur, noise, compression, illumination variation, and geometric distortion).[^typhoon-ocr-report]

The V1.5 recipe is full-parameter supervised fine-tuning of Qwen3-VL 2B with a 16,384-token maximum sequence length, resolution-aware preprocessing capped at 1,800-pixel width for larger images, two epochs on four H100 GPUs, and quantization-aware training. The report says Qwen3-VL and Dots.OCR were used to improve labels; it does not publish the training corpus, labels, or training implementation.[^typhoon-ocr-report]

## Reported evaluation

These are author-reported results on held-out, internally curated Thai-document test sets; the source bundle does not provide the test data, sizes, prompts, or evaluation implementation needed to reproduce the comparisons.[^typhoon-ocr-report]

- Across six categories, V1.5 2B reports average BLEU **0.644**, ROUGE-L **0.774**, and Levenshtein distance **0.251**, versus V1 7B's **0.558**, **0.686**, and **0.332**, respectively.
- V1.5 leads the table on Thai books and government forms on all three metrics. On Thai financial reports, V1 7B has higher BLEU (0.849 vs. 0.819) and ROUGE-L (0.933 vs. 0.910), while V1.5 has slightly lower Levenshtein distance (0.079 vs. 0.082).
- Gemini 2.5 Pro leads the table's infographic, handwriting-form, and "Others" categories on all three metrics; V1.5 nonetheless improves on V1 in each of those rows. GPT-5 is included as a baseline but does not lead a reported category.[^typhoon-ocr-report]

## Scope and trust limits

The authors identify severe image degradation (low resolution, motion blur, and occlusion), primary support limited to Thai and English, and lack of higher-level reasoning as limitations. They propose evaluation on ThaiOCRBench and future diagram understanding and structured information extraction.[^typhoon-ocr-report]

This local bundle contains the report source, bibliography, model card, and six source figures. It does not contain model weights, datasets, annotations, training code, evaluation code, or the in-house test corpus. Therefore, performance, robustness, throughput, and "frontier" comparisons remain author claims rather than independently reproduced findings.[^typhoon-ocr-report]

[^typhoon-ocr-report]: Nonesung et al., *Typhoon OCR: Open Vision-Language Model For Thai Document Extraction*, local LaTeX source at [main.tex](../raw/2601.14722_TyphoonOCR/main.tex), including six PDFs in `picture/` (accessed 2026-08-17).
[^typhoon-ocr-model-card]: SCB 10X, *Typhoon-OCR-1.5-2B model card*, local [README.md](../raw/2601.14722_TyphoonOCR/README.md) (accessed 2026-08-17).
