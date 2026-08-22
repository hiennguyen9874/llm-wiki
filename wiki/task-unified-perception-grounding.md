---
type: Concept
title: "Task: Unified perception and grounding"
description: Unified perception and grounding groups models that cast detection, grounding, OCR, and keypoints as quantized point-sequence generation for multi-task vision.
tags: [task, perception, grounding, detection, keypoints, ocr]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00+07:00 }
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
---

# Task: Unified perception and grounding

Unified perception and grounding reformulates classical vision tasks — object detection, referring-expression grounding/segmentation, OCR polygon prediction, and keypoint estimation — as a single next-point prediction problem with quantized coordinates, refined by geometry-aware GRPO.

## Models in this task

- [Rex-Omni](rex-omni.md) — 3B VLM, unified detection/grounding/OCR/keypoint via point sequences + geometry-aware GRPO; OCR treated as polygon generation
- [Falcon Perception](falcon-perception.md) — 600M early-fusion dense Transformer emitting instance geometry autoregressively with specialized heads for high-resolution masks
- [FalconOCR](falcon-ocr.md) — downstream document system built on Falcon Perception family (crossover to [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md))
- [MonkeyOCRv2](monkeyocrv2.md) — document-native visual encoder family pretrained with image-to-text generation and pixel reconstruction; transferable to detection/grounding/OCR tasks
- [PBench](pbench.md) — benchmark separating five prompt capabilities + crowded long-context stress test for this task family

## Task characteristics

- **Input:** image + prompt specifying task (e.g., “detect,” “ground phrase X,” “OCR,” “keypoints”).
- **Output:** sequence of quantized points/polygons/masks; geometry metrics (mIoU, L1 coordinate loss) plus task-specific scores.
- **Strengths:** one model serves detection, interaction, and OCR; shared coordinate vocabulary enables multi-task transfer.
- **Limits:** not a replacement for full document-to-Markdown pipelines; evaluated on referring-expression and detection benchmarks rather than OmniDocBench document parsing.

## Relationships

- **Contrasts with:** document-centric tasks ([Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md), [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md)) where structure and reading order dominate
- **Related to:** [Task: Layout analysis and reading order](task-layout-analysis-reading-order.md) via shared localization capability
- **Benchmarked by:** [PBench](pbench.md)
