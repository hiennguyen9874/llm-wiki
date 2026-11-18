---
type: Concept
title: pydantic-graph core library
description: How pydantic-graph models a workflow as typed nodes — BaseNode classes whose run return annotation is the outgoing edge, End to finish, optional state and deps on GraphRunContext, and a GraphBuilder that discovers and renders the graph.
tags: [pydantic-ai, ml, agents, orchestration]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:20:00Z }
stale_after: 2027-01-17
sources:
  - id: pydantic-docs-graph-2026
    resource: ../raw/graph/graph/index.md
    scope: ../raw/graph/graph/
    kind: documentation
    revision: sha256:22e3c49dae90e663dc1ec7f2da567ad6ce5f16b633ced20fe473c7372a23ab6b
    title: "Graphs"
---

`pydantic-graph` is an async graph and state-machine library where nodes and edges come from Python type hints: a node is a `BaseNode` subclass whose `run` method's return annotation names its successors, so the graph topology lives in the type signature rather than in a separate edge list. The library is developed alongside Pydantic AI but has no dependency on `pydantic-ai` and stands alone as a pure graph-based state machine, usable with or without GenAI[^pydantic-docs-graph-2026]

The vendor's own positioning is a caution as much as an invitation: reach for it when control flow is the hard part — explicit states, branches and resumable transitions you want typed and diagrammed — because for most agents plain Python plus the [multi-agent patterns](https://pydantic.dev/docs/ai/guides/multi-agent-applications/) is the shorter road[^pydantic-docs-graph-2026] That is the same scope statement [the graph builder page](pydantic-ai-graph-builder.md) records from the V2 tour, now from the library's own documentation.

## Nodes are classes, edges are return types

A node is generally a `dataclass` holding the parameters needed to construct it, plus a `run` method whose return annotation `pydantic-graph` reads to determine outgoing edges. A node that cannot finish the run returns only successor nodes and omits the return-type generic; a node that can finish returns a union such as `AnotherNode | End[int]` and must declare it[^pydantic-docs-graph-2026]

