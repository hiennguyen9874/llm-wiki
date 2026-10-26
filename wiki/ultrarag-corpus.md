---
type: Concept
title: UltraRAG corpus processing and chunking
description: Text, page-image, and MinerU corpus builders with JSONL schemas and configurable Chonkie chunking.
tags: [ml, ultrarag, document-processing, chunking]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e2032d9f134099405b8b483edbbad95274080
    title: UltraRAG repository
---

**Observed:** UltraRAG's corpus server produces text and image JSONL corpora from local documents, optionally delegates parsing to MinerU, and chunks text with Chonkie. Parsing and indexing are separate pipeline stages; producing a corpus does not establish that it is embedded, indexed, or available to chat.[^ultrarag]

## Processing paths and schemas

| Tool | Main behavior | Output row shape |
| --- | --- | --- |
| `build_text_corpus` | Decode TXT/Markdown; convert/extract Office formats; use PyMuPDF for supported document containers | `id`, `title`, `contents` |
| `build_image_corpus` | Render PDF pages to verified JPEGs at 144 DPI | `id`, `image_id`, `image_path` |
| `mineru_parse` | Locate and invoke the external `mineru` executable asynchronously | MinerU output tree |
| `build_mineru_corpus` | Read `<stem>/auto/<stem>.md` and associated images | Text/image corpus artifacts |
| `chunk_documents` | Token, sentence, or recursive chunking with configured counter/tokenizer | `id`, `doc_id`, `title`, `contents` |

Text extraction sorts PDF blocks by coordinates, cleans text, and reflows hard-wrapped paragraphs with CJK-aware handling and hyphen repair. **Synthesis:** these heuristics may not preserve complex reading order or every document's layout semantics. Single unsupported inputs raise; directory processing can warn and skip unsupported files.[^ultrarag]

## Effective defaults and prerequisites

The shipped parameter file selects sentence chunking, size `512`, character counting, and `use_title: false`. These override the tool signature's token-oriented defaults when the parameter block is used. Tokenizer names are resolved through tiktoken, with `word`/`character` sentinels and a warning/fallback to `gpt2` for unknown encodings. The committed token/sentence backend configurations set overlap to `50`; `64` is the code fallback when that key is omitted. Overlap at least as large as a chunk is clamped to one quarter of chunk size. Title inclusion, when enabled, adds explicit title/content labels.[^ultrarag]

MinerU is an optional corpus extra and still requires its CLI/model resources. The launcher uses `create_subprocess_exec`, not a shell, passes extra configured CLI flags, and raises a tool error for nonzero exit. Office conversion may require a separately installed Office/LibreOffice executable. Missing tools or model assets are external prerequisites, not automatically satisfied by having YAML examples.[^ultrarag]

## Filesystem and execution boundary

Paths for source documents and output corpora are configurable. `_validate_path` supports an `allowed_base`, but inspected callers do not supply one; path checks are therefore not a repository/storage-root confinement guarantee. MinerU arguments are user-influenced, and conversion/parsing touches local files and launches executables. Use only trusted configurations under an appropriately restricted process account.[^ultrarag]

## Coverage and limits

Draft: the large corpus module was sampled across all tool paths, while detailed Office-conversion and text-normalization helpers were not exhaustively reviewed. No document conversion, parser invocation, OCR, image rendering, corpus writing, or chunk-quality evaluation was executed. Sample schemas are observed; actual extraction fidelity is **unverified**.[^ultrarag]

## Relationships

- **Feeds:** [retrieval](ultrarag-retrieval.md) through text/image corpus artifacts.
- **Used by:** [UI knowledge-base tasks](ultrarag-ui.md).
- **Depends on:** [deployment extras and external binaries](ultrarag-deployment.md).
- **Constrained by:** [filesystem and subprocess security](ultrarag-security.md).

[^ultrarag]: Revision `185e2032d9f134099405b8b483edbbad95274080`: `servers/corpus/src/corpus.py::_validate_path`, `clean_text`, `reflow_paragraphs`, `build_text_corpus`, `build_image_corpus`, `mineru_parse`, `build_mineru_corpus`, `chunk_documents`; `servers/corpus/parameter.yaml` chunk settings and `mineru_extra_params`; `data/corpus_example.jsonl` `id`/`contents`; `examples/experiments/{build_text_corpus,build_image_corpus,build_mineru_corpus,corpus_chunk}.yaml`; `pyproject.toml` corpus extra. Helper internals were selectively inspected; no runtime verification.
