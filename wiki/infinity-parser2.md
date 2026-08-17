---
type: Model System
title: Infinity-Parser2
description: Infinity-Parser2 is a Qwen3.5-based end-to-end document parser trained with multi-task SFT and GRPO using task-native verifiable rewards.
tags: [document-parsing, reinforcement-learning, vision-language-models, layout-analysis, multimodal]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:10:09Z }
sources:
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
  - id: infinity-parser2-pro-card
    resource: ../raw/Infinity-Parser2-Pro.md
    title: Infinity-Parser2-Pro model card
---

# Infinity-Parser2

Infinity-Parser2 is an end-to-end document-image parser that maps a page image and task instruction to structured outputs, including coordinate-bearing JSON, Markdown, HTML, LaTeX, and SMILES. The report describes a 2B Flash model and a 35B-A3B Pro model, both trained on [Infinity-Doc2-5M](infinity-doc2-5m.md) with multi-task supervised fine-tuning (SFT), then joint GRPO using task-native verifiable rewards.[^infinity-parser2-report]

## Release and operation

The provider's model card announces Pro and Flash on 2026-05-11 and labels the model Apache-2.0. It positions Pro for accuracy-sensitive work and Flash for lower-latency use.[^infinity-parser2-pro-card]

The card supplies a native `transformers` example for image-to-structured-layout JSON and an `infinity_parser2` wrapper for PDF, image, batch, and directory parsing. The wrapper exposes `doc2json`, `doc2md`, and custom-prompt tasks, can write Markdown or requested raw JSON, and supports local Transformers, offline vLLM Engine (the stated default), and a vLLM HTTP-server backend.[^infinity-parser2-pro-card]

## Model and training

Flash is based on Qwen3.5-2B; Pro is based on Qwen3.5-35B-A3B. For the document `doc2json` task, each output element has a category, bounding box, and text. The report's reward combines category-wise occupied-area mIoU (weight 0.3) with edit-distance similarity over the concatenated reading-order text (weight 0.7). This avoids one-to-one box matching, but consequently does not directly penalize different box partitions with the same category-area union.[^infinity-parser2-report]

The joint RL stage co-trains document parsing, layout analysis, table parsing, formula parsing, chart parsing, chemical-formula parsing, document VQA, and a short-answer subset of general multimodal understanding. It routes each task to a native metric: EDS, mIoU, TEDS, CDM, RMS-F1/SCRM/EDS, Tanimoto similarity, or ANLS as applicable. The authors sample 5% of each task for roughly 220K RL examples, use eight GRPO rollouts per prompt, and exclude open-ended general-multimodal samples from RL.[^infinity-parser2-report]

## Reported results

All results are author-reported and were not independently reproduced from this bundle:[^infinity-parser2-report]

- **Document parsing:** Pro reports 87.6 on olmOCR-Bench and 74.3 on ParseBench; it reports 93.95 on OmniDocBench v1.6, below the table's PaddleOCR-VL-1.5 (94.87) and GLM-OCR (95.15).
- **Element tasks:** Pro reports 94.76/98.88 TEDS on PubTabNet/FinTabNet, 97.7 mean formula CDM, 86.5 ChartQA chart-to-table RMS-F1, and 53.91 InChI exact-match accuracy on CoSyn-Chemical.
- **Layout and VQA:** Pro reports 52.41 mIoU on D4LA and 96.43/86.26 ANLS on DocVQA/InfoVQA under the report's evaluation pipeline.
- **Speed:** on H100s at tensor parallelism 2 and concurrency 8, Flash reports 1,624 tokens/s and 0.95 s/page for its longer `doc2json` output. The claimed 3.68x gain over Infinity-Parser-7B uses the same serving configuration but not the same output format.

## Trust limits

- The local bundle contains a technical report, bibliography, and figures, not weights, code, data records, prompts, or evaluation implementation. Links to external release pages in the report were not independently inspected.[^infinity-parser2-report]
- Some training sources, the financial-extraction benchmark, and the evaluation pipeline are internal or proprietary. The source provides aggregate descriptions rather than auditable records, licenses, filtering rules, or full protocols.[^infinity-parser2-report]
- Baseline scores mix values from original reports with author re-evaluations. Benchmark versions, prompts, output formats, and serving configurations vary, so tables do not establish controlled cross-system rankings.[^infinity-parser2-report]
- The authors identify bilingual training coverage, residual pseudo-label noise, dense charts, arbitrarily rotated content, inline-format preservation, and complex visual instruction following as limitations.[^infinity-parser2-report]
- The model card's release status, license, interfaces, dependency versions, and performance claims are provider statements; the linked external repository, package, dataset, demo, and performance images were not independently inspected. Its local `assets/logo.png` reference is not present alongside this raw Markdown file.[^infinity-parser2-pro-card]

## Relationships

- **Builds on:** [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md), the earlier Qwen2.5-VL-7B document parser; the report calls Infinity-Parser-7B the prior generation.[^infinity-parser2-report]
- **Uses:** [Infinity-Doc2-5M](infinity-doc2-5m.md) for SFT and the sampled multi-task RL set.[^infinity-parser2-report]
- **Uses:** [Document-parser data flywheel](document-parser-data-flywheel.md) to target data collection, pseudo-labeling, synthesis, and cumulative retraining.[^infinity-parser2-report]
- **Uses:** [DOM-based document synthesis](dom-based-document-synthesis.md) to generate controlled, geometry-aligned training examples.[^infinity-parser2-report]

[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local LaTeX source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex), including [document parsing results](../raw/2607.07836_Infinity-Parser2/figures/document_parsing_perf.pdf), [capability results](../raw/2607.07836_Infinity-Parser2/figures/capabilities_perf.pdf), [data flywheel](../raw/2607.07836_Infinity-Parser2/figures/data_flywheel_0605.pdf), [synthesis engine](../raw/2607.07836_Infinity-Parser2/figures/data-engine-0704.pdf), and [training framework](../raw/2607.07836_Infinity-Parser2/figures/overall_training_strategy_0707.pdf) (accessed 2026-08-17).

[^infinity-parser2-pro-card]: INF Team, *Infinity-Parser2-Pro model card*, [local Markdown source](../raw/Infinity-Parser2-Pro.md) (accessed 2026-08-17).
