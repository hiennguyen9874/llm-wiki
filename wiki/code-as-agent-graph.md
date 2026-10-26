---
type: Concept
title: Code as the agent graph
description: Samuel Colvin's argument that a graph library is the wrong runtime for agents — the call stack already is the graph, durability belongs to replay, and Monty's host-call boundary is the snapshot graph libraries cannot find.
tags: [ml, pydantic-ai, agents, orchestration, durability]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T05:05:00Z }
stale_after: 2026-12-23
sources:
  - id: colvin-code-is-graph-2026
    resource: ../raw/the-code-is-the-graph/index.md
    scope: ../raw/the-code-is-the-graph/
    kind: article
    revision: sha256:d8803b5fa767d23f0a03bda63f364781d1f1f476ba4e3d243f33e05dea5f21be
    title: "The code is the graph"
---

Samuel Colvin, the author of `pydantic-graph`, argues that a graph library is the wrong runtime for an agent: the program's own call stack already holds the graph, so a node-and-edge library adds a second representation of state that then has to be kept consistent with the code. Only two of the three properties a graph agent wants — type safety, parallel execution, and snapshot resumption — can hold at once, so durability belongs to an engine that replays code (Temporal) or, inside a sandbox, to an interpreter whose host-call boundary is the snapshot (Monty)[^colvin-code-is-graph-2026]

## The thesis

The article's summary claim is that "graph libraries are a mistake" and that code gives type safety from type hints, parallel execution from async, and durable execution from Temporal outside the sandbox and Monty inside it[^colvin-code-is-graph-2026] The author is arguing against a specific position: that prompting is over, that agents should be built from graphs and loops, and that graph engineering becomes the default architecture for serious agentic systems.

He grants half of it. Writing the code goes away; the developer's job becomes formulating the problem — choosing the metrics an agent should optimize and the constraints it must respect, writing the evals that measure them, and making iteration fast[^colvin-code-is-graph-2026] The architectural half he rejects, with the concession that a graph is still the right shape for a workflow a human wired up in advance: for agents, the control flow is rarely known before the run, so a fixed graph is "a prompt with extra steps", and the real unit of work is a loop with a check in it, designed around the task[^colvin-code-is-graph-2026]

## The call stack already is the graph

| Code construct | Graph meaning |
| --- | --- |
| `if` | a branch |
| `for` | a loop |
| a function call | an edge |
| `except` | the failure edge |
| a `for` around a `try` | a retry |
| `await asyncio.gather(...)` | a fan-out and a join |

The formal name is structured control flow[^colvin-code-is-graph-2026] The call stack records where the run is and a stack trace records how it got there, and that structure already has a debugger, a profiler, a type checker, and every programmer and model as prior knowledge. A graph library rebuilds the same thing worse: nodes become functions you cannot call, edges become registration calls, state becomes a dict merged by reducers or a dataclass mutated at moments you do not control instead of a local variable, and "where is the run right now" is answered by the library's iterator rather than by a trace in an observability tool[^colvin-code-is-graph-2026]

The article makes the comparison concrete with its own documentation example, a five-element fan-out written in the `GraphBuilder` API — `@g.step` functions, a `g.join(reduce_list_append, initial_factory=list[int])`, four `g.edge_from(...).to(...)` registrations and `g.build()` — against the same program as `await asyncio.gather(*(square(n) for n in [1, 2, 3, 4, 5]))`. Both print `[1, 4, 9, 16, 25]`. The second is typed with nothing added, accepts a `breakpoint()`, and fans out in one line[^colvin-code-is-graph-2026] The graph API is not discarded entirely: the diagram is the thing you draw *about* the code, which is why `pydantic-graph` renders Mermaid.

## Typed, snapshotted, parallel: pick two

The article frames an agent-graph library's wish list as a three-way trade-off it calls "a CAP theorem for graphs"[^colvin-code-is-graph-2026]:

