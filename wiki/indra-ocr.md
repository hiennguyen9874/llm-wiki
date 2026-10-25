---
type: Model System
title: Indra OCR
description: Indra OCR is Datalab's CPU-only ONNX document parser that converts PDFs and images into Markdown, text, or boxed JSON using layout blocks, a script-routing line classifier, and four line recognizers.
tags: [ocr, document-parsing, onnx, cpu-inference, multilingual, handwriting, markdown, lightweight-models]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:24:25Z }
sources:
  - id: indra-ocr-card
    resource: ../raw/datalab-to-indra-ocr.md
    title: Indra OCR model card (datalab-to/indra-ocr)
---

# Indra OCR

Indra OCR is Datalab's OCR system that runs on CPUs through ONNX Runtime and turns PDFs and images into Markdown, plain text, or JSON with boxes. Its card positions it as a speed-first complement to Datalab's larger generative models: it adds layout labels and reading order to line-level transcription, including a hybrid path that reuses a digital PDF's existing text layer and OCRs only what the layer is missing.[^indra-ocr-card]

## Pipeline as documented

The card describes a modular pipeline rather than one network: a layout stage assigns each line and block a box, a label, and a reading order; a line classifier routes each line to one of four script recognizers; and orientation or skew is corrected before recognition so sideways, inverted, and tilted pages still read.[^indra-ocr-card]

- **Script recognizers.** `rec.onnx` covers Latin-script languages, Cyrillic, Greek, and Latin-script handwriting; `rec_cjk.onnx` covers Chinese, Japanese, and Korean; `rec_rtl.onnx` covers Arabic, Persian, Urdu, Pashto, Kurdish, and Hebrew, emitting lines in logical order; `rec_world.onnx` covers Devanagari, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Gurmukhi, Odia, Thai, Lao, Khmer, Myanmar, Sinhala, Georgian, Armenian, and Ethiopic. When the classifier is unsure, the main recognizer also reads the line and the more confident reading wins.[^indra-ocr-card]
- **Page routing.** `mode=auto` (the default) reads the text layer where it passes internal checks and OCRs elsewhere; `ocr` never reads the text layer; `text` uses it even when checks fail. `--no-image-ocr` suppresses OCR of text inside images on text-layer pages. `page.source` reports which path ran: `text`, `ocr`, `hybrid`, or `error`.[^indra-ocr-card]
- **Output contract.** Each page carries `markdown` (headings as `##`, lists, and tables as HTML), `text`, `lines` as `Line(box, text, conf)` in image pixels, `blocks` as `{label, bbox, text}` in reading order, plus `rotation`, `skew`, `vertical`, `timings`, and a `note` explaining the routing decision. Block labels are `Text`, `Section-Header`, `Page-Header`, `Page-Footer`, `List-Group`, `Table`, `Caption`, `Footnote`, `Table-Of-Contents`, and `Form`; page headers and footers are dropped unless `--keep-furniture` is set.[^indra-ocr-card]

## Packaging and operation

`pip install indra-ocr` requires Python 3.10+ and installs ONNX Runtime, OpenCV, and pypdfium2 with no PyTorch; the card reports testing on Linux x86_64/aarch64 (Python 3.10–3.13) and macOS Apple silicon. Default models total about 76 MB (30 MB of networks plus 46 MB of language models for unsure lines) and download from Hugging Face on first run, overridable with `INDRA_OCR_MODEL_DIR` or `--model-dir`.[^indra-ocr-card]

The CLI takes PDFs and images (PNG, JPEG, TIFF, BMP, WebP; one page per TIFF frame) and offers `--format [md|text|json]`, `--mode [auto|ocr|text]`, `--dpi` (default 200), `--max-pages`, `--password`, `--cores`, `--math`, `--timings`, and `--out DIR`. It continues past unreadable files and exits 1 if any failed. The Python API is `indra_ocr.load(threads=, dpi=, mode=, image_ocr=, furniture=, math=)` returning a converter whose `convert`/`ocr` yield pages, plus `indra_ocr.convert_many` for one single-threaded worker process per core; `indra-ocr-viewer` serves a local viewer on port 8765 that keeps files on the machine.[^indra-ocr-card]

