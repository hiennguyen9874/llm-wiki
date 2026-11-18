---
type: Concept
title: Anthropic server-side tools in Pydantic AI
description: How Claude's web search, web fetch and code execution tools behave in Pydantic AI — the tool versions chosen, who calls them, the server-side sandbox that filters results and strips citations, the ZDR and citations levers, per-tool provider settings, and the container lifecycle behind code execution.
tags: [pydantic-ai, anthropic, native-tools, web-search, code-execution]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:37:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
---

Anthropic's web search, web fetch and code execution tools are not functions your process calls: on models that support dynamic filtering, the model calls the search and fetch tools *from a server-side code execution sandbox of Anthropic's*, which filters results before they reach the context window — and that sandbox exists whether or not you enabled code execution, has none of your files, credentials or environment, and returns no citations because the pages it read never entered the context.[^pydantic-anthropic-2026] Two levers make the model call the tools itself instead — `anthropic_web_tools_allowed_callers` and the `Citations` capability — each at the cost of dynamic filtering, while the per-tool `provider_settings` choose which tool version is sent and whether a code-execution caller sees full results; code execution has its own version and container lifecycle underneath. The route is [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), the usage these tools inflate is in [Anthropic context management](anthropic-context-management.md), and the native-tool surface itself is introduced in [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md).

## Three versions, two callers

On models that support dynamic filtering, `WebSearchTool` and `WebFetchTool` are sent as Anthropic's `20260209` versions — or `20260318` once [web tool settings](#per-tool-provider-settings) are used[^pydantic-anthropic-2026] By default Anthropic lets the model call them from a server-side code execution sandbox, so an agent that also has its own shell or code tool has two places to run code, and the sandbox has no access to the agent's files, credentials or environment[^pydantic-anthropic-2026]

Two consequences follow from the sandbox. Results the model reads there are not added to its context, so they come back **without citations**[^pydantic-anthropic-2026] And the container is provided even when `CodeExecutionTool` is not enabled, so code execution can be running server-side in an agent that never asked for it[^pydantic-anthropic-2026]

## Citations switch the caller

When you ask for citations — with the `Citations` capability and text output, or with `provider_settings={'anthropic': {'enable_citations': True}}` for web fetch — Pydantic AI sends the cited tools with `allowed_callers=['direct']` on the Anthropic API, so the model calls them itself and their results can be cited[^pydantic-anthropic-2026] That turns off dynamic filtering, so the model reads every result in full[^pydantic-anthropic-2026]

Claude Platform on AWS and Microsoft Foundry keep Anthropic's default, because they have not been verified to accept `allowed_callers` with citations; the profile flag `anthropic_calls_cited_web_tools_directly` routes them there too[^pydantic-anthropic-2026]

A request that already needs code execution keeps the default, and therefore returns uncited results, in two cases: an `anthropic_container` you set yourself — Skills included — and a user turn that has already used code execution, where direct calls would leave the request without it[^pydantic-anthropic-2026] Anthropic rejects that container on a request without code execution, and the turn's code execution calls can still be running[^pydantic-anthropic-2026] Callers are decided for each user turn, so every request in a turn sends the same ones: a conversation whose earlier turns used the sandbox switches to direct calls at its next user prompt, and the sandbox's container and files do not carry over[^pydantic-anthropic-2026]

## The explicit lever: `anthropic_web_tools_allowed_callers`

Setting `anthropic_web_tools_allowed_callers=['direct']` makes the model call both web tools itself with no sandbox, whether or not citations were requested[^pydantic-anthropic-2026] This turns off dynamic filtering and makes the tools eligible for Zero Data Retention[^pydantic-anthropic-2026] A value you set is sent on whichever web tool version the model uses and takes precedence over the citations default[^pydantic-anthropic-2026]

In practice that is three unconnected benefits from one field — citations, ZDR eligibility and no server-side execution — and one cost: the model now reads every page in full, so the context grows with each result[^pydantic-anthropic-2026]

## Per-tool provider settings

Anthropic's newer web tool versions take settings the other providers do not have, passed as typed `provider_settings` on each native tool[^pydantic-anthropic-2026]

| Setting | Effect | Default |
| --- | --- | --- |
| `AnthropicWebFetchToolSettings.use_cache` | Uses Anthropic's cached page rather than fetching fresh; setting it, even to its default, selects `web_fetch_20260318` | `True` |
| `AnthropicWebSearchToolSettings.response_inclusion` / `AnthropicWebFetchToolSettings.response_inclusion` | Whether results consumed by code execution are included in full or excluded; selects the `20260318` versions when code execution may call the tool | `'full'` |

`response_inclusion` only changes the version when code execution may call the tool — on models with dynamic filtering, or when `anthropic_web_tools_allowed_callers` names a code execution caller[^pydantic-anthropic-2026] Otherwise the tool is called directly, where `response_inclusion` has no effect and therefore does not change the version[^pydantic-anthropic-2026] Turning `use_cache` off fetches the page fresh, which adds latency[^pydantic-anthropic-2026]

Two edge rules apply. On a model without dynamic filtering, `web_fetch_20260318` is sent with `allowed_callers=['direct']` so it does not bring code execution with it, and `anthropic_web_tools_allowed_callers` overrides that[^pydantic-anthropic-2026] And `response_inclusion` only affects results consumed by code execution — direct calls, including citation-routed ones, see the full result, and so do results from a code execution call that paused before completing[^pydantic-anthropic-2026]

