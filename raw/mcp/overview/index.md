---
title: "Model Context Protocol (MCP)"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/mcp/overview/"
domain: "pydantic.dev"
language: "en"
description: "Use the Model Context Protocol with Pydantic AI: connect agents to MCP servers as a client, use provider-native MCP tools, or run agents inside an MCP server."
word_count: 430
---

Pydantic AI supports [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) in multiple ways:

1. [Agents](https://pydantic.dev/docs/ai/core-concepts/agent/) can connect to MCP servers and use their tools — see [Use MCP servers](#use-mcp-servers) below.
2. Agents can be used within MCP servers. [Learn more](https://pydantic.dev/docs/ai/mcp/server/)

## What is MCP?

The Model Context Protocol is a standardized protocol that allows AI applications (including programmatic agents like Pydantic AI, coding agents like [cursor](https://www.cursor.com/), and desktop applications like [Claude Desktop](https://claude.ai/download)) to connect to external tools and services using a common interface.

As with other protocols, the dream of MCP is that a wide range of applications can speak to each other without the need for specific integrations.

There is a great list of MCP servers at [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers).

Some examples of what this means:

- Pydantic AI could use a web search service implemented as an MCP server to implement a deep research agent
- Cursor could connect to the [Pydantic Logfire](https://github.com/pydantic/logfire-mcp) MCP server to search logs, traces and metrics to gain context while fixing a bug
- Pydantic AI, or any other MCP client could connect to our [Run Python](https://github.com/pydantic/mcp-run-python) MCP server to run arbitrary Python code in a sandboxed environment

## Use MCP servers

The recommended way to give an agent access to an MCP server is the [`MCP` capability](https://pydantic.dev/docs/ai/capabilities/mcp/). It runs the MCP server locally by default — keeping credentials, hooks, and tracing under your control — and lets you opt into the model provider’s [native MCP support](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/#mcp-server-tool) with a single `native=True` flag, so the same agent works across providers without code changes:

mcp\_capability.py

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import MCP

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[
        # Runs the MCP server locally by default
        MCP(url='https://mcp.example.com/api'),

        # Opt into native MCP — falls back to local if the model doesn't support it
        MCP(url='https://mcp.example.com/other', native=True),
    ],
)
```

Pass a URL as the first argument to enable both the local fallback and (with `native=True`) provider-native MCP. On the local side, `local=` accepts any [`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) input — a URL, FastMCP transport, pre-built `fastmcp.Client`, in-process `FastMCP` server, or local script path. See the [capability documentation](https://pydantic.dev/docs/ai/capabilities/mcp/) for the full set of inputs and configuration options.

For lower-level access — managing the toolset lifecycle directly, sharing one MCP server across multiple agents, or passing advanced transport or client configuration the [`MCP` capability](https://pydantic.dev/docs/ai/capabilities/mcp/) does not expose — use `MCPToolset` directly via `toolsets=[...]`. See the [MCP client documentation](https://pydantic.dev/docs/ai/mcp/client/) for details.

If you only need the model provider’s native MCP support without a local fallback, you can use [`MCPServerTool`](https://pydantic.dev/docs/ai/api/pydantic-ai/native_tools/#pydantic_ai.native_tools.MCPServerTool) as a [native tool](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/#mcp-server-tool) directly.

For building MCP servers with Pydantic AI agents, see the [MCP server documentation](https://pydantic.dev/docs/ai/mcp/server/).
