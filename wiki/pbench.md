---
type: Benchmark
title: PBench
description: PBench is an internal referring-expression segmentation benchmark that separates five prompt capabilities and a crowded long-context stress test.
tags: [benchmark, visual-grounding, instance-segmentation, ocr, spatial-reasoning, long-context]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:00:00Z }
sources:
  - id: falcon-perception-report
    resource: ../raw/2603.27365_FalconPerception/main.tex
    title: Falcon Perception
---

# PBench

PBench is an internally constructed benchmark for promptable referring-expression segmentation. It labels each sample with one deliberately isolated capability level and adds a separate high-instance-count split, aiming to expose semantic and long-output failures obscured by aggregate referring-benchmark scores.[^falcon-perception-report]

## Capability profile

The five mutually exclusive prompt levels are:

| Level | Primary capability |
| --- | --- |
| 0 | general object classes |
| 1 | attributes, states, subtypes, or components |
| 2 | OCR text as an instance identifier |
| 3 | spatial relationships and layout |
| 4 | relations, interactions, functional links, or comparisons |

Prompts are written to avoid cross-level cues: for example, OCR prompts omit spatial qualifiers, and spatial prompts omit in-image-text disambiguators. The authors report about 5,000 samples across Levels 0–4.[^falcon-perception-report]

The additional Dense split keeps the query semantically simple but varies object count: training-style evaluation reaches 150 instances, while long-context tests reach about 600. It is intended to distinguish failures of semantic grounding from instability in autoregressive generation, including duplicate outputs and absent-object decisions.[^falcon-perception-report]

## Evaluation use and limits

The source reports Macro-F1 by level and dense split. Its Falcon Perception evaluation reports 65.1, 63.6, 38.0, 53.5, 49.1, and 72.6 Macro-F1 for Levels 0–4 and Dense respectively; these are author-reported model results, not benchmark validation.[^falcon-perception-report]

- PBench was made internally by the Falcon Perception team. The bundle supplies neither benchmark instances, masks, annotation protocol beyond the summary, evaluator, nor public split, so independence, label quality, and claimed single-skill separation cannot be verified.[^falcon-perception-report]
- Its comparisons use a segmentation conversion for detection-only models, where their boxes prompt SAM for masks. Results depend on that adaptation and its settings.[^falcon-perception-report]

## Relationships

- **Evaluates:** [Falcon Perception](falcon-perception.md) across prompt-composition and dense-output regimes.[^falcon-perception-report]

[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local LaTeX source at [main.tex](../raw/2603.27365_FalconPerception/main.tex), especially `sections/pbench.tex` and `sections/results.tex` (accessed 2026-08-17).