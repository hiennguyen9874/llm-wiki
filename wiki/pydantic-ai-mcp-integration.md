---
type: Concept
title: Pydantic AI MCP integration
description: Pydantic AI's MCP integration — the capability, `MCPToolset` and `MCPServerTool` layers and when to drop to each, local-by-default and provider-native modes, derived ids, tool prefixes, server-instruction trust, per-user credentials, Streamable HTTP transport, and MCP Apps relay.
tags: [ml, pydantic-ai, agents, mcp]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:35:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: pydantic-docs-mcp-capability
    resource: ../raw/capabilities/mcp/index.md
    scope: ../raw/capabilities/mcp/
    kind: docs
    title: "MCP Capability"
  - id: pydantic-docs-mcp-overview
    resource: ../raw/mcp/overview/index.md
    scope: ../raw/mcp/overview/
    kind: docs
    title: "Model Context Protocol (MCP)"
---

In V2 the recommended MCP client path is the `MCP` [capability](pydantic-ai-capability-primitive.md), and its default changed in a security-relevant way: it connects to the server locally, in your process, and `native=True` opts into the provider's own MCP connector, where the provider calls the server instead[^dd-v2-tour-2026] The capability is documented as *provider-adaptive* and as the primary entry point for MCP: it runs the MCP server locally by default, keeping credentials, hooks, and tracing under your control, and it supports both URL-based servers and direct client, toolset, or transport inputs[^pydantic-docs-mcp-capability] The lower-level `MCPToolset` remains available over Streamable HTTP. V2 also replaced the per-transport server classes with one `MCPToolset`[^dd-v2-tour-2026]

## What the protocol is for

MCP is a protocol rather than a library: it lets AI applications — programmatic agents like Pydantic AI, coding agents like Cursor, and desktop applications like Claude Desktop — reach external tools and services through one interface, so no application needs a bespoke integration per service[^pydantic-docs-mcp-overview] Pydantic AI sits on both sides of that interface. An agent connects out to MCP servers as a client, which is most of this page, and an agent can also be served inside an MCP server so other MCP clients can call it[^pydantic-docs-mcp-overview] The vendor's own examples are a web-search server behind a deep research agent, a coding agent reading traces through the [Logfire MCP server](logfire-mcp-server.md), and any MCP client running Python in the sandboxed Run Python server[^pydantic-docs-mcp-overview]

The value the overview page claims for MCP is integration economics, not capability: a service written once as an MCP server is reachable from every MCP-speaking application, which is why the same Logfire and Run Python servers appear on both the agent and the coding-agent side[^pydantic-docs-mcp-overview] The protocol revision itself is not named in the capture.

## Two client shapes

The three client layers differ in who owns the toolset and the transport, and the vendor's rule for dropping below the capability is concrete[^pydantic-docs-mcp-overview]

| Layer | Declaration | Who talks to the MCP server | Choose it when |
| --- | --- | --- | --- |
| Capability, default | `capabilities=[MCP(url=..., id=...)]` | Your process, locally | The default: local-by-default with provider-native opt-in, and nothing lower-level to manage |
| Capability, native | `MCP(url=..., id=..., native=True)` | The model provider | The provider's connector is preferred, with the local toolset as the fallback |
| Toolset | `toolsets=[MCPToolset('http://localhost:8000/mcp', id=...)]` | Your process | You manage the toolset lifecycle directly, share one MCP server across several agents, or need transport or client configuration the capability does not expose |
| Native tool | `MCPServerTool(...)` | The model provider | Only the provider's native MCP is wanted, with no local fallback |

The portability argument the vendor gives for the capability is that one agent definition spans providers: local is what runs by default and `native=True` is a flag, so the same `Agent(...)` works whether or not the selected model supports native MCP, without code changes[^pydantic-docs-mcp-overview] That is a claim about the capability's ergonomics, not a measurement; the same page also points at the [MCP client documentation](https://pydantic.dev/docs/ai/mcp/client/) for the lower-level surface and the [MCP server documentation](https://pydantic.dev/docs/ai/mcp/server/) for serving an agent, neither of which is captured here.

Streamable HTTP is the recommended transport. SSE is still supported, and URLs ending in `/sse` are detected automatically; the MCP specification's 2025-03-26 revision replaced the older HTTP+SSE transport, so new servers should expose Streamable HTTP. The integration also runs the other way: an agent can be served inside an MCP server[^dd-v2-tour-2026]

## Configuring the capability

The two sides are configured independently. `local=` accepts any `MCPToolset` input — a URL, a `fastmcp.Client`, a transport, an in-process `FastMCP` server, or a script path — and a non-toolset input is wrapped in `MCPToolset` automatically. The native side is backed by `MCPServerTool`, which can also be passed whole as `native=MCPServerTool(...)` when the derived configuration is wrong, for example a different `id`, `authorization_token`, or `description` than the capability would derive[^pydantic-docs-mcp-capability]

