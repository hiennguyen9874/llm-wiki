---
type: Concept
title: Pi Durable Tasks and Lifecycle
description: Tasks are durable state machines that checkpoint each phase, can sleep across restarts, wait on owned children, be abandoned on restart, and appear in a live task graph.
tags: [pi-durable, tasks, state-machines, scheduling]
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
  - id: earendil-pi-durable-on-cloudflare
    resource: ../raw/earendil-pi-durable-on-cloudflare/index.md
    scope: ../raw/earendil-pi-durable-on-cloudflare/
    kind: article
    title: "Pi Durable on Cloudflare"
  - id: pi-durable-talk
    resource: "../raw/Pi Durable: Agents That Survive Crashes.md"
    kind: video-transcript
    title: "Pi Durable: Agents That Survive Crashes — Mario Zechner & Armin Ronacher (YouTube)"
---

A task is a durable state machine defined with `defineTask` (name, version, initial state, named phases, optional abort handler). Each phase runs, commits a new state as its checkpoint, and ends; after a crash the task resumes from the last checkpoint rather than from the top of an unfinished phase. Every task has an owner — its conversation, or another task — and built-in `pi.generation` and `pi.tool` tasks implement model turns and tool calls on this machinery.[^pi-durable-readme]

The authors describe the model in one sentence: "basically everything that happens in the harness is a task that is just this effect sandwich" — store the intent, run the effect, store the result. Preparing and issuing a model request and executing a single tool call are both such tasks. Composition comes from a task spawning another and waiting for it, which the talk calls "the whole magic" beyond the primitive itself (see [the effect sandwich](pi-durable-effect-sandwich.md)).[^pi-durable-talk]

## Phases and checkpoints

A phase reruns from its top after a restart, so a phase must be resumable from its input and committed checkpoint. Work that depends on a wait belongs in the phase after it, and anything that phase needs must be in the checkpoint.[^pi-durable-readme]

## Sleeping, clocks, and host wake

A task waits for time by ending its phase asleep: `runtime.sleepUntil(until, checkpoint, context)` resolves once the sleep is stored, and the task then holds no invocation while it survives restarts. It resumes at the checkpoint when the Harness clock reaches `until`. The same sleep can be returned from `runtime.commit()` as `{ status: "sleeping", until, checkpoint }` and committed together with other writes. Retry backoffs and deferred-response polls of built-in tasks use this mechanism.[^pi-durable-readme]

Scheduler and task timers go through `setTimer` (default `setTimeout`) and their times through `now` (default `Date.now`), which allows a fake clock in tests. Sleep deadlines are stored in terms of `now`, so every process that opens one storage must use the same clock. The Node.js environment, file watcher, and image worker keep their own timers.[^pi-durable-readme]

A host whose process can be evicted, such as a Cloudflare Durable Object, passes `onWake`. The Harness then arms no timer for sleeps; it reports `harness.wake()` whenever it changes: `active` while some task can run or is running, and `at`, the earliest sleep. The host keeps its alarm armed and calls `resume()` when it fires. It should arm before any call that can start work (submit, compact, abort, a registry change) because `onWake` runs after the commit: an early alarm is harmless, a missing one strands the work. On Cloudflare, the README also arms a fallback alarm and treats a failed alarm write as a reason to reset the object. The default `setTimer` declines timers that only free memory in Workers, so no pending timer prevents hibernation or eviction.[^pi-durable-readme]

The Cloudflare host example makes the many-to-one mapping concrete. Pi can hold any number of sleep deadlines but a Durable Object has one alarm, so the host projects the earliest future deadline onto it, gives every non-blocked task that is ready or running a short recovery alarm instead, and recalculates the whole schedule from stored tasks on each wake because alarms execute at least once. It persists that recovery alarm before `waitForTask()` starts the scheduler, and relies on a stable request ID so a repeated alarm cannot submit a scheduled instruction twice (see [Pi Durable on Cloudflare](pi-durable-on-cloudflare.md)).[^earendil-pi-durable-on-cloudflare]

## Child tasks and ownership

A task can create children with `ownership: { kind: "task", taskId }` and wait for them by committing a `waiting` state with `on` (the tasks to await) and `policy`: `allSettled` resumes once every listed task is done, while `failFast` aborts the others on the first failure. `on` may also name tasks the waiter does not own when using `allSettled`.[^pi-durable-readme]

