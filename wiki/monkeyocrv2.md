---
type: Model Family
title: MonkeyOCRv2
description: MonkeyOCRv2 is a document-native visual encoder family pretrained with image-to-text generation and pixel-level reconstruction for transfer across document-AI tasks.
tags: [vision-encoder, document-ai, ocr, pretraining, multilingual]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:32:14Z }
stale_after: 2027-01-25
sources:
  - id: monkeyocrv2-paper
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI"
  - id: monkeyocrv2-model-card
    resource: ../raw/zenosai-MonkeyOCRv2-B-Parsing.md
    kind: model-card
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI (model card and repository README)"
  - id: hunyuanocr-repo-readme
    resource: ../raw/HunyuanOCR-github.md
    kind: code
    title: "HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better (GitHub repository README)"
---

# MonkeyOCRv2

MonkeyOCRv2 is a family of document-image visual encoders trained from scratch on [MonkeyDoc v2](monkeydoc-v2.md). Its pretraining jointly autoregressively generates depicted text and reconstructs input pixels, aiming to retain character strokes, glyph detail, and layout information that natural-image encoders may discard.[^monkeyocrv2-paper]

## Pretraining and variants

An encoder produces visual tokens for a text decoder and a vision decoder. The loss combines autoregressive text cross-entropy with pixel reconstruction; standard reported results use MSE reconstruction. A separate document-understanding variant also matches soft edges and distance-to-edge maps. The authors describe this as encouraging visual grounding, but the objectives alone do not establish that causal mechanism.[^monkeyocrv2-paper]

The family comprises ViT-Small **S** (28M parameters), ViT-Base **B** (113M), and multi-scale ViTAEv2-Small **AS** (21M). S and B use 14-pixel patches; AS uses 16-pixel patches and is the stated choice for resolution-sensitive detection, segmentation, and tampering localization. All use dynamic-resolution training; only the encoder transfers downstream, with the pretraining decoders discarded.[^monkeyocrv2-paper]

## Parsing system and reported results

MonkeyOCRv2-Parsing pairs a frozen S or B encoder with an MLP projector and Qwen3-0.6B. It autoregressively predicts element categories and coordinates in reading order, crops the predicted elements for content recognition, then assembles the results. The authors train the projector alone, then jointly train projector and language model, keeping the encoder frozen.[^monkeyocrv2-paper]

All performance values below are author-reported, not independently reproduced:[^monkeyocrv2-paper]

- **MDPBench:** B-Parsing reports **83.3** overall, versus the table's 80.5 for dots.mocr and 75.0 for PaddleOCR-VL-1.6. The card versions of the same table also publish S-Parsing at **82.5**, and the release announcement claims first place among evaluated open-source models. The lead is not uniform: B-Parsing trails dots.mocr on traditional Chinese (75.3 versus 79.6) and Japanese (71.9 versus 75.0), trails PaddleOCR-VL-1.5 on simplified Chinese (83.6 versus 84.8), and S-Parsing scores higher than B on simplified Chinese (84.4) and Spanish (76.8) with a 28M encoder.[^monkeyocrv2-model-card][^monkeyocrv2-paper] Its 0.1B encoder is about 11 times smaller than dots.mocr's stated 1.2B encoder; the table is a cross-system comparison, not an encoder-controlled attribution.
- **OmniDocBench 1.6:** B-Parsing reports **91.57** overall without unfreezing the encoder or task-specific post-training. The same table reports higher scores for specialized systems including PaddleOCR-VL-1.6 (96.33), and the paper explicitly warns that their differing pipelines prevent encoder-level attribution.
- **Controlled document understanding:** with a fixed Qwen3-1.7B decoder and frozen encoders, B with edge- and distance-aware reconstruction reports a mean **57.2** across eight document-VQA benchmarks. The source reports 50.7 for S without reconstruction, 51.7 for S with MSE, and 55.9 for S with the structure-aware loss; this is the paper's controlled evidence for its encoder objective.
- **Faithfulness probes:** at long-side resolution 448, S-Parsing with reconstruction reports 72.1% scrambled-text recognition and a 15.3-point semantic--scrambled gap, versus 55.4% and 29.3 points without reconstruction. On CHAOS-Bench, B-Parsing reports 17.9 page-average recall of perturbed words; the benchmark is the HunyuanOCR team's character-level hallucination probe, which injects character-level corruptions into academic-paper images, and neither its scoring rules nor that figure is present in this bundle.[^monkeyocrv2-paper][^hunyuanocr-repo-readme] These are pipeline-level, distribution-shifting probes, not complete measures of hallucination or encoder-only visual fidelity.

## Encoder transfer across task heads

The model card extends the controlled encoder comparisons beyond parsing to six task families, each keeping its own recognition or segmentation head and training recipe: text recognition under the OpenOCR/SVTRv2 protocol, formula recognition on OmniDocBench 1.6, MathWriting, and UniMER-Test, text detection under MMOCR and DPText-DETR, tampering detection on DocTamper, and overlapping-text segmentation on MOT. Swapping only the backbone is a closer approximation of an encoder-controlled comparison than the paper's pipeline-level tables, and the reported swaps favor the MonkeyOCRv2 encoders in every task where the card publishes numbers:[^monkeyocrv2-model-card]

