---
type: Model System
title: FireRed-OCR
description: FireRed-OCR is a 2B end-to-end document-parsing VLM that adapts Qwen3-VL through geometry- and semantics-balanced data, structured SFT, and format-constrained GRPO.
tags: [ocr, document-parsing, vision-language-models, reinforcement-learning, markdown, structural-generation]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:52:41Z }
sources:
  - id: firered-ocr-report
    resource: ../raw/2603.01840_FireRed-OCR/fireredocr_report.tex
    title: FireRed-OCR Technical Report
  - id: firered-ocr-model-card
    resource: ../raw/2603.01840_FireRed-OCR/README.md
    title: FireRed-OCR model card
---

# FireRed-OCR

FireRed-OCR-2B is an end-to-end document-image-to-Markdown model based on Qwen3-VL-2B-Instruct. The authors specialize it through geometry- and semantics-balanced data curation, multi-task spatial pre-alignment, structured supervised fine-tuning (SFT), and Group Relative Policy Optimization (GRPO) with output-format rewards.[^firered-ocr-report][^firered-ocr-model-card]

## Data and training

The report's data factory indexes pages by visual-layout clusters and by language, layout, source, and genre tags. It upsamples rare or complex strata, re-annotates selected data into a common Markdown format with PaddleOCR-VL, procedurally renders difficult tables and formulas, filters malformed or low-quality targets, and sends legible hard cases to a proprietary-model refinement step.[^firered-ocr-report]

Training progresses through three stages:

1. **Multi-task pre-alignment** jointly trains detection plus OCR, prompted region OCR, and full-page layout-to-Markdown conversion to establish spatial grounding.
2. **Specialized SFT** trains standardized, hierarchical Markdown output across multilingual and complex layouts.
3. **Format-constrained GRPO** samples output groups and scores formula syntax, Markdown/hierarchical closure, rectangular table structure, and text similarity to pseudo-ground truth or human labels.[^firered-ocr-report]

The reported implementation uses about 1.3M pre-alignment samples, 400K SFT document--Markdown pairs, and 50K GRPO samples. The supervised stages use a global batch size of 256 and a learning rate of $3 \times 10^{-5}$; GRPO uses $5 \times 10^{-7}$, 24,576-token context, and 2,048-token completions.[^firered-ocr-report]

## Reported evaluation

All results are author-reported and have not been independently reproduced:[^firered-ocr-report][^firered-ocr-model-card]

- On OmniDocBench v1.5, FireRed-OCR-2B reports **92.94** overall, text edit distance **0.032**, formula CDM **91.71**, table TEDS **90.31**, table TEDS-S **93.81**, and reading-order edit distance **0.041**. The report presents this as the top end-to-end result, but its own table reports higher overall scores for pipeline systems PaddleOCR-VL-1.5 (94.50) and GLM-OCR (94.60).
- On the authors' internal FireRedBench for distorted and non-standard layouts, it reports **74.62** overall, ahead of the listed end-to-end baselines but below Gemini-3.0 Pro (79.68), Qwen3-VL-235B (79.04), and Qwen3.5-397B (81.85).
- On OCRBench Text, TEDS_TEST, and PubTabNet, it reports **93.5**, **80.6**, and **77.0**, respectively. Its comparison table lists these values alongside systems whose configurations vary; the source does not establish a controlled cross-system comparison.[^firered-ocr-report]

## Trust limits

- The local bundle contains the technical report, model card, bibliography, and figures, but not weights, code, training data, evaluation scripts, prompts, or complete baseline configurations. Its training and performance claims are therefore not reproducible from this bundle.[^firered-ocr-report][^firered-ocr-model-card]
- FireRedBench is described as an internal benchmark, but its contents and evaluation implementation are not included. Its robustness result cannot be independently checked here.[^firered-ocr-report]
- The report states that standardized re-annotation spans more than 10 million samples, while its implementation section gives 1.3M, 400K, and 50K samples for the three training stages. It does not clarify whether the larger value is a processed pool or a different count, so the relationship between these quantities is unresolved.[^firered-ocr-report]
- Format validity is not equivalent to document fidelity: the GRPO rewards test syntax, closure, and table rectangularity, while its text reward may use pseudo-ground truth. The source does not provide an independent error analysis showing that syntactic gains preserve semantic or visual accuracy.[^firered-ocr-report]

## Relationships

- **Builds on:** [PaddleOCR-VL](paddleocr-vl.md) as an automated Markdown re-annotator rather than as its inference pipeline.[^firered-ocr-report]
- **Compared with:** [DeepSeek-OCR 2](deepseek-ocr-2.md) and [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) on author-reported document-parsing benchmarks; their architectures and evaluation configurations differ.[^firered-ocr-report]

[^firered-ocr-report]: Super Intelligence Team, Xiaohongshu Inc., *FireRed-OCR Technical Report*, local LaTeX source at [fireredocr_report.tex](../raw/2603.01840_FireRed-OCR/fireredocr_report.tex), including [abstract](../raw/2603.01840_FireRed-OCR/section/0_abstract.tex), [data](../raw/2603.01840_FireRed-OCR/section/2_data.tex), [method](../raw/2603.01840_FireRed-OCR/section/3_method.tex), [experiments](../raw/2603.01840_FireRed-OCR/section/5_experiments.tex), [data-pipeline figure](../raw/2603.01840_FireRed-OCR/figures/data.png), [training-pipeline figure](../raw/2603.01840_FireRed-OCR/figures/model.png), and [benchmark figure](../raw/2603.01840_FireRed-OCR/figures/omnidoc_228.png) (accessed 2026-08-17).
[^firered-ocr-model-card]: FireRedTeam, [FireRed-OCR model card](../raw/2603.01840_FireRed-OCR/README.md) (accessed 2026-08-17).
