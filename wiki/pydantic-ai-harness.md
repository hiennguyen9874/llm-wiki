---
type: Concept
title: Pydantic AI Harness
description: First-party Pydantic AI package of agent batteries — Coder, memory, guardrails, context management, approvals, code mode, and durability integrations — kept outside a deliberately small core.
tags: [ml, pydantic-ai, agents, llm-frameworks]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T13:10:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-ai-v2
    resource: ../raw/pydantic-ai-v2/index.md
    scope: ../raw/pydantic-ai-v2/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2: capabilities, a leaner core, and the Harness"
  - id: vstorm-v2-blog
    resource: ../raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md
    scope: ../raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2 and the road to production-grade agentic AI"
  - id: alphasignal-v2-news
    resource: ../raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/index.md
    scope: ../raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work"
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: pydantic-image-gen-2026
    resource: ../raw/image-generation/index.md
    scope: ../raw/image-generation/
    kind: article
    revision: sha256:2563fee14c8dd9209912c64e26cb10d888eb54d1e0d027343f546fe21ceaf69e
    title: "Generate images with Pydantic AI"
  - id: pydantic-vs-claude-sdk-2026
    resource: ../raw/pydantic-ai-vs-claude-agent-sdk/index.md
    scope: ../raw/pydantic-ai-vs-claude-agent-sdk/
    kind: article
    revision: sha256:e13b086e39460e61065006caca8d0b4b2502621205a283c70cd66ea1da31974b
    title: "Pydantic AI vs Claude Agent SDK: Who owns the agent?"
  - id: colvin-code-is-graph-2026
    resource: ../raw/the-code-is-the-graph/index.md
    scope: ../raw/the-code-is-the-graph/
    kind: article
    revision: sha256:d8803b5fa767d23f0a03bda63f364781d1f1f476ba4e3d243f33e05dea5f21be
    title: "The code is the graph"
  - id: sanchez-self-improving-2026
    resource: ../raw/when-agents-improve-agents/index.md
    scope: ../raw/when-agents-improve-agents/
    kind: article
    revision: sha256:3a72d59c7e98809d43fbf8b36a3fb77a26fa72444fb698a84bf5eb2229d9f2b2
    title: "When agents improve agents: loops that improve themselves"
---

The **Pydantic AI Harness** is the first-party package of "batteries for your agent" that sits outside the core library: memory, guardrails, context management, file system access, code mode, and more, all delivered as [capabilities](pydantic-ai-capability-primitive.md)[^pydantic-ai-v2] It exists to keep the core small and stable while the surrounding layer moves fast.

## The core / Harness split

| Tier | Contains | Rationale |
| --- | --- | --- |
| Core (`pydantic-ai`) | The agent loop, providers, the capability and hooks API, and only capabilities that need deep provider support or are fundamental to every agent | Small, stable surface |
| First-party Harness | Memory, guardrails, context management, file system access, code mode, and further capabilities | Moves fast without destabilizing core |
| Third-party / your own | Community capabilities, endorsed or self-written | Same capability interface |

A capability can **graduate into core** once it proves broadly essential, so the split is a release-velocity decision rather than a permanent classification[^pydantic-ai-v2] Code mode is named as an early candidate for that graduation[^alphasignal-v2-news]

## Reported capability set

Press coverage describes the following Harness capabilities as "currently available or in progress", so per-item maturity is not established by either capture[^alphasignal-v2-news]:

| Capability | Reported behaviour |
| --- | --- |
| `CodeMode` | Replaces multiple tool calls with one sandboxed code execution, powered by Monty, Pydantic's safe Python subset |
| `ContextManagerCapability` | Real-time token tracking with auto-compression at a configurable threshold |
| `MemoryCapability` | Persistent `MEMORY.md` per agent name |
| `SubAgentCapability` | Spawn, check, and cancel subagents as tools |
| `TodoCapability` | Task planning with subtasks, dependencies, and PostgreSQL persistence |
| `ConsoleCapability` | Filesystem and shell access |

`ConsoleCapability` is the security-relevant entry: a filesystem and shell surface is what turns a chat agent into one that can act on a machine, and neither source documents the isolation properties of a given backend.

