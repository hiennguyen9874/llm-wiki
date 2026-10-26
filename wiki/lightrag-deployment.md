---
type: Concept
title: LightRAG packaging, configuration, and deployment
description: Dependency extras and runtime installs, environment layering, container variants, single-writer Helm defaults, and destructive operational boundaries.
tags: [operations, deployment, configuration]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:15:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
---

**Observed:** LightRAG offers core/API/offline dependency profiles, host and Compose setup tooling, full/lite images and a Helm chart. Packaged installation does not eliminate runtime package downloads or external NLP/model assets. **Synthesis:** reproducibility requires aligned source, lockfile/extras, model assets, backend versions and deployment configuration—not merely a pinned Python wheel.[^lightrag-aaebfe1]

## Packaging and offline assets

**Observed:** `pyproject.toml` defines Python ≥3.10, dynamic package version, API/offline-storage/offline-LLM/test/evaluation/observability extras, and server/maintenance console scripts. API dependencies carry explicit version floors/caps; their comments explain compatibility/security intent, not proof this build is vulnerability-free. Wheels include built `api/webui`/static assets, not the frontend source tree.[^lightrag-aaebfe1]

Server entrypoints and selected storage imports call pipmaster dependency checks/installers. Offline extras and pre-staged caches are necessary to avoid those downloads. Smart-heading needs pinned spaCy language-model wheels separately from its runtime; its direct-GitHub-URL requirements file is not by itself an air-gapped install recipe. Native SVG handling also depends on system libcairo, not just a Python package.[^lightrag-aaebfe1]

**Observed build surfaces, not commands executed here:** `make dev` uses uv test/offline extras and Bun install/build. Full Docker builds use frozen uv resolution, include frontend assets and spaCy models; lite omits offline provider/storage extras and those NLP models. The PostgreSQL sidecar Dockerfile builds AGE 1.7.0 for PG18. Mutable image tags and build-time downloads still exist.[^lightrag-aaebfe1]

## Configuration layers

- **Observed:** process environment wins over CWD `.env` (`load_dotenv(override=False)`) in the main configuration paths; `operate.py` additionally consults a package-directory `.env`. CLI override applies only to options with actual flags, such as host/port, bindings, working directory and SSL. Many query budgets, timeouts/concurrency, limits, auth/whitelist/CORS and VLM settings are environment/dotenv-only assignments, not CLI options. API-key resolution explicitly uses `os.getenv("LIGHTRAG_API_KEY") or args.key`, so environment wins in that case.
- Storage `config.ini` is deprecated compatibility fallback; backend environment settings take precedence. Backend-specific workspace overrides may redirect the passed workspace.
- Compose `environment:` injects container paths/hostnames over the mounted dotenv file; host-path values in `.env` do not automatically remain effective inside containers.
- `LIGHTRAG_RUNTIME_TARGET` distinguishes host versus compose configuration. The setup wizard generates `.env` and `docker-compose.final.yml`, backs up existing files, and prints startup instructions rather than starting services itself.
- **Security limit:** the tracked compose environment sample is not safe to copy unchanged; see the [redacted credential finding](lightrag-security.md).[^lightrag-aaebfe1]

## Container and Kubernetes boundaries

**Observed:** standard Compose binds the configured host/port and mounts working/input/prompt/cache-related data plus dotenv/customization files. The root entrypoint adjusts writable-directory ownership and drops to UID/GID 1000 with gosu; it deliberately does not chown mounted `.env`. Read permissions and bind-mount ownership still matter.[^lightrag-aaebfe1]

**Observed:** Helm defaults to one replica and Recreate updates; optional StatefulSet/PVC templates exist. Its shared-state rationale explicitly warns that per-host coordination does not span independent pods. A writer Service can select pod zero, but the application does not enforce read-only replicas; an external routing policy would have to separate all writes. Retained PVC annotations prevent ordinary uninstall from deleting graph/vector/upload volumes.[^lightrag-aaebfe1]

Chart configuration can render all values-env into a chart-owned Secret mounted as `.env`; `envFrom` is also available. **Synthesis:** putting secrets in values/CLI flags can retain them in release history or process arguments; a Secret resource alone is not proof of safe secret lifecycle. The chart has a readiness probe but no inspected startup/liveness probe or pod security context. Chart appVersion does not track the package version closely enough to serve as the source revision.[^lightrag-aaebfe1]

## Destructive operations and safeguards

- **Observed:** vector rebuild and selected repair tools require every writer stopped; use their dedicated runbooks, not blanket working-directory deletion.
- Kubernetes database cleanup can delete the application and KubeBlocks namespaces/PVCs without an interactive confirmation. App uninstall separately retains PVCs and prints optional deletion instructions.
- Apple-container `down --purge` removes data volumes.
- Setup rewrite modes alter generated config; release helpers alter version files; build/publish helpers push artifacts. None ran during ingestion.[^lightrag-aaebfe1]

## Relationships

- **Depends on:** [Storage](lightrag-storage.md), [concurrency](lightrag-concurrency.md), and [embedding recovery](lightrag-embedding-recovery.md).
- **Constrained by:** [Authentication/security](lightrag-security.md).
- **Checked by:** [Testing/evaluation surfaces](lightrag-testing.md), which are not a deployed-system certification.

## Evidence limits

Static manifests, scripts and selected documentation inspected; no dependency install, container image build, Helm rendering, database extension/migration, package resolver or deployment ran. Lockfile packages, registry signatures and runtime permissions were not independently verified. See [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`: `pyproject.toml` metadata/extras/scripts/package-data; `Makefile`; `Dockerfile`, `Dockerfile.lite`, `Dockerfile.postgres`, `docker-entrypoint.sh`; `docker-compose.yml`, `docker-compose.podman.yml`, `docker-compose-full.yml`; `requirements-offline*.txt`; `lightrag/api/{config,lightrag_server,run_with_gunicorn,utils_api}.py` configuration/startup, particularly `config.py::parse_args` and `lightrag_server.py` 1635; `lightrag/operate.py` package-directory dotenv load (111); `kg/{postgres_impl,neo4j_impl,pgtable_impl}.py` configuration fallback; `scripts/setup/setup.sh`, `scripts/setup/lib/file_ops.sh`, `scripts/setup/apple-container.sh`; `k8s-deploy/lightrag/{Chart.yaml,values.yaml,templates/_helpers.tpl,templates/service.yaml,templates/pvc.yaml,templates/secret.yaml}`; `k8s-deploy/{K8S-README.md,install_lightrag.sh,uninstall_lightrag.sh,databases/04-cleanup.sh}`; `docs/{DockerDeployment,InteractiveSetup,OfflineDeployment}.md`; README optional libcairo and smart-heading sections.
