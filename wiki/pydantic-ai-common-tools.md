---
type: Concept
title: Pydantic AI common tools
description: The ready-made tools pydantic_ai.common_tools ships — DuckDuckGo search, web fetch and Tavily search — with each factory's install extra, the web-fetch content and download caps, and the Tavily parameters a caller can pin so the model never sees them.
tags: [pydantic-ai, tools, web-search, web-fetch, model-agnostic]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:40:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-common-tools
    resource: ../raw/tools-toolsets/common-tools/index.md
    scope: ../raw/tools-toolsets/common-tools/
    kind: documentation
    revision: sha256:486815f0bf53e56a8207d8ba279e0be48d23940050a72b9fb6a3ec9fc36cf42c
    title: "Common Tools"
---

**Reported, Pydantic AI version unspecified:** `pydantic_ai.common_tools` ships three ready-made tools — DuckDuckGo search, web fetch and Tavily search — implemented in Pydantic AI rather than by the model provider, so they run with any model[^pydantic-docs-common-tools] Each ships behind its own optional install group and is attached as an ordinary `Agent(tools=[…])` entry, so nothing about them depends on the capability layer. **Synthesis:** that second half is the consequence the capture leaves implicit — implemented in Pydantic AI and runnable with any model means the round trip returns to your process and the provider needs no support for the tool, and attaching the tool is the only step. Two operational rules are easy to miss and are why this page earns its own retrieval: the web fetch tool has two independent byte limits plus a conversion ceiling it does not control, and the Tavily factory silently decides which parameters the model is allowed to set[^pydantic-docs-common-tools]

## What ships and how it attaches

| Tool | Factory | Install | Backend | Source |
| --- | --- | --- | --- | --- |
| DuckDuckGo search | `duckduckgo_search_tool()` | `pydantic-ai-slim[duckduckgo]` | the DuckDuckGo API via the `ddgs` library | `pydantic_ai.common_tools.duckduckgo` |
| Web fetch | `web_fetch_tool()` | `pydantic-ai-slim[web-fetch]` | Pydantic AI's own fetcher, with SSRF protection | `pydantic_ai.common_tools.web_fetch` |
| Tavily search | `tavily_search_tool(api_key)` | `pydantic-ai-slim[tavily]` | the Tavily API | `pydantic_ai.common_tools.tavily` |

Installation is against `pydantic-ai-slim` with the matching optional group rather than the full package[^pydantic-docs-common-tools] The samples construct an `Agent('openai:gpt-6.1-sol', tools=[duckduckgo_search_tool()], instructions=…)` and read `result.output`, which is the same registration shape as any other function tool — the factory returns the tool and the agent gathers it into the combined toolset[^pydantic-docs-common-tools] Only Tavily takes a credential, read from `TAVILY_API_KEY` in the sample and asserted non-`None` before the agent is built[^pydantic-docs-common-tools]

## DuckDuckGo search

`duckduckgo_search_tool()` is the argument-lightest of the three: the capture shows it constructed with no arguments at all and handed to `tools=`, with the behaviour steered by the agent's instructions rather than by tool configuration[^pydantic-docs-common-tools] What it returns to the model looks like summarised results, judging by the sample's answer, which reads as prose drawn from several outlets and names publications rather than URLs[^pydantic-docs-common-tools] The page documents no parameters for this tool and no result shape, so how many results come back, whether they carry URLs, and how errors surface are all unstated; the reading above is **Synthesis** from one transcript, not a stated contract.

## Web fetch

`web_fetch_tool()` fetches a page and converts it to markdown, and the source states that it uses SSRF protection to prevent server-side request forgery attacks[^pydantic-docs-common-tools] That is the security-relevant fact on the page: a model-supplied URL reaches your process, and the tool — not the caller — is what refuses internal addresses.

The default limits are worth knowing before raising them[^pydantic-docs-common-tools]:

| Limit | Default | Effect of passing `None` |
| --- | --- | --- |
| `max_content_length` | 50,000 characters of returned text | disable the text cap |
| `max_download_bytes` | 50 MiB of downloaded response body | disable the download cap |

The two limits answer different questions — how much the model is shown versus how much is pulled over the wire — and passing `None` disables only the one you name, so a large response can still be fetched in full and then truncated to the text cap[^pydantic-docs-common-tools] A third ceiling is not a setting at all: unusually complex HTML may exceed the tool's separate conversion limit, and the tool then asks the model to try something else rather than returning partial markdown[^pydantic-docs-common-tools]

The conversion work is scheduled, not per-call unbounded: HTML is converted to markdown in a worker thread, at most four pages at a time per event loop, with further HTML responses waiting for a free slot[^pydantic-docs-common-tools] JSON is indented in a worker thread too, and only as far as the returned text needs — with `max_content_length=None`, a JSON response whose indented form would pass 20 million characters is returned as fetched rather than indented[^pydantic-docs-common-tools] **Synthesis:** those two JSON rules together mean indentation is a presentation step bounded by the output budget, so the worker thread's cost tracks what the model will see except in the one uncapped case where the original bytes are preferred.

