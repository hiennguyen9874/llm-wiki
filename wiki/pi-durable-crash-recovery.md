---
type: Concept
title: Pi Durable Crash Recovery and Durability
description: How pi-durable commits before display, resumes interrupted work, bounds the loss from a crash, makes submissions idempotent, parks crash-looping tasks, and classifies fatal errors.
tags: [pi-durable, durability, crash-recovery, errors]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:07:19Z }
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
---

Pi Durable's durability contract is commit-before-display: a state change is stored before any UI sees it, and work interrupted by a crash or a close stays pending until a later process resumes it. Calling `resume()` starts the task scheduler (submitting or waiting also starts it), so a reopened SQLite or JSONL session continues the runs the previous process left unfinished. The general model behind this is [the effect sandwich](pi-durable-effect-sandwich.md): store the intent, run the effect, store the result.[^pi-durable-readme]

## What a crash can lose

Progress is deliberately coarser than the committed transcript. Partial answers and tool output are committed at most every 100 ms by default and watches see each commit at once, but storage receives them as deferred commits: with the next commit that reads `pi.live`, or at the latest after `settings.progress.persistWithinMs` (default 1,000 ms). A crash therefore loses at most about that window of an answer or tool output; a stream that crashes in its first second may leave no aborted entry, and that attempt's usage is not recorded.[^pi-durable-readme]

An interrupted model request can be sent again, and a stored partial answer is marked aborted rather than completed, so a retry can mean a second API charge.[^flaviocopes-pi-durable]

Deferred persistence is narrow: only a commit that changes nothing but existing documents with `history: "latest"` and `fork: "initial"` can be deferred. Anything else in the commit — an entry, a new document, or a task state — stores at once. Storage receives a deferred value with the next commit that reads or writes the document, before the document leaves memory, at close, and no later than the requested `withinMs`; `subscribeCommits()` then sees exactly what was stored. A host must not derive durable state from a deferred value outside a commit that reads it.[^pi-durable-readme]

## Idempotent submission and session identity

A retried submission with the same `requestId` returns the existing submission instead of admitting a second one, and `harness.submission(id)` reacquires one by ID, which lets a host wait for it after a restart. Retrying a request that already completed returns the same submission ID and saved answer without rerunning its tools.[^flaviocopes-pi-durable] Each conversation also keeps a persisted UUIDv7 provider session identity in `pi.provider`, forwarded to pi-ai as `sessionId` for prompt caching and session affinity; it survives reopen, retries, reset, compaction, and model changes, while a child or fork receives a fresh identity.[^pi-durable-readme]

## Read-only viewers

A process that only displays a session another process drives opens it with `readOnly: true`. Open recovers nothing, and every write, `resume()`, and every call that would run tasks rejects with `ReadOnlySession`. This is the supported way to avoid two writers on one storage.[^pi-durable-readme]

## Crash loops and parked tasks

Open counts each task that a crash, eviction, or reset cut off; a close is not counted, and a new state the task commits starts the count over. When the count reaches `settings.restartLimit` (default 5; `Infinity` never parks), the task is parked: `inspect()` and the task graph show it as blocked with reason `restart_limit`, `wake()` no longer counts it as active, and `onReport` reports `task_parked` once. Hosts should surface parked tasks and offer `harness.retryTask(id)`, which runs one again. `abortTask()` still runs the abort handler; an abort handler cut off that many times ends the task `faulted`.[^pi-durable-readme]

Tasks blocked on a missing or unmigratable definition appear in the task graph with their reason, and a registry change that unblocks them makes `onWake` report the session active, so a host need not poll.[^pi-durable-readme]

## Failure rules

Three rules decide what an error does:[^pi-durable-readme]

