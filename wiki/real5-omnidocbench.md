---
type: Benchmark
title: Real5-OmniDocBench
description: Real5-OmniDocBench is an OmniDocBench v1.5-derived benchmark that applies five physical-document distortion conditions while retaining corresponding ground-truth annotations.
tags: [benchmark, document-parsing, ocr, robustness, layout-analysis]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:00:00Z }
sources:
  - id: paddleocr-vl-1-5-report
    resource: ../raw/2601.21957_PaddleOCR-VL-1.5/main.tex
    title: "PaddleOCR-VL-1.5: Towards a Multi-Task 0.9B VLM for Robust In-the-Wild Document Parsing"
---

# Real5-OmniDocBench

Real5-OmniDocBench is an author-constructed robustness benchmark derived from OmniDocBench v1.5. It assesses document parsing under scanning, warping, screen photography, illumination variation, and skew while retaining a stated one-to-one correspondence with the original dataset’s annotations and evaluation protocol.[^paddleocr-vl-1-5-report]

## Construction and evaluation

The source states that all conditions except scanning were manually acquired with handheld mobile devices. Its included sample figure shows the same source pages under each distortion condition. The benchmark uses the text edit-distance, formula CDM, table TEDS, and reading-order metrics of OmniDocBench v1.5; its overall score is their weighted combination.[^paddleocr-vl-1-5-report]

The source reports that [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) scores 92.05 overall: 93.43 for scanning, 91.25 warping, 91.76 screen photography, 92.16 illumination, and 91.66 skew. These are author-reported model results, not independently reproduced benchmark results.[^paddleocr-vl-1-5-report]

## Trust limits

- The source links to a dataset page but this bundle contains no dataset files, capture instructions, exact splits, transformation specifications, evaluation implementation, or baseline prompts/configurations. The benchmark construction and scores cannot be reproduced from local evidence.[^paddleocr-vl-1-5-report]
- The claimed annotation correspondence may permit comparable scoring, but the report does not establish whether each physical condition has comparable capture quality, sample distribution, or inter-annotator treatment. It should therefore be treated as a targeted robustness evaluation rather than a complete characterization of in-the-wild document performance.[^paddleocr-vl-1-5-report]

## Relationships

- **Derived from:** OmniDocBench v1.5, as described by the source; this wiki has no separate concept for that upstream benchmark.
- **Used by:** [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) for evaluation of physical-distortion robustness.

[^paddleocr-vl-1-5-report]: Cui et al., *PaddleOCR-VL-1.5: Towards a Multi-Task 0.9B VLM for Robust In-the-Wild Document Parsing*, local LaTeX source at [main.tex](../raw/2601.21957_PaddleOCR-VL-1.5/main.tex), including [Real5 sample PDF](../raw/2601.21957_PaddleOCR-VL-1.5/images/Real5-OmniDocBench-sample.pdf) (rendered and inspected, accessed 2026-08-17).