---
type: Concept
title: Pydantic AI Harness
description: First-party Pydantic AI package of agent batteries — Coder, memory, guardrails, context management, approvals, code mode, and durability integrations — kept outside a deliberately small core.
tags: [ml, pydantic-ai, agents, llm-frameworks]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:52:00Z }
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
  - id: pydantic-planning-docs
    resource: ../raw/harness/planning/index.md
    scope: ../raw/harness/planning/
    kind: documentation
    revision: sha256:13d1290b5beb86fcdc54d8111be20cd8fdfd48378657c9219f051a1492ba2864
    title: "Planning"
  - id: pydantic-subagents-docs
    resource: ../raw/harness/subagents/index.md
    scope: ../raw/harness/subagents/
    kind: documentation
    revision: sha256:53a83ad8be94200b67b4414a89df6e179c81b68c3a602f6fc242efd32761a974
    title: "Subagents"
  - id: pydantic-docs-capabilities-overview
    resource: ../raw/capabilities/overview/index.md
    scope: ../raw/capabilities/overview/
    kind: docs
    revision: sha256:6434ebdb6f8a86b177d4659f738e214d9f719260787ae93cd1bcda3811bd15c
    title: "Capabilities"
  - id: pydantic-multi-agent-guide
    resource: ../raw/guides/multi-agent-applications/index.md
    scope: ../raw/guides/multi-agent-applications/
    kind: documentation
    revision: sha256:2439e904aa5b1b1ecacfc0e0dcc1dbb8f5e89062198169f4f9f22304589598c1
    title: "Multi-agent Applications"
  - id: pydantic-harness-docs
    resource: ../raw/harness/index.md
    scope: ../raw/harness/
    kind: documentation
    revision: sha256:81a797897bfed51babf134beea8b5306db5f9109f2f4913a4b1b2a542885cde0
    title: "Pydantic AI Harness"
---

The **Pydantic AI Harness** is the first-party package of "batteries for your agent" that sits outside the core library: memory, guardrails, context management, file system access, code mode, and more, all delivered as [capabilities](pydantic-ai-capability-primitive.md)[^pydantic-ai-v2] It exists to keep the core small and stable while the surrounding layer moves fast.

For selection against other SDKs, see the [Python agent harness comparison](python-agent-harness-comparison.md), including portability, isolation and recovery tradeoffs.

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

The vendor's own catalog is the closest thing to a manifest, and it is a different kind of list: every capability on the capabilities overview page carries the package it ships from, under the rule that core carries only what needs model or framework support while the Harness carries everything else, from one capability to a complete agent[^pydantic-docs-capabilities-overview] Against the tour's inventory it corroborates `Coder`, `Researcher`, `Memory`, `Guardrails`, `Spend Limits`, `Subagents`, `Planning`, `Code Mode`, `Step Persistence`, `Compaction` and the three Harness durability engines, and it adds families the press lists never mentioned: `FileSystem`, `Shell`, `Smart Search`, sixteen further execution-environment entries, fourteen service integrations, and the policy entries — `Prompt Injection Defender`, `Artifact Scanning`, `Ask User`, `System Reminders`, `Detect Loops`, `Trajectory Judge`, `Refine Output`[^pydantic-docs-capabilities-overview] It answers the earlier maturity question by stating a package for each entry, and leaves it open by naming no version. The full tier-tagged inventory is compiled in [Pydantic AI capability catalog](pydantic-ai-capability-catalog.md).

Two details of the split are worth fixing here. `Compaction` exists on **both** sides — provider-native in core, model-agnostic strategies in Harness — so a capability name is not a unique key to a tier[^pydantic-docs-capabilities-overview] And one capability reverses the usual default: `MCP` runs locally by default because it carries credentials, while the other provider-adaptive tools default to native[^pydantic-docs-capabilities-overview] That reversal, the constructor-time `UserError` for a missing optional extra, and the stable default ids are compiled in [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md).

