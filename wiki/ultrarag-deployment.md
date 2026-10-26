---
type: Concept
title: UltraRAG installation, deployment, and test coverage
description: Python and frontend dependencies, optional backend extras, CUDA-aware containers, and the limits of CI smoke tests.
tags: [ml, ultrarag, deployment, tech-stack]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e2032d9f1
    title: UltraRAG repository
---

**Observed:** UltraRAG is a Python package with a separately built React/TypeScript frontend and optional heavy model/retrieval/parser dependencies. Its containers share the frontend build and core runtime, while only the full GPU image installs all extras. CI checks selected launch/configuration paths and buildability; it is not a full feature, security, or benchmark validation suite.[^ultrarag]

## Stack and version constraints

| Layer | Inspected manifest choices |
| --- | --- |
| Package | `ultrarag` `0.3.0.2`; Python `>=3.11,<3.13`; setuptools; CLI `ultrarag.client:main` |
| Core orchestration | FastMCP `>=3.3.1,<3.4.5`, MCP, PyYAML, Jinja2, Rich |
| APIs/data/UI backend | OpenAI client, HTTPX/aiohttp/requests, pandas/NumPy, Flask, SQLite from Python |
| Retrieval extras | Infinity, Sentence Transformers, BM25s, FAISS, Milvus/Qdrant clients, Torch/FastAPI |
| Local generation extras | vLLM `0.22.1`, Transformers/Torch, xgrammar `<0.2.4` |
| Other extras | Separate LiteLLM `>=1.60,<2.0`; MinerU `>=3,<4`; ROUGE and pytrec evaluation |
| Frontend | React 19, TypeScript 5.9, Vite 8, React Router, TanStack Query, Zustand, React Flow, Radix |

The manifest pins Linux GPU wheel sources to CUDA 12.9 indexes, bounds NumPy to `>=2,<2.4`, and selects FAISS GPU on non-macOS versus FAISS CPU on macOS. **Synthesis:** platform markers and dependency resolution are not proof that every non-macOS platform has usable matching GPU wheels/hardware.[^ultrarag]

## Setup and entry points

These are **source-observed instructions, not executed here**; use a working checkout rather than `raw/UltraRAG/`:

```sh
uv sync                       # core
uv sync --extra retriever      # selected backend family
uv sync --extra litellm        # API-only routing without local generation extra
uv sync --all-extras           # full dependency environment
```

Activate/use that environment, then build and run a chosen YAML pipeline. Server backends need their own assets: downloaded model weights, GPU drivers, vector databases, remote endpoints/API credentials, or parsing executables. API-only inference can avoid the local vLLM/Torch generation extra, but does not remove all core dependencies.[^ultrarag]

`ultrarag show ui` launches the UI, while `ultrarag show case` launches the result viewer. The CLI defaults UI binding to loopback/port `5050`; the Docker command instead binds `0.0.0.0`. Remote MCP requires Node ≥20 and npx; containers install Node 22. Bundled vLLM service scripts and demo parameter URLs use differing port selections, so reconcile endpoints explicitly rather than assuming the scripts match a demo.[^ultrarag]

## Container variants

| Dockerfile | Runtime base | Python install scope |
| --- | --- | --- |
| `Dockerfile.base-cpu` | Ubuntu 24.04 | Frozen core, no dev dependencies |
| `Dockerfile.base-gpu` | CUDA 12.9.1 base on Ubuntu 24.04 | Frozen core, no dev dependencies |
| `Dockerfile` | Same CUDA base | All extras |

All use a Node 22 frontend builder (`npm ci`, `npm run build`), Python 3.12 and uv `0.12.0`, include Node/npm/npx and LibreOffice, check for built `dist/index.html`, and expose `5050`. A GPU base image is not the same as installing the generation/retrieval extras. Nightly publishing checks daily at 00:00 UTC for recent commits and publishes moving `latest` and `v0.3.0` families. Pin digests for reproducible deployment; the package's `0.3.0.2` and container tag's `v0.3.0` are different version surfaces.[^ultrarag]

## What CI and tests establish

**Observed workflow definitions, not results from this ingestion:**

- Core job: `uv lock --check`; reject selected CUDA-13 runtime/compiler package names in the lock; `uv sync`; `pytest tests/ultrarag -q`; build/run `sayhello`.
- Frontend job: `npm ci` and `npm run build` (the build includes `tsc -b`); no separate lint step.
- CPU-image smoke: build the core CPU image, check Node/npx, and use Flask's test client to check the root HTML response.
- Dependency-resolution job: frozen all-extras dry run.

Seven top-level test files target local interpreter launch, remote MCP configuration, FAISS padding, Serply requests, query extraction, evaluation normalization, and benchmark key-map alignment. Two additional server-local tests exercise LiteLLM generation/embedding with stubs. The CI pytest command does not select all these files, and no dedicated UI auth, chat/KB API, browser/E2E, or model-quality suite was identified.[^ultrarag]

**Actual ingestion check:** Python's `ast.parse` parsed all 52 repository `.py` files without syntax errors on 2026-10-26, without imports or source execution. This only checks syntax. No installation, pytest run, npm build, lock-resolution check, container build, inference, or benchmark was performed; CI success is not inferred from reading workflows.[^ultrarag]

## Relationships

- **Supports:** [MCP orchestration](ultrarag-pipelines.md) and [UI](ultrarag-ui.md).
- **Constrained by:** [security defaults](ultrarag-security.md) before publishing the container port.
- **Depends on:** external assets required by [generation](ultrarag-generation.md), [retrieval](ultrarag-retrieval.md), and [corpus processing](ultrarag-corpus.md).

[^ultrarag]: Revision `185e2032d9f1`: `pyproject.toml` project/dependency/extras/uv-index sections; `README.md` Installation and Docker sections; `Dockerfile`, `Dockerfile.base-cpu`, `Dockerfile.base-gpu` stages/install/CMD; `ui/frontend/package.json` dependencies/scripts; `ui/frontend/vite.config.ts`; `.github/workflows/{ci-smoke,dockerhub-nightly}.yml` jobs, schedules, tags; `src/ultrarag/client.py::main`, `launch_ui`; `src/ultrarag/mcp_exceptions.py::check_node_version`; `script/vllm_serve*.sh`; demo parameter endpoints; `tests/**/*.py` and `servers/{generation,retriever}/tests/*.py` static inventory. Session-local syntax check: standard-library `ast.parse(f.read_text(encoding='utf-8'), filename=str(f))` over `Path('raw/UltraRAG').rglob('*.py')`, 52 files, zero errors, 2026-10-26; no import/test execution.
