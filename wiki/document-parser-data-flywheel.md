---
type: Workflow
title: Document-parser data flywheel
description: The document-parser data flywheel iteratively converts model weaknesses into targeted mined, pseudo-labeled, or synthesized training data.
tags: [data-curation, document-parsing, evaluation, synthetic-data, workflows]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:06:36Z }
sources:
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
  - id: hunyuanocr-1-5-model-card
    resource: ../raw/HunyuanOCR-1.5.md
    title: "HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better"
---

# Document-parser data flywheel

The document-parser data flywheel is an iterative data-curation workflow that maps a current model's weaknesses into requirements for targeted mined, pseudo-labeled, or synthesized training data and uses the resulting data in a later training cycle. Infinity-Parser2 reports a controlled implementation that excludes held-out evaluation examples from training, while HunyuanOCR-1.5 reports an agent-mediated variant without equivalent procedural detail.[^infinity-parser2-report][^hunyuanocr-1-5-model-card]

## Cycle

1. **Evaluate and diagnose:** score a fixed multi-task benchmark suite, retain low-scoring samples or subcategories, inspect prediction overlays, and tag failures along document, element, and layout axes.
2. **Acquire:** translate weakness tags into source-specific collection queries, then use web crawling, public datasets, or internal corpora. The report says initial collection targets about 2,000 samples per tag and later rounds rebalance unresolved tags.
3. **Create supervision:** segment real pages, route regions to expert models, and apply confidence and rule filters; synthesize targeted examples for sparse layouts, languages, and elements that mining cannot supply economically.
4. **Train cumulatively:** append the newly labeled batch to historical data, fine-tune the model, and repeat until benchmark gains saturate.[^infinity-parser2-report]

## Agent-mediated variant

HunyuanOCR-1.5 calls its approach **Agentic Data Flow**. Its model card says agents turn model weaknesses into executable data requirements and participate in material search, tool-based verification, sample cleaning, and pipeline development with algorithm engineers. It names low-resource OCR, ancient-script OCR, and multi-image text-centric QA as targeted capabilities, but gives no source manifests, data volumes, outcome metrics, or overlap controls. Thus, it supports the general weakness-to-data pattern, not the detailed acquisition, separation, or efficacy claims documented for Infinity-Parser2.[^hunyuanocr-1-5-model-card]

## Observed ablation in the report

On the authors' Flash ablation, adding pseudo-labeled web documents to public and manually labeled data raises olmOCR-Bench from 28.4 to 83.3 and DocLayNet from 49.03 to 62.48; adding synthetic data reaches 85.3 and 62.31. Later addition of element and generalization data expands capabilities but slightly lowers the reported core parsing and layout scores. These author-reported results support that the listed data additions coincided with performance changes, not that the flywheel alone caused them.[^infinity-parser2-report]

## Guardrails and limits

The reported design properly separates diagnosis from training: benchmark examples act as a demand signal, while acquisition should draw from disjoint sources. This is a procedural claim rather than an independently audited contamination guarantee, because the report does not supply source manifests, deduplication artifacts, or benchmark-overlap checks.[^infinity-parser2-report]

The workflow relies on proprietary data, specialist pseudo-labelers, hand-crafted filters, and internal evaluation infrastructure. It does not quantify their error rates or show that a fixed benchmark remains representative as the cycle converges.[^infinity-parser2-report]

## Relationships

- **Constructs:** [Infinity-Doc2-5M](infinity-doc2-5m.md) through targeted mining, pseudo-labeling, and synthesis.[^infinity-parser2-report]
- **Uses:** [DOM-based document synthesis](dom-based-document-synthesis.md) to fill targeted coverage gaps.[^infinity-parser2-report]
- **Used by:** [Infinity-Parser2](infinity-parser2.md) as its reported data-curation process.[^infinity-parser2-report]
- **Used by:** [HunyuanOCR-1.5](hunyuanocr-1.5.md) as a related agent-mediated data-construction approach with less documented procedure.[^hunyuanocr-1-5-model-card]

[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local LaTeX source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex), including [data flywheel](../raw/2607.07836_Infinity-Parser2/figures/data_flywheel_0605.pdf) (accessed 2026-08-17).
[^hunyuanocr-1-5-model-card]: Tencent Hunyuan, *HunyuanOCR-1.5: Making Lightweight OCR VLMs Faster and Better*, local model card at [HunyuanOCR-1.5.md](../raw/HunyuanOCR-1.5.md) (accessed 2026-08-17).
