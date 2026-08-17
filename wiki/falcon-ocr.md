---
type: Model System
title: FalconOCR
description: FalconOCR is a 300M two-stage English document-parsing system that uses PP-DocLayoutV3 regions and an early-fusion autoregressive recognizer for text, LaTex, and HTML tables.
tags: [ocr, document-parsing, vision-language-models, layout-analysis, table-recognition, formula-recognition]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:03:48Z }
sources:
  - id: falcon-perception-report
    resource: ../raw/2603.27365_FalconPerception/main.tex
    title: Falcon Perception
  - id: falcon-ocr-model-card
    resource: ../raw/FalconOCR.md
    title: Falcon OCR model card
---

# FalconOCR

FalconOCR is an English-focused, 300M-parameter document-recognition model built from Falcon Perception's early-fusion Transformer. It uses [PP-DocLayoutV3](pp-doclayoutv3.md) to detect page regions, then recognizes each crop as text, LaTeX, or HTML table markup before assembling outputs in layout reading order.[^falcon-perception-report]

## Pipeline and model

PP-DocLayoutV3 detects text blocks, tables, formulas, figures, headers, footers, and captions as axis-aligned boxes. FalconOCR receives each crop plus an element-type prompt, and its outputs are reassembled by the detector's reading order into Markdown. The layout detector can be skipped for latency-sensitive, sparse pages, at a reported performance cost on dense documents.[^falcon-perception-report]

The recognizer is a 22-layer, 300M early-fusion Transformer, initialized from scratch rather than from the perception model's DINOv3/SigLIP2 distillation. It uses bidirectional image attention and causal text attention, native-aspect-ratio cropped inputs with width capped at 1,024 pixels, packed sequences, and next-token cross-entropy without CTC or other OCR-specific losses.[^falcon-perception-report]

Training covers English document text, formulas, tables, handwriting, scene text, and synthetic rendered LaTex/HTML. The described schedule has 250,000 constant-rate pretraining iterations followed by 20,000 cosine-decay steps.[^falcon-perception-report]

## Availability and operation

The model card identifies the released Transformers model as `tiiuae/Falcon-OCR` (Apache-2.0) and requires PyTorch 2.5 or newer for FlexAttention; its first request may incur `torch.compile` kernel-compilation overhead. Its `generate` interface accepts one PIL image or a list and returns one string per image. Prompts select plain/text, formula (LaTeX), table (HTML), and layout categories including captions, headers, footers, list items, section headers, and titles.[^falcon-ocr-model-card]

`generate_with_layout` lazily loads PP-DocLayoutV3 on the OCR model's GPU, detects page regions, and returns category, original-pixel bounding box, detection score, and extracted text in reading order. The card recommends direct whole-image OCR for simple or sparse pages and layout-plus-OCR for dense, heterogeneous pages.[^falcon-ocr-model-card]

The supplied Docker image exposes vLLM's OpenAI-compatible API on port 8000 and a page-parsing service on port 5002. The latter accepts image or PDF uploads and can return per-region JSON plus assembled Markdown; two GPUs avoid layout/OCR contention, while a single-GPU deployment requires reducing vLLM memory allocation and concurrency.[^falcon-ocr-model-card]

## Reported evaluation

After excluding non-English documents, the authors report 80.3% average accuracy on olmOCR and 88.64 overall on OmniDocBench v1.5. On olmOCR, reported strengths are multi-column layouts (87.1%) and tables (90.3%), while OldScan is 43.5% and TinyText 78.5%. On OmniDocBench, it reports edit distance 0.055, formula CDM 86.8, and table TEDS 84.6.[^falcon-perception-report]

## Contradictions

- The report's deployment section reports approximately 3,000 output tokens/s on one GPU, while its efficiency discussion reports about 6,000 tokens/s and 2.8 images/s. The model card reports 5,825 tokens/s and 2.9 images/s for layout-plus-OCR on one A100-80GB under high concurrency. It does not supply conditions that reconcile the report's 3,000-token figure with the other measurements.[^falcon-perception-report][^falcon-ocr-model-card]

## Trust limits

- The model card names public model, source-code, and container locations, but the local sources do not preserve their versions, weights, training data, layout-detector configuration, output normalization rules, or evaluation implementation. Results and throughput remain author-reported and cannot be independently reproduced from this bundle.[^falcon-perception-report][^falcon-ocr-model-card]
- End-to-end accuracy depends on PP-DocLayoutV3 boxes and reading order as well as recognizer outputs; the supplied results do not isolate those contributions.[^falcon-perception-report]
- The reported OmniDocBench discussion attributes some penalties to element matching and noncanonical HTML/LaTex representations. That is an author interpretation, not an independently verified measurement of evaluator error.[^falcon-perception-report]

## Relationships

- **Uses:** [PP-DocLayoutV3](pp-doclayoutv3.md) for element detection and reading order before crop-level recognition.[^falcon-perception-report]
- **Shares architecture with:** [Falcon Perception](falcon-perception.md), but differs in scratch initialization, OCR-only loss, and a modular document pipeline.[^falcon-perception-report]
- **Compared with:** [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) is a larger two-stage document parser reported in the same olmOCR and OmniDocBench comparison tables.[^falcon-perception-report]

[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local LaTeX source at [main.tex](../raw/2603.27365_FalconPerception/main.tex), especially `sections/ocr.tex` (accessed 2026-08-17).
[^falcon-ocr-model-card]: Falcon Vision Team, *Falcon OCR model card*, local Markdown source at [FalconOCR.md](../raw/FalconOCR.md) (accessed 2026-08-17).