---
type: Synthesis
title: PDF-to-Markdown tool selection
description: Selecting MinerU, Marker, Docling, OpenDataLoader-PDF, or model-free LiteParse for PDF-to-Markdown depends on document difficulty, image-export needs, RAG integration, and CPU-throughput constraints.
tags: [ocr, document-parsing, pdf, markdown, tool-selection, rag, model-free]
status: draft
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:24:46Z }
sources:
  - id: tool-comparison
    resource: ../raw/ocr-tool-compare.md
    title: PDF-to-Markdown tool comparison
  - id: liteparse-readme
    resource: ../raw/liteparse.md
    title: LiteParse README
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
| Fast, GPU-free conversion where a rule-based path is acceptable | LiteParse | Apache-2.0 Rust/PDFium tool with optional Tesseract or HTTP OCR, Markdown/JSON/text output, bounding boxes, and multi-language bindings. | The README calls its Markdown rendering purely heuristic and defers dense tables, multi-column pages, charts, handwriting, and scans to the commercial LlamaParse. |

## Output and integration requirements

The comparison treats a portable output bundle as a central requirement:

```text
document.md
images/
  image_001.png
  image_002.png
```

The expected Markdown must preserve reading order, headings, paragraphs, tables, equations, figures, and captions, while linking images through relative paths. The source specifically reports that MinerU and Marker produce this shape conveniently; Docling can produce it with referenced-image configuration rather than its default path.[^tool-comparison]

## The model-free baseline

A fourth option is defined by *absence* of a model rather than by a different model choice: LiteParse extracts the text layer with PDFium, classifies blocks with geometric rules, and adds OCR only on demand. In its own runs it reports 0.389 (ParseBench), 0.901 (opendataloader-bench), and 42.2 (olmOCR-bench) with PaddleOCR attached, ahead of every other model-free tool it tested; those figures are project-reported and its math categories score zero.[^liteparse-readme] Independent project runs of the same named harnesses disagree by a wide margin, as recorded under [LiteParse → Contradictions](liteparse.md#contradictions), so this branch of the decision should be re-measured on the caller's own corpus rather than taken from any single leaderboard. Details and the conflicting numbers are on [LiteParse](liteparse.md).

## Evaluation procedure

A production choice should be based on 20–50 representative PDFs rather than simple digital-text PDFs. The retained source recommends deliberately including two-column layouts, scans, merged-cell tables, equations, charts with captions, headers/footers, and Vietnamese PDFs. Score each candidate separately for text, reading order, tables, formulas, figure/image extraction, and the operational cost appropriate to the deployment.[^tool-comparison]

## Contradictions and evidence limits

- The source reports no community consensus: different Reddit discussions favor MinerU, Marker, or Docling. Those reports are anecdotal and their linked threads were not inspected during this ingest.[^tool-comparison]
- The ordering “MinerU ≈ Marker > Docling > OpenDataLoader-PDF” is the source author's synthesis. It combines product documentation, community discussion, and a cited academic benchmark with different goals, so it is not a common experimental result.[^tool-comparison]
- OpenDataLoader-PDF's reported relative score is explicitly identified by the source as a project-provided benchmark, not independent evidence.[^tool-comparison]
- The source's linked external documentation, repositories, Reddit threads, issue reports, PyPI page, and arXiv paper remain unverified external references; this page does not elevate their claims beyond that source's attribution.[^tool-comparison]

## Relationships

- **Uses:** [Current OCR approaches](current-ocr-approaches.md) for the architectural trade-offs behind structured document conversion.
- **Related to:** [LiteParse](liteparse.md), the model-free option added to this decision after the original four-tool comparison.
- **Related to:** [MinerU2.5](mineru2-5.md), a separately documented MinerU model release; this comparison does not establish that its tool-level claims apply unchanged to that release.

[^tool-comparison]: User-supplied [*PDF-to-Markdown tool comparison*](../raw/ocr-tool-compare.md), accessed 2026-08-21. It cites external product documentation, Reddit discussions, an issue report, and an academic benchmark; none was independently inspected for this compilation.
[^liteparse-readme]: run-llama, [*LiteParse README*](../raw/liteparse.md), "Benchmarks" section (v2.14.4, run 2026-09-09). Project-reported scores from a single machine; competing tools' rows were produced by the same project.
