---
type: Benchmark
title: MarathonDocBench
description: MarathonDocBench is a 100-document benchmark for hundred-page parsing with annotated cross-page text, tables, and document structure.
tags: [ml, benchmark, document-parsing, ocr, long-context]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:01:00Z }
stale_after: 2027-04-27
sources:
  - id: report
    resource: ../raw/Unlimited-OCR-2.pdf
    kind: paper
    title: Unlimited OCR Works 2
  - id: readme
    resource: ../raw/Unlimited-OCR-github.md
    kind: documentation
    title: Unlimited OCR GitHub README capture
---

# MarathonDocBench

MarathonDocBench is the [Unlimited OCR 2](unlimited-ocr-2.md) authors' benchmark for long-document parsing. **Reported:** it contains 100 documents of 103–300 pages and 205,000 annotated layout elements, with a median of 178 pages; it emphasizes cross-page structural continuity as well as page recognition.[^report]

## Construction and metrics

**Reported:** page-by-page parser output initializes boxes, block types, hierarchy, reading order and cross-page text/table continuations; human annotators refine structure. Transcriptions are initialized by the parser and checked through iterative VLM refinement, with flagged disagreements adjudicated by humans. Figure 2 reports cross-page text in 89% of documents, 36.3 text blocks per document, and cross-page tables in 82%, 13.2 tables per document; corresponding MPDocBench values are 47%, 3.2, 11% and 0.23.[^report]

The paper follows MPDocBench-style text and reading-order edit distance, formula CDM, table TEDS and figure F1, adding T-TextEdit and T-TableTEDS for cross-page continuations and an aggregate overall score. The exact aggregate formula, dataset selection and detailed baseline prompts are not described in the supplied report.[^report]

## Reported comparison and limits

**Reported:** Unlimited OCR 2 reaches overall 77.06, text edit 0.104, T-TextEdit 0.123, formula CDM 87.93, table TEDS 74.81, T-TableTEDS 71.11, figure F1 71.79, reading-order edit 0.147 and heading TEDS 48.20. Kimi-K3 is the strongest listed comparator overall at 33.74; these results originate from the benchmark creator and are not independently reproduced. Table 2 says original Unlimited OCR is not evaluated because of a 40-page limit, despite Figure 5 plotting it at zero.[^report]

The GitHub README capture documents an evaluation client and output conversion but the client, converter, dataset and annotations are not present in the supplied artifacts and were not inspected or run. Benchmark licensing and public availability are not established by these captures.[^readme]

## Relationships

- **Evaluates:** [Unlimited OCR 2](unlimited-ocr-2.md), with author-run results.[^report]
- **Related to:** [Task: Cross-page table reconstruction](task-cross-page-table-reconstruction.md), which targets a structural behavior measured by T-TableTEDS.[^report]

[^report]: Baidu ERNIE Team, [Unlimited OCR Works 2](../raw/Unlimited-OCR-2.pdf), §3.1.2 and Figure 2, §§5.1–5.2, Table 2 and Figure 5.
[^readme]: Baidu, [Unlimited OCR GitHub README capture](../raw/Unlimited-OCR-github.md), § Evaluation.