A task whose outcome is decided while work it owns is still running is `completing`: it becomes terminal, and `waitForTask()` returns, only after that work finishes. A failed or aborted outcome aborts the owned work first. Aborting runs bottom-up: a task's owned work is aborted before its own abort handler starts, so each task undoes its own effects.[^pi-durable-readme]

A task created with `{ background: true }` is a boundary: work it owns survives its parent's abort and does not keep the parent busy. `abort(context, { background: true })` aborts it too. This is how persistent background subagents outlive a foreground call. The guide spells that pattern out as an anchor task owning each child conversation plus a reporter task that sends each answer to the parent as a follow-up.[^pi-durable-readme][^tannermidd-durable]

## Work a restart abandons

A task that its creator awaits only in memory, and that the creator never resumes after a restart, can be created with `abandonOnRestart: true`. When a later Harness starts scheduling and finds it live, it is aborted with `abortReason: "restart"`, together with everything it owns, before any of it runs again. Nested calls of tools that are not replay-safe get this automatically, and so do child tasks such a tool creates with `api.createTask()`. If the abandoned task's definition is missing, it waits until its extension is installed so its abort handler can still clean up; its caller and conversation wait with it, and `harness.inspect()` shows it blocked. Aborting it then orphans it, as any abort does.[^pi-durable-readme]

## Task graph and inspection

`harness.watchTaskGraph(context)` watches every live task as one value for a task panel or debugging. A node carries its owner edge (owner task, or none for a conversation-owned task), status, background/abort markers, and the conversations it owns. Statuses are the committed ones: `pending`, `running`, `waiting` (with `on` and `policy`), and `completing` (with the held outcome's status). A task appears with the commit that creates it and leaves with the commit that makes it terminal; after a restart, tasks that were `running` show as `pending` until they run again. Whether a pending task is blocked by a missing definition is not part of the graph — `harness.inspect()` reports it. The guide defines `faulted` as a task that broke the task rules, for example with an error it did not catch, and adds that a task no installed code can run goes directly from pending or waiting to terminal `orphaned` when the harness aborts it.[^tannermidd-durable] Once a subagent's owner task is terminal, a later task in its conversation is a top-level node, and `ConversationRecord.owner` links it to its parent.[^pi-durable-readme]

## Evidence and limits

The task model is **Reported** documentation, not reproduced; no scheduler, sleep, or restart was run. The secondary Pi Pocket guide repeats the model and adds the background-subagent roles and the `faulted`/`orphaned` outcome wording, but it is not an independent test. The authors' talk adds the design framing — every step is an effect sandwich, and spawning plus waiting is the whole composition mechanism — but describes it verbally, with no date or timestamps, and nothing was inspected or run through it. The README does not specify a persistence guarantee per backend beyond each storage's own (see [storage](pi-durable-storage.md)), and it warns that crash-loop counting treats every task running at process death as cut off.

## Relationships

- **Owns** model and tool work: [tools](pi-durable-tools-nested-calls.md) run each call as its own task, and [code mode](pi-durable-code-mode.md) scripts run as nested calls.
- **Is observed by** the [task graph and telemetry](pi-durable-observability-telemetry.md).
- **Provides the recovery unit for** [crash recovery](pi-durable-crash-recovery.md) and the reset/handoff behavior of [conversations](pi-durable-conversations.md).
- **Supports** compaction tasks described in [compaction](pi-durable-compaction.md).
- **Instantiates** [the effect sandwich](pi-durable-effect-sandwich.md) once per step.

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Concepts, §Sleeping and Waking Up, §Child Tasks, §Tasks a restart abandons, §Task Graph, §Failures and Recovery.

[^tannermidd-durable]: Pi Pocket, “Pi Durable, explained” (`raw/tannermidd-durable/index.md`), locators: §Task ownership and abort order.

[^earendil-pi-durable-on-cloudflare]: Earendil Engineering, “Pi Durable on Cloudflare” (`raw/earendil-pi-durable-on-cloudflare/index.md`, published 2026-10-16), locators: §Map Pi deadlines to the Durable Object alarm.

[^pi-durable-talk]: Mario Zechner and Armin Ronacher, “Pi Durable: Agents That Survive Crashes” (`raw/Pi Durable: Agents That Survive Crashes.md`; <https://www.youtube.com/watch?v=ja_7AF54OtE>), locators by quoted phrase because the transcript has no headings or timestamps: “everything that happens in the harness is is a task that is just this effect sandwich”, “One task can spawn another task and wait for it to stop. And that's the whole magic.”
