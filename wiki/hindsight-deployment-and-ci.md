---
type: Concept
title: Hindsight deployment, monitoring and CI/release
description: How Hindsight is deployed (Docker targets, compose variants, Helm), monitored (Prometheus metrics, Grafana dashboards) and released through GitHub Actions.
tags: [agent-memory, hindsight, deployment, docker, helm, ci]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: dockerfile
    resource: ../raw/hindsight/docker/standalone/Dockerfile
    kind: code
    revision: eb963cb
    title: Standalone Dockerfile
  - id: helm-chart
    resource: ../raw/hindsight/helm/hindsight/Chart.yaml
    kind: config
    revision: eb963cb
    title: Helm chart manifest
  - id: monitoring-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/monitoring.md
    kind: documentation
    revision: eb963cb
    title: Monitoring developer doc
  - id: release-wf
    resource: ../raw/hindsight/.github/workflows/release.yml
    kind: config
    revision: eb963cb
    title: Release workflow
---

Hindsight deploys as a stateless API container (plus optional worker and control-plane containers) over PostgreSQL; options range from a single `docker run` to a Helm chart.[^readme] Defaults below are static observations of the 1.2.0 snapshot (hence `stale_after`).

## Docker

- `docker/standalone/Dockerfile` builds by `--target`: `standalone` (API + control plane; ports 8888 and 9999), `api-only` (8888), `cp-only` (9999). Build args `INCLUDE_LOCAL_MODELS` and `PRELOAD_ML_MODELS` (default true; preload `BAAI/bge-small-en-v1.5` and `hindsight-ai/hs-rerank-1`). Slim images set both to false.[^dockerfile][^release-wf]
- `docker/standalone/start-all.sh` starts the API, waits for `/health` (default 300 s), then the control plane; handles pg0 checks and SIGTERM (60 s; compose sets 75 s).[^dockerfile]
- Compose variants under `docker/docker-compose/`: `external-pg` (pgvector pg18), `alloydb`, `vchord`, `pg_search`, `pg_textsearch`, `pgroonga`, `timescale`, `s3-file-storage` (SeaweedFS), `tei` (embedding and reranker sidecars), `local-llm` (llama.cpp), `cuda`/`cuda-onnx`, `custom-models`, `nginx` (base path `/hindsight`), `claude-code`. Compose files carry a placeholder DB password default; production deployments must override it.[^dockerfile]
- README one-liner exposes 8888/9999 with volume `hindsight-data:/home/hindsight/.pg0`.[^readme]

## Helm

`helm/hindsight` chart 1.2.0 (Kubernetes 1.19+, Helm 3): components `api` (ClusterIP 8888; resources 500m/1Gi→2000m/4Gi), `worker` (StatefulSet, disabled by default, port 8889), `controlPlane` (port 3000), in-chart `postgresql` (`ankane/pgvector:latest`, 8Gi; defaults for user/password/db are all `hindsight`), optional TEI reranker and embedding sidecars, ingress or Gateway API HTTPRoute, HPA, PDB, ServiceMonitor, `extraObjects`. Install: `helm install hindsight oci://ghcr.io/vectorize-io/charts/hindsight --set api.llm.provider=… --set postgresql.enabled=true`.[^helm-chart][^readme]

## Monitoring

Prometheus at `/metrics` (API 8888, worker 8889), OTLP tracing, `/health/live` vs `/health/ready`. Metric families: `hindsight_http_*`, `hindsight_operation_*`, `hindsight_llm_*` (calls, input/output tokens, latency by `scope`), `hindsight_db_pool_*`, `hindsight_process_*`. Three Grafana dashboards live in `monitoring/grafana/dashboards/` (`hindsight-api-service`, `hindsight-llm`, `hindsight-operations`); the repo has no Prometheus scrape config or Grafana provisioning (Observed).[^monitoring-doc]

## CI and release (`.github/workflows/`)

`test.yml` (~85 path-filtered jobs: API shards, LLM-gated acceptance, Oracle, blackbox system tests not secret-gated, per-integration jobs, client tests in 5 languages, docker build, Helm lint), `release.yml` (on `v*` tags: PyPI trusted publishing for six Python packages, npm, Rust CLI, ghcr.io images `hindsight-api`, `-slim`, `hindsight-control-plane`, `hindsight`, `hindsight-slim`, OCI Helm chart, GitHub release), `release-integration.yml`, `perf-test.yml` (daily), `security-scan.yml` (daily Trivy HIGH/CRITICAL), `sign-images.yml` (cosign), `windows-smoke.yml`, `deploy-docs.yml`, `triage-labels.yml`.[^release-wf]

## Relationships

Config knobs: [Storage and configuration](hindsight-storage-and-configuration.md). Test content: [Benchmarks and testing](hindsight-benchmarks-and-testing.md). Release script and rules: [Contributor workflow](hindsight-contributor-workflow.md). UI container: [Control plane](hindsight-control-plane.md).

[^readme]: `README.md` § "Quick Start" (Docker, Helm).
[^dockerfile]: `docker/standalone/Dockerfile`, `start-all.sh`; `docker/docker-compose/*/docker-compose.yaml`.
[^helm-chart]: `helm/hindsight/Chart.yaml`, `values.yaml`, `templates/`; `helm/hindsight/README.md`.
[^monitoring-doc]: `hindsight-docs/docs/developer/monitoring.md`; `monitoring/grafana/dashboards/*.json`.
[^release-wf]: `.github/workflows/{test,release,release-integration,perf-test,security-scan,sign-images,windows-smoke,deploy-docs,triage-labels}.yml`.
