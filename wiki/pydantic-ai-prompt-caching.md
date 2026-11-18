---
type: Concept
title: Pydantic AI prompt caching
description: Pydantic AI's unified cache setting and Caching capability — the retention tiers and how they snap, the breakpoints each provider receives, what costs and invalidates a cache, the prefix guarantees the framework makes, and the extension rules that keep a prefix reusable.
tags: [ml, pydantic-ai, agents, cost]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:05:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: pydantic-openai-2026
    resource: ../raw/models/openai/index.md
    scope: ../raw/models/openai/
    kind: documentation
    revision: sha256:843643d2d611697bb1b730046fa5d0721dc79a32f8665c573769afcbbdc15457
    title: "OpenAI"
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
  - id: pydantic-capabilities-caching-2026
    resource: ../raw/capabilities/caching/index.md
    scope: ../raw/capabilities/caching/
    kind: documentation
    revision: sha256:2271a04714729433cd83bd2b3b2736f277df0c334ccee9e91a135d096cc2ce23
    title: "Caching"
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
---

Prompt caching lets a provider reuse the work it did on the *prefix* of a request — the tool definitions, the instructions and the conversation so far — instead of processing it again. Providers read a request in a fixed order, tools, then system prompt, then messages, so appending a new message keeps the prefix usable while changing anything earlier invalidates the cache from that point onward and re-charges everything after it[^pydantic-capabilities-caching-2026] Because an agent run resends the whole conversation at every step, caching is often the difference between paying for the history once and paying for it on every turn[^pydantic-capabilities-caching-2026]

Prompt caching became one switch in v2.55.0: a `cache` model setting and a `Caching` [capability](pydantic-ai-capability-primitive.md) that are equivalent, so `Caching()` and `model_settings={'cache': True}` do the same thing[^dd-v2-tour-2026]

## What the switch does depends on the provider

