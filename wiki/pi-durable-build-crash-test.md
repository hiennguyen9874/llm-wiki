---
type: Concept
title: Pi Durable Build and Crash-Test Recipe
description: A worked recipe for a minimal SQLite-backed Pi Durable agent, the kill-and-restart test that shows replay, the duplicate-request check, and the deployment checklist.
tags: [pi-durable, tutorial, crash-recovery, sqlite, deployment]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:09:52Z }
stale_after: 2027-01-25
sources:
  - id: flaviocopes-pi-durable
    resource: ../raw/flaviocopes-pi-durable/index.md
    scope: ../raw/flaviocopes-pi-durable/
    kind: article
    title: "How to build agents that survive crashes with Pi Durable"
---

A practitioner walkthrough builds the smallest durable agent — one read-only tool, SQLite storage, one CLI request — and then kills the process mid-tool to watch it recover. Its durable content is the call order and the two checks that separate recovery from duplicate work: after a crash the same `requestId` resumes one submission, and after completion the same `requestId` returns the stored answer without running the tool again.[^flaviocopes-pi-durable]

## Project and packages

The tutorial targets a current Node.js LTS release with the built-in `node:sqlite` module, an OpenAI API key, and three runtime packages (`@earendil-works/pi-durable`, `@earendil-works/pi-ai`, `@earendil-works/chord`) plus three development packages (`tsx`, `typescript`, `@types/node`). It installs with `--ignore-scripts` and keeps `node_modules/`, `.env`, and `agent.sqlite*` out of Git; running the demo creates the database and possibly SQLite journal files.[^flaviocopes-pi-durable]

A container's temporary filesystem can disappear when the container is replaced, so `agent.sqlite` is only useful across a deployment when it sits on persistent storage at the same path (see [storage](pi-durable-storage.md) for the backend's own guarantees).[^flaviocopes-pi-durable]

## Tool and harness shape

The example tool answers with a small fixture and deliberately waits ten seconds so the process can be killed while it runs. Four details carry the lesson: the TypeBox `parameters` schema validates the service argument before execution; `api.output()` publishes progress to the model; `context.abortSignal` lets the delay stop when the call is cancelled; and `replay: 'safe'` declares that reading the fixture may run again after an interruption. The tool is packaged in a named `defineExtension`, which must be installed again every time the agent's storage is opened.[^flaviocopes-pi-durable]

The harness script then follows one order — build a `BACKGROUND_CONTEXT`, register models and the extension, `Harness.open(openNodeSqliteStorage('./agent.sqlite'), { models, registry }, context)`, obtain the root conversation with an `agent` (model, instructions), call `harness.resume()`, `root.submit({ type: 'input', content, requestId })`, `submission.wait()`, commit the answer entry, and `harness.close()` in a `finally` block. Points that the surrounding README does not make obvious:[^flaviocopes-pi-durable]

- `root()` creates the root conversation on first use; reopening the same database returns it, and its initial agent settings apply only at creation. Changing them later goes through `root.configure()`.
- `resume()` is what starts recovery of pending tasks. Submitting or waiting also starts the scheduler, so the explicit call exists to make restart behavior visible.
- A hard process kill skips the `finally` block, which is exactly the condition being tested.
- Model credentials come from the environment; the article's model identifier is an example from its October 2026 snapshot, not a verified available model.

## The crash test

Run the request, wait for the tool's `Tool started` line, find the Node child that executes the TypeScript file (`pgrep -fl 'agent.ts'`), send it `kill -9`, and restart with the identical command. The submission ID printed after the restart should match the one from before the crash, and the replay-safe tool starts over, waits again, and returns its result.[^flaviocopes-pi-durable]

What this does and does not show:[^flaviocopes-pi-durable]

- Recovery resumes from durable checkpoints, not from the interrupted JavaScript instruction; the tool function restarts from its beginning because no result was committed.
- An interrupted model request can be sent again, and a stored partial answer is marked aborted rather than completed; a second request can mean a second API charge.
- The author reports that the recovery path was tested with SQLite and a scripted provider from Pi's testing utilities, killing a subprocess inside the real tool, reopening its database, and checking the submission ID. That verifies persistence and replay behavior without depending on a live model's wording; it does not measure model quality or exercise a real monitoring integration.

## The duplicate-request check

