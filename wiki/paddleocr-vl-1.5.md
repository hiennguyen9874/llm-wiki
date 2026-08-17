---
type: Model System
title: PaddleOCR-VL-1.5
description: PaddleOCR-VL-1.5 is a 0.9B two-stage document parser that adds distortion-robust polygonal layout analysis, text spotting, seal recognition, and long-document post-processing to PaddleOCR-VL.
tags: [document-parsing, ocr, vision-language-models, layout-analysis, text-spotting, multilingual]
status: deprecated
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:23:38Z }
sources:
  - id: paddleocr-vl-1-5-report
    resource: ../raw/2601.21957_PaddleOCR-VL-1.5/main.tex
    title: "PaddleOCR-VL-1.5: Towards a Multi-Task 0.9B VLM for Robust In-the-Wild Document Parsing"
  - id: paddleocr-vl-1-5-model-card
    resource: ../raw/2601.21957_PaddleOCR-VL-1.5/README.md
    title: PaddleOCR-VL-1.5 model card
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: "PaddleOCR-VL-1.6: Expanding the Frontier of Document Parsing with Under-Optimized Region Refinement and Progressive Post-Training"
---

# PaddleOCR-VL-1.5

PaddleOCR-VL-1.5 is a 0.9B two-stage parser that replaces [PaddleOCR-VL](paddleocr-vl.md)'s layout stage with [PP-DocLayoutV3](pp-doclayoutv3.md), then uses an ERNIE-4.5-0.3B-backed VLM to recognize localized document elements. It adds end-to-end text spotting and seal recognition, emits Markdown and JSON, and provides cross-page table merging and heading-hierarchy refinement.[^paddleocr-vl-1-5-report]

## Architecture and tasks

PP-DocLayoutV3 first predicts element categories, polygonal or rectangular regions, and reading order. The VLM recognizes the resulting localized regions as OCR text, tables, formulas, charts, or seals; its separate spotting mode directly emits text and quadrilateral locations in reading order.[^paddleocr-vl-1-5-report]

The recognition model retains the predecessor's NaViT-style native-resolution encoder, adaptive MLP connector, and ERNIE-4.5-0.3B language model. Its six instruction tasks are OCR, table, formula, chart, seal, and spotting. Spotting represents each region with four ordered vertices, using normalized-coordinate special tokens rather than textual numbers.[^paddleocr-vl-1-5-report]

## Training and data

The report describes PP-DocLayoutV3 as jointly trained from PP-DocLayout-plus-L initialization on more than 38,000 manually annotated document samples, with distortion-aware augmentation. The element VLM is trained for one epoch of pre-training on 46M samples and one epoch of post-training on 5.6M samples, at a maximum resolution of 1280×28×28 except for spotting, which uses up to 2048×28×28.[^paddleocr-vl-1-5-report]

The authors report adding Bengali and China’s Tibetan script, for 111 supported languages in total. They also describe GRPO-based training and uncertainty-aware cluster sampling for the VLM, but omit implementation, data releases, and reward details sufficient to reproduce either procedure.[^paddleocr-vl-1-5-report]

## Reported results and deployment

All results below are author-reported and not independently reproduced:[^paddleocr-vl-1-5-report]

- **OmniDocBench v1.5:** 94.50 overall, text edit distance 0.035, formula CDM 94.21, table TEDS 92.76, table TEDS-S 95.79, and reading-order edit distance 0.042.
- **Real5-OmniDocBench:** 92.05 overall across scanning, warping, screen photography, illumination, and skew; the reported per-condition scores are 93.43, 91.25, 91.76, 92.16, and 91.66 respectively.
- **New tasks:** 0.8621 average accuracy on the authors' nine-dimension text-spotting benchmark, and 0.138 normalized edit distance on their 300-image seal benchmark.
- **End-to-end performance:** on a single A100 processing 1,355 OmniDocBench v1.5 pages in batches of 512, its FastDeploy v2.3 configuration reports 1.4335 pages/s and 2,016.6 tokens/s, including PDF rendering and Markdown generation. The model card documents PaddleOCR pipeline use, a `transformers` element-level example, and vLLM serving; it notes that the official pipeline is faster and supports page-level parsing.[^paddleocr-vl-1-5-report][^paddleocr-vl-1-5-model-card]

## Trust limits

- The source bundle provides the report, model card, source figures, and visual examples, but not weights, training or evaluation code, datasets, prompts, or complete baseline configurations. The claimed training procedures and results are not reproducible from this bundle.[^paddleocr-vl-1-5-report]
- The text-spotting and seal results use in-house benchmarks whose complete composition and protocol are not supplied. The Real5 benchmark preserves OmniDocBench annotations but its capture procedure and public benchmark implementation are not included here.[^paddleocr-vl-1-5-report]
- Several comparison scores are independently evaluated by the authors rather than taken from the cited leaderboard. Cross-system throughput comparisons also use different serving backends and versions, so they are deployment-configuration results rather than model-only measurements.[^paddleocr-vl-1-5-report]

## Supersession

PaddleOCR-VL-1.6 replaces this version as of 2026-08-17; it retains the 0.9B two-stage architecture while adding its under-optimized-region data engine and progressive post-training recipe.[^paddleocr-vl-1-6-report]

## Relationships

- **Superseded by:** [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), effective 2026-08-17.[^paddleocr-vl-1-6-report]
- **Supersedes:** [PaddleOCR-VL](paddleocr-vl.md) as the next version of the two-stage parser.
- **Uses:** [PP-DocLayoutV3](pp-doclayoutv3.md) for layout regions and reading order.
- **Uses:** [Real5-OmniDocBench](real5-omnidocbench.md) to assess physical-distortion robustness.
- **Related approach:** [PP-StructureV3](pp-structurev3.md) also produces Markdown and JSON via a modular document-parsing pipeline, but it uses specialized recognizers rather than the V1.5 element VLM.[^paddleocr-vl-1-5-report]

[^paddleocr-vl-1-5-report]: Cui et al., *PaddleOCR-VL-1.5: Towards a Multi-Task 0.9B VLM for Robust In-the-Wild Document Parsing*, local LaTeX source at [main.tex](../raw/2601.21957_PaddleOCR-VL-1.5/main.tex), including the [system architecture](../raw/2601.21957_PaddleOCR-VL-1.5/images/PaddleOCR-VL-1.5.png), [PP-DocLayoutV3 architecture](../raw/2601.21957_PaddleOCR-VL-1.5/images/PP-DocLayoutV3.png), [result figures](../raw/2601.21957_PaddleOCR-VL-1.5/images/paddleocr-vl-1.5_metrics.png), and [Real5 sample PDF](../raw/2601.21957_PaddleOCR-VL-1.5/images/Real5-OmniDocBench-sample.pdf) (accessed 2026-08-17).
[^paddleocr-vl-1-5-model-card]: PaddlePaddle, [PaddleOCR-VL-1.5 model card](../raw/2601.21957_PaddleOCR-VL-1.5/README.md) (accessed 2026-08-17).
[^paddleocr-vl-1-6-report]: Zhang et al., *PaddleOCR-VL-1.6: Expanding the Frontier of Document Parsing with Under-Optimized Region Refinement and Progressive Post-Training*, local LaTeX source at [main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex) (accessed 2026-08-17).