---
type: Model System
title: Surya OCR 2.5
description: Surya OCR 2.5 is a 689M document-OCR VLM that generates ordered, geometrically annotated HTML blocks and reads tables, with a separate text-line detector.
tags: [ml, ocr, document-parsing, vision-language-models, layout-analysis, table-recognition, multilingual]
status: draft
created: 2026-10-30
stale_after: 2027-04-30
generated: { by: llm-wiki-agent/1, at: 2026-10-30T02:11:12Z }
sources:
  - id: surya-25-card
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
---

# Surya OCR 2.5

**Reported:** Datalab's Surya 2.5 is a 689M-parameter document OCR model: a Qwen3.5-style VLM uses different prompts for layout JSON and full-page HTML, while a separate small Torch model detects text lines. It targets documents rather than natural-scene photographs. The same VLM supports layout, OCR and table reading; full-page OCR and optional layout-first block OCR are distinct workflows.[^surya-25-card]

## Outputs and limitations

The documented page OCR output contains blocks in reading order with canonical and raw labels, HTML, polygon and bounding box, token-probability confidence, and skip/error flags. Inline equations are KaTeX-compatible LaTeX inside `<math>`; tables are HTML with merged cells. The model's compact output encodes label and coordinates normalized to 0–1000 as special tokens and encodes spanning cells using parent/ghost markers; the package decodes them into usable HTML.[^surya-25-card]

**Reported:** Unlike [Surya OCR 2](surya-ocr-2.md), Surya 2.5 does not provide table row/column geometry through `surya_table --mode simple`; that mode returns an error and requires a Surya 2 checkpoint. This is not a general claim that 2.5 lacks block geometry. [Deployment and output details](surya-ocr-2-5-deployment.md) describe the APIs and serving constraints.[^surya-25-card]

## Vendor-reported evaluation

These results are Datalab's claims, not independently reproduced. On [OmniParseBench](omniparsebench.md), Surya 2.5 versus 2 scores 85.9 versus 83.3 headline, 83.8 versus 81.0 text, 78.3 versus 74.3 tables, and 95.7 versus 94.5 layout. Both use `surya-ocr` 0.23.0, 192 DPI, the public scorer, and one run per model; the reported paired page-bootstrap 95% interval for the headline difference is +1.6 to +3.7 points. On olmOCR-bench the respective scores are 83.7 and 82.8, means of three passes with plain output. The older Surya 2 card reports 83.3 under a different described run; these results should not be conflated.[^surya-25-card]

On a newer, harder internal 91-language benchmark, 2.5 scores 74.9% versus 74.5% for 2; 21 languages reach 90% and 52 reach 80%. The earlier 87.2% Surya 2 figure uses an older version, so it is not a like-for-like comparison. The shown 2.5 language scores include Vietnamese 63.6%, English 90.3%, Chinese 75.7% and Arabic 45.4%; the full language table is unavailable locally.[^surya-25-card]

For full-page OCR against a running vLLM server, the vendor reports 4.52 pages/s at 192 DPI on one H100 80 GB, 32 concurrent requests and 300 pages, versus 2.72 for Surya 2 with MTP. On an M4 Max with llama.cpp Metal, 96 DPI, eight concurrent requests and 32 requests, it reports 0.190 pages/s for 2.5 bf16; 2.5 finished all 32 before the token cap, versus 28 for 2. These are conditional throughput measurements, not general latency guarantees.[^surya-25-card]

## License and evidence limits

**Reported:** Code is Apache 2.0; model weights use a modified AI Pubs Open Rail-M license, described as free for research, personal use and startups under $5M funding/revenue, with broader commercial licensing offered separately. The linked license text is absent, so consult the actual current terms before use.[^surya-25-card]

The supplied English model-card capture was inspected statically; publication date, capture date, exact upstream revision and canonical card URL are not established. The linked full multilingual table, local example images and chart, implementation, checkpoints, benchmark datasets and scorer are not included in this capture and were not inspected. The size chart's central scores are reproduced in the text table; visual examples are illustrative and excluded. External docs, pricing and repository links were not fetched. No model, commands, tests or benchmarks were run. Vendor claims, including licensing and performance, remain unverified.[^surya-25-card]

## Relationships

- **Related to:** [Surya OCR 2](surya-ocr-2.md), an earlier checkpoint with a distinct table geometry capability and separately reported evaluation.[^surya-25-card]
- **Uses:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) for full-page generation, with optional layout-first block recognition.[^surya-25-card]
- **Evaluated by:** [OmniParseBench](omniparsebench.md), in the vendor's reported run.[^surya-25-card]
- **Related to:** [Marker](marker.md), whose table converter the card suggests for table positions and formatting; compatibility with a particular Marker release was not tested.[^surya-25-card]

[^surya-25-card]: Datalab, local [Surya 2.5 model card](../raw/surya-ocr-2.5-hf.md), §§ Surya, Usage, OCR, Table Recognition, Math / equations, Output format, Limitations, Commercial usage, Benchmarks, Multilingual, Throughput and Training (inspected 2026-10-30).
