---
type: Concept
title: Pydantic AI MCP server
description: Serving a Pydantic AI agent from an MCP server — the FastMCP tool that wraps an agent run, and MCPSamplingModel, which reverses the LLM call so the connected client supplies the completion through its own sampling handler.
tags: [pydantic-ai, mcp, agents, models]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:14:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-mcp-server
    resource: ../raw/mcp/server/index.md
    scope: ../raw/mcp/server/
    kind: docs
    title: "Server"
---

Pydantic AI runs on both sides of MCP, and this is the server side: a tool on a FastMCP server calls `agent.run(...)`, so an MCP client that asks for a poem gets an agent run instead of a hand-written function[^pydantic-docs-mcp-server] The same agent can then drop its own model and pass an `MCPSamplingModel(session=ctx.session)` per run, which makes the *client* perform the LLM call — the server becomes a broker of instructions and conversation history, not a holder of model credentials[^pydantic-docs-mcp-server] The client half of the protocol, including the `sampling_model` a client needs to answer that call, is [Pydantic AI MCP client](pydantic-ai-mcp-client.md); the layer choice for consuming servers is [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md).

## An agent inside a server tool

The wiring is three pieces: a `FastMCP` server, an `Agent` built at module scope, and a `@server.tool()` coroutine that awaits `agent.run()` and returns `r.output`[^pydantic-docs-mcp-server]

- `FastMCP('Pydantic AI Server')` from `mcp.server.fastmcp`, then `server.run()` under `if __name__ == '__main__':`, which the sampling sample's comment identifies as serving over stdio.
- `Agent('anthropic:claude-haiku-5-5', instructions='always reply in rhyme')` — an ordinary agent, model string and instructions included, constructed once outside the tool.
- `@server.tool()` on `async def poet(theme: str) -> str` with the docstring `"""Poem generator"""`, which is the tool description the client's model sees; the body formats the theme into a prompt and returns `r.output`, the V2 result field ([capability primitive](pydantic-ai-capability-primitive.md) records `result.output` as V2's).

No Pydantic AI MCP class appears on this side. The server is the MCP Python SDK's FastMCP; Pydantic AI supplies the tool's *body*, and the agent's own tool calls, if any, run in the server process.

## What any MCP client sees

The second sample is a plain Python-SDK client, deliberately not Pydantic AI: `StdioServerParameters(command='python', args=['mcp_server.py'], env=dict(os.environ))` into `stdio_client`, then `ClientSession(read, write)`, `await session.initialize()`, `await session.call_tool('poet', {'theme': 'socks'})`, and the first content block cast to `TextContent` and printed — which yields a poem about socks[^pydantic-docs-mcp-server] The point is interchangeability: the agent inside the tool is invisible over the wire, so any MCP client works.

## Sampling: the client makes the model call

The third sample keeps the same server shape and removes the model from the agent: `Agent(instructions='always reply in rhyme')`, with the tool taking `ctx: Context` as well as `theme` and passing `model=MCPSamplingModel(session=ctx.session)` to `run()`[^pydantic-docs-mcp-server] The docs frame it as the agent calling back through the MCP client to make LLM calls instead of connecting to the LLM directly[^pydantic-docs-mcp-server]

| Piece | Direct server | Sampling server |
| --- | --- | --- |
| Agent model | `'anthropic:claude-haiku-5-5'` at construction | none; `MCPSamplingModel(session=ctx.session)` per `run()` |
| Tool signature | `poet(theme: str)` | `poet(ctx: Context, theme: str)`, because the session comes from `ctx` |
| Who executes the LLM call | the server process | the connected client's sampling handler |
| What the server needs | provider credentials | a client that supports sampling |

**[Synthesis]** The consequence the docs do not spell out: with sampling the server never selects a model vendor, holds its API key, or pays for the completion — the client's handler decides all three, and the returned `CreateMessageResult` carries a `model` field naming whichever model the client used.

`MCPSamplingModel` is named as a model class with an API-reference page of its own, so it is selected the same way a provider model is — through the run's `model=` argument — rather than through the `<provider>:<model>` string covered by [models and providers](pydantic-ai-models-and-providers.md)[^pydantic-docs-mcp-server]

### Continuing another model's conversation

The sampling agent can pick up a conversation that a different model started, by passing that model's `message_history` to `run()`. Three limits come with it[^pydantic-docs-mcp-server]

- Function tool calls, tool results and retry feedback in that history are preserved using MCP's native tool content blocks — which requires a client implementing the **2025-11-25** sampling format or later. An older client sees a history it cannot represent.
- Multimodal tool results are not yet supported.
- Replaying tool history does not let the sampling agent call new tools: the history is context, not capability. A sampling request carries no toolset of its own.

## What the client must do

The simple stdio client above cannot answer a sampling request, and the docs say using it with the sampling server produces an error — without naming the error[^pydantic-docs-mcp-server] Two routes are documented for clients that can[^pydantic-docs-mcp-server]

