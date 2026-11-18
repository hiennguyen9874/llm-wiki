---
type: Concept
title: Pydantic AI tool search
description: How Pydantic AI hides individual tools behind keyword discovery — ToolSearch selectors, its declared tool_search id and defer_loading, native provider search versus the local search_tools fallback and its retry budget, the per-provider cache bill and stored-history portability, and the tools that appear mid-run.
tags: [pydantic-ai, agents, tools, prompt-caching]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:07:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: pydantic-docs-tool-search-capability
    resource: ../raw/capabilities/tool-search/index.md
    scope: ../raw/capabilities/tool-search/
    kind: documentation
    revision: sha256:d7e51e0a242bd9c822cd13fd2f6eb207b5cedc8f5f3ce03e1cab958b55c0fe42
    title: "Tool Search"
---

**Reported, Pydantic AI version unspecified:** tool search is Pydantic AI's answer to a toolset too large to describe up front — definitions cost input tokens before any work happens and selection accuracy "noticeably degrades past ~30–50 available tools", so tools can be marked for deferred loading, kept out of the initial context, and discovered by keyword when the model needs them[^pydantic-docs-tools-advanced] The subtlety that earns this page is that tool search works on **every** model but preserves the prompt cache only where discovery leaves the tool array untouched, so the same feature is free on a native-search model and paid on every other[^pydantic-docs-tools-advanced]

## When to defer

The documented reach-for list[^pydantic-docs-tools-advanced]:

- roughly 10 or more tools, or more than about 10k tokens of definitions;
- tools covering distinct domains — several MCP servers, say — where only a subset matters per request;
- a toolset that is growing and wants headroom.

The skip rule is symmetrical: a small hot toolset where every tool is used most turns only gains a discovery round-trip. The stated rule of thumb is to keep the handful of most-used tools eagerly loaded and defer the long tail[^pydantic-docs-tools-advanced] Workflow *bundles* — instructions, tools, model settings and hooks that travel together — are [on-demand capabilities](pydantic-ai-on-demand-capabilities.md) instead, disclosing at the bundle level on the same machinery[^pydantic-docs-tools-advanced]

## Turning it on

The one place to choose what is searchable is the `ToolSearch` capability, whose `tools` argument takes a selector: the string `'all'`, a list of tool names, a metadata dict, or a callable[^pydantic-docs-tools-advanced] The documented forms are `ToolSearch(tools='all')`, `ToolSearch(tools=['crm_lookup', 'crm_update'])`, and `ToolSearch(tools={'searchable': True})` matching tool metadata[^pydantic-docs-tools-advanced] Two exclusions and one no-op are stated: output tools and the framework's own `search_tools` and `load_capability` tools are never searchable, and a bare `ToolSearch()` defers nothing — it only configures how search runs[^pydantic-docs-tools-advanced]

The same visibility can be declared at the registration instead[^pydantic-docs-tools-advanced]:

- `defer_loading=True` on `Tool`, `@agent.tool` or `@agent.tool_plain`;
- `.defer_loading()` on a whole toolset, including `MCPToolset`, passing a list of names to hide specific ones or `None` to hide all.

These add up: a tool is deferred if any of them selects it[^pydantic-docs-tools-advanced]

The capability's identity is what makes it safe to leave undeclared: it ships a default `id` of `'tool_search'`, so two `ToolSearch` instances merge into one configuration rather than raising a duplicate-id error[^pydantic-docs-tool-search-capability] That puts it in the same fixed-id family as `WebSearch` and `Thinking` described under [custom capabilities](pydantic-ai-custom-capabilities.md), where repeated instances are one configuration stated twice and a field only one of them states survives the merge. The capability is also auto-injected into every agent that has searchable deferred tools[^pydantic-docs-tool-search-capability] **Synthesis:** together, those two statements make the explicit instance in the sample below — and the explicit `tools=` selector above — configuration of a capability that would be attached anyway, not the switch that turns discovery on; what turns it on is having searchable deferred tools at all.

## Who runs the search

Once deferred tools exist, an auto-injected `ToolSearch` capability handles discovery, in one of three modes[^pydantic-docs-tools-advanced]:

