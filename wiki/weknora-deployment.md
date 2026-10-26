---
type: Concept
title: WeKnora deployment and verification surfaces
description: Docker Compose, Helm, Lite/desktop tradeoffs, upgrade caveats, and the difference between local and CI checks.
tags: [ml, weknora, deployment]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd5855fc4ded5c981a92dcb82a455246
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora supports standard multi-service deployment and a Lite application with local infrastructure substitutes. **Observed/Synthesis:** Compose and Helm assemble a Go app, frontend, docreader, relational/vector database, and Redis; Lite selects SQLite and in-process facilities, with a Wails desktop wrapper as another delivery shell. These modes have different persistence, network, and authentication assumptions.[^weknora]

## Topology choices

| Mode | Inspected or reported distinction |
| --- | --- |
| Compose | App/UI images selected by `WEKNORA_VERSION` (default `latest`), PostgreSQL/ParadeDB, Redis, docreader; optional service profiles |
| Helm | Chart app version v0.8.3 and Kubernetes requirement >=1.25; configurable app/UI/docreader replicas and secrets |
| Lite | Build target with `sqlite_fts5`; example selects SQLite retrieval, local storage, memory stream manager, disabled sandbox |
| Desktop | Lite runtime wrapped in Wails; README says no published installer yet |

**Observed:** Compose binds UI port 80 and API port 8080 by default, requires `.env`, and mounts `config/config.yaml`. Docreader has no host port mapping by default. The app health check targets `/health`. Optional README profiles include `neo4j`, `minio`, `langfuse`, and `full`; not every service inside every profile was reviewed.[^weknora]

## Operations, not executed here

The README's standard procedure is `cp .env.example .env`, edit configuration, then `docker compose pull` and `docker compose up -d`. It explicitly warns that `up -d` alone may reuse cached images and leave UI/release versions mismatched. **Reported:** production should use private/internal networking, controlled firewall exposure, and regular security updates. Copying a template is not production hardening.[^weknora]

**Observed:** the Lite systemd unit uses a dedicated service user, `NoNewPrivileges`, strict system protection, home protection, and an explicit writable data path. Helm secret templates reuse existing generated secrets on upgrade. Deleting/recreating those secrets can lose the encryption identity needed by stored credentials; see [configuration](weknora-configuration.md).[^weknora]

## Verification surface

**Observed:** `Makefile::test` invokes `go test -v ./...`, while the inspected app CI workflow filters `/docreader/` packages and separately tests a desktop-tagged container build. These are different check scopes, not equivalent “all tests passed” gates. Helm includes render-level storage tests; frontend and CLI have separate suites. **No upstream build, test, migration, Compose, Helm, or deployment command was run during this ingest.**[^weknora]

## Version differences worth preserving

Compose pins ParadeDB `v0.25.11-pg17`; the inspected Helm values use `v0.18.9-pg17`. These are different declared baselines, not evidence of a failed chart. Lite's example retains an `ENABLE_GRAPH_RAG` knob while Compose comments call that old flag superseded by `NEO4J_ENABLE`; the effective consumer of the legacy flag was not established.[^weknora]

## Relationships

- Deploys the [backend architecture](weknora-backend-architecture.md).
- Requires deliberate [configuration/key management](weknora-configuration.md) and [security posture](weknora-security.md).
- Queue and stream durability depend on the [Redis versus Lite choice](weknora-task-queues.md).

## Coverage limits

Compose app/core wiring, selected chart values/secrets, Lite docs/template/unit, Make targets, and selected CI sections were inspected. Most Dockerfiles, chart templates, release scripts, full workflows, upgrade migrations, and actual infrastructure compatibility remain pending. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd5855fc4ded5c981a92dcb82a455246`: `docker-compose.yml::services.frontend`, `app`, `docreader`, `postgres`, `redis` and graph-flag comments; `helm/Chart.yaml::appVersion`, `kubeVersion`; `helm/values.yaml` replica/image keys; `helm/templates/secrets.yaml` existing-secret lookup; `helm/tests/test_app_storage.py`; `.env.lite.example` driver/stream/sandbox keys; `Makefile::build-lite`, `run-lite`, `test`; `deploy/weknora-lite.service`; `.github/workflows/app.yml` Go vet/test steps; `.github/workflows/helm.yml`; `docs/LITE.md`, comparison matrix. Package entry: [README](../raw/WeKnora/README.md), “Run with Docker Compose,” “Optional services,” “Upgrading,” “Other ways to deploy,” and “Validating your change.”