## Language coverage

The card reports measuring 95 languages on held-out printed pages: 83 at character F1 0.90 or higher and 67 at 0.95 or higher. Per-script OmniParseBench scores are reproduced below because the test counts are small and one test can move a score by 2–8 points.[^indra-ocr-card]

| Script (tests) | Score | Script (tests) | Score |
|---|---|---|---|
| Latin (9,406) | 61.6 | Thai (39) | 87.2 |
| Chinese (136) | 64.0 | Lao (52) | 96.2 |
| Korean (24) | 79.2 | Khmer (34) | 70.6 |
| Japanese kana (19) | 57.9 | Tamil (25) | 84.0 |
| Devanagari (23) | 69.6 | Telugu (33) | 87.9 |
| Bengali (40) | 77.5 | Kannada (48) | 93.8 |
| Arabic (13) | 69.2 | Malayalam (40) | 65.0 |
| Hebrew (30) | 80.0 | Gujarati (15) | 80.0 |
| Georgian (14) | 100 | Gurmukhi (31) | 64.5 |
| Armenian (60) | 100 | Ethiopic (43) | 100 |

Two script-specific behaviours matter for retrieval. Vertical Chinese and Japanese pages are read turned a quarter turn so each column becomes a line for the CJK recognizer, detected by an orientation model on scans and by the text layer on digital PDFs. For digital PDFs the card reports checking text mode on 1,125 pages from 75 language families and retaining at least 98% of each family's characters on pages whose layer passes the checks, including right-to-left scripts.[^indra-ocr-card]

## Reported quality and speed

| Protocol | Result |
|---|---|
| [OmniParseBench](omniparsebench.md) headline, default `auto` | 66.7 (text 46.7, tables 61.1, layout 92.2; 212 ms median/page) |
| OmniParseBench headline with `--math` | 71.4 (text 62.7, tables 59.6, layout 92.0; 357 ms median/page) |
| OmniParseBench OCR-only mode | 61.2 (text 40.7, tables 52.7, layout 90.3; 344 ms median/page) |
| OmniParseBench Chinese subset (136 tests) | 64.0, versus 65.4 for PP-OCRv5 mobile Chinese and 68.4 for PP-StructureV3 |
| OmniParseBench throughput (default OCR mode) | 6.2 / 11.9 / 23.7 / 43.9 pages/s on 4 / 8 / 16 / 32 x86 cores |
| OmniDocBench v1.5, OCR only | text edit distance 0.114 English, 0.237 simplified Chinese; table TEDS 0.47 |
| olmOCR-bench, Datalab's own harness | headers/footers 91.2, multi-column 70.0, long tiny text 67.9, tables 60.5, old scans 20.0 |

All of these are vendor-reported or vendor-run and were not reproduced here. The OmniParseBench comparison, engine-by-engine differences, and protocol caveats are recorded in [OmniParseBench](omniparsebench.md); the olmOCR-bench rows are Datalab's own harness against its own Tesseract 4 run (headers/footers 35.5, multi-column 70.4, long tiny text 64.0, tables 1.0, old scans 18.4), so they are not comparable to third-party olmOCR-bench leaderboards.[^indra-ocr-card]

`--math` is off by default; when enabled, a small classifier selects math lines and a second recognizer emits inline LaTeX. The card reports a net trade-off: headline, text, and math-test scores rise while table scores drop 1.5 points because numbers in some cells are read as math, and throughput falls about 30% on 4 cores and 38% on 32 cores.[^indra-ocr-card]

## Limitations

The card is explicit that Indra OCR targets clean print, not degraded or complex material:[^indra-ocr-card]

