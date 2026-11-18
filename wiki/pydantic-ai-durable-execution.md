---
type: Concept
title: Pydantic AI durable execution
description: The nine durability engines Pydantic AI supports, where each integration ships, and the naming and step rules a deployment must not break.
tags: [ml, pydantic-ai, agents, durability]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:52:00Z }
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
  - id: durable-exec-docs
    resource: ../raw/capabilities/durable_execution/overview/index.md
    scope: ../raw/capabilities/durable_execution/overview/
    kind: documentation
    revision: sha256:3601b2702b26f347d71e6b5a302b709d9bc87e177fba35c85eaaf7be1cf45333
    title: "Durable Execution"
  - id: pydantic-subagents-docs
    resource: ../raw/harness/subagents/index.md
    scope: ../raw/harness/subagents/
    kind: documentation
    revision: sha256:53a83ad8be94200b67b4414a89df6e179c81b68c3a602f6fc242efd32761a974
    title: "Subagents"
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
---

Durable execution is attached as one [capability](pydantic-ai-capability-primitive.md), so the agent code barely mentions it, and Pydantic AI offers more engines than the frameworks the source compares it with: nine, plus a builder for any other backend. The engines are split by docs group and by where their code ships, which decides whose stability policy covers them[^dd-v2-tour-2026]

**Reported, version unspecified:** the reason to pay for an engine is narrower than "make the agent reliable". Use one when a run in flight has to survive its process stopping — through a deploy, a crash or a transient API failure — or when a workflow waits hours or days for a person or another system[^durable-exec-docs] The mechanism is a journal plus replay: the engine records the agent's model requests and the tool calls it wraps, and a restarted run replays the completed ones from the journal and retries the one in flight[^durable-exec-docs] Which tool calls (function tools, MCP servers) an engine wraps for you, and how it delivers streaming, differ per engine[^durable-exec-docs]

For a worked Temporal recovery example and the limits of replaying sandbox side effects, see [E2B sandbox recovery](pydantic-ai-e2b-sandbox-recovery.md). The Temporal integration's own surface — permanent activity names, the limited `RunContext`, payload ceilings and child workflows — is in [Pydantic AI on Temporal](pydantic-ai-temporal.md); its streaming, cancellation and continue-as-new behaviour is in [Temporal streaming and cancellation](pydantic-ai-temporal-streaming.md).

## What replay repeats

A step that was in flight when the process died runs again **from its start**, so a tool with side effects has to be safe to repeat — for example by passing an idempotency key to the API it calls[^pydantic-production-docs] A replay that skips completion is a saving; a replay that repeats a payment is the failure mode this rule exists to prevent. The same boundary is described below as the activity you, not the engine, declare; this is the operational instruction that follows from it.

## The engines and their shipping location

The docs table gives the install extra and the symbol that makes an agent durable; where that symbol ships is what decides whose stability policy covers it[^durable-exec-docs]

| Engine | Install | Make an agent durable with | Ships in |
| --- | --- | --- | --- |
| Temporal | `pydantic-ai-slim[temporal]` | `TemporalDurability` (`pydantic_ai.durable_exec.temporal`) | Core, co-maintained |
| DBOS | `pydantic-ai-slim[dbos]` | `DBOSDurability` (`pydantic_ai.durable_exec.dbos`) | Core, co-maintained |
| Prefect | `pydantic-ai-slim[prefect]` | `PrefectDurability` (`pydantic_ai.durable_exec.prefect`) | Core, co-maintained |
| Restate | `restate_sdk[serde]` | `RestateAgent` (`restate.ext.pydantic`) | Restate's own Python SDK, co-maintained |
| AWS Lambda | `pydantic-ai-harness[aws-lambda]` | `AWSLambdaDurability` (`pydantic_ai_harness.aws_lambda`) | [Harness](pydantic-ai-harness.md), co-maintained |
| Absurd | `pydantic-ai-harness[absurd]` | `AbsurdDurability` (`pydantic_ai_harness.absurd`) | Harness, added v2.53.0 |
| pgtask | `pydantic-ai-harness[pgtask]` | `PGTaskDurability` (`pydantic_ai_harness.pgtask`) | Harness, added v2.56.0 |
| Azure Durable Task | `pydantic-ai-harness[azure-durable-task]` | `AzureDurableTaskDurability` (`pydantic_ai_harness.azure_durable_task`) | Harness |
| Apache Airflow | `apache-airflow-providers-common-ai` | `AgentOperator(..., durable=True)` (`airflow.providers.common.ai.operators.agent`) | Airflow's own provider package |

