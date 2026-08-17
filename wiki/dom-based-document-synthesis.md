---
type: Method
title: DOM-based document synthesis
description: DOM-based document synthesis renders a typed logical document tree into pages and derives aligned structural labels from the laid-out DOM.
tags: [synthetic-data, document-parsing, provenance, rendering, layout-analysis]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:42:55Z }
sources:
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
  - id: ovisocr2-report
    resource: ../raw/2607.13639_OvisOCR2/main.tex
    title: OvisOCR2 Technical Report
---

# DOM-based document synthesis

DOM-based document synthesis is the controllable rendering method reported for Infinity-Parser2. A typed logical document tree retains native content, structure, style, and block-flow constraints; a browser lays it out and the system reads geometry and structured labels from that same laid-out DOM, aligning synthetic page pixels with their labels by construction.[^infinity-parser2-report]

## Inputs and rendering paths

The engine draws plain text, tables and formulas, charts, chemical strings, and images, then samples template-controlled page and element parameters such as layout mode, typography, writing direction, colors, margins, resolution, and spacing. Jittering parameter ranges makes visually varied documents while retaining logical structure.[^infinity-parser2-report]

Its two paths serve different purposes:

- **Fixed layout:** a VLM extracts boxes and attributes from a real exemplar, after which sampled content and styles are injected to reproduce its structure.
- **Flexible layout:** the engine constructs a DOM from typed nodes, then chooses a single- or multi-column/page layout while preserving explicit hierarchy and reading order.[^infinity-parser2-report]

For flexible layout, an off-screen browser measures each rendered element before placement. Elements may fully fit, split while preserving their configured flow constraint, or overflow to a later region; atomic blocks can trigger backward reflow rather than fragment. Dedicated renderers handle formulas, HTML/CSS tables, images, and fonts before measurement. The system then rasterizes pages and exports character, line, and cell boxes; element type and hierarchy; reading order; and native structured text.[^infinity-parser2-report]

## OvisOCR2 variant

OvisOCR2 reports a narrower HTML-based variant: a multimodal model turns mined hard samples into initial templates, an agent diversifies those templates, and Playwright renders page images while the same HTML source yields Markdown targets. Its serializer encodes visual regions as normalized DOM bounding boxes and uses layout-specific reading-order rules. This provides source-aligned synthetic labels, but its hard-sample selection, template quality, and agent constraints are not supplied for audit.[^ovisocr2-report]

## Provenance implications

The engine's synthetic flexible-layout labels are geometrically consistent with its own rendered pixels because both derive from the same DOM. That does **not** establish that labels match real-document conventions or that fixed-layout VLM-extracted structures are error-free; those depend on template choices, renderer behavior, and the VLM extraction stage.[^infinity-parser2-report]

The OvisOCR2 variant likewise aligns its targets to its rendered HTML source, not to an independently validated real-document annotation convention.[^ovisocr2-report]

## Trust limits

The report supplies an architectural description and a figure, not source code, templates, rendering configurations, input licenses, generated records, or a measured label-error analysis. Claims of exact geometry apply to rendered-DOM extraction, not to the semantic validity of source content or extrapolation to real documents.[^infinity-parser2-report]

## Relationships

- **Constructs:** synthetic portions of [Infinity-Doc2-5M](infinity-doc2-5m.md).[^infinity-parser2-report]
- **Used by:** [Document-parser data flywheel](document-parser-data-flywheel.md) to target uncovered layouts and element types.[^infinity-parser2-report]
- **Used by:** [Infinity-Parser2](infinity-parser2.md) through its reported training corpus.[^infinity-parser2-report]
- **Used by:** [OvisOCR2](ovisocr2.md) for hard-sample-directed HTML generation and source-aligned Markdown targets.[^ovisocr2-report]

[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local LaTeX source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex), including [synthesis engine](../raw/2607.07836_Infinity-Parser2/figures/data-engine-0704.pdf) (accessed 2026-08-17).
[^ovisocr2-report]: Lu et al., *OvisOCR2 Technical Report*, local LaTeX source at [main.tex](../raw/2607.13639_OvisOCR2/main.tex), including [data pipeline](../raw/2607.13639_OvisOCR2/figures/data_pipeline.png) (accessed 2026-08-17).