`Planning` is the one capability with a documented API surface, because it now supersedes Vstorm's community `pydantic-ai-todo`: the same task-list feature set (persistent stores, subtasks, dependencies, events) as a first-party capability whose plan travels in tool results instead of the system prompt, so editing it leaves the cached prefix intact[^pydantic-planning-docs] That also resolves the `TodoCapability` row above — the name in the newsroom list and the `Planning` name in the later inventory are the same job, and the first-party package is the one that ships the todo feature set. The capability, its tools, stores, events and durable behaviour are compiled in [Pydantic AI Harness planning](pydantic-ai-harness-planning.md).

`Subagents` follows the same path and resolves the `SubAgentCapability` row the same way: the newsroom list describes "spawn, check, and cancel subagents as tools", and the vendor's later names are one capability, `SubAgents`, whose single `delegate_task` tool spawns, whose `list_tasks`/`check_task`/`cancel_task` tools check and cancel under `task_control`, and whose roster is listed in the system prompt rather than rebuilt per turn[^pydantic-subagents-docs] The delegation contract — the roster, what crosses into the child run, per-delegate budgets, the model menu, soft-versus-hard failure handling, disk-defined delegate files and the child-workflow opt-in — is compiled in [Harness subagents](pydantic-ai-subagents.md); the background-task, remote-worker, model-created-agent and persisted-session half is in [subagent task control](pydantic-ai-subagent-tasks.md).

Sandboxing has since become a core concern rather than a Harness one: `LocalWorkspace` ships in core, sandbox backends (`E2BSandbox`, `SpritesSandbox`, `BubblewrapSandbox`, `SmolSandbox`, `DaytonaSandbox`) are core workspace backends, and v2.59.0's `DaytonaSandbox` runs `Coder`, `Shell`, `FileSystem` and the other Harness capabilities inside a Daytona sandbox[^dd-v2-tour-2026] See [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md).

One further Harness feature is named without detail: media externalization, which moves large payloads out of persisted message history, with storage configured separately — generating an image through [Pydantic AI image generation](pydantic-ai-image-generation.md) does not persist it automatically[^pydantic-image-gen-2026] That is the feature that matters once a `BinaryImage` would otherwise sit in every saved message, but no capture here documents its configuration keys, its trimming policy, or what remains once a payload has been externalized.

For the versioned sandbox boundary, benchmark results and retry risks of `CodeMode`, see [Pydantic AI code mode](pydantic-ai-code-mode.md).

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

The vendor's own page documents that tool's parameters, its return shape, the catalog API and what the type check enforces; they are compiled in [Pydantic AI dynamic workflows](pydantic-ai-dynamic-workflow.md).

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

A third-party tour restates that policy with more operational detail: APIs may move between minor releases "always with deprecation warnings where practical", every breaking change is documented in release notes with migration guidance, and patch releases will not intentionally break existing behaviour. The stated consequence is to pin the exact version, read release notes before upgrading, and keep relied-on capabilities under test — including the durability engines that ship in this tier[^dd-v2-tour-2026]

The vendor's own Harness page fills in the mechanics of that policy, and one of them is the upgrade rule to rely on[^pydantic-harness-docs]: while the Harness is on 0.x, **each Harness release ships alongside the Pydantic AI release with the same minor and patch number** — Harness 0.51.0 with Pydantic AI 2.51.0 — and pins that exact `pydantic-ai-slim` version, so upgrading the Harness upgrades Pydantic AI with it and every installable pair has been tested together. The install is `pydantic-ai-harness`, which pulls `pydantic-ai-slim` in, so Pydantic AI need not be installed separately; provider and CLI extras pass through (`[anthropic]`, `[cli]`), capability-specific extras are per page, and the package requires **Python 3.11+**.

From 1.0 the Harness adopts core's policy, and the interesting part is what counts as behaviour[^pydantic-harness-docs] — a stability claim wider than signatures:

