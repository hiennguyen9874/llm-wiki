---
type: Concept
title: LiteParse OCR and deployment
description: LiteParse OCR selects injected, HTTP, or Tesseract engines and has distinct networking, concurrency, and untrusted-input boundaries.
tags: [ml, ocr, pdf, document-parsing, deployment, security]
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

In [LiteParse](liteparse.md), selective OCR enriches or replaces native PDF text; the engine and deployment environment determine whether processing remains local, how failures surface, and what document content leaves the host. **Observed:** native engine selection prefers an injected engine, then a configured HTTP server, then feature-enabled Tesseract; WASM needs a caller-provided OCR callback.[^liteparse-repo]

## OCR contract and behavior

- **Observed:** The HTTP specification describes multipart `POST /ocr` with an image and optional language, returning text, pixel-coordinate bounding boxes, confidence and optionally an upright-frame polygon. The polygon supports rotation recovery. The specification defaults to `en`, while the Rust configuration uses Tesseract-style `eng`: server integrations must account for the difference.[^liteparse-repo]
- **Observed:** The merge code describes one result per word. Some example servers operate at line or block granularity; consequently word-level boxes may inherit coarser granularity rather than true individual words. Tesseract filters word confidence at `> 0.3`, whereas the shared merge filters results at `> 0.1`; confidence is therefore not directly comparable across engines.[^liteparse-repo]
- **Observed:** HTTP retries default to 10 attempts with a 60-second per-request timeout and backoff; optional hedging issues duplicate requests. The default systemic-failure policy errors only when every OCR task fails and at least one failed page is text-sparse; callers can request partial results instead.[^liteparse-repo]
- **Observed:** An optional `oar-ocr` feature provides an in-process ONNX engine, but it is not automatically selected by the normal engine-selection function; it requires injection. Example HTTP integrations include EasyOCR, PaddleOCR, Surya, Indra and MiniCPM-OCR.[^liteparse-repo]

## Deployment boundaries

- **Observed:** The HTTP engine sends rendered page images to the configured endpoint, including configured headers; the example configuration permits HTTP. Protect both document imagery and credentials with an appropriate trusted transport and service boundary. Config includes passwords and headers and derives `Debug` and serialization, so avoid logging or serializing secrets.[^liteparse-repo]
- **Observed:** Missing Tesseract language data can trigger a first-use network download. Offline operation requires the appropriate data already present. Optional PDF form-field rendering is documented as running PDF document open/JavaScript actions; it defaults off.[^liteparse-repo]
- **Reported:** The project's security policy places malicious documents, resource exhaustion, and service deployment outside its security scope and recommends upload validation, sandboxing, limits and timeouts. This policy is not an independent safety assessment.[^liteparse-repo]

## Evidence limits

Static inspection only: no OCR engine, server, network request or security test was run. The API, bindings and example servers were sampled rather than exhaustively audited; see the [pipeline coverage ledger](liteparse-pipeline.md). Runtime accuracy, server hardening and backend-specific language support remain unverified.[^liteparse-repo]

## Relationships

- **Depends on:** [LiteParse parsing pipeline](liteparse-pipeline.md) for selective OCR scheduling and native-text merge.
- **Related to:** [Detector–recognizer OCR](task-detector-recognizer-ocr.md) and [Indra OCR](indra-ocr.md), one of the example integrations.

[^liteparse-repo]: run-llama, [LiteParse repository](../raw/liteparse/README.md), revision `9bd22ec`; `OCR_API_SPEC.md` Request and Response Format; `crates/liteparse/src/parser.rs::ocr_engine`, `ocr_merge.rs::merge_ocr_results`, `ocr/tesseract.rs::recognize` and `ensure_traineddata`, `ocr/http_simple.rs::OcrRetryConfig` and `recognize`, `config.rs::LiteParseConfig`, `ocr/oar.rs::OarOcrEngine`, `crates/liteparse/Cargo.toml` features; `ocr/README.md` and `ocr/{paddleocr,suryaocr,minicpmocr}/server.py`; `SECURITY.md` Scope and Building Secure Services. Source code and servers were inspected only statically and in part.
