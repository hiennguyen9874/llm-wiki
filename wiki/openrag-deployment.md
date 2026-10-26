---
type: Concept
title: "OpenRAG deployment and operational constraints"
description: "Compose, local-development and Kubernetes deployment surfaces, storage/network defaults, destructive commands, and static deployment hazards."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d
    title: OpenRAG repository
---

**Observed:** OpenRAG ships terminal-managed, Compose, host-development, Helm, and operator deployment surfaces, but their defaults and maturity differ. The inspected artifacts are deployment recipes, not evidence that any image, chart, or installation works at this snapshot.[^openrag-repo]

## Commands and topology

**Observed Make targets:** `make setup`, `make dev` (GPU) / `make dev-cpu`; `make dev-local` with separate `make backend` / `make frontend` supports host app development. The Python package's `openrag` command enters the Textual TUI. These commands were inspected, not executed.[^openrag-repo]

Compose publishes frontend 3000, Langflow 7860, OpenSearch 9200/9600, and Dashboards 5601; backend 8000 is internal in the base configuration. Backend mounts cover keys, flows/backups, config, data, and documents; OpenSearch and Langflow have persistent storage. Public service exposure and gateway identity assumptions must be reviewed together.[^openrag-repo]

The backend declares Python ≥3.13; CI and `.python-version` select 3.13 while the backend image uses 3.14. Ruff targets py312. The Helm chart app version differs from package `0.5.0`. These are observed version surfaces, not proof of incompatibility.[^openrag-repo]

## Concurrency and prerequisites

`MAX_WORKERS=4` describes task processing, not permission to run four backend processes: startup rejects multiple Uvicorn workers and non-memory cache backends. Langflow worker settings are a separate concern. Supply environment-specific session/encryption/admin secrets and review RBAC, TLS verification, and trusted header handling; see [security](openrag-auth-security.md).[^openrag-repo]

Helm uses a single backend replica/Recreate strategy and persistent volumes, including RWX shared storage and RWO data volumes. Its supplied StorageClass is IBM-specific with delete reclamation; ingress needs host configuration and TLS is off by default. A stock chart is not a provider-neutral production hardening profile.[^openrag-repo]

## Destructive operations

- `factory-reset` removes volumes/local state and keys, with a prompt unless forced.
- `clean` force-removes shared images without the same confirmation.
- `db-reset` and `clear-os-data` delete indexed state.
- `test-ci` teardown uses volume removal.
- Documentation's stop-all snippet stops **all** Docker/Podman containers, not only OpenRAG.

**Synthesis:** inspect these recipes and scope storage/containers before execution; their names alone do not define a safe blast radius.[^openrag-repo]

## Static deployment hazards

- `.dockerignore` excludes `*.json` with exceptions only for package manifests/locks, while Dockerfiles copy `flows/`. **Synthesis, unbuilt:** flow JSON may be absent from image build context; mounts/init downloads can mask packaging issues.
- The Helm backend readiness script sets `FAILED=1` after a failed Langflow check but ends with unconditional `exit 0`. **Observed:** the scripted dependency failure does not fail readiness.
- Flow init download and load paths differ across Helm values/templates. **Unverified:** no chart rendering or pod filesystem inspection established effective flow loading.
- Operator Langflow worker configuration differs from Compose and relies on an image flag allowing multi-worker execution without a shared queue. **Synthesis:** scaling requires separate validation, not just changing replicas.[^openrag-repo]

## Relationships

- Depends on [backend architecture](openrag-backend-architecture.md) and [security](openrag-auth-security.md).
- Supplies runtime assets for [Langflow workflows](openrag-langflow-workflows.md); evaluated by [testing](openrag-testing.md).

## Coverage limits

No container build, chart render, startup, TUI workflow, upgrade, backup/restore, or destructive action was executed. Operator reconciliation internals and many TUI/package assets remain pending; seven dangling asset links are recorded in the [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d`: `Makefile::{setup,dev,dev-cpu,dev-local,backend,frontend,factory-reset,clean,db-reset,clear-os-data,test-ci}`; `pyproject.toml::{project.requires-python,project.scripts,tool.ruff}`; `.python-version`; `Dockerfile{,.backend,.frontend,.langflow}`; `.dockerignore`; `docker-compose.yml::services/volumes`; `src/app/lifespan.py::run_startup`; `kubernetes/helm/openrag/{Chart.yaml,values.yaml}`; `templates/backend/deployment.yaml::readinessProbe/load-default-flows`; `templates/storage/backend-sc.yaml`; `templates/langflow/deployment.yaml`; `kubernetes/operator/internal/controller/env.go`; `docs/docs/_partial-docker-stop-all.mdx`.