- `MCP(url)` runs the server locally, which needs the `mcp` extra (`pydantic-ai-slim[mcp]`).
- `MCP(url, native=True)` prefers the provider's connector and falls back to the local toolset.
- `MCP(url, native=True, local=False)` is strict native-only and therefore does not need the `mcp` extra.
- Passing an explicit `MCPServerTool` as `native=` together with an explicit `local=` configures each side separately, e.g. a provider-relay URL for native and a direct connection for local[^pydantic-docs-mcp-capability]

### The derived `id`

Without an explicit `id=`, the capability uses the server URL's hostname as its `id`, spelled with `-` in place of the colons of an IPv6 address. Only the hostname is used because a URL's path or query can carry a credential. The `id` also names the local toolset and the server's [durable-execution](pydantic-ai-durable-execution.md) operations, so two `MCP` capabilities for servers on the same host would collide: the agent rejects them and asks for an explicit `id=` on each[^pydantic-docs-mcp-capability]

### Tool names and prefixes

By default the model sees each tool under the name the server gives it, so a generic name such as `search` can collide with another server's or your own. `tool_prefix` prepends a prefix joined with `_`. `tool_prefix=True` uses the `id=` you passed, and raises `UserError` without one — the hostname-derived `id` is deliberately never used as a prefix, so the names the model sees are always names you chose. The prefix changes only what the model sees: `allowed_tools` keeps matching the server's own tool names, and the capability `id` and toolset `id` are unchanged, so durable execution and `defer_loading` behave as before. With native MCP the provider names the server's tools, so a prefix applies to the local tools only[^pydantic-docs-mcp-capability]

### Server instructions are trust surface

By default the capability adds the MCP server's instructions to the agent's instructions. The server writes that text and the model receives it with the same authority as the instructions you write yourself, so for a server you do not trust — one your end users supply — pass `include_instructions=False` to leave it out. A pre-built `MCPToolset` passed as `local=` keeps its own `include_instructions`, and in native mode the provider decides what to do with the server's instructions[^pydantic-docs-mcp-capability]

### Per-user credentials

Where each user has their own credentials, one agent can serve all of them: `authorization_token` and `headers` accept a function that is called with the run's `RunContext` at the start of each run, so it can read the current user's token from the run's [dependencies](pydantic-ai-dependencies.md). The returned value is used on both sides — the native `MCPServerTool` is built with it, and the local toolset connects in an MCP session of its own, so concurrent runs never share a session between users. Returning `None` sends no `Authorization` header[^pydantic-docs-mcp-capability]

## MCP Apps

v2.57.0 added MCP Apps support. `MCPToolset.call_tool_for_app` relays tool calls from MCP Apps and `MCPToolset.read_resource_contents` reads resources — the later [MCP client](pydantic-ai-mcp-client.md) capture instead names `read_resource_for_app`, and that naming conflict is recorded there, not resolved here. Results are forwarded to AG-UI frontends as an `ACTIVITY_SNAPSHOT` with activity type `mcp-apps`, and to Vercel AI frontends as a `data-mcp-apps` chunk. Tools whose `_meta.ui.visibility` leaves out `'model'` are not exposed to the model at all, so UI-only tools stay out of the model's context[^dd-v2-tour-2026]

On the frontend side, `VercelAIAdapter` speaks the Vercel AI Data Stream Protocol, so a `useChat` frontend can drive an agent; it targets AI SDK v5 by default and `sdk_version=6` enables v6 features. v2.57.0 stopped emitting unset optional fields in `UIMessage` JSON, which the AI SDK had been rejecting[^dd-v2-tour-2026]

## Security note

MCP configuration has been a leak path: v2.58.0 fixed GHSA-xv4x-g8mx-ch56, rated medium, where provider-native MCP configuration could expose server URLs and authorization tokens in telemetry[^dd-v2-tour-2026] The advisory list and upgrade guidance live in [Pydantic AI v2 release](pydantic-ai-v2-release.md).

## Limits