Rerunning the completed command should print the same submission ID and the saved answer, and should not start the tool again. `requestId` deduplicates admission of a submission, not work already done:[^flaviocopes-pi-durable]

- Retrying delivery of the same logical job reuses its ID; a genuinely new status check needs a new ID even when the prompt is identical.
- Never reuse an old ID for a different prompt — the ID identifies the original job, not a request for an updated answer.
- For a webhook, derive the ID from a stable event identifier and keep an incident-to-investigation mapping, because monitoring systems can send several different events about one incident.

Exactly-once behavior for external effects is a separate problem; see [replay safety and external effects](pi-durable-replay-safety.md).[^flaviocopes-pi-durable]

## Multi-client and deployment checklist

- **One owner.** A single process opens and owns a store; other clients connect through it, because Pi Durable provides no cross-process locking for independent harnesses on one database. For a UI, `root.viewState(context)` exposes committed entries, running tool output, and queued inputs so a reconnecting client does not need a private stream. Transport, authentication, and authorization remain the application server's job.[^flaviocopes-pi-durable]
- **Busy conversations.** A message sent while the conversation works becomes a follow-up by default; `whenBusy: 'steer'` joins the current work at a tool-round boundary and does not interrupt an executing tool. Cancelling a wait only stops that caller from waiting; aborting the conversation is a separate action, as described in [conversations and submissions](pi-durable-conversations.md).[^flaviocopes-pi-durable]
- **Deploys.** Mount persistent storage, keep the same database path, and stop the old owner before starting its replacement. A deleted database cannot be resumed, and SQLite's Node adapter uses WAL with `synchronous = NORMAL`, so a power failure can lose the newest commits even though a process crash is recoverable.[^flaviocopes-pi-durable]
- **Data handling.** Conversations and tool output can contain private prompts and service information; restrict access and back them up.[^flaviocopes-pi-durable]
- **Scope.** The demo agent has one read-only tool, no shell, no file editing, and no deployment credentials, so a compromised or confused run cannot repair or deploy anything.[^flaviocopes-pi-durable]

## From demo to a real investigation agent

The article's next step is a webhook that produces the request ID and prompt: verify the webhook and its project, find or create the incident's investigation, submit it under a stable ID, offer narrow tools over an isolated repository copy, run checks and prepare a pull request for review, then record the PR and reconcile later events with that investigation. It recommends keeping the crash test and adding a test that an interrupted unsafe action does not repeat, and that a duplicate event creates no second investigation.[^flaviocopes-pi-durable]

## Evidence and limits

Every procedure here is **Reported** from a tutorial published 2026-10-16 whose examples follow the package API as checked in October 2026; nothing was installed or run for this wiki, because the package is not in `raw/` and the demo needs provider credentials. The author's subprocess-kill test is a report of the author's own check, not an independent reproduction. The eight interactive SVG figures and the demo fixture are illustrative; the linked upstream README, runnable examples, and the Syntax video were not captured, so their content is a coverage limit. The `stale_after` date reflects the experimental API and the tutorial's own warning to keep a lockfile.

## Relationships

- **Demonstrates** the commit-before-display and resume behavior of [crash recovery](pi-durable-crash-recovery.md) with a concrete SQLite setup.
- **Depends on** single-owner [SQLite storage](pi-durable-storage.md) that survives a process restart.
- **Uses** a replay-safe [tool](pi-durable-tools-nested-calls.md) and applies the application-level checks in [replay safety](pi-durable-replay-safety.md).
- **Drives** [conversation submissions and steering](pi-durable-conversations.md) and reads `viewState` through [observability](pi-durable-observability-telemetry.md).
- **Is bounded by** [compaction](pi-durable-compaction.md), which can drop details a durable workflow must keep in documents.

[^flaviocopes-pi-durable]: Flavio Copes, “How to build agents that survive crashes with Pi Durable” (`raw/flaviocopes-pi-durable/index.md`, published 2026-10-16), locators: §What Pi Durable stores, §Create the project, §Give the agent a tool, §Open SQLite and submit a request, §Run the agent, §Kill it halfway through, §Retry a request without creating a second job, §Separate the transcript from the work, §Connect more than one screen, §Keep the storage when you deploy, §Long conversations still have context limits, §From this demo to an agent that investigates errors.
