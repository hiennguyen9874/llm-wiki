---
type: Synthesis
title: Current OCR approaches
description: Current document OCR spans lightweight detector–recognizer pipelines, modular layout-first systems, end-to-end generative VLMs, and emerging data-, decoding-, and evaluation-centered approaches.
tags: [ocr, document-parsing, vision-language-models, synthesis]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:34:28Z }
sources:
  - id: pp-ocrv6-report
    resource: ../raw/2606.13108_PP-OCRv6/main.tex
    title: PP-OCRv6 Technical Report
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: PaddleOCR-VL-1.6 Technical Report
  - id: deepseek-ocr-2-report
    resource: ../raw/2601.20552_DeepSeek-OCR-2/main.tex
    title: DeepSeek-OCR 2 Technical Report
  - id: unlimited-ocr-report
    resource: ../raw/2606.23050_Unlimited-OCR/main.tex
    title: Unlimited OCR Works
  - id: mineru-diffusion-card
    resource: ../raw/MinerU-Diffusion-V1-0320-2.5B.md
    title: MinerU-Diffusion model card
  - id: ovisocr2-report
    resource: ../raw/2607.13639_OvisOCR2/main.tex
    title: OvisOCR2 Technical Report
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
  - id: multimodal-ocr-report
    resource: ../raw/2603.13032_MultimodalOCR/main.tex
    title: Multimodal OCR Technical Report
  - id: falcon-perception-report
    resource: ../raw/2603.27365_FalconPerception/main.tex
    title: Falcon Perception
  - id: real5-source
    resource: ../raw/2601.21957_PaddleOCR-VL-1.5/main.tex
    title: PaddleOCR-VL-1.5 Technical Report
---

# Current OCR approaches

Current document OCR is no longer one homogeneous text-recognition task. The design space ranges from compact detection–recognition pipelines to models that reconstruct a page as ordered Markdown, JSON, HTML, LaTeX, SVG, or other typed representations. The strongest recurring pattern is not uniform model scaling but explicit management of resolution, layout and reading order, structured-output validity, long-tail data, and inference cost.

## Architectural families

### Lightweight detector–recognizer pipelines

Classical two-stage OCR remains the preferred shape when the target is text boxes plus transcription under tight latency, memory, mobile, or hallucination constraints. [PP-OCRv6](pp-ocrv6.md) shares a reparameterizable backbone across detection and CTC recognition at 1.5M–34.5M parameters; [Nemotron OCR v2](nemotron-ocr-v2.md) adds a relational grouping and reading-order stage. These systems are efficient and controllable, but rich document reconstruction requires separate layout and specialist modules.[^pp-ocrv6-report]

### Modular layout-first document parsing

