---
type: Model
title: MiniCPM-OCR 1.0
description: MiniCPM-OCR 1.0 is a 1.3B OCR VLM used with PP-DocLayoutV3 and an SDK to recognize document regions and assemble ordered output.
tags: [ml, ocr, document-parsing, vision-language-model]
status: draft
created: 2026-10-28
generated: { by: llm-wiki-agent/1, at: 2026-10-28T16:51:28Z }
stale_after: 2027-04-28
sources:
  - id: minicpm-card
    resource: ../raw/MiniCPM-OCR-1.0.md
    kind: model-card
    title: MiniCPM-OCR 1.0 model card
  - id: minicpm-repo
    resource: ../raw/MiniCPM-OCR/README.md
    scope: ../raw/MiniCPM-OCR/
    kind: code
    revision: b33b474
    title: MiniCPM-OCR repository
---

# MiniCPM-OCR 1.0

**Reported:** MiniCPM-OCR 1.0 is a 1.3B Chinese-and-English document OCR VLM based on MiniCPM-V 4.6, with a SigLIP vision encoder and Qwen3.5 language model. Its document pipeline combines [PP-DocLayoutV3](pp-doclayoutv3.md), region recognition and SDK assembly, rather than requiring the recognition model to parse an entire page in one pass.[^minicpm-card][^minicpm-repo]

## Pipeline and interfaces

The SDK renders PDF pages, detects and orders regions, recognizes crops concurrently, and assembles Markdown; it converts OTSL tables to HTML and retains formulas as LaTeX. The card specifies 4× visual-token compression, resolution 448 and up to nine slices. Direct region prompts include `Text Recognition:`, `Table Recognition:`, `Formula Recognition:`, `Seal Recognition:` and `Chart to Table:`. KIE requests JSON fields and uses `###` as the requested missing-value sentinel; generated JSON must be validated. The recognition service and SDK can run separately.[^minicpm-card][^minicpm-repo]

**Reported deployment:** vLLM, SGLang, llama.cpp, Ollama, Transformers and FlagOS are documented; main weights are available in BF16, GGUF, AWQ and GPTQ. DSpark acceleration requires a matching main model and draft head from the same release. Region and page concurrency are distinct controls; check `finish_reason` for truncation.[^minicpm-card][^minicpm-repo]

## Reported evaluation and limits

The repository figure reports 96.51 OmniDocBench v1.6, 93.68 [Real5-OmniDocBench](real5-omnidocbench.md), 92.39 Wild, 82.7 olmOCR-Bench, 29.78 CHAOS and 54.7 OCRBench v2. These are **vendor-reported**, not independently verified; scores across benchmarks are not interchangeable. The archived benchmark-data JSON marks the MiniCPM CHAOS value as pending confirmation, despite the figure printing 29.78.[^minicpm-repo]

The vendor reports 1.217 pages/s on 1,651 OmniDocBench v1.6 images on an RTX 5090 at image concurrency 1, versus 2.133 at concurrency 8; regions within a page may run concurrently. The 55% end-to-end DSpark efficiency claim lacks complete comparison commands and logs. Exact versions, complete evaluation scripts and timing boundaries are also pending in the reproduction guide. Wild results use SDK rotation correction; Real5 uses v1.5 ground truth and an equal mean of the five scenario scores. CHAOS scoring searches full-page output without bbox alignment.[^minicpm-repo]

## Contradictions

The model guide gives **1.217 pages/s** at concurrency 1, whereas the benchmark-data JSON lists **1.213 pages/s** under its stated conditions; the difference remains unresolved. See [MiniCPM-OCR evaluation](minicpm-ocr-evaluation.md) for comparison rows, scoring conditions and other artifact discrepancies.[^minicpm-repo]

## Relationships

- **Uses:** [PP-DocLayoutV3](pp-doclayoutv3.md) for [layout-first modular parsing](task-layout-first-modular-parsing.md).[^minicpm-repo]
- **Uses:** an optional SDK heuristic for [cross-page table reconstruction](task-cross-page-table-reconstruction.md), disabled in the bundled configuration; statically inspected, not executed.[^minicpm-repo]
- **Supports:** direct prompted image [KIE](task-structured-extraction-kie.md).[^minicpm-repo]
- **Can be assessed by:** [MiniCPM-OCR Jev](minicpm-ocr-jev.md), a separate region-level correctness model.[^minicpm-repo]

## Coverage and trust

The model card, repository README, English model guide, Jev guide, reproduction guide, project environment manifest, benchmark-data JSON, two benchmark-table images, SDK cross-page merge implementation, configuration, CLI assembly and its tests were inspected; no model, installer or benchmark was executed. Repository checkout was clean at the recorded revision. The English/Chinese parallel guides, backend and fine-tuning documentation, SDK implementation and tests, Jev scripts and deployment services, and other material figures remain **pending**, as do external weights, datasets and scoring artifacts. The bundled KaTeX and other static vendor assets are excluded as third-party dependencies; decorative logos and examples are not evidence for benchmark claims. The repository reports Apache-2.0 for code, documentation and weights; individual remote artifacts were not independently checked. This incomplete package coverage makes the page draft.[^minicpm-card][^minicpm-repo]

[^minicpm-card]: [MiniCPM-OCR 1.0 model card](../raw/MiniCPM-OCR-1.0.md), §§ Model architecture, Recognition guide, Related checkpoints and License.
[^minicpm-repo]: [Repository README](../raw/MiniCPM-OCR/README.md), revision `b33b474`; `docs/minicpm_ocr_1dot0_en.md` §§ Model Base, Document Parsing Workflow, Inference, Evaluation and Throughput; `docs/benchmark_reproduction_en.md` §§ Evaluation Settings, Scoring and Aggregation Rules, Parsing Efficiency Test; `assets/minicpm-ocr/ocr-benchmarks.png` MiniCPM row; `assets/minicpm-ocr/benchmark-data.json` `benchmarks.models` and `throughput.models` MiniCPM rows; `sdk/minicpmvocr/postprocess/crosspage.py::merge_cross_page_tables`, `sdk/minicpmvocr/configs/minicpmvocr.yaml` key `pipeline.merge_cross_page_tables`.