1. **Type safety** — the checker catches node A handing node B something it cannot take; a node reads and writes state as an ordinary object and its return type is the edge out.
2. **Parallel execution** — more than one node in flight at once, so branches can fan out and join.
3. **Snapshots** — at a node boundary the whole run is a value that serializes, and resuming from it gives the same result as never having stopped.

No API the author has found gives all three, and after building one he does not think it can be done. The three real systems sit on the corners[^colvin-code-is-graph-2026]:

| Corner given up | System | What it does instead |
| --- | --- | --- |
| Type safety | LangGraph | Nodes return state updates, a checkpoint is written after every super-step, and concurrent writes to one key are merged by a reducer declared in an `Annotated` hint — or the graph raises |
| Parallelism | Original `pydantic-graph` | `FullStatePersistence` saved the state and the one next node, and only one node ran at a time |
| Snapshots | `pydantic-graph` today | Typed and parallel, with `pydantic_graph.persistence` removed in V2 and durability delegated to an engine |

The mechanism behind the loss is worth stating because it is the reusable part. In the original design the snapshot was literally `NodeSnapshot(state, next_node)` — the state plus where we are — which worked only because "where we are" was one node. Add parallelism and "where we are" becomes a set of in-flight nodes and half-filled joins while several of those nodes mutate the one state object, so there is no moment at which the state is a coherent value except a barrier where nothing is in flight[^colvin-code-is-graph-2026] Snapshotting only at barriers loses the whole step on a crash, and a node that wrote half its changes in place has already corrupted the state with no undo. Re-running the in-flight nodes is not available either: the runner cannot know whether a node touched the outside world, or whether doing it twice is harmless — "it sent the email or it didn't, and the graph can't tell"[^colvin-code-is-graph-2026]

The consequence is the part that costs the types. To snapshot under parallelism, nodes must stop writing state and return a description of a change that the runtime applies at a commit point. Two nodes' changes then arrive in no fixed order, so the application has to be order-independent: one merge rule per field, declared outside the node code. A type checker can verify the rule's signature; it cannot verify the rule is commutative, and it cannot verify the state's cross-field invariants hold after two partial updates land[^colvin-code-is-graph-2026] Joining outputs is fine — `gather` returns a typed tuple — and joining state is the problem, because no type system checks a semantic merge.

## How durability escapes the triangle

**Temporal** never snapshots application state at all. It records the result of each activity as it completes and re-runs the code to rebuild the state, so "how many of the three updates had happened" is answered by replaying the code rather than by a serialized checkpoint. An activity interrupted mid-flight may run twice, and the activity boundary is where you, not the runner, declare what touches the outside world and whether it is safe to retry[^colvin-code-is-graph-2026] That is the same role the wiki records for durability engines in general — see [Pydantic AI durable execution](pydantic-ai-durable-execution.md) — with the graph machinery adding one more thing that has to replay deterministically.

**Monty** is the same answer inside the sandbox, where no Temporal is available. The interpreter holds no operating-system resources — no sockets, no file descriptors, no threads — so every parallel branch of the script is a host function the sandbox is waiting on. At the moment it pauses, everything in flight is outside the interpreter, and the interpreter itself, heap and call stack included, is a coherent value a few kilobytes long[^colvin-code-is-graph-2026] That is the barrier the graph libraries could not find, and code gets it free: the only state is local variables and the only places anything crosses the boundary are the calls you wrote.

The resulting semantics:

- A `gather` over three sub-agents pauses as **one snapshot with three pending calls**, and resuming it — in another process if you like — means handing back their results[^colvin-code-is-graph-2026]
- The host function remains where you decide what touches the outside world and whether running it twice is safe, exactly as an activity does under Temporal[^colvin-code-is-graph-2026]
- The join is a line of Python, so it is typed, and the state is the interpreter, so it snapshots — the two corners the triangle said could not be held together[^colvin-code-is-graph-2026]

