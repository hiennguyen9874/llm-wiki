---
type: Concept
title: Pydantic AI durable execution
description: The nine durability engines Pydantic AI supports, where each integration ships, and the naming and step rules a deployment must not break.
tags: [ml, pydantic-ai, agents, durability]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:02:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: colvin-code-is-graph-2026
    resource: ../raw/the-code-is-the-graph/index.md
    scope: ../raw/the-code-is-the-graph/
    kind: article
    revision: sha256:d8803b5fa767d23f0a03bda63f364781d1f1f476ba4e3d243f33e05dea5f21be
    title: "The code is the graph"
---

Durable execution is attached as one [capability](pydantic-ai-capability-primitive.md), so the agent code barely mentions it, and Pydantic AI offers more engines than the frameworks the source compares it with: nine, plus a builder for any other backend. The engines are split by docs group and by where their code ships, which decides whose stability policy covers them[^dd-v2-tour-2026]

## The engines and their shipping location

| Engine | Docs group | Ships in |
| --- | --- | --- |
| Temporal, DBOS, Prefect | Co-maintained by Pydantic and the vendor | Core `pydantic-ai` (`pydantic_ai.durable_exec`) |
| Restate | Co-maintained | Restate's own Python SDK (`restate.ext.pydantic`) |
| AWS Lambda | Co-maintained | [Harness](pydantic-ai-harness.md) (`AWSLambdaDurability`, extra `pydantic-ai-harness[aws-lambda]`) |
| Absurd | Additional external SDK integration | Harness, added v2.53.0 (`AbsurdDurability`, replacing `pydantic-ai-absurd`) |
| pgtask | Additional external SDK integration | Harness, added v2.56.0 (`PGTaskDurability`) |
| Kitaru, Apache Airflow | Additional external SDK integration | External SDKs |

An engine that ships in the Harness follows the Harness 0.x promise rather than core's stricter policy, so the placement is an upgrade-risk decision, not trivia[^dd-v2-tour-2026]

## One engine per agent

Each agent gets one engine. Since v2.54.0 a second one is refused at construction: building an agent with two durability capabilities raised `UserError` with "An agent can have only one durable execution engine"[^dd-v2-tour-2026]

## DBOS: names become step names

Two requirements are easy to miss. Each agent needs a unique `name`, and each `MCPToolset` needs a unique `id`; DBOS derives step names from those values, so renaming either after deploy breaks in-flight workflows. Function tools registered by the application are not wrapped automatically — any that do I/O must be decorated with `@DBOS.step`[^dd-v2-tour-2026] Since v2.57.0 the waits between continuation polls (Anthropic `pause_turn`, OpenAI background mode) are durable `DBOS.sleep` steps, so recovery skips waits that already finished.

The source's DBOS example also shows the shape of a deployment: `DBOS(config=DBOSConfig(...))` at import time, an agent with `name='support'` and `capabilities=[DBOSDurability()]`, and a `@DBOS.workflow()` wrapper that calls `agent.run(question)`[^dd-v2-tour-2026]

## Retry classification reaches the engine

Durability and error typing meet in `non_retryable_model_errors` (v2.59.0): Temporal can be told to stop retrying failures such as a context-window overflow that will never succeed[^dd-v2-tour-2026] The error categories themselves are covered in [Pydantic AI run controls](pydantic-ai-run-controls.md).

## What durability does not give you

Durability keeps one run alive across crashes; it does not store a chat thread between runs, and a conversation round-trip needs only a database column — see [Conversation state](pydantic-ai-conversation-state.md). Graph state is a third case: the [graph builder](pydantic-ai-graph-builder.md) deliberately does not checkpoint between steps.

## Replay instead of snapshots

Temporal's model, as the `pydantic-graph` author describes it, never snapshots application state at all: it records the result of each activity as it completes and re-runs the code to rebuild the state, so a question like "how many of three in-flight state updates had happened" is answered by replay rather than by a serialized checkpoint[^colvin-code-is-graph-2026] Two consequences follow for anyone designing around it. An activity interrupted mid-flight may run twice, and the activity boundary is where **you**, not the engine, declare what touches the outside world and whether a retry is safe[^colvin-code-is-graph-2026] And because the state is the code, any orchestration layer replayed alongside it has to be deterministic too — the argument for keeping model-written choreography as plain Python rather than a node library, in [Code as the agent graph](code-as-agent-graph.md).

The same pattern recurs inside a sandbox: Monty, the interpreter the Harness `CodeMode` capability runs model-written Python in, snapshots the interpreter at each host-function call, which is the sandbox's equivalent of an activity boundary[^colvin-code-is-graph-2026]

## Limits

- The engine count and the co-maintained/extra classification are the article's reading of the durable-execution docs; no engine integration, vendor SDK, or crash test was exercised in this ingest[^dd-v2-tour-2026]
- The article defers crash and retry behaviour to a separate comparison post, so what actually survives a mid-tool crash is not documented here.
- The one-engine restriction was observed by the author as a construction error, not from release notes.
- The replay-versus-snapshot description is the `pydantic-graph` author's account of Temporal, published on Pydantic's site with no Temporal version named; no workflow was replayed and no activity was interrupted here[^colvin-code-is-graph-2026]
- Evidence class: **Reported**.

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) for attachment.
- **Ships partly in** the [Pydantic AI Harness](pydantic-ai-harness.md), which governs its version stability.
- **Complemented by** [deferred tool approval](pydantic-ai-deferred-approvals.md), which turns a human wait into a serialized pause.
- **Avoids** the mistake of using an engine where [Conversation state](pydantic-ai-conversation-state.md) suffices.
- **Is the outside-the-sandbox half of** the durability argument in [Code as the agent graph](code-as-agent-graph.md); Monty is its inside-the-sandbox half.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Durable execution: nine engines, one line to attach" (raw lines 358–399) for the engine table, shipping locations, the one-engine `UserError`, the DBOS naming and `@DBOS.step` rules, `DBOS.sleep` continuation waits, and the DBOS sample; §"What changed in v2.58 and v2.59" for `non_retryable_model_errors`; §"Example 3" for the engine-versus-thread distinction. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — docs summary plus one observed construction error; no durable engine was run.
[^colvin-code-is-graph-2026]: Samuel Colvin, "The code is the graph", Pydantic, published 2026-10-13T09:00Z, 2,445 words as declared; local capture `raw/the-code-is-the-graph/index.md`, content digest sha256:d8803b5f. §"Typed, snapshotted, parallel: pick two" (raw lines 113–143) for Temporal's replay instead of state snapshots, the at-least-once activity and the declaration of side effects at the activity boundary, and the note that graph machinery is one more thing that must replay deterministically; §"Long live graphs" (lines 145–167) for Monty's host-function boundary as the sandbox's snapshot point. Evidence class: **Reported** — vendor article; no workflow, activity or interpreter was exercised here.
