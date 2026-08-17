---
type: Model System
title: Qianfan-OCR
description: Qianfan-OCR is a 4B end-to-end document-intelligence VLM that optionally emits structured layout reasoning before prompt-driven parsing or understanding outputs.
tags: [ocr, document-parsing, vision-language-models, layout-analysis, document-understanding, multilingual]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:59:59Z }
sources:
  - id: qianfan-ocr-report
    resource: ../raw/2603.13398_Qianfan-OCR/qianfan_ocr_report.tex
    title: "Qianfan-OCR: A Unified End-to-End Model for Document Intelligence"
  - id: qianfan-ocr-model-card
    resource: ../raw/2603.13398_Qianfan-OCR/README.md
    title: Qianfan-OCR model card
---

# Qianfan-OCR

Qianfan-OCR is a Baidu Qianfan 4B-parameter end-to-end document-intelligence VLM. A Qianfan-ViT vision encoder, two-layer projection MLP, and Qwen3-4B language model directly produce Markdown or other prompt-specified outputs; optional **Layout-as-Thought** first emits ordered boxes, element labels, and brief summaries inside `<think>` tokens.[^qianfan-ocr-report]

## Architecture and tasks

The AnyResolution Qianfan-ViT has 24 Transformer layers and tiles images into 448x448 regions, producing 256 visual tokens per tile and at most 4,096 tokens for 16 tiles. A two-layer GELU MLP maps 1,024-dimensional vision features to the Qwen3-4B backbone's 2,560-dimensional embeddings. The report describes 3.6B non-embedding parameters, 36 language-model layers, and a 32K native context window (extendable to 131K with YaRN).[^qianfan-ocr-report]

Prompt-driven tasks include image-to-Markdown parsing, layout analysis and reading order, HTML table and LaTeX formula conversion, chart QA, document QA, key-information extraction, handwriting and scene-text recognition, and multilingual OCR. The model card claims coverage of 192 languages.[^qianfan-ocr-report][^qianfan-ocr-model-card]

## Layout-as-Thought

Appending `<think>` requests a structured intermediate layout in which each element has normalized `[0, 999]` box coordinates, one of 25 layout categories, and (for text-like elements) a short description. Coordinates use one special token per value (`<COORD_0>` through `<COORD_999>`) rather than digit strings; the authors estimate this reduces layout-output length by about 50%.[^qianfan-ocr-report]

The report's OmniDocBench v1.5 ablation gives the default mode a 93.12 overall score and the thinking mode 92.64. Thinking improves table TEDS (91.21 vs. 91.02) and TEDS-S (94.03 vs. 93.85), but worsens text edit distance, formula CDM, and the aggregate result. Its cumulative-score plot, ordered by page layout-label entropy, shows an advantage on high-entropy pages and a reversal as homogeneous pages are added. The source therefore recommends thinking for mixed-layout pages such as technical reports, newspapers, and exam sheets, not simple text pages or forms.[^qianfan-ocr-report]

## Training

The reported four-stage recipe is adapter-only cross-modal alignment (50B tokens), full-parameter OCR-heavy pretraining (2T), domain-specific enhancement (800B), and instruction tuning. Its six described synthesis pipelines cover document parsing, KIE, complex tables, charts, formulas, and multilingual OCR; document-parsing labels are generated using [PaddleOCR-VL](paddleocr-vl.md)'s 25-category taxonomy and recognition output.[^qianfan-ocr-report]

On a Qianfan-VL-8B ablation rather than the released 4B model, the full sequence scores 84.39 average accuracy, compared with 71.37 for Stage 1 plus instruction tuning. Adding a 1:1 general-data mix to OCR-specific Stage 3 raises the ablation from 75.97 to 80.07 without Stage 2, and from 84.09 to 84.39 with it.[^qianfan-ocr-report]

## Reported evaluation

All results are author-reported and have not been independently reproduced:[^qianfan-ocr-report]

