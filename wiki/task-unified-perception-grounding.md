---
type: Concept
title: "Task: Unified perception and grounding"
description: Unified perception and grounding groups models that cast detection, grounding, OCR, and keypoints as quantized point-sequence generation for multi-task vision.
tags: [task, perception, grounding, detection, keypoints, ocr]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-10-30T02:16:13Z }
sources:
  - id: rex-omni-report
    resource: "../raw/2510.12798_Detect Anything via Next Point Prediction/main.tex"
    title: Detect Anything via Next Point Prediction
  - id: falcon-perception-report
    resource: ../raw/2603.27365_FalconPerception/main.tex
    title: Falcon Perception
  - id: current-ocr-approaches
    resource: ../wiki/current-ocr-approaches.md
    title: Current OCR approaches
  - id: groundanything-card
    resource: ../raw/GroundingPI-GroundAnything.md
    kind: model-card
    title: GroundAnything (DLM) model card
  - id: ovisocr3
    resource: ../wiki/ovisocr3.md
    title: OvisOCR3
  - id: lightonocr-3
    resource: ../wiki/lightonocr-3.md
    title: LightOnOCR-3
  - id: surya-25-card
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
---

# Task: Unified perception and grounding

Unified perception and grounding reformulates classical vision tasks — object detection, referring-expression grounding/segmentation, OCR polygon prediction, and keypoint estimation — as a single next-point prediction problem with quantized coordinates, refined by geometry-aware GRPO.[^rex-omni-report]

## Models in this task

- [Rex-Omni](rex-omni.md) — 3B VLM, unified detection/grounding/OCR/keypoint via point sequences + geometry-aware GRPO; OCR treated as polygon generation[^rex-omni-report]
- [Falcon Perception](falcon-perception.md) — 600M early-fusion dense Transformer emitting instance geometry autoregressively with specialized heads for high-resolution masks[^falcon-perception-report]
- [FalconOCR](falcon-ocr.md) — downstream document system built on Falcon Perception family (crossover to [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md))
- [GroundAnything](groundanything.md) — 4B family pairing an autoregressive and a blockwise-diffusion checkpoint over one backbone, using the quantized GAM coordinate protocol for boxes, points, OCR text boxes, document layout, and GUI targets
- [MonkeyOCRv2](monkeyocrv2.md) — document-native visual encoder family pretrained with image-to-text generation and pixel reconstruction; transferable to detection/grounding/OCR tasks
- [PBench](pbench.md) — benchmark separating five prompt capabilities + crowded long-context stress test for this task family

## Task characteristics

- **Input:** image + prompt specifying task (e.g., “detect,” “ground phrase X,” “OCR,” “keypoints”).
- **Output:** sequence of quantized points/polygons/masks; geometry metrics (mIoU, L1 coordinate loss) plus task-specific scores.
- **Strengths:** one model serves detection, interaction, and OCR; shared coordinate vocabulary enables multi-task transfer.
- **Decoding axis:** this task was originally defined by autoregressive point-sequence generation, but it is not inherently left-to-right. [GroundAnything](groundanything.md) argues the coordinate dependencies do not imply a generation order and adds entropy-guided blockwise diffusion plus optional self-speculative decoding over the same spatial-token interface.[^groundanything-card]
- **Limits:** not a replacement for full document-to-Markdown pipelines; evaluated on referring-expression and detection benchmarks rather than OmniDocBench document parsing.[^current-ocr-approaches]
- **Boundary with document parsers:** normalized coordinate output alone does not place a model in this task. [OvisOCR3](ovisocr3.md) exposes word-level text-spotting and reference-grounding prompts beside its parsing modes, and [LightOnOCR-3](lightonocr-3.md) adds a `grounding` mode that prefixes every page block with a type label and box; both quantize boxes to 0–1000 integers, yet return prompt-selected document structure rather than one point sequence per query, so they remain document-centric. [Surya OCR 2.5](surya-ocr-2-5.md) likewise emits 0–1000 normalized block coordinates within its document OCR output, but its card describes document layout and transcription rather than a general-purpose query-grounding interface. These boundary classifications are synthesis, not claims of the cards.[^ovisocr3][^lightonocr-3][^surya-25-card]

## Relationships

- **Contrasts with:** document-centric tasks ([Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md), [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md)) where structure and reading order dominate
- **Related to:** [Task: Layout analysis and reading order](task-layout-analysis-reading-order.md) via shared localization capability
- **Benchmarked by:** [PBench](pbench.md)
- **Decoding variant:** [GroundAnything decoding and serving](groundanything-decoding-and-serving.md) records the parallel and speculative decoder mechanics for this task family.
- **Adjacent from the document side:** [OvisOCR3](ovisocr3.md) and [LightOnOCR-3](lightonocr-3.md) add on-demand box output inside page-to-Markdown generation, the reverse direction of [Rex-Omni](rex-omni.md) and [GroundAnything](groundanything.md), which add document tasks to a perception interface.[^ovisocr3][^lightonocr-3]

[^surya-25-card]: Datalab, [Surya OCR 2.5 model card](../raw/surya-ocr-2.5-hf.md), §§ Usage, OCR (text recognition), Output format and Limitations (inspected 2026-10-30).
[^rex-omni-report]: Sun et al., *Detect Anything via Next Point Prediction*, local LaTeX source at [main.tex](../raw/2510.12798_Detect%20Anything%20via%20Next%20Point%20Prediction/main.tex) (accessed 2026-08-22).
[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local LaTeX source at [main.tex](../raw/2603.27365_FalconPerception/main.tex) (accessed 2026-08-22).
[^current-ocr-approaches]: Compiled synthesis in this wiki: [Current OCR approaches](current-ocr-approaches.md), § Adjacent unified perception (accessed 2026-10-25).
[^groundanything-card]: GroundingPI, *GroundAnything (DLM) model card*, local capture at [GroundingPI-GroundAnything.md](../raw/GroundingPI-GroundAnything.md), § Model Overview and § Model Architecture (accessed 2026-10-25).
[^ovisocr3]: Compiled synthesis in this wiki: [OvisOCR3](ovisocr3.md), § Document parsing and § General OCR (accessed 2026-10-25).
[^lightonocr-3]: Compiled synthesis in this wiki: [LightOnOCR-3](lightonocr-3.md), § Prompt modes and § Grounding output contract (accessed 2026-10-25).
