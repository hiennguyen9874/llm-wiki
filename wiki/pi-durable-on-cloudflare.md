---
type: Concept
title: Pi Durable on Cloudflare Durable Objects
description: A worked deployment pattern that maps one Pi session to a SQLite-backed Durable Object, holds events during initialization, streams committed state over hibernatable WebSockets, projects task deadlines onto one alarm, and delegates history search to an owned subagent.
tags: [pi-durable, cloudflare, durable-objects, deployment, websockets, subagents]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:12:06Z }
stale_after: 2027-01-25
sources:
  - id: earendil-pi-durable-on-cloudflare
    resource: ../raw/earendil-pi-durable-on-cloudflare/index.md
    scope: ../raw/earendil-pi-durable-on-cloudflare/
    kind: article
    title: "Pi Durable on Cloudflare"
---

Earendil's sample deployment gives each Pi Durable session its own SQLite-backed Cloudflare Durable Object, so the harness hibernates while idle and resumes on a request, WebSocket message, or alarm. A Worker mints the session ID and a shareable URL, participants connect to it over hibernatable WebSockets, and the object owns the Pi harness, the conversations, and the task deadlines; the pattern is presented as a small multiplayer chat agent rather than a production template.[^earendil-pi-durable-on-cloudflare]

## Session-to-object mapping

The durable boundary is one Pi session per Durable Object instance, addressed by the session ID. The Worker creates the ID and returns the shareable URL; everyone opening that URL reaches the same object, while different IDs reach objects with isolated state. Inside the object, WebSockets survive hibernation, the embedded SQLite database holds conversations and tasks, and the harness calls the model provider. The article's diagram is the whole architecture: React client over PartySocket → Worker routing by session ID → SQLite-backed Durable Object instance.[^earendil-pi-durable-on-cloudflare]

## Initialization on every start

Cloudflare runs the Durable Object constructor on first creation and again after hibernation or eviction, whenever a request, alarm, or WebSocket message arrives. The sample wraps all of that in `ctx.blockConcurrencyWhile(() => this.#initialize())`, so events are held back until initialization finishes. Initialization opens the object's SQLite storage with `openDurableObjectSqliteStorage(ctx.storage)`, calls `Harness.open` with an `onReport` that reports background-task failures, then restores the live event streams and the alarm.[^earendil-pi-durable-on-cloudflare]

A failed Harness is turned into an object reset: the constructor attaches to `harness.closed`, and when `end.reason` is `"failed"` it calls `this.ctx.abort("Harness failed")` so the next event starts a fresh object that reopens the storage. If initialization itself throws, the sample closes the harness before rethrowing, leaving the next start to retry the open. This is the concrete host-side counterpart to the general rule that a storage error ends the harness and reopening recovers.[^earendil-pi-durable-on-cloudflare]

## Multiple conversations in one session

The session is not one transcript. Participants create independent ownerless conversations or fork one from a committed user or assistant entry; a fork receives the parent's history up to the selected entry. To avoid duplicate conversations after a dropped WebSocket, the sample stores a receipt keyed by the request ID in the same commit that creates the conversation: the transaction reads `ConversationCommandReceipts` by request ID, returns the saved conversation ID when present, and otherwise creates the conversation and writes the receipt. Forks use `tx.forkConversation(parentConversationId, entryId, …)` and take the same ownerless ownership.[^earendil-pi-durable-on-cloudflare]

Incoming messages are submitted as follow-up prompts with a display-name attribution and the client's `requestId` and `whenBusy: "followUp"`. When several participants send while the model or a tool is running, their messages wait in Pi's durable inbox and are answered in order.[^earendil-pi-durable-on-cloudflare]

## Streaming committed state to clients

For each connected client the session opens Pi's `watchEvents` stream for the selected conversation. The stream begins with an atomic snapshot and then emits batches for committed transcript changes, streaming output, tools, compaction, resets, and inbox changes; the React client applies them to the selected conversation, and a separate session snapshot fills the sidebar. The socket stores `{ username, conversationId }` as a serialized attachment, so the participant's identity and selection survive hibernation and the object can reopen the matching streams when it wakes. A reconnecting client resends anything the server has not confirmed under the same request ID, so nothing runs twice.[^earendil-pi-durable-on-cloudflare]

## Resuming work and projecting deadlines

After restoring live views, the session inspects the persisted task set. Deadlines that lie in the future are projected onto the Durable Object alarm; tasks that can run now start Pi's scheduler through `waitForTask()`, and the session recalculates its next alarm once they settle. The agent's `schedule` tool becomes a durable Pi task that sleeps until its deadline, so a scheduled instruction survives the object going idle.[^earendil-pi-durable-on-cloudflare]

