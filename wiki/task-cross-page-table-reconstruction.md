---
type: Concept
title: "Task: Cross-page table reconstruction"
description: Cross-page table reconstruction stitches table fragments separated by page boundaries into one table using per-page parses and page-pair continuation reasoning.
tags: [task, table-recognition, document-parsing, multi-page, ocr]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:23:54Z }
stale_after: 2027-04-25
sources:
  - id: ovisocr3-model-card
    resource: ../raw/ATH-MaaS-OvisOCR3.md
    kind: model-card
    title: OvisOCR3 model card
---

# Task: Cross-page table reconstruction

Cross-page table reconstruction detects that a table continues across a page boundary and merges the fragments into one structurally complete table, while preserving which source pages contributed. It differs from single-table [structure recognition](task-table-structure-recognition.md): the input is adjacent page images plus their per-page parses, and the central ambiguity is continuation rather than cell geometry.[^ovisocr3-model-card]

## OvisOCR3's two-stage procedure

OvisOCR3 implements the task with the same checkpoint in both stages:[^ovisocr3-model-card]

1. **Page parsing.** Parse each page independently with `document_markdown.txt` or `document_structured.txt`. For structured output, concatenate each element's `content` in reading order to obtain Markdown while preserving HTML tables, formulas, and image references.
2. **Table reconstruction.** Supply two adjacent page images and their parsed Markdown with `crosspage_table.txt`. The model decides whether a table continues across the boundary and reconstructs continued fragments as a single HTML table; otherwise it returns a negative prediction.

The result is a JSON array. Each record carries `source_pages`, using input-local 1-based page numbers, and `html`, containing one complete table. Images inside a reconstructed table retain page-qualified references such as `page_1/images/bbox_100_200_300_400.jpg`.[^ovisocr3-model-card]

When no cross-page table exists, the specified response is:[^ovisocr3-model-card]

```json
[{"source_pages": [], "html": "No cross-page table exists between these pages."}]
```

## Recursive merging beyond two pages

For tables spanning more than two pages, stage 2 is applied recursively, processing adjacent pairs from the end of each consecutive table-bearing sequence toward its beginning. After each merge, the reconstructed table is written into the earlier page and that page's Markdown is re-rendered before the next step, keeping the image and text consistent. The card's example merges pages 2 and 3 first, then pairs the updated page 2 with page 1. Each step still uses only two page images and preserves the original source-page associations.[^ovisocr3-model-card]

The supplied `document_crosspage.py` supports either stage-1 prompt, converts structured JSON to Markdown before reconstruction, and requires `beautifulsoup4`, `markdown-it-py`, and Playwright with Chromium. It writes `document.md`, per-page Markdown, raw responses, and `result.json` with table provenance and processing errors to a new output directory. The card does not include the script locally.[^ovisocr3-model-card]

## Guardrails and failure points

The card's example checks that both page Markdowns contain a `<table>` before invoking stage 2, requires stage-1 finish reasons of `stop` or `length`, cleans repeated tails, strips Markdown/HTML code fences, rejects empty page Markdown, and requires a `stop` finish reason for the reconstruction call. These are caller-side checks, not guarantees from the model.[^ovisocr3-model-card]

The procedure inherits stage-1 parsing quality and depends on correct page order. Missing table fragments, inconsistent page context, or truncated generations can produce incorrect merges, and recursive merging can compound those errors. Results should be reviewed before critical use.[^ovisocr3-model-card]

## Reported evaluation

The OvisOCR3 card reports the following author-run comparison. Relation F1 is shown with precision/recall in parentheses.[^ovisocr3-model-card]

| System | CrossTabBench relation F1 (P/R) ↑ | CrossTabBench reconstruction TEDS ↑ | MPDocBench-Parse truncated-table TEDS ↑ |
|---|---:|---:|---:|
| PaddleOCR-VL-1.6 | 42.61 (90.13/27.90) | 24.24 | 83.39 |
| Logics-Parsing-V3 | 44.55 (90.63/29.53) | 26.10 | 88.05 |
| MinerU2.5-Pro | 59.14 (93.81/43.18) | 41.02 | 91.44 |
| MinerU2.5-Pro + MinerU-PoPo | 54.76 (97.40/38.09) | 36.42 | 91.87 |
| Qwen3.8-Max | 94.47 (90.19/99.19) | **91.71** | 89.57 |
| **[OvisOCR3](ovisocr3.md)** | **97.07** (96.20/97.96) | 89.66 | **92.04** |

**Synthesis:** The table separates two capabilities. OvisOCR3 leads relation F1 and the truncated-table TEDS column, while Qwen3.8-Max leads reconstruction TEDS. Several systems show high relation precision with low recall—PaddleOCR-VL-1.6 detects few continuations but is usually right when it does—so relation F1 alone does not establish reconstruction quality. The card gives no benchmark construction details, split, prompt configuration, or per-page error analysis.[^ovisocr3-model-card]

## Related systems

The retained wiki records cross-page table merging claims for [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) and [MinerU2.5-Pro](mineru2-5-pro.md), including the latter's unresolved status between its capability list and quick-start note. Those pages retain their own evidence and limits; they are not merged into OvisOCR3's benchmark protocol here.

## Relationships

- **Extends:** [Task: Table structure recognition](task-table-structure-recognition.md) from single-table grid recovery to page-boundary continuation and merge.
- **Part of:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) as an optional multi-image stage rather than a separate deployment.
- **Implemented by:** [OvisOCR3](ovisocr3.md), which uses one checkpoint for page parsing and page-pair reconstruction.[^ovisocr3-model-card]
- **Related:** [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) and [MinerU2.5-Pro](mineru2-5-pro.md) also document cross-page table handling, with different pipeline designs and evidence.
- **Evaluated by:** CrossTabBench and MPDocBench-Parse, as reported in the OvisOCR3 card; no separate benchmark concepts are retained because their construction is not locally documented.[^ovisocr3-model-card]

[^ovisocr3-model-card]: ATH-MaaS, *OvisOCR3 model card*, local source at [ATH-MaaS-OvisOCR3.md](../raw/ATH-MaaS-OvisOCR3.md), especially § Capabilities, § Performance › Cross-Page Table Reconstruction, and § Task-Specific Usage › Cross-Page Table Reconstruction (accessed 2026-10-25). The referenced `prompts/crosspage_table.txt`, `document_crosspage.py`, and model files are absent from the local bundle.
