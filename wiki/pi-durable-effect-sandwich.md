---
type: Concept
title: "The Effect Sandwich: Durable Intent, Execution, and Result"
description: How pi-durable makes each step resumable by storing its intent, executing the effect, and persisting the result, and why external effects still need idempotency keys.
tags: [pi-durable, durability, idempotency, effects, tasks]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T17:05:00Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-talk
    resource: "../raw/Pi Durable: Agents That Survive Crashes.md"
    kind: video-transcript
    title: "Pi Durable: Agents That Survive Crashes — Mario Zechner & Armin Ronacher (YouTube)"
  - id: yaogangqiang-status
    resource: ../raw/yaogangqiang-status/index.md
    scope: ../raw/yaogangqiang-status/
    kind: social-post
    title: "Post by @yaogangqiang on X: Pi as a durable runtime, and its state model"
---

Pi Durable's design reduces durability to one recurring shape that its authors call the **effect sandwich**: store what you are about to do, do it, then store what came back. A crash can land before execution, during it, or after it, and the stored intent plus the stored result let a new process tell which of those happened. The harness applies this shape to every step — preparing a model request, calling the model, and running a tool call are all sandwiches — and composes steps by running each as a [task](pi-durable-tasks.md) that can own and wait for child tasks.[^pi-durable-talk]

## What the authors mean by durability

The talk's working definition is stated in one breath: an agent starts in a process, calls tools, and the process dies; durability means restarting the process and having the agent continue exactly where it left off — "without you having to type continue", without losing tool results or assistant streams, with application state also persisted and reliably resumed.[^pi-durable-talk]

Two motivations are given. Long-running agents need it at all, and so does a history that outgrows memory: Pi historically loaded the entire conversation tree into memory, which the talk says cannot work for a Slack bot that lives in its workspace for years with a huge trace. What must survive is not necessarily what is sent to the model, but the full history still has to be reachable and resumable.[^pi-durable-talk]

## Three crash windows

The talk's framing of the general problem, before describing Pi's own answer:[^pi-durable-talk]

| Window | What is uncertain after a restart | What the sandwich provides |
| --- | --- | --- |
| Before the effect runs | Whether the inputs were validated and the step was authorized | A stored intent with the exact inputs, so the step can simply run now |
| While the effect runs | Whether the external action happened at all | Nothing by itself; the effect needs an idempotent identifier or a reconciliation step |
| After the effect runs | Nothing, if the result was stored | A stored result, after which the step is finished and its intermediate state can be discarded |

"Effect" is the talk's term for the thing being executed. Storing intent before execution is, in its words, "the first part of the sandwich"; storing the result closes it, and the sandwich of intent, execution, and result is then done.[^pi-durable-talk]

## Closing the middle gap with an idempotency key

The hard window is the middle one. If the effect is an external system call and the process dies before the result arrives, the local database cannot say whether the call happened. The talk's worked example is a GitHub Actions run: mint the run key first, save it, then ask the external system to execute "with this ID". A retry that finds the run already in progress waits for it; one that finds nothing starts it. That is what the talk calls idempotency — the name Armin Ronacher reacts to with mock horror.[^pi-durable-talk]

Not every effect fits. Deleting a file cannot be undone without something like Git, and charging a credit card must not happen twice, so the talk concludes that the effects an agent runs have to be *combinable* with the durability system; most external systems are, and for the rest the host has to decide how to handle the mismatch. The per-operation consequences for tools are compiled in [replay safety and external effects](pi-durable-replay-safety.md).[^pi-durable-talk]

## Every harness step is a task

The harness applies the shape uniformly: "basically everything that happens in the harness is a task that is just this effect sandwich". A model call stores the prepared request — gathered context window, parameters, thinking level, model — then calls the model as the effect, then persists the answer. A tool call gets the same treatment as a task that executes one tool call. Tasks compose because one task can spawn another and wait for it to stop, which the talk calls "the whole magic" and describes as the entirety of the mechanism beyond the basic primitive.[^pi-durable-talk]

## What it deliberately is not

The interviewer guessed the design was event sourcing, with actions committed to a file in a queue; the answer was that this is exactly what Pi Durable does *not* do: "We don't do event sourcing. That is what everybody else is doing." The talk says it avoids that approach because it has "a lot of problems" but does not enumerate them in the captured transcript, so the comparison is recorded as an authorial position rather than an argued trade-off.[^pi-durable-talk] The durable state that takes its place is a transcript plus position-versioned [documents](pi-durable-documents.md), and the recovery behavior built on them is in [crash recovery](pi-durable-crash-recovery.md).