| Mode | Where it runs | Availability |
| --- | --- | --- |
| Native provider search | The provider | Anthropic Sonnet 4.5+, Opus 4.5+ and Haiku 4.5+ through BM25 or regex; OpenAI Responses on GPT-5.4+ except GPT-5.4 nano. Deferred tools are sent with `defer_loading` on the wire and the provider manages visibility |
| Custom callable | Your code, routed through the provider's client-executed native surface | `ToolSearch(strategy=…)` with a search function; on Anthropic it becomes `tool_reference` blocks, on OpenAI `execution='client'`, so the model still sees a tool-search call |
| Local fallback | Your side, as an ordinary function tool | A `search_tools` tool that matches keywords against tool names and descriptions |

Native search is preferred where available because the discovery exchange is append-only — a `tool_search_call` plus `tool_search_output` pair — while each tool's authored `defer_loading` value stays stable, which preserves the prompt cache across rounds[^pydantic-docs-tools-advanced] The local fallback instead tracks revealed tools separately from their stable definitions and sends each only once discovered[^pydantic-docs-tools-advanced]

### What the local search tool costs

The local `search_tools` function tool is billed like any other tool on the retry ladder recorded in [tool execution](pydantic-ai-tool-execution.md): `Agent(retries={'tools': N})` gives the model `N` attempts to correct a malformed `queries` argument, and the per-tool, per-toolset and agent-wide precedence is the same one every function tool resolves through[^pydantic-docs-tool-search-capability] The one asymmetry is a negative result: a search that finds no matches is a normal, successful tool call, so it never spends a retry[^pydantic-docs-tool-search-capability] A model that keeps searching for a tool that is not in the corpus therefore burns requests, not retries.

### Corpus and ranking rules

Every searchable deferred tool stays in the corpus for the whole run, including tools the model has already found, so repeating a search is safe and lets it recover a tool after its earlier discovery is no longer visible — after compaction, for instance[^pydantic-docs-tools-advanced] With the default keyword strategy, undiscovered matches always rank ahead of already-available ones, so `max_results` trimming never lets an available tool displace an undiscovered match; it only fills leftover slots[^pydantic-docs-tools-advanced]

Toolsets that aggregate or wrap deferred definitions can ask `ctx.is_tool_available(tool_def)` inside `get_tools` whether a definition is visible — available when it is not deferred or its name has been revealed in history[^pydantic-docs-tools-advanced] Tools gated as a bundle belong to on-demand capabilities and are not part of the searchable corpus[^pydantic-docs-tools-advanced]

Each recorded reveal also surfaces as a `ToolAvailabilityDeltaEvent` in the agent event stream and as the corresponding Vercel AI data chunk or AG-UI activity snapshot[^pydantic-docs-tools-advanced]

## Configuring ToolSearch

| `strategy` | Algorithm | Behaviour |
| --- | --- | --- |
| `None` (default) | Native where available, otherwise local keyword matching | Anthropic BM25 on Sonnet 4.5+/Opus 4.5+/Haiku 4.5+ (native regex on the legacy Bedrock client), OpenAI server-executed `tool_search` on GPT-5.4+ except nano, local keywords elsewhere |
| `'keywords'` | Local keyword overlap | Runs on your side but adapts the wire shape: client-executed native on Anthropic and OpenAI so the cache stays warm, a regular `search_tools` function tool elsewhere |
| `'bm25'` / `'regex'` | Anthropic native | Server-executed; the request **fails** on other providers rather than silently substituting another algorithm |
| Callable `(ctx, queries, tools) -> names` | Your function | Same execution-mode handling as `'keywords'` |

The execution mode itself is auto-derived from the algorithm and the current provider; users do not choose it[^pydantic-docs-tools-advanced] To force the local `keywords` path on a provider that natively supports search, the documented lever is overriding `ModelProfile.supported_native_tools` to exclude `ToolSearchTool`, after which the capability falls through to the local tool[^pydantic-docs-tools-advanced]

## Stored history and portability

Stored history can describe a tool becoming callable in two different ways — a model-driven search, or an application-driven availability change — and Pydantic AI preserves that distinction when the history is replayed on another model[^pydantic-docs-tools-advanced] The page's seven-column matrix covers six stored representations:

| Stored as | Replays as |
| --- | --- |
| A local `search_tools` call and result | Native search on every native-search target; local search plus an `additional_tools` item on first-party OpenAI Responses without native search; plain local search elsewhere |
| An Anthropic or OpenAI native search | Native search on native-search targets, otherwise local search |
| A `ToolAvailabilityDeltaPart` | `tool_addition` on Anthropic with `tool_addition_mode='by_reference'`, `additional_tools` on OpenAI Responses with `'with_definitions'`, an announcement or local search where the mode is `None` |
| A `search_tools` result carrying `metadata['discovered_tools']` | Native search on native-search targets, local search elsewhere |