The mapping is many-to-one: Pi can track any number of deadlines, but a Durable Object has only one alarm. The sample's `#refreshAlarm()` walks the stored tasks, skips blocked ones, takes the earliest future deadline, and brings the alarm forward when a newly scheduled task comes first. Every task not waiting on a future time — ready, running, or being recovered — gets a short recovery alarm (`RECOVERY_ALARM_DELAY_MS`) instead, so an evicted object returns to finish in-progress work; the recovery alarm is persisted before `waitForTask()` starts the scheduler, because that call can settle immediately.[^earendil-pi-durable-on-cloudflare]

Because alarms execute at least once, the alarm handler must be idempotent. `#refreshAlarm()` recalculates everything from stored tasks rather than from in-memory state, and the scheduled instruction's stable request ID prevents a second submission when the alarm fires twice.[^earendil-pi-durable-on-cloudflare]

## Durable history search with an owned subagent

With several conversations per session, a participant can ask about something outside the selected context. Instead of loading every transcript into the parent conversation, the sample's `search_history` tool delegates retrieval to a subagent: in Pi Durable a subagent is an ordinary conversation owned by the tool task that created it. The child searches user and assistant messages of top-level conversations, including earlier messages of the conversation that started the search, and it cannot search its own conversation or messages produced by earlier searches, so generated answers never become evidence for a later search. The subagent's only tool, `search_conversations`, is a deliberately simple substring search in the sample; raw matches and intermediate tool calls stay isolated in the child, and the parent receives only the final answer.[^earendil-pi-durable-on-cloudflare]

The tool is marked replay-safe, so if the object is evicted mid-call Pi reruns it instead of reporting an interruption. The rerun stays safe because the commit scans conversations by `ownerTaskId` and returns an existing child, and the submission uses the stable ID `search-history:${taskId}`; `api.details({ conversationId })` lets the interface link the parent tool call to its subagent. This is a working instance of the general ownership rule that an owned child gives a replayed tool a durable identity to find and continue.[^earendil-pi-durable-on-cloudflare]

## Storage conformance and local run

The Cloudflare adapter goes through the Durable Object's synchronous `SqlStorage` API (`ctx.storage.sql`). A custom backend can be checked with the shared conformance suite; the article shows running it against a Durable Object through Cloudflare's Workers Vitest integration inside `runInDurableObject`, using the instance's `state.storage`.[^earendil-pi-durable-on-cloudflare]

The sample lives at `github.com/earendil-works/pi-durable-cloudflare` and needs Node.js 22.19 or newer, pnpm 11, and an OpenAI API key: copy `.dev.vars.example` to `.dev.vars`, set `OPENAI_API_KEY`, and run `pnpm dev`. The walkthrough then creates a session, opens its URL in a second browser, states a decision in one conversation, creates another, asks what was decided, inspects the search subagent's searches, and schedules a weather check two minutes out before closing the browser and returning after the deadline. The demo intentionally has no authentication, so it is a local demonstration, not a deployment to expose.[^earendil-pi-durable-on-cloudflare]

## Evidence and limits

Everything here is **Reported** from a vendor engineering post published 2026-10-16; no Worker, Durable Object, WebSocket, alarm, or sample repository was run or inspected in this repository, and the code appears only as snippets quoted by the article, so it was not compiled. The sample repository itself, its tests, and its full implementation (including live task-activity streaming and subagent notifications) are outside the captured source. The four demonstration videos are remote mp4/webm assets whose behavior the text describes; they were not downloaded or viewed, and they carry no additional claims here. Cloudflare's constructor, hibernation, alarm, and `SqlStorage` semantics are the article's account and platform behavior that may change, which the `stale_after` date records.[^earendil-pi-durable-on-cloudflare]

## Relationships

- **Deploys** the [Pi Durable harness](pi-durable-overview.md) as one session per Durable Object.
- **Uses** the Cloudflare [storage backend](pi-durable-storage.md) and its conformance path.
- **Persists** [conversations](pi-durable-conversations.md), their forks, and conversation-creation receipts.
- **Projects** [task](pi-durable-tasks.md) deadlines onto the platform alarm and recovers in-progress work.
- **Streams** committed state through the [event and watch](pi-durable-observability-telemetry.md) surface.
- **Implements** a replay-safe [tool](pi-durable-tools-nested-calls.md) whose subagent is an owned conversation, under the [replay safety](pi-durable-replay-safety.md) rules.
- **Relies on** the [crash recovery](pi-durable-crash-recovery.md) rule that a failed harness closes and reopens on the next start.

[^earendil-pi-durable-on-cloudflare]: Earendil Engineering, “Pi Durable on Cloudflare” (`raw/earendil-pi-durable-on-cloudflare/index.md`, published 2026-10-16; <https://earendil.com/posts/pi-durable-on-cloudflare/>), locators: §One Pi session per Durable Object, §Persist Pi session data in Durable Object storage, §Open Pi when the Durable Object starts, §Run multiple conversations in one shared session, §Stream durable conversation state, §Resume after hibernation and wake for work, §Map Pi deadlines to the Durable Object alarm, §Search conversation history with a durable subagent, §Run locally.