## Agents that write the graph

The article's practical case is that the graph author is now a model, which needs somewhere to run code no human read first without handing over the filesystem and network. Monty's only exit is a function the host registered; there is no container to start and no network call, so the graph can be rewritten on every turn[^colvin-code-is-graph-2026]

The [Pydantic AI Harness](pydantic-ai-harness.md) is reported to work this way already. Each sub-agent is an async function, the orchestrator gets one tool, `run_workflow`, and writes the choreography itself: an `asyncio.gather` over two `reviewer` calls followed by a `summarizer` call. Retries and voting are ordinary Python — a `for` around a `try`, a list comprehension over results — and only the last value returns to the model's context. The script is type-checked against the sub-agent signatures first, so a misspelled function or a wrong-typed argument is rejected before any sub-agent runs[^colvin-code-is-graph-2026] Attaching Temporal to the orchestrator and to the sub-agents whose model calls should be activities replays that same script against recorded results without changing it.

The supporting example is Prime Intellect's rewrite of Prime Agent from TypeScript to Rust: more than 2,000 agents over two weeks, a result "roughly 14x faster", orchestrated by a root agent that sorted work into a topological order and wrote no product code, with each task passing through a planner, an implementer, a reviewer and a verifier, and a failed review or verification sending the task back to the implementer. They call it a factory of finite state machines; the author reads the shape as a `for` over tasks with a `while` and a `try` inside[^colvin-code-is-graph-2026]

## The trace is the drawing

Because sub-agents are Pydantic AI agents, each run and model call is an OpenTelemetry span in the orchestrator's trace, in Logfire or any other backend, and the fan-out, the join and every retry appear nested the way the code was written[^colvin-code-is-graph-2026] That is the article's answer to graph visualization: the graph worth looking at is the one the run actually took, not the one someone drew beforehand, so agent observability needs no graph visualizer — see [Pydantic AI observability](pydantic-ai-observability.md) for the span tree this rests on.

## What survives of graphs

The recommendation is to keep drawing graphs — in design docs, rendered from code, to explain a run after the fact — and not to execute them. The runtime for a graph already exists, it is the one the language ships with, and when the author of the graph is a model the thing to hand it is Monty rather than a library of nodes[^colvin-code-is-graph-2026]

## Contradictions

- **LangGraph as the answer for checkpointed graph state.** A third-party tour of the Pydantic AI docs records that if checkpointed, resumable graph state is the core abstraction a project wants, LangGraph's checkpointer model is built around exactly that and is a reasonable choice — a position the wiki carries in [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md) and [graph builder](pydantic-ai-graph-builder.md). This article argues the opposite: that the checkpointed-graph shape is a mistake at any size, because the state merge it forces cannot be typed, and durability should come from replaying code instead[^colvin-code-is-graph-2026] Neither is chosen here. They answer different questions — which library fits a given abstraction, versus whether that abstraction should be adopted — but they cannot both guide the same architecture decision, and only this source argues the second question at length.
- **Retracting versus narrowing `pydantic-graph`.** The same article says graph libraries are a mistake while `pydantic-graph` continues to ship as a typed state machine whose diagrams are rendered from code. Read as a scope claim it is consistent: the library covers typed control flow, and durability is delegated. Read as an architecture verdict it would deprecate the library it describes. The article does not resolve which reading applies to a human-wired workflow, which it separately concedes is a real shape.

## Limits

