---
type: Concept
title: RAG-Anything runtime stack and operations
description: Python packaging, dependency pins, environment configuration, provider/storage adapters, CI intent, and deployment cautions.
tags: [ml, rag, dependencies, operations]
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

**Observed:** the inspected package is `raganything` 1.4.3, MIT-licensed, Beta-classified, and requires Python ≥3.10. Its four core dependencies are `huggingface_hub`, `lightrag-hku<1.5`, `mineru[core]>=3.4.1`, and `tqdm`; optional parsers/renderers/media add significant native/model dependencies. **Synthesis:** pin the complete environment and external assets for deployment rather than treating the package version as a reproducible installation specification.[^rag-anything-3a14ecb]

## Dependency decisions

| Constraint | Evidence and meaning |
| --- | --- |
| `lightrag-hku<1.5` | **Observed** pin; **Reported** rationale in requirements comments: RAG-Anything merged upstream into LightRAG 1.5+, whose `role_llm_funcs` extraction is incompatible with this line |
| `mineru[core]>=3.4.1` | **Observed** lower bound; **Reported** rationale: earlier MinerU fails when iterating `pdftext>=0.7` `PageChars` |
| `av<19` in audio/video | **Observed** pin; **Reported** rationale: faster-whisper passes the removed `metadata_errors` argument to PyAV |
| `office=[]` | **Observed:** Office extra installs no Python package; LibreOffice is external |
| `[all]` | **Observed:** modern manifest includes image/text/PaddleOCR/Markdown/audio/video Python dependencies, but not Docling, LibreOffice, or all platform-specific runtime packages |

The older `setup.py` `all` list omits audio/video while `pyproject.toml` includes them. **Synthesis:** installation results can differ for legacy versus PEP 621 packaging paths. Neither dependency-conflict rationale above was independently reproduced.[^rag-anything-3a14ecb]

## Configuration precedence and effective defaults

**Observed:** dataclass defaults read the process environment at each `RAGAnythingConfig` instantiation rather than freezing it at module import. Explicit field arguments normally override defaults. `.env` loading uses `override=False`, preserving existing shell values. **Exception:** `__post_init__` applies legacy `MINERU_PARSE_METHOD` whenever it is set and `PARSE_METHOD` is absent, even after an explicit `parse_method` argument; remove the legacy variable to avoid this override.[^rag-anything-3a14ecb]

| Setting | Default / control |
| --- | --- |
| Parser / parse method | `mineru` / `auto`; `PARSER`, `PARSE_METHOD` |
| Working / parser output directory | `./rag_storage` / `./output`; `WORKING_DIR`, `OUTPUT_DIR` |
| Image/table/equation | Enabled; `ENABLE_IMAGE_PROCESSING`, `ENABLE_TABLE_PROCESSING`, `ENABLE_EQUATION_PROCESSING` |
| Audio/video | Disabled; `ENABLE_AUDIO_PROCESSING`, `ENABLE_VIDEO_PROCESSING` |
| Concurrent files / recursion | 1 / true; `MAX_CONCURRENT_FILES`, `RECURSIVE_FOLDER_PROCESSING` |
| Context | One-page window, 2000 tokens, headers/captions on, text-only filter |
| File citation path | Basename by default; `USE_FULL_PATH=True` retains full path |

**Observed:** `lightrag_kwargs` controls a newly created LightRAG instance, not an externally supplied instance. LightRAG's own provider/storage/chunk/retrieval environment variables are a separate configuration layer, not simply lower-priority fields of `RAGAnythingConfig`. A sample `SUPPORTED_FILE_EXTENSIONS` comment omits some media extensions present in code defaults.[^rag-anything-3a14ecb]

## Model and storage integrations

**Observed:** core orchestration accepts injected text/vision/embedding functions. Examples demonstrate OpenAI-style wrappers, vLLM chat plus a separate embedding server, LM Studio, Ollama, and MiniMax. Ollama's example uses its native embedding endpoint; MiniMax's example requires separate embeddings and refuses a missing API key. These examples establish adapter intent, not live provider compatibility.[^rag-anything-3a14ecb]

