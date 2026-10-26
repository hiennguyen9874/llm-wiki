---
type: Concept
title: Ragas installation, CLI and test operations
description: Python packaging, uv workspace, template scaffolding and CI checks coexist with unfinished CLI evaluation contracts and unexecuted provider-dependent suites.
tags: [operations, rag, packaging, testing, cli]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:28:37Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234c060deacab3cf5fb52aa3a20e885
    title: Ragas repository
---

**Observed:** Ragas is distributed as a Python library and Typer CLI, with setuptools/SCM dynamic versioning and an examples workspace package. The repository configures lint/type/unit-test and release lanes, but that configuration is not proof those checks pass. This compilation performed source inspection and syntax parsing only.[^ragas-298b682]

## Installation and stack

The root manifest requires Python >=3.9, Pydantic >=2, NumPy >=1.21,<3, datasets >=4, OpenAI >=1, Instructor, tiktoken, LangChain packages, Pillow, NetworkX/scikit-network, diskcache, Typer/Rich and other utilities. Many dependencies are broadly ranged/unpinned. Extras add tracing, Drive, Git, AG-UI, OCI, DSPy and framework tooling. `examples` is a separate workspace member; docs' `ragas[examples]` and lazy-import `ragas[experimental]` hints do not correspond to extras declared in the inspected root manifest.[^ragas-298b682]

Source-documented commands include `pip install ragas`, editable local installation, `make setup-venv`, `make install-minimal` and `make install`. These commands were not executed; pin the source revision and resolve/test dependencies before treating them as reproducible deployment instructions. No hosted server/database deployment is established by this packaging review.[^ragas-298b682]

## CLI implementation and drift

- `quickstart` offers nine templates in code, despite the README listing only rag_eval as available. It searches installed examples, then the development tree, then downloads unpinned GitHub main.zip. A future fallback template need not match this revision.
- `evals` executes a user-selected evaluation module and looks for project-like get_dataset/get_experiment and a `run_async` experiment object. Current `@experiment` wrapper exposes `arun` instead; Project is marked unimplemented in source comments. **Synthesis:** current decorator objects do not satisfy this command's protocol without compatibility code; do not advertise it as a verified end-to-end runner.
- `hello_world` writes sample CSV/code containing commented Project TODOs. Help/scaffold tests do not establish the generated workflow runs.

Use [the actual experiment API](ragas-experiments.md) or [legacy evaluator](ragas-legacy-evaluation.md) consciously rather than treating docs snippets as interchangeable.[^ragas-298b682]

## Configured checks versus executed checks

| Surface | Source configuration / inspected intent |
| --- | --- |
| Formatting/type | Ruff and pyright basic; local precommit runs Ruff formatting checks plus lint, not pyright or tests |
| Unit CI | Linux Python 3.9/3.12/3.13, macOS 3.11, Windows 3.10; platform-specific notebook/slow/xdist choices; telemetry disabled |
| e2e/docs/benchmarks | Provider/data-dependent tests outside configured unit lane; broad pytest collection is not proven offline-safe |
| Release | Package/examples build and PyPI publication workflows; attestations explicitly disabled in inspected publish config |

**Reproduced, syntax-only session check:** standard-library ast.parse passed all 387 tracked Python files under Python 3.12.3/Linux, without importing project modules. This does not check dependency resolution, imports, typing, tests or model compatibility. Details and artifact-level ledger are in the [source map](ragas-source-map.md).

## Trust and remaining limits

`benchmarks-docker` passes an environment API key as a Docker build arg and the benchmark Dockerfile promotes it to ENV; that pattern can embed a supplied credential in image configuration. AI documentation workflows include pull_request_target/fork checkout/write permissions and secret-bearing actions. These are [static trust concerns](ragas-security.md), not attempted exploits. No upstream tests, notebooks, builds, release jobs, provider calls or Git-versioning helper ran.[^ragas-298b682]

[^ragas-298b682]: Ragas `298b68274234c060deacab3cf5fb52aa3a20e885`, `pyproject.toml::project/project.optional-dependencies/build-system/tool.uv.workspace/tool.pytest`; `README.md::Installation/Quickstart`; `src/ragas/__init__.py::__getattr__`; `examples/README.md::Installation`; `Makefile::setup-venv/install-minimal/install/run-ci/benchmarks-docker`; `src/ragas/cli.py::quickstart/evals/hello_world/load_eval_module`; `tests/unit/test_cli.py`; `.pre-commit-config.yaml`; `.github/workflows/ci.yaml::unit_tests/code_quality_check`; `.github/workflows/python-publish.yml`; `.github/workflows/publish-examples.yml`; `.github/workflows/claude-docs-check.yml`; `tests/benchmarks/Dockerfile`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