1. **A Pydantic AI agent as the client**, which the docs call the simplest option: its toolset's `sampling_model` (or `agent.set_mcp_sampling_model()`) supplies the completion, as recorded in [Pydantic AI MCP client](pydantic-ai-mcp-client.md).
2. **The vanilla MCP SDK**, by passing `sampling_callback=` to `ClientSession(read, write, sampling_callback=sampling_callback)`. The callback receives a `RequestContext[ClientSession, Any]` and `CreateMessageRequestParams`, and returns either a `CreateMessageResult` or `ErrorData`.

The sample callback shows what crosses the wire: `params.systemPrompt` is the sampling agent's own instructions (`always reply in rhyme`), and `params.messages` is a single `SamplingMessage` with role `user` and a `TextContent` holding `write a poem about socks`[^pydantic-docs-mcp-server] The callback returns `CreateMessageResult(role='assistant', content=TextContent(type='text', text=...), model='fictional-llm')` — in the sample the response text is hard-coded behind a `# TODO get the response content by calling an LLM`, and the tool then returns that text to the caller unchanged[^pydantic-docs-mcp-server] Agent instructions therefore arrive at the client as a sampling system prompt, and agent-side prompt text is what a client operator sees.

## Limits

- Single vendor page (569 words as declared, 620 by local `wc -w`) naming **no Pydantic AI version, FastMCP version, MCP SDK version or publication date**, so the page is `draft` under the `pydantic-ai` domain rule and every API name here is version-unknown[^pydantic-docs-mcp-server]
- The only version statement is MCP's **2025-11-25** sampling format, required for tool history replay; the protocol revision the server speaks otherwise is unstated.
- Coverage: `raw/mcp/server/` holds that one `index.md` capture — no attachments, includes, downloads or supporting files. Its links (the Python MCP SDK on GitHub, the `MCPSamplingModel` API reference, the client page's `#mcp-sampling` anchor) were read as links, not followed, so `MCPSamplingModel`'s parameters and its current status are not evidence here.
- The capture is four examples and a paragraph, not a server-side reference: error shaping, resource and prompt declaration, task declaration, authentication, HTTP transports and result content types are all absent. The client capture names several of them only from the client's side of the protocol.
- The samples' model alias `anthropic:claude-haiku-5-5` is pinned nowhere and appears nowhere else in this wiki; the second sample's `'fictional-llm'` is a placeholder, not a model.
- Unstated and load-bearing: whether an `Agent` built with no model at all raises until `model=` is supplied, what error a non-sampling client provokes, whether sampling works over Streamable HTTP as well as stdio, and how a server discovers a client's sampling-format support.
- The vendor marks the sampling pair complete and runnable "as is"; nothing was installed, no server started, no client connected, no sampling request answered and no agent run executed, so every claim is **Reported** and none **Observed** or **Reproduced**.

## Relationships

- **Runs opposite to** [Pydantic AI MCP client](pydantic-ai-mcp-client.md): that page is the client that answers `sampling/createMessage` through `sampling_model` or `set_mcp_sampling_model()`; this one is the server that issues the request from inside a tool.
- **Completes the second direction named by** [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md): that page states that an agent can be served inside an MCP server and records the direction without the mechanism; this page is the mechanism.
- **Uses** a model implementation where [models and providers](pydantic-ai-models-and-providers.md) describe provider models: `MCPSamplingModel` is selected per run and delegates the request to the client rather than to a provider HTTP API.
- **Differs from** [Logfire MCP server](logfire-mcp-server.md): both are MCP servers, but that one exposes traces to a coding agent, while this one puts your own agent behind a tool.
- **Requires a client feature that** [Pydantic AI MCP client](pydantic-ai-mcp-client.md) implements only through `sampling_model`, so a server deployed with sampling and consumed by a non-sampling client fails at call time rather than at connection time.

[^pydantic-docs-mcp-server]: Pydantic Docs, "Server" (https://pydantic.dev/docs/ai/mcp/server/; declared 569 words, 620 by local `wc -w`; no publication date and no Pydantic AI, FastMCP or MCP SDK version stated), local capture `raw/mcp/server/index.md` (content digest sha256:b191ea11). §"MCP Server" (lines 13–37) for the `FastMCP` name, the module-scope `Agent('anthropic:claude-haiku-5-5', instructions='always reply in rhyme')`, the `@server.tool()` `poet` coroutine with its docstring, the `f'write a poem about {theme}'` prompt, `return r.output`, and `server.run()`; §"Simple client" (lines 39–73) for the vanilla `StdioServerParameters`/`stdio_client`/`ClientSession`/`initialize`/`call_tool` sequence, the `TextContent` cast and the printed poem; §"MCP Sampling" (lines 75–170) for `MCPSamplingModel` in the `model=` argument beside `ctx: Context` and `ctx.session`, the model-less `Agent(instructions='always reply in rhyme')`, the stdio comment, the statement that the simple client errors on a sampling server, the Pydantic AI client as the simplest sampling client, the `message_history` continuation with its 2025-11-25 format requirement, unsupported multimodal tool results and no new tools on replay, and the vanilla `sampling_callback` with `CreateMessageResult`/`ErrorData`, `params.systemPrompt`, `params.messages`, the TODO placeholder and `model='fictional-llm'`; line 170 for the runnable-as-is claim. Evidence class: **Reported** — four vendor samples; nothing was installed, served, connected or executed.
