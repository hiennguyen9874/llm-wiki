---
type: Benchmark
title: OmniParseBench
description: OmniParseBench is Datalab's pass/fail document-parsing benchmark whose headline score averages text, table, and layout families across 2,937 pages, with per-script, handwriting, degraded-scan, and math subsets.
tags: [benchmark, document-parsing, ocr, tables, layout-analysis, multilingual]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-30T03:30:00Z }
sources:
  - id: indra-ocr-card
    resource: ../raw/datalab-to-indra-ocr.md
    title: Indra OCR model card (datalab-to/indra-ocr)
  - id: opb-card
    resource: ../raw/ocr-benchmark-assets-2026-10-30/omniparsebench-card.md
    kind: dataset-card
    title: Omni Parse Bench dataset card
  - id: surya25-card
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
---

# OmniParseBench

OmniParseBench is Datalab's document-parsing benchmark: 16,288 pass/fail tests over 2,937 pages, where the headline score is the mean of the text, table, and layout test families. It is the protocol Datalab uses to position [Indra OCR](indra-ocr.md) against PaddleOCR's PP-StructureV3, PP-OCR text models, and Tesseract 5. The only local evidence is Indra OCR's model card, so this page describes the benchmark as that card reports it and is not an independent description of the upstream harness.[^indra-ocr-card]

## Reported structure

- **Families.** Text, tables, and layout carry the headline; separate math tests exist and are reported alongside it, and a per-script breakdown of the Latin, Chinese, Korean, Japanese kana, Devanagari, Bengali, Arabic, Hebrew, Georgian, Armenian, Thai, Lao, Khmer, Tamil, Telugu, Kannada, Malayalam, Gujarati, Gurmukhi, and Ethiopic subsets is published in the card.[^indra-ocr-card]
- **Sensitivity.** Most scripts have few tests, so a single test moves a script score by 2 to 8 points; the Chinese subset has 136 tests and Latin 9,406.[^indra-ocr-card]
- **Scoring provenance.** Indra OCR's rows come from the benchmark's own Indra OCR adapter and scorer (`omni-parse-bench` 1.0.0rc1, dataset revision `961c0f89`). The other engines' rows come from Datalab's separate runs of the same pages and scorer, not from those projects' own reporting.[^indra-ocr-card]
- **Family eligibility.** Engines that output lines rather than tables or layout blocks (PP-OCR text models, Tesseract) score 0 on tables and are not scored on layout, so their headline is undefined (`–`).[^indra-ocr-card]

## Reported comparison

x86, 4 vCPUs per engine, one page at a time, same pages and scorer, default settings. Higher is better except milliseconds.[^indra-ocr-card]

| Engine | Headline | Text | Tables | Layout | Median ms/page |
|---|---|---|---|---|---|
| Indra OCR, `auto` (text layer + OCR) | 66.7 | 46.7 | **61.1** | **92.2** | **212** |
| Indra OCR, OCR only | 61.2 | 40.7 | 52.7 | 90.3 | 344 |
| Indra OCR, `--math` | **71.4** | **62.7** | 59.6 | 92.0 | 357 |
| PaddleOCR PP-OCRv6 small text models only (RapidOCR) | – | 35.8 | 0.0 | – | 2,685 |
| PaddleOCR PP-StructureV3 | 58.4 | 55.6 | 47.8 | 71.7 | 40,958 |
| Tesseract 5 (Latin model) | – | 19.3 | 0.0 | – | 5,496 |

The load-bearing reading is conditional: without math, PP-StructureV3 leads on text (55.6 vs 46.7) while Indra OCR leads on headline, tables, and layout; with `--math`, Indra OCR leads on text as well (62.7). PP-StructureV3 takes roughly 190× the per-page time of Indra OCR's default mode. The card also notes the upstream leaderboard's own Tesseract run scores 17.6 on text rather than 19.3 quoted here, which indicates cross-run variation in the same protocol.[^indra-ocr-card]

Throughput runs one single-threaded worker per core on the same 300 pages, OCR mode, default settings (pages/s):[^indra-ocr-card]

| Engine | 4 cores | 8 cores | 16 cores | 32 cores |
|---|---|---|---|---|
| Indra OCR | **6.2** | **11.9** | **23.7** | **43.9** |
| PP-OCRv6 small text models (RapidOCR) | 0.65 | 1.24 | 2.42 | 4.28 |
| Tesseract 5 | 0.78 | 1.37 | 2.27 | 2.92 |
| PP-StructureV3 (upper bounds) | ≤ 0.022 | ≤ 0.044 | ≤ 0.089 | ≤ 0.18 |

## Dataset-card leaderboard

The dataset card captured on 2026-10-30 publishes the full results table: closed systems up to Datalab accurate at 94.1, and open-weight models served by Datalab from omni-parse-bench server images with each vendor's recommended defaults. Selected open rows (headline / text / tables / layout): chandra-ocr-2 90.1 / 87.4 / 87.4 / 95.4; MinerU2.5-Pro 87.1 / 77.4 / 92.1 / 91.7; Infinity-Parser2-Pro 87.0 / 83.3 / 84.1 / 93.5; Surya OCR 2.5 85.9 / 83.8 / 78.3 / 95.7; MiniCPM-OCR-1.0 83.2 / 72.8 / 89.1 / 87.6; LightOnOCR-3-4B 82.9 / 83.9 / 70.8 / 94.0; PaddleOCR-VL-1.6 78.7 / 61.7 / 83.7 / 90.7. Parsers that return no layout (olmOCR-2, Nanonets-OCR2-3B, Tesseract) have no headline, and closed models marked `*` helped create or verify some tests. Every verdict is published in `results.parquet`, which was not downloaded here.[^opb-card] Cross-benchmark context for these models is in [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md).

