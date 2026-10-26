---
type: Concept
title: Pydantic AI graph builder
description: pydantic-graph's typed GraphBuilder for fan-out, joins and decisions, and its deliberate lack of persistence compared with checkpointing frameworks.
tags: [ml, pydantic-ai, agents, orchestration]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:03:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

Most Pydantic AI agents should stay a single loop; when a workflow needs explicit fan-out, joins, or decisions, `pydantic-graph`'s `GraphBuilder` supplies typed steps and type-checked edges. In V2 the builder API became the top-level `pydantic_graph` API, replacing `pydantic_graph.beta` imports[^dd-v2-tour-2026]

## How a graph is declared

Each step declares `StepContext[State, Deps, Input]`, and edges are checked against those types. A `GraphBuilder(state_type=..., input_type=..., output_type=...)` collects `@g.step` functions, then `g.edge_from(g.start_node).to(a, b, c)` broadcasts to parallel steps and `g.join(reduce_list_append, initial_factory=list[str])` reduces their outputs before `g.end_node`. `.map()` on an edge spreads an iterable across parallel tasks instead of broadcasting the same input[^dd-v2-tour-2026]

```python
g = GraphBuilder(state_type=ReviewState, input_type=str, output_type=list[str])

@g.step
async def lint(ctx: StepContext[ReviewState, None, str]) -> str: ...

collect = g.join(reduce_list_append, initial_factory=list[str])
g.add(
    g.edge_from(g.start_node).to(lint, security, tests),
    g.edge_from(lint, security, tests).to(collect),
    g.edge_from(collect).to(g.end_node),
)
graph = g.build()
findings = await graph.run(state=ReviewState(repo='api'), inputs='PR-981')
```

The example printed all three findings and then a Mermaid `stateDiagram-v2` from `graph.render(title='review', direction='LR')`, which inserted a `broadcast` fork state and a `reduce_list_append` join state on its own. `render()` therefore doubles as documentation of the topology the builder inferred[^dd-v2-tour-2026]

## No checkpointing by design

V2 removed `pydantic_graph.persistence`, so the builder does not snapshot graph state between steps. Persistence is delegated to Harness `StepPersistence` or a [durable engine](pydantic-ai-durable-execution.md). The source's framing is that if checkpointed, resumable graph state is the core abstraction a project wants, LangGraph's checkpointer model is built around exactly that and is a reasonable choice for that shape of problem[^dd-v2-tour-2026]

That is a scope statement rather than a gap: one agent loop plus capabilities covers most agent work, and the graph layer covers control flow, not state ownership.

## Limits

- The graph example was type-checked and run by the author, but not by this ingest; the printed output and Mermaid diagram are the article's report[^dd-v2-tour-2026]
- No performance, scale, or error-handling behaviour of graphs is documented in this capture.
- The LangGraph recommendation is positioning, not a measured comparison.
- Evidence class: **Reported**.

## Relationships

- **Complements** the agent loop described in [Pydantic AI v2 release](pydantic-ai-v2-release.md).
- **Delegates** persistence to [durable execution](pydantic-ai-durable-execution.md) and Harness `StepPersistence`.
- **Contrasted with** LangGraph in [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md).

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"pydantic-graph: typed control flow when one loop is not enough" (raw lines 400–481) for the top-level import, `StepContext` typing, broadcast and join edges, `.map()`, the `graph.render()` Mermaid output, and the removal of `pydantic_graph.persistence`; §"What changed in V2, in one table" for the `pydantic_graph.beta` to `pydantic_graph` import change. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — an author-run example reported secondhand; nothing was executed here.
