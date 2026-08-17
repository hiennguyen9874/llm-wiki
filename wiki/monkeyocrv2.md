---
type: Model Family
title: MonkeyOCRv2
description: MonkeyOCRv2 is a document-native visual encoder family pretrained with image-to-text generation and pixel-level reconstruction for transfer across document-AI tasks.
tags: [vision-encoder, document-ai, ocr, pretraining, multilingual]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:39:23Z }
sources:
  - id: monkeyocrv2-paper
    resource: ../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex
    title: "MonkeyOCRv2: A Visual-Text Foundation Model for Document AI"
---

# MonkeyOCRv2

MonkeyOCRv2 is a family of document-image visual encoders trained from scratch on [MonkeyDoc v2](monkeydoc-v2.md). Its pretraining jointly autoregressively generates depicted text and reconstructs input pixels, aiming to retain character strokes, glyph detail, and layout information that natural-image encoders may discard.[^monkeyocrv2-paper]

## Pretraining and variants

An encoder produces visual tokens for a text decoder and a vision decoder. The loss combines autoregressive text cross-entropy with pixel reconstruction; standard reported results use MSE reconstruction. A separate document-understanding variant also matches soft edges and distance-to-edge maps. The authors describe this as encouraging visual grounding, but the objectives alone do not establish that causal mechanism.[^monkeyocrv2-paper]

The family comprises ViT-Small **S** (28M parameters), ViT-Base **B** (113M), and multi-scale ViTAEv2-Small **AS** (21M). S and B use 14-pixel patches; AS uses 16-pixel patches and is the stated choice for resolution-sensitive detection, segmentation, and tampering localization. All use dynamic-resolution training; only the encoder transfers downstream, with the pretraining decoders discarded.[^monkeyocrv2-paper]

## Parsing system and reported results

MonkeyOCRv2-Parsing pairs a frozen S or B encoder with an MLP projector and Qwen3-0.6B. It autoregressively predicts element categories and coordinates in reading order, crops the predicted elements for content recognition, then assembles the results. The authors train the projector alone, then jointly train projector and language model, keeping the encoder frozen.[^monkeyocrv2-paper]

All performance values below are author-reported, not independently reproduced:[^monkeyocrv2-paper]

- **MDPBench:** B-Parsing reports **83.3** overall, versus the table's 80.5 for dots.mocr and 75.0 for PaddleOCR-VL-1.6. Its 0.1B encoder is about 11 times smaller than dots.mocr's stated 1.2B encoder; the table is a cross-system comparison, not an encoder-controlled attribution.
- **OmniDocBench 1.6:** B-Parsing reports **91.57** overall without unfreezing the encoder or task-specific post-training. The same table reports higher scores for specialized systems including PaddleOCR-VL-1.6 (96.33), and the paper explicitly warns that their differing pipelines prevent encoder-level attribution.
- **Controlled document understanding:** with a fixed Qwen3-1.7B decoder and frozen encoders, B with edge- and distance-aware reconstruction reports a mean **57.2** across eight document-VQA benchmarks. The source reports 50.7 for S without reconstruction, 51.7 for S with MSE, and 55.9 for S with the structure-aware loss; this is the paper's controlled evidence for its encoder objective.
- **Faithfulness probes:** at long-side resolution 448, S-Parsing with reconstruction reports 72.1% scrambled-text recognition and a 15.3-point semantic--scrambled gap, versus 55.4% and 29.3 points without reconstruction. On CHAOS-Bench, B-Parsing reports 17.9 page-average recall of perturbed words. These are pipeline-level, distribution-shifting probes, not complete measures of hallucination or encoder-only visual fidelity.

## Trust limits

- The local bundle contains an author manuscript, bibliography, figure PDFs, and appendix example PDFs, but no weights, training/evaluation code, prompts, outputs, data records, full hyperparameter configurations, or benchmark implementations. Model behavior and reported results cannot be independently reproduced from it.[^monkeyocrv2-paper]
- The paper compares systems with different data, post-training, layout modules, and inference pipelines. Its cross-system tables do not establish a general model ranking or isolate the visual encoder except for the stated controlled document-understanding experiment.[^monkeyocrv2-paper]
- The semantic--scrambled gap is expressly an operational proxy: scrambling is out of distribution and can interact with tokenization and decoding. It is not a complete hallucination or language-prior measurement.[^monkeyocrv2-paper]

## Relationships

- **Uses:** [MonkeyDoc v2](monkeydoc-v2.md) as its multilingual, multi-type pretraining corpus.[^monkeyocrv2-paper]
- **Evaluated on:** [MDPBench](mdpbench.md) for multilingual digital-born and photographed document parsing.[^monkeyocrv2-paper]
- **Compared with:** [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), [Multimodal OCR](multimodal-ocr.md)'s dots.mocr, and [DeepSeek-OCR](deepseek-ocr.md) in source-reported cross-system tables; matching evaluation conditions are required for a causal comparison.[^monkeyocrv2-paper]

[^monkeyocrv2-paper]: Liu et al., *MonkeyOCRv2: A Visual-Text Foundation Model for Document AI*, local LaTeX source at [monkeyocr.tex](../raw/2607.11562_MonkeyOCRv2/monkeyocr.tex), including visually reviewed [model overview](../raw/2607.11562_MonkeyOCRv2/images/figfig.pdf), [pretraining overview](../raw/2607.11562_MonkeyOCRv2/images/pretrain.pdf), [data distribution](../raw/2607.11562_MonkeyOCRv2/images/data_dis.pdf), [MDPBench comparison](../raw/2607.11562_MonkeyOCRv2/images/fig1_mdpbench_bubble_svg-raw.pdf), and [reconstruction analysis](../raw/2607.11562_MonkeyOCRv2/images/resolution.pdf) (accessed 2026-08-17).
