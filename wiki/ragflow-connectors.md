---
type: Concept
title: "RAGFlow connectors and incremental synchronization"
description: "Connector factories, window/cursor checkpoints, fingerprint skips, scheduling leases, retries, and guarded outbound fetches."
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

# RAGFlow connectors and incremental synchronization

**Observed:** the syncer separates connector sessions, scheduling, task coordination and document jobs. The registry has exact-name factories for task contexts and raw configs, including aliases such as `google-drive`/`google_drive`. An unsupported source errors rather than silently choosing a connector; available factory names do not establish per-connector correctness.[^ragflow]

## Incremental data path

`SyncRequest` carries a poll window, optional resume checkpoint and fingerprints. `SyncRunner.Run` pins the run end, resumes progress, and advances checkpoints only after successful batch work. An invalid resume anchor triggers a bounded restart rather than a guessed cursor. Per document, processing resolves a stable ID, skips equal fingerprints, lazily fetches blob data, then upserts with the connector-to-dataset auto-parse setting. Fingerprints use xxh3; their role is change detection, not cryptographic integrity.[^ragflow]

## Coordination and retry semantics

The scheduler requires a NATS task broker, reconciles persisted tasks and schedules pruning only when deleted-file sync is enabled. A connector/dataset pair is serialized by a local plus Kvrocks-backed lock; execution deadlines are clamped by connector timeout and lock-lease safety margin. Job queues are task-bounded and dispatched fairly. Per-document and task retries use separate budgets; transient classification partly relies on error strings. A NATS acknowledgement is not proof that sync completed successfully.[^ragflow]

If a durable checkpoint store is unavailable, wiring can fall back to process-local memory. **Synthesis:** after a crash, correct reprocessing then relies on stable IDs/fingerprint behavior rather than durable cursor recovery alone. Connector implementations, deletion semantics and sink transaction behavior remain largely uninspected.[^ragflow]

## Egress boundary

Connector HTTP requests validate each redirect hop, pin validated DNS addresses, disable environment proxies, require HTTPS and strip sensitive headers across origins. Body-bearing 307/308 redirects are refused. Private-host configuration escape hatches exist for internal data sources; their deployment settings matter. **Synthesis:** these controls reduce common SSRF/credential-forwarding risks but are not a substitute for egress network policy or a complete per-connector audit.[^ragflow]

## Relationships

- **Produces inputs for:** [document ingestion](ragflow-ingestion.md).
- **Depends on:** [NATS/Kvrocks and metadata persistence](ragflow-persistence.md).
- **Constrained by:** [credential-use and deployment boundaries](ragflow-security.md).

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa024356711dc86de2e231afb0e4bf1`; locators: `internal/syncer/connector/registry.go::Registry / Open`; `internal/syncer/connector/builtin.go::RegisterBuiltIns / newS3SourceConnector`; `internal/syncer/connector/models.go::SyncRequest / SyncCheckpointState`; `internal/syncer/sync_runner.go::Run / processDocument / collectResults / resetCheckpointForRestart`; `internal/syncer/connector/fingerprint.go::contentFingerprint / stableFingerprint`; `internal/syncer/scheduler.go::Run / taskDelay`; `internal/syncer/connector_lock.go::ConnectorLocker.TryLock`; `internal/syncer/task_coordinator.go::taskExecutionDeadline`; `internal/syncer/job_executor.go::RegisterTask / dispatch / popReadyJob`; `internal/syncer/transient_error.go::isTransientSyncError`; `internal/syncer/syncer.go::checkpoint store wiring`; `internal/syncer/README.md::acknowledgement semantics`; `internal/syncer/connector/ssrf.go::connectorRequest / assertConnectorURLSafe / newConnectorPinnedTransport`.
