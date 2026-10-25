---
type: Concept
title: Pi Durable Storage Backends
description: Pi Durable's storage options and their guarantees, including SQLite, JSONL, IndexedDB, Cloudflare Durable Objects, namespacing, transaction rules, and conformance testing.
tags: [pi-durable, storage, sqlite, cloudflare]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:12:06Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-readme
    resource: ../raw/pi-durable-readme.md
    kind: docs
    title: "@earendil-works/pi-durable README"
  - id: tannermidd-durable
    resource: ../raw/tannermidd-durable/index.md
    scope: ../raw/tannermidd-durable/
    kind: article
    title: "Pi Durable, explained (Pi Pocket guide)"
  - id: flaviocopes-pi-durable
    resource: ../raw/flaviocopes-pi-durable/index.md
    scope: ../raw/flaviocopes-pi-durable/
    kind: article
    title: "How to build agents that survive crashes with Pi Durable"
  - id: earendil-pi-durable-on-cloudflare
    resource: ../raw/earendil-pi-durable-on-cloudflare/index.md
    scope: ../raw/earendil-pi-durable-on-cloudflare/
    kind: article
    title: "Pi Durable on Cloudflare"
---

Pi Durable runs on an open storage that writes atomic commit batches, and the README offers five backends with different durability and hosting trade-offs. One process owns a storage at a time; there is no cross-process locking, so a second process should open `readOnly: true` when it only displays a session.[^pi-durable-readme]

## Backends

| Backend | Import | Characteristics |
| --- | --- | --- |
| Memory | `MemoryStorage` from the package root | Nothing persisted. |
| IndexedDB | `IndexedDbStorage.open(name)` from `@earendil-works/pi-durable/storage/indexeddb` | Browser-only storage in one IndexedDB database. |
| SQLite | `openNodeSqliteStorage(file)` from `@earendil-works/pi-durable/storage/sqlite/node` | One database file; WAL mode with `synchronous = NORMAL`, so commits survive process crashes but the newest may be lost on power or host failure. |
| JSONL | `openNodeJsonlStorage(directory, context)` from `@earendil-works/pi-durable/storage/jsonl/node` | Append-only files in one directory; `{ fsync: true }` flushes before each commit marker. Keeps the whole history in memory, so memory grows with it; use SQLite for long-running agents. |
| Cloudflare Durable Object | `openDurableObjectSqliteStorage(ctx.storage)` from `@earendil-works/pi-durable/storage/sqlite/cloudflare` | The SQLite storage of one SQLite-backed Durable Object; commits are its storage transactions. |

In a browser, one owner must hold the IndexedDB database at a time; the README recommends a Web Lock around its lifetime rather than opening it in competing tabs or workers, and `navigator.storage.persist()` when durable retention matters.[^pi-durable-readme]

## Keeping the database across deployments

A process crash is recoverable because the database file survives; a container replacement is not, if the database lived on the container's temporary filesystem. The operational rule is to mount persistent storage, keep the same database path, and stop the old owner before starting its replacement. A deleted database cannot be resumed, and SQLite's WAL with `synchronous = NORMAL` can still lose the newest commits on a power or host failure. Conversations and tool output are application data — they can carry private prompts and service information — so restrict access and back them up.[^flaviocopes-pi-durable]

## Namespacing and sharing a database

SQLite storage can namespace its tables and indexes with `{ prefix: "pi_" }` on `SqliteStorage.open`, `openNodeSqliteStorage`, or `openDurableObjectSqliteStorage`. The prefix is rendered into the SQL, so adapters need no support; it must be a SQLite identifier and cannot begin with `sqlite_`, and a host may reserve more, such as `_cf_` in Durable Objects. Changing the prefix does not migrate existing data.[^pi-durable-readme]

On Cloudflare, multiple Pi storages opened through the adapter with the same storage object automatically share an operation queue. To share the database with host tables, the host should create a `DurableObjectSqliteDatabase`, use it for both Pi and host queries, and open Pi with `SqliteStorage.open(database, { prefix: "pi_" })`; direct storage calls bypass the queue and may be rolled back with a Pi transaction.[^pi-durable-readme]

