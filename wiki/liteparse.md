---
type: Tool
title: LiteParse
description: LiteParse is run-llama's Apache-2.0, model-free PDF parser that extracts spatial text with bounding boxes and optionally merges Tesseract or HTTP-server OCR into Markdown, JSON, or text.
tags: [ocr, document-parsing, pdf, markdown, model-free, layout-analysis, rag]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:24:46Z }
sources:
  - id: liteparse-readme
    resource: ../raw/liteparse.md
    title: LiteParse README
  - id: opendataloader-pdf-readme
    resource: ../raw/opendataloader-pdf.md
    title: OpenDataLoader PDF README
  - id: marker-readme
    resource: ../raw/marker.md
    title: Marker README
---

# LiteParse

LiteParse is run-llama's Apache-2.0 document-conversion tool, written in Rust with PDFium as its extraction core. Its stated design target is fast, light, fully local parsing: no LLM, no layout model, and no cloud dependency, producing spatial text with bounding boxes plus rule-based Markdown reconstruction. OCR is optional and plugs in either as bundled Tesseract or as any server implementing a small HTTP contract. The README explicitly defers dense tables, multi-column layouts, charts, handwriting, and scans to LlamaParse, the same vendor's commercial cloud parser.[^liteparse-readme]

## Pipeline and architecture

The documented flow is: non-PDF inputs are converted first (Office formats through LibreOffice; images natively via Rust crates since v2.8.0, so ImageMagick is no longer required), PDFium extracts the text layer, selective OCR runs only where needed, OCR results merge with native text, and a "grid projection" step reconstructs spatial layout before rendering JSON, text, or screenshots.[^liteparse-readme]

The Markdown path is described as classifying each page into blocks — `heading`, `paragraph`, `list_item`, `code`, `table`, `grid_fallback`, `rule`, `figure` — and rendering them. Table cells are objects with their own `bbox`, taken from the drawn grid cell for ruled tables and from the span extent for borderless ones; cells inserted only to square off a ragged grid carry no `bbox`. Coordinates use a top-left, 72-DPI viewport space. The README states this mode is "purely heuristics and rule-based" and that complex documents may not render perfectly.[^liteparse-readme]

The same core ships through four interfaces: `napi-rs` Node.js/TypeScript bindings, `PyO3` Python bindings, `wasm-bindgen` browser bindings (no CLI), and a `lit` CLI installed by npm, pip, or cargo. A Python/Node "worker pool" mode runs parses in persistent worker processes because PDFium serializes concurrent parses, and adds hard per-parse timeouts that kill and name a rogue document. Platform claims are Linux, macOS (Intel and ARM), and Windows.[^liteparse-readme]

## OCR modes

Tesseract is bundled and enabled by default (`--ocr-language eng`, offline via `TESSDATA_PREFIX` or `--tessdata-path`). Higher-accuracy engines are attached by running a local HTTP OCR server that answers `POST /ocr` with `{results: [{text, bbox, confidence}]}`; the repository ships EasyOCR and PaddleOCR wrapper examples, and every benchmark's PaddleOCR row uses a PP-OCRv5 mobile detector plus English recognizer served over that API on ONNX Runtime, reported as 20–40× faster per page than the sibling PaddleOCR wrapper on CPU-only machines.[^liteparse-readme]

## Outputs and optional extraction fields

`--format` accepts `json`, `text`, or `markdown`; defaults are 1,000 pages maximum, 150 DPI rasterization, and `placeholder` image mode. Most structured detail is opt-in, so default JSON stays small: `--extract-blocks` (the classified blocks the Markdown renderer used, in reading order), `--extract-images` (image bytes and metadata written to disk, never embedded in JSON), `--extract-vector-graphics` (shapes plus merged horizontal/vertical line segments), `--extract-structure-tree` (tagged-PDF logical structure), `--extract-annotations`, `--extract-form-fields` (AcroForm widgets), `--extract-text-metadata`, `--extract-content-bounds`, `--extract-xfa-packets`, and `extract_document_metadata` (`/Info`, dates, PDF version, encryption permissions, signatures, XMP capped at 64 KiB, skipped above 16 MiB and in WASM). API-only `/Info` creator and producer values never appear in CLI JSON. Library opt-ins mirror these flags as `extract_images` / `extractImages` / `extractVectorGraphics` and so on.[^liteparse-readme]

