---
type: Concept
title: WeKnora external datasource synchronization
description: Connector interfaces, resumable streaming checkpoints, schedules, and capability-dependent deletion reconciliation.
tags: [ml, weknora, connectors, ingestion]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T16:19:21Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora models external knowledge systems through connector contracts rather than embedding provider-specific fetch behavior in the generic ingestion layer. **Observed:** optional streaming and cursor-aware full-sync interfaces support resumable processing and deletion reconciliation; these capabilities must not be assumed for every registered connector.[^weknora]

## Interface boundaries

`internal/datasource/connector.go::Connector` declares type identification, validation, hierarchical resource listing, ancestor resolution, full fetch, and incremental fetch. Resource listing can populate lazy tree pickers without fetching an entire remote corpus.[^weknora]

The optional `StreamingConnector` passes one item at a time to `StreamHandler.Emit`, interleaving remote fetch and local ingest. Its `Checkpoint` contract requires a synchronously serialized **complete resumable snapshot**, not just a delta or a reference to a map that the connector will later mutate. The interface comment describes returned `Emit` errors as aborting further remote work; the concrete handler below has a different per-item failure policy. **Synthesis:** merely implementing an incremental API does not establish restart safety; cursor completeness and checkpoint persistence matter separately.[^weknora]

## Concrete checkpoint and item-failure policy

**Observed follow-up:** `streamSyncHandler.Checkpoint` synchronously serializes the complete cursor and persists it through `dsRepo.UpdateSyncState`; sync-log progress is best-effort. `streamStartCursor` drops the cursor for an initial forced-full attempt but preserves it for retries. `streamingFetch` uses the optional full-stream interface to retain a deletion baseline.[^weknora]

`streamSyncHandler.Emit` aborts on context cancellation, but calls `applyFetchedItem` and returns nil for ordinary per-item ingest failures. That helper records counters/errors. `processSyncStreaming` can report a partial run; all-failed runs return an error. For deletions, lookup uses tenant/KB/data-source/external identity and skips already-missing rows; delete or hard-delete failures increment `DeletionFailed`. The code explicitly warns that these failures normally retry only on a later full sync.[^weknora]

**Synthesis:** persisted cursors already exist; they do not establish checkpoint-after-every-item-success or durable failed-item replay. The interface's abort-on-error commentary must not be generalized into such a guarantee. A failed-item/deletion retry ledger is a proposed hardening target, not an implemented feature verified here.

## Deletions and scheduling

`FullStreamingConnector.FetchFullStream` and `FullSyncWithCursor.FetchAllFromCursor` preserve previous cursor state during full sync so removed remote items can be reconciled. A connector without the cursor-bearing full-sync interface cannot be assumed to emit deletions during full refresh.[^weknora]

The registry rejects nil connectors and empty type strings and returns an explicit unknown-connector error. Metadata declares UI priority, authentication style, and capability flags such as incremental, webhook, and deletion sync. Scheduler symbols include schedule validation, add/update, and a trigger carrying source/tenant identifiers; only a symbol-level view of scheduling was inspected.[^weknora]

**Reported support:** README lists Feishu wiki/Drive, Lark, Confluence, GitLab, Tencent IMA, Notion, Yuque, DingTalk Docs, Seafile, and RSS. Package names corroborate implementation presence, not correct provider authentication, pagination, deletions, or supported API versions.[^weknora]

## Relationships

- Feeds [document ingestion](weknora-document-ingestion.md).
- Uses [background task infrastructure](weknora-task-queues.md).
- External endpoints and credentials depend on [security controls](weknora-security.md).
- Informs the [selective fork roadmap](weknora-fork-roadmap.md), particularly durable failed-item and deletion recovery.

## Coverage limits

Connector framework/registry and selected concrete service bodies were inspected; scheduler inspection was symbolic. Provider implementations, OAuth/token refresh, remote attachments, markdown conversion, rate limits, conflict handling, repository checkpoint implementation, leases, and crash/retry behavior remain pending. No remote connection or sync ran. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd58`: `internal/datasource/connector.go::Connector`, `StreamHandler`, `StreamingConnector`, `FullStreamingConnector`, `FullSyncWithCursor`, `ConnectorRegistry`, `ConnectorMetadataRegistry`; `internal/datasource/scheduler.go::ValidateSyncSchedule`, `Scheduler.AddOrUpdate`, `addEntryLocked`, `triggerSync` (symbol inventory); follow-up `internal/application/service/datasource_service.go::streamStartCursor`, `streamSyncHandler.Emit`, `Checkpoint`, `streamingFetch`, `processSyncStreaming`, `applyFetchedItem` (selected service bodies, not provider/repository implementation). Package entry: [README](../raw/WeKnora/README.md), “Data sources and formats” and “Supported backends.”
