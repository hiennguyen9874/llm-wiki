---
type: Benchmark
title: MDPBench
description: MDPBench is an author-constructed benchmark for multilingual document parsing on digital-born and photographed pages under varied real-world capture conditions.
tags: [benchmark, document-parsing, multilingual, ocr, robustness]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:39:23Z }
sources:
  - id: mdpbench-paper
    resource: ../raw/2603.28130_MDPBench/main.tex
    title: "MDPBench: A Benchmark for Multilingual Document Parsing in Real-World Scenarios"
  - id: monkeyocrv2-paper
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI"
---

# MDPBench

MDPBench evaluates document parsing across 17 languages, diverse document types, and both digital-born and photographed pages. The authors construct 3,400 images from 850 source pages: each source page is included digitally and captured three times under varied indoor or outdoor conditions.[^mdpbench-paper]

## Construction and annotation

The 850 source pages span Arabic, Chinese (simplified and traditional), English, French, German, Hindi, Indonesian, Italian, Japanese, Korean, Dutch, Portuguese, Russian, Spanish, Thai, and Vietnamese. They include academic papers, business reports, handwritten notes, newspapers, textbooks, and comics.[^mdpbench-paper]

For photographed pages, the authors print or screen-display source documents, then capture them indoors (two images per document) and outdoors (one). The stated conditions cover backgrounds, bending, creasing, wrinkling, handheld capture, camera orientation, illumination, shadows, blur, glare, and screen moiré.[^mdpbench-paper]

Annotation starts with manually selected layout proposals from dots.ocr or [PaddleOCR-VL](paddleocr-vl.md). Cropped text, formula, and table elements are recognized by PaddleOCR-VL, dots.ocr, and Qwen3-VL; the highest-average-similarity result is selected using normalized edit distance for text/formulas and TEDS for tables. When that score is below 0.7, the pipeline falls back to Gemini-3-Pro. Trained annotators correct layout, type, reading order, and content; independent reviewers return failed documents for revision until acceptance.[^mdpbench-paper]

The paper states that 2,720 images and annotations form a public split, while the remaining 680 make a private split evaluated through an official submission site.[^mdpbench-paper]

## Evaluation protocol and reported results

MDPBench aggregates scores by page before averaging across pages, rather than first averaging scores by element type. It follows OmniDocBench preprocessing, element extraction, and matching; headers, footers, page numbers, and page footnotes are ignored. Text and reading order use $1 -$ normalized edit distance, formulas use CDM, and tables use TEDS.[^mdpbench-paper]

The authors report that Gemini-3-Pro scores 86.4 overall (90.4 digital-born; 85.1 photographed) and dots.mocr is the highest-scoring listed open model at 80.5 (90.5 digital-born; 77.2 photographed). Across the evaluated systems, photographed-page performance declines by 17.8 percentage points on average and non-Latin-script performance is 14.0 points below Latin-script performance. These are author-run comparisons, not independently reproduced results.[^mdpbench-paper]

The paper's examples identify content omissions, incorrect reading order, fabricated or repetitive output, and language drift in individual outputs. It specifically illustrates right-to-left reading-order failures on two-column Arabic pages, Hindi diacritic omissions, Latin/Cyrillic character confusions in Russian, and unwanted word breaks in Thai.[^mdpbench-paper]

## Trust limits

- The local bundle contains the paper and its figures, but no dataset images or annotations, public/private split manifest, capture instructions, evaluation implementation, model outputs, prompts, or baseline configurations. The claimed benchmark and results cannot be reproduced from local evidence.[^mdpbench-paper]
- The 17.8-point photographed and 14.0-point script-group drops aggregate systems with different architectures and training data; they describe this paper's evaluated set, not an inherent or universal degradation rate.[^mdpbench-paper]
- This compilation visually reviewed the overview, capture-condition, annotation-pipeline, and qualitative-error figures. The source figures demonstrate examples and intended coverage, not prevalence estimates for individual error types.[^mdpbench-paper]

## Relationships

- **Related benchmark:** [Real5-OmniDocBench](real5-omnidocbench.md) also evaluates physical-document robustness, but MDPBench adds multilingual source pages, its own annotations, and a private evaluation split.[^mdpbench-paper]
- **Evaluates:** [Multimodal OCR](multimodal-ocr.md)'s dots.mocr, [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), [PaddleOCR-VL](paddleocr-vl.md), [GLM-OCR](glm-ocr.md), [DeepSeek-OCR](deepseek-ocr.md), and [PP-StructureV3](pp-structurev3.md) among other systems.[^mdpbench-paper]
- **Evaluates:** [MonkeyOCRv2](monkeyocrv2.md)'s B-Parsing implementation, which reports 83.3 overall under the stated official MDPBench protocol; this is an author-reported model result, not an independent benchmark re-evaluation.[^monkeyocrv2-paper]

[^mdpbench-paper]: Li et al., *MDPBench: A Benchmark for Multilingual Document Parsing in Real-World Scenarios*, local LaTeX source at [main.tex](../raw/2603.28130_MDPBench/main.tex), including visually reviewed [benchmark overview](../raw/2603.28130_MDPBench/examples/overall_MDP.pdf), [capture conditions](../raw/2603.28130_MDPBench/examples/photographed.pdf), [annotation pipeline](../raw/2603.28130_MDPBench/examples/annotation.pdf), and qualitative-error figures (accessed 2026-08-17).
[^monkeyocrv2-paper]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, local LaTeX source at [monkeyocr.tex](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex) (accessed 2026-08-17).
