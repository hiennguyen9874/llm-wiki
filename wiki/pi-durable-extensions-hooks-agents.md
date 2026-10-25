---
type: Concept
title: Pi Durable Extensions, Hooks, and Agents
description: How pi-durable packages behavior into named extensions, renders the system prompt, resolves a per-conversation agent, applies hooks, reloads code safely, and builds per-call execution environments.
tags: [pi-durable, extensions, hooks, system-prompt]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:02:23Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-readme
    resource: ../raw/pi-durable-readme.md
    kind: docs
    title: "@earendil-works/pi-durable README"
---

Everything the Harness runs beyond its built-in tasks comes in named **extensions** installed in a registry the host process owns. An extension bundles tools, system-prompt sections, hooks, wrappers (`wraps`), and tasks. Nothing in the registry is stored; conversations store extension names, which are resolved against the registry at each use. By default every conversation selects every installed extension in install order, and `settings.extensions` can set a default selection.[^pi-durable-readme]

## Reload and code lifetime

Installing an extension with an installed name replaces it in place in one step, and `registry.uninstall(extension)` removes the installed extension with that name whichever object it is. Work already started keeps the code it took: a running tool call finishes under its old implementation, and each task phase resolves hooks and the agent once at the phase's start. The next phase, request, or call uses the new code. After a restart the host must install the same extensions again; pending tasks of an extension's `tasks` resume once it is installed.[^pi-durable-readme]

## Hooks

Hooks observe or adjust built-in tasks in conversations that select their extension. Generation hooks are `beforeRequest` (replace the messages of one request), `afterResponse`, `onYield` (continue the run with another user message), and `afterTools` (runs once a round's tools are done). Tool hooks are `beforeTool` (block or rewrite arguments) and `afterTool` (replace the result). A throwing hook is reported and skipped, and a throwing `beforeTool` blocks the call. Limiting a hook to some conversations is done by selecting its extension only there, for example with `configure({ extensions: { add: [Guard] } })`.[^pi-durable-readme]

## System prompt

The system prompt is built from the selected extensions' sections, rendered in order before each request. A section receives the resolved agent, the request's environment, and committed documents, and may read documents through `input.read`, treating an absent one as its default. The conversation's `instructions` render last as the section `instructions`. Section and tool changes are stored as positional system entries in the transcript, and only what changed is sent again, which keeps provider prompt caches warm. A section that returns something different every time, such as the current time, defeats that caching.[^pi-durable-readme]

## Per-conversation agent

Each conversation stores what it runs with in its `pi.agent` document; `configure()` changes it in one commit, and unset fields follow the host. Settable fields are `model`, `thinkingLevel`, `extensions`, `tools`, `modelTools`, `instructions`, and `cwd`; an array selects exactly those entries, `{ remove: [...] }` drops some, and `null` clears a field back to the host default. `agent()` returns the resolved agent. Extensions and tools are passed as objects and stored by name, so a stored name outlives its code: after uninstall, conversations that select it simply stop getting it until it is installed again.[^pi-durable-readme]

`createConversation()`, `fork()`, and `root()` accept the same agent change. A task-owned conversation, such as a subagent's, starts as a copy of its owner's agent; a fork starts with the agent its parent had at the fork entry. The model, prompt, and offered tools of a request are fixed when it is prepared, so a change applies from the next request; tool calls and hooks use the agent as their task phase resolves it, and the environment is built from the current `cwd` at each use, so a `cwd` or extension change can reach calls the model already made.[^pi-durable-readme]

## Run policy and settings

`settings` is run policy shared by every conversation. It is read at every use and never stored, so getters make it live — for example backed by a settings file. The README's example configures `extensions` (default selection; absent means every installed extension), `stream: { timeoutMs }`, `retry: { maxRetries }`, `compaction: { reserveTokens }`, `progress: { partialIntervalMs, outputIntervalMs, persistWithinMs }`, `toolExecution: "parallel"`, `contextRetentionMs` (how long idle conversations keep context in memory, checked lazily where background timers are declined, as in Workers), `documentRetentionMs` (how long loaded documents nothing observes stay in memory after last use; observed ones always), and a `followUpMode` getter. Other settings govern `afterFailedRun` and `restartLimit` (see [crash recovery](pi-durable-crash-recovery.md)), `steeringMode`/`followUpMode` (see [conversations](pi-durable-conversations.md)), and compaction thresholds (see [compaction](pi-durable-compaction.md)).[^pi-durable-readme]

## Environment

`env` builds the execution environment for each tool call, section rendering, and `runtime.env()`. It receives the conversation's ID, its agent `cwd`, and committed reads, so one function can serve a directory per conversation or a container per conversation. A throw from `env` becomes the call's error result; without an environment, built-in tools fail with an error result. A fresh environment object per call is fine: `edit` and `write` serialize changes to one file by the environment's `id` and path, so a custom `ExecutionEnv` sets `id` such that equal ids see the same files at the same paths.[^pi-durable-readme]

Hosts can use the environment directly, for example to show a project's files. `openBinaryReader()` reads byte ranges of one opened file, `openDirReader()` pages a directory, and `exec()` with an argv array runs a program without a shell and reports which stream each chunk came from. Aborting the context stops one call; `cleanup()` shuts the environment down. Some environments implement optional `listFiles()` (files and directories below a path at any depth, skipping git-ignored paths, with `truncated` at bounds); `NodeExecutionEnv` does not, while pi-env's `RemoteExecutionEnv` and `LocalExecutionEnv` do, and callers fall back to their own walk on `not_supported`.[^pi-durable-readme]

## Evidence and limits

Extension, hook, prompt, and environment behavior is **Reported** by the README; nothing was loaded or executed. The README does not enumerate every built-in extension or section, so coverage of those is a limit.

## Relationships

- **Bundles** [tools](pi-durable-tools-nested-calls.md) and [code mode](pi-durable-code-mode.md) as extensions.
- **Configures** the agent that drives [conversations](pi-durable-conversations.md) and [compaction](pi-durable-compaction.md).
- **Hooks into** [tasks](pi-durable-tasks.md) and reports failures through [observability](pi-durable-observability-telemetry.md).
- **Uses** the environment abstraction to reach files and processes; the durable substrate is [storage](pi-durable-storage.md).

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Extensions, §Reload, §Hooks, §System Prompt, §Per-Conversation Agent, §Settings, §Environment, §Tools.