`BaseNode` is generic in three parameters, in positional order: the **state** type (`None` for a graph without state, and it must match the graph's state type), the **deps** type (`DepsT` defaults to `object`, which fits any graph), and the **graph return type** (`RunEndT` defaults to `Never`). Because the parameters are positional-only, widening a node to return `End[int]` forces the deps slot to be written explicitly — `BaseNode[MyState, object, int]` — even when the node uses no deps[^pydantic-docs-graph-2026]

## State and deps travel with the run

State is optional and exists to carry one mutable object — often a `dataclass` or Pydantic model — through the graph, mutated by nodes as they run. Nodes reach it as `ctx.state` off the `GraphRunContext`, the per-run context that also holds deps and mirrors Pydantic AI's `RunContext`; the initial object is passed at `graph.run(state=state)`, so the caller keeps the reference and can read the accumulated result afterwards. The documented sample is a vending machine whose `MachineState` holds a balance and a selected product, with `Purchase` either ending the run or routing back to `InsertCoin` or `SelectProduct` depending on the balance and the product lookup[^pydantic-docs-graph-2026]

Dependency injection is configured by `deps_type` on the `GraphBuilder`, parameterizing each node subclass with the deps type, and read as `GraphRunContext.deps` inside `run()` or `StepContext.deps` inside step functions. The documented example wraps a `ProcessPoolExecutor` in a `GraphDeps` dataclass and awaits `loop.run_in_executor(ctx.deps.executor, ...)` inside a node — contrived, the docs concede, because the executor buys nothing on that workload[^pydantic-docs-graph-2026]

## From nodes to a runnable graph

`GraphBuilder` is the assembly point and is generic in state (`StateT`), deps (`DepsT`), input (`InputT`) and output (`OutputT`). `g.build()` returns the executable `Graph`; `graph.run()` is async and returns the raw output value that `End` carried, and `graph.iter()` replaces `run()` when each step must be inspected, the next step overridden, or the loop driven by hand[^pydantic-docs-graph-2026] Broadcast, join, map and decision wiring on that builder are covered in [the graph builder page](pydantic-ai-graph-builder.md), which this page does not repeat.

Two registration routes exist. `g.add_reachable(RootNode)` walks outward from one or more roots, inferring edges from `run` return annotations and from paths already configured through steps, decisions, joins, broadcasts and maps: existing outgoing paths are preserved and annotations only fill in `BaseNode` classes that have none, so bridge paths must be configured **before** the call; only roots-reachable nodes are inspected; cycles, duplicate roots and repeated calls do not duplicate inferred edges; and registration never instantiates a node, so `run` bodies and the start step still construct nodes with their own arguments. Registering single classes instead takes `g.add(g.node(A), g.node(B))`. Whichever route is used, `g.start_node` is wired explicitly (`g.edge_from(g.start_node).to(start)` with a `@g.step`-decorated start step), and discovery must be complete before `g.build()`[^pydantic-docs-graph-2026]

## Splitting nodes across modules

Because a node's `run` return annotation names its successor classes, nodes that route to each other would import each other. The documented workaround is `from __future__ import annotations` plus importing the sibling *module* rather than its class (`from . import second`, annotated `-> second.Second`): the annotation is a string until it is resolved at `g.node()` or `g.add_reachable()` time, and the `run` bodies execute later still, so no module reads the other's class during its own import. Importing the class directly (`from .second import Second`) fails with a circular `ImportError`. For independent tasks whose routing belongs in the composition root, the docs prefer ordinary step functions registered with `g.step(imported_function)` and connected there, which keeps the function's module free of the builder[^pydantic-docs-graph-2026]

## Diagrams are the byproduct

`print(graph)` or `graph.render()` emits Mermaid `stateDiagram-v2` source, and `direction` (`'TB'`, `'LR'`, `'RL'`, `'BT'`) controls layout. Union return types appear as `state <<choice>>` decision states, and the start step appears as the entry state, so the rendered diagram is a reading of the annotations rather than a hand-maintained drawing[^pydantic-docs-graph-2026]

## Packaging

`pydantic-graph` is a required dependency of `pydantic-ai` and an optional dependency of `pydantic-ai-slim`, and installs directly as `pip install pydantic-graph`[^pydantic-docs-graph-2026]

## Limits

- The capture names no `pydantic-graph` or Pydantic AI version, no publication date, author or licence, so under the `pydantic-ai` domain rule this page is `draft` and every API name is version-unknown[^pydantic-docs-graph-2026]
- Every claim is **Reported**: no package was installed, node constructed, graph built, run, iterated or rendered here.
- The `graph.iter()` iteration model and the full rendering options live in the graph builder docs, which were read as links, not followed[^pydantic-docs-graph-2026]
- The capture is silent on persistence, checkpointing, failure handling and concurrency limits; [the graph builder page](pydantic-ai-graph-builder.md) and [Code as the agent graph](code-as-agent-graph.md) carry the recorded position that `pydantic-graph` snapshots nothing and leaves durability to an external engine.
- The GenAI example pins `google:gemini-4-argon` and `openai:gpt-6.1-sol`, model names nothing else in this wiki corroborates, and its printed `Email(...)` output is not a measurement[^pydantic-docs-graph-2026]

## Relationships

- **Uses** [the graph builder](pydantic-ai-graph-builder.md) for the step, broadcast, join and map edges this page treats only as registration targets.
- **Contrasted with** [Code as the agent graph](code-as-agent-graph.md), the library author's argument that the call stack already is the graph.
- **Delegates** durability to [durable execution](pydantic-ai-durable-execution.md), since the library provides no snapshots of its own.
- **Complements** [Pydantic AI dependencies](pydantic-ai-dependencies.md): both pass a deps object per run through a context, and the `GraphRunContext` mirror of `RunContext` is the read in a node or step.

[^pydantic-docs-graph-2026]: Pydantic, "Graphs", Pydantic Docs (`https://pydantic.dev/docs/ai/graph/graph/`), language `en`, 2,839 words as declared and 2,871 by local `wc -w`, no publication date, author, licence or library version; local capture `raw/graph/graph/index.md`, content digest sha256:22e3c49d. §"Graphs" (raw lines 9–17) for the type-hint framing, the no-dependency statement, the typed-and-diagrammed positioning and the plain-Python advice; §"Installation" (lines 19–31) for the dependency relationship and `pip install pydantic-graph`; §"GraphRunContext" and "End" (lines 36–47); §"Nodes" (lines 48–119) for dataclass fields, the `run` method as edge source, the three generics with `object`/`Never` defaults, and the positional-only consequence (line 116); §"Graph" (lines 120–213) for the `GraphBuilder` generics, `/graph_example.py`, and the printed `stateDiagram-v2` with `<<choice>>` states; §"Registering reachable nodes" (lines 214–225, especially 222 and 224); §"Nodes in separate modules" (lines 226–261, circular-import rule at 258); §"Stateful Graphs" (lines 262–422, state definition at 264); the GenAI example (lines 423–561); §"Iterating Over a Graph" (lines 562–565); §"Dependency Injection" (lines 566–638); §"Mermaid Diagrams" (lines 639–642) for `direction`. Evidence class: **Reported** — vendor documentation; nothing was executed.