**Reported, unreconciled:** the dataset card lists Indra OCR at 69.5 / 60.3 / 58.1 / 90.1 and Surya OCR 2 at 83.1 / 80.6 / 74.3 / 94.3, while the Indra card's `auto` row gives 66.7 / 46.7 / 61.1 / 92.2 and the Surya 2.5 card's own rerun of Surya 2 gives 83.3 / 81.0 / 74.3 / 94.5. Run date, mode, and package version can differ; no source maps the rows to each other.[^opb-card][^indra-ocr-card][^surya25-card]

## Protocol caveats

- **Asymmetric execution.** The Indra OCR rows were produced with the benchmark's own adapter; the competing rows were produced by Datalab running each engine at default settings. That is a vendor-run comparison under a shared scorer, not a neutral third-party evaluation.[^indra-ocr-card]
- **Partial PP-StructureV3 coverage.** Its row omits 19 pages because one of its 150 shards stalled for six hours on its first page, so the row covers 2,918 of 2,937 pages. Its throughput figures come from a time-capped run over a different subset and are therefore upper bounds.[^indra-ocr-card]
- **Run-level noise.** Median latency varies by about 15% between runs of the same code, so the card's guidance is to compare engines within one run rather than across runs. Faster settings exist for the baselines but were not scored for accuracy.[^indra-ocr-card]
- **Unscored alternatives.** Tesseract with the `eng` model and one thread is quoted at 3.4 s/page and PP-StructureV3 with reduced stages at 10.5 s/page, but these are runtime remarks without accuracy scores.[^indra-ocr-card]
- **Adjacent protocols.** [olmOCR-bench](indra-ocr.md) results in the same card come from Datalab's own harness and must not be merged with these numbers; [OmniDocBench](https://github.com/opendatalab/OmniDocBench) runs quoted in the card (text edit distance and table TEDS) are a third, separate protocol.[^indra-ocr-card]

## Reproduction as documented

The card documents a harness script in the Indra repository: clone, `pip install indra-ocr 'omni-parse-bench[benchmark]'`, then `python bench/opb_indra.py --out runs/opb_auto --mode auto --procs 8`, with `--mode ocr`, `--math`, `--suites`, `--limit`, and `--models` variants. It writes `summary.json` (the benchmark's summary plus median and p90 ms/page) and `pages.jsonl`. The card warns that this script gives each page one thread while the tables above give each page four, so scores can differ by a few tenths of a point and timings will differ more. None of this was executed here.[^indra-ocr-card]

## Trust limits

- No OmniParseBench test content, ground truth, scoring code, or per-test verdicts are present locally; the only leaderboard snapshot is the 2026-10-30 dataset-card capture. Every structural and numeric statement above is **reported** by Datalab's model or dataset cards.[^indra-ocr-card][^opb-card]
- The card does not define how a text, table, or layout test is judged as pass/fail, how the page sample was drawn, or what uncertainty surrounds the headline, so rankings at differences of a few points should not be treated as established.[^indra-ocr-card]
- Because the retained comparison is single-run and vendor-executed, the defensible claim is that Indra OCR is far faster and competitive-to-ahead on this benchmark as its vendor ran it — not that any engine is globally best at document parsing.[^indra-ocr-card]

## Relationships

- **Used by:** [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md) as one of its per-dataset sections.[^opb-card]
- **Benchmarks:** [Indra OCR](indra-ocr.md), whose headline, text, table, layout, math, throughput, and per-script results this page catalogs.[^indra-ocr-card]
- **Compares against:** [PP-StructureV3](pp-structurev3.md), PP-OCRv6 text models, and Tesseract 5 as the three baselines in the reported tables.[^indra-ocr-card]
- **Distinct from:** [MDPBench](mdpbench.md) and [Real5-OmniDocBench](real5-omnidocbench.md), which use different page sets, capture conditions, and metric definitions; scores must not be transferred between them.

[^opb-card]: Datalab, [Omni Parse Bench dataset card](../raw/ocr-benchmark-assets-2026-10-30/omniparsebench-card.md), §§ Results, Results details (fetched 2026-10-30 per `manifest-text.json`).
[^surya25-card]: Datalab, [Surya OCR 2.5 model card](../raw/surya-ocr-2.5-hf.md), § Benchmarks › OmniParseBench.
[^indra-ocr-card]: Datalab, *Indra OCR* model card (`datalab-to/indra-ocr`), local capture [datalab-to-indra-ocr.md](../raw/datalab-to-indra-ocr.md), sections *Indra OCR*, *Languages*, *Math*, *Benchmarks* (subsections *OmniParseBench*, *olmOCR-bench*, *Throughput*, *Reproducing*) (accessed 2026-10-25).
