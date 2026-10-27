---
type: SourceMap
title: RAG-Anything source map and coverage
description: Pinned repository identity, per-artifact static-inspection ledger, exclusions, external dependencies, and unexecuted checks.
tags: [ml, rag, source-map, provenance]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:07:43Z }
stale_after: 2027-01-24
sources:
  - id: rag-anything-3a14ecb
    resource: ../raw/RAG-Anything/README.md
    scope: ../raw/RAG-Anything/
    kind: code
    revision: 3a14ecb66fb3
    title: RAG-Anything repository
---

**Observed:** this compilation covers HKUDS RAG-Anything's local repository at commit `3a14ecb66fb3`, using static code/document inspection by the curator and four parallel Explore agents, followed by a separate focused semantic review of all twelve compiled pages. The ledger distinguishes full reading, targeted reading, inventory/syntax-only coverage, and deliberate exclusions. **Limit:** this is not a runtime or complete test-assertion audit; the source map remains draft for the explicit coverage gaps below.[^rag-anything-3a14ecb]

## Source identity and trust

| Field | Inspected value |
| --- | --- |
| Canonical entry point / scope | `raw/RAG-Anything/README.md` / `raw/RAG-Anything/` |
| Revision / commit date | `3a14ecb66fb3` / 2026-10-26 |
| Commit subject | Discard empty Whisper transcription segments (#438) |
| Upstream | `https://github.com/HKUDS/RAG-Anything` (remote points to the same HKUDS repository) |
| Distribution | `raganything` 1.4.3; Python ≥3.10; MIT; package author Zirui Guo; license attribution Data Intelligence Lab @ HKU |
| Languages | Python implementation, English/Chinese documentation and prompts |
| Snapshot | 143 tracked files; clean source worktree at inspection and post-compilation check |

**Observed:** source authors' comments explain dependency pins and documentation reports capabilities; neither is independent corroboration. The README links the 2025 technical report by Zirui Guo, Xubin Ren, Lingrui Xu, Jiahao Zhang, and Chao Huang, but the paper was not retrieved. No benchmark claim from that paper is compiled as a checked result.[^rag-anything-3a14ecb]

**Reproduced, compilation-session check only:** all 114 Python files passed standard-library `ast.parse` under Python 3.12.3 on Linux; no repository module was imported or executed. This checks Python syntax, not imports, dependencies, behavior, typing, tests, or provider compatibility. File-pattern screening of text plus reviewed matches found no likely live credentials; secret-shaped matches were placeholders or synthetic fixtures. This is not a certified secret/PII scan.

The inspected tracked-file content digest is `5725cac7a7d599819e9a2bbd9d5e09d045e39bb96d2b03af23733bb39d6b46e4` (SHA-256 over sorted relative path bytes, NUL, then each file's raw SHA-256 digest bytes). This is an inspection fingerprint, not an upstream signed attestation.

## Retrieval map

- [Architecture](rag-anything-architecture.md) — composition, lifecycle, extension boundaries.
- [Audio/video](rag-anything-audio-video.md) — ASR, scenes, keyframes, windows, quality limits.
- [Batch processing](rag-anything-batch-processing.md) — manifests, skip/retry semantics, concurrency, timeouts.
- [DOCX equations](rag-anything-docx-equations.md) — explicit OMML enrichment and synthetic placement.
- [Document ingestion](rag-anything-ingestion.md) — text completion, identity, page provenance, best-effort modal status.
- [Document parsing](rag-anything-parsing.md) — backend routing, content schema, MinerU v2, file/network trust.
- [Enhanced Markdown rendering](rag-anything-enhanced-markdown.md) — standalone PDF utility and documentation drift.
- [Multimodal grounding](rag-anything-multimodal-grounding.md) — descriptions, context, chunks, graph anchors.
- [Query and retrieval](rag-anything-query-retrieval.md) — text/attachment/VLM paths and caches.
- [Reproduction/evaluation](rag-anything-reproduction-evaluation.md) — protocol, grades, schema mismatch, missing data.
- [Runtime operations](rag-anything-stack-operations.md) — dependencies, config, adapters, CI, deployment cautions.

## Coverage ledger

Paths below are relative to the source scope. **Full** means static reading, not execution. **Targeted** means substantive regions were read, with the remainder not fully audited. All Python artifacts also received syntax parsing. Inventory-only tests are explicitly excluded from behavioral claims, not treated as passing tests.

### Entry point, metadata, policy, and build artifacts

| Artifact | Coverage / disposition |
| --- | --- |
| `README.md` | Full; canonical overview, APIs, setup, formats, research citation; reconcile promotional claims against code |
| `README_zh.md` | Header/heading inspection and credential screen only; remainder excluded as alternate-language overview, no line-by-line parity claim |
| `LICENSE` | Full; MIT/license attribution |
| `SECURITY.md` | Full; support-version drift recorded in operations |
| `pyproject.toml` | Full; build, metadata, dependencies/extras, pytest/ruff settings |
| `setup.py` | Full; legacy metadata/extras compared with modern manifest |
| `requirements.txt` | Full; runtime dependencies and pin rationale |
| `MANIFEST.in` | Full; distribution inclusion rules |
| `env.example` | Full; configuration template and privacy screen; values not promoted into wiki |
| `.gitignore` | Full; generated state/secret-file exclusions |
| `.pre-commit-config.yaml` | Full; configured hooks and manual manifest check |
| `.github/workflows/test.yaml` | Full; configured test matrix/command, not workflow run outcomes |
| `.github/workflows/linting.yaml` | Full; lint/auto-commit behavior |
| `.github/workflows/pypi-publish.yml` | Full; release build/OIDC publication configuration |
| `.github/dependabot.yml` | Excluded: dependency-update housekeeping, no runtime mechanism compiled |
| `.github/pull_request_template.md` | Excluded: contribution template |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | Excluded: triage form |
| `.github/ISSUE_TEMPLATE/config.yml` | Excluded: triage routing |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | Excluded: triage form |
| `.github/ISSUE_TEMPLATE/question.yml` | Excluded: triage form |

### Implementation modules

| Artifact | Coverage / retrieval destination |
| --- | --- |
| `raganything/__init__.py` | Full; exports, optional imports, version → architecture/operations |
| `raganything/asset_urls.py` | Full; local-to-public mapping → parsing/grounding/operations |
| `raganything/base.py` | Full; document status enum → ingestion |
| `raganything/batch.py` | Full; batch API/RAG orchestration → batch processing |
| `raganything/batch_parser.py` | Full; workers/manifest/timeouts/CLI → batch processing |
| `raganything/callbacks.py` | Full; events/callbacks/metrics → architecture |
| `raganything/config.py` | Full; field defaults and legacy override → operations |
| `raganything/document_context.py` | Full; operation-local state → architecture/grounding |
| `raganything/enhanced_markdown.py` | Full; renderer/configuration/trust → enhanced Markdown |
| `raganything/image_signature.py` | Full; magic bytes/MIME → parsing/retrieval |
| `raganything/mineru_content.py` | Full; v2 conversion/schema → parsing |
| `raganything/modalprocessors.py` | Full; processors/context/direct indexing → grounding |
| `raganything/modalprocessors_audio.py` | Full; transcription/windows → audio/video |
| `raganything/modalprocessors_video.py` | Full; scenes/frames/audio/windows → audio/video |
| `raganything/omml_extractor.py` | Full; DOCX XML conversion/enrichment → DOCX equations |
| `raganything/parse_options.py` | Full; cache-option contract → ingestion/batch/parsing |
| `raganything/parser.py` | Full; backend implementations/URL/rendering/registry/CLI → parsing |
| `raganything/processor.py` | Full; ingest/cache/index/status/page mapping → ingestion/grounding |
| `raganything/prompt.py` | Full; prompt registry/templates → grounding/retrieval |
| `raganything/prompt_manager.py` | Full; language resolution/swap → grounding |
| `raganything/prompts_zh.py` | Targeted: keys and first 50 lines; full translated-prompt semantic parity pending; not used to claim equivalent output quality |
| `raganything/query.py` | Full; query paths/caches/image loading → retrieval |
| `raganything/raganything.py` | Full; orchestration/lifecycle/init → architecture |
| `raganything/resilience.py` | Full; standalone retry/circuit-breaker helpers; internal call-site search → operations |
| `raganything/utils.py` | Full; content separation/provenance/validation/insertion helpers → ingestion/grounding/retrieval |

### Documentation, examples, scripts, and assets

All six `docs/` files were read in full: `batch_processing.md`, `context_aware_processing.md`, `enhanced_markdown.md`, `multimodal_rag_failure_modes.md`, `offline_setup.md`, `vllm_integration.md`. Durable procedures and implementation disagreements are mapped to the concepts above. External URLs were not followed; referenced issue discussions, upstream documentation, and model assets remain uninspected external evidence.[^rag-anything-3a14ecb]

| Artifact | Coverage / disposition |
| --- | --- |
| `examples/batch_dry_run_example.py` | Full; dry-run configuration/control flow |
| `examples/batch_processing_example.py` | Targeted: 1–45, 230–270, 487–561; remaining repeated demo logic excluded |
| `examples/enhanced_markdown_example.py` | Targeted: first 30 lines; repetitive demo body excluded, implementation audited directly |
| `examples/image_format_test.py` | Targeted: 1–130; remainder repetitive demo, not executed |
| `examples/insert_content_list_example.py` | Targeted: first 45 lines and insertion call sites; repeated model setup excluded |
| `examples/lmstudio_integration_example.py` | Targeted: first 120 lines; adapter configuration, remainder not fully audited |
| `examples/minimax_integration_example.py` | Targeted: first 140 lines; key/temperature/embedding boundary, remainder not fully audited |
| `examples/modalprocessors_example.py` | Targeted: 1–120 and 213–243; repeated provider/demo bodies excluded |
| `examples/office_document_test.py` | Targeted: first 45 lines; remaining demo body excluded |
| `examples/ollama_integration_example.py` | Targeted: first 110 lines; chat/embedding adapter pattern, remainder not fully audited |
| `examples/raganything_example.py` | Targeted: first 120 lines; environment/model setup, remainder not fully audited |
| `examples/text_format_test.py` | Targeted: first 45 lines; remaining demo body excluded |
| `examples/vllm_integration_example.py` | Targeted: first 180 lines; separate chat/embedding services, remainder not fully audited |
| `reproduce/env.example` | Full; experiment configuration, placeholders only |
| `reproduce/index.py` | Full; indexing assumptions and error behavior |
| `reproduce/query.py` | Full; QA input/query/result schema |
| `reproduce/llm_answer_evaluator.py` | Targeted: prompts 46–158, evaluation 286–530, structured reader around 870–980, save/report 1009–1188, resume/QA/CLI 1489–1876; other evaluator helpers not fully audited |
| `scripts/create_tiktoken_cache.py` | Full; static offline-cache helper inspection, not run |
| `assets/rag_anything_framework.png` | Visually inspected full diagram; graph/vector convergence and retrieval panels; no quantitative benchmark extracted |
| `assets/logo.png` | Excluded: decorative branding |
| `assets/LiteWrite.png` | Excluded: non-core promotional asset, not used as architecture or evaluation evidence |

### Tests: full static reading

The following 22 modules were read in full (assertions observed, none run): `test_asset_urls.py`, `test_batch_parser_workers.py`, `test_config_environment.py`, `test_docling_text_files.py`, `test_document_context_isolation.py`, `test_enhanced_markdown_css.py`, `test_enhanced_markdown_images.py`, `test_html_routing.py`, `test_initialization_lifecycle.py`, `test_media_file_routing.py`, `test_multimodal_concurrency.py`, `test_multimodal_query_key.py`, `test_null_caption_items.py`, `test_parse_options.py`, `test_parser_url_download.py`, `test_processor_lightrag_api.py`, `testquery_stream_cache.py`, `test_vlm_query_flags.py`, `test_video_audio_cleanup.py`, `testparse_cache_key.py`, `testparser_wiring.py`, `test_docling_page_provenance.py`.[^rag-anything-3a14ecb]

### Tests: targeted reading

| Module under `tests/` | Inspected region; remainder not fully audited |
| --- | --- |
| `test_batch_rag_incremental.py` | 1–200 |
| `test_callbacks.py` | 1–120 |
| `test_close_event_loop.py` | 1–60 |
| `test_content_list_alias_handling.py` | 1–60 |
| `test_custom_parser.py` | 1–130 |
| `test_docling_content_blocks.py` | 1–120 |
| `test_force_multimodal_reprocess.py` | 1–60 |
| `test_image_caption_string_normalization.py` | 1–60 |
| `test_lmstudio_integration_example.py` | 1–40 |
| `test_md_image_blocks.py` | Test-name inventory plus 180–225 fixture/validation assertions |
| `test_mineru_content.py` | First 60 lines plus targeted test-name/selection greps; not all selection assertions read |
| `test_mineru_error_hints.py` | Targeted context across 1–146, not guaranteed continuous full read |
| `test_minimax_integration.py` | 1–45 |
| `test_omml_extractor.py` | 1–60 and test-name inventory |
| `test_plain_text_direct.py` | 1–60 and test-name inventory |
| `test_text_chunk_page_idx_pipeline.py` | 1–80 |
| `test_video_processor.py` | Sections 302–515; earlier portions not fully audited |
| `test_vision_example_media_type.py` | 1–40 |
| `testbatch_incremental.py` | 612–637 fixture/manifest assertions; remainder inventory only |
| `testparser_kwargs.py` | 1–80 |

### Tests: inventory/syntax only, excluded from behavioral claims

These 29 modules were inventoried and syntax-parsed, but their assertion bodies were not substantively audited: `test_audio_processor.py`, `test_batch_rag_async.py`, `test_chinese_cid_font.py`, `test_circuit_breaker_stale_results.py`, `test_core_modules.py`, `test_doc_status_creation.py`, `test_embedding_examples.py`, `test_full_entities_merge.py`, `test_image_la_alpha_composite.py`, `test_image_section_scan.py`, `test_insert_content_list.py`, `test_json_latex_escapes.py`, `test_lightrag_api_doc_status.py`, `test_md_pdf_escape.py`, `test_modalprocessor_chunk_document_id.py`, `test_modalprocessor_fallback_arity.py`, `test_modalprocessors_config.py`, `test_multimodal_chunks_list_merge.py`, `test_prompt_language.py`, `test_query_content_aliases.py`, `test_queued_text_insert.py`, `test_raganything_example.py`, `test_regex_fallback_entity_name.py`, `test_resilience.py`, `test_strip_thinking_tags.py`, `test_text_chunk_page_idx.py`, `test_vlm_image_media_type.py`, `testbatch_mixin.py`, `testpaddleocr_parser.py`.

## Dependency closure, exclusions, and missing evidence

- **External, not vendored/audited:** LightRAG, MinerU, Docling, PaddleOCR/Paddle runtime, Hugging Face/model downloads, tiktoken assets, Pillow, ReportLab, python-markdown, WeasyPrint/Pygments, faster-whisper/PyAV, SceneDetect/OpenCV/moviepy, provider SDKs, LibreOffice, Pandoc/wkhtmltopdf, ffmpeg, database services. Adapter calls/configuration were inspected, not their implementations or live behavior.
- **Unavailable:** default `reproduce/data/`, experiment PDFs/questions/reference-answer corpora, real model weights, run outputs and benchmarks. No dataset/split/compute claims are inferred from their absence.
- **Excluded:** `.git/` internals except revision/remote/status metadata; contribution forms, decorative/promotional assets, repeated demo bodies, alternate-language overview, unaudited test assertions. No generated or vendored tree was ingested.
- **Not performed:** dependency installation, network retrieval, parser execution, API calls, ASR/video processing, PDF rendering, pytest, live CI inspection, performance/security testing. Source files stayed read-only. No unreadable local text artifact was encountered; external implementations/assets above were unavailable within the inspected package.
- **Remaining coverage:** full Chinese prompt semantic review, uninspected example/evaluator regions, and unsampled tests. Future ingestion should reconcile these gaps against this identity rather than compile supporting files as new sources.

## Idempotency and maintenance

**Synthesis:** all linked concepts use the same package identity (scope plus revision); internal supporting files are not separate sources. Reingesting the same audited regions without changed/new knowledge should not rewrite concepts or log. New revisions, newly inspected pending regions, meaningful corrections, or cross-concept connections justify a targeted update. The current graph has no prior concepts from this source to supersede; implementation/document disagreements are preserved in their owning concepts, not flattened into one unsupported claim.

[^rag-anything-3a14ecb]: Canonical README plus source scope at revision `3a14ecb66fb3`; identity locators: README title/overview/citation, `pyproject.toml` project metadata/dependencies, `raganything/__init__.py::__version__`, `LICENSE`; all file paths/regions above are the coverage locators for static findings. Git revision/status and tracked-file inventory were inspected during this compilation. Detailed claim locators are preserved in the linked concept footnotes; no unavailable upstream attachment is treated as inspected evidence.