- **Defaults** do not change in a way that alters what an existing agent does (enabling a tool, lowering a limit, switching a fallback); new behaviour arrives behind a new parameter, and a default changes only in a major release.
- **Stored history** is stable: tool names, argument schemas, metadata keys and framing tags persist in histories you may store and resume, so a minor release may add optional arguments but does not rename or remove a tool, an argument or a record a capability relies on.
- **Prompt text is not stable**: the wording of instructions, tool descriptions and other model-facing text may change in a minor release, with release notes listing the changes; passing a capability its own instructions or descriptions keeps your wording fixed.
- Capabilities marked experimental (currently `ACP` only) are excluded until they graduate, and a change forced by a third-party service or SDK the capability integrates with is not breaking.

From 1.0 the version numbers stop mirroring Pydantic AI's, a Harness major release does not require a core major, and moving the `pydantic-ai-slim` pin to a new core major is itself a Harness major release — so upgrading within a major never crosses a Pydantic AI major[^pydantic-harness-docs]

## Three packages, one direction

The vendor page is the clearest statement of what the tiers are, because it names the third one[^pydantic-harness-docs]: **Pydantic AI** (`pydantic-ai`) is the framework — agent loop, models, tools, structured output, the capability system; **Pydantic AI Harness** (`pydantic-ai-harness`) is the capability library over it, including complete agents such as `Coder`; and **CLAI** (`pydantic-clai2`, run as `clai2`) is a terminal coding agent built on the Harness's `Coder` and extended with plugins. Each installs the one below it: `pydantic-ai-harness` installs `pydantic-ai-slim`, and `pydantic-clai2` installs `pydantic-ai-harness`. CLAI is explicitly **not** the `clai` chat CLI that ships with Pydantic AI[^pydantic-harness-docs] — the name collision is worth carrying, because the same page documents both.

The split is mechanical rather than a maturity ladder[^pydantic-harness-docs]: core carries what needs model or framework support — provider-native tools such as image generation, provider APIs such as compaction, deep loop integration such as tool search, and fundamentals such as thinking, MCP and web search — and the Harness ships everything else, as a separate package so capabilities can iterate at the field's speed while Pydantic AI stays lean. The vendor's count is "90+" capabilities, grouped into harnesses (Coder, Researcher), execution environments, tools and native abilities, integrations, web and research, reasoning/planning/delegation, context management, knowledge and memory, control and safety, self-extension, and execution runtime[^pydantic-harness-docs]

The page also states the workspace rule the individual capability pages enforce[^pydantic-harness-docs]: a workspace is where files and commands live, **capabilities never pick one for you**, and a run without one fails at its start with a message saying what to attach. `LocalWorkspace('.')` is the machine you are on and is **not** a sandbox, so commands can reach anything the process user can; the sandbox list is Modal, E2B, Render, Sprites, Daytona, boxd and the rest compiled in [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md). Two path defaults follow: Harness files — shell background-job logs and tool-output spills — live in `.pydantic-ai-harness/` in the workspace's working directory and are git-ignored (Shell falls back to a user-private directory under `$TMPDIR` when the working directory is unwritable), while step-persistence and media stores and Code Mode mounts are paths on the **machine running the agent**, not the workspace. `FileSystem`'s `root_dir` limits the file tools only, never `Shell` commands.

For the problem-to-capability lookup the page publishes — a flooding tool result spilling at 10,000 characters with a 4,000-character truncation fallback, `SpendLimits` for a day or a month per tenant, `ToolBudgets` refusing the fourth expensive call with a tool result the model can act on, `DetectLoops` nudging or erroring, and `RepairToolArguments` running `json-repair` before validation — the compiled per-capability pages are the place to read the contract; the respective capabilities are linked from the [capability catalog](pydantic-ai-capability-catalog.md).

## Limits

