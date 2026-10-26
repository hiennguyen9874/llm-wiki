---
type: Concept
title: RAG-Anything document parsing
description: MinerU, Docling, PaddleOCR, and direct text parsing normalize files into content lists with explicit format and trust boundaries.
tags: [ml, rag, parsing, document-processing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:43:55Z }
stale_after: 2027-01-24
sources:
  - id: rag-anything-3a14ecb
    resource: ../raw/RAG-Anything/README.md
    scope: ../raw/RAG-Anything/
    kind: code
    revision: 3a14ecb66fb352b90d40a9884a5ad235d98ac72e
    title: RAG-Anything repository
---

**Observed:** RAG-Anything normalizes parser output into a flat list of typed content blocks consumed by ingestion. MinerU is the default subprocess backend; Docling uses a Python API and is the only built-in HTML parser; PaddleOCR provides OCR-focused text extraction. TXT/Markdown take a direct text path rather than automatic PDF conversion. **Synthesis:** “supported format” depends on backend, optional packages, and system binaries, not merely a filename appearing in a global extension list.[^rag-anything-3a14ecb]

## Backend selection and capabilities

| Backend/path | Observed behavior and constraints |
| --- | --- |
| `MineruParser` | Runs `mineru` with argv, parses output JSON, handles PDF/images, and converts Office through LibreOffice; unknown extensions fall through to PDF parsing |
| `DoclingParser` | Python converter with option-keyed cache; PDF, Office, native HTML, and direct text paths; requires separately installed `docling`, not included in `[all]` |
| `PaddleOCRParser` | OCR engine plus PDF-page rendering using `pypdfium2`; Office can convert through LibreOffice; requires platform-appropriate Paddle runtime |
| `Parser.parse_text_file` | Direct TXT/MD decoding/block construction, heading recognition, local Markdown image references; no PDF/OCR round trip |
| Audio/video routing | Bypasses these parsers and constructs media content items |

**Observed:** choose `RAGAnythingConfig(parser=...)` or `PARSER` when constructing the instance; it is not a per-ingest-call switch. `register_parser` supports in-process custom parser registration, with normalized names and rejection of builtin-name collisions/non-subclasses. Registration does not establish that an implementation handles every needed capability. CLI use is `python -m raganything.parser`; packaging declares no console-script entry point.[^rag-anything-3a14ecb]

## Content-list schema

**Observed:** blocks use `type` and type-specific content, normally with zero-based `page_idx`:

- Text: `text`, optional `text_level` for headings.
- Image: `img_path`, caption/footnote fields; MinerU aliases `img_caption` ↔ `image_caption` and `img_footnote` ↔ `image_footnote` are reconciled.
- Table: `table_body`, caption/footnotes and optional image path.
- Equation: LaTeX/text representation and optional image path.
- Other blocks may retain code/list/chart subtype, `bbox`, `anchor`, and source-specific metadata. Media items use their own audio/video paths.

Caption lists/strings/null values vary by parser and are normalized downstream. Docling page provenance converts `page_no` to zero-based indexing and uses 0 for unpaginated items; that does not independently establish pagination of HTML or text.[^rag-anything-3a14ecb]

## MinerU v2 reconciliation

**Observed:** document-scoped output directories outrank shared roots; within a bundle v2 outranks legacy flat content lists and exact-stem files outrank generic names. `convert_mineru_content_list_v2` flattens page-grouped blocks, preserving page indexes, bounding boxes, anchors, heading levels, captions, and visual metadata. It maps algorithms to `type="code", sub_type="algorithm"` and joins spans with CJK-aware spacing.[^rag-anything-3a14ecb]

Headers, footers, page numbers, aside text, and page footnotes are excluded unless `include_layout_blocks=True`. Unknown future blocks warn/skip. Malformed, structurally invalid, or supported-content-empty v2 output can fall back to a legacy file when present. Relative media paths resolve under the output image root; paths escaping that root are cleared with a warning. Optional public URL siblings are attached only on this MinerU path; mapping does not upload assets or make them publicly reachable.[^rag-anything-3a14ecb]

## Direct Markdown and image trust

**Observed:** Markdown headings become text blocks, fenced/inline code suppresses image interpretation, and resolvable local image references become image blocks. Remote URLs, missing images, and non-image files remain literal text. Image detection requires both supported suffix and recognizable file bytes; encoding rechecks signatures before sending content to a vision function.[^rag-anything-3a14ecb]