A later, v2.59-era inventory names the shipped set more sharply: `Coder` (a full coding-agent stack), `Memory`, `Guardrails`, `Spend Limits`, `Subagents`, `Planning`, `Code Mode` (model-written Python in the Monty sandbox), `Step Persistence` (saved checkpoints that can be resumed or forked without writing save/load code), and `Compaction`, plus the AWS Lambda, Absurd and pgtask durability integrations and the `ApprovalReviewer` and `ToolCallJudge` approval capabilities[^dd-v2-tour-2026] The two lists overlap without matching one-to-one — `ContextManagerCapability` and `ConsoleCapability` do not appear under those names, while `Coder` and `Step Persistence` were absent from the newsroom list — so neither is a complete manifest of a single version.

Sandboxing has since become a core concern rather than a Harness one: `LocalWorkspace` ships in core, sandbox backends (`E2BSandbox`, `SpritesSandbox`, `BubblewrapSandbox`, `SmolSandbox`, `DaytonaSandbox`) are core workspace backends, and v2.59.0's `DaytonaSandbox` runs `Coder`, `Shell`, `FileSystem` and the other Harness capabilities inside a Daytona sandbox[^dd-v2-tour-2026] See [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md).

One further Harness feature is named without detail: media externalization, which moves large payloads out of persisted message history, with storage configured separately — generating an image through [Pydantic AI image generation](pydantic-ai-image-generation.md) does not persist it automatically[^pydantic-image-gen-2026] That is the feature that matters once a `BinaryImage` would otherwise sit in every saved message, but no capture here documents its configuration keys, its trimming policy, or what remains once a payload has been externalized.

## Whole agents you can take apart

Two of the shipped agents are described from the product side rather than as capability names: `Coder` is a complete coding agent with file tools, a shell, repository instructions, delegation and context management, and `Researcher` answers questions from the web with cited sources. Both are built from the same capabilities, so they come apart the way they went together — start from one and remove what the application does not need, or skip both and build your own[^pydantic-vs-claude-sdk-2026] Attaching one is a single entry beside a workspace:

```python
agent = Agent("anthropic:claude-sonnet-4-6", capabilities=[LocalWorkspace("."), Coder()])
```

The same agent can run as a GitHub Agentic Workflow triggered by issues, pull requests or a schedule, with your instructions, tools and model — the vendor's counterpart to a vendor's GitHub Action for its own agent[^pydantic-vs-claude-sdk-2026] This is the Harness being sold as a starting point that survives growth: the small agent is not replaced when the application becomes ambitious.

`Researcher` appears in no other capture here, and neither agent's package, prompt or tool list has been inspected, so both are marketing-level descriptions[^pydantic-vs-claude-sdk-2026]

## Dynamic workflows the model writes

Multi-agent coordination is reported to work through a single tool rather than a graph API. Each sub-agent is an async function, the orchestrator gets one tool, `run_workflow`, and writes the choreography as Python — an `asyncio.gather` over two `reviewer` calls followed by a `summarizer` call, retries and voting as a `for` around a `try` or a comprehension over results[^colvin-code-is-graph-2026] Three properties are claimed for that shape:

- The script is **type-checked against the sub-agent signatures before any sub-agent runs**, so a misspelled function or a wrong-typed argument is rejected up front[^colvin-code-is-graph-2026]
- Only the **last value** returns to the model's context, so intermediate sub-agent output does not accumulate there[^colvin-code-is-graph-2026]
- The script is **plain Python**, so attaching Temporal to the orchestrator and to the sub-agents whose model calls should be activities replays it against recorded results without editing it[^colvin-code-is-graph-2026]

Execution happens in Monty, whose only exit is a function the host registered — no container to start and no network call — which is what makes rewriting the workflow on every turn affordable[^colvin-code-is-graph-2026] The reasoning behind code instead of graphs, including Monty's interpreter-level snapshot, is in [Code as the agent graph](code-as-agent-graph.md); the durability engines the last bullet relies on are in [Pydantic AI durable execution](pydantic-ai-durable-execution.md).

No capture here documents `run_workflow`'s parameters, its return shape, the sub-agent registration API, or what the type check actually enforces.

## Recall across runs

Two capabilities read and write one shared store, which is what lets a later run inspect an earlier one[^sanchez-self-improving-2026] **Conversation search** gives the model a single tool, `search_conversation_history`, running a BM25 search over every run the store has persisted — across sessions and across agents, so an agent can find what another already tried, the tool calls it made, the reasoning it wrote and how it failed[^sanchez-self-improving-2026] **Memory** adds a notebook that survives the run[^sanchez-self-improving-2026] The write half is `StepPersistence`, the same saved-checkpoint capability listed above, pointed at a history source rather than at a resume path:

