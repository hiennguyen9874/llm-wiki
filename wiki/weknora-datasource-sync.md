---
type: Concept
title: WeKnora external datasource synchronization
description: Connector interfaces, resumable streaming checkpoints, schedules, and capability-dependent deletion reconciliation.
tags: [ml, weknora, connectors, ingestion]
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

WeKnora models external knowledge systems through connector contracts rather than embedding provider-specific fetch behavior in the generic ingestion layer. **Observed:** optional streaming and cursor-aware full-sync interfaces support resumable processing and deletion reconciliation; these capabilities must not be assumed for every registered connector.[^weknora]

## Interface boundaries

`internal/datasource/connector.go::Connector` declares type identification, validation, hierarchical resource listing, ancestor resolution, full fetch, and incremental fetch. Resource listing can populate lazy tree pickers without fetching an entire remote corpus.[^weknora]

The optional `StreamingConnector` passes one item at a time to `StreamHandler.Emit`, interleaving remote fetch and local ingest. Its `Checkpoint` contract requires a synchronously serialized **complete resumable snapshot**, not just a delta or a reference to a map that the connector will later mutate. Errors from ingestion should abort further remote work. **Synthesis:** merely implementing an incremental API does not establish restart safety; cursor completeness and checkpoint persistence matter separately.[^weknora]

## Deletions and scheduling

`FullStreamingConnector.FetchFullStream` and `FullSyncWithCursor.FetchAllFromCursor` preserve previous cursor state during full sync so removed remote items can be reconciled. A connector without the cursor-bearing full-sync interface cannot be assumed to emit deletions during full refresh.[^weknora]

The registry rejects nil connectors and empty type strings and returns an explicit unknown-connector error. Metadata declares UI priority, authentication style, and capability flags such as incremental, webhook, and deletion sync. Scheduler symbols include schedule validation, add/update, and a trigger carrying source/tenant identifiers; only a symbol-level view of scheduling was inspected.[^weknora]

**Reported support:** README lists Feishu wiki/Drive, Lark, Confluence, GitLab, Tencent IMA, Notion, Yuque, DingTalk Docs, Seafile, and RSS. Package names corroborate implementation presence, not correct provider authentication, pagination, deletions, or supported API versions.[^weknora]

## Relationships

- Feeds [document ingestion](weknora-document-ingestion.md).
- Uses [background task infrastructure](weknora-task-queues.md).
- External endpoints and credentials depend on [security controls](weknora-security.md).

## Coverage limits

Connector framework and registry metadata were inspected; scheduler inspection was symbolic. Provider implementations, OAuth/token refresh, remote attachments, markdown conversion, rate limits, conflict handling, and actual checkpoint storage remain pending. No remote connection or sync ran. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd58`: `internal/datasource/connector.go::Connector`, `StreamHandler`, `StreamingConnector`, `FullStreamingConnector`, `FullSyncWithCursor`, `ConnectorRegistry`, `ConnectorMetadataRegistry`; `internal/datasource/scheduler.go::ValidateSyncSchedule`, `Scheduler.AddOrUpdate`, `addEntryLocked`, `triggerSync` (symbol inventory). Package entry: [README](../raw/WeKnora/README.md), “Data sources and formats” and “Supported backends.”