- The source is a vendor argument by the framework's own author, published on Pydantic's site, and the author states his own prior dislike of LangGraph as a possible bias before arguing past it[^colvin-code-is-graph-2026] No independent source, benchmark, or competing implementation was inspected here.
- It **names no version** for Pydantic AI, `pydantic-graph`, Monty, Temporal or LangGraph, so every API name and behaviour claim is version-unknown; under the `pydantic-ai` domain rule the page is `draft`, and the architectural argument it carries is the durable part.
- The LangGraph mechanism — updates instead of mutation, a checkpoint after every super-step, a reducer in an `Annotated` hint, `INVALID_CONCURRENT_GRAPH_UPDATE` when there is none — rests on LangGraph documentation read as a link, not followed, and was not inspected[^colvin-code-is-graph-2026]
- The two example programs, the Harness `run_workflow` script and its type-check-before-run behaviour are as printed in the article; nothing was executed, type-checked, or benchmarked here, so the claim that the plain-Python version type-checks "with nothing added" is the author's[^colvin-code-is-graph-2026]
- No Monty snapshot was taken, sized, resumed or timed; the "few kilobytes" figure and the cross-process resume are reported, not measured[^colvin-code-is-graph-2026]
- The Prime Intellect figures — 2,000+ agents, two weeks, roughly 14x — are that company's own reported result, cited by this source rather than observed by it[^colvin-code-is-graph-2026]
- The article is dated 2026-10-13 and refers to its own FastAPI Conf talk on 2026-10-28 as upcoming, so the capture predates any later revision of the same argument.
- Evidence class: **Reported** for all mechanism and case-study claims; **Synthesis** for the two contradiction readings above.

## Relationships

- **Contradicts** the LangGraph recommendation carried by [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md) and [Pydantic AI graph builder](pydantic-ai-graph-builder.md), as recorded above.
- **Explains** why `pydantic_graph.persistence` was removed in V2, the gap [graph builder](pydantic-ai-graph-builder.md) records without a stated reason.
- **Depends on** [durable execution](pydantic-ai-durable-execution.md): the replay model is what replaces snapshots outside the sandbox.
- **Is implemented by** the [Pydantic AI Harness](pydantic-ai-harness.md) `run_workflow` tool and by Monty, the sandboxed interpreter whose `exec` server [Logfire MCP server](logfire-mcp-server.md) also runs Python in.
- **Motivates** the "no graph visualizer" reading of [Pydantic AI observability](pydantic-ai-observability.md): the span tree is the graph.

[^colvin-code-is-graph-2026]: Samuel Colvin, "The code is the graph", Pydantic, published 2026-10-13T09:00Z, 2,445 words as declared; local capture `raw/the-code-is-the-graph/index.md`, content digest sha256:d8803b5f. §"TL;DR" (raw lines 13–17) for the three-way claim and Monty's placement; §"Introduction" (lines 19–41) for the concession about human-written code going away, the metrics/constraints/evals job, the `review_comments` fan-out-and-branch function, the "only graph that works is code itself" thesis and the LangGraph bias disclosure; §"Every graph fights the call stack" (lines 43–111) for the code-to-graph mapping, structured control flow, the graph library's worse rebuild, the `GraphBuilder` versus `asyncio.gather` comparison with its `[1, 4, 9, 16, 25]` output, the Mermaid-rendering concession, and "a prompt with extra steps"; §"Typed, snapshotted, parallel: pick two" (lines 113–143) for the three properties, `NodeSnapshot(state, next_node)`, the parallel-snapshot incoherence argument, the email/undo/re-run problem, the commit-point and reducer design, the semantic-merge limit, the three corners with `FullStatePersistence` and the removal of `pydantic_graph.persistence`, and the David Montague quote; §"Long live graphs" (lines 145–167) for Temporal replay and activity boundaries, Monty's no-OS-resource property, the few-kilobyte interpreter snapshot, the three-pending-call resume, the host function as side-effect boundary, Prime Intellect's TypeScript-to-Rust rewrite with its 2,000+ agents and ~14x figure, the "factory of finite state machines" description, the Harness `run_workflow` example with its type-check-before-run rule and Temporal attachment, and the OTel span nesting; §"Keep drawing graphs" (lines 169–173) for the draw-don't-execute recommendation. Evidence class: **Reported** — a vendor article by the framework's author; no code was executed, no snapshot taken or resumed, no framework inspected.