**Observed:** `env.example` lists LightRAG storage selections and configurations for PostgreSQL, Neo4j, Milvus, Qdrant, Redis, and MongoDB; TiDB-related settings are marked deprecated. Actual stores and their schema/transaction behavior belong to LightRAG, not this repository. Public media URL mapping requires both `RAGANYTHING_PUBLIC_ASSET_BASE_URL` and `RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX`, applies only to parsed MinerU items, and performs no upload.[^rag-anything-3a14ecb]

## Setup and offline operation

**Reported commands** in README/package configuration (not run here):[^rag-anything-3a14ecb]

```bash
pip install raganything
pip install 'raganything[image,text]'
pip install 'raganything[audio,video]'
pip install docling  # separately, when selecting this backend
mineru --version
python -m raganything.parser --help
python -m raganything.batch_parser --help
```

**Observed/reported:** `docs/offline_setup.md` and `scripts/create_tiktoken_cache.py` describe prewarming tiktoken assets and setting `TIKTOKEN_CACHE_DIR` before LightRAG import. Parser/ASR models must be available separately; local providers alone do not guarantee an offline pipeline. Office rendering and video need system programs. Do not run copied install/download scripts without their normal environment/security review.[^rag-anything-3a14ecb]

## CI and testing: configured checks, not observed passes

**Observed:** `.github/workflows/test.yaml` configures Ubuntu jobs for Python 3.10/3.11/3.12, installs `.[all]` plus pytest/pytest-asyncio, and runs `pytest tests/ -v`. Pytest discovers `test*.py` under `tests`, not examples. Selected tests load examples with mocked modules or inspect documentation strings. Missing optional packages may cause `importorskip` rather than a hard failure.[^rag-anything-3a14ecb]

**Observed:** lint CI runs pre-commit/ruff and has an auto-commit action for formatting changes. Publishing is release-triggered with PyPI OIDC Trusted Publishing. No coverage gate, non-Linux test matrix, or live provider/database service setup was observed in the inspected workflows. **Limit:** workflow definitions do not prove a run passed; no CI history or local pytest run was checked.[^rag-anything-3a14ecb]

## Security and documentation cautions

- **Observed:** configuration/examples contain demo credentials/placeholders, not identified live secrets. **Synthesis:** copying the template unchanged is not production authentication or database hardening; never promote placeholder login/storage values into a deployment.
- **Observed:** `SECURITY.md` names support for 1.3.x, while package metadata reports 1.4.3. The applicable security-support policy for 1.4.3 is unclear from this snapshot.
- **Reported:** vLLM documentation says Python 3.9+. **Observed:** package metadata requires ≥3.10; follow the package requirement for this revision.
- **Observed:** exported `retry`, `async_retry`, and `CircuitBreaker` include backoff/jitter and half-open protection, but no internal ingestion/query call site was found. They must not be credited as automatic pipeline retries.[^rag-anything-3a14ecb]

## Relationships

- **Supports:** [Architecture](rag-anything-architecture.md), [parsing](rag-anything-parsing.md), [media processing](rag-anything-audio-video.md), and [query adapters](rag-anything-query-retrieval.md).
- **Constrains:** [Batch processing](rag-anything-batch-processing.md) concurrency and resource use.
- **Depends on:** [Source map](rag-anything-source-map.md) for snapshot identity and inspection limits.

[^rag-anything-3a14ecb]: Revision `3a14ecb66fb3`: `pyproject.toml` project/dependencies/extras/pytest tables; `requirements.txt` pin rationale; `setup.py` extras (66–89); `LICENSE`; `raganything/__init__.py::__version__`; `config.py::RAGAnythingConfig` and `__post_init__` (145–157); `raganything.py` dotenv loading and LightRAG construction (426–442); `tests/test_config_environment.py` (assertions inspected, not run); `env.example` provider/storage/configuration sections; provider examples `vllm_integration_example.py`, `lmstudio_integration_example.py`, `ollama_integration_example.py`, `minimax_integration_example.py` (targeted reads); `asset_urls.py`; `docs/offline_setup.md`, `scripts/create_tiktoken_cache.py`; `.github/workflows/test.yaml`, `linting.yaml`, `pypi-publish.yml`; `.pre-commit-config.yaml`; `SECURITY.md` version-support table; `docs/vllm_integration.md` prerequisites; `resilience.py::retry`, `async_retry`, `CircuitBreaker` and `__init__.py` re-exports; README installation/configuration sections.