- **Recognition:** PARSeq with S reports **84.3** overall in the card's recognition table (81.5 on occlusion scene text) versus 82.2 for PARSeq with a ViT backbone; CRNN with S reaches **67.3** versus 58.7 for CRNN with ResNet.[^monkeyocrv2-model-card]
- **Formula:** UniMERNet-T with S reaches the table's best overall CDM **90.9** and ExpRate **66.4**, against 89.4 and 61.8 for the Swin variant, though the larger UniMERNet-B keeps a higher CPE ExpRate (80.5 versus 79.2).[^monkeyocrv2-model-card]
- **Tampering:** FFDN with AS reaches **78.2** IoU and **87.5** F versus 70.7 and 82.7 for FFDN on a ViTAEv2 backbone, while DTD retains a higher SCD IoU (68.0 versus 67.2).[^monkeyocrv2-model-card]
- **Overlapping-text segmentation:** MOTS with AS reaches **76.9** text mIoU versus 72.6 for MOTS on ResNet, and Mask2Former rises from 70.3 to 76.6.[^monkeyocrv2-model-card]
- **Document understanding:** with a fixed Qwen3 decoder, B scores **57.2** overall against 44.0 for OpenVision-B, 37.5 for RADIOv2.5-B, 24.9 for SigLIP2-B, 16.1 for DINOv3-B, and 16.0 for CLIP-B at comparable encoder sizes.[^monkeyocrv2-model-card]
- **Detection:** the card reports detection on Total-Text, CTW1500, ICDAR2015, and ArT as an image only, with no numbers in text, so no detection comparison is recorded here.[^monkeyocrv2-model-card]

These remain author-run, single-value comparisons with no seeds, variance, or per-backbone hyperparameter disclosure; the vision-encoder rows also inherit whatever decoder pairing the paper used. Transfer is therefore reported and internally consistent, not independently reproduced.[^monkeyocrv2-model-card]

## Released checkpoints and license

Each variant ships as its own Hugging Face and ModelScope repository, with AS reserved for detection and segmentation and DFlash available for B-Parsing only. The release is Apache License 2.0, stated as free for research and commercial use, and the repository documents CLI, vLLM, CPU, and third-party deployment paths on [MonkeyOCRv2 serving and deployment stack](monkeyocrv2-serving-stack.md).[^monkeyocrv2-model-card]

## Trust limits

- The local bundle contains an author manuscript, bibliography, figure PDFs, and appendix example PDFs, but no weights, training/evaluation code, prompts, outputs, data records, full hyperparameter configurations, or benchmark implementations. Model behavior and reported results cannot be independently reproduced from it.[^monkeyocrv2-paper]
- The paper compares systems with different data, post-training, layout modules, and inference pipelines. Its cross-system tables do not establish a general model ranking or isolate the visual encoder except for the stated controlled document-understanding experiment.[^monkeyocrv2-paper]
- The semantic--scrambled gap is expressly an operational proxy: scrambling is out of distribution and can interact with tokenization and decoding. It is not a complete hallucination or language-prior measurement.[^monkeyocrv2-paper]

## Relationships

- **Deployed by:** [MonkeyOCRv2 serving and deployment stack](monkeyocrv2-serving-stack.md) for the vLLM, DFlash, CPU, and API paths.[^monkeyocrv2-model-card]
- **Uses:** [MonkeyDoc v2](monkeydoc-v2.md) as its multilingual, multi-type pretraining corpus.[^monkeyocrv2-paper]
- **Evaluated on:** [MDPBench](mdpbench.md) for multilingual digital-born and photographed document parsing.[^monkeyocrv2-paper]
- **Compared with:** [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [Multimodal OCR](multimodal-ocr.md)'s dots.mocr, and [DeepSeek-OCR](deepseek-ocr.md) in source-reported cross-system tables; matching evaluation conditions are required for a causal comparison.[^monkeyocrv2-paper]

[^monkeyocrv2-paper]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, local LaTeX source at [monkeyocr.tex](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex), including visually reviewed [model overview](../raw/2607.11562_MonkeyOCRv2/images/figfig.pdf), [pretraining overview](../raw/2607.11562_MonkeyOCRv2/images/pretrain.pdf), [data distribution](../raw/2607.11562_MonkeyOCRv2/images/data_dis.pdf), [MDPBench comparison](../raw/2607.11562_MonkeyOCRv2/images/fig1_mdpbench_bubble_svg-raw.pdf), and [reconstruction analysis](../raw/2607.11562_MonkeyOCRv2/images/resolution.pdf) (accessed 2026-08-17).
[^monkeyocrv2-model-card]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, model card and repository README captured at [zenosai-MonkeyOCRv2-B-Parsing.md](../raw/zenosai-MonkeyOCRv2-B-Parsing.md), locators: § News entry dated 2026.07.22; § Model Zoo tables 1–3; § Evaluation Results tables 1, 2, 4, 5, 6, and 7; § Copyright (accessed 2026-10-25).
[^hunyuanocr-repo-readme]: Tencent Hunyuan, *HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better* (GitHub repository README), local capture at [HunyuanOCR-github.md](../raw/HunyuanOCR-github.md), locator: `News` entry dated 2026/07/13 (accessed 2026-10-25).
