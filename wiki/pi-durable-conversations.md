---
type: Concept
title: Pi Durable Conversations and Submissions
description: How pi-durable admits inputs and writes, queues work while busy, resets context, forks branches, owns conversations from tasks, and aborts cleanly.
tags: [pi-durable, conversations, submissions, subagents]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:12:06Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-readme
    resource: ../raw/pi-durable-readme.md
    kind: docs
    title: "@earendil-works/pi-durable README"
  - id: earendil-pi-durable-on-cloudflare
    resource: ../raw/earendil-pi-durable-on-cloudflare/index.md
    scope: ../raw/earendil-pi-durable-on-cloudflare/
    kind: article
    title: "Pi Durable on Cloudflare"
---

A conversation is a transcript of immutable entries plus documents. Hosts hand it a **submission** — user input or an entry to write — and can wait for it: `done` when the input is answered, or `unanswered` with a reason (such as model error, reset, run failure, or `stale` compaction). A retried submission with the same `requestId` returns the existing one, and `harness.submission(id)` reacquires it after a restart.[^pi-durable-readme]

## Busy conversations and the inbox

A conversation is busy while a run works on an input. Submitting while busy queues the submission in `pi.inbox`, and `whenBusy` chooses how it is placed:[^pi-durable-readme]

| `whenBusy` | Placement |
| --- | --- |
| `follow-up` (default) | Placed when the run answers, starting the next run. |
| `steer` | Placed after the current tool round and joins the running work. |
| `reject` | Throws `ConversationBusy`. |
| write (no `whenBusy`) | Appends an entry without asking the model anything. |

A write of only `kind` and `data` changes nothing the model sees, so it is appended at once even mid-run and is never queued — a chat message appears as soon as it is sent — and can therefore appear before earlier queued items, except behind a queued reset where it waits so the reset does not hide it. A write with `model`, `head`, or `edits` waits for the next boundary like a steer. `submission.abort(context)` withdraws a queued submission, and `settings.steeringMode: "all"` / `followUpMode: "all"` place every queued item at once instead of one per turn. If a run fails, queued items stay in the inbox until the next input or queued write places them, oldest first.[^pi-durable-readme]

An input can be shown as a host-defined entry while still seen by the model as the user message: pass `entry: { kind, data }` to `submit()`. Its kind must not start with `pi.`. It behaves like any other input — starts a run, steers, follows up, or rejects — and while queued its inbox item carries the entry.[^pi-durable-readme]

## Reset and handoff

`reset()` starts a new context: the model no longer sees older entries, but they stay in storage. Passing a string writes it as a handoff note (`reset("We were fixing the flaky login test. Continue.")`). While busy the reset is queued like a write; if placed during a tool round, the current run ends, its inputs settle `unanswered` with reason `reset`, and queued inputs run in the new context.[^pi-durable-readme]

A tool can return `control: { handoff: "..." }` to write the same reset text, but the run continues: the next model request starts in the new context and the submission settles with that eventual answer. Queued writes and steers land after the handoff text, follow-ups wait for the run's end, and a queued `reset()` still ends the run. When every call of the round also returns `terminate: true`, the run ends after the handoff.[^pi-durable-readme]

## Forks and new conversations

`harness.createConversation()` creates an ownerless conversation, and `root.fork(entryId)` creates one that sees its parent's entries up to `entryId` and continues independently. A fork keeps the parent's agent as of that entry but receives a fresh provider session identity. Both take `agent` and `init`, applied in the creating commit; `init` writes per-call data in the same commit, and `HarnessOptions.conversationCreated(tx, conversation)` runs in every commit that creates or forks a conversation, including a tool's raw `tx.createConversation()`.[^pi-durable-readme]

Creating a conversation is not idempotent on its own. A host that must survive a dropped connection can store a receipt keyed by the client's request ID in the same commit that creates the conversation and return the saved conversation ID when that ID arrives again, as the Cloudflare multiplayer sample does for both creation and forks; the fork helper is `tx.forkConversation(parentConversationId, entryId, …)`.[^earendil-pi-durable-on-cloudflare]

## Ownership, subagents, and abort

A conversation can be owned by a task. A subagent tool creates its child inside `api.commit()` with `ownership: { kind: "task", taskId: api.taskId }` and drives it through `api.conversation(id)`. Owned work belongs to its owner: aborting the call aborts the child (as does the call failing, throwing, or crashing when it is not replay-safe), and the parent is idle only once the child is. A task created with `{ background: true }` is a boundary: work it owns survives the parent's abort and does not keep the parent busy, and `root.abort(context, { background: true })` aborts it too. The README's example subagent is replay-safe and reuses an existing child on rerun, with request IDs preventing duplicate messages or reports.[^pi-durable-readme]

`await root.abort(context)` stops a conversation: queued inputs are withdrawn (queued writes stay), every task of its current work is aborted, and the call resolves once the conversation is idle. Compaction is requested separately; see [compaction](pi-durable-compaction.md).[^pi-durable-readme]

## Evidence and limits

Submission, queue, reset, fork, and ownership behavior is **Reported** from the README; no conversation was driven. The README's background-subagent pattern is presented as example code (`22-subagent-background.ts`), which is not present in `raw/`, so its exact implementation is a coverage limit.

## Relationships

- **Runs** [tasks](pi-durable-tasks.md) and consumes [tool](pi-durable-tools-nested-calls.md) results.
- **Stores** entries and documents through [storage](pi-durable-storage.md), with durability rules in [crash recovery](pi-durable-crash-recovery.md).
- **Uses** the [agent and extension](pi-durable-extensions-hooks-agents.md) resolution and triggers [compaction](pi-durable-compaction.md).
- **Is observed** through [watches and events](pi-durable-observability-telemetry.md).

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Concepts, §Busy Conversations, §Reset and Handoff, §More Conversations and Forks, §Abort and Subagents, §Your Own State.

[^earendil-pi-durable-on-cloudflare]: Earendil Engineering, “Pi Durable on Cloudflare” (`raw/earendil-pi-durable-on-cloudflare/index.md`, published 2026-10-16), locators: §Run multiple conversations in one shared session.