- The capability lists above come from a newsroom restatement, a third-party tour and the vendor's own catalog; no Harness package, README, or repository was inspected, so per-item maturity still rests on documentation alone, and the catalog's package column is a vendor claim rather than an import that was tried[^pydantic-docs-capabilities-overview]
- The catalog names no Harness or Pydantic AI version, so the tier membership it states cannot be dated against the tour's v2.59-era list, and `ContextManagerCapability` and `ConsoleCapability` from the newsroom list match nothing in it by name — whether they were renamed, removed or simply omitted is unstated[^pydantic-docs-capabilities-overview]
- Individual capability APIs, configuration keys, and dependency footprints are documented here only where a capture was compiled: `Planning` in [Harness planning](pydantic-ai-harness-planning.md), `Subagents` in [Harness subagents](pydantic-ai-subagents.md) and [subagent task control](pydantic-ai-subagent-tasks.md), `DynamicWorkflow` in [dynamic workflows](pydantic-ai-dynamic-workflow.md), `BackgroundTools` in [background tools](pydantic-ai-harness-background-tools.md), and — from this pass — [advisor](pydantic-ai-harness-advisor.md), [researcher](pydantic-ai-harness-researcher.md), [coder](pydantic-ai-harness-coder.md), [shell](pydantic-ai-harness-shell.md), [file system](pydantic-ai-harness-filesystem.md), [smart search](pydantic-ai-harness-smart-search.md), [memory](pydantic-ai-harness-memory.md), [skills](pydantic-ai-harness-skills.md), [documentation lookup](pydantic-ai-harness-docs.md), [ask user](pydantic-ai-harness-ask-user.md), [prompt injection defender](pydantic-ai-harness-prompt-injection-defender.md), [Modal](pydantic-ai-harness-modal-sandbox.md) and [E2B](pydantic-ai-harness-e2b-sandbox.md). Every one of them, and the vendor catalog page itself, names **no Harness or Pydantic AI version**, so each is `draft` under the `pydantic-ai` domain rule with a `stale_after`[^pydantic-harness-docs]
- `TodoCapability`'s PostgreSQL persistence and `MemoryCapability`'s `MEMORY.md` imply external state, but no capture says how that state is migrated or isolated between agents.
- `Coder`'s prompt caching default and the sandbox isolation properties are reported, not measured.
- The `run_workflow` description in that article is a vendor sketch naming no Harness or Pydantic AI version and was not executed; the signature, budgets and type-checking mechanism are now documented by the vendor's own page, compiled in [Pydantic AI dynamic workflows](pydantic-ai-dynamic-workflow.md), which is also version-unknown[^colvin-code-is-graph-2026]
- Evidence class: **Reported**.

## Relationships

