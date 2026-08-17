---
type: Dataset
title: Infinity-Doc2-5M
description: Infinity-Doc2-5M is an approximately 5-million-sample Chinese-and-English multi-task corpus for document structure, element parsing, and document reasoning.
tags: [datasets, document-parsing, synthetic-data, pseudo-labeling, multimodal]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:35:12Z }
sources:
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
---

# Infinity-Doc2-5M

Infinity-Doc2-5M is the reported training corpus for Infinity-Parser2. It combines public datasets, flywheel-mined real documents, expert-model pseudo-labels, manually labeled examples, and [DOM-based synthesis](dom-based-document-synthesis.md) into approximately five million Chinese-and-English samples across document parsing, element parsing, document VQA, and general multimodal understanding.[^infinity-parser2-report]

## Coverage and composition

The corpus represents outputs as Markdown, HTML, LaTeX, JSON, SMILES, and structured chart forms, with element bounding boxes and reading order where relevant. Its document-structure data include 776K pseudo-labeled web documents across nine document types, 2.5K manually annotated complex newspapers, 251K synthesized documents, 57K examples sampled from [Infinity-Doc-400K](infinity-doc-400k.md), and 62K handwritten document pairs.[^infinity-parser2-report]

The report also lists 676K table-to-HTML samples, 336K table-to-Markdown samples including 309K synthesized tables, 631K sampled formula examples, three chart datasets sampled at 315K each, 315K synthesized chemical-formula images, 315K document-VQA examples, 631K general-multimodal examples, and 5K blank-page examples. These are balanced samples rather than a complete release manifest, so their rounded counts should not be treated as an exact deduplicated total.[^infinity-parser2-report]

## Curation boundaries

The data iteration cycle evaluates held-out benchmarks for weaknesses, but the report says it does not reuse held-out examples for training. It mines disjoint sources matching a weakness taxonomy, pseudo-labels real documents with specialist models and filters them by confidence and rules, then adds synthetic examples for gaps. Each round appends data to the historical training set rather than replacing it.[^infinity-parser2-report]

The authors state that they removed business-sensitive and privacy-related samples before release. This is a source claim: the local bundle supplies no data records, licenses, filtering criteria, acceptance rates, deduplication method, or audit artifacts to verify it.[^infinity-parser2-report]

## Trust limits

- The dataset itself is not in the local source bundle, so its stated size, bilingual composition, labels, quality controls, and release status are not independently auditable here.[^infinity-parser2-report]
- Real-document labels include pseudo-labels from multiple expert systems; the report gives neither per-source error rates nor human agreement. The 2.5K manual-newspaper subset does not establish quality across the corpus.[^infinity-parser2-report]
- The training mix includes internal proprietary corpora and model-distilled text, whose provenance, permissions, and contamination controls are not fully described.[^infinity-parser2-report]

## Relationships

- **Used by:** [Infinity-Parser2](infinity-parser2.md) for multi-task SFT and a 5% per-task RL sample.[^infinity-parser2-report]
- **Partly reuses:** [Infinity-Doc-400K](infinity-doc-400k.md), sampling 57K examples for the `doc2md` task.[^infinity-parser2-report]
- **Constructed with:** [Document-parser data flywheel](document-parser-data-flywheel.md) and [DOM-based document synthesis](dom-based-document-synthesis.md).[^infinity-parser2-report]

[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local LaTeX source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex), including [data flywheel](../raw/2607.07836_Infinity-Parser2/figures/data_flywheel_0605.pdf) and [synthesis engine](../raw/2607.07836_Infinity-Parser2/figures/data-engine-0704.pdf) (accessed 2026-08-17).
