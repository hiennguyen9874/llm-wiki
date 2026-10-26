---
type: Concept
title: WeKnora backend architecture and technology stack
description: Go/Gin service composition, dependency injection, startup, shutdown, and standard-versus-Lite runtime choices.
tags: [ml, weknora, architecture]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora's backend is a Go/Gin application assembled through an Uber Dig dependency-injection container. **Observed:** bootstrap binds repositories, services, handlers, pipeline plugins, external clients, and asynchronous workers into one application process; standard and Lite editions select different persistence and queue implementations rather than separate business applications.[^weknora]

## Stack and process boundaries

**Observed dependency declarations** in `go.mod`: Go 1.26.0, Gin 1.12.0, GORM 1.31.1, Dig 1.19.0, Asynq 0.26.0, golang-migrate 4.19.1, gRPC 1.81.0, and Wails 2.12.0. These are declared versions, not confirmation that dependencies build or interoperate in this environment.[^weknora]

The main server entry is `cmd/server/main.go::main`; composition lives in `internal/container/container.go::BuildContainer`, and the global container in `internal/runtime/container.go`. Parsing can cross into a Python docreader service over gRPC or HTTP (`initDocReaderClient`); graph and tracing services are optional (`initNeo4jClient`, `initLangfuse`). **Synthesis:** a modular monolith with external infrastructure is a more useful reading of this code than independent microservices for each feature.[^weknora]

## Startup and shutdown

**Observed:** provider registration order matters. Pipeline plugin invocation can instantiate session services before reapers start, and pending wiki triggers are recovered after task-handler registration. `must` panics on wiring errors; startup bootstrap backfills legacy API-key hashes and can promote an initial system administrator, with bootstrap errors handled non-fatally.[^weknora]

The server retries listener binding, starts catalog/settings notifications, and serves HTTP. Shutdown first drains HTTP, then cleans resources; the default budget is 30 seconds split into 25 seconds drain and 5 seconds cleanup. Cleanup hooks run in reverse registration order with bounded individual steps; a second signal forces closure (`runtime/shutdown.go`, `container/cleanup.go`). This is static lifecycle inspection, not a reproduced graceful-shutdown guarantee.[^weknora]

## Edition-dependent wiring

- `DB_DRIVER` selects PostgreSQL or SQLite; SQLite constrains open connections to one.
- Empty `REDIS_ADDR` disables the Redis client and selects an in-process executor instead of Asynq.
- Automatic migrations run unless disabled; dirty-migration recovery has a separate switch.
- Lite embeds the frontend; the desktop wrapper selects Lite behavior.[^weknora]

## Relationships

- Uses [domain persistence and migrations](weknora-persistence.md).
- Starts [worker queues](weknora-task-queues.md).
- Configured by [layered configuration](weknora-configuration.md); deployed through [standard, Helm, or Lite topologies](weknora-deployment.md).
- Overview: [WeKnora](weknora.md).

## Coverage limits

Selected bootstrap, wiring, router, and lifecycle sections were inspected. Most feature-service bodies and platform-specific desktop lifecycle paths remain pending. Runtime shutdown/server test files were read but not executed. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd58`: `go.mod` dependency declarations; `cmd/server/main.go::main`; `cmd/server/bootstrap.go::runStartupBootstrap`; `internal/runtime/container.go::GetContainer`; `internal/container/container.go::BuildContainer`, `must`, `initDatabase`, `initRedisClient`, `initDocReaderClient`, `initNeo4jClient`, `initLangfuse`; `internal/runtime/shutdown.go::ShutdownBudgets`; `internal/container/cleanup.go::ResourceCleaner.Cleanup`; `internal/router/router.go::NewRouter`; `cmd/desktop/main.go::ensureDesktopLiteEdition`; `Makefile::build-lite`. Package entry: [README](../raw/WeKnora/README.md), “Architecture” and “Other ways to deploy.”
