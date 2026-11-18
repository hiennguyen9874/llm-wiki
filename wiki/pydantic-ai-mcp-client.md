---
type: Concept
title: Pydantic AI MCP client
description: How Pydantic AI connects out to MCP servers — the five `MCPToolset` inputs and four transports, the `init_timeout` and `read_timeout` deadlines an MCP tool gets instead of a tool timeout, JSON config loading with `${VAR}` expansion, tool-error behaviour, prefixes and instruction ids, resources and MCP Apps relay, and the server-initiated sampling and elicitation handlers.
tags: [pydantic-ai, mcp, agents, tools]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:42:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-mcp-client
    resource: ../raw/mcp/client/index.md
    scope: ../raw/mcp/client/
    kind: docs
    title: "Client"
  - id: pydantic-docs-timeouts
    resource: ../raw/core-concepts/timeouts/index.md
    scope: ../raw/core-concepts/timeouts/
    kind: documentation
    revision: sha256:f05691956599cfeccf1de6aa3383a528e516d06310baf5db2d282edda7bd852f
    title: "Timeouts"
---

Pydantic AI is an MCP client through one class: an `MCPToolset` wraps the FastMCP `Client` and accepts a URL, a local script path, a FastMCP transport, a pre-built `fastmcp.Client`, or an in-process `FastMCP` server as its first positional argument, then plugs into an `Agent` through `toolsets=[...]`[^pydantic-docs-mcp-client] This page is the client surface below the capability: transports and lifecycle, config-file loading, tool-call rewriting, error routing, names and instructions, resources and Apps, authentication, and the two requests a server sends back to the client (sampling and elicitation). The layer choice and the capability's own `id`/`tool_prefix`/per-user settings are on [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md).

## One class, five inputs

`MCPToolset`'s first positional argument decides the transport, and the docs recommend Streamable HTTP for remote servers[^pydantic-docs-mcp-client]

| Input | Transport | Notes |
| --- | --- | --- |
| URL string | Streamable HTTP, or SSE when the path ends in `/sse` | Recommended remote route; `/sse` is auto-detected |
| Path to a Python or Node.js script | stdio | Runs the script as a subprocess |
| `StdioTransport` / `StreamableHttpTransport` / `SSETransport` | as named | Full control over command, arguments and environment |
| `fastmcp.Client` | as configured | For FastMCP-specific configuration the wrapper does not expose, such as OAuth or tool transformation |
| In-process `FastMCP` server | none | Saves the network round trip; testing and single-process deployments |

The local transports need the `mcp` optional group: `pip install "pydantic-ai-slim[mcp]"`[^pydantic-docs-mcp-client] For any transport other than `/sse` auto-detection, an `SSETransport` must be passed explicitly[^pydantic-docs-mcp-client]

### Lifecycle and identity

`async with agent:` opens every registered MCP toolset for the block and closes them at the end, starting and stopping stdio subprocesses; `async with toolset:` manages one toolset directly, which is what you do to share it across several agents. Without either context manager the toolset opens and closes as needed[^pydantic-docs-mcp-client]

