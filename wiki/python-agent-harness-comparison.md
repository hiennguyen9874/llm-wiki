---
type: Concept
title: Python agent harness comparison
description: Decision criteria and vendor-reported tradeoffs between Pydantic AI Harness and seven Python agent harness SDKs.
tags: [pydantic-ai, agents, llm-frameworks, ecosystem]
status: draft
created: 2026-11-17
generated: { by: llm-wiki-agent/1, at: 2026-11-17T06:49:19Z }
stale_after: 2026-12-17
sources:
  - id: pydantic-harness-comparison-2026
    resource: ../raw/best-python-agent-harnesses/index.md
    scope: ../raw/best-python-agent-harnesses/
    kind: article
    revision: sha256:ca1c66b7cbdcb995d2e0900d44df78d9cc20c9b192f640f916c2d28a58636c73
    title: Best Python Agent Harnesses in 2026
---

Pydantic's November 2026 comparison distinguishes a configurable finished agent from a harness SDK assembled as a library, and recommends choosing by model portability, replaceable components, execution isolation, approval, recovery, context management, tracing and support. Its first choice is its own [Pydantic AI Harness](pydantic-ai-harness.md), but it identifies cases for alternatives. This is **Reported**, not an independent ranking; Pydantic AI and Harness versions are not specified in the article.[^pydantic-harness-comparison-2026]

## Decision boundaries

The source defines an SDK as a Python-importable library with file/shell tools, planning, sub-agents, context management, a workspace and a ready-made agent; it includes wrappers of finished agents. **Reported:** saving a conversation is not the same as durable execution replaying completed steps after restart. Ask separately where commands run, whether an approval can survive a process exit, and which engine or store must be operated.[^pydantic-harness-comparison-2026]

| Option | Reported positioning and tradeoff |
| --- | --- |
| Pydantic AI Harness, version unspecified | Composable capabilities and ready-made Coder/Researcher; multiple providers and workspace backends, external durable engines, and OpenTelemetry. Python-only library: infrastructure and testing combinations are the user's responsibility. The article warns Coder with `LocalWorkspace` runs host shell commands without an allowlist. |
| LangChain Deep Agents | Fits LangGraph and LangSmith; middleware changes components. Approvals require a checkpointer; the article found no external durable engine documented. Version 0.7 made planning opt-in. |
| Claude Agent SDK | Embeds Claude Code as a subprocess on Claude models. The article reports sandboxing off by default, with an unsandboxed fallback warning if startup fails; session-store persistence is best-effort. |
| OpenAI Agents SDK | Fits OpenAI's model and tracing stack; article reports serialized approval state and Temporal, DBOS, Restate and Dapr integrations. Other-provider adapters are described as beta/best-effort; default tracing goes to OpenAI. |
| Codex SDK | Embeds Codex, rather than recomposing its agent; has sandbox presets and resumable local threads. The article reports limited Python approval choices. |
| OpenHands Software Agent SDK | Coding-focused components and separate agent server for remote/container execution; models via LiteLLM. Local workspace acts on the host; its documented risky-only policy depends on the acting model's risk assessment. |
| Strands harness | Assembled harness for AWS/Bedrock-oriented teams; defaults can be overridden. The article found no external durable engine or commercial SDK support documented. |
| Microsoft Agent Framework Harness | Python, .NET and Go; Durable Extension on Durable Task. Article marks several Python features and the extension pre-release or experimental, and found no command sandbox documented on the Harness page. |

These are the publisher's **Reported** descriptions as checked by its authors on 2026-10-30, with the Pydantic row rechecked 2026-11-09; “not documented” is a search result, not proof of absence. The source lists 30+ providers, 12 sandbox/remote workspace integrations and nine durability engines for its own unversioned Pydantic AI Harness; these are time-sensitive inventory counts, not guarantees of interchangeability.[^pydantic-harness-comparison-2026]

## Relationships

- [Python agent framework comparison](python-agent-framework-comparison.md) covers the broader framework and voice-stack choices rather than only harness SDKs.

- [Pydantic AI Harness](pydantic-ai-harness.md) describes the components behind the comparison's Pydantic entry.
- [Claude Agent SDK versus Pydantic AI](claude-agent-sdk-vs-pydantic-ai.md) examines the agent-ownership tradeoff in more detail.
- [Pydantic AI durable execution](pydantic-ai-durable-execution.md) separates engine integrations and execution rules from simple session persistence.

## Evidence and coverage limits

The single local capture is an English Pydantic article by Douwe Maan, published and updated 2026-11-09. It reports a documentation-and-license review, not a controlled comparison; the publisher sells the leading option and applies its own criteria. The capture contains no local attachments or includes; external documentation, licenses, benchmark records and linked articles were not fetched. Promotional install text and unrelated framework internals were excluded. No packages, commands, approvals, sandboxes or recovery tests were run; versions, capture date and article license are unspecified. Counts, security defaults and support terms require fresh primary-source checks before a decision.[^pydantic-harness-comparison-2026]

[^pydantic-harness-comparison-2026]: “Best Python Agent Harnesses in 2026,” frontmatter; “What to look for in an agent harness,” “How we compared,” entries 1–8, “Comparison at a glance,” and “When another harness is the better pick.”