## Routing, batch, and screenshots

`lit is-complex` is a text-layer-only pass intended for routing, rejection, or cost estimation. It prints per-page JSON to stdout, a `SIMPLE`/`COMPLEX` verdict to stderr, and exits non-zero when any page needs OCR; each page carries `needs_ocr` plus reasons (`scanned`, `no-text`, `sparse-text`, `embedded-images`, `garbled`, `vector-text`, `annotation-text`). Because it is a shell predicate, the README's documented pattern is `lit is-complex doc.pdf --quiet && lit parse doc.pdf --no-ocr`. `lit batch-parse` converts a directory (optionally recursive, optionally filtered by extension), and `lit screenshot` renders pages at a chosen DPI while drawing AcroForm field appearances into the raster, optionally reporting `is_solid_fill` and detected solid rectangles and lines.[^liteparse-readme]

## Reported benchmarks

All figures below are project-reported: run on one machine from one command, with each benchmark's own unmodified evaluator, every competitor at its latest release as of 2026-09-09, LiteParse v2.14.4, hyperlinks off (`--no-links`) because all three ground truths are plain text, and otherwise default `lit parse --format markdown`. Hardware was an Apple M2 Max, 12 cores, 32 GB.[^liteparse-readme]

| Benchmark | Metric | No OCR | + Tesseract | + PaddleOCR | Best other model-free tool |
|---|---|---:|---:|---:|---:|
| ParseBench (2,049 docs) | mean of 5 categories | 0.364 | 0.380 | 0.389 | pdf-inspector 0.283 |
| opendataloader-bench (200 docs) | NID + TEDS + MHS | 0.886 | 0.896 | 0.901 | opendataloader 0.842 |
| olmOCR-bench (1,403 pages) | % tests passed | 39.6 | 41.1 | 42.2 | pdf-inspector 33.7 |

The per-category detail is more informative than the aggregate. On ParseBench, LiteParse + PaddleOCR scores 0.430 tables but 0.013 charts, 0.787 content faithfulness, 0.402 semantic formatting, and 0.314 visual grounding, with every tested tool near zero on charts. On olmOCR-bench the same row scores 99.9 on `baseline`, 69.1 `multi_column`, 54.0 `table_tests`, 46.4 `long_tiny_text`, 19.4 `old_scans`, and 0.0 on both math categories, which the README attributes to the absence of a LaTeX path; OCR also lowers `headers_footers` (55.8 → 48.7) because OCR recovers letterhead text from logo images where the repeated-line filter cannot fire. On opendataloader-bench, the opendataloader row in LiteParse's own table reaches only 0.483 TEDS against LiteParse's 0.832, at comparable reading order (0.912 vs 0.932).[^liteparse-readme]

## Contradictions

Two re-used public harnesses disagree with these numbers by a wide margin, and the available sources do not let the wiki reconcile them.

- **opendataloader-bench.** LiteParse reports 0.886 overall / 0.917 NID / 0.818 TEDS / 0.821 MHS for its no-OCR mode, while the OpenDataLoader README's own run of the same harness lists liteparse at 0.576 overall / 0.866 reading order / **0.000** table / **0.000** heading, at 1.061 s/page.[^liteparse-readme][^opendataloader-pdf-readme] The gap is concentrated in table and heading extraction, so the two runs plausibly used different tool versions or non-default flags; neither source states which liteparse build or options the other used.
- **olmOCR-bench.** LiteParse reports 39.6 (no OCR), 41.1 (Tesseract), and 42.2 (PaddleOCR) as an average of per-category pass rates. The Marker README's comparison lists liteparse at **22.4** overall (27.3 digital-only) and liteparse without OCR at **20.4** (25.0), also describing liteparse as having "no layout model" that "collapses on anything non-linear".[^liteparse-readme][^marker-readme] LiteParse does implement a geometry-based block classifier and ordering, so the two sources also disagree about the presence of layout logic, not only about the score.

