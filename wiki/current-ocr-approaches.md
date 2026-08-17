---
type: Synthesis
title: Current OCR approaches
description: Current document OCR spans lightweight detector–recognizer pipelines, modular layout-first systems, end-to-end generative VLMs, and emerging data-, decoding-, and evaluation-centered approaches.
tags: [ocr, document-parsing, vision-language-models, synthesis]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:43:44Z }
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
  - id: infinity-parser-report
    resource: ../raw/2506.03197_InfinityParser/main.tex
    title: Infinity-Parser Technical Report
  - id: rex-omni-report
    resource: "../raw/2510.12798_Detect Anything via Next Point Prediction/main.tex"
    title: Detect Anything via Next Point Prediction
  - id: lightonocr-report
    resource: ../raw/2601.14251_LightOnOCR/templateArxiv.tex
    title: LightOnOCR Technical Report
  - id: typhoonocr-report
    resource: ../raw/2601.14722_TyphoonOCR/main.tex
    title: Typhoon OCR Technical Report
  - id: qianfan-ocr-report
    resource: ../raw/2603.13398_Qianfan-OCR/qianfan_ocr_report.tex
    title: Qianfan-OCR Technical Report
  - id: monkeyocrv2-report
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    title: MonkeyOCRv2 Technical Report
  - id: chandra-ocr-2-card
    resource: ../raw/chandra-ocr-2.md
    title: Chandra OCR 2 model card
  - id: dots-ocr-card
    resource: ../raw/dots.ocr.md
    title: dots.ocr model card
  - id: granite-docling-card
    resource: ../raw/granite-docling-258m.md
    title: Granite Docling 258M model card
  - id: hunyuanocr-card
    resource: ../raw/HunyuanOCR-1.5.md
    title: HunyuanOCR-1.5 model card
  - id: mineru2-5-card
    resource: ../raw/MinerU2.5-2509-1.2B.md
    title: MinerU2.5 model card
  - id: mineru2-5-pro-card
    resource: ../raw/MinerU2.5-Pro-2604-1.2B.md
    title: MinerU2.5-Pro model card
  - id: nanonets-ocr2-card
    resource: ../raw/Nanonets-OCR2.md
    title: Nanonets-OCR2 model card
  - id: nemotron-parse-card
    resource: ../raw/NVIDIA-Nemotron-Parse-v1.1.md
    title: NVIDIA Nemotron Parse v1.1 model card
  - id: olmocr2-card
    resource: ../raw/olmOCR-2-7B-1025.md
    title: olmOCR-2-7B-1025 model card
  - id: rolmocr-card
    resource: ../raw/RolmOCR.md
    title: RolmOCR model card
  - id: surya-ocr-2-card
    resource: ../raw/surya-ocr-2.md
    title: Surya OCR 2 model card
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

### Adjacent unified perception

Not every retained OCR-capable model is a document parser. [Rex-Omni](rex-omni.md) casts detection, grounding, OCR polygons, and keypoints as quantized coordinate-token generation, making OCR one task in a unified perception interface. [Falcon Perception](falcon-perception.md) similarly supplies a general early-fusion perception architecture related to FalconOCR. These systems matter where OCR must share a model with localization or interaction, but they do not replace document-to-Markdown pipelines.[^rex-omni-report][^falcon-perception-report]

## Retained model coverage

The architectural families above use representative systems. For complete retrieval, the remaining current model families retained under `raw/` map as follows:

| Model or family | Primary distinguishing direction |
|---|---|
| [Chandra OCR 2](chandra-ocr-2.md) | Multilingual PDF/image conversion to Markdown, HTML, or layout-bearing JSON.[^chandra-ocr-2-card] |
| [dots.ocr](dots-ocr.md) | One prompt-driven 1.7B VLM for layout detection, recognition, grounding, and reading-order output.[^dots-ocr-card] |
| [Granite Docling 258M](granite-docling-258m.md) | Compact document-conversion VLM integrated into the Docling processing stack.[^granite-docling-card] |
| [HunyuanOCR-1.5](hunyuanocr-1.5.md) | Lightweight end-to-end OCR with agentic data construction and DFlash speculative decoding.[^hunyuanocr-card] |
| [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) | Direct GRPO training with verifiable content, segment-count, and reading-order rewards.[^infinity-parser-report] |
| [LightOnOCR](lightonocr.md) | Native-resolution ViT plus Qwen3 decoder, with an optional image-box output variant.[^lightonocr-report] |
| [MonkeyOCRv2](monkeyocrv2.md) | Document-native visual-encoder pretraining through text generation and pixel reconstruction.[^monkeyocrv2-report] |
| [MinerU2.5](mineru2-5.md) and [MinerU2.5-Pro](mineru2-5-pro.md) | Coarse-to-fine global layout followed by native-resolution crop recognition; Pro emphasizes scaled and refined data.[^mineru2-5-card][^mineru2-5-pro-card] |
| [Nanonets-OCR2](nanonets-ocr2.md) | Multilingual image-to-Markdown with explicit handling of equations, tables, figures, signatures, watermarks, checkboxes, and VQA.[^nanonets-ocr2-card] |
| [NVIDIA Nemotron Parse v1.1](nemotron-parse-v1-1.md) | Sub-1B encoder–decoder emitting ordered text, element classes, and boxes.[^nemotron-parse-card] |
| [olmOCR-2-7B-1025](olmocr-2-7b-1025.md) | Qwen2.5-VL PDF-page extraction specialized through SFT and GRPO.[^olmocr2-card] |
| [Qianfan-OCR](qianfan-ocr.md) | Optional Layout-as-Thought emits boxes, labels, and summaries before parsing or understanding.[^qianfan-ocr-report] |
| [RolmOCR](rolmocr.md) | Metadata-independent PDF-page OCR trained with rotated pages for off-angle robustness.[^rolmocr-card] |
| [Surya OCR 2](surya-ocr-2.md) | Shared compact VLM for layout, order, OCR, and tables, plus a separate line detector.[^surya-ocr-2-card] |
| [Typhoon OCR](typhoon-ocr.md) | Thai–English extraction using one image-only prompt and rich Markdown/HTML/formula outputs.[^typhoonocr-report] |

