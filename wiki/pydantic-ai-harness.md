---
type: Concept
title: Pydantic AI Harness
description: First-party Pydantic AI package of agent batteries — Coder, memory, guardrails, context management, approvals, code mode, and durability integrations — kept outside a deliberately small core.
tags: [ml, pydantic-ai, agents, llm-frameworks]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:10:00Z }
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

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md): every Harness battery is attached as a capability.
- **Part of** the [Pydantic AI v2 release](pydantic-ai-v2-release.md) story: the split is what lets core stay lean.
- **Includes** endorsed third-party capabilities, documented from the provider side in [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md).
- **Hosts** [deferred tool approval](pydantic-ai-deferred-approvals.md) capabilities and three of the nine [durable execution](pydantic-ai-durable-execution.md) engines, which is why its 0.x policy reaches deployment risk.
- **Defines the boundary with** core [workspaces](pydantic-ai-workspaces-and-sandboxes.md) and the [capability primitive](pydantic-ai-capability-primitive.md).

[^pydantic-ai-v2]: Douwe Maan, "Pydantic AI v2: capabilities, a leaner core, and the Harness", Pydantic, published 2026-06-23, §"The Harness and a leaner core" (split rationale, community capabilities, June focus) and §"One primitive: the capability" for the `pydantic_ai_harness` `CodeMode` import. Local capture: `raw/pydantic-ai-v2/index.md` (revision 836bd3b1). Evidence class: **Reported**; no Harness package, source tree, or capability matrix was inspected in this ingest, so tier membership and maturity are the maintainer's description only.
[^vstorm-v2-blog]: Nicholas Berryman, "Pydantic AI v2 and the road to production-grade agentic AI", Vstorm, published 2026-07-03, §"Where Vstorm fits: endorsed, linked, and upstreaming" (the Harness README's use of `pydantic_ai_summarization` and `pydantic_deep`). Local capture: `raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md` (revision 836bd3b1). Evidence class: **Reported** — secondhand description by a partner; the Harness README and packages were not inspected.
[^alphasignal-v2-news]: AlphaSignal Newsroom, "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work", AlphaSignal, published 2026-06-23, §"The Harness: batteries for your agent" (capability list, graduation of code mode, the core/Harness split rationale) and §"Getting started and migrating from v1" (`uv add pydantic-ai-harness`, 0.x policy). Local capture: `raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/index.md` (revision 836bd3b1). Evidence class: **Reported** — no Harness package or repository was inspected.
[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"The mental model: an agent loop plus capabilities" (raw lines 98–120) for the core/Harness split and the v2.59-era Harness inventory; §"What changed in V2, in one table" for the 0.x policy wording and the durability placement; §"Workspaces: one API for local and sandboxed tools (v2.52)" for `DaytonaSandbox` running Harness capabilities; §"Caching is now one switch (v2.55)" for the `Coder` caching default. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — a third-party tour; no Harness package, README, or capability matrix was inspected.
