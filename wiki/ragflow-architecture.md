---
type: Concept
title: "RAGFlow server architecture"
description: "Go process modes, bootstrap ordering, dependency composition, and runtime versus migration boundaries."
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
    revision: 1731e54b3aa024356711dc86de2e231afb0e4bf1
    title: RAGFlow repository snapshot
---

# RAGFlow server architecture

**Observed:** one Go server entrypoint dispatches API, admin, ingestor, syncer, DeepDoc, and migration modes. Application behavior is composed from `internal/server`, handlers/services, ingestion, agents, and engine adapters rather than a Python web server. Mode selection and dependency startup are centralized, while per-mode runners wire the required service subsets.[^ragflow]

## Process and bootstrap model

- `cmd/ragflow_server.go::main` parses mode flags, resolves configuration/identity, initializes shared infrastructure, and calls the appropriate mode runner. Multiple mode flags do not launch multiple services: the last mode flag wins.
- Standalone DeepDoc takes an early-boot path before relational DB, cache, document engine, storage, and queue initialization.
- Ordinary boot initializes the metadata DB, checks its migration version, initializes the document engine, Kvrocks, object storage and NATS, and then starts mode-specific services. Most infrastructure failures are fatal; object-storage initialization is logged without immediately aborting.
- API composition installs handler/service dependencies and process-wide component/tool registries. Ingestor wiring repeats the subset required for worker-side compilation/navigation.[^ragflow]

## Migrations are a separate action

`dao.InitDB` distinguishes full migrations from runtime-only table setup. Full migration applies manual fixes before broad `AutoMigrate`, then specialized migration steps. Normal server boot maintains Go runtime models but does not replace the standalone migration command. A shared database-version marker prevents an older non-development binary starting against a newer database.[^ragflow]

## Static failure surface

**Observed:** `storage.Init` failure is nonfatal in `main`, but `CloseStorage` calls the configured storage without a nil guard. **Synthesis:** if initialization leaves storage nil, deferred cleanup could panic; this path was not reproduced. Avoid treating a started process as proof that every storage dependency is usable.[^ragflow]

## Documentation reconciliation

The root source `AGENTS.md` describes legacy Python server directories as pending deletion, but the inspected tree no longer contains those directories. Its reference to MySQL/PostgreSQL metadata persistence also overstates the current config parser: the inspected metadata parser accepts MySQL and MySQL-wire-protocol OceanBase. Python SDK/tests/downloaders remain, so “all Python removed” would also be inaccurate.[^ragflow]

## Relationships

- **Depends on:** [persistence and engines](ragflow-persistence.md) for shared infrastructure.
- **Uses:** [agent workflows](ragflow-agent-workflows.md) and [document ingestion](ragflow-ingestion.md), wired by different mode runners.
- **Uses:** [operations](ragflow-operations.md) for native libraries, migrations, and startup procedures.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa024356711dc86de2e231afb0e4bf1`; locators: `cmd/ragflow_server.go::main / modeFlag.Set / isStandaloneDeepDocServer / checkDatabaseVersion`; `internal/server/bootstrap/bootstrap.go::GetServerType / ResolveServerName`; `internal/server/api/server.go::startServer`; `internal/server/ingestor/server.go::Run`; `internal/dao/database.go::InitDB / autoMigrateRuntimeModels`; `internal/dao/migration_version.go::migrationDBVersionMarker`; `internal/storage/storage_factory.go::CloseStorage`; `AGENTS.md::Current stack / Code Layout to Expect`; `internal/server/config/database_config.go::ParseDatabaseConfig`.