Older or release-specific artifacts are represented by their current family pages: [DeepSeek-OCR](deepseek-ocr.md) precedes DeepSeek-OCR 2; [PaddleOCR-VL](paddleocr-vl.md) and [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) precede 1.6; [Chandra OCR](chandra-ocr.md) is superseded by Chandra OCR 2; `dots.mocr` is the released implementation covered by Multimodal OCR; and Infinity-Parser2-Pro is covered by Infinity-Parser2. [PaddleOCR 3.0](paddleocr-3.md) is a toolkit rather than one model, while [MDPBench](mdpbench.md), [Real5-OmniDocBench](real5-omnidocbench.md), MonkeyDoc, and Infinity-Doc are benchmarks or datasets rather than model families.

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

- **Synthesizes:** the retained current OCR and document-parsing model families cataloged under **Retained model coverage**, with [PP-OCRv6](pp-ocrv6.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [DeepSeek-OCR 2](deepseek-ocr-2.md), [OvisOCR2](ovisocr2.md), [Infinity-Parser2](infinity-parser2.md), and [Multimodal OCR](multimodal-ocr.md) as architectural exemplars.
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
[^infinity-parser-report]: Wang et al., *Infinity-Parser*, local source at [main.tex](../raw/2506.03197_InfinityParser/main.tex).
[^rex-omni-report]: Sun et al., *Detect Anything via Next Point Prediction*, local source at [main.tex](../raw/2510.12798_Detect%20Anything%20via%20Next%20Point%20Prediction/main.tex).
[^lightonocr-report]: LightOnOCR authors, local source at [templateArxiv.tex](../raw/2601.14251_LightOnOCR/templateArxiv.tex).
[^typhoonocr-report]: Typhoon OCR authors, local source at [main.tex](../raw/2601.14722_TyphoonOCR/main.tex).
[^qianfan-ocr-report]: Qianfan-OCR authors, local source at [qianfan_ocr_report.tex](../raw/2603.13398_Qianfan-OCR/qianfan_ocr_report.tex).
[^monkeyocrv2-report]: MonkeyOCRv2 authors, local source at [monkeyocr.tex](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex).
[^chandra-ocr-2-card]: Datalab, local [Chandra OCR 2 model card](../raw/chandra-ocr-2.md).
[^dots-ocr-card]: rednote-hilab, local [dots.ocr model card](../raw/dots.ocr.md).
[^granite-docling-card]: IBM, local [Granite Docling 258M model card](../raw/granite-docling-258m.md).
[^hunyuanocr-card]: Tencent Hunyuan, local [HunyuanOCR-1.5 model card](../raw/HunyuanOCR-1.5.md).
[^mineru2-5-card]: OpenDataLab, local [MinerU2.5 model card](../raw/MinerU2.5-2509-1.2B.md).
[^mineru2-5-pro-card]: OpenDataLab, local [MinerU2.5-Pro model card](../raw/MinerU2.5-Pro-2604-1.2B.md).
[^nanonets-ocr2-card]: Nanonets, local [Nanonets-OCR2 model card](../raw/Nanonets-OCR2.md).
[^nemotron-parse-card]: NVIDIA, local [Nemotron Parse v1.1 model card](../raw/NVIDIA-Nemotron-Parse-v1.1.md).
[^olmocr2-card]: Allen Institute for AI, local [olmOCR-2-7B-1025 model card](../raw/olmOCR-2-7B-1025.md).
[^rolmocr-card]: Reducto AI, local [RolmOCR model card](../raw/RolmOCR.md).
[^surya-ocr-2-card]: Datalab, local [Surya OCR 2 model card](../raw/surya-ocr-2.md).
