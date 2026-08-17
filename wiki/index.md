---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [Chandra OCR](chandra-ocr.md) — Chandra OCR is Datalab's earlier document-OCR model for converting images and PDFs to Markdown, HTML, or JSON with layout information.
- [Chandra OCR 2](chandra-ocr-2.md) — Chandra OCR 2 is a Datalab document-OCR model that converts images and PDFs to Markdown, HTML, or JSON with layout information.
- [Current OCR approaches](current-ocr-approaches.md) — Current document OCR spans lightweight detector–recognizer pipelines, modular layout-first systems, end-to-end generative VLMs, and emerging data-, decoding-, and evaluation-centered approaches.
- [DeepSeek-OCR](deepseek-ocr.md) — DeepSeek-OCR is an end-to-end OCR VLM whose DeepEncoder compresses high-resolution visual features before a 3B MoE decoder generates text or structured outputs.
- [DeepSeek-OCR 2](deepseek-ocr-2.md) — DeepSeek-OCR 2 is an end-to-end document OCR VLM that uses DeepEncoder V2 to causally reorder compressed visual tokens before a 3B MoE decoder.
- [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md) — Detector–recognizer OCR benchmarks catalog the retained classical OCR model families, comparison-only baselines, datasets, metrics, and author-reported results without treating incompatible protocols as one leaderboard.
- [Document-parser data flywheel](document-parser-data-flywheel.md) — The document-parser data flywheel iteratively converts model weaknesses into disjoint mined, pseudo-labeled, and synthesized training data.
- [dots.ocr](dots-ocr.md) — dots.ocr is a 1.7B multilingual document-parsing vision-language model that uses prompts to produce layout detection, content recognition, and reading-order outputs.
- [DOM-based document synthesis](dom-based-document-synthesis.md) — DOM-based document synthesis renders a typed logical document tree into pages and derives aligned structural labels from the laid-out DOM.
- [Falcon Perception](falcon-perception.md) — Falcon Perception is a 600M early-fusion dense Transformer that autoregressively emits instance geometry and uses specialized heads for parallel high-resolution masks.
- [FalconOCR](falcon-ocr.md) — FalconOCR is a 300M two-stage English document-parsing system that uses PP-DocLayoutV3 regions and an early-fusion autoregressive recognizer for text, LaTex, and HTML tables.
- [FireRed-OCR](firered-ocr.md) — FireRed-OCR is a 2B end-to-end document-parsing VLM that adapts Qwen3-VL through geometry- and semantics-balanced data, structured SFT, and format-constrained GRPO.
- [GLM-OCR](glm-ocr.md) — GLM-OCR is a 0.9B two-stage document OCR system that combines PP-DocLayoutV3 region parsing with a CogViT-GLM recognizer using shared-parameter multi-token prediction.
- [Granite Docling 258M](granite-docling-258m.md) — Granite Docling 258M is IBM's 258M-parameter document-conversion VLM, integrated with Docling to produce structured document outputs.
- [HunyuanOCR-1.5](hunyuanocr-1.5.md) — HunyuanOCR-1.5 is a lightweight end-to-end OCR VLM with DFlash speculative decoding, multiple inference stacks, and an agentic data-construction workflow.
- [Infinity-Doc-400K](infinity-doc-400k.md) — Infinity-Doc-400K pairs rendered document pages with structured targets using synthetic HTML rendering and cross-validated pseudo-labeling of real documents.
- [Infinity-Doc2-5M](infinity-doc2-5m.md) — Infinity-Doc2-5M is an approximately 5-million-sample Chinese-and-English multi-task corpus for document structure, element parsing, and document reasoning.
- [Infinity-Parser2](infinity-parser2.md) — Infinity-Parser2 is a Qwen3.5-based end-to-end document parser trained with multi-task SFT and GRPO using task-native verifiable rewards.
- [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) — Layout-first modular OCR benchmarks catalog retained models, datasets, metrics, author-reported results, protocol differences, and evidence limits for systems that localize document regions before specialized recognition.
- [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) — LayoutRL trains an end-to-end document-image parser with rewards for content similarity, segment count, and reading order; Infinity-Parser is its Qwen2.5-VL-7B implementation.
- [LightOnOCR](lightonocr.md) — LightOnOCR-2-1B is a 1B end-to-end document-OCR VLM that combines a native-resolution ViT with a Qwen3 decoder and optionally emits image bounding boxes.
- [MDPBench](mdpbench.md) — MDPBench is an author-constructed benchmark for multilingual document parsing on digital-born and photographed pages under varied real-world capture conditions.
- [MonkeyDoc v2](monkeydoc-v2.md) — MonkeyDoc v2 is a 113-million-sample, 17-language document-image corpus used to pretrain MonkeyOCRv2 for page-level and cropped-element document tasks.
- [MonkeyOCRv2](monkeyocrv2.md) — MonkeyOCRv2 is a document-native visual encoder family pretrained with image-to-text generation and pixel-level reconstruction for transfer across document-AI tasks.
- [MinerU-Diffusion](mineru-diffusion.md) — MinerU-Diffusion is a 2.5B document-OCR model that replaces autoregressive generation with block-level parallel diffusion decoding.
- [MinerU2.5](mineru2-5.md) — MinerU2.5 is a 1.2B two-stage vision-language document parser that performs low-resolution global layout analysis before native-resolution crop recognition.
- [MinerU2.5-Pro](mineru2-5-pro.md) — MinerU2.5-Pro is a 1.2B document-parsing vision-language model whose authors attribute improvements over MinerU2.5 to scaled and refined training data.
- [Multimodal OCR](multimodal-ocr.md) — Multimodal OCR (MOCR) is a 3B document-parsing VLM formulation that produces ordered text, table, formula, and SVG representations for information-bearing page elements.
- [Nanonets-OCR2](nanonets-ocr2.md) — Nanonets-OCR2 is a Nanonets family of multilingual image-to-Markdown document OCR models with structured outputs for equations, tables, images, signatures, watermarks, checkboxes, and VQA.
- [Nemotron OCR v2](nemotron-ocr-v2.md) — Nemotron OCR v2 is NVIDIA's detector–recognizer OCR system with a relational layout model, offered in English word-level and six-language line-level variants.
- [NVIDIA Nemotron Parse v1.1](nemotron-parse-v1-1.md) — NVIDIA Nemotron Parse v1.1 is a sub-1B vision-encoder–decoder document parser that emits reading-order text, element classes, and bounding boxes from an image.
- [OCR Arena](ocr-arena.md) — OCR Arena is a pairwise LLM-as-judge protocol for Markdown OCR that uses position-swapped comparisons, ties inconsistent judgments, and aggregates results with bootstrapped Elo ratings.
- [olmOCR-2-7B-1025](olmocr-2-7b-1025.md) — olmOCR-2-7B-1025 is a 7B Qwen2.5-VL-based document OCR model fine-tuned with supervised and GRPO training for structured PDF-page extraction.
- [OvisOCR2](ovisocr2.md) — OvisOCR2 is a 0.8B end-to-end document parser that generates page-level Markdown after SFT, 4B-teacher RL, on-policy distillation, and model fusion.
- [Optical Context Compression](optical-context-compression.md) — Optical context compression is the proposal to render text into images and retain compressed vision tokens, trading fidelity for a smaller long-context representation.
- [PaddleOCR 3.0](paddleocr-3.md) — PaddleOCR 3.0 is an open-source document-AI toolkit that unifies model training, layered inference, heterogeneous deployment, and MCP access around three OCR and document-understanding pipelines.
- [PaddleOCR-VL](paddleocr-vl.md) — PaddleOCR-VL is a two-stage document parser that combines PP-DocLayoutV2 with a 0.9B dynamic-resolution VLM for multilingual text, table, formula, and chart conversion.
- [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) — PaddleOCR-VL-1.5 is a 0.9B two-stage document parser that adds distortion-robust polygonal layout analysis, text spotting, seal recognition, and long-document post-processing to PaddleOCR-VL.
- [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) — PaddleOCR-VL-1.6 is a 0.9B two-stage document parser that targets residual weak regions through data mining, expert-guided label refinement, and staged CPT–SFT–GRPO post-training.
- [PBench](pbench.md) — PBench is an internal referring-expression segmentation benchmark that separates five prompt capabilities and a crowded long-context stress test.
- [PP-ChatOCRv4](pp-chatocrv4.md) — PP-ChatOCRv4 extracts key information from documents by fusing retrieval-augmented OCR text answers with direct PP-DocBee2 vision-language answers.
- [PP-DocLayoutV2](pp-doclayoutv2.md) — PP-DocLayoutV2 is an RT-DETR-based document-layout model with a six-layer relation-aware pointer network that predicts reading order from detected elements.
- [PP-DocLayoutV3](pp-doclayoutv3.md) — PP-DocLayoutV3 jointly predicts layout classes, regions, instance masks, and reading order with an RT-DETR-derived Transformer and pairwise precedence ranking.
- [PP-OCRv5](pp-ocrv5.md) — PP-OCRv5 is a 0.07B-parameter OCR pipeline for unified Chinese, Pinyin, English, and Japanese text detection and recognition across server and mobile deployments.
- [PP-OCRv6](pp-ocrv6.md) — PP-OCRv6 is a 1.5M–34.5M-parameter OCR family that uses a shared reparameterizable MetaFormer-style backbone for text detection and recognition.
- [PP-StructureV3](pp-structurev3.md) — PP-StructureV3 is a modular document parser that combines OCR, layout and article-region detection, specialized element recognition, and reading-order reconstruction to produce JSON and Markdown.
- [Qianfan-OCR](qianfan-ocr.md) — Qianfan-OCR is a 4B end-to-end document-intelligence VLM that optionally emits structured layout reasoning before prompt-driven parsing or understanding outputs.
- [Real5-OmniDocBench](real5-omnidocbench.md) — Real5-OmniDocBench is an OmniDocBench v1.5-derived benchmark that applies five physical-document distortion conditions while retaining corresponding ground-truth annotations.
- [Reference Sliding Window Attention](reference-sliding-window-attention.md) — Reference Sliding Window Attention preserves a fixed reference prefix while restricting generated-token attention to a bounded causal window, bounding decode-side KV-cache growth for a fixed prefix.
- [Rex-Omni](rex-omni.md) — Rex-Omni is a 3B vision-language model that unifies detection, grounding, OCR, and keypoint tasks as quantized point-sequence generation refined with geometry-aware GRPO.
- [RolmOCR](rolmocr.md) — RolmOCR is Reducto AI's Apache-2.0 Qwen2.5-VL-7B document-OCR model that omits PDF metadata inputs and trains with rotated pages for off-angle robustness.
- [Surya OCR 2](surya-ocr-2.md) — Surya OCR 2 is a 650M document-OCR system whose shared VLM produces layout, reading order, OCR content, and table-recognition outputs.
- [Typhoon OCR](typhoon-ocr.md) — Typhoon OCR is an open Thai-and-English document-extraction VLM family whose 2B V1.5 revision uses a single image-only prompt to emit Markdown, HTML tables, figure descriptions, equations, and page markers.
- [Unlimited OCR](unlimited-ocr.md) — Unlimited OCR is a 3B-total, 500M-active end-to-end document OCR VLM that uses Reference Sliding Window Attention to bound decode-side KV-cache growth for one-shot multi-page parsing.
