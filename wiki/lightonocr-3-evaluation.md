---
type: Concept
title: LightOnOCR-3 evaluation
description: LightOnOCR-3 evaluation reports vendor-run OCR benchmarks and H100 serving measurements, with postprocessing and rendering conditions that limit direct comparisons.
tags: [ml, ocr, benchmarks, inference, evaluation]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:11:56Z }
stale_after: 2027-04-27
sources:
  - id: lightonocr-3-blog
    resource: ../raw/lightonocr-3/index.md
    scope: ../raw/lightonocr-3/
    kind: article
    title: "LightOnOCR-3: High-Performance OCR and Layout Extraction in One Model"
---

# LightOnOCR-3 evaluation

**Reported:** LightOn's blog evaluates [LightOnOCR-3](lightonocr-3.md) against selected open or locally runnable OCR models on three parsing benchmarks, and reports H100 serving measurements. Results are vendor-run, not independently reproduced, and output normalization and render settings materially affect comparisons.[^lightonocr-3-blog]

## Parsing quality

| Model | olmOCR-Bench overall | ParseBench overall, 5 categories | fr-bench-pdf2md overall |
|---|---:|---:|---:|
| LightOnOCR-3-0.8B | 85.5 | 74.6 | 70.5 |
| LightOnOCR-3-1B | 84.5 | 71.4 | 69.6 |
| LightOnOCR-3-4B | 86.3 | 75.1 | 74.1 |
| Infinity Parser Pro | 87.6 | 74.3 | 63.2 |
| Chandra 2 | 85.8 | 70.1 | 69.0 |

The blog reports the 4B leading its shown ParseBench five-category and French overall tables, while Infinity leads its olmOCR overall table. Category-level results vary: for example, Infinity scores 74.9 on ParseBench visual grounding versus 68.3 for LightOnOCR-3-4B. LightOnOCR-2's 83.2 olmOCR overall excludes headers/footers, unlike other rows, so it is not directly comparable. The blog says it selected top models rather than publishing every model evaluated; no uncertainty or significance is provided.[^lightonocr-3-blog]

## Normalization and tokens

The blog cautions that edit-distance scoring responds to formatting differences even when content is equivalent. Its figure reports LightOnOCR-3-4B olmOCR overall 85.0 raw versus 86.3 postprocessed; Chandra 2 85.1 versus 85.8; Infinity-Parser2-Pro 85.9 versus 87.6. The described normalization code is external and was not inspected; the article inconsistently refers to normalizing “raw inputs” even though the figure compares raw and postprocessed outputs.[^lightonocr-3-blog]

For the same 512 pages, mean complete grounding outputs are 1,582 tokens for 0.8B and 1,554 for 4B, versus 1,812 for Chandra 2 and 1,742 for Infinity-Parser2-Pro. This is not an isolated measurement of formatting overhead: outputs and included visual information differ.[^lightonocr-3-blog]

## Serving measurements

The reported test used the same 512 olmOCR pages, one H100 per model, vLLM 0.30.0 with identical server flags, model-specific render settings and guidellm load variation. Peak means all 512 requests submitted at once and completed; latency is median single-page latency.[^lightonocr-3-blog]

| Model | Benchmark rendering | Median latency | Peak pages/s | Peak at 1540px |
|---|---|---:|---:|---:|
| 0.8B | 400 DPI, ≤5 MP | 3.8 s | 3.32 | 4.78 |
| 1B | 1540px long side | 2.7 s | 3.52 | 3.52 |
| 4B | 400 DPI, ≤5 MP | 6.6 s | 2.03 | 3.36 |
| Chandra 2 | 300 DPI, ≤6.3 MP; 579-token prompt | 8.1 s | 1.68 | 2.95 |

The authors report 19% lower 4B single-page latency and 21% higher peak throughput than Chandra at their respective benchmark settings; the render and prompt workloads differ. At the same 1540px resolution, the reported peak advantage is approximately 14%. These results do not establish accuracy at the lower resolution or transfer to other hardware and load distributions.[^lightonocr-3-blog]

## Coverage and relationships

- **Compared in:** [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md), which places this model's reported results beside nine other document parsers per dataset.
- **Evaluates:** [LightOnOCR-3](lightonocr-3.md); see [deployment](lightonocr-3-deployment.md) for model-card runtime instructions and [training](lightonocr-3-training.md) for the reported data recipe.
- The article and 11 local image assets were inspected, including the postprocessing and speed tables. The interactive benchmark and example iframes, external benchmarking repository, weights and execution environment were unavailable for inspection; no benchmark or inference was run. The article's model-card render recommendations and benchmark settings have different contexts and should not be conflated. Draft records these limits.[^lightonocr-3-blog]

[^lightonocr-3-blog]: Taghadouini, Cavaillès and Aubertin, [LightOnOCR-3 blog](../raw/lightonocr-3/index.md), §§ 1 “Formatting efficiency”, 2.2–2.4; `assets/VjGuS22FehyMGIaLiZ7fU.png` (raw and postprocessed results), `assets/QKQIrgIR9NpILnyGLu9fW.png` (speed table), `assets/2ow1-IiTO82eBgUU2MoRr.png` (output tokens).
