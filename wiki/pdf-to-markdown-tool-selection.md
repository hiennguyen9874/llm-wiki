---
type: Synthesis
title: PDF-to-Markdown tool selection
description: Selecting MinerU, Marker, Docling, or OpenDataLoader-PDF for PDF-to-Markdown depends on document difficulty, image-export needs, RAG integration, and CPU-throughput constraints.
tags: [ocr, document-parsing, pdf, markdown, tool-selection, rag]
status: draft
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T10:09:08+07:00 }
sources:
  - id: tool-comparison
    resource: ../raw/ocr-tool-compare.md
    title: PDF-to-Markdown tool comparison
---

# PDF-to-Markdown tool selection

For PDF-to-Markdown with separate image assets, the retained comparison recommends benchmarking **MinerU** first for difficult scientific or layout-heavy documents, **Marker** for a lower-friction practical conversion path, **Docling** where Markdown feeds a broader document/RAG pipeline, and **OpenDataLoader-PDF** when CPU throughput dominates. This is a source-level recommendation, not an independently established quality ranking.[^tool-comparison]

## Selection guide

| Primary requirement | Candidate to evaluate first | Rationale reported by the source | Qualification |
|---|---|---|---|
| Difficult papers, books, scans, multi-column pages, formulas, and tables | MinerU | The source ranks it highest overall and says its Markdown uses relative references to a sibling `images/` directory. | The cited claims and community reports were not independently verified in this wiki. |
| Straightforward PDF-to-Markdown workflow with exported images | Marker | The source describes a simple Markdown CLI workflow and image extraction alongside the output. | The source characterizes this as a practical/DX advantage, not a controlled benchmark result. |
| Markdown as input to a broader RAG or document-understanding pipeline | Docling | The source highlights its unified document representation and `referenced` image-export mode. | A cited RAG benchmark favors one Docling pipeline, but the source itself says chunking, metadata, and image preprocessing can matter more than parser choice. |
| Very large CPU-bound batch conversion | OpenDataLoader-PDF | The source reports a deterministic CPU mode and a claimed throughput above 100 pages/s. | Its reported comparison scores are project-published rather than independent; table-extraction issues are also cited. |

## Output and integration requirements

The comparison treats a portable output bundle as a central requirement:

```text
document.md
images/
  image_001.png
  image_002.png
```

The expected Markdown must preserve reading order, headings, paragraphs, tables, equations, figures, and captions, while linking images through relative paths. The source specifically reports that MinerU and Marker produce this shape conveniently; Docling can produce it with referenced-image configuration rather than its default path.[^tool-comparison]

## Evaluation procedure

A production choice should be based on 20–50 representative PDFs rather than simple digital-text PDFs. The retained source recommends deliberately including two-column layouts, scans, merged-cell tables, equations, charts with captions, headers/footers, and Vietnamese PDFs. Score each candidate separately for text, reading order, tables, formulas, figure/image extraction, and the operational cost appropriate to the deployment.[^tool-comparison]

## Contradictions and evidence limits

- The source reports no community consensus: different Reddit discussions favor MinerU, Marker, or Docling. Those reports are anecdotal and their linked threads were not inspected during this ingest.[^tool-comparison]
- The ordering “MinerU ≈ Marker > Docling > OpenDataLoader-PDF” is the source author's synthesis. It combines product documentation, community discussion, and a cited academic benchmark with different goals, so it is not a common experimental result.[^tool-comparison]
- OpenDataLoader-PDF's reported relative score is explicitly identified by the source as a project-provided benchmark, not independent evidence.[^tool-comparison]
- The source's linked external documentation, repositories, Reddit threads, issue reports, PyPI page, and arXiv paper remain unverified external references; this page does not elevate their claims beyond that source's attribution.[^tool-comparison]

## Relationships

- **Uses:** [Current OCR approaches](current-ocr-approaches.md) for the architectural trade-offs behind structured document conversion.
- **Related to:** [MinerU2.5](mineru2-5.md), a separately documented MinerU model release; this comparison does not establish that its tool-level claims apply unchanged to that release.

[^tool-comparison]: User-supplied [*PDF-to-Markdown tool comparison*](../raw/ocr-tool-compare.md), accessed 2026-08-21. It cites external product documentation, Reddit discussions, an issue report, and an academic benchmark; none was independently inspected for this compilation.