**Native search** there means a paired provider-native search call and result plus the native search tool, with searchable deferred tools left in the deferred corpus; **local search** means a paired `search_tools` function call and result plus the local tool, with the revealed tool present as an eager function tool[^pydantic-docs-tools-advanced] A capability-only corpus is the degenerate case: a provider-native availability change carries neither a search exchange nor a search tool[^pydantic-docs-tools-advanced]

The rule behind the matrix is about evidence. A genuine search is evidence of what the model did — it chose a query and received matches — so rewriting that exchange as `tool_addition` or `additional_tools` would turn model-driven discovery into application-driven control; provider-native availability changes are therefore used only for a `ToolAvailabilityDeltaPart`[^pydantic-docs-tools-advanced] On targets without that control primitive a mid-conversation system instruction announces `The following tool(s) are now available: {names}` when the schemas are already visible, and a complete local search exchange is synthesized only when its result must reveal a schema that is actually withheld[^pydantic-docs-tools-advanced]

## What it costs the cache

The prefix order is tool definitions → system/instructions → message history, and a change at any layer invalidates that layer and everything after it — which is why changing, adding, removing or reordering a tool definition normally invalidates the cache, since definitions sit at the very front[^pydantic-docs-tools-advanced] A tool that appears mid-run is the exception on OpenAI Responses and Anthropic, which receive it outside `tools[]`[^pydantic-docs-tools-advanced]

Tool search preserves the cache only where discovery leaves the definitions untouched[^pydantic-docs-tools-advanced]:

- **Preserved:** native-search models (Anthropic Sonnet 4.5+/Opus 4.5+/Haiku 4.5+, OpenAI Responses GPT-5.4+ except nano) and first-party OpenAI Responses models without native search, whose local fallback reveals each tool in an `additional_tools` item.
- **Broken:** every other model — Google, older Anthropic models, OpenAI Chat Completions, OpenAI-compatible Responses endpoints — where the local `search_tools` fallback reveals a tool by adding it to the tools array, invalidating the cached prefix from the definitions onward on each discovery turn. On Google a stable `system_instruction` sits ahead of the tool block and can still be reused.

For on-demand capabilities the rule is separate and recorded in [prompt caching](pydantic-ai-prompt-caching.md): a load that reveals no tool definitions preserves the cache on every provider[^pydantic-docs-tools-advanced]

### Tools that appear mid-run

A tool can join a run without being searched for or loaded: added to a `FunctionToolset` from inside another tool, returned by a dynamically built toolset, listed by an MCP server after `notifications/tools/list_changed`, or let through by a `prepare_tools` function[^pydantic-docs-tools-advanced] Pydantic AI compares the immediately available function tools at each step with the ones the run started with and records each new one as a `ToolAvailabilityDeltaPart`; a new tool that carries `defer_loading=True` is not recorded but joins the search corpus[^pydantic-docs-tools-advanced]

| Provider | How the new tool arrives | Cache prefix |
| --- | --- | --- |
| First-party OpenAI Responses | An `additional_tools` input item carrying its definition | **Stable**, except on models before GPT-5.6 for a request whose `tool_choice` names it |
| Anthropic models with tool search | A `defer_loading` declaration plus a `tool_addition` block (or a `tool_reference` result on models without mid-conversation tool changes) | **Stable** once the request already declares a deferred tool; otherwise the first deferred declaration adds a one-time preamble on some models, moving the prefix for that request only |
| Everything else — older Anthropic, OpenAI-compatible Responses endpoints, OpenAI Chat Completions | Added to `tools[]` plus a note in the conversation | **Breaks** from the definitions onward on the request where it appears |

One exception is stated: when nothing the model was already given is left to keep stable — the run started with no plainly visible tools, or every starting tool has since left — the tools present go into `tools[]` directly and nothing is recorded[^pydantic-docs-tools-advanced] That also keeps a request from carrying only deferred tools, which Anthropic rejects[^pydantic-docs-tools-advanced]

Three further rules close the accounting[^pydantic-docs-tools-advanced]:

- The record lives in history, so a retried request or a later run over the same history does not announce the tool again; when compaction summarizes the record away mid-run the tool is announced once more, and a run that starts after the compaction declares it in `tools[]` from its first request.
- Only tools that appear **within a single run** are detected. A tool new to a later run over the same history — one unlocked after a tool approval, say — is sent in `tools[]` from that run's first request, and tools that disappear or whose definition changes under the same name are sent as-is.
- Under durable execution, drive mid-run changes from workflow code — a `prepare_tools` function or a state-reading dynamic toolset. On Temporal, tools run in activities that are not re-executed on replay, so a tool that calls `add_function()` makes a change replay will not reproduce.