| Without `Caching()` | Providers | With `Caching()` |
| --- | --- | --- |
| Nothing cached | Anthropic (direct, Bedrock, Vertex AI, Microsoft Foundry, OpenRouter's Anthropic models), Bedrock Claude and Nova | Tool definitions, instructions and the conversation are cached |
| Cached implicitly | OpenAI GPT-5.6 and later, Gemini 2.5 and later on OpenRouter | Explicit breakpoints are added on top, such as one after the instructions |
| Cached implicitly | Older OpenAI models, Gemini, DeepSeek, xAI | No effect |

The first row carries the cost: a Claude agent without the capability pays full input price for its instructions, tools and history on every step of every run, whether it calls Anthropic directly or routes through Bedrock, Vertex AI, Foundry or OpenRouter[^dd-v2-tour-2026] On the implicitly-caching providers the switch cannot turn caching off either: it has no effect, so passing `messages=False` there does not disable their implicit caching[^pydantic-capabilities-caching-2026]

## Retention tiers and how they snap

The setting accepts `True` (the capability's default, meaning the provider's own default retention) and `False` (turn off library-managed caching, for example to override a `cache` value inherited from the model's default settings), plus four durations: `'5m'`, `'30m'`, `'1h'` and `'12h'`[^pydantic-capabilities-caching-2026] A requested duration is snapped to the nearest tier the provider actually offers — **down** where a shorter tier exists, otherwise **up** to the shortest one — so `'30m'` becomes `'5m'` and `'12h'` becomes `'1h'` on Anthropic, whose tiers are five minutes and one hour, while `'5m'` becomes `'30m'` on OpenAI GPT-5.6 and later, whose shortest tier is thirty minutes[^pydantic-capabilities-caching-2026]

That resolution settles the retention question this page previously left open. The v2.55 tour's three-value list and OpenAI's `'30m'`/`'12h'` pair were not rival vocabularies: the setting accepts all four durations and each provider snaps, which is also why the provider chapters document only their own tiers (**Synthesis** across the two captures)[^dd-v2-tour-2026][^pydantic-capabilities-caching-2026]

Retention is how long the provider keeps a cached prefix after its last use, so the default is the starting point. Anthropic's `'1h'` pays off when a conversation commonly continues more than five minutes after its last request; OpenAI's `'12h'` (GPT-5.6 and later, Responses API only) suits instructions or reference material reused across gaps of hours, such as a run that pauses for human approval. Both cost more to write, so each needs at least two reads to beat uncached input[^pydantic-capabilities-caching-2026] The same values are what the underlying `cache` model setting takes, and it is unset by default; a provider-specific cache setting such as `anthropic_cache` or `bedrock_cache_instructions` takes precedence whenever it is set, including to `False`, and the unified setting is then ignored for that request[^pydantic-capabilities-caching-2026] `cache=False` only disables caching Pydantic AI manages: `CachePoint` markers in the history and provider-specific settings still apply, and implicitly-caching providers still cache[^pydantic-capabilities-caching-2026]

## What the capability places on each provider

By default `Caching()` caches the tool definitions, the static instructions, the `on_change='append'` instructions after them (except on OpenAI), and the conversation, and it places a breakpoint — a marker ending the content eligible for caching — at the end of each of those blocks[^pydantic-capabilities-caching-2026] The order matters: the breakpoint at the end of the static instructions is what lets separate conversations share a long prefix, while append-mode instructions join the shared prefix only when their first value is identical in every conversation — as with a catalog Pydantic AI computes, not with per-user state such as memory[^pydantic-capabilities-caching-2026] Where the provider has an automatic caching mode the conversation is cached with it instead of an explicit breakpoint, and where explicit `CachePoint`s would exceed the provider's breakpoint limit the breakpoint after the append-mode instructions is dropped first (unless there are no static instructions or system prompt before them, making it the only instruction breakpoint), then the oldest message breakpoints; OpenAI, which does not trim requests client-side, has the server drop the earliest breakpoints first, starting with the instruction breakpoint[^pydantic-capabilities-caching-2026]

| Provider | `Caching()` | `Caching('1h')` | `Caching(messages=False)` | Notes |
| --- | --- | --- | --- | --- |
| Anthropic API, Vertex AI, Microsoft Foundry, the Bedrock Messages API, and the legacy `AsyncAnthropicBedrock` client on Anthropic's documented models | `anthropic_cache`, `anthropic_cache_instructions` and `anthropic_cache_tool_definitions` set to `'5m'` | The same, set to `'1h'` | Without `anthropic_cache` | Automatic caching places the conversation breakpoint on the last cacheable block and moves it forward |
| Anthropic on the legacy `AsyncAnthropicBedrock` client on other models | `anthropic_cache_instructions`, `anthropic_cache_tool_definitions` and `anthropic_cache_messages` set to `'5m'` | The same, set to `'1h'` | Without `anthropic_cache_messages` | `'1h'` snaps to `'5m'` on models AWS does not grant the one-hour TTL |
| Bedrock (Claude and Nova) | `bedrock_cache_instructions`, `bedrock_cache_tool_definitions` and `bedrock_cache_messages` set to `True` | The same, set to `'1h'` | Without `bedrock_cache_messages` | `'1h'` snaps to `'5m'` on models AWS does not grant the one-hour TTL |
| OpenRouter (Anthropic and Gemini) | `openrouter_cache_instructions`, `openrouter_cache_tool_definitions` and `openrouter_cache_messages` set to `'5m'` | The same, set to `'1h'` | Without `openrouter_cache_messages` | Gemini routes take no tool-definition breakpoint and no TTL, and the message breakpoint goes on the message before the final one |
| OpenAI (GPT-5.6 and later, on the OpenAI API and the Azure OpenAI v1 API) | `openai_prompt_cache_options={'mode': 'implicit', 'ttl': '30m'}` and `openai_cache_instructions=True` | The same | `mode='explicit'`, so only the instructions are written | `Caching('12h')` sends `'ttl': '12h'` on the Responses API; Chat Completions rejects it, and `AzureProvider` follows Microsoft's documentation listing only `'30m'`, so both snap every value to `'30m'`. Requests that continue server-side state (`openai_previous_response_id` or `openai_conversation_id`) cannot carry an instruction breakpoint and keep the implicit one, so they cache like `Caching()` |
| Providers that only cache implicitly | No effect | No effect | No effect | Google, and OpenAI models before GPT-5.6 |

_Table: how `Caching()` translates per provider._[^pydantic-capabilities-caching-2026]

The same switch can also be spelled as a `cache` model setting, which takes a `CacheConfig` with an optional retention and the same `messages` flag[^pydantic-capabilities-caching-2026]:

```python
agent = Agent(
    'anthropic:claude-opus-5-5',
    model_settings={'cache': {'retention': '1h', 'messages': False}},
)
```

## Why it stays opt-in

Caching is off by default because a cache write costs more than uncached input — the source cites 1.25x for Anthropic's 5-minute cache, 2x for the 1-hour cache, and 0.1x for reads — so a prefix that is never read back costs more with caching than without[^dd-v2-tour-2026] For agents that mostly make one-off requests with long shared instructions, `Caching(messages=False)` caches only the stable prefix[^dd-v2-tour-2026]

That narrow mode is for the case where many short, unrelated conversations share long instructions or tools: writing each conversation to the cache would never be read back, so pass `messages=False` and only the tools and instructions are cached. On providers where `Caching()` has no effect, `messages=False` has none either[^pydantic-capabilities-caching-2026] The source's worked example runs two unrelated questions against one long handbook instruction and the second reads the handbook from the cache[^pydantic-capabilities-caching-2026]

v2.55.0 also turned prompt caching on by default in the Harness `Coder` capability and halved `import pydantic_ai` time by lazy-loading `pydantic_ai.mcp`[^dd-v2-tour-2026]

## OpenAI specifics

OpenAI's own setup page fills in what the unified switch does on that provider: `cache=True` sends `openai_prompt_cache_options={'mode': 'implicit', 'ttl': '30m'}` and turns on `openai_cache_instructions`, `cache='12h'` is accepted only on the Responses API and snaps to `'30m'` on Chat Completions as does every other retention, and setting either provider field directly takes precedence[^pydantic-openai-2026] The same page documents the parts the article leaves out — `CachePoint` placement rules, the one-implicit-plus-three-explicit and four-explicit breakpoint budgets, the 1,024-token floor, cache diagnostics in `provider_details`, and the 1.25×/2.5× write multipliers whose two TTLs `cache_write_tokens` cannot distinguish[^pydantic-openai-2026] Those mechanics are compiled in [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md). The retention vocabulary is no longer in tension: OpenAI's `'30m'`/`'12h'` and the tour's three-value list are the same four-value setting, snapped per provider as the section above records[^pydantic-capabilities-caching-2026]

## Anthropic specifics

Anthropic's setup page supplies this page's provider row from the other side. On Claude, `cache=True` or `cache='1h'` is a *placement* shorthand: it puts breakpoints at the end of the tool definitions and the static instructions and caches the conversation with Anthropic's automatic caching, and the provider-specific `anthropic_cache*` settings take precedence as soon as one is set[^pydantic-anthropic-2026] The write prices agree with this page's figures — 1.25× for the 5-minute cache and 2× for the one-hour, 0.1× for reads — so the review cost is corroborated by the second capture rather than resting on one summary[^pydantic-anthropic-2026]

The detail this page leaves out is the supply side: automatic caching is a per-client capability read from `supports_auto_cache`, per-block `anthropic_cache_messages` exists for Anthropic-compatible gateways, instruction caching places its boundary at the static/dynamic split, and a request has only four cache points to spend across five sources[^pydantic-anthropic-2026] Those rules, the cache diagnostics that name a miss reason, and the mid-conversation and turn-scoped system messages that keep a prefix valid are compiled in [Anthropic prompt caching](anthropic-prompt-caching.md). The retention question is now answered rather than open: the unified setting's `'30m'` and `'12h'` are accepted and snapped down to Claude's `'5m'` and `'1h'`, which is why the Anthropic chapter documents only `True` and `'1h'`[^pydantic-capabilities-caching-2026]

## Google specifics

Google is the provider where the unified switch has least to configure: Gemini already caches prompts implicitly, so the unified `ModelSettings.cache` "adds nothing to a Google request"[^pydantic-google-2026] What Google offers instead is a **named resource**. Create a cached content resource with the underlying `google-genai` SDK — the source's example is `provider.client.caches.create(model=…, config=CreateCachedContentConfig(system_instruction=…, contents=[…], ttl='3600s'))` — and pass its name through `google_cached_content` to reuse it across requests[^pydantic-google-2026] Pydantic AI deliberately does not wrap the cache-management API, so `list`, `update` and `delete` stay with the SDK[^pydantic-google-2026]

Two numbers bound the resource: a minimum size of roughly **2,048 tokens** on Gemini 2.5 series models and roughly **4,096** on Gemini 3 series models, and a TTL[^pydantic-google-2026] The source defers current thresholds, pricing and the management operations to the Gemini caching docs, which were read as a link and not followed — so the thresholds here are the vendor's approximations, not a measured floor. This is also the reading of the matrix's Google row above: "no effect" is correct for the unified switch, and an explicit resource is the mechanism that does something.

Google is also where the capability's translation stops: `CachePoint` markers are ignored, and a resource created this way owns the system instructions and the tools, so the agent's own instructions and tools are left out of the requests that reference it[^pydantic-capabilities-caching-2026]

## Provider behaviour the unified setting cannot express

A few provider behaviours are documented only per provider, and the unified setting neither exposes nor fixes them:

- **Bedrock** caches explicitly on Claude and Nova at a five-minute default with a one-hour TTL on the Claude models AWS grants it to. Nova does not cache tool definitions, content below the model's minimum token threshold is not cached, a request carries at most four cache points, and a cache point only finds the previous request's entry within roughly 20 content blocks — so after a turn that adds more than that, `bedrock_cache_messages` also marks the end of the previous request[^pydantic-capabilities-caching-2026]
- **OpenRouter** passes breakpoints through to Anthropic and Gemini. Anthropic routes honour the requested TTL; Gemini routes ignore it, use only the last breakpoint, take no tool-definition breakpoint, and that breakpoint goes on the closest user or assistant message *before* the final one, because a breakpoint at the very end makes OpenRouter's Google Vertex endpoint bill the prompt twice. Gemini's cached system instructions cannot change, so dynamic content belongs in a later user message[^pydantic-capabilities-caching-2026]
- **Implicit-only providers** need no breakpoint but some take a hint that keeps related requests on the same cache: xAI's cache sticky routing metadata, `mistral_prompt_cache_key`, and the prompt-cache identity the OpenAI Codex model derives from the conversation[^pydantic-capabilities-caching-2026]

## What a cache costs

On Anthropic and on OpenAI GPT-5.6 and later, writing a prefix costs more than sending it uncached and reading it back costs much less:

| Provider | Cache write | Cache read |
| --- | --- | --- |
| Anthropic, including Bedrock, Vertex AI and Foundry | 1.25× input for the 5-minute cache, 2× for the 1-hour cache | 0.1× |
| OpenAI GPT-5.6 and later | 1.25× for the 30-minute cache, 2.5× for the 12-hour cache | 0.1× |

_Table: write and read multipliers._[^pydantic-capabilities-caching-2026]

So the 1.25× tiers break even after one read and the 2× and 2.5× tiers after two. Within an agent run with tool calls every request after the first reads the prefix, and in a conversation continued through [`message_history`](pydantic-ai-message-history.md) every turn that arrives before the retention expires does; a request that is never repeated pays the write premium alone[^pydantic-capabilities-caching-2026]

## What invalidates a cache

Two classes of cause are worth separating, because only one of them is under your control.

**Changes under your control** — each moves the prefix and re-charges everything after it[^pydantic-capabilities-caching-2026]:

- Minute-precision timestamps or other per-request values in instructions or system prompts; prefer date-only granularity where the exact time is not needed.
- Instructions whose text changes mid-conversation, such as a todo list or memory. Opt them into `on_change='append'` so changes are appended to the history instead of rewriting the prefix, and keep untrusted text out of instructions.
- Reordering or changing tool definitions between steps. A tool that appears mid-run is recorded in the message history instead, which keeps the prefix on OpenAI Responses and Anthropic.
- History processors that rewrite already-sent messages on every request.
- Switching models or providers during a conversation; each provider keeps a separate cache.
- On Anthropic models that bind thinking blocks to the prefix that produced them (Claude Fable 5.1 and 5.2, Claude Mythos 5.2, Claude Opus 5.5, Claude Sonnet 5.5 and Claude Haiku 5.5), the same mid-conversation change is a 400 error rather than only a miss[^pydantic-capabilities-caching-2026]

**Provider retention** — caches expire after idle gaps, which is unavoidable but useful: schedule history-mutating maintenance for cache-cold windows, when the next request would pay the full input price anyway[^pydantic-capabilities-caching-2026] The documented default is carried as `ModelProfile.default_cache_retention`, a longer requested retention is resolved by `Model.resolve_cache_retention()`, and `prompt_cache_outlook()` takes either to predict whether the next request will find a cold cache — the mechanism [history processors](pydantic-ai-history-processors.md) uses.

## Observing cache health

Model-request spans carry `pydantic_ai.cache.*` attributes from v2.55: a per-request hit ratio, the size of the established cached prefix, a `pydantic_ai.cache.collapse` event when a prefix is lost unexpectedly, and a `pydantic_ai.cache.not_enabled` flag when a request long enough to cache goes to a model that needs caching configured[^dd-v2-tour-2026] On Anthropic, requested and applied breakpoints are reported so a breakpoint dropped to fit the limit is visible[^pydantic-capabilities-caching-2026] The counters, the collapse classification and the diagnostic order that turns a low hit rate into a cause are compiled in [Pydantic AI prompt-cache health](pydantic-ai-prompt-cache-health.md); the span format itself belongs to [Pydantic AI observability](pydantic-ai-observability.md).

## Keeping the prefix stable

Cache hits depend on the prefix staying byte-stable, and the source states that as guarantees rather than intentions[^pydantic-capabilities-caching-2026]:

- Instructions are assembled deterministically for each request — static `Agent(instructions=...)` first, then `on_change='append'` ones, then the dynamic ones that rewrite the prefix — so the stable prefix survives when the rewriting content changes.
- Append-mode instructions keep the prefix the conversation started with: a change is appended to the history, and the prefix only moves when a new baseline starts, such as a rewriting block changing or the history being compacted.
- Message history is append-only within a run; Pydantic AI does not rewrite or reorder settled messages. History processors you add, and capabilities that rewrite history such as compaction, are the deliberate exceptions.
- For a structured `output_type` that does not pick an output mode, the mode is chosen on the run's first request to each model and kept for the rest of the run — but chosen again per request behind a [`FallbackModel`](pydantic-ai-model-fallback.md) — so a [thinking](pydantic-ai-thinking.md) setting that changes between steps does not add or remove the output tool. A new run, including one continuing the same conversation, chooses again.
- Internal bookkeeping such as run IDs, message timestamps and deferred-tool flags never reaches the provider wire and so cannot move the prefix.
- The Vercel AI and AG-UI adapter round-trips are tested to reconstruct histories that serialize back to the same provider request for the wire-relevant fields; older UI protocol versions can be lossy, and AG-UI clients can omit the activity messages that carry compaction items and tool-availability changes.
- Every recorded provider conversation in Pydantic AI's test suite is checked for wire-level prefix stability, so a framework change that starts moving prefixes fails CI in the pull request that introduces it.

v2.59.0's `on_change='append'` instruction mode is the same rule from the authoring side: it adds changes to the end of the prompt instead of rewriting the prefix, so a value that changes between turns stops breaking the cache[^dd-v2-tour-2026] See [Pydantic AI run controls](pydantic-ai-run-controls.md).

## Rules for extension authors

Tool, toolset and capability authors are asked to preserve the same contract[^pydantic-capabilities-caching-2026]:

- Never mutate the cached prefix during a run.
- Put per-turn dynamic content in the user message, in tool results, or after the last `CachePoint`.
- Keep tool definitions and their ordering stable across steps.
- Use date-only timestamps in instructions.
- Give instructions that change mid-conversation `on_change='append'`, which needs an `id` on the capability or toolset, and keep untrusted text out of instructions.
- Register framing tags at import time, not partway through a conversation.

## Limits

- The provider matrix and the price multipliers are the article's summary of the caching docs; no provider account, invoice, or cache-hit measurement was reproduced here[^dd-v2-tour-2026]
- The caching reference page behind the translation table, the retention snapping, the guarantees and the extension rules names **no Pydantic AI version and no date**, so which release ships the four-value retention list, the `CacheConfig` shape or `resolve_cache_retention()` is unstated[^pydantic-capabilities-caching-2026]
- Provider support moves quickly, and the matrix is tied to v2.59-era provider behaviour, hence the short `stale_after`.
- The `Caching()` example in the article is attached to an agent that was run against `TestModel`, where no real cache exists, so the caching path itself is **Reported**, not reproduced.
- The reference page's links — the `Caching` API page, the provider chapters, `CachePoint`, the promise and Logfire pages, and the Harness Warn On Cache Busts capability — were read as links, not followed; the provider chapters already compiled here supply the detail this page does not restate, and the two agree on the Anthropic multipliers, the `'12h'` Responses-only rule and the Azure `'30m'` snap.
- The breakpoint budget, the per-model minimum cacheable length and the trimming order are the vendor's statements; none was triggered against a live provider, so the drop order in particular is **Reported**, not **Observed**.

## Relationships

- **Is a** [capability](pydantic-ai-capability-primitive.md) in core `pydantic-ai`, alongside `Hooks`, `MCP`, `LocalWorkspace`, `Thinking` and `ToolSearch`.
- **Detailed for OpenAI** by [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md), which records the breakpoint budgets, `CachePoint` placement, TTL semantics and write multipliers on that provider.
- **Detailed for Anthropic** by [Anthropic prompt caching](anthropic-prompt-caching.md), which records what the unified switch places on Claude, the four-point budget and its trimming order, cache diagnostics, and the two mid-conversation system-message mechanisms that keep a cached prefix valid.
- **Detailed for Google** by [Google models in Pydantic AI](google-models-in-pydantic-ai.md) for the provider and settings half of `google_cached_content`, and by this page's Google section for the resource itself[^pydantic-google-2026]
- **Exposes** its health through [observability](pydantic-ai-observability.md) span attributes, and **is diagnosed through** [Pydantic AI prompt-cache health](pydantic-ai-prompt-cache-health.md), which owns the usage counters, the collapse signals and the order in which to check a low hit rate.
- **Depends on** stable prompt prefixes, which [run controls](pydantic-ai-run-controls.md) preserve with append-only instructions.
- **Protected by** [file understanding](pydantic-ai-file-understanding.md), which records a file's description once in message metadata so later requests keep the same content — a protection lost when history is rebuilt from a client.
- **Invalidated by** a changed request-level reasoning effort, as [reasoning effort changes](pydantic-ai-reasoning-effort-changes.md) records: that effort is part of the provider's cache key, so the conversation is processed again unless the API takes the change mid-conversation.
- **Built on by** [Pydantic AI Harness planning](pydantic-ai-harness-planning.md), a Harness capability whose whole design is this page's prefix rule — the model's task list travels in tool results and recorded parts rather than the system prompt, and the capability places no breakpoint of its own.
- **Is spent by** [Pydantic AI tool choice](pydantic-ai-tool-choice.md): most providers cache on the whole tools array, so a restrictive `tool_choice` preserves the cache only where the provider has a native filter (`allowed_tools`, `allowed_function_names`) rather than a client-side trim[^pydantic-docs-tools-advanced].
- **Is preserved or broken by** [Pydantic AI tool search](pydantic-ai-tool-search.md), which records the one tool-level mechanism that adds tools without moving the prefix — native search, or first-party OpenAI Responses `additional_tools` — against the local `search_tools` fallback that invalidates it on every discovery turn[^pydantic-docs-tools-advanced].
- **Is qualified by** [on-demand capabilities](pydantic-ai-on-demand-capabilities.md): a capability load costs the prefix only when its reveal mode changes `tools[]` — instruction-only loads stay stable, native tools always move the prefix, and function tools depend on the provider's native reveal item.
- **Scheduled by** [history processors](pydantic-ai-history-processors.md), which use `prompt_cache_outlook` and `ModelProfile.default_cache_retention` to spend a history mutation when the cache is already cold, and **assumed by** [prompt framing](pydantic-ai-prompt-framing.md), whose announcement changes the cached prefix once per conversation under `'when_needed'` and every turn in an AG-UI or Vercel AI app that does not send it back.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Caching is now one switch (v2.55)" (raw lines 249–264) for the setting equivalence, retention tiers, the provider matrix, write-versus-read pricing, `Caching(messages=False)`, the Coder default, and the lazy `pydantic_ai.mcp` import; §"Observability: Logfire or any OpenTelemetry backend" for the `pydantic_ai.cache.*` attributes; §"What changed in v2.58 and v2.59" for `on_change='append'`. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — a docs-derived summary by a third party; nothing was executed or measured.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, 7,634 words as declared and 7,648 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Prompt caching" (raw lines 191–265) for the unified-setting mapping (`cache=True` → `{'mode': 'implicit', 'ttl': '30m'}` plus `openai_cache_instructions`), `cache='12h'` being Responses-only and snapping to `'30m'` on Chat Completions, the provider-field precedence, the 1,024-token floor, the breakpoint budgets, `provider_details['prompt_cache_diagnostics']`, and the 1.25×/2.5× write multipliers with the `cache_write_tokens` ambiguity. Evidence class: **Reported** — vendor documentation; nothing was cached, written or billed.

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Unified cache setting" (raw lines 231–248) for the `cache=True`/`'1h'` placement at tool definitions and static instructions, the automatic-caching conversation, the legacy-Bedrock exception, the 1.25×/2×/0.1× prices and provider-field precedence; §"Automatic Caching" (249–296) for `supports_auto_cache`, the per-client support and the per-block fallback; §"Per-block Message Caching" (297–329) for `anthropic_cache_messages` and its gateway use case; §"Smart Instruction Caching" (368–400) for the static/dynamic boundary; §"Cache Point Limits" (471–566) for the four-point ceiling and the five sources. Retention is reconciled in this page's §"Retention tiers and how they snap": the unified setting accepts `'5m'`/`'30m'`/`'1h'`/`'12h'` and snaps them to Claude's two tiers, which is why this chapter documents only `True` and `'1h'`[^pydantic-capabilities-caching-2026] Evidence class: **Reported** — vendor documentation; nothing was cached, written, read or billed.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Context caching (google_cached_content)" (raw lines 453–491) for the statement that the unified `ModelSettings.cache` adds nothing to a Google request, `google_cached_content` taking a cached content resource name, the `provider.client.caches.create(model=…, config=CreateCachedContentConfig(system_instruction=…, contents=[…], ttl='3600s'))` example and its printed `cachedContents/abc123…`, the statement that Pydantic AI does not wrap the cache-management API, and the ≈2,048/≈4,096-token minimums with the pointer to the Gemini caching docs for thresholds, pricing and `list`/`update`/`delete`. Evidence class: **Reported** — vendor documentation; nothing was cached, created or billed.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Prompt caching implications" inside Tool Choice (raw lines 533–555) for the full-tools-array caching assumption, the API-level `allowed_tools`/`allowed_function_names` filtering that preserves it and the per-provider client-side trim table; §"Tool search and prompt caching" (986–993) for the prefix order, the native-search and `additional_tools` cases that add tools without moving it, and the local `search_tools` fallback that invalidates from the definitions onward. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.

[^pydantic-capabilities-caching-2026]: Pydantic Docs, "Caching", <https://pydantic.dev/docs/ai/capabilities/caching/>, 3,412 words as declared and 3,560 by local `wc -w`, 252 lines, `domain: pydantic.dev`, `language: en`, no publication date and no Pydantic AI version named; local capture `raw/capabilities/caching/index.md`, content digest sha256:2271a047. §intro and "Unified caching settings" (raw lines 10–31) for the prefix definition, the fixed request order, the append-versus-change rule, the three-row matrix and the opt-in argument; §"Configuring caching" (32–50) for the `True`/`False`/four-duration set, the snap-down-then-up rule with the Anthropic and OpenAI examples, and the precedence of provider-specific settings including `False`; §"Caching only the stable prefix" (51–75) for `messages=False`, the one-off-conversation case, the no-effect-on-implicit-providers rule and the `CacheConfig` model-setting form; §"Provider translation" (76–93) for the breakpoint placement at tools, static instructions, append-mode instructions and conversation, the shared-prefix condition for append values, the trimming order and OpenAI's server-side earliest-first drop, and the per-provider translation table; §"Anthropic" and "Bedrock" (95–108) for automatic caching on the last cacheable block, the four-breakpoint ceiling, the five-minute default, Nova's missing tool-definition cache, the minimum token threshold and the ~20-content-block lookback; §"OpenAI" (110–119) for implicit caching, the 1,024-token minimum on GPT-5.6 and later, `openai_prompt_cache_options`, the four-breakpoint write limit and `openai_prompt_cache_key`; §"OpenRouter" (121–129) for TTL pass-through, Gemini's ignored TTL and last-breakpoint rule, the before-final-message placement and the double-billing reason; §"Google" (131–137) for ignored `CachePoint`s and the resource owning instructions and tools; §"Other providers" (139–142) for implicit caching and the sticky-routing hints; §"Cost" (144–154) for the write/read table and the break-even arithmetic; §"What invalidates a cache" (156–171) for the controllable causes, the thinking-block 400, retention expiry and the `default_cache_retention`/`resolve_cache_retention()`/`prompt_cache_outlook()` triple; §"Prefix-stability guarantees" (173–185) for the seven guarantees including the output-mode choice, the off-wire bookkeeping, the adapter round-trip tests and the CI wire-prefix check; §"Monitoring cache efficiency" (187–216) for the usage counters and diagnostic order compiled in [prompt-cache health](pydantic-ai-prompt-cache-health.md); §"Rules for extension authors" (218–228) for the six author rules. Evidence class: **Reported** — vendor documentation naming no version or date; nothing was cached, written, read, measured or diagnosed.
