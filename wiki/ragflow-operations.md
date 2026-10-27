---
type: Concept
title: "RAGFlow build, deployment, and testing"
description: "Native build prerequisites, asset provisioning, Compose startup/migrations, configuration rendering, and unexecuted test tiers."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
---

# RAGFlow build, deployment, and testing

**Observed:** the main image builds a Go backend and React frontend with native parsing/tokenization libraries and a separate dependency-assets image. Docker startup runs migrations before supervised API/admin/syncer/ingestor processes. A working source checkout alone is insufficient: model weights, native archives, tokenizer assets and external services must also be provisioned.[^ragflow]

## Build and external asset contract

- The module declares Go 1.27; `build.sh` help advertises an older floor, so the module directive is the stronger snapshot constraint. Frontend package declarations and CI toolchain choices should likewise be checked together rather than relying only on the Node engines field.
- `build.sh` builds the C++ tokenizer and a CGO-enabled Go binary with static/native flags. Dependencies include ONNX Runtime 1.29.0, pdfium-static 7809, pdf_oxide 0.3.73 and office_oxide 0.1.12. It assembles CGO link paths and requires an LLD linker on Linux; project guidance recommends LLD 20 and a post-build startup smoke check.
- Native archives come from `tools/scripts/download_dev_deps.py`; models, cl100k BPE/tokenizer assets and browser support assets come from `deps/download_deps.py` and `ragflow_deps`. Scripts/downloads were inspected, not run.
- Docker's asset-copy loop fails if required embedding tokenizer assets are missing. VERSION is generated from git metadata during image build; the `.git` build context is material. This resolves the earlier question raised by an entrypoint-only inspection about where VERSION originates.
- The main image does not install a Python application runtime, but Python downloaders, SDK/tests and older Dockerfiles remain in source. Do not describe the repository as containing no Python.[^ragflow]

## Startup, configuration and exposure

The entrypoint regenerates `conf/service_conf.yaml` from its template at every boot; operator changes belong in the template/environment, not only the rendered file. It runs `ragflow_server --migrate`, then starts enabled modes under a restart loop; API/ingestor/syncer are enabled by default and admin is opt-in at the script level. Compose's default command enables admin. The dependency DB init SQL only creates the database, not the full schema.[^ragflow]

Compose publishes web 80/443, API 9380 and admin 9381 by default; dependency services and optional components publish additional ports. nginx routes admin before general API and serves the SPA. Configuration and published ports must be reviewed before exposure, especially credential defaults, TLS and proxy trust. The README recommends a starting 4 CPU cores/16 GB RAM/50 GB disk and Elasticsearch `vm.max_map_count` tuning; these are **Reported** recommendations, not measured minimums.[^ragflow]

## Commands to consider, not executed here

```bash
# Dependency download/build steps can fetch code and large binary assets.
uv run tools/scripts/download_dev_deps.py
bash build.sh --all
# Requires prepared native libraries/assets even for unit tests.
bash build.sh --test
bash build.sh --test-integration ./...
bash build.sh --test-e2e
# Compose starts services and changes persistent database state via migrations.
cd docker && docker compose -f docker-compose.yml up -d
# Runtime readiness check, only after starting a deployment.
curl -f http://localhost/api/v1/system/healthz
```

These commands are documented interfaces, not an authorization to run them in an arbitrary environment; review credentials, volumes, network access and backups first.[^ragflow]

## Tests and CI boundaries

The project separates default unit tests from `integration`, `e2e` and local-only `manual` build tags, with orthogonal native/cgo requirements. Unit tests can avoid external services but still need native link assets. The main CI workflow gates jobs by labels/draft status and change detection, runs separate engine/native/integration jobs, and includes Python SDK tests. Manual tests are not intended for CI. Codecov status checks are disabled in config. No application tests, build, benchmark, container or service was run during this ingest.[^ragflow]

## Static documentation hazards

`Dockerfile_ci` copies removed Python server directories, and `run_tests.py` defaults to a missing test directory: these paths are stale for the inspected tree. Compose/comments still mention removed Redis/Valkey/Go-specific file names. `docker/migration.sh` names legacy backup volumes, so it is not evidence of a complete backup plan for the current Kvrocks/NATS/ClickHouse stack. CLI release-platform support does not establish backend native support on those same platforms.[^ragflow]

## Relationships

- **Depends on:** [server modes/migrations](ragflow-architecture.md), [persistence services](ragflow-persistence.md) and [redacted security constraints](ragflow-security.md).
- **Constrains:** reproducibility of [ingestion](ragflow-ingestion.md), [agents](ragflow-agent-workflows.md) and [frontend](ragflow-frontend.md).

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa0`; locators: `go.mod::go / require`; `web/package.json::engines / scripts`; `build.sh::check_cpp_deps / check_go_deps / setup_cgo_env / build_go / show_help / run_go_tests / run_go_tests_tagged`; `Dockerfile::base / web-builder / go-builder / production / ORT_VERSION / VERSION generation / tokenizer asset loop`; `deps/Dockerfile::asset image COPY`; `deps/download_deps.py::DEEPDOC_MODEL_FILES / TOKENIZER_ASSETS / STAGEHAND_SERVER_VERSION`; `tools/scripts/download_dev_deps.py::native versions`; `docker/entrypoint.sh::CONF_DIR rendering / run_go_migrations / run_with_restart`; `docker/docker-compose.yml::ports / command / include`; `docker/docker-compose-base.yml::services / volumes`; `docker/init.sql::CREATE DATABASE`; `docker/nginx/ragflow.conf::location blocks`; `README.md::Docker Deployment Prerequisites / Start up the server`; `AGENTS.md::Go Test Tiers / Commands / Validation Preference`; `docs/develop/launch_ragflow_from_source.md::build and startup instructions`; `Dockerfile_ci::legacy COPY`; `run_tests.py::Config.__init__`; `docker/migration.sh::volume names`; `.github/workflows/sep-tests.yml::ragflow_preflight / ragflow_python_sdk_unit / ragflow_native_backend / ragflow_go_integration`; `codecov.yml::coverage.status`.
