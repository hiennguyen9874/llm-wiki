---
type: Concept
title: Youtu-Parsing-Omni
description: Youtu-Parsing-Omni is a reported 5B multimodal parser that uses a shared image-and-audio encoder and prompt-selected OmniSchema JSON outputs.
tags: [ml, ocr, document-parsing, multimodal, vision-language-models]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:47:26Z }
stale_after: 2027-02-02
sources:
  - id: youtu-omni-card
    resource: ../raw/Youtu-Parsing-Omni.md
    kind: model-card
    title: Youtu-Parsing-Omni model card
---

# Youtu-Parsing-Omni

Youtu-Parsing-Omni is Tencent Youtu Lab's reported 5B multimodal parsing model, designed to map a single document page, image, audio clip, or audiovisual video to task-prompted structured JSON. The vendor describes shared perception for vision and audio and a common OmniSchema output; its capabilities and results are **reported**, not independently reproduced here.[^youtu-omni-card]

## Tasks and output

The card lists eight task keys: `document`, `natural_image`, `graphics_chart`, `graphics_flowchart`, `graphics_geometric`, `audio`, `natural_video`, and `textrich_video`. Document parsing reports layout, text, LaTeX, OTSL tables, Markdown charts, Mermaid flowcharts, and reading order. Natural images add entities, boxes and captions; geometry includes objects and relationships; audio and video add timed segments, speech and events, and text-rich video adds a structured report. The card describes seven parsing families and elsewhere ten parsing tasks without explaining the counting differences; the eight listed keys should not be silently equated with either count.[^youtu-omni-card]

Output is described as one fenced JSON block, with image `elements`, document `reading_order`, audio/video `segments`, and a `global_description`. Box coordinates use special tokens on a 0–1000 grid, and timestamps use `HH:MM:SS`. See [deployment](youtu-parsing-omni-deployment.md) for request and decoding constraints.[^youtu-omni-card]

## Encoder and training

**Reported architecture:** modality-specific stems map pixels or log-mel audio to tokens; a shared bidirectional Transformer uses `(t,h,w)` positional coordinates, followed by modality-specific mergers/projectors and a Youtu-LLM decoder. Video frames and audio chunks are packed temporally: ordinary layers use separate windows, while selected fusion layers create windows at audio-to-frame boundaries; audio positions use `h=w=0`. The claimed effect is cross-modal alignment inside the encoder.[^youtu-omni-card]

**Reported training:** after SFT and schema-routed RLVR, OmniSchema-Aware On-Policy Distillation (OSAD) samples student parses and admits those passing JSON, schema, box-syntax and repetition checks. A frozen teacher also sees the reference parse; content tokens use Jensen–Shannon divergence, structure tokens use higher-temperature forward KL, and all tokens receive an additional JS term. At round boundaries LoRA adapters merge and the student becomes the next teacher. Exact objectives, datasets and ablations require the linked technical report, not inspected here.[^youtu-omni-card]

## Reported evaluation

| Benchmark | Vendor-reported results | Qualification |
| --- | --- | --- |
| OmniDocBench v1.6 | Overall 96.96; text edit 0.0271; formula CDM 96.80; table TEDS 96.79; reading-order edit 0.1104 | The card's table also reports TeleOCR overall 96.91; individual metric leaders differ. |
| OmniParsingBench | Average 75.08; chart 95.02, geometry 74.33, natural image 62.84, audio 78.08, natural video 74.18, text-rich video 75.62 | Card reports Gemini-3-Pro average 77.44; model comparisons reflect its reported setup. |
| ChemOCR | Average similarity 74.6, Tani@1.0 54.2 | DeepSeek-OCR 2 reports 74.9 average similarity in the same table. |
| PDMX-Synth | CER 22.73, SER 26.73, LER 33.20 | LEGATO has lower SER and LER in the same table. |

All figures are **vendor-reported**, not verified or run. Do not merge the differently named OmniParsingBench with [OmniParseBench](omniparsebench.md), a separate benchmark described by another source, without evidence of equivalence.[^youtu-omni-card]

## Relationships

- **Extends:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) with a document-page mode inside a broader multimodal interface.[^youtu-omni-card]
- **Uses:** [Youtu-Parsing-Omni deployment](youtu-parsing-omni-deployment.md) documents the card's serving and decoding instructions.

## Coverage and limits

The supplied English model-card capture was inspected in full. The architecture, fusion and training figures (`assets/arch_figure.png`, `assets/mech_figure.png`, `assets/osad_figure.png`) are unavailable locally; the prose is the only inspected description. The logo is decorative. The linked report, code, prompts, weights, evaluator, and license were not inspected; no revision or capture date is stated. The card labels its license `other` / `youtu-parsing`, so terms must be checked separately. No code, inference, or benchmark was executed; model access and availability remain unverified. Draft status records these material coverage limits.[^youtu-omni-card]

[^youtu-omni-card]: Tencent Youtu Lab, [Youtu-Parsing-Omni model card](../raw/Youtu-Parsing-Omni.md), §§ Introduction, Method, Model Zoo, Results, Quick Start › Output format, and Citation; inspected 2026-11-02.
