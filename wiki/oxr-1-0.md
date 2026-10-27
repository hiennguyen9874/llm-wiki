---
type: Concept
title: OXR-1.0
description: OXR-1.0 is SoMark's 1.3B document parser with a replaceable layout model and combined content recognition and reading-order prediction.
tags: [ml, ocr, document-parsing, layout-analysis]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:01:15Z }
stale_after: 2027-04-27
sources:
  - id: oxr-readme
    resource: ../raw/OXR-1.0.md
    kind: readme
    title: SoMark OXR-1.0 README
---

# OXR-1.0

**Reported:** SoMark's OXR (Optical Everything Recognition) is a 1.3B-parameter document parser converting PDFs and images to Markdown or JSON with layout coordinates. Its independent, replaceable layout model works alongside OXR's combined content recognition and reading-order model. SoMark says OXR was pretrained from scratch and post-trained using recursive self-improvement (RSI).[^oxr-readme]

## Architecture and outputs

The documented system separates layout analysis from recognition and reading order, which the same OXR model handles. Layout types, boundaries and grouping vary across domains. The source claims custom layout models can replace the built-in model but does not specify an integration contract or establish that arbitrary models work equally well; crop resolution and intermediate flow are not described. This is a related boundary of [layout-first modular parsing](task-layout-first-modular-parsing.md), because order is predicted during recognition rather than layout.[^oxr-readme]

The README lists 13 types: caption, footnote, formula, text, page footer, page header, picture, title, table, stamp, chemical equation, code block and chemical structure. Formulas and chemical equations use LaTeX (the latter mhchem `\ce`); tables use HTML or Markdown, chemical structures SMILES or images, and code blocks Markdown. Headers and footers are filtered by default.[^oxr-readme]

## Training and evaluation

**Reported:** The RSI loop targets weak or incorrectly handled samples, aiming to improve without human annotation. It is related to the [document-parser data flywheel](document-parser-data-flywheel.md), but the local text does not specify its data generation, verification, training algorithm or evaluation separation.[^oxr-readme]

SoMark claims first place on olmOCR-Bench, OmniDocBench and DocParsingBench, and the fastest open-source document parser in its RTX PRO 6000 speed test. These are vendor-reported promotional rankings, not independent verification or a universal leaderboard. The local text omits score vectors, benchmark versions, test conditions and uncertainty; the linked benchmark document and figures were not inspected, so comparisons to [layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) cannot be normalized.[^oxr-readme]

## Deployment and limits

The README describes Linux, NVIDIA BF16 and CUDA 13.0-compatible drivers, with 24 GB GPU memory for low-concurrency testing and at least 48 GB recommended for longer documents or higher concurrency. Docker is recommended; source deployment uses separate OXR, layout and parsing API services. The local API supports Markdown and JSON and the visual demo's temporary cache expires after an hour by default. The advertised free hosted API is not recommended by the vendor for production; assess privacy and retention separately before sending sensitive documents.[^oxr-readme]

The source calls the model open-source under a custom OXR license based on Apache 2.0 with additional terms. The license text is not in the capture and `raw/LICENSE` is absent; do not assume Apache-2.0 permissions.[^oxr-readme]

**Coverage:** inspected the supplied English README statically; no code, model, commands, benchmarks or service were run. The upstream repository, model weights, benchmark documentation, external architecture and RSI diagrams, benchmark plots, examples, API documentation and license were not retrieved. Diagrams and plots may contain material details absent from the text. Promotional badges, community links and decorative assets were excluded. No publication date, immutable upstream revision, technical paper or complete evaluation protocol is provided in the capture. These gaps make the concept draft.[^oxr-readme]

[^oxr-readme]: SoMark, [OXR-1.0 README](../raw/OXR-1.0.md), introduction; §§ Why OXR?, How it works, Quick Start, Citation, License. Inspected 2026-10-27; upstream revision and capture date unspecified.