- **Specialized parsing:** 93.12 overall on OmniDocBench v1.5 (text edit distance 0.041, formula CDM 92.43, table TEDS 91.02, table TEDS-S 93.85, reading-order edit distance 0.049) and 79.8 on OlmOCR Bench. The report positions these as the leading listed end-to-end results, while [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), a pipeline, is listed at 94.50 on OmniDocBench.
- **General OCR and understanding:** 880 on OCRBench; 56.0/60.77 on OCRBenchv2 English/Chinese; and 76.7/79.3 on CCOCR multilingual/overall. It reports 92.8 DocVQA, 94.0/85.2 CharXiv DQ/RQ, 88.1 ChartQA, 42.9 ChartQAPro, 85.9 ChartBench, and 66.8 OCRVQA. The authors' OCR-plus-Qwen3-4B pipeline baselines score 0.0 on both CharXiv tasks, an experiment supporting their claim that text-only extraction loses chart structure.
- **KIE and throughput:** The report gives an 87.9 mean across five public KIE benchmarks and 1.024 pages/s at W8A8 quantization on OmniDocBench pages with one A100 and vLLM 0.10.2; its W16A16 configuration is 0.503 pages/s.[^qianfan-ocr-report]

## Trust limits

- The local bundle contains the technical-report LaTex, model card, bibliography, three rendered report figures, a benchmark chart, and a qualitative layout example, but no weights, source code, training data, evaluation scripts, or complete evaluation prompts/configurations. Its training, quality, language-coverage, and benchmark claims are not reproducible from this bundle.[^qianfan-ocr-report][^qianfan-ocr-model-card]
- Several comparison values are attributed to official leaderboards or other papers; the report also says it modified VLMEvalKit for some evaluations and integrates specialist OCR outputs into its own environment. This prevents the reported cross-system rankings from serving as a controlled comparison.[^qianfan-ocr-report]
- Layout-as-Thought has only been evaluated for document parsing on OmniDocBench v1.5 in this source. Its usefulness for KIE, document QA, and chart understanding remains untested, and the entropy analysis is author-provided rather than an independently validated routing policy.[^qianfan-ocr-report]
- The throughput table mixes the authors' Qianfan runs with pipeline results taken from other reports. It is a deployment-configuration measurement, not a model-only performance guarantee.[^qianfan-ocr-report]

## Relationships

- **Uses:** [PaddleOCR-VL](paddleocr-vl.md) as the report's document-parsing annotation and recognition engine for synthesized training data.[^qianfan-ocr-report]
- **Compared with:** [DeepSeek-OCR 2](deepseek-ocr-2.md) and [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) on author-reported OmniDocBench v1.5 results; their different architectures and evaluation provenance make this an uncontrolled cross-paper comparison.[^qianfan-ocr-report]
- **Related approach:** [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md), another end-to-end parser that uses layout-aware optimization; Qianfan-OCR instead uses supervised layout reasoning exposed through optional intermediate output.[^qianfan-ocr-report]

[^qianfan-ocr-report]: Baidu Qianfan Team, *Qianfan-OCR: A Unified End-to-End Model for Document Intelligence*, local LaTeX source at [qianfan_ocr_report.tex](../raw/2603.13398_Qianfan-OCR/qianfan_ocr_report.tex), including the [architecture comparison](../raw/2603.13398_Qianfan-OCR/ocr_comparison.pdf), [OmniDocBench chart](../raw/2603.13398_Qianfan-OCR/omnidocbench_v1.5.pdf), [thinking ablation](../raw/2603.13398_Qianfan-OCR/think_and_no_think_compare.pdf), [other benchmark chart](../raw/2603.13398_Qianfan-OCR/qianfan_ocr_other_benchmarks.jpg), and [qualitative layout example](../raw/2603.13398_Qianfan-OCR/show_cases/jiaocaineedrop_jiaocai_needrop_en_2893_think_viz.jpg) (accessed 2026-08-17).
[^qianfan-ocr-model-card]: Baidu Qianfan Team, [Qianfan-OCR model card](../raw/2603.13398_Qianfan-OCR/README.md) (accessed 2026-08-17).