## Portable cores and adapter contract

The portable SQLite and JSONL cores (`/storage/sqlite`, `/storage/jsonl`) run without Node APIs, for example on Bun or in Cloudflare Durable Objects, given an asynchronous `SqliteDatabase` facade or a `FileSystem` from `@earendil-works/pi-durable/env`. SQLite adapters implement promise-based `exec`, `run`, `get`, `all`, `transaction`, and `close`; `run`, `get`, and `all` take SQL text plus positional bindings, and adapters may cache prepared statements by SQL text. A transaction callback receives a handle that expires when the callback settles, all work in the transaction must use it, and adapters must queue unrelated operations and transactions until it finishes — so calling the database itself inside the callback never settles.[^pi-durable-readme]

A custom backend's `commit(writes, adopt, context)` calls `adopt(seq)` once the batch is durable, synchronously and before its next commit starts, then resolves with `seq`. A commit that fails before durability never calls `adopt`, so memory never shows a partial log. Custom storage can run the shared conformance suite with any Vitest- or Jest-compatible runner via `registerStorageConformance`; custom execution environments can use `registerEnvConformance` (see [extensions and environments](pi-durable-extensions-hooks-agents.md)).[^pi-durable-readme] The Cloudflare host example runs that suite against a Durable Object through Cloudflare's Workers Vitest integration inside `runInDurableObject`, passing the instance's `state.storage` to `openDurableObjectSqliteStorage`, which reaches the object's synchronous `SqlStorage` API through `ctx.storage.sql`.[^earendil-pi-durable-on-cloudflare]

The guide names the SQLite schema's tables as `conversations`, `entries`, `documents`, `document_revisions`, `tasks`, `submissions`, `record_ids`, `durable_metadata`, and `durable_schema`, and notes that with SQLite the harness keeps only the working set in memory while older messages stay on disk until needed — unlike JSONL, whose records are all in memory.[^tannermidd-durable]

## Cost note

The package root loads TypeBox because the tool task validates arguments with pi-ai's `validateToolArguments()`. The README states this costs about 23 MB of peak RSS unbundled, or about 4 MB in a tree-shaken bundle.[^pi-durable-readme]

## Evidence and limits

Backend behavior and performance numbers are **Reported** by the README or by the secondary Pi Pocket guide; no backend was opened or benchmarked here. The WAL/power-loss caveat, JSONL memory growth, and the browser single-owner rule are consequential limits rather than observed measurements. The deployment persistence rule comes from a practitioner tutorial and was not tested against a real container platform.

## Relationships

- **Is used by** the [Harness and durability model](pi-durable-crash-recovery.md), which depends on atomic commits and single ownership.
- **Persists** [task](pi-durable-tasks.md) state and [conversation](pi-durable-conversations.md) entries and documents.
- **Hosts** deferred progress commits that [observability](pi-durable-observability-telemetry.md) watches see earlier than storage does.
- **Shares a persistence substrate with** [code mode](pi-durable-code-mode.md) journals and [compaction](pi-durable-compaction.md) summaries.

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Storage, §Environment, §Errors, §Persist and Resume.

[^tannermidd-durable]: Pi Pocket, “Pi Durable, explained” (`raw/tannermidd-durable/index.md`), locators: §Storage backends, §SQLite, §JSONL.

[^flaviocopes-pi-durable]: Flavio Copes, “How to build agents that survive crashes with Pi Durable” (`raw/flaviocopes-pi-durable/index.md`, published 2026-10-16), locators: §Keep the storage when you deploy.

[^earendil-pi-durable-on-cloudflare]: Earendil Engineering, “Pi Durable on Cloudflare” (`raw/earendil-pi-durable-on-cloudflare/index.md`, published 2026-10-16), locators: §Persist Pi session data in Durable Object storage.