```python
from pydantic_ai_harness.conversation_search import ConversationSearch, SnapshotHistorySource
from pydantic_ai_harness.step_persistence import SqliteStepStore, StepPersistence

store = SqliteStepStore(database='sessions.db')
agent = Agent('anthropic:claude-opus-4-8', capabilities=[
    StepPersistence(store=store),
    ConversationSearch(SnapshotHistorySource(store)),
])
```

The stated limit is scope: search spans the whole store rather than a rank, so a sub-agent cannot be handed only the histories at or below its own level, and the choice is all runs or one conversation[^sanchez-self-improving-2026] The capability ships; per-rank access control is described as future work[^sanchez-self-improving-2026] Neither the store schema, the snapshot policy nor the ranking is documented in that capture, so the isolation question a shared multi-tenant store raises is open here.

## Ecosystem and dogfooding

- Community capabilities already exist; the article names VStorm as one provider whose capabilities Pydantic endorses and links from the Harness capability matrix, with work underway to upstream them[^pydantic-ai-v2]
- The wiring is concrete, not just a link: per Vstorm's account of the Harness README, the reference example attaches `pydantic_ai_summarization` for context management and `pydantic_deep` for memory and stuck-loop detection[^vstorm-v2-blog] See [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md) for the third-party tier as a whole.
- The Harness is where the maintainers said they were concentrating effort at publication: a wave of new capabilities plus a headless coding agent built on Pydantic AI, dogfooded across Pydantic's own repositories[^pydantic-ai-v2]

## Packaging consequence

Because the long tail of provider integrations is opt-in in v2 while OpenAI, Anthropic, and Google ship by default, Harness-style capabilities are the main way to add capability breadth without pulling providers you do not use — see [Pydantic AI v2 release](pydantic-ai-v2-release.md)[^pydantic-ai-v2]

## Install and version policy

The Harness installs separately (`uv add pydantic-ai-harness`) and uses **0.x versioning**: minor releases may include breaking changes, patch releases will not[^alphasignal-v2-news] That marks the tier as pre-1.0 even while core v2 is stable, and it matches the stated reason for the split — Harness capabilities iterate without core's backward-compatibility guarantees.

The Harness's own policy adds the operational detail: APIs may move between minor releases "always with deprecation warnings where practical", every breaking change is documented in release notes with migration guidance, and patch releases will not intentionally break existing behaviour. The stated consequence is to pin the exact version, read release notes before upgrading, and keep relied-on capabilities under test — including the durability engines that ship in this tier[^dd-v2-tour-2026]

## Limits

- The capability lists above come from a newsroom restatement and a third-party tour; no Harness package, README, or repository was inspected, and per-item maturity is still not established[^dd-v2-tour-2026]
- Individual capability APIs, configuration keys, and dependency footprints are not documented here.
- `TodoCapability`'s PostgreSQL persistence and `MemoryCapability`'s `MEMORY.md` imply external state, but no capture says how that state is migrated or isolated between agents.
- `Coder`'s prompt caching default and the sandbox isolation properties are reported, not measured.
- The `run_workflow` description is a vendor article's sketch of a feature of its own package, names no Harness or Pydantic AI version, and was not executed; neither the tool's signature nor the type-checking mechanism is documented[^colvin-code-is-graph-2026]
- Evidence class: **Reported**.

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md): every Harness battery is attached as a capability.
- **Part of** the [Pydantic AI v2 release](pydantic-ai-v2-release.md) story: the split is what lets core stay lean.
- **Includes** endorsed third-party capabilities, documented from the provider side in [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md).
- **Hosts** [deferred tool approval](pydantic-ai-deferred-approvals.md) capabilities and three of the nine [durable execution](pydantic-ai-durable-execution.md) engines, which is why its 0.x policy reaches deployment risk.
- **Supplies the whole agents** — `Coder` and `Researcher` — that [Claude Agent SDK versus Pydantic AI](claude-agent-sdk-vs-pydantic-ai.md) compares with a bundled coding agent, and the sandbox backends that page swaps in.
- **Defines the boundary with** core [workspaces](pydantic-ai-workspaces-and-sandboxes.md) and the [capability primitive](pydantic-ai-capability-primitive.md).
- **Runs model-written choreography through** [Code as the agent graph](code-as-agent-graph.md): `run_workflow` and `CodeMode` both execute Python in Monty instead of walking a node graph.
- **Supplies the recall half of** [Self-improving agent loops](self-improving-agent-loops.md): `StepPersistence` writes the runs, `ConversationSearch` reads them back, and the check at the edge of idle is the capability this tier does not ship.