For a genuinely open-ended tool universe the page's answer is one stable tool: the harness [Code Mode](pydantic-ai-code-mode.md) capability collapses many tools into a single `run_code` tool whose definition stays byte-stable, surfacing discovered tools as sandbox callables instead of new schemas[^pydantic-docs-tools-advanced]

## Naming and the trace

Discovery quality is partly a naming decision: descriptive names with consistent prefixes (`github_*`, `slack_*`, `mortgage_*`) and the words a user would search for in the tool description, plus an instruction nudge such as "Search by topic when you don't see a tool you need", because a search returns only a handful of matches at a time and the model may iterate search → discover → call → search[^pydantic-docs-tools-advanced]

The page shows the cache consequence in two embedded public Logfire traces: with native search the deferred catalog never enters the cached prefix, so `cache_read_tokens` stays warm while the model discovers tools; editing one tool's description records no cache read at all[^pydantic-docs-tools-advanced] The related controls are recorded rather than restated here — `tool_choice` can also trim the array client-side, `CachePoint` places explicit breakpoints on messages (honored by Anthropic, Bedrock and OpenRouter), and Google's implicit cache keys on a `system_instruction` field ahead of the tool block, while an explicit `CachedContent` fixes the tools as an immutable part of the cache[^pydantic-docs-tools-advanced]

## Evidence and coverage

The package is a single `index.md` capture (11,651 words as declared, 11,888 by local `wc -w`, 1,141 lines), inspected as text; `raw/tools-toolsets/tools-advanced/` holds no attachments, includes, downloads or supporting files. The capture names **no Pydantic AI version, author, publication date or licence**, so every API name, model-version claim and wire detail here is version-unknown, and its samples pin `anthropic:claude-sonnet-5-5`, which no other capture here corroborates. Every external link — the `ToolSearch`, `ToolSearch.tools`, `ToolSelector`, `ToolDefinition.defer_loading`, `AbstractToolset.defer_loading`, `MCPToolset`, `RunContext.is_tool_available`, `ModelProfile.supported_native_tools`, `ToolAvailabilityDeltaPart`/`ToolAvailabilityDeltaEvent`, `CachePoint`, `CachedContent` and `FunctionToolset` API pages, the toolsets, on-demand-capability, compaction, Code Mode, MCP client, Anthropic, OpenAI and Google model pages, and both public Logfire traces — was read as a link, not followed; the two embedded trace iframes were not opened, so the cache-read claim is **Reported** from the surrounding text rather than **Observed** in a span. Nothing was installed, no tool deferred, no search run, no provider cache read, no history replayed and no compaction induced, so every claim is **Reported** and the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set because the native-search model list and the per-provider wire rules move with releases.

A second, much smaller capture — the vendor's own [Tool Search capability page](../raw/capabilities/tool-search/index.md) (213 words as declared, 252 by local `wc -w`, content digest sha256:d7e51e0a, no version or date, three prose paragraphs, one naming sentence and a four-line `ToolSearch(strategy='keywords')` sample) was reconciled against the above and is mostly a restatement: the provider-adaptive native-versus-local split, the auto-injection, the strategy list (`'keywords'`, `'bm25'`, `'regex'`, custom callable), the `'anthropic:claude-sonnet-5-5'` sample model and the bundle-level pointer to on-demand capabilities all duplicate §"Tool Search" here, so they were left as they were rather than restated from the weaker page. Its durable delta is confined to §"What the local search tool costs" and the capability-identity paragraph under §"Turning it on": the declared `id` of `'tool_search'` and the `search_tools` retry and no-match rules, neither of which the tools-advanced capture states. `raw/capabilities/tool-search/` holds that single `index.md` with no attachments, includes or supporting files; its only external link (the `ToolSearch` API reference) and the tools-advanced page it points to for the full strategy table were read as links, not followed, and the sample was not executed. Nothing was constructed, so both additions are **Reported** and none **Observed** or **Reproduced**.

## Relationships