- **Supplies Coder to** [Pydantic AI AgentEnv evaluation](pydantic-ai-agentenv-evaluation.md), an environment-based evaluation integration documented in a separate vendor announcement.
- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md): every Harness battery is attached as a capability.
- **Is catalogued tier by tier in** the [capability catalog](pydantic-ai-capability-catalog.md), the vendor's own package-tagged inventory of both tiers.
- **Routes its MCP and web tools through** [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md), which documents the local-first default `MCP` takes and the constructor-time error for a missing optional extra.
- **Part of** the [Pydantic AI v2 release](pydantic-ai-v2-release.md) story: the split is what lets core stay lean.
- **Includes** endorsed third-party capabilities, documented from the provider side in [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md).
- **Hosts** [deferred tool approval](pydantic-ai-deferred-approvals.md) capabilities and three of the nine [durable execution](pydantic-ai-durable-execution.md) engines, which is why its 0.x policy reaches deployment risk.
- **Supplies the whole agents** — `Coder` and `Researcher` — that [Claude Agent SDK versus Pydantic AI](claude-agent-sdk-vs-pydantic-ai.md) compares with a bundled coding agent, and the sandbox backends that page swaps in.
- **Defines the boundary with** core [workspaces](pydantic-ai-workspaces-and-sandboxes.md) and the [capability primitive](pydantic-ai-capability-primitive.md): its `Coder`, `Shell`, `FileSystem`, `RepoContext` and `Researcher` capabilities act in whatever workspace the run has, take the `authority` and `path_authority` arguments recorded in [workspace file authority](pydantic-ai-workspace-authority.md), and work under Temporal, DBOS and Prefect with Azure Durable Task and Render Workflows covering `FileSystem` and the `shell` tool.
- **Runs model-written choreography through** [Code as the agent graph](code-as-agent-graph.md): `run_workflow` and `CodeMode` both execute Python in Monty instead of walking a node graph — with `run_workflow`'s catalog, budgets and engine behaviour in [dynamic workflows](pydantic-ai-dynamic-workflow.md).
- **Supplies the recall half of** [Self-improving agent loops](self-improving-agent-loops.md): `StepPersistence` writes the runs, `ConversationSearch` reads them back, and the check at the edge of idle is the capability this tier does not ship.
- **Works under Temporal with three deviations** documented in [Pydantic AI on Temporal](pydantic-ai-temporal.md): write-tool events reach listeners while read and shell events do not, non-`self` delegates run in an activity and need their own model, and `run_command`/`shell` activity timeouts start at 300 seconds.
- **Documents its task-list capability in** [Pydantic AI Harness planning](pydantic-ai-harness-planning.md), which absorbs Vstorm's `pydantic-ai-todo` feature set and is the tier's worked example of a cache-aware, durably journaled capability.
- **Schedules slow tools through** [Harness background tools](pydantic-ai-harness-background-tools.md): a selected tool runs while the model continues, and its result returns later as a framed follow-up message carrying the task ID rather than as a tool return.
- **Delegates through** [Harness subagents](pydantic-ai-subagents.md), the roster and `delegate_task` contract behind the `Subagents` entry, with [subagent task control](pydantic-ai-subagent-tasks.md) for the background tasks, remote workers and persisted sessions that capability ports from Vstorm's `subagents-pydantic-ai`[^pydantic-subagents-docs]
- **Runs complete agents** assembled from the catalog: [Coder](pydantic-ai-harness-coder.md) over [filesystem](pydantic-ai-harness-filesystem.md) and [shell](pydantic-ai-harness-shell.md), and [Researcher](pydantic-ai-harness-researcher.md) over core web search and fetch plus [subagents](pydantic-ai-subagents.md).
- **Supplies the knowledge layer**: [Memory](pydantic-ai-harness-memory.md) for notes across runs, [skills](pydantic-ai-harness-skills.md) for on-demand procedures, and [documentation lookup](pydantic-ai-harness-docs.md) for the six Pydantic AI topics an agent may need while writing capabilities of its own.
- **Composes into the deep-agent level** described in [multi-agent patterns](pydantic-ai-multi-agent-patterns.md): the vendor guide lists planning, file operations, delegation, sandboxed code execution, context management, human approval and durable execution as the seven concerns a deep agent combines, each of them a capability shipped here, with `Coder` as the prebuilt assembly[^pydantic-multi-agent-guide]
- **Supplies the sandbox workspace backends** [Modal](pydantic-ai-harness-modal-sandbox.md) and [E2B](pydantic-ai-harness-e2b-sandbox.md), which register no tools of their own and are paired with the capabilities above.
- **Bounds what the agent may read and ask**: [prompt injection defender](pydantic-ai-harness-prompt-injection-defender.md) screens local tool results, and [ask user](pydantic-ai-harness-ask-user.md) puts multiple-choice questions to a person mid-run.

