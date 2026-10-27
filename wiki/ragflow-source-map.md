---
type: SourceMap
title: "RAGFlow source map and coverage"
description: "Pinned RAGFlow source identity, tracked-artifact inspection ledger, redacted security handling, exclusions, and pending verification."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:16:02Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
---

# RAGFlow source map and coverage

This SourceMap records a **partial, static repository ingest** of RAGFlow at revision `1731e54b3aa0`. The canonical entrypoint is [README.md](../raw/ragflow/README.md), the package scope is `raw/ragflow/`, and the upstream named by the entrypoint is `https://github.com/infiniflow/ragflow`. The inspected license is Apache-2.0. No independent runtime or benchmark verification occurred.[^ragflow]

## Identity and idempotency

All RAGFlow concepts declare the same scope/revision identity; supporting files are not separate sources. Primary domain is `ml`. Language is English with original technical terms. For a future ingest, reconcile this map, every concept citing the package, and the [tracked-path ledger](ragflow-source-coverage.tsv) before changing content. A repeated request is not a no-op merely because the README was read: pending coverage is explicit.[^ragflow]

## Coverage ledger

The ledger contains **5,482 tracked paths** from `git ls-files` at the pinned revision: **263 excluded, 1 excluded-key-material, 1 excluded-sensitive, 6 inspected-redacted, 1 inspected-sensitive, 241 inspected-static, 4969 pending**. Statuses preserve the distinction between targeted inspection and mere discovery. An `inspected-static` row means a substantive excerpt or symbol read/grep was reported in this session; it does not mean whole-file review. Sensitive rows record only category and handling. No source artifact was executed.[^ragflow]

| Area | Inspected owner paths | Consequential remaining limits |
| --- | --- | --- |
| Entry/manifests | README, LICENSE, go.mod, web/package.json, pyproject | README images/remote docs are not imported evidence; full dependency graph not audited |
| Bootstrap/persistence | cmd/server, config parsers, DAO migration, engine/global, ES chunk/client, storage factory, Kvrocks/NATS | Live migrations, all storage implementation bodies, non-ES engine parity and EE additions unverified |
| Ingestion | pipeline/template, parser dispatch, general chunker, tokenizer/extractor, task/indexdoc and writer | Many parser/chunker/native implementations, fixtures and failure paths pending |
| Retrieval/citations | NLP retrieval/query/reranker, dataset search, conventional and agentic citations | Quality/faithfulness, engine equivalence, UI citation rendering and performance not tested |
| Compilation | compiler dispatch, representative wiki/structure/tree/mindmap, scheduler/consumer/writer/merge | Full prompt/cache/state/merge closure and incremental correctness not tested |
| Agents/harness | canvas/compiler/runner, registry, loop/parallel, agentic entry, harness contracts | Tool/sandbox bodies and graph internals sampled or pending; harness external-import conclusion is static negative evidence |
| Frontend/API | routes, package/config, hook/service/request/SSE chain, canvas store | Most feature screens/UI components/locales/accessibility and browser execution pending |
| Sync/MCP/permissions/channels | syncer runner/registry/SSRF, policy/query scope, MCP handlers/client, channel bootstrap/auth excerpts | Individual connectors, service authorization closure, protocol lifecycle and most channel internals pending |
| Build/deployment/CI | Dockerfile/assets/entrypoint/compose, build functions, CI job excerpts | Full workflow branches, backup correctness, native archives and external services unverified |

The TSV, not this summary table, is the per-artifact accounting record. Uninspected source/tests/docs/configs remain `pending`, rather than being excluded simply for size.[^ragflow]

## Attachments, generated files and external dependencies

- Translated READMEs are excluded as duplicate entrypoint surfaces; generated lock/checksum files are excluded from semantic extraction, not claimed verified.
- Selected UI images/fonts are excluded as decorative assets; layout/rendering was not evaluated. The README architecture diagram, linked GIFs/screenshots and remote release/docs pages were not fetched. Architecture here is reconstructed from code, not a visual reading of that diagram.
- Binary models, native static libraries, cl100k/embedding tokenizer assets, browser binaries and the dependency image are material but were not downloaded or executed. Their provisioning contracts were inspected; successful retrieval, integrity and compatibility remain unavailable evidence.
- External Go/npm/Python dependency bodies, cloud/model providers and infrastructure services were not audited. Manifests/downloader declarations are observed; external behavior is unverified.
- Git metadata is used for revision/path inventory, not ingested as application knowledge. Untracked build/cache artifacts are outside the tracked snapshot ledger.[^ragflow]

## Security and disclosure disposition

A tracked private key plus an embedded loader passphrase were discovered. The human directed continuation after disclosure. Only a [redacted security note](ragflow-security.md) is compiled; no key, passphrase, infrastructure password, token or PII is copied. Whether these defaults are used in a live deployment remains unknown. Raw source stays untouched; repository-level distribution still includes its raw evidence. No remediation was performed.[^ragflow]

## Documentation drift and uncertainty

Root instructions retain deleted Python-server paths; metadata config is narrower than the docs' MySQL/PostgreSQL description; harness README paths do not match the tree; older Python Docker/test entrypoints target absent paths. Main Dockerfile generation of VERSION resolves the initial entrypoint-only uncertainty about that file. Broader support/default claims use current owning code where inspected and remain qualified elsewhere.[^ragflow]

## Relationships

- **Documents:** [RAGFlow overview](ragflow.md) and all linked subsystem concepts.
- **Constrains:** the maturity of every RAGFlow page; all are `draft` because coverage/verification work remains.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa0`; locators: `README.md::What is RAGFlow? / System Architecture / Local Deployment`; `LICENSE::Apache License Version 2.0`; `go.mod::module / go / require`; `web/package.json::dependencies`; `AGENTS.md::Current stack / Code Layout to Expect`; `internal/server/config/database_config.go::ParseDatabaseConfig`; `internal/harness/README.md::Project Structure`; `Dockerfile::VERSION generation / dependency image mounts`; `Dockerfile_ci::legacy COPY`; `run_tests.py::Config.__init__`; `deps/download_deps.py::DEEPDOC_MODEL_FILES / TOKENIZER_ASSETS`; `tools/scripts/download_dev_deps.py::native dependency declarations`; `internal/common/password.go::LoadPrivateKey`; `git ls-files at pinned revision::tracked path inventory; ragflow-source-coverage.tsv::path/status/reason`.