Systems such as [PP-StructureV3](pp-structurev3.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [GLM-OCR](glm-ocr.md), and [FalconOCR](falcon-ocr.md) first detect page elements and reading order, then recognize native-resolution crops in parallel. [PP-DocLayoutV3](pp-doclayoutv3.md) illustrates the trend toward jointly predicting classes, boxes, masks, and pairwise order. This decomposition preserves small text and routes formulas and tables to suitable recognizers, at the cost of error propagation across stages and greater system complexity.[^paddleocr-vl-1-6-report][^falcon-perception-report]

### End-to-end generative document VLMs

End-to-end models map a full page and prompt directly to an ordered structured representation. [FireRed-OCR](firered-ocr.md), [OvisOCR2](ovisocr2.md), [DeepSeek-OCR 2](deepseek-ocr-2.md), and [Infinity-Parser2](infinity-parser2.md) exemplify page-to-Markdown or task-conditioned JSON/HTML/LaTeX generation. This unifies recognition, layout, and formatting and makes one model reusable across tasks, but introduces sequence-length cost, repetition or hallucination risk, and sensitivity to output schemas and language priors.[^deepseek-ocr-2-report][^ovisocr2-report][^infinity-parser2-report]

### Unified multimodal reconstruction

[Multimodal OCR](multimodal-ocr.md) extends parsing beyond text, tables, and formulas by assigning type-specific payloads such as SVG to information-bearing graphics. This points toward document reconstruction rather than OCR alone, although the retained source describes full-page parsing and region-level SVG generation as separate task-conditioned passes rather than one fully unified release path.[^multimodal-ocr-report]

## Cross-cutting technical directions

1. **Resolution management:** modular systems use low-resolution global layout followed by native-resolution crops; end-to-end systems use native/dynamic-resolution encoders, multi-crop views, or aggressive visual-token compression. The objective is to preserve tiny text without paying full-page quadratic cost.
2. **Reading order as a first-class target:** approaches include detector-level pairwise precedence, sequence order in generated markup, RL order rewards, and DeepSeek-OCR 2's causal visual queries. Reading order is now part of the learned objective rather than only an X–Y-sort postprocess.[^deepseek-ocr-2-report]
3. **Typed and grounded output:** Markdown is common, but JSON with boxes, HTML tables, LaTeX formulas, image-region coordinates, SVG, and task-specific formats increasingly serve downstream automation and auditability.
4. **Data-centric specialization:** the frontier is shifting from indiscriminate scaling toward mining unstable predictions, sparse feature regions, and unreliable labels. [Document-parser data flywheel](document-parser-data-flywheel.md) converts observed failures into targeted mined, pseudo-labeled, or synthesized data; [DOM-based document synthesis](dom-based-document-synthesis.md) derives pixels and geometry-aligned labels from the same rendered source.[^paddleocr-vl-1-6-report][^infinity-parser2-report][^ovisocr2-report]
5. **Progressive post-training:** CPT or pre-alignment establishes broad visual-text competence, SFT teaches canonical structured outputs, and GRPO uses verifiable task-native rewards such as edit similarity, TEDS, CDM, mIoU, syntax validity, and reading-order consistency. Compact models may use teacher RL followed by on-policy distillation and model fusion when direct RL is unstable.[^paddleocr-vl-1-6-report][^ovisocr2-report][^infinity-parser2-report]
6. **Faster and longer decoding:** compressed visual tokens and sparse MoE decoders reduce prefix and active-parameter cost; multi-token prediction generates several future tokens per step; [MinerU-Diffusion](mineru-diffusion.md) explores block-parallel diffusion instead of autoregression; [Unlimited OCR](unlimited-ocr.md) preserves the full visual prefix while limiting generated-token attention to a sliding window for bounded decode-side KV cache.[^mineru-diffusion-card][^unlimited-ocr-report]
7. **Robust real-world capture:** training and evaluation increasingly include skew, warping, illumination, screen photography, low resolution, handwriting, old scans, seals, rare scripts, rotated tables, and long-tail layouts. [Real5-OmniDocBench](real5-omnidocbench.md) captures five physical distortion conditions, but remains a targeted rather than comprehensive in-the-wild test.[^real5-source]

## Practical selection

| Requirement | Usually suitable approach | Main trade-off |
|---|---|---|
| Mobile, CPU, high throughput, plain text | Lightweight detector + CTC recognizer | Limited document semantics and structure |
| Dense pages, tiny text, tables/formulas, traceable boxes | Layout-first modular parser | Stage coupling, deployment complexity |
| One model, flexible prompts, Markdown/JSON output | End-to-end document VLM | Hallucination, formatting, long decoding |
| Multi-page one-shot parsing | Compressed visual tokens plus bounded-history decoding | Input prefix and finite context remain limits |
| Graphics and charts as editable structure | Typed multimodal reconstruction | Coverage and evaluation remain immature |
| Domain-specific or long-tail documents | Data flywheel, expert pseudo-labeling, DOM synthesis, staged post-training | Label noise, contamination, and proprietary data dependencies |

A robust production design is often hybrid: use a detector/recognizer for faithful text localization, a layout model for structure and order, specialist parsers for tables and formulas, and a VLM only where flexible reconstruction or semantic extraction justifies its cost and risk.

## Evidence and evaluation limits

Nearly all relevant wiki concepts are `draft`; missing independent verification must not be read as falsity, but the retained evidence is predominantly author reports and model cards. Cross-paper scores are not a reliable global ranking because benchmark versions, prompts, rendering, output normalization, hardware, and model configurations differ. Ground-truth metrics should be decomposed by text, table, formula, layout, reading order, and robustness; LLM-as-judge methods such as [OCR Arena](ocr-arena.md) measure judge preference under a prompt and deliberately omit some layout and figure concerns.

## Relationships

- **Synthesizes:** [PP-OCRv6](pp-ocrv6.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [DeepSeek-OCR 2](deepseek-ocr-2.md), [OvisOCR2](ovisocr2.md), [Infinity-Parser2](infinity-parser2.md), and [Multimodal OCR](multimodal-ocr.md).
- **Uses:** [Document-parser data flywheel](document-parser-data-flywheel.md), [DOM-based document synthesis](dom-based-document-synthesis.md), and [Reference Sliding Window Attention](reference-sliding-window-attention.md) as cross-cutting methods.

[^pp-ocrv6-report]: Zhang et al., *PP-OCRv6*, local source at [main.tex](../raw/2606.13108_PP-OCRv6/main.tex).
[^paddleocr-vl-1-6-report]: Zhang et al., *PaddleOCR-VL-1.6*, local source at [main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex).
[^deepseek-ocr-2-report]: Wei, Sun, and Li, *DeepSeek-OCR 2*, local source at [main.tex](../raw/2601.20552_DeepSeek-OCR-2/main.tex).
[^unlimited-ocr-report]: Yin et al., *Unlimited OCR Works*, local source at [main.tex](../raw/2606.23050_Unlimited-OCR/main.tex).
[^mineru-diffusion-card]: MinerU-Diffusion authors, local [model card](../raw/MinerU-Diffusion-V1-0320-2.5B.md).
[^ovisocr2-report]: Lu et al., *OvisOCR2 Technical Report*, local source at [main.tex](../raw/2607.13639_OvisOCR2/main.tex).
[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex).
[^multimodal-ocr-report]: Zheng et al., *Multimodal OCR*, local source at [main.tex](../raw/2603.13032_MultimodalOCR/main.tex).
[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local source at [main.tex](../raw/2603.27365_FalconPerception/main.tex).
[^real5-source]: Cui et al., *PaddleOCR-VL-1.5*, local source at [main.tex](../raw/2601.21957_PaddleOCR-VL-1.5/main.tex).
