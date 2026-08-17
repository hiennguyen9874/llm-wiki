---
type: Model System
title: PP-OCRv5
description: PP-OCRv5 is a 0.07B-parameter OCR pipeline for unified Chinese, Pinyin, English, and Japanese text detection and recognition across server and mobile deployments.
tags: [ocr, multilingual, handwriting, lightweight-models]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:27:19Z }
sources:
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
  - id: pp-ocrv6-report
    resource: ../raw/2606.13108_PP-OCRv6/main.tex
    title: "PP-OCRv6: From 1.5M to 34.5M Parameters, Surpassing Billion-Scale VLMs on OCR Tasks"
---

# PP-OCRv5

PP-OCRv5 is a lightweight OCR pipeline with server and CPU-oriented mobile variants. A single recognition model handles Simplified Chinese, Traditional Chinese, Chinese Pinyin, English, and Japanese; the report gives the system a 0.07B parameter count and says its recognition model is under 100 MB.[^paddleocr3-report]

## Pipeline

1. **Optional preprocessing:** PP-LCNet-based page orientation classification and UVDoc-based image unwarping.
2. **Text detection:** PP-HGNetV2 replaces PP-HGNet; GOT-OCR2.0 visual features supervise the detector through distillation. PFHead and dynamic scale-aware refinement carry over from PP-OCRv4, while hard-case mining and multilingual augmentation expand training coverage.
3. **Text-line orientation:** detected lines are classified and corrected before recognition.
4. **Text recognition:** a PP-HGNetV2 dual-branch model uses attention-based GTC-NRTR to guide the CTC-based SVTR-HGNet branch during training; only SVTR-HGNet runs at inference.[^paddleocr3-report]

Training-data construction combines synthetic rare characters, automatically parsed PDFs and ebooks, conventional OCR models, and ERNIE-4.5-VL-424B-A47B for handwritten-sample annotation and filtering.[^paddleocr3-report]

## Reported results

The authors evaluate 17 scenarios using 1 minus normalized edit distance. The detailed figure reports an average of **0.804** for PP-OCRv5, tied at the displayed precision with Qwen2.5-VL-72B and above the other plotted systems. PP-OCRv5 is strongest in the plotted handwritten Chinese, Pinyin, and ancient-Chinese subsets, while several VLMs score higher on handwritten and printed English. The report also claims a 26% recognition-error reduction over previous models on non-standard Chinese and English handwriting.[^paddleocr3-report]

## Trust limits

- Results use a self-built 17-scenario dataset rather than a released benchmark corpus; the bundle does not provide samples, scenario sizes, evaluation code, uncertainty, or independent reproduction.[^paddleocr3-report]
- The prose says PP-OCRv5 "ranks first" and surpasses all compared multimodal models, but the figure shows PP-OCRv5 and Qwen2.5-VL-72B both at **0.804** average after rounding. A strict lead cannot be established from the displayed values.[^paddleocr3-report]
- The 26% handwriting error reduction does not identify the exact predecessor, per-language sample counts, or confidence intervals in the surrounding text.[^paddleocr3-report]

## Relationships

- **Part of:** [PaddleOCR 3.0](paddleocr-3.md).
- **Used by:** [PP-StructureV3](pp-structurev3.md) supplies its OCR stage.
- **Precedes:** [PP-OCRv6](pp-ocrv6.md), which retains this data-curation methodology while replacing the backbone and both neck designs.[^pp-ocrv6-report]

[^paddleocr3-report]: Cui et al., *PaddleOCR 3.0 Technical Report*, local LaTeX source at [main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), including `images/ocr_res_final.png`, `images/pp_ocrv5_benchmark.pdf`, and `images/pp_ocrv5_framwork2.pdf` (accessed 2026-08-17).
[^pp-ocrv6-report]: Zhang et al., *PP-OCRv6: From 1.5M to 34.5M Parameters, Surpassing Billion-Scale VLMs on OCR Tasks*, local LaTeX source at [main.tex](../raw/2606.13108_PP-OCRv6/main.tex) (accessed 2026-08-17).