- The client capture `raw/mcp/client/index.md` is compiled at [Pydantic AI MCP client](pydantic-ai-mcp-client.md) and the sibling `raw/mcp/server/index.md` at [Pydantic AI MCP server](pydantic-ai-mcp-server.md), so both halves of the integration are now inspected; what neither capture states is a Pydantic AI, FastMCP or MCP specification version.
- The overview page names no Pydantic AI version, no MCP specification revision, and no publication date, so the layer-choice table inherits the same version-unknown status as the rest of the page.
- The MCP-capability vendor page names no Pydantic AI version at all, so every configuration detail above is version-unknown; the page is therefore `draft` under the `pydantic-ai` domain rule rather than `stable`.
- "Provider-adaptive" was asserted here without a definition because `raw/capabilities/overview/` was outside those ingests; it is now compiled in [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md), which records the `native=`/`local=` vocabulary, the per-capability fallback table, the constructor-time `UserError` for a missing optional extra, and the rule that a native-only constraint field locks the capability to the native path. What that page still does not state is the resolution algorithm itself: whether native is chosen from the model profile, from provider support, or per request, and what happens when an enabled native tool is rejected mid-run.
- No capability, `MCPServerTool`, `MCPToolset`, or MCP server was constructed; neither the same-host rejection nor the `tool_prefix=True` `UserError` was triggered, and no per-user session or durable-execution operation was observed, so the whole configuration surface is **Reported**[^pydantic-docs-mcp-capability]
- No MCP server, App, or frontend was run in this ingest; the article's MCP snippet was type-checked, and the App relay is described from release notes[^dd-v2-tour-2026]
- The security difference between local and native connectors beyond the telemetry advisory — credential handling, network egress, prompt-injection surface — is not analysed.
- The AI SDK v5/v6 compatibility statement is a claim about the adapter, not a tested frontend integration.
- Evidence class: **Reported** for all three sources; nothing here is **Observed** or **Reproduced**.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md); `MCP` is a core capability, and the native-or-local fallback is the same shape as the image generation capability's.
- **Drops to** a bare `MCPToolset` for the vendor's three cases — direct lifecycle management, one server shared by several agents, or transport/client configuration the capability does not expose — while keeping the same toolset underneath; what that toolset itself accepts is [Pydantic AI MCP client](pydantic-ai-mcp-client.md), which holds the transports, config loading, error routing, resources, Apps relay, sampling and elicitation detail, so the two pages share the `id`, prefix, instructions and per-user concepts without restating them.
- **Names** its [durable-execution](pydantic-ai-durable-execution.md) operations and its local toolset by the same `id`, which is why ids must be unique per host and why prefixes never touch them.
- **Exposes** configuration to [observability](pydantic-ai-observability.md) telemetry, which is where the v2.58 advisory applied.
- **Feeds** frontends that [Pydantic Evals](pydantic-evals.md) cannot see when tools run provider-side.
- **Is inverted by** [Pydantic AI MCP server](pydantic-ai-mcp-server.md): the same agent can sit inside an MCP server, either holding its own model or — with `MCPSamplingModel` — asking the connected client, which is this page's `MCPToolset` with a `sampling_model`, to make the call.
- **Runs opposite to** [Logfire MCP server](logfire-mcp-server.md): this page is Pydantic AI consuming an MCP server, while that one is a hosted MCP server consumed by a coding agent.
- **Is an instance of** [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md): `MCP` is the one provider-adaptive capability whose default is local, and the reason is that it carries credentials.
- **Configured at its native half by** [native tool configuration](pydantic-ai-native-tool-configuration.md), which records the `MCPServerTool` public-URL requirement, the three providers that host it, and the slots Anthropic does not accept (`description`, `headers`).
- **Loses its session at the activity boundary under** [Pydantic AI on Temporal](pydantic-ai-temporal.md): each activity connects its own session and `cache_tools` covers only that activity, while the recorded `get_tools` result keeps discovery to one activity per run.

[^pydantic-docs-mcp-overview]: Pydantic Docs, "Model Context Protocol (MCP)" (https://pydantic.dev/docs/ai/mcp/overview/; declared 430 words, 477 by local `wc -w`; no publication date or version stated), §intro for the two-way support list (agents as MCP clients; agents inside MCP servers); §"What is MCP?" for the protocol definition, the programmatic-agent/coding-agent/desktop-app audience, the no-bespoke-integration goal, and the web-search, Logfire and Run Python examples; §"Use MCP servers" for the capability as the recommended path with the local-default/`native=True` rationale and the same-agent-across-providers claim, the first-positional-URL behaviour, the `MCPToolset` escape hatches (direct lifecycle management, one server across several agents, advanced transport or client configuration), and `MCPServerTool` as the native-only route. Local capture: `raw/mcp/overview/index.md` (content digest sha256:f9f4634d), lines 11–58. Evidence class: **Reported** — vendor documentation naming no release version; no capability, toolset, server or native tool was constructed.

[^pydantic-docs-mcp-capability]: Pydantic Docs, "MCP Capability" (https://pydantic.dev/docs/ai/capabilities/mcp/; no version or revision stated in the capture), §intro for the provider-adaptive framing, the `MCPServerTool` native backing, the `local=` inputs, and the hostname-derived `id` including the IPv6 spelling, credential-in-path reasoning, and same-host rejection; §"Tool names" for `tool_prefix`, the `tool_prefix=True`-needs-`id` `UserError`, and the untouched `allowed_tools`/`id`/`defer_loading` semantics; §"Server instructions" for instructions being added by default, their equal authority, and `include_instructions=False`; §"Per-user credentials" for the `RunContext` function form, the shared value across native and local, per-user sessions, and the `None` case. Local capture: `raw/capabilities/mcp/index.md`, lines 22–122. Evidence class: **Reported** — vendor documentation naming no release version; nothing was constructed or triggered.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"MCP: local by default, native opt-in, and MCP Apps (v2.57)" (raw lines 560–593) for the local-versus-native default, `MCPToolset`, Streamable HTTP and SSE detection, MCP Apps relay, UI-only tool visibility, and `VercelAIAdapter`; §"What changed in v2.58 and v2.59" for GHSA-xv4x-g8mx-ch56; §"What changed in V2, in one table" for the single `MCPToolset` replacement. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — docs summary and release-note summary; no MCP client, server, or frontend was exercised.
