---
type: Concept
title: LiteParse parsing pipeline
description: LiteParse exposes a staged PDF extraction, selective OCR, projection, and Markdown layout pipeline with process-serialized PDFium access.
tags: [ml, ocr, pdf, document-parsing, layout-analysis]
status: draft
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: 2026-11-08T03:13:43Z }
stale_after: 2027-05-08
sources:
  - id: liteparse-repo
    resource: ../raw/liteparse/README.md
    scope: ../raw/liteparse/
    kind: code
    revision: 9bd22ec9ddd2b64b47c49827b35970931641efcd
    title: LiteParse repository
---

[LiteParse](liteparse.md) exposes its PDF parsing pipeline as composable stages: open and orient, extract, assess complexity, render and recognize selected pages, merge OCR, filter, project spatial text, classify blocks and render Markdown. **Observed:** stages that use PDFium are distinct from data-only stages; callers can insert their own inputs between stages.[^liteparse-repo]

## Architecture and concurrency

- **Observed:** Non-PDF Office documents require LibreOffice conversion, while supported images are converted natively. The workspace contains the core and CLI, PDFium wrapper and FFI, Node, Python and WASM binding crates; language packages provide their own wrappers.[^liteparse-repo]
- **Observed:** A process-global mutex serializes native PDFium access, while OCR and data-only work can happen outside the lock. Node and Python offer worker processes and parse timeouts to isolate work across processes; OCR uses a bounded worker window.[^liteparse-repo]
- **Observed:** A batch session defaults to 25 pages; repeated-header/footer removal and image deduplication only see each batch, so its output can differ from a whole-document parse.[^liteparse-repo]
- **Observed:** Page complexity controls OCR routing; the merge discards unusable native text, filters OCR results and avoids overlapping surviving native text. Grid projection and the Markdown block classifier use page geometry; headings and repeated header/footer filtering also use document-level signals.[^liteparse-repo]

## Coverage ledger and limits

This is a **partial static ingest** of snapshot `9bd22ec`, whose core manifest declares version 2.18.0. Inspected or sampled: root README and manifest; core stage, parser, extraction, projection, layout, OCR, configuration and test regions; PDFium wrapper and build configuration; binding and pool interfaces; OCR specification and example-server regions; documentation, security policy, benchmark scripts and CI. The separately captured `raw/liteparse.md` is byte-identical to the repository README; its prior wiki coverage was retained rather than duplicated. Generated FFI bindings and lockfiles were inventoried but not exhaustively read; binary fixtures and decorative assets were excluded. Large layout, wrapper, documentation and test trees remain only sampled; external benchmark corpora, packaged binaries, generated outputs and external services were not inspected. The README's `ocr/rapidocr` and the script's `LAUNCH_BENCHMARKS.md` are absent from this checkout. No build, document parse, tests, inference or benchmark was executed; claims about runtime behavior are static observations, not reproductions.[^liteparse-repo]

## Relationships

- **Uses:** [LiteParse OCR and deployment](liteparse-ocr-and-deployment.md) describes engine selection, HTTP contracts and security boundaries.
- **Related to:** [Layout analysis and reading order](task-layout-analysis-reading-order.md) covers the broader task served by the projection and block stages.

[^liteparse-repo]: run-llama, [LiteParse repository](../raw/liteparse/README.md), revision `9bd22ec`; `Cargo.toml`, `crates/liteparse/Cargo.toml`, `crates/liteparse/src/stages.rs` module documentation and `document_signals`, `parser.rs::parse_resolved`, `ocr_merge.rs::merge_ocr_results`, `crates/pdfium/src/library.rs::pdfium_lock`, `crates/liteparse-napi/src/lib.rs::open_batch_session`, `packages/node/src/pool.ts`, `packages/python/liteparse/_pool.py`, `run_benchmarks.sh`; root README sections “Development”, “Multi-Format Input Support”, and “Reproducing the benchmarks”. Inspection was static and partial; missing artifacts and execution limits are listed above.