A shared `MCPToolset` connects as a **single identity**. Users with their own credentials need the function form of `auth` instead (see [per-user authentication](#per-user-authentication))[^pydantic-docs-mcp-client]

### The two deadlines an MCP tool has

An MCP tool is bounded by neither `Agent(tool_timeout=...)` nor a per-tool `timeout=`, because those are enforced by `FunctionToolset` and a remote toolset is not one[^pydantic-docs-timeouts] What remains are two `MCPToolset` arguments, whose defaults are wide enough to matter[^pydantic-docs-timeouts]:

| Argument | Bounds | Default | On expiry |
| --- | --- | --- | --- |
| `init_timeout` | Connecting and the `initialize` handshake | `5` seconds | The connection fails |
| `read_timeout` | A single MCP request | `300` seconds | The request fails; under the default `tool_error_behavior='retry'` the model sees a retryable tool error |

The second is the one worth reviewing (**Synthesis**): five minutes is far longer than a normal agent step, so a hung server holds the run open unless `read_timeout` is lowered — and lowering it puts the failure into the `tool_error_behavior` table below rather than into a timeout error the run raises[^pydantic-docs-timeouts]

## Loading toolsets from configuration

`load_mcp_toolsets('mcp_config.json')` builds several toolsets from a JSON file with an `mcpServers` object, keyed per server, so servers can be configured outside the code[^pydantic-docs-mcp-client]

- A stdio entry takes `command`, `args`, `env`, `cwd`; an HTTP entry takes `url` and `headers`.
- An entry carrying both `command` and `url` runs the command and ignores `url`/`headers`, as FastMCP does.
- The config is validated as loaded, so a wrongly typed field fails immediately instead of at connection time.
- Unknown keys are ignored, never honoured: `disabled` does not skip a server and `type` does not choose the transport, which is inferred from the URL — including the `/sse` suffix rule.
- `${VAR}` and `${VAR:-default}` expand from the environment, which is the documented way to keep API keys and hostnames out of the file[^pydantic-docs-mcp-client]

## Tool calls, errors and names

`process_tool_call` receives the run context, the `call_tool` callable, the tool name and the arguments, and may rewrite both request and response — the documented use being metadata injection, passed as `await call_tool(name, tool_args, metadata={'deps': ctx.deps})` and read on the server from its request context (`ctx.request_context.meta` with the MCP Python SDK). How the server reads that metadata is server-SDK specific[^pydantic-docs-mcp-client]

An MCP tool error is routed by `tool_error_behavior`, the client-side twin of the local tool retry-versus-failed distinction[^pydantic-docs-mcp-client]

| `tool_error_behavior` | Result |
| --- | --- |
| `'retry'` (default) | Raises `ModelRetry`, sending the server error back to the model as a retried tool result |
| `'failed'` | Raises `ToolFailed`, recorded as a tool result with `outcome='failed'` and left to the model |
| `'error'` | Propagates the MCP tool exception and fails the agent run, for application code to handle |

Structured error content is serialized as JSON in the model-visible message for `'retry'` and `'failed'`, so retryability hints survive; protocol and transport errors are not reported as completed failed tool calls[^pydantic-docs-mcp-client] Server-side error shaping is the [MCP server](https://pydantic.dev/docs/ai/mcp/server/) surface, which is a sibling capture this wiki has not compiled.

Naming conflicts across servers are handled by wrapping a toolset with `.prefixed('weather')`, so two servers' `get_data` become `weather_get_data` and `calc_get_data`; the [MCP capability](pydantic-ai-mcp-integration.md) does the same with `tool_prefix`[^pydantic-docs-mcp-client]

### Server instructions and the toolset `id`

`MCPToolset.instructions` holds what the server sends at initialization, and `include_instructions=True` adds it to the agent's instructions. On the toolset that flag is **off by default**, because the server writes the text and the model receives it with the same authority as your own instructions — enable it only for trusted servers. The capability turns it on for the local toolset it builds, so an untrusted server behind the capability needs `include_instructions=False`[^pydantic-docs-mcp-client]

Instructions are read each time the toolset connects, once per agent run by default, and with an `id` their changes are **appended** rather than replacing the cached instruction prefix; the model sees them in a `<pyai:context id="toolset:<id>">` element naming the source server. A URL toolset without an `id` takes the URL's hostname as its id (IPv6 with `-` for `:`), but only an explicit `id` is stamped on the tool definitions as `toolset_id`, and [durable execution](pydantic-ai-durable-execution.md) rejects a derived one. Two toolsets that would share a hostname keep the id for neither: their instructions rewrite the prefix as plain text and a warning asks for a distinct `id=` each. A stdio or in-process toolset without an `id` has nothing to key instructions by, so it must be given one to get append behaviour[^pydantic-docs-mcp-client]

### Tool metadata

MCP `meta` and `annotations` appear in the `metadata` dict of the `ToolDefinition` passed to [toolset](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/) filter functions, the tool's output schema is `return_schema`, and `task: bool` says whether the toolset will use task-augmented execution (reflecting `prefer_tasks` where task support is optional). Tools whose MCP Apps `_meta.ui.visibility` leaves out `"model"` are not exposed to the model at all[^pydantic-docs-mcp-client]

## Background tasks

MCP task-augmented execution (SEP-1686) is negotiated per tool through `execution.taskSupport`[^pydantic-docs-mcp-client]

| `execution.taskSupport` | Client behaviour |
| --- | --- |
| `"required"` | Always `task=True`; the server creates a task and the client awaits `tasks/result` |
| `"optional"` | `task=True` by default; `prefer_tasks=False` calls normally instead |
| `"forbidden"` or absent | Calls normally |

The version split matters: SEP-1686 covers FastMCP 3 servers, while FastMCP 4 uses the MCP Tasks extension (SEP-2663) where the server directs task creation, so `task` and `prefer_tasks` apply to FastMCP 3 only. An ordinary call still drives a task-only tool to completion; explicitly selecting the tasks extension with `use_task=True` needs the separate `fastmcp-tasks` package via `pip install "pydantic-ai-slim[mcp-tasks]"`. A FastMCP 3 server declares support per tool with `task=TaskConfig(mode=...)` and needs `pip install "fastmcp[tasks]>=3,<4"`[^pydantic-docs-mcp-client]

## Resources

Resources are application-driven: the server exposes files and data, and host applications decide what context to give the model. They are **not** exposed to the LLM automatically unless a tool returns a `ResourceLink` or `EmbeddedResource`[^pydantic-docs-mcp-client]

- `list_resources()` and `list_resource_templates()` for discovery, the latter with parameter placeholders.
- `read_resource(uri)` for one resource, returned as `str` for text and `BinaryContent` for binary.
- `read_resource_for_app(uri)` for the MCP result as-is, keeping each item's MIME type and `_meta`[^pydantic-docs-mcp-client]

## MCP Apps

An MCP App is an HTML page the server attaches to a tool through `_meta.ui.resourceUri`. Pydantic AI does not render it; it hands the frontend what it needs[^pydantic-docs-mcp-client]

- When an app tool is called, the `ToolReturn` carries an `MCPAppToolResult` in `metadata['mcp_app']`: the resource URI, the model's arguments, the full MCP result with `structuredContent` and `_meta`, and the toolset `id`. The model does not see it; the AG-UI and Vercel AI adapters forward it.
- A `process_tool_call` hook that changes the result or skips the call prevents the attachment, and a `WrapperToolset` around the toolset gets the `ToolReturn`, so it should edit `return_value` and drop `metadata` when the page must not see the original.
- The backend gives the page three things: `read_resource_for_app(uri)` for the HTML and its `_meta.ui` CSP/permissions, `call_tool_for_app(name, arguments)` for page-initiated tool calls (MCP results as-is, `isError` included, only tools whose `_meta.ui.visibility` includes `"app"` or omits visibility, and `process_tool_call` does not apply), and `read_resource_for_app` again for resource reads.
- Protocol errors raise `MCPError`, whose `code`, `message` and `data` are sent back to the page as the JSON-RPC error; other failures such as an unreachable server propagate unchanged.
- Use one `MCPToolset` per server and keep it entered while pages are open, so requests do not reconnect.
- `capabilities.extensions` lists the extensions a server supports, and MCP Apps servers list `'io.modelcontextprotocol/ui'`. Some servers only offer app tools to clients that advertise the extension, which `MCPToolset` does not do by default: on FastMCP 4 pass a `Client` built with `advertise(...)`; FastMCP 3 clients cannot[^pydantic-docs-mcp-client]

## HTTP authentication

For HTTP transports, `auth` accepts a bearer-token string, any `httpx2.Auth` (legacy `httpx.Auth` on FastMCP 3), the literal `'oauth'` for FastMCP's OAuth flow, or a function returning credentials per agent run. Static headers such as API keys go through `headers` instead[^pydantic-docs-mcp-client]

### Per-user authentication

In a multi-tenant application the token cannot be fixed at construction, so `auth` takes a function called with the run's `RunContext` at the start of each run, reading the user's token from the run's [dependencies](pydantic-ai-dependencies.md). Each run then opens its own MCP session with the returned credentials, so concurrent runs for different users never share a session. The function may be sync or async and may return anything a fixed `auth` accepts except `'oauth'`; `headers` accepts a function the same way[^pydantic-docs-mcp-client]

Three consequences the docs call out[^pydantic-docs-mcp-client]

- Each session gets its own HTTP client unless you pass `http_client`, in which case every run's session goes through that one client and shares its cookie jar — so a cookie the server sets for one user is replayed on later users' requests. Do not share an `http_client` across users; pass the toolset's `verify` argument for TLS instead.
- Because credentials are only known once a run has started, the toolset connects **inside** an agent run: `async with toolset:` or `async with agent:` does not open a connection, and calling `list_tools()` directly raises `UserError`. Outside a run, use the copy a run would use, from `await toolset.for_run(ctx)`.
- With the [MCP capability](pydantic-ai-mcp-integration.md), pass the function as `authorization_token` or `headers`; if users need more than credentials, such as their own server URL, build the whole toolset per run with a dynamic toolset (`@agent.toolset` with `per_run_step=False`)[^pydantic-docs-mcp-client]

## TLS, client identity and per-call models

- **TLS/mTLS.** `http_client` takes a pre-configured `httpx2.AsyncClient`, so an internal CA (`ssl.create_default_context(cafile=...)`), a client certificate (`load_cert_chain`) or, in local development only, disabled verification applies to all MCP traffic. The toolset never closes the client, so reuse and closing are yours. On FastMCP 3, build the client with legacy `httpx`[^pydantic-docs-mcp-client]
- **Client identification.** `client_info=mcp_types.Implementation(name=..., version=...)` is sent during initialization, for server logs, client-specific behaviour, debugging and feature negotiation[^pydantic-docs-mcp-client]
- **Sampling.** A server can call back for an LLM completion (`ctx.session.create_message(...)`), and the client answers only if the toolset has a `sampling_model` — set on the toolset directly or on every registered toolset with `agent.set_mcp_sampling_model()`, the second using the agent's own model unless an argument overrides it[^pydantic-docs-mcp-client] The server side of that request is [Pydantic AI MCP server](pydantic-ai-mcp-server.md).

## Elicitation

Elicitation lets a server ask the client for structured input mid-session: the server sends an `ElicitRequest`, the client presents it to the user, and the user accepts, declines or cancels, which the client returns as an `ElicitResult` with the data or the decision[^pydantic-docs-mcp-client]

Provide `elicitation_handler` when constructing the toolset. The handler receives the message, the response type, the `ElicitRequestParams` and a context object, and it must distinguish form requests (`ElicitRequestFormParams` with a `requestedSchema`) from other params, collect the schema's properties itself — the documented sample prompts a terminal per field and casts `integer` values — and return `ElicitResult(action='accept', content=...)`, `action='decline'` or `action='cancel'`[^pydantic-docs-mcp-client]

Two limits the docs state: elicitation schemas support string, number, boolean and enum types in **flat** object structures only, for cross-client compatibility; and servers must not request sensitive information while clients must implement user approval with clear explanations[^pydantic-docs-mcp-client]

## Contradictions

- **The MCP Apps resource read has two names.** The v2.57.0 release summary compiled in [Pydantic AI v2 release](pydantic-ai-v2-release.md) names `MCPToolset.read_resource_contents`, while this client page names `read_resource_for_app` for the app-shaped MCP result and keeps `read_resource(uri)` for the text-or-`BinaryContent` form[^pydantic-docs-mcp-client] The capture states no version, so which name is current is unresolved here; the newer-looking pair is the one that keeps `_meta`, but the wiki does not assert a rename.

## Limits

- Single vendor docs page for Pydantic AI's own client, naming **no framework version**, no publication date and no MCP specification revision for the client behaviour, so the page is `draft` under the `pydantic-ai` domain rule and every API name is version-unknown.
- Coverage: `raw/mcp/client/` holds that one `index.md` capture — no attachments, includes, downloads or supporting files. Its 58 pydantic.dev links, 15 modelcontextprotocol.io, 14 gofastmcp.com and the httpx2/httpx/GitHub/Claude Code links were read as links, not followed; the linked API reference for `MCPToolset` parameters is therefore not evidence here.
- Server-side behaviour is compiled separately: the sibling `raw/mcp/server/index.md` capture is [Pydantic AI MCP server](pydantic-ai-mcp-server.md), which documents a server tool wrapping an agent run and `MCPSamplingModel` asking this page's `sampling_model` for a completion. Error shaping, resource declaration and task declaration remain un-inspected from the server's side, so they are named here only as the client handles them.
- The docs name three model aliases (`openai:gpt-6.1-sol`) and FastMCP majors (3 and 4) without pinning Pydantic AI, FastMCP or MCP versions, and the FastMCP-3-versus-4 task split is the one place where the version boundary is stated.
- `client_info`'s list of uses is aspirational prose: no server-side behaviour keyed on the client was inspected.
- No package was installed, no toolset constructed or entered, no server contacted, no config file loaded, no sampling or elicitation round trip performed, no app rendered and no TLS handshake made, so every claim is **Reported** and none **Observed** or **Reproduced**.

## Relationships

- **Drops below** [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md): that page owns the capability-versus-toolset decision and the `id`, `tool_prefix`, instructions and per-user capability settings; this one owns what an `MCPToolset` itself accepts and does.
- **Uses** [Pydantic AI dependencies](pydantic-ai-dependencies.md) for per-user credentials, which are read from the run's deps by the `auth`/`headers` function at run start.
- **Depends on** an explicit `id=` under [Pydantic AI durable execution](pydantic-ai-durable-execution.md), which does not accept the hostname-derived id.
- **Continues the tool-error contract of** Pydantic AI's local tools: `'retry'`/`'failed'`/`'error'` route an MCP server error the way `ModelRetry`/`ToolFailed` route a local one.
- **Runs opposite to** [Logfire MCP server](logfire-mcp-server.md): this page is Pydantic AI consuming a server, that one is a hosted server consumed by a coding agent.
- **Answers the sampling request of** an MCP server: [Pydantic AI MCP server](pydantic-ai-mcp-server.md) is the server that issues the completion request through `MCPSamplingModel`, and the two pages meet at `sampling_model`.
- **Is exposed through** the AG-UI and Vercel AI adapters, which relay an `MCPAppToolResult` to a frontend that renders the page itself.

[^pydantic-docs-mcp-client]: Pydantic Docs, "Client" (https://pydantic.dev/docs/ai/mcp/client/; declared 4,654 words, 4,771 by local `wc -w`; no publication date, Pydantic AI version or MCP specification revision stated), local capture `raw/mcp/client/index.md` (content digest sha256:8cc564be). §"Install" and §"Usage" (lines 13–38, 162) for the `pydantic-ai-slim[mcp]` extra, the five `MCPToolset` inputs, the toolset-to-agent wiring, the `async with agent`/`async with toolset` lifecycle and the single-identity warning; §"Streamable HTTP" (39–102) for the recommended transport, the FastMCP Streamable HTTP server sample and the six-step tool-call walkthrough; §"SSE" (103–116) for `/sse` auto-detection and explicit `SSETransport`; §"Stdio" (117–132) and §"In-process FastMCP server" (133–161) for the subprocess and no-network-round-trip routes; §"Loading MCP toolsets from configuration" (162–243) for `load_mcp_toolsets`, the `mcpServers` shape, the `command`/`args`/`env`/`cwd` and `url`/`headers` keys, the both-keys precedence, load-time validation, ignored unknown keys (`disabled`, `type`), URL-inferred transport choice and `${VAR}`/`${VAR:-default}` expansion; §"Tool call customization" (244–314) for `process_tool_call`'s signature, the `metadata` injection and the MCP-Python-SDK `ctx.request_context.meta` read; §"Tool errors" (315–328) for the `tool_error_behavior` table, `ModelRetry`/`ToolFailed`/propagation, JSON-serialized structured error content and the protocol/transport-error exclusion; §"Tool prefixes" (329–348) for `.prefixed()` and the capability's `tool_prefix` cross-reference; §"Server instructions" (349–368) for `instructions`, `include_instructions` being off by default on the toolset and on for the capability's local toolset, per-connection reads, appending with an `id`, the `<pyai:context id="toolset:<id>">` element, hostname ids, `toolset_id` stamping, the durable-execution requirement and the same-hostname warning; §"Tool metadata" (369–376) for `meta`/`annotations`/`return_schema`/`task` and the `_meta.ui.visibility` exclusion; §"Background tasks" (377–420) for the `execution.taskSupport` table, `prefer_tasks`, SEP-1686 versus SEP-2663, the `fastmcp[tasks]` and `mcp-tasks` extras and `TaskConfig`; §"Resources" (421–482) for the application-driven framing, `ResourceLink`/`EmbeddedResource`, the four read/list methods and the `str`/`BinaryContent` split; §"MCP Apps" (483–543) for `MCPAppToolResult` in `metadata['mcp_app']`, `process_tool_call` and `WrapperToolset` interactions, the three frontend needs, `MCPError` codes, one-toolset-per-server and the `extensions`/`advertise` requirement; §"HTTP authentication" (544–547) for the `auth` forms and `headers`; §"Per-user authentication" (548–587) for the `RunContext` function, per-run sessions, the `http_client` cookie-jar warning, `verify`, the no-connection-outside-a-run behaviour, the `UserError` and `for_run(ctx)`, plus the capability's `authorization_token`/`headers` and dynamic-toolset routes; §"Custom TLS / SSL configuration" (588–615) for `http_client`, the CA and mTLS samples, never closing the client and the legacy-`httpx` note; §"Client identification" (616–640) for `client_info` and its stated uses; §"MCP sampling" (641–731) for the sequence, `sampling_model` and `set_mcp_sampling_model()`; §"Elicitation" (732–867) for `ElicitRequest`/`ElicitResult`, the interaction sequence, the `elicitation_handler` signature and sample, accept/decline/cancel, the flat-schema type limit and the security note. Evidence class: **Reported** — vendor documentation naming no version; nothing was constructed, connected, rendered or executed.

[^pydantic-docs-timeouts]: Pydantic Docs, "Timeouts" (<https://pydantic.dev/docs/ai/core-concepts/timeouts/>; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/timeouts/index.md`, content digest sha256:f0569195. §"Bounding how long a step takes" (raw lines 15–27) for the connection row (`MCPToolset(init_timeout=...)`, default `5` seconds, failing the connection and `initialize` handshake) and the request row (`MCPToolset(read_timeout=...)`, default `300` seconds, a failing request that the default `tool_error_behavior='retry'` turns into a retryable tool error); line 36 for the rule that tool timeouts are `FunctionToolset`-only, so an MCP tool reads neither `tool_timeout` nor a per-tool `timeout`. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence; the reading that 300 seconds is long for a step is **Synthesis**.