## Tavily search and pinned parameters

`tavily_search_tool(api_key)` is where the capture documents a rule that applies to the model-facing schema rather than to search behaviour[^pydantic-docs-common-tools]:

| Parameter state | Where it lives | Model's visibility |
| --- | --- | --- |
| `max_results` | always developer-controlled | never appears in the LLM tool schema |
| provided at construction (e.g. `include_domains=[…]`) | fixed for all searches | hidden from the LLM tool schema |
| left unset | available per call | the model may set it |

The sample locks `max_results=5` and `include_domains=['arxiv.org']` at creation time and leaves `exclude_domains` to the model, which is the intended division: policy in code, tactics left to the prompt[^pydantic-docs-common-tools] **Synthesis:** because the factory removes what you supply, the tool definition the model receives differs between two constructions of the same factory — which matters beyond Tavily, since tool definitions are the first element of the request prefix that prompt caching reuses, so a pinned parameter is also a decision about prefix stability rather than only about capability.

## Limits

- The capture names no Pydantic AI version, no date, no author and no licence, so every factory name, argument and default here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-docs-common-tools]
- Nothing was installed, no extra resolved, no page fetched, no search performed and no agent run, so every claim is **Reported**; none is **Observed** or **Reproduced**.
- The three factories' full signatures are not shown beyond the arguments in the samples; the DuckDuckGo tool's parameters and result shape, the fetch tool's timeout and redirect behaviour, and Tavily's remaining parameter list are unstated.
- The capture does not say whether the opt-in `duckduckgo` and `web-fetch` extras are the same distributions the `WebSearch`/`WebFetch` capabilities' local fallbacks need, only that the group names match those on [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md); whether one implements the other is **Unverified**.
- The sample model alias `openai:gpt-6.1-sol` and both sample outputs are the vendor's own transcripts — the DuckDuckGo answer visibly declines to give a settled top-five list, which illustrates the tool's reach but proves nothing about result quality.

## Relationships

- **Contrasts with** [native tools](pydantic-ai-native-tools.md): these are the "common tools" side of that page's opening distinction — implementations Pydantic AI executes, against provider-executed tools that come back as `NativeToolCallPart`.
- **Provides the local half of** the provider-adaptive story in [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md), whose `WebSearch(local='duckduckgo')` and `WebFetch(local=True)` need the same named extras; that the capability layer reuses these factories is not stated by either capture.
- **Registers through** the `Agent(tools=[…])` route compiled in [Pydantic AI function tools](pydantic-ai-function-tools.md), so — **Synthesis** — the validation, retries and per-tool timeouts described in [tool execution, retries and failures](pydantic-ai-tool-execution.md) apply to them as to any function tool; that the factories return ordinary tools is shown by the samples, not stated as a contract.
- **Sits outside** the [capability catalog](pydantic-ai-capability-catalog.md): none of the three is a capability, so there is no id, no deferral and no `load_capability` step — attaching the tool is the whole switch.
- **Constrained by** [prompt caching](pydantic-ai-prompt-caching.md)'s prefix order: tool definitions lead the request, so the arguments pinned at construction are part of what a cache reuses.
- **Distinct from** the server-side web tools in [Anthropic server-side tools](anthropic-server-side-tools.md) and [citations](pydantic-ai-citations.md): results fetched here are tool results your process produced, not provider results that arrive with citation anchors.

[^pydantic-docs-common-tools]: Pydantic Docs, "Common Tools" (https://pydantic.dev/docs/ai/tools-toolsets/common-tools/; `domain: pydantic.dev`; language `en`; 1,167 words as declared and 1,224 by local `wc -w`; 219 lines; no publication date, author, licence or Pydantic AI version). Sections used: §"DuckDuckGo Search Tool" including its `pip install "pydantic-ai-slim[duckduckgo]"` line, the `ddgs` attribution and the sample agent and transcript; §"Web Fetch Tool" for the SSRF statement, the `pydantic-ai-slim[web-fetch]` install, the `max_content_length` 50,000-character and `max_download_bytes` 50 MiB defaults with `None` to disable, the separate conversion limit that makes the tool ask the model to try something else, the four-pages-per-event-loop worker-thread conversion rule, the JSON indentation rules and the 20-million-character uncapped case; §"Tavily Search Tool" for the `TAVILY_API_KEY` sample, the `max_results`-never-in-schema rule and the provided-versus-unset parameter visibility; and §"Configuring Parameters" for the `max_results=5, include_domains=['arxiv.org']` sample that leaves `exclude_domains` to the model. Local capture: `raw/tools-toolsets/common-tools/index.md`, content digest sha256:486815f0. Evidence class: **Reported** — vendor documentation naming no release version; nothing was installed, fetched or searched.
