---
type: Concept
title: Pydantic AI MCP integration
description: Pydantic AI's MCP client defaults — local connections, opt-in provider-native connectors, Streamable HTTP transport, and MCP Apps relayed to AG-UI and Vercel AI frontends.
tags: [ml, pydantic-ai, agents, mcp]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:05:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

In V2 the recommended MCP client path is the `MCP` [capability](pydantic-ai-capability-primitive.md), and its default changed in a security-relevant way: it connects to the server locally, in your process, and `native=True` opts into the provider's own MCP connector, where the provider calls the server instead[^dd-v2-tour-2026] The lower-level `MCPToolset` remains available over Streamable HTTP. V2 also replaced the per-transport server classes with one `MCPToolset`[^dd-v2-tour-2026]

## Two client shapes

| Shape | Declaration | Who talks to the MCP server |
| --- | --- | --- |
| Capability, default | `capabilities=[MCP(url=..., id=...)]` | Your process, locally |
| Capability, native | `MCP(url=..., id=..., native=True)` | The model provider |
| Toolset | `toolsets=[MCPToolset('http://localhost:8000/mcp', id=...)]` | Your process |

Streamable HTTP is the recommended transport. SSE is still supported, and URLs ending in `/sse` are detected automatically; the MCP specification's 2025-03-26 revision replaced the older HTTP+SSE transport, so new servers should expose Streamable HTTP. The integration also runs the other way: an agent can be served inside an MCP server[^dd-v2-tour-2026]

## MCP Apps

v2.57.0 added MCP Apps support. `MCPToolset.call_tool_for_app` relays tool calls from MCP Apps and `MCPToolset.read_resource_contents` reads resources. Results are forwarded to AG-UI frontends as an `ACTIVITY_SNAPSHOT` with activity type `mcp-apps`, and to Vercel AI frontends as a `data-mcp-apps` chunk. Tools whose `_meta.ui.visibility` leaves out `'model'` are not exposed to the model at all, so UI-only tools stay out of the model's context[^dd-v2-tour-2026]

On the frontend side, `VercelAIAdapter` speaks the Vercel AI Data Stream Protocol, so a `useChat` frontend can drive an agent; it targets AI SDK v5 by default and `sdk_version=6` enables v6 features. v2.57.0 stopped emitting unset optional fields in `UIMessage` JSON, which the AI SDK had been rejecting[^dd-v2-tour-2026]

## Security note

MCP configuration has been a leak path: v2.58.0 fixed GHSA-xv4x-g8mx-ch56, rated medium, where provider-native MCP configuration could expose server URLs and authorization tokens in telemetry[^dd-v2-tour-2026] The advisory list and upgrade guidance live in [Pydantic AI v2 release](pydantic-ai-v2-release.md).

## Limits

- No MCP server, App, or frontend was run in this ingest; the article's MCP snippet was type-checked, and the App relay is described from release notes[^dd-v2-tour-2026]
- The security difference between local and native connectors beyond the telemetry advisory — credential handling, network egress, prompt-injection surface — is not analysed.
- The AI SDK v5/v6 compatibility statement is a claim about the adapter, not a tested frontend integration.
- Evidence class: **Reported**.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md); `MCP` is a core capability.
- **Exposes** configuration to [observability](pydantic-ai-observability.md) telemetry, which is where the v2.58 advisory applied.
- **Feeds** frontends that [Pydantic Evals](pydantic-evals.md) cannot see when tools run provider-side.
- **Runs opposite to** [Logfire MCP server](logfire-mcp-server.md): this page is Pydantic AI consuming an MCP server, while that one is a hosted MCP server consumed by a coding agent.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"MCP: local by default, native opt-in, and MCP Apps (v2.57)" (raw lines 560–593) for the local-versus-native default, `MCPToolset`, Streamable HTTP and SSE detection, MCP Apps relay, UI-only tool visibility, and `VercelAIAdapter`; §"What changed in v2.58 and v2.59" for GHSA-xv4x-g8mx-ch56; §"What changed in V2, in one table" for the single `MCPToolset` replacement. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — docs summary and release-note summary; no MCP client, server, or frontend was exercised.
