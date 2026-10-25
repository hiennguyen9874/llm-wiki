---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../AGENTS.md) for storage and maintenance rules.

## Concepts

- [Home, Cloud, and Durable Agents: Where Work Runs and Whether It Survives](agent-execution-models-home-cloud-durable.md) — A comparison of running coding agents on your own machine versus a cloud virtual machine, and why durability is an orthogonal harness layer that resumes work after process death rather than a third place to run.
- [Pi Durable Build and Crash-Test Recipe](pi-durable-build-crash-test.md) — A worked recipe for a minimal SQLite-backed Pi Durable agent, the kill-and-restart test that shows replay, the duplicate-request check, and the deployment checklist.
- [Pi Durable Code Mode](pi-durable-code-mode.md) — Code mode lets the model run JavaScript in a sandbox that calls tools as nested tasks and journals results so a script resumes deterministically after a restart.
- [Pi Durable Compaction](pi-durable-compaction.md) — Manual and automatic compaction summarizes old entries into a pi.compaction entry, respects per-model token budgets, and governs how a too-long context recovers or fails.
- [Pi Durable Conversations and Submissions](pi-durable-conversations.md) — How pi-durable admits inputs and writes, queues work while busy, resets context, forks branches, owns conversations from tasks, and aborts cleanly.
- [Pi Durable Crash Recovery and Durability](pi-durable-crash-recovery.md) — How pi-durable commits before display, resumes interrupted work, bounds the loss from a crash, makes submissions idempotent, parks crash-looping tasks, and classifies fatal errors.
- [Pi Durable Documents and Host State](pi-durable-documents.md) — How pi-durable defines typed documents for host state, controls history and fork behavior, commits edits atomically, and defers cheap writes.
- [Pi Durable Extensions, Hooks, and Agents](pi-durable-extensions-hooks-agents.md) — How pi-durable packages behavior into named extensions, renders the system prompt, resolves a per-conversation agent, applies hooks, reloads code safely, and builds per-call execution environments.
- [Pi Durable Observability and Telemetry](pi-durable-observability-telemetry.md) — Pi Durable exposes committed state through watches and agent events, reports failures through onReport, and emits typed telemetry spans, events, metrics, and usage totals.
- [Pi Durable on Cloudflare Durable Objects](pi-durable-on-cloudflare.md) — A worked deployment pattern that maps one Pi session to a SQLite-backed Durable Object, holds events during initialization, streams committed state over hibernatable WebSockets, projects task deadlines onto one alarm, and delegates history search to an owned subagent.
- [Pi Durable Overview](pi-durable-overview.md) — An experimental TypeScript agent harness in which model turns, tool calls, and application state are committed to storage before display, so an interrupted process resumes where it stopped, built as a small general primitive rather than a feature of one product.
- [Pi Durable Replay Safety and External Effects](pi-durable-replay-safety.md) — Why a reused requestId deduplicates submissions but not side effects, how interrupted tool calls recover, and the per-operation checks that keep email, pull requests, and deployments from repeating.
- [Pi Durable State Model: Journal-and-Reduce to Authoritative Snapshots](pi-durable-state-model-snapshots.md) — How Pi Durable's persisted state reportedly moved from an event-sourcing-style journal-and-reduce in Harness v2 to complete, ID-keyed OperationState snapshots that are the authoritative recovery state rather than a cache that shortens replay.
- [Pi Durable Storage Backends](pi-durable-storage.md) — Pi Durable's storage options and their guarantees, including SQLite, JSONL, IndexedDB, Cloudflare Durable Objects, namespacing, transaction rules, and conformance testing.
- [Pi Durable Tasks and Lifecycle](pi-durable-tasks.md) — Tasks are durable state machines that checkpoint each phase, can sleep across restarts, wait on owned children, be abandoned on restart, and appear in a live task graph.
- [Pi Durable Tools and Nested Calls](pi-durable-tools-nested-calls.md) — How pi-durable defines tools, routes output to models versus programs, replays interrupted calls, restricts callers, runs nested tool calls as owned tasks, and handles images and bash results.
- [The Effect Sandwich: Durable Intent, Execution, and Result](pi-durable-effect-sandwich.md) — How pi-durable makes each step resumable by storing its intent, executing the effect, and persisting the result, and why external effects still need idempotency keys.