Temporal, DBOS, Prefect, Restate and AWS Lambda are co-maintained by the Pydantic and vendor teams; AWS Lambda, Absurd, pgtask and Azure Durable Task ship in the Harness, while Restate and Airflow ship in the engine's own package[^durable-exec-docs] An engine that ships in the Harness follows the Harness 0.x promise rather than core's stricter policy, so the placement is an upgrade-risk decision, not trivia[^dd-v2-tour-2026]

For an engine outside the table, the durable execution backend builder is documented as a stable surface for third-party runtime authors, and lets them integrate it without importing Pydantic AI internals[^durable-exec-docs]

## One engine per agent

Each agent gets one engine. Since v2.54.0 a second one is refused at construction: building an agent with two durability capabilities raised `UserError` with "An agent can have only one durable execution engine"[^dd-v2-tour-2026]

## DBOS: names become step names

Two requirements are easy to miss. Each agent needs a unique `name`, and each `MCPToolset` needs a unique `id`; DBOS derives step names from those values, so renaming either after deploy breaks in-flight workflows. Function tools registered by the application are not wrapped automatically — any that do I/O must be decorated with `@DBOS.step`[^dd-v2-tour-2026] Since v2.57.0 the waits between continuation polls (Anthropic `pause_turn`, OpenAI background mode) are durable `DBOS.sleep` steps, so recovery skips waits that already finished.

The source's DBOS example also shows the shape of a deployment: `DBOS(config=DBOSConfig(...))` at import time, an agent with `name='support'` and `capabilities=[DBOSDurability()]`, and a `@DBOS.workflow()` wrapper that calls `agent.run(question)`[^dd-v2-tour-2026] The integration's own surface — step identity, what DBOS does and does not wrap, the pickle payload, child workflows, the concurrent-run replay hazard and retry ownership — is in [Pydantic AI on DBOS](pydantic-ai-dbos.md).

## Retry classification reaches the engine

Durability and error typing meet in `non_retryable_model_errors` (v2.59.0): Temporal can be told to stop retrying failures such as a context-window overflow that will never succeed[^dd-v2-tour-2026] The error categories themselves are covered in [Pydantic AI run controls](pydantic-ai-run-controls.md).

## What durability does not give you

Durability keeps one run alive across crashes; it does not store a chat thread between runs, and a conversation round-trip needs only a database column — see [Conversation state](pydantic-ai-conversation-state.md). Graph state is a third case: the [graph builder](pydantic-ai-graph-builder.md) deliberately does not checkpoint between steps.

## Replay instead of snapshots

Temporal's model, as the `pydantic-graph` author describes it, never snapshots application state at all: it records the result of each activity as it completes and re-runs the code to rebuild the state, so a question like "how many of three in-flight state updates had happened" is answered by replay rather than by a serialized checkpoint[^colvin-code-is-graph-2026] Two consequences follow for anyone designing around it. An activity interrupted mid-flight may run twice, and the activity boundary is where **you**, not the engine, declare what touches the outside world and whether a retry is safe[^colvin-code-is-graph-2026] And because the state is the code, any orchestration layer replayed alongside it has to be deterministic too — the argument for keeping model-written choreography as plain Python rather than a node library, in [Code as the agent graph](code-as-agent-graph.md).

The same pattern recurs inside a sandbox: Monty, the interpreter the Harness `CodeMode` capability runs model-written Python in, snapshots the interpreter at each host-function call, which is the sandbox's equivalent of an activity boundary[^colvin-code-is-graph-2026]

## Replay rules that reach your own code

**Reported, version unspecified:** four framework features change shape under replay, and the docs defer each to its owning page[^durable-exec-docs]

- Batched model requests are recorded differently on every engine, so the batch guide is the thing to read before batching under durable execution; the per-engine split — submission and checks as steps or activities, durable versus plain-sleep waits, and the engines that bypass the batch path altogether — is compiled in [batch processing](pydantic-ai-batch-processing.md).
- Append-on-change instructions derive their baseline and replacements from persisted history, yet their callbacks still follow the engine's replay rules: an external read belongs in a durable operation, so replay sees the same values and produces the same history shape.
- Capability authors can move custom hook work into engine activities, steps or tasks with durable capability operations.
- Harness workspace capabilities — `Coder`, `Shell`, `FileSystem` — also run inside a durable agent, with per-engine support in the workspace guide; each workspace call is recorded as a unit of its own.

Which tool calls an engine wraps at all, and how to keep one in workflow code instead, is a separate decision covered in [durable tool placement](pydantic-ai-durable-tool-placement.md).

## Contradictions

Both sources count nine engines and name a different ninth one. The tour lists Kitaru beside Apache Airflow as an additional external SDK integration; the docs list Azure Durable Task in the Harness and never mention Kitaru[^dd-v2-tour-2026][^durable-exec-docs] Neither source is dated precisely enough to say which is current — the tour is dated 2026-10-17 and the docs capture carries no date — so both remain recorded, and the table above follows the docs because it is the vendor's own reference page.