**Synthesis:** this prevents a renamed text/key file from being treated as a normal image, but it does not confine all Markdown references to the document directory. Trusted Markdown can name real images elsewhere on disk, which may then be sent to the vision provider. The parser's validation is not identical to retrieval-time size/symlink/directory checks.[^rag-anything-3a14ecb]

## Network and conversion boundary

- **Observed:** Docling's direct `parse_document` accepts URLs through `_download_file`; the helper uses `urlopen`, a 30-second timeout, and temporary-file cleanup, but has no explicit size cap or scheme/host/redirect allowlist. The URL predicate is broader than HTTP(S). **Synthesis:** enforce an application-level download policy before exposing this API to untrusted callers. The outer `RAGAnything.parse_document` path is file-oriented; do not infer end-to-end URL support from Docling alone.
- **Observed:** `.html/.htm/.xhtml` are refused by MinerU/PaddleOCR and Office conversion because LibreOffice HTML conversion can fetch remote URLs/embed referenced local files. Recognition is suffix-based; disguised HTML under an Office extension is not ruled out.
- **Observed:** Office conversion uses LibreOffice with a default 600-second `LIBREOFFICE_CONVERT_TIMEOUT`; MinerU's command timeout defaults to `None`, and ordinary PDF/image callers do not supply one. Batch timeout reporting does not guarantee subprocess termination.
- **Observed:** subprocess calls use argv lists, not shell interpolation. **Synthesis:** this avoids one injection vector but is not a document-renderer sandbox.[^rag-anything-3a14ecb]

## Static failure risks

- **Observed:** MinerU stderr lines containing `error` (unless first classified as warnings) contribute to failure even at exit code 0. **Synthesis:** benign “0 errors” text can produce a false failure; occurrence on real runs was not measured.
- **Observed:** `_read_output_files` has broad warning-only error handling and can return an empty list; the outer ingestion path rejects an empty parse, while direct parser callers must inspect results themselves.
- **Observed:** the cache option whitelist omits `vlm_url` and PaddleOCR `cls`. **Synthesis:** changing these without changing included cache inputs may reuse earlier output; runtime impact is untested.
- **Observed:** Docling option compatibility guards can ignore unsupported options; some text-block key accesses are unguarded while image/table handling catches errors. Live Docling-version behavior remains unverified.[^rag-anything-3a14ecb]

## Relationships

- **Used by:** [Document ingestion](rag-anything-ingestion.md) and [batch processing](rag-anything-batch-processing.md).
- **Produces inputs for:** [Multimodal grounding](rag-anything-multimodal-grounding.md).
- **Related to:** [Enhanced Markdown rendering](rag-anything-enhanced-markdown.md) and [DOCX equations](rag-anything-docx-equations.md), both separate opt-in utilities, not automatic parser stages.
- **Depends on:** [Runtime operations](rag-anything-stack-operations.md) for extras and external programs.

## Evidence limits

All backend mechanisms are observed adapter code, not successful parsing with external engines. External model files, LibreOffice behavior, parser schemas, and provider outputs were not executed or independently validated; see [source map](rag-anything-source-map.md).

[^rag-anything-3a14ecb]: Revision `3a14ecb66fb352b90d40a9884a5ad235d98ac72e`: `raganything/parser.py::HTML_FILE_EXTENSIONS`/`html_requires_docling_error` (131–144), `Parser` URL/download helpers (162–243), `convert_office_to_pdf` (317–490), Markdown image resolution/block construction (791–1027), `parse_text_file` (1029), `MineruParser` (1153), `_run_mineru_command` (1266–1513; stderr/failure 1420–1491), output discovery/read (1515–1810), `parse_document` (2083), `DoclingParser` (2167; URL dispatch 2278–2341, converter options 2343–2417, block mapping 2587–2676), `PaddleOCRParser` (2821), registry/factory/CLI (3147–3436); `mineru_content.py::convert_mineru_content_list_v2` and conversion helpers; `parse_options.py::PARSER_CACHE_KWARGS`; `asset_urls.py`; `processor.py::parse_document` (614–811); `image_signature.py`; `utils.py` image validation/encoding; README “Parser Configuration”, “MinerU 3.x Content List v2”, “Document Formats”; tests `test_html_routing.py`, `test_parser_url_download.py`, `test_docling_text_files.py`, `testparser_wiring.py` (not executed).