- **Complex tables.** Merged or spanning cells, wrapped cell text, nested headers, and tables without ruling lines can land in wrong rows or columns; simple grid tables read well.
- **Handwriting.** Handwritten pages read but poorly: 25.2% on OmniParseBench handwriting tests and about a third of words on held-out handwritten pages, worst for cursive and faint pencil.
- **Degraded scans.** Old, faded, or low-resolution scans score 29.5% on the corresponding OmniParseBench tests.
- **Unsupported scripts.** Syriac, Tibetan, Mongolian, Santali, Meitei, and other unlisted scripts work only through a digital PDF's text layer; Khmer and Malayalam OCR are called fair (65–71); written Cantonese characters are absent from the Chinese recognizer.
- **Diacritic-heavy Latin.** Kurmanji, Czech, Lithuanian, Icelandic, Turkish, and Slovak sometimes get a neighbouring diacritic (for example ñ for ň); English, French, German, and Spanish are said to be unaffected.
- **Geometry.** Vertical pages order columns right-to-left and tiers top-to-bottom but can misorder newspaper articles that wind across tiers; vertical scans read worse than horizontal ones; very wide banner-shaped pages and labels inside engineering drawings read poorly; pages above 100 megapixels at 200 dpi are rendered at a lower dpi, risking small text.

For these cases the card redirects to [Chandra OCR 2](chandra-ocr-2.md) on Datalab's managed platform, which it describes as the higher-accuracy option, alongside a batch service the card says handles 1B+ pages per day with zero data retention by default, SOC 2 Type 2, and custom BAAs. Those platform claims are marketing statements in the same source and were not inspected further.[^indra-ocr-card]

## Licensing

The code is Apache 2.0 while the model weights use a modified OpenRAIL-M licence: free for research, personal use, and startups under $20M funding or revenue, not usable competitively against Datalab's API, with broader commercial terms on Datalab's pricing page.[^indra-ocr-card]

## Contradictions

- The introduction describes Indra OCR as a "1M-parameter OCR model", but the installation section gives about 1.25M parameters for the Latin recognizer `rec.onnx` and 7.3M for all default models together. The card does not state what the "1M" figure counts, so no single parameter count is asserted here.[^indra-ocr-card]
- The introduction claims "80+ languages" while the language section reports 95 languages measured with 83 above 0.90 character F1. The two figures appear to describe advertised support versus evaluated coverage rather than a measured conflict, but the card does not reconcile them explicitly.[^indra-ocr-card]

## Coverage and trust limits

- Only the model card is available locally. It documents no network architecture, training data, training procedure, evaluation code, or prompts, so the architecture above is what the card gives at the pipeline-component level and nothing deeper.[^indra-ocr-card]
- Five referenced assets — the Datalab logo, `assets/throughput.png`, `assets/speed_score.png`, and two example page images under `assets/examples/` — are not present in `raw/`, so their visual content was not inspected. The numeric tables carry the same information and are the basis for the figures above.[^indra-ocr-card]
- The card links an external code repository, `EXAMPLES.md`, and separate licence files that are not part of this bundle; no install, run, or benchmark was executed. Every performance claim is **reported**, not **observed** or **reproduced**.[^indra-ocr-card]

## Relationships

- **Uses:** ONNX Runtime, pypdfium2, OpenCV, and the Hugging Face Hub for weights, credited as its open-source dependencies.[^indra-ocr-card]
- **Contrasts with:** [Chandra OCR 2](chandra-ocr-2.md), which Datalab positions as the accuracy option for handwriting, math, complex tables, and degraded scans while Indra OCR targets CPU speed.[^indra-ocr-card]
- **Benchmarked by:** [OmniParseBench](omniparsebench.md), whose text, table, layout, handwriting, degraded-scan, per-script, and throughput results form most of the reported evidence here.[^indra-ocr-card]
- **Shares a stage shape with:** [PP-StructureV3](pp-structurev3.md), the full PaddleOCR pipeline the card compares against, and PP-OCR text models and Tesseract 5, the comparison baselines in its benchmark tables.[^indra-ocr-card]

[^indra-ocr-card]: Datalab, *Indra OCR* model card (`datalab-to/indra-ocr`, `library_name: onnx`, OpenRAIL-M weights), local capture [datalab-to-indra-ocr.md](../raw/datalab-to-indra-ocr.md), sections *Indra OCR*, *Quickstart*, *License*, *Installation*, *Usage*, *Output*, *Languages*, *Limitations*, *Math*, *Benchmarks*, and *Credits* (accessed 2026-10-25).
