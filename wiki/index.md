---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../AGENTS.md) for storage and maintenance rules.

## Concepts

- [Durable Pi Agent Network](durable-pi-network.md) — A device-owned durable agent network with a backend per machine, a local hub, and web, terminal, and API clients.
- [Durable Pi Device API and Streams](durable-pi-device-api.md) — The reported v1 device API for message admission, creation receipts, streaming snapshots, shared state, and durable jobs.
- [Durable Pi Proactive Incident Demo](durable-pi-proactive-demo.md) — A simulated incident pipeline combining per-row classification, coded thresholds, an agent investigation, and checkpointed human-approved deployment.
- [Eta Bot Operation and Recovery](eta-bot.md) — Eta Bot hosts remote agent threads with request deduplication, snapshot streaming, recovery controls, and optional Discord intake.
- [Eta Personal Agent Architecture](eta-overview.md) — Eta combines a desktop agent, self-hosted Bot, and mobile companion around a shared agent core, with separate local and cloud state.
- [Eta Sandbox and Approval Boundaries](eta-security.md) — Eta's local and Bot execution modes differ in defaults, approval review, operating-system support, and full-access risks.
- [Foreman Attached Hooks and Pi Integration](foreman-attached-hooks.md) — Foreman supervises externally started coding sessions through local hook adapters, including a Pi and Pi Durable bridge.
- [Foreman Evidence and Request Budgets](foreman-evidence.md) — Foreman selects bounded evidence per check, compacts model requests, and can run centrally configured trusted evidence commands.
- [Foreman Responsibilities and Routing](foreman-responsibilities.md) — Foreman routes jobs to additive responsibilities whose checks propose directives that policy arbitrates.
- [Foreman Semantic Supervision Overview](foreman-overview.md) — Foreman separates coding-agent work from decision-model supervision, responsibility checks, and deterministic intervention policy.
- [Home, Cloud, and Durable Agents: Where Work Runs and Whether It Survives](agent-execution-models-home-cloud-durable.md) — A comparison of running coding agents on your own machine versus a cloud virtual machine, and why durability is an orthogonal harness layer that resumes work after process death rather than a third place to run.
- [Pi Agents Configuration, Profiles, and Hooks](pi-agents-configuration.md) — Reusable agent profiles, concurrency and tool sharing, and extension hooks for durable agent requests.
- [Pi Agents Graphs and Delegation](pi-agents-graphs.md) — How Pi Agents groups, dependency graphs, recursive spawning, waits, and failure handling compose delegated work.
- [Pi Agents Messaging Guarantees](pi-agents-messaging.md) — Peer message reach, ordering, delivery, interruption, and limits in a Pi Agents session.
- [Pi Agents Overview and Recovery](pi-agents-overview.md) — A Pi extension for named, session-owned agents backed by Pi Durable, with separate storage and bounded recovery guarantees.
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
- [Pi Orbs Architecture and Deployment](pi-orbs-overview.md) — Pi Orbs deploys named Pi Durable bots on one Fly.io Sprite from a local client, with shared workspace and model.
- [Pi Orbs Bot Coordination and State](pi-orbs-coordination.md) — Pi Orbs isolates bot conversations while using steer submissions and a bounded ledger for cross-bot coordination.
- [Pi Orbs Schedules, Voice, and MCP Integrations](pi-orbs-integrations.md) — Pi Orbs integrates scheduled bot messages, realtime voice, signed MCP events, and sandboxed MCP Apps through distinct paths.
- [Pi Orbs Security and Approval Boundaries](pi-orbs-security.md) — Pi Orbs exposes a public Sprite endpoint while separating local credentials, gateway keys, webhook authentication, and command approvals.
- [Pi Pocket Deployment and Remote Access](pi-pocket-deployment.md) — Installation, networking, backup, upgrade, and container considerations for operating Pi Pocket.
- [Pi Pocket Linked Sessions and Durable Automation](pi-pocket-orchestration.md) — How Pi Pocket coordinates linked agent sessions, durable schedules and watches, including replay and delivery limits.
- [Pi Pocket Overview and Architecture](pi-pocket-overview.md) — Pi Pocket is a self-hosted, mobile-first multiplayer application built on Pi Durable, with SQLite-backed agent state and a separate launcher and server.
- [Pi Pocket Security and Trust Boundaries](pi-pocket-security.md) — Pi Pocket's reported access, session, browser, extension, and container trust boundaries and their limitations.
- [Pi Tab Browser Agent Overview](pi-tab-overview.md) — Pi Tab runs a Pi Durable-based agent as a bookmark or Chrome extension, with distinct page access, storage, and collaboration scopes.
- [Pi Tab Linux Tools](pi-tab-linux.md) — Pi Tab's extension offers per-conversation ephemeral Linux Wasm tools with restricted networking and explicit loss and replay limits.
- [Pi Tab Recovery and Storage](pi-tab-recovery.md) — Pi Tab's bookmark and extension modes differ in conversation ownership, reload recovery, page authorization, and deletion guarantees.
- [Pi Tab Security and Integrations](pi-tab-security.md) — Pi Tab's page access, model credentials, and remote MCP integrations cross different trust boundaries in bookmark and extension modes.
- [The Effect Sandwich: Durable Intent, Execution, and Result](pi-durable-effect-sandwich.md) — How pi-durable makes each step resumable by storing its intent, executing the effect, and persisting the result, and why external effects still need idempotency keys.