A third-party post makes that denial more precise without contradicting it: it reports that an earlier Harness v2 did use an event-sourcing-style journal-and-reduce, and that the current specification instead writes a complete `OperationState` snapshot at each state transition, which is authoritative recovery state rather than a replay cache — the history and trade-off are compiled in [the state model](pi-durable-state-model-snapshots.md).[^yaogangqiang-status] The talk carries no publication date, so the two accounts cannot be ordered.

## Evidence and limits

**Reported** throughout: the source is an English-language, machine-generated transcript of a YouTube conversation between Pi's authors and a host, read in full (155 lines). It carries only a title, the video URL, and the transcript text — no publication date, headings, timestamps, speaker roles, or license — so locators are quoted phrases. The talk is the designers' own account, which makes it authoritative about intent and weak as independent verification; no code was inspected and no crash, effect, or retry was run here.

Material limits:

- The sandwich is described conversationally and simplified. The actual per-phase checkpoints, replay policies, and failure rules live in [tasks](pi-durable-tasks.md), [crash recovery](pi-durable-crash-recovery.md), and [tools](pi-durable-tools-nested-calls.md); this page records the model, not the implementation.
- The claim that external effects must be "combinable" with durability is a requirement statement without an inventory of which systems qualify; the GitHub Actions run-key example is the only concrete one.
- "A lot of problems" with event sourcing is the only stated reason for avoiding it; no specific failure is named.
- The captured text is an automatic transcript and repeats words, drops words, and misattributes a few interjections; quoted phrases are reproduced as they appear, and no claim here depends on a garbled passage.

Coverage exclusions: the transcript is one self-contained file with no attachments or includes. Much of the conversation — model capability, coding-agent maintenance, harness comparisons, product roadmap, multi-user sessions — is commentary rather than durable knowledge about durability and is not compiled; the design details that are compiled live in the pages linked above.

## Relationships

- **Is applied by** every [task](pi-durable-tasks.md), including `pi.generation` and `pi.tool` work.
- **Is the general model behind** [crash recovery and durability](pi-durable-crash-recovery.md).
- **Leaves external actions to** [replay safety and external effects](pi-durable-replay-safety.md), which decides when a repeat is acceptable.
- **Persists application state as** position-versioned [documents](pi-durable-documents.md), the other half of the primitive.
- **Is contrasted with** event sourcing, which the authors say they deliberately avoided; a third party reports that the earlier Harness v2 did journal events, as recorded in [the state model](pi-durable-state-model-snapshots.md).

[^yaogangqiang-status]: @yaogangqiang, “Post by @yaogangqiang on X” (`raw/yaogangqiang-status/index.md`, published 2026-08-11), locators: ¶4 “Harness v2 采用类似 Event Sourcing 的 journal-and-reduce”; ¶5 “写入完整、以 ID 为主的 OperationState，再用 slot 指向最新版”.

[^pi-durable-talk]: Mario Zechner and Armin Ronacher, “Pi Durable: Agents That Survive Crashes” (`raw/Pi Durable: Agents That Survive Crashes.md`; <https://www.youtube.com/watch?v=ja_7AF54OtE>), locators by quoted phrase because the captured transcript has no headings or timestamps: durability “agent starts up in a process, agent calls tools, process dies”, “continues exactly from where it left off”, “without you having to type continue”, “application state being also persisted durably”, “loaded the entire conversation”, “a Slack bot that lives in your Slack for years and years”; crash windows “before you start executing it, while you are executing it, or after you've executed it”, “commonly referred to as an effect”, “I store something in some storage that says I'm about to execute this thing”, “that's the first part of the sandwich”; idempotency “like you send to GitHub Actions”, “you get a key. and then you can save that before you actually execute that run”, “execute with this ID”, “it's already running”, “that is what's called idempotency”, “I store that result and then my effect sandwich”, “I can throw away all the information that happened”, “if I delete the file on disk as the effect”, “If I charge your credit card, I don't want to charge it twice”, “combinable with this durability system”; tasks “everything that happens in the harness is is a task that is just this effect sandwich”, “prepare the request, gather the context window and the parameters, thinking level, model”, “One task can spawn another task and wait for it to stop. And that's the whole magic.”; event sourcing “We don't do event sourcing.”, “That is what everybody else is doing”, “there is a lot of problems”.
