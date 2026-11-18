---
type: Concept
title: Pydantic AI third-party tool bridges
description: How a Pydantic AI agent reuses tools that belong to another library — tool_from_langchain for one LangChain tool and LangChainToolset for a whole toolkit, the packages each needs, the argument validation Pydantic AI gives back to the library, and the MCP and capability doors the vendor points at instead.
tags: [pydantic-ai, agents, tools, integrations]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:35:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-third-party-tools
    resource: ../raw/tools-toolsets/third-party-tools/index.md
    scope: ../raw/tools-toolsets/third-party-tools/
    kind: documentation
    revision: sha256:9b153ee34a2681713c938fdd323fd94e21ebe0c2f2535e918bf26639789cc058
    title: "Third-Party Tools"
---

**Reported, Pydantic AI version unspecified:** reusing another library's tools means adapting the foreign object into something the agent can register, and this page names exactly one concrete adapter — LangChain — while the other two routes are pointers rather than instructions: MCP servers arrive as toolsets through the MCP client, and the same third-party tools are said to be available as capabilities, with the Extensibility guide named as the catalog[^pydantic-docs-third-party-tools] The LangChain adapter lives in `pydantic_ai.ext.langchain` and comes in two shapes, a conversion function for a single tool and a toolset class for a list, and neither shape adds behaviour: the call is forwarded to the LangChain tool and the answer returned[^pydantic-docs-third-party-tools] The load-bearing part of the page is therefore not the imports but the check that is deliberately skipped, because it moves a failure the framework normally catches into the foreign library.

## The two LangChain forms

| Form | Called as | Registered through | Fit |
| --- | --- | --- | --- |
| `tool_from_langchain` | a function taking one LangChain tool | `Agent(..., tools=[...])` | A single community-library tool, converted in place |
| `LangChainToolset` | a toolset class taking a list of tools | `Agent(..., toolsets=[...])` | Several tools at once, including a LangChain toolkit's output such as `SlackToolkit().get_tools()` |

Both samples follow the same three steps — build the LangChain object, wrap it, register the result — and they differ only in which agent argument receives it, which is the same split [Pydantic AI toolsets](pydantic-ai-toolsets.md) records for locally defined tools and toolsets[^pydantic-docs-third-party-tools] The single-tool sample wraps `DuckDuckGoSearchRun` and asks a release-date question; the page's stated reason for the tool is freshness, quoting a printed answer for a game released "after the knowledge cutoff for Gemini 2.0 (August 2024)", so the demonstration is that a live third-party tool outruns the model's cutoff rather than that the adapter does anything clever[^pydantic-docs-third-party-tools] One internal inconsistency is worth keeping visible instead of smoothing over: the sample constructs its agent on `google:gemini-3.8-flash` while the surrounding prose justifies the answer against "Gemini 2.0", and the page names no Pydantic AI version anywhere, so neither model identifier can be pinned to a release here.

## What the bridge does not validate

The warning is explicit and it is a design statement, not an install note: Pydantic AI **will not validate the arguments** passed to a LangChain tool — providing arguments that match the schema the LangChain tool declares is the model's job, and raising an error on a bad call is the LangChain tool's[^pydantic-docs-third-party-tools] Read against the rest of the framework this is a handover of two responsibilities that [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md) and [Pydantic AI tool execution, retries and failures](pydantic-ai-tool-execution.md) otherwise own: the definition the model sees is generated from the foreign tool, and an invalid call surfaces as whatever the library raises. What Pydantic AI then does with a library-raised error — consume a retry, report a failed result, or let it escape the run — is **not stated** by this page, and the page's own sample never triggers it, so the recovery path is a limit rather than a claim.

Installation is one line of prose: `langchain-community`, plus any package the individual tool needs — `ddgs` for `DuckDuckGoSearchRun`, with nothing said about pinning, extras or how the LangChain dependency range interacts with a given Pydantic AI release[^pydantic-docs-third-party-tools]

## The other two doors

- **MCP servers** need no adapter at all: the page delegates entirely to the MCP client documentation and describes MCP servers as arriving as toolsets, which is what [Pydantic AI MCP client](pydantic-ai-mcp-client.md) compiles in detail[^pydantic-docs-third-party-tools]
- **Capabilities** are offered as the parallel packaging of the same third-party tools, with `capabilities/third-party/` plus the Extensibility guide as the place to look[^pydantic-docs-third-party-tools] Neither page was followed and no capture of them exists in this wiki, so what a third-party capability contains, which libraries are packaged, and whether it wraps the same `pydantic_ai.ext` adapters or replaces them remain **unknown** here; the vendor's own capability model is recorded separately in [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md).

## Evidence and coverage

The source is a single `index.md` capture of the vendor's Third-Party Tools page — 276 words as declared and 319 by local `wc -w` including frontmatter and markup, 59 lines — inspected as text; `raw/tools-toolsets/third-party-tools/` holds that file alone, with no attachments, includes, downloads, screenshots or supporting assets, and the two samples are embedded code blocks rather than separate files[^pydantic-docs-third-party-tools] It carries `domain: pydantic.dev` and `language: en` and names **no Pydantic AI version, author, publication date or licence**, so every API name and behaviour here is version-unknown, which is why the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set. Every link it offers — `tool_from_langchain` and `LangChainToolset` in the API reference, LangChain's community tool library and toolkit concept pages, the MCP client page and the Extensibility guide — was read as a link, not followed. Nothing was installed, no LangChain tool wrapped, no agent run and no invalid-argument call attempted, so every claim is **Reported** and none **Observed** or **Reproduced**. Limits beyond the validation handover: the page never shows what the generated tool definition looks like, never says whether arguments are passed through as-is or coerced first, and never states whether a wrapped tool keeps LangChain's name and description verbatim.

## Relationships

- **Complements** [Pydantic AI toolsets](pydantic-ai-toolsets.md), which catalogs the third-party toolsets that ship and the four attachment sites; this page owns the single-tool adapter and the no-validation contract that the toolset catalog mentions in passing.
- **Inherits the definition surface of** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md): the schema and description the model is offered are the foreign tool's, not a Pydantic AI-generated one.
- **Moves failure handling into** [Pydantic AI tool execution, retries and failures](pydantic-ai-tool-execution.md) and out of the framework's argument validation, with the resulting retry accounting unstated.
- **Defers the MCP route to** [Pydantic AI MCP client](pydantic-ai-mcp-client.md), where an MCP server is a toolset and the `MCP` capability is the recommended entry point.
- **Parallels** [Pydantic AI native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md): both pages are about admitting a tool whose implementation sits outside the agent's own code, one through an adapter and the other through a provider-or-local switch.

[^pydantic-docs-third-party-tools]: Pydantic Docs, "Third-Party Tools" (<https://pydantic.dev/docs/ai/tools-toolsets/third-party-tools/>, `domain: pydantic.dev`, `language: en`, 276 words as declared and 319 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/third-party-tools/index.md`, 59 lines, content digest sha256:9b153ee3. Intro, raw lines 11–15, for the third-party-integration statement, the capability pointer with the Extensibility guide, and the delegation of MCP servers to the MCP client page as toolsets; §"LangChain Tools" (17–44) for `tool_from_langchain`, the `langchain-community` and `ddgs` install requirements, the no-argument-validation warning, the `DuckDuckGoSearchRun` sample building `Agent('google:gemini-3.8-flash', tools=[search_tool])` and printing a release-date answer, and the "after the knowledge cutoff for Gemini 2.0 (August 2024)" justification; the same section (46–59) for `LangChainToolset` over `SlackToolkit().get_tools()` and its registration through `toolsets=[toolset]`. Both samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date.
