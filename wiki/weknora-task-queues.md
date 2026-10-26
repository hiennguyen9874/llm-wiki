---
type: Concept
title: WeKnora asynchronous task queues
description: Isolated Asynq worker pools, retry/dead-letter handling, model concurrency, and the Redis-free Lite executor.
tags: [ml, weknora, queues]
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

WeKnora separates background work into stage-specific Asynq worker pools rather than giving all tasks one concurrency budget. **Observed:** standard mode uses Redis-backed queues, while Redis-free mode runs task handlers through a goroutine-based executor. Durable pending-operation rows supplement queue triggers for wiki compilation; the fallback executor itself is not a durable Redis queue.[^weknora]

## Pool topology

**Observed defaults** in `internal/types/task.go` and constructors in `internal/router/task.go`:[^weknora]

| Pool | Default workers | Purpose |
| --- | ---: | --- |
| core | 8 | Primary ingestion |
| postprocess | 2 | Postprocessing |
| enrichment | 12 | Summary, image, graph, question and related enrichment queues |
| maintenance | 4 | Maintenance work; physical legacy queue name `low` retained |
| shared | 6 | Elastic capacity for core/enrichment queues, not postprocess or maintenance |
| wiki | 8 | Wiki processing isolated from upstream work |

Physical queue definitions also include `default`, `chat_attachment`, `postprocess`, `summary`, `multimodal`, `graph`, `question`, `sync`, `wiki`, and `memory`. All pools use the task handler mux; pool-specific queue subscriptions determine what each server can claim. Runtime settings/environment overrides resolve pool capacities.[^weknora]

## Failure, recovery, and concurrency

**Observed:** the handler mux installs dead-letter middleware and background-context tagging. Terminal failures can persist a dead letter and mark an affected document failed, but only for designated task types. Most retries use Asynq backoff; a wiki-concurrency sentinel has a fixed 15-second retry. Retries mean this inspection does **not** establish exactly-once processing or universal task idempotence.[^weknora]

Background model calls have a separate per-model governor (default cap 32, disabled by non-positive configured caps), backed by Redis or a local limiter. It intentionally distinguishes background ingestion from interactive chat. An additional Ants goroutine pool defaults to five; none of these caps should be mistaken for total application request concurrency.[^weknora]

Without Redis, `SyncTaskExecutor` emulates task delay/retry/timeout options in goroutines and includes reflection/unsafe access to Asynq options. On Lite restart, interrupted processing documents are reset to failed; distributed mode avoids that blanket reset. Pending wiki operation triggers are recovered after handlers are registered.[^weknora]

## Relationships

- Started by [backend composition](weknora-backend-architecture.md).
- Updates [document lifecycle state](weknora-persistence.md).
- Supports the durable two-lane [wiki compilation workflow](weknora-wiki-compilation.md).

## Coverage limits

Static selected sections and queue-test names only; no worker, crash-recovery, retry, fairness, or load test ran. Housekeeping and every task handler's idempotence remain unreviewed. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd5855fc4ded5c981a92dcb82a455246`: `internal/types/task.go::queueDefinitions`, `QueueWeightsForSharedPool`, `ResolveWorkerPoolConcurrency`, worker default constants; `internal/router/task.go::RunAsynqServer`, `asynqRetryDelayFunc`, `taskTypesAffectingKnowledgeStatus`, `newDeadLetterKnowledgeFailer`, server constructors; `internal/router/sync_task.go::SyncTaskExecutor`; `internal/container/container.go::BuildContainer`, `initAntsPool`, model-governor initialization; `internal/container/reset_pending_tasks.go::resetPendingTasks`. Package entry: [README](../raw/WeKnora/README.md), “Permissions and operations” and v0.7.0 notes.
