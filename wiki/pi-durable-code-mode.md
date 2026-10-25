---
type: Concept
title: Pi Durable Code Mode
description: Code mode lets the model run JavaScript in a sandbox that calls tools as nested tasks and journals results so a script resumes deterministically after a restart.
tags: [pi-durable, code-mode, sandbox, determinism]
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

`@earendil-works/pi-durable/codemode` adds a `codemode` tool: the model writes JavaScript that calls the conversation's tools as `await tools.<name>(args)` inside a QuickJS sandbox (`@earendil-works/pi-codemode`). Each call is a nested tool call, and only the script's output reaches the model. The script survives a restart by resuming where it was without rerunning its finished calls.[^pi-durable-readme]

## Setup and prompt surface

`createCodemodeExtension({ sandbox: new CodemodeSandbox({ memoryLimitBytes: 256 * 1024 * 1024 }) })` installs the extension. It also adds a `codemode` prompt section listing callable tools as TypeScript declarations within a token budget; scripts find others with `searchTools()`, `describeTool()`, and `describeNamespace()`. Tools can be grouped by name prefix with `namespaces: [{ name, description, prefix }]`, such as an MCP server's `mcp__github__`. Scripts also get `models.*`: the model catalog, `models.classify()`, and `models.generateImages()`, run as nested calls of internal tools; `models: false` disables them. On Cloudflare, pass a `RemoteCodemodeSandbox` instead.[^pi-durable-readme]

The result reads like a coding agent's: a header, the script's output, and on failure the calls already made; text past `max_output_tokens` is cut, with the full text in a temporary file. A failed nested call rejects in the script with its error text, unless the tool declares a schema and returned its own value with the error: `tools.bash` resolves with `{ output, exitCode, ... }` even for a nonzero exit, so scripts check `exitCode`. `store(key, value)` and `load(key)` keep JSON values per conversation, and a fork sees them as they were at its entry.[^pi-durable-readme]

## How a restart preserves a script

The sandbox runs the script deterministically (a virtual clock, seeded randomness, UTC), and the tool writes each result the script receives to a journal before handing it over. After a restart, the tool runs the script again and hands it the journaled results in the same order, so it makes the same calls with the same arguments; these reattach to their nested calls by key, and then the script continues. A rerun ends the call with an error instead when the script takes another path than before, when the sandbox's fingerprint or the code-mode version changed, or when its `timeout_ms` passed meanwhile. A nested call that was running at the restart follows its own replay policy.[^pi-durable-readme]

Closing the sandbox while a script runs (for example during shutdown) is not an outcome: the script resumes with the next process's sandbox.[^pi-durable-readme]

## Evidence and limits

Code-mode behavior is **Reported** documentation; no sandbox was run. The README does not list every QuickJS capability restriction, so the sandbox's exact JavaScript surface is a limit. The guarantee depends on tool results being deterministic and on nested calls honoring their replay policy, both described in [tools and nested calls](pi-durable-tools-nested-calls.md).

## Relationships

- **Is installed as** an [extension](pi-durable-extensions-hooks-agents.md).
- **Calls** [tools](pi-durable-tools-nested-calls.md) as nested durable tasks keyed for replay.
- **Runs under** [task](pi-durable-tasks.md) lifecycle rules and relies on [crash recovery](pi-durable-crash-recovery.md) for the journal's durability.
- **Uses** the [storage](pi-durable-storage.md) commit path and reports through [observability](pi-durable-observability-telemetry.md).

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Code Mode, §Calling tools from tools, §Who may call a tool.