1. **A storage error ends the Harness.** The call rejects with the error; later calls and pending waits reject with `SessionFailed` (whose `cause` is the error); watches and event streams end `failed`; running tasks get their abort signal; `onReport` gets the error once. The Harness closes itself and nothing is retried, because a custom storage retries its own transient failures. Reopening recovers, and resubmitting the same `requestId` finds the already-admitted submission.
2. **An invalid read fails only that call.** A bad cursor, unknown conversation, or unavailable history throws `StorageRequestError`, and a cancelled read fails only itself. The exemption covers reads only: any error from `commit()` or `mintId()`, `StorageRequestError` included, ends the Harness as in rule 1.
3. **Host code fails only its own unit.** A throwing task phase faults that task, a throwing tool yields an error result, a throwing hook is reported and skipped (`beforeTool` blocks the call), a throwing commit callback rolls back that commit, and a throwing listener is reported while other listeners still run. The exception is a host `RegistryReader` whose `snapshot()` throws: the Harness cannot schedule without it, so it fails the Harness like a storage error.

`harness.closed` settles after `close()` or after a storage failure, exposing `end.reason` (`failed`) and `end.error`, which lets a host reopen on failure. Closing waits for running task code to return, so code that ignores its abort signal delays the close.[^pi-durable-readme]

## Queued inputs after a failed run

A run that fails with a model error leaves inputs queued behind it waiting until the next input arrives. `settings.afterFailedRun` changes this: `continue` starts the next run with them as after an answer, and `withdraw` settles them `unanswered` with reason `run_failed`.[^pi-durable-readme]

## Contradictions

The guide's simulator says that killing the process while a chunk is in flight loses only that chunk, "approximately 100 ms of output" and longer for large tool output, while killing after a flush leaves the committed part as an aborted answer. The README's deferred persistence allows the newest watched output to stay un-stored for up to `settings.progress.persistWithinMs` (default 1,000 ms). Both claims are recorded: the guide may model a committed chunk rather than the storage flush, and it carries no publication or revision date, so the two cannot be ordered.[^pi-durable-readme][^tannermidd-durable]

## Evidence and limits

All behavior here is **Reported** from the README; the Pi Pocket guide adds a simulated account of chunk loss but is neither independent nor dated. The Flavio Copes tutorial reports its own subprocess-kill test with SQLite and a scripted provider — killing a process inside the real tool, reopening the database, and checking the submission ID — which supports the replay account without depending on a live model; it is the author's report, not an independent reproduction here. No crash, storage failure, or restart was reproduced in this repository. Concrete loss windows depend on storage and on `settings.progress`, and the README gives no cross-process locking beyond "one process owns a storage at a time" (see [Storage backends](pi-durable-storage.md)).

## Relationships

- **Uses** a single-writer [storage backend](pi-durable-storage.md) and atomic commits.
- **Recovers** [tasks](pi-durable-tasks.md) from their last checkpoint.
- **Protects** [conversation submissions](pi-durable-conversations.md) through `requestId` and the persisted provider session identity.
- **Bounds** streamed progress that [observability](pi-durable-observability-telemetry.md) surfaces through watches and telemetry.
- **Stops at the storage boundary**, leaving external side effects to [replay safety](pi-durable-replay-safety.md).
- **Implements** [the effect sandwich](pi-durable-effect-sandwich.md) for each recoverable step.
- **Contradicts neither** the code-mode restart design nor compaction: both rely on committed state and are described in [code mode](pi-durable-code-mode.md) and [compaction](pi-durable-compaction.md).

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Persist and Resume, §Failures and Recovery, §Watching a Conversation, §Your Own State, §Errors, §Storage.

[^tannermidd-durable]: Pi Pocket, “Pi Durable, explained” (`raw/tannermidd-durable/index.md`), locators: §Stop the process during an answer.

[^flaviocopes-pi-durable]: Flavio Copes, “How to build agents that survive crashes with Pi Durable” (`raw/flaviocopes-pi-durable/index.md`, published 2026-10-16), locators: §Kill it halfway through, §Retry a request without creating a second job.
