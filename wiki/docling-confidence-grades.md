---
type: Concept
title: Docling confidence grades
description: Docling conversion confidence reports expose document- and page-level categorical quality grades derived from layout, OCR, parse, and currently unimplemented table component scores.
tags: [docling, document-parsing, quality-assessment, confidence-scores, ocr]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:17:04Z }
sources:
  - id: docling-confidence-docs
    resource: ../raw/docling-concepts/confidence_scores.md
    title: Docling confidence scores documentation
---

# Docling confidence grades

Docling v2.34.0 introduced confidence grades on `ConversionResult.confidence` to assess conversion quality and help route documents to review or alternative processing. A report includes numerical 0.0–1.0 scores and categorical `POOR`, `FAIR`, `GOOD`, or `EXCELLENT` grades.[^docling-confidence-docs]

## Operational interpretation

The documentation advises users to assess overall conversion with document-level `mean_grade` and `low_grade`, rather than relying on numerical scores whose computation and weighting may change. The grades can support manual-review selection, pipeline adjustment, unattended-batch thresholds, and early issue detection.[^docling-confidence-docs]

## Report components

The report has component scores and grades for layout recognition (`layout_score`), OCR-extracted content (`ocr_score`), and the 10th-percentile score of digital text cells (`parse_score`). It also reserves `table_score` for table-extraction quality, but the source says that component is not yet implemented.[^docling-confidence-docs]

`mean_grade` aggregates the four component scores, while `low_grade` is based on the 5th-percentile score to highlight poor regions. Reports exist at page level in `pages` and at document level, where corresponding fields aggregate page-level grades.[^docling-confidence-docs]

## Relationships

- **Applies to:** [Docling architecture](docling-architecture.md), specifically the conversion result returned by its document converter.[^docling-confidence-docs]
- **Related to:** [Docling OCR engines](docling-ocr-engines.md), because OCR quality is one reported confidence component.[^docling-confidence-docs]

[^docling-confidence-docs]: Docling, [*Confidence scores*](../raw/docling-concepts/confidence_scores.md) (accessed 2026-08-21).