A second, smaller mismatch sits inside the docs: the placement table in "Running a tool outside the durable unit" gives Render Workflows a row, though Render Workflows appears in neither the nine-engine table nor the shipping-location paragraph. Its support and its shipping location are therefore recorded as the placement table states them and nothing more[^durable-exec-docs]

## Limits

- The engine count and the co-maintained/extra classification are the article's reading of the durable-execution docs; no engine integration, vendor SDK, or crash test was exercised in this ingest[^dd-v2-tour-2026]
- The article defers crash and retry behaviour to a separate comparison post, so what actually survives a mid-tool crash is not documented here.
- The one-engine restriction was observed by the author as a construction error, not from release notes.
- The replay-versus-snapshot description is the `pydantic-graph` author's account of Temporal, published on Pydantic's site with no Temporal version named; no workflow was replayed and no activity was interrupted here[^colvin-code-is-graph-2026]
- The docs page names no Pydantic AI, Harness or engine version, gives no author, publication or capture date, and its install extras and symbols are unverified here; every engine page, the backend builder, the batch guide, the custom-capability page and the workspace guide were read as links, not followed[^durable-exec-docs]
- The docs state that engine wrapping and streaming delivery differ per engine but enumerate them only per page, so no claim about a particular engine's coverage is made on this page from that source.
- Evidence class: **Reported**.

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) for attachment.
- **Ships partly in** the [Pydantic AI Harness](pydantic-ai-harness.md), which governs its version stability.
- **Complemented by** [deferred tool approval](pydantic-ai-deferred-approvals.md), which turns a human wait into a serialized pause.
- **Avoids** the mistake of using an engine where [Conversation state](pydantic-ai-conversation-state.md) suffices.
- **Is separated from session storage by** [persistence choices](pydantic-ai-persistence-choices.md), which owns the map of which state belongs to a run, a thread, a person, or the provider.
- **Is the outside-the-sandbox half of** the durability argument in [Code as the agent graph](code-as-agent-graph.md); Monty is its inside-the-sandbox half.
- **Is refined per call site by** [durable tool placement](pydantic-ai-durable-tool-placement.md): which tool calls each engine records as its own unit, and when a tool opts out.[^durable-exec-docs]
- **Runs capability-owned I/O through** `@durable_operation`: a capability's own non-deterministic work moves into an activity, step or task by capability id plus operation name, and the live-value hooks cannot be decorated at all — the dispatch timing, engine-unit rules and `ctx.in_durable_context` split are in [custom capabilities](pydantic-ai-custom-capabilities.md).
- **Constrains** [on-demand capabilities](pydantic-ai-on-demand-capabilities.md): a `ctx.load_capability()` made in an activity, task or step is refused or lost on replay, so the load has to come from workflow code, a capability hook or a tool hook.
- **Is exercised by** [Pydantic AI Harness planning](pydantic-ai-harness-planning.md), whose store reads and writes are journaled capability operations — the concrete case behind the DBOS single-tool-call ordering rule and Temporal's resolve-the-store-from-the-run-context requirement.
- **Is what Harness delegation becomes by default**: a delegation other than to `self` runs in an activity on Temporal and inline on DBOS, so a delegate gets child-workflow durability only through `SetToolMetadata` — the opt-in and its `UserError` cases are in [Harness subagents](pydantic-ai-subagents.md), and the task-control mode that keeps tasks in the workflow is in [subagent task control](pydantic-ai-subagent-tasks.md)[^pydantic-subagents-docs]
- **Reaches tool scheduling through** [Harness background tools](pydantic-ai-harness-background-tools.md): the capability works with Temporal, while under DBOS durable work belongs in an explicit step the background tool calls and `ctx.enqueue()` stays out of a durable activity or task because replay cannot restore it.
- **Rebuilds an environment per unit with** [workspaces](pydantic-ai-workspaces-and-sandboxes.md): a workspace capability attaches next to the durability capability, the run attaches its environment eagerly at start, and a run-level policy wrapper such as `ReadOnlyWorkspace` raises `UserError` because every unit rebuilds from the agent's own capabilities.
- **Has two engines documented at integration depth**: [Pydantic AI on Temporal](pydantic-ai-temporal.md) covers Temporal's naming, context boundary, payload ceiling and activity configuration, with [Temporal streaming and cancellation](pydantic-ai-temporal-streaming.md) for its event delivery and long-run behaviour; [Pydantic AI on DBOS](pydantic-ai-dbos.md) covers DBOS's in-process steps, step identity, child workflows and concurrent-run replay, with [DBOS streaming and cancellation](pydantic-ai-dbos-streaming.md) for its buffered events and workflow-level cancellation.
- **Reaches model-written orchestration through** [dynamic workflows](pydantic-ai-dynamic-workflow.md): a `DynamicWorkflow` script is workflow code, so Temporal replays it against recorded sub-agent results (and a sandbox `max_duration_seconds` can turn replay into a `NondeterminismError`), DBOS serializes every call once any catalog agent carries `DBOSDurability`, and AWS Lambda folds the pre-wait calls into one `parallel` operation.
- **Is given capability-specific rules by the compiled Harness pages**: [memory](pydantic-ai-harness-memory.md) journals each snapshot and requires deterministic resolvers, [ask user](pydantic-ai-harness-ask-user.md) records the answerer's response on AWS Lambda and is refused outright by engines without external-event waits, [prompt injection defender](pydantic-ai-harness-prompt-injection-defender.md) needs an explicit `id` per defender, and [file system](pydantic-ai-harness-filesystem.md), [shell](pydantic-ai-harness-shell.md) and the [Modal](pydantic-ai-harness-modal-sandbox.md)/[E2B](pydantic-ai-harness-e2b-sandbox.md) workspaces each state which events stay live and what a replay re-runs.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Durable execution: nine engines, one line to attach" (raw lines 358–399) for the engine table, shipping locations, the one-engine `UserError`, the DBOS naming and `@DBOS.step` rules, `DBOS.sleep` continuation waits, and the DBOS sample; §"What changed in v2.58 and v2.59" for `non_retryable_model_errors`; §"Example 3" for the engine-versus-thread distinction. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — docs summary plus one observed construction error; no durable engine was run.
[^colvin-code-is-graph-2026]: Samuel Colvin, "The code is the graph", Pydantic, published 2026-10-13T09:00Z, 2,445 words as declared; local capture `raw/the-code-is-the-graph/index.md`, content digest sha256:d8803b5f. §"Typed, snapshotted, parallel: pick two" (raw lines 113–143) for Temporal's replay instead of state snapshots, the at-least-once activity and the declaration of side effects at the activity boundary, and the note that graph machinery is one more thing that must replay deterministically; §"Long live graphs" (lines 145–167) for Monty's host-function boundary as the sandbox's snapshot point. Evidence class: **Reported** — vendor article; no workflow, activity or interpreter was exercised here.
[^durable-exec-docs]: Pydantic, "Durable Execution" (docs.pydantic.dev, `/docs/ai/capabilities/durable_execution/overview/`), 1,028 words as declared; local capture `raw/capabilities/durable_execution/overview/index.md`, content digest sha256:3601b270. Opening paragraphs for when an engine earns its cost, the journal-and-replay mechanism, the per-engine difference in which tool calls are wrapped and how streaming is delivered; the engine table for the nine engines, their install extras, symbols and shipping locations, and the co-maintained division; the paragraph on the stable backend builder for third-party runtime authors; the batched-request, durable-capability-operation, append-on-change-instruction and workspace paragraphs; and the Render Workflows row and Restate/Airflow deferral used in the contradiction. Evidence class: **Reported** — vendor reference page naming no version; no engine, workflow or activity was exercised.
- **Is split into three jobs by** [Pydantic AI production readiness](pydantic-ai-production-readiness.md): this page owns crash recovery inside a run, [Conversation state](pydantic-ai-conversation-state.md) owns the thread between runs, and Harness `StepPersistence` owns resumable snapshots.
- **Constrains** [Pydantic AI deployment shapes](pydantic-ai-deployment-shapes.md): a deploy changes what an in-flight run replays against, so runs drain on the old version or follow the engine's versioning guidance.

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. §"What happens when the process crashes mid-run?" (raw lines 126–132) for the journal-and-replay mechanism, the per-engine difference in which tool calls are wrapped, the in-flight step running again from its start, the idempotency-key advice, and the per-layer retries. Evidence class: **Reported** — vendor documentation; no workflow was crashed, recovered or replayed.

[^pydantic-subagents-docs]: Pydantic Docs, "Subagents", <https://pydantic.dev/docs/ai/harness/subagents/>; local capture `raw/harness/subagents/index.md`, content digest sha256:53a83ad8, 18,887 words as declared (19,277 by `wc -w`), no publication date, author, licence or framework version. Lines 82–99 for `self` running in the Temporal workflow and the `TemporalDurability(models=...)` requirement; lines 464–495 for the child-workflow opt-in, its `SetToolMetadata` form, the `UserError` cases and the uncounted delegate usage; lines 300–308 for the task-control durability limits. Evidence class: **Reported** — vendor documentation; no workflow, activity or Harness package was exercised.