These versions are sent to every client that offers the web tool and the provider's API decides whether to accept them[^pydantic-anthropic-2026] Vertex AI has no dynamic filtering, so `response_inclusion` on `WebSearchTool` keeps `web_search_20250305` there; the Bedrock clients and web fetch on Vertex raise a `UserError`; and Anthropic documents only the older versions on Microsoft Foundry deployments hosted on Azure, so Foundry may reject these settings[^pydantic-anthropic-2026]

## Code execution: version pinning and containers

Pydantic AI picks a compatible `CodeExecutionTool` version for the selected model, and `anthropic_code_execution_tool_version` overrides it when a specific version is needed[^pydantic-anthropic-2026] Explicitly selecting a version the model does not support raises a `UserError`[^pydantic-anthropic-2026]

Containers are reused from history rather than recreated. When a run continues from message history, Pydantic AI reuses the code execution container recorded there on requests that have code execution: `CodeExecutionTool`, or `WebSearchTool`/`WebFetchTool` where code execution may call them[^pydantic-anthropic-2026] "May call them" means the `20260209` and `20260318` versions by default, unless citations route them to direct calls — which only happens on the Anthropic API — and any version when `anthropic_web_tools_allowed_callers` names a code execution caller[^pydantic-anthropic-2026]

Container reuse is deliberately narrow. The Anthropic API rejects a container on any other request, such as one with no tools, so Pydantic AI does not send it there[^pydantic-anthropic-2026] Tools passed in `extra_body['tools']` are not read, so a request carrying them still sends the container[^pydantic-anthropic-2026]

Containers expire after 30 days, and a request that refers to an expired container returns an error[^pydantic-anthropic-2026] There is one recovery: if a request uploads files through `CodeExecutionTool` and Anthropic answers a history-derived container with an HTTP 404 `not_found_error` saying the container was not found, or with an HTTP 500, Pydantic AI retries once without the rejected container id so Anthropic can create a fresh container and receive the uploads[^pydantic-anthropic-2026] Other errors are raised without that retry, and the fresh container holds none of the expired container's state or files[^pydantic-anthropic-2026] An `anthropic_container` you set explicitly is never replaced automatically; Anthropic's original error is raised instead[^pydantic-anthropic-2026]

## Limits

- The page names **no Pydantic AI version** and no date, so tool versions, settings names and the container rules here are version-unknown; the page is `draft` under the `pydantic-ai` domain rule[^pydantic-anthropic-2026]
- Evidence class is **Reported** throughout: no web tool was called, no page fetched, no code executed, no container created or expired, and no citation produced[^pydantic-anthropic-2026]
- The version→model matrix is not enumerated: which models support dynamic filtering, and which models take which web tool version, are described only as "models that support" it[^pydantic-anthropic-2026]
- What "excluded" does to a result's content, and how a code execution pause is signalled, are named rather than specified[^pydantic-anthropic-2026]
- ZDR eligibility is Anthropic's policy; the page links Anthropic's server-tools docs rather than restating the retention rules[^pydantic-anthropic-2026]

## Relationships

- **Configured through** [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), whose transports decide whether container and file ids travel at all.
- **Substitutes for** the local tool loop in [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md): these tools run on Anthropic's side and reach the context only through their results.
- **Explains the usage inflation** recorded in [Anthropic context management](anthropic-context-management.md): each server-side tool round is a separate model pass, so one response's usage can exceed its context.
- **Interacts with** [Anthropic prompt caching](anthropic-prompt-caching.md), since a tool-array change — filtering the available tools to force one — invalidates the cached prefix.
- **Semantically distinct from** [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md), which puts execution where your files and credentials already are; the Anthropic sandbox deliberately has neither.
- **Turns into a citation surface through** [Pydantic AI citations](pydantic-ai-citations.md): `Citations()`, and `enable_citations` for web fetch, are the two levers that send these tools with `allowed_callers=['direct']`, so the same switch that makes results citable also reads every page in full and gives up dynamic filtering.
- **Complements** [Pydantic AI code mode](pydantic-ai-code-mode.md), the client-side pattern for letting a model write code instead of calling tools one at a time.
- **Is one column of** [native tool configuration](pydantic-ai-native-tool-configuration.md), which records the cross-provider picture this page's Anthropic-only detail sits inside: Claude is the only provider supporting web fetch alongside Google, the only one with `MemoryTool`, and one of two with `AdvisorTool`, while it refuses `description` and `headers` on a native MCP server.

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Web Tool Callers" (raw lines 897–920) for the `20260209`/`20260318` versions, the dynamic-filtering sandbox and its missing files and credentials, the lost citations, the `Citations` capability and `enable_citations` route to `allowed_callers=['direct']`, the AWS/Foundry exception and `anthropic_calls_cited_web_tools_directly`, the two code-execution cases that keep the default, the per-turn caller decision, `anthropic_web_tools_allowed_callers` and its ZDR eligibility; §"Web Tool Settings" (921–968) for `AnthropicWebSearchToolSettings`/`AnthropicWebFetchToolSettings`, `use_cache` and `response_inclusion` with their defaults and version selection, the direct-call no-effect rule, the `web_fetch_20260318` direct default, the code-execution-only scope, the Vertex/Bedrock/Foundry behaviour and the `UserError`s; §"Code Execution Tool Version" (969–988) for the automatic version choice, the `anthropic_code_execution_tool_version` override and the `UserError`; "Code Execution Containers" (989–995) for history-based reuse, the requests it is allowed on, the `extra_body['tools']` blind spot, the 30-day expiry, the single 404/500 retry without the container id, the fresh-container state loss and the explicit `anthropic_container` that is never replaced. Evidence class: **Reported** — vendor documentation; nothing was called, executed or cited.