Neither contradiction is resolvable from the inspected material: both competing tables are vendor-published, the liteparse versions and category handling in each are unstated, and no run was reproduced here. Treat every LiteParse score as conditional on its harness configuration rather than as a leaderboard position.

## Evidence limits

- The README, source tree, benchmark harnesses, and packaged binaries were not inspected or executed for this page. Architecture, flags, defaults, and platform claims are reported documentation, not observed implementation.[^liteparse-readme]
- Benchmark numbers are project-reported and self-run, including the competitor rows and the choice of model-free competitors; the comparison deliberately excludes LLM-based parsers that would win on difficult pages.
- Throughput cannot be compared across sources: the README's "~2–5 ms per page" is a PDFium text-extraction claim per page, while competitor tables publish concurrent pages/second on other hardware (the Marker README, for instance, lists 1,721 pg/s for liteparse without OCR on a B200 host).[^liteparse-readme][^marker-readme]
- The README's own recommendation defers dense tables, multi-column layouts, charts, handwriting, and scanned PDFs to the commercial LlamaParse service, so LiteParse is documented as a fast baseline rather than a quality ceiling.
- Text and tables here cover the v2 Rust rewrite; the README points to a separate branch for "LiteParse V1", whose behavior is out of scope.

## Relationships

- **Uses:** PDFium for text extraction and rendering, Tesseract (via `tesseract-rs`) for bundled OCR, LibreOffice for Office-format conversion, and any HTTP OCR server for stronger recognition.[^liteparse-readme]
- **Compared with:** [OpenDataLoader PDF](opendataloader-pdf.md), the closest architectural analogue — both use PDF objects and geometry with no required model — although OpenDataLoader's project benchmark and LiteParse's own run of that benchmark disagree sharply. Both also use the same benchmark harness (opendataloader-bench) and the same corpus family, making them the most directly comparable pair in this wiki.[^liteparse-readme][^opendataloader-pdf-readme]
- **Compared with:** [Marker](marker.md), which keeps a layout model on CPU in its fast mode and reports higher olmOCR-bench scores at lower throughput; the two projects' cross-ranking of LiteParse is recorded under Contradictions.[^marker-readme]
- **Related to:** [PDF-to-Markdown tool selection](pdf-to-markdown-tool-selection.md), which places LiteParse in the model-free, CPU-bound branch of that decision.
- **Related to:** [PDF-to-Markdown parser architectures](pdf-to-markdown-parser-architectures.md), whose geometry-first versus model-first split applies to LiteParse's rule-based block classifier.

[^liteparse-readme]: run-llama, [*LiteParse README*](../raw/liteparse.md), sections "Overview", "Benchmarks", "CLI Usage", "OCR Setup", "Multi-Format Input Support", and "Development" (captured 2026-10-25; benchmarks describe v2.14.4). Linked docs, source code, benchmark harnesses, and package artifacts were not inspected.
[^opendataloader-pdf-readme]: OpenDataLoader Project, [*OpenDataLoader PDF README*](../raw/opendataloader-pdf.md), project benchmark table listing `liteparse` at 0.576 overall (accessed 2026-10-25). The benchmark implementation and the liteparse build it used were not inspected.
[^marker-readme]: Datalab, [*Marker README*](../raw/marker.md), "Overall PDF Conversion" competitive comparison table and the "Born-digital, CPU-only" subsection (accessed 2026-10-25). The benchmark runs and liteparse version used were not inspected.