- **Is the individual-tool counterpart of** [Pydantic AI on-demand capabilities](pydantic-ai-on-demand-capabilities.md): that page loads a bundle of instructions, tools, settings and hooks, while this one searches a flat catalog of tools; the vendor's selection rule is shared tools-together versus a long tail.
- **Depends on** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md) for `ToolDefinition.defer_loading` and for `prepare_tools`, which can both add a tool mid-run and hide one per step.
- **Is constrained by** [Pydantic AI tool choice](pydantic-ai-tool-choice.md): a hidden tool is ignored when forcing by name, and the reveal mechanism — `additional_tools`, `tool_addition` or a synthesized exchange — decides whether a forced name is accepted.
- **Costs or preserves** the prefix described in [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), and is the page that records which models get the free version.
- **Uses** [Pydantic AI message history](pydantic-ai-message-history.md) as its state store: a `ToolAvailabilityDeltaPart` beside the `ToolReturnPart` is what keeps a revealed tool revealed.
- **Is explained to the model through** [Pydantic AI mid-run injection and instruction placement](pydantic-ai-mid-run-injection.md): the `The following tool(s) are now available` announcement is a mid-conversation system instruction, and this page records when it is used instead of a synthesized search.
- **Collapses into one stable tool when the universe is open-ended**, per [Pydantic AI code mode](pydantic-ai-code-mode.md), whose `run_code` definition does not move as tools are discovered.
- **Is not the same search as** [Harness smart search](pydantic-ai-harness-smart-search.md): that capability retrieves source *content* by behaviour, while this page's capability selects tool *definitions*.
- **Is classified by** [Pydantic AI tool kinds](pydantic-ai-tool-kinds.md): core's own `'tool-search'` and `'capability-load'` kinds are what let a hook match a search part without matching on its name.
- **Is wrapped by** [Pydantic AI toolset composition](pydantic-ai-toolset-composition.md), which catalogs `DeferredLoadingToolset` and `.defer_loading()` beside the per-tool `defer_loading` flag this page reads.

[^pydantic-docs-tool-search-capability]: Pydantic Docs, "Tool Search" (<https://pydantic.dev/docs/ai/capabilities/tool-search/>, `domain: pydantic.dev`, `language: en`, 213 words as declared and 252 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/capabilities/tool-search/index.md`, content digest sha256:d7e51e0a. Line 11 for the capability's purpose (model-driven discovery of `defer_loading=True` tools so a large toolset costs tokens only for what is used), the provider-adaptive split (native server-executed search on Anthropic and OpenAI Responses, a local `search_tools` function tool elsewhere) and the auto-injection into every agent with searchable deferred tools; line 13 for the default `id` of `'tool_search'` and the merge-instead-of-duplicate-id-error consequence; line 15 and lines 19–24 for the explicit-instance strategy selection and the `ToolSearch(strategy='keywords')` sample; line 26 for the `search_tools` retry budget following the agent's tool budget on the same precedence ladder, the `Agent(retries={'tools': N})` reading of `N` as attempts to correct a malformed `queries` argument, and the no-match search returning normally without spending a retry; line 28 for the pointer to the tools-advanced page for the reach-for rules, strategy table and provider support. Evidence class: **Reported** — vendor documentation naming no version or date; nothing was constructed or executed.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>, `domain: pydantic.dev`, `language: en`, 11,651 words as declared and 11,888 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, 1,141 lines, content digest sha256:8ba11efd. §"Tool Search" (raw lines 836–919) for the token-and-accuracy motivation, the on-demand-capability distinction, the reach-for/skip rules, `ToolSearch(tools=…)`, the never-searchable tools, `defer_loading` on registrations and toolsets, the three execution modes, the append-only native exchange, the corpus and ranking rules, `is_tool_available`, the event surface, the provider projection and the naming guidance; §"Configuring ToolSearch" (920–967) for the strategy table, the auto-derived execution mode and the `supported_native_tools` override; §"Tool-availability history portability" (968–985) for the stored-representation matrix, the native-versus-local definitions and the evidence rationale for not rewriting a real search; §"Tool search and prompt caching" (986–993) for the prefix order, the preserved and broken model sets and the Google `system_instruction` note; §"Tools that appear mid-run" (994–1013) for the four ways a tool joins, the `ToolAvailabilityDeltaPart` record, the per-provider table, the empty-baseline exception, the history and compaction rules, the single-run-only detection and the durable-execution and Code Mode guidance; §"Seeing it in a trace" (1014–1027) for the two traces, the `cache_read_tokens` claim, `tool_choice` as a second cache hazard, `CachePoint` and the Google cache shapes. Excerpted samples were read, not executed; the embedded traces were not opened. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
