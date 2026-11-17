---
type: Concept
title: Pydantic AI E2B sandbox recovery
description: How the E2B workspace capability isolates coding tools, resumes a sandbox across runs, and combines with Temporal recovery without exactly-once side effects.
tags: [pydantic-ai, agents, sandboxing, durability]
status: draft
created: 2026-11-17
generated: { by: llm-wiki-agent/1, at: 2026-11-17T06:52:17Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-e2b-2026
    resource: ../raw/pydantic-ai-e2b-sandboxes/index.md
    scope: ../raw/pydantic-ai-e2b-sandboxes/
    kind: article
    revision: sha256:5cea050dc1ebea3dd47cc8b270afee7d02f59d7fe1ff5f1861a82c5a19679d29
    title: "Pydantic AI + E2B: sandboxed coding agents in Python"
---

**Reported, Pydantic AI and Harness versions unspecified:** `E2BSandbox` supplies an E2B workspace backend to coding tools; a credential-free workspace reference can reconnect later runs or a recovered Temporal worker to the same sandbox. Preserving workspace state is not equivalent to exactly-once execution or rollback.[^pydantic-e2b-2026]

## Setup and boundary

The vendor's example installs `pydantic-ai-harness[e2b,anthropic,temporal]` and `pydantic-ai-slim[openai,logfire]`, with `E2B_API_KEY` and a model provider key. `E2BSandbox()` supplies execution, not tools: attach `Coder` or select `Shell` and `FileSystem` tools. The example exposes only `run_command`, `read_file`, `write_file`, and `edit_file`, and disables network access with `allow_internet_access=False`. The default E2B template reportedly has Python, git and pip, but not uv; install project dependencies in a custom template or inside the sandbox.[^pydantic-e2b-2026]

**Reported, versions unspecified:** the default sandbox timeout is one hour, after which E2B pauses rather than kills it; internet access defaults to enabled. The application owns sandbox lifetime: runs do not automatically kill it and forgotten sandboxes may incur charges. Plan explicit cleanup, including failure before a result exposes a reference; the article points to an `on_run_error` hook. Do not infer a complete security guarantee from isolation: the article does not specify all network, credential or hostile-code boundaries.[^pydantic-e2b-2026]

## Resume across runs

**Reported, versions unspecified:** construct `E2BSandboxBackend(working_dir=..., sandbox_timeout=600, allow_internet_access=False)` and wrap it in `Workspace`. Backend construction performs no I/O; the first workspace write provisions the sandbox. Pass the backend as `workspace` for the first run, retain `first.workspace.ref`, and pause via `await (await backend.get_sandbox()).pause()`. A new backend built with `E2BSandbox(...).backend(ref)` resumes it on first file access. The second run can pass `workspace=ref` and `message_history=first.all_messages()`: the reference selects the workspace, while history carries the conversation; the article says history naming the workspace can also select it.[^pydantic-e2b-2026]

The article reports E2B retains paused filesystem and memory indefinitely. Its example checks the same sandbox ID and file hashes across pause, restores a trusted test file before independently running tests, checks input logs, and kills the sandbox in `finally`. Restoring tests matters because shell commands can bypass restrictions on file tools. These are vendor-reported example outcomes, not checks reproduced here.[^pydantic-e2b-2026]

## Temporal worker recovery

**Reported, versions unspecified:** add `TemporalDurability` to a named agent, define agent and workflow at module scope for activity registration, and give the workflow a `WorkspaceRef` created and seeded by the controller. Temporal records this credential-free input before worker execution. In the example the workflow saves a diagnosis and checksums, waits for a signal, and a controller kills the idle worker with `SIGKILL`; a replacement worker on the same task queue replays history, checks the checkpoint, and continues using the original reference. The article reports one sandbox, four passing tests, and verified cleanup. If the referenced sandbox is gone, `WorkspaceUnavailableError` is reported instead of silent replacement.[^pydantic-e2b-2026]

The demonstration crashes **between** runs, not during a command. Activities may repeat if a worker dies before completion is recorded: shell side effects are at-least-once, and recovery does not undo file writes. Prefer idempotent operations, such as replacing a named result rather than appending; this does not make arbitrary commands exactly-once.[^pydantic-e2b-2026]

## Tracing and costs

**Reported, versions unspecified:** `E2BSandbox` creates no spans itself; agent run spans include `pydantic_ai.workspace.provider` and `pydantic_ai.workspace.id`, while tool calls contain their command or file operations. The example uses `logfire.configure()` and `logfire.instrument_pydantic_ai()` to correlate the two runs by sandbox ID. Its per-run `UsageLimits` allow eight requests and an estimated $0.10; the estimate depends on pricing data, the final request can exceed it, and neither bound is an account spending cap.[^pydantic-e2b-2026]

## Coverage and limits

The source is a Pydantic vendor article by Laís Carvalho, published 2026-10-22; its sole local artifact, `index.md`, was inspected. Linked E2B cookbook code, provider persistence documentation, and external traces were not fetched; article examples and output are not independently verified. No package was installed, sandbox created, worker killed, or trace opened. The source names no Pydantic AI, Harness, E2B or Temporal version; configuration and defaults may change. License and capture date are not stated. Promotional pricing is excluded.[^pydantic-e2b-2026]

## Relationships

- **Uses** [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) for the common file and command boundary.
- **Composes with** [Pydantic AI durable execution](pydantic-ai-durable-execution.md): Temporal replay retains the workspace reference, not exactly-once side effects.
- **Related to** [Pydantic AI observability](pydantic-ai-observability.md): workspace identifiers correlate sandbox activity with agent traces.

[^pydantic-e2b-2026]: Laís Carvalho, [Pydantic AI + E2B: sandboxed coding agents in Python](../raw/pydantic-ai-e2b-sandboxes/index.md), Pydantic, 2026-10-22, sections “One line, and the agent is off your machine”, “Diagnose, pause, resume, fix”, “Kill the worker, keep the sandbox”, “Where the trace goes”, and “Get started”. **Reported:** vendor article; external sources not fetched and examples not executed.
