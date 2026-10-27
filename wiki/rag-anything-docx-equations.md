---
type: Concept
title: RAG-Anything DOCX equation extraction
description: An opt-in OMML-to-LaTeX utility enriches content lists with equations while retaining synthetic rather than precise page placement.
tags: [ml, equations, docx, document-processing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:43:55Z }
stale_after: 2027-01-24
sources:
  - id: rag-anything-3a14ecb
    resource: ../raw/RAG-Anything/README.md
    scope: ../raw/RAG-Anything/
    kind: code
    revision: 3a14ecb66fb3
    title: RAG-Anything repository
---

**Observed:** `omml_extractor.py` reads Office Math Markup Language (OMML) equations directly from DOCX XML and converts them to LaTeX-like equation blocks. Its enrichment helper is not wired automatically into the built-in parser/ingestion pipeline. **Synthesis:** it is an application-level repair path for missing equations, not a guarantee that normal Office ingestion preserves inline mathematics.[^rag-anything-3a14ecb]

## Extraction and conversion

**Observed:** `extract_omml_equations` opens the DOCX ZIP, reads `word/document.xml`, parses XML, finds math elements, and dispatches conversion handlers by local element names. The handler set includes mathematical structures such as fractions, scripts, radicals, delimiters, and matrices, with text-oriented fallbacks for unsupported structure. This inspects the main document part, not a complete audit of every possible equation-bearing DOCX attachment/part.[^rag-anything-3a14ecb]

Returned `raw_omml` is generated with `ElementTree.tostring`: **Observed**, it is reserialized XML and can rewrite namespace prefixes, despite a docstring calling it the original XML. **Synthesis:** do not use byte-for-byte equality against the source package as its identity contract.[^rag-anything-3a14ecb]

## Content-list enrichment

**Observed:** `enrich_content_list_with_docx_equations` returns a new list, appending equation blocks with `type="equation"`, LaTeX `text`, `text_format="latex"`, empty image path, and `_source="omml_extractor"`. It copies the last existing block's page index, or 0 for an empty input. Extracted equations preserve their extraction order but are appended at the tail rather than positioned among original text blocks.[^rag-anything-3a14ecb]

- Deduplication defaults on and compares stripped LaTeX text to existing equation-block `text` exactly.
- It does not semantically equate OCR LaTeX, placeholders, or different equivalent formulas.
- **Synthesis:** synthetic pages and tail placement are retrieval hints only; precise provenance requires separate placement evidence. Exact deduplication can leave semantic duplicates.[^rag-anything-3a14ecb]

## Safety and fidelity limits

**Observed:** ZIP decompression/XML parsing has no explicit package-size or expansion cap in this utility; handler dispatch strips namespaces. **Synthesis:** place resource limits around untrusted DOCX processing and do not treat conversion as a complete fidelity/security validator. Namespace-blind handlers can also misinterpret unexpected elements sharing recognized local names. No malicious-document test or symbolic-equivalence check was executed.[^rag-anything-3a14ecb]

## Relationships

- **Related to:** [Document parsing](rag-anything-parsing.md), which must explicitly call enrichment if desired.
- **Produces inputs for:** [Document ingestion](rag-anything-ingestion.md) through direct content-list insertion.
- **Uses:** [Multimodal grounding](rag-anything-multimodal-grounding.md) once enriched equation blocks are inserted.

## Evidence limits

The extraction/conversion code and selected test setup were statically inspected. No DOCX was opened by execution and no equation fidelity or precise page placement was reproduced; see [source map](rag-anything-source-map.md).

[^rag-anything-3a14ecb]: Revision `3a14ecb66fb3`: `raganything/omml_extractor.py::extract_omml_equations` (main ZIP/XML processing 155–196), `enrich_content_list_with_docx_equations` (220–332), local-name/dispatch helpers (362–384), `_HANDLERS` (784–817); absence of parser/processor integration found by static import/reference search; sampled `tests/test_omml_extractor.py` (first 60 lines and test-name inventory, not executed).