[^pydantic-ai-v2]: Douwe Maan, "Pydantic AI v2: capabilities, a leaner core, and the Harness", Pydantic, published 2026-06-23, §"The Harness and a leaner core" (split rationale, community capabilities, June focus) and §"One primitive: the capability" for the `pydantic_ai_harness` `CodeMode` import. Local capture: `raw/pydantic-ai-v2/index.md` (revision 836bd3b1). Evidence class: **Reported**; no Harness package, source tree, or capability matrix was inspected in this ingest, so tier membership and maturity are the maintainer's description only.
[^vstorm-v2-blog]: Nicholas Berryman, "Pydantic AI v2 and the road to production-grade agentic AI", Vstorm, published 2026-07-03, §"Where Vstorm fits: endorsed, linked, and upstreaming" (the Harness README's use of `pydantic_ai_summarization` and `pydantic_deep`). Local capture: `raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md` (revision 836bd3b1). Evidence class: **Reported** — secondhand description by a partner; the Harness README and packages were not inspected.
[^alphasignal-v2-news]: AlphaSignal Newsroom, "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work", AlphaSignal, published 2026-06-23, §"The Harness: batteries for your agent" (capability list, graduation of code mode, the core/Harness split rationale) and §"Getting started and migrating from v1" (`uv add pydantic-ai-harness`, 0.x policy). Local capture: `raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/index.md` (revision 836bd3b1). Evidence class: **Reported** — no Harness package or repository was inspected.
[^pydantic-image-gen-2026]: David Sanchez, "Generate images with Pydantic AI", Pydantic, published 2026-09-14, §"Why we added image generation" (raw lines 87–102) for the Harness media-externalization reference, and §"Let an agent generate the image" for the non-persistence of generated images. Local capture: `raw/image-generation/index.md`, content digest sha256:2563fee1. Evidence class: **Reported** — vendor announcement; no Harness package was inspected.
[^pydantic-vs-claude-sdk-2026]: Aditya Vardhan, "Pydantic AI vs Claude Agent SDK: Who owns the agent?", Pydantic, published 2026-10-05, §"Pydantic AI grows with your application" (raw lines 69–101) for `Coder` (file tools, shell, repository instructions, delegation, context management), `Researcher` (web answers with cited sources), the composability claim, the `capabilities=[LocalWorkspace("."), Coder()]` snippet and GitHub Agentic Workflows. Local capture: `raw/pydantic-ai-vs-claude-agent-sdk/index.md`, content digest sha256:e13b086e. Evidence class: **Reported** — a vendor article naming no Pydantic AI release version and linking, not quoting, the Harness documentation.
[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"The mental model: an agent loop plus capabilities" (raw lines 98–120) for the core/Harness split and the v2.59-era Harness inventory; §"What changed in V2, in one table" for the 0.x policy wording and the durability placement; §"Workspaces: one API for local and sandboxed tools (v2.52)" for `DaytonaSandbox` running Harness capabilities; §"Caching is now one switch (v2.55)" for the `Coder` caching default. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — a third-party tour; no Harness package, README, or capability matrix was inspected.
[^sanchez-self-improving-2026]: David Sanchez, "When agents improve agents: loops that improve themselves", Pydantic, published 2026-07-31T12:00Z; local capture `raw/when-agents-improve-agents/index.md`, content digest sha256:3a72d59c. §"Learning from its own runs" (raw lines 31–59) for the `search_conversation_history` tool, the BM25 search across sessions and agents, `Memory`, the whole-store-versus-rank scope limit, and the `StepPersistence`/`ConversationSearch` snippet; §"The loop supplies its own continue" (lines 25–27) for the output-guardrail `retry` verdict and Macroscope. Evidence class: **Reported** — vendor article; no Harness package, store or search was exercised.

[^colvin-code-is-graph-2026]: Samuel Colvin, "The code is the graph", Pydantic, published 2026-10-13T09:00Z, 2,445 words as declared; local capture `raw/the-code-is-the-graph/index.md`, content digest sha256:d8803b5f. §"Long live graphs" (raw lines 145–167) for the Harness dynamic-workflow description, the single `run_workflow` tool, the two-`reviewer`-then-`summarizer` script, type-checking against sub-agent signatures before any sub-agent runs, only the last value returning to context, retries and voting as ordinary Python, the Temporal attachment without script changes, and Monty's host-function-only exit. Evidence class: **Reported** — vendor article; no Harness package, tool, script or sandbox was exercised here.
[^pydantic-planning-docs]: Pydantic Docs, "Planning", <https://pydantic.dev/docs/ai/harness/planning/>; local capture `raw/harness/planning/index.md`, content digest sha256:13d1290b, 3,176 words as declared (3,260 by `wc -w`), no publication date, author or framework version. Lines 219–236 for the `pydantic-ai-todo` incorporation and supersession; lines 38–50 for the plan-in-tool-results design and its cache argument. Evidence class: **Reported** — vendor documentation; no Harness package was inspected.
[^pydantic-harness-docs]: Pydantic Docs, "Pydantic AI Harness", <https://pydantic.dev/docs/ai/harness/>; local capture `raw/harness/index.md`, content digest sha256:81a79789, 4,157 words as declared (4,695 by `wc -w`), 371 lines, no publication date, author, licence or Pydantic AI/Harness version, and the only asset in the package is the decorative Slack badge SVG `assets/Slack-Join-Slack-4A154B.svg`, excluded as decoration. Locators are line ranges in that capture: 11–17 for the one-paragraph pitch and the capability framing; 21–33 for the three-package table (`pydantic-ai`, `pydantic-ai-harness`, `pydantic-clai2`), the install direction and the CLAI-versus-`clai`-CLI note; 35–79 for the quick start, `LocalWorkspace('.')`'s non-sandbox caveat and the `coder_agent` CLI route; 81–93 for the `Coder` composition and its remote-sandbox creation note; 95–113 for the workspace rule, the `.pydantic-ai-harness/` file location, the `$TMPDIR` fallback, the machine-local Step Persistence/Media/Code Mode paths and the `root_dir`-does-not-bound-Shell rule; 115–131 for the problem-to-capability table (10,000-character spill, 4,000-character truncation fallback, `SpendLimits`, `ToolBudgets`, `DetectLoops`, `RepairToolArguments`); 133–349 for the 90+ capability catalog grouped into harnesses, execution environments, tools, integrations, web and research, reasoning/planning/delegation, context management, knowledge and memory, control and safety, self-extension and execution runtime; 351–371 for the "When do you need the Harness?" boundary, installation, observability and version policy (0.x same-numbered pairing and pin, and the from-1.0 defaults/stored-history/prompt-text rules). Evidence class: **Reported** — vendor documentation for its own package; no Harness package was installed, no capability imported, and every linked capability page was read as a link, not followed.
[^pydantic-subagents-docs]: Pydantic Docs, "Subagents", <https://pydantic.dev/docs/ai/harness/subagents/>; local capture `raw/harness/subagents/index.md`, content digest sha256:53a83ad8, 18,887 words as declared (19,277 by `wc -w`), no publication date, author, licence or framework version. Lines 15–19 for the single-tool contract and its cache-stable roster; lines 60–69 and 271–308 for the spawn/check/cancel tool set behind the `SubAgentCapability` name in the newsroom list. Evidence class: **Reported** — vendor documentation; no Harness package was installed or imported.
[^pydantic-docs-capabilities-overview]: Pydantic Docs, "Capabilities" (https://pydantic.dev/docs/ai/capabilities/overview/; 4,642 words as declared, 5,228 by local `wc -w`; no publication date and no Pydantic AI or Harness version). §"Available capabilities" for the core-versus-Harness rule and the package column; §"Harnesses" for `Coder` and `Researcher`; the group tables under §"Execution environments", §"Tools & native abilities", §"Integrations", §"Web & research", §"Reasoning, planning & delegation", §"Context management", §"Knowledge & memory", §"Control & safety", §"Self-extension", §"Execution runtime" and §"Loop customization" for the per-entry `Core`/`Harness` attribution, including both `Compaction` rows; §"Provider-adaptive tools" for the local-by-default `MCP` reversal. Local capture: `raw/capabilities/overview/index.md`, content digest sha256:6434ebdb. Evidence class: **Reported** — vendor documentation naming no release version; no package was installed or imported.

[^pydantic-multi-agent-guide]: Pydantic Docs, "Multi-agent Applications", <https://pydantic.dev/docs/ai/guides/multi-agent-applications/>; local capture `raw/guides/multi-agent-applications/index.md`, content digest sha256:2439e904, 2,082 words as declared (2,144 by `wc -w`), and the page names no publication date, author, licence or Pydantic AI/Harness version. §"Deep Agents" (raw lines 356–368) for the seven concerns and the capability each one links to — `Planning`, `FileSystem` and `Shell`, `SubAgents`, `Shell` over `DockerContainer` and `CodeMode`, core Compaction plus the Harness compaction strategies, tool approval and durable execution — and for `Coder` as the ready-made assembly of file system, shell, delegation and context management, "you can use whole or take apart". Evidence class: **Reported** — a vendor guide read as text; no Harness package was installed, no capability composed.