[^pydantic-ai-v2]: Douwe Maan, "Pydantic AI v2: capabilities, a leaner core, and the Harness", Pydantic, published 2026-06-23, §"The Harness and a leaner core" (split rationale, community capabilities, June focus) and §"One primitive: the capability" for the `pydantic_ai_harness` `CodeMode` import. Local capture: `raw/pydantic-ai-v2/index.md` (revision 836bd3b1). Evidence class: **Reported**; no Harness package, source tree, or capability matrix was inspected in this ingest, so tier membership and maturity are the maintainer's description only.
[^vstorm-v2-blog]: Nicholas Berryman, "Pydantic AI v2 and the road to production-grade agentic AI", Vstorm, published 2026-07-03, §"Where Vstorm fits: endorsed, linked, and upstreaming" (the Harness README's use of `pydantic_ai_summarization` and `pydantic_deep`). Local capture: `raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md` (revision 836bd3b1). Evidence class: **Reported** — secondhand description by a partner; the Harness README and packages were not inspected.
[^alphasignal-v2-news]: AlphaSignal Newsroom, "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work", AlphaSignal, published 2026-06-23, §"The Harness: batteries for your agent" (capability list, graduation of code mode, the core/Harness split rationale) and §"Getting started and migrating from v1" (`uv add pydantic-ai-harness`, 0.x policy). Local capture: `raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/index.md` (revision 836bd3b1). Evidence class: **Reported** — no Harness package or repository was inspected.
[^pydantic-image-gen-2026]: David Sanchez, "Generate images with Pydantic AI", Pydantic, published 2026-09-14, §"Why we added image generation" (raw lines 87–102) for the Harness media-externalization reference, and §"Let an agent generate the image" for the non-persistence of generated images. Local capture: `raw/image-generation/index.md`, content digest sha256:2563fee1. Evidence class: **Reported** — vendor announcement; no Harness package was inspected.
[^pydantic-vs-claude-sdk-2026]: Aditya Vardhan, "Pydantic AI vs Claude Agent SDK: Who owns the agent?", Pydantic, published 2026-10-05, §"Pydantic AI grows with your application" (raw lines 69–101) for `Coder` (file tools, shell, repository instructions, delegation, context management), `Researcher` (web answers with cited sources), the composability claim, the `capabilities=[LocalWorkspace("."), Coder()]` snippet and GitHub Agentic Workflows. Local capture: `raw/pydantic-ai-vs-claude-agent-sdk/index.md`, content digest sha256:e13b086e. Evidence class: **Reported** — a vendor article naming no Pydantic AI release version and linking, not quoting, the Harness documentation.
[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"The mental model: an agent loop plus capabilities" (raw lines 98–120) for the core/Harness split and the v2.59-era Harness inventory; §"What changed in V2, in one table" for the 0.x policy wording and the durability placement; §"Workspaces: one API for local and sandboxed tools (v2.52)" for `DaytonaSandbox` running Harness capabilities; §"Caching is now one switch (v2.55)" for the `Coder` caching default. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — a third-party tour; no Harness package, README, or capability matrix was inspected.
[^sanchez-self-improving-2026]: David Sanchez, "When agents improve agents: loops that improve themselves", Pydantic, published 2026-07-31T12:00Z; local capture `raw/when-agents-improve-agents/index.md`, content digest sha256:3a72d59c. §"Learning from its own runs" (raw lines 31–59) for the `search_conversation_history` tool, the BM25 search across sessions and agents, `Memory`, the whole-store-versus-rank scope limit, and the `StepPersistence`/`ConversationSearch` snippet; §"The loop supplies its own continue" (lines 25–27) for the output-guardrail `retry` verdict and Macroscope. Evidence class: **Reported** — vendor article; no Harness package, store or search was exercised.

[^colvin-code-is-graph-2026]: Samuel Colvin, "The code is the graph", Pydantic, published 2026-10-13T09:00Z, 2,445 words as declared; local capture `raw/the-code-is-the-graph/index.md`, content digest sha256:d8803b5f. §"Long live graphs" (raw lines 145–167) for the Harness dynamic-workflow description, the single `run_workflow` tool, the two-`reviewer`-then-`summarizer` script, type-checking against sub-agent signatures before any sub-agent runs, only the last value returning to context, retries and voting as ordinary Python, the Temporal attachment without script changes, and Monty's host-function-only exit. Evidence class: **Reported** — vendor article; no Harness package, tool, script or sandbox was exercised here.
