---
type: Concept
title: Python agent framework comparison
description: Vendor-reported framework selection tradeoffs for Pydantic AI, competing Python agent frameworks, and voice stacks.
tags: [pydantic-ai, agents, llm-frameworks, ecosystem, voice]
status: draft
created: 2026-11-17
generated: { by: llm-wiki-agent/1, at: 2026-11-17T06:49:19Z }
stale_after: 2026-12-17
sources:
  - id: pydantic-frameworks-2026
    resource: ../raw/best-python-ai-agent-frameworks/index.md
    scope: ../raw/best-python-ai-agent-frameworks/
    kind: article
    revision: sha256:95b1833321c11972d79ec037df239f7bfd875e632111553198fdf3934e129f99
    title: Best Python AI Agent Frameworks in 2026
---

Pydantic's comparison recommends choosing an agent framework by model portability, recovery, approval, user interfaces, tracing, replaceable components and support; its preferred option is its own Pydantic AI. **Reported:** these are vendor-selected criteria and documentation-based claims, not an independent ranking or runtime test. The article specifies no Pydantic AI version, so its framework-specific details are version-unknown.[^pydantic-frameworks-2026]

## Choosing by operating constraint

**Reported:** A saved session, a graph checkpointer and replay on an external durable engine are different recovery models; ask what happens to an interrupted tool call and who operates the store or engine. Likewise, approval should survive process exit if a human may take days to respond. The article defines native integrations as built in or officially maintained, excludes generic adapters from that count, and uses “none documented” for what its authors did not find, not proof of impossibility.[^pydantic-frameworks-2026]

| Option | Reported fit and qualification |
| --- | --- |
| Pydantic AI, version unspecified | Typed Python agent with validated outputs, model choice, deferred approvals, external durability and OpenTelemetry; Python-only library run on the user's infrastructure, not a hosted management platform. LangChain has more document loading, vector store and retrieval integrations; its tools can also be used via `LangChainToolset` (Pydantic AI version unspecified). |
| LangGraph / LangChain | Suits existing graph checkpoints and LangSmith workflows or a needed LangChain integration; own graph checkpointers rather than a documented external durable engine, LangSmith tracing and beta MCP client. |
| OpenAI Agents SDK | Suits OpenAI models and tracing; approval state is serialized, and Temporal, DBOS, Restate and Dapr are listed. Other model adapters are described as beta or best-effort; default tracing uploads to OpenAI. |
| Google ADK | Suits Google Cloud/Gemini or a Python, Java or Go team. Event-log resume reruns a tool interrupted mid-call, i.e. at least once; tool confirmation is described as experimental. |
| Microsoft Agent Framework | Suits Azure/Foundry or Python and .NET; checkpoints and a Durable Task extension, plus OTel. The article limits Unified support to issues arising from Azure AI services and notes Python/.NET feature differences. |
| Strands Agents | Suits AWS/Bedrock; persisted sessions and a Temporal plugin described as public preview. AG-UI is via a partner package, not the SDK. |
| CrewAI | Suits role-and-task-oriented teams; Flows provide persistence and checkpointing. Webhook-based human approval is described as an enterprise feature. |
| Claude Agent SDK | Suits embedding Claude Code's loop on Claude models; runs the CLI as a subprocess and uses local session state. The article found no durable-engine integration documented. |
| Agno | Suits a ready-made server, storage and management surface; AgentOS and its database define the service shape, and continuing a paused run requires the same database and session. Some management features are paid. |

These entries and limitations reflect the source's own review rather than firsthand verification. Product-specific support contracts, adapters, licenses and preview labels should be checked against current primary documentation before procurement.[^pydantic-frameworks-2026]

## Voice is also a transport decision

For Pydantic AI (version unspecified), the article reports the same agent and tools can run over realtime speech, with message history passed to a text agent for structured output; audio transport and telephony are brought separately. LiveKit Agents supplies WebRTC rooms, SIP and composable speech plugins; Pipecat composes transport and speech-processing stages. **Synthesis:** choose based on who owns the call and its pipeline as well as who owns the agent; these stacks can complement rather than simply replace each other. The article also reports a hosted ElevenLabs path and a LiveKit-history conversion, neither tested here.[^pydantic-frameworks-2026]

## Relationships

- [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md) records broader and partly independent perspectives on integration breadth.
- [Python agent harness comparison](python-agent-harness-comparison.md) compares assembled harnesses rather than the broader agent framework category.
- [Pydantic AI durable execution](pydantic-ai-durable-execution.md), [deferred tool approval](pydantic-ai-deferred-approvals.md) and [realtime voice agents](pydantic-ai-realtime-voice.md) cover the relevant mechanisms in more detail.
- [Claude Agent SDK versus Pydantic AI](claude-agent-sdk-vs-pydantic-ai.md) examines ownership of the agent loop.

## Evidence and coverage limits

English article by Douwe Maan, published by Pydantic on 2026-11-02; the author reports comparing documentation and license files, not an experiment. The publisher has a direct interest in the preferred product. The header says last updated October 29, while the sources section also reports checks on November 2 and November 4; those dates cannot be reconciled from the capture. Framework versions, capture date and article license are unspecified. The sole local artifact, `index.md`, was read; there are no local attachments or includes. External documentation, licenses and comparison pages were not fetched; promotional install text and unrelated framework internals were excluded. No SDK, model, voice pipeline or recovery behavior was executed. Counts, feature status and support terms are time-sensitive.[^pydantic-frameworks-2026]

[^pydantic-frameworks-2026]: “Best Python AI Agent Frameworks in 2026,” frontmatter; “What to look for in an agent framework,” “How we compared,” framework entries 1–9, “Comparison at a glance,” “If you're building voice agents,” and “Sources.” Evidence class: **Reported**, except the explicitly labeled synthesis.
