---
type: Concept
title: Anthropic prompt caching in Pydantic AI
description: How Claude caching is placed in Pydantic AI — the unified switch's Anthropic mapping, automatic versus per-block versus explicit breakpoints, smart instruction caching, the four-point budget and its trimming order, cache diagnostics, and the mid-conversation system messages that keep a prefix valid.
tags: [pydantic-ai, anthropic, caching, cost, message-history]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:47:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
---

Claude caches nothing until told where the prefix ends, so on this provider the unified `cache` switch is not a mode toggle but a shorthand for a placement: it puts breakpoints after the tool definitions and after the static instructions and then caches the conversation itself, which is what makes a new conversation read back the prefix it shares with earlier ones.[^pydantic-anthropic-2026] Everything below is the Anthropic side of [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), which owns the framework-wide switch, the provider matrix and the opt-in argument; this page owns the placement rules, the four-point budget, what a miss can be diagnosed as, and the two history mechanisms — mid-conversation and turn-scoped system messages — that exist to keep the prefix valid.

## What the unified switch turns on

On Anthropic, `cache=True` or a retention such as `cache='1h'` places cache breakpoints at the end of the tool definitions and the static instructions — the same two points `anthropic_cache_tool_definitions` and `anthropic_cache_instructions` place — and caches the conversation with Anthropic's automatic caching, the same mechanism as `anthropic_cache`[^pydantic-anthropic-2026] The one exception is the legacy `AsyncAnthropicBedrock` client on models without automatic caching, where the conversation is instead cached with a breakpoint at its end[^pydantic-anthropic-2026] Cache writes cost 1.25× the input price for the 5-minute cache and 2× for the 1-hour cache, reads cost 0.1×, and any provider-specific `anthropic_cache*` setting takes precedence over the unified switch as soon as it is set[^pydantic-anthropic-2026]

## Three ways to place a breakpoint

They are not interchangeable: each exists for a different server capability, and two of them are mutually exclusive.

| Setting | Where the breakpoint goes | Use it when |
| --- | --- | --- |
| `anthropic_cache` | A top-level `cache_control` parameter; the server applies the breakpoint to the last cacheable block of each request | The conversation should cache itself and the breakpoint should move forward as it grows |
| `anthropic_cache_messages` | Per-block `cache_control` on the last content block of the final message | An Anthropic-compatible gateway or proxy takes the message format but not the top-level parameter |
| `CachePoint` marker | Exactly where you put it in a user message; everything before it is cached | The prefix boundary is content you control |

**Automatic caching.** `AnthropicModelSettings(anthropic_cache=True)` sends the top-level `cache_control` parameter, and a custom TTL with `anthropic_cache='1h'`[^pydantic-anthropic-2026] It is the natural fit for multi-turn conversation, and the reported cache counters make it observable: `usage.cache_write_tokens`, `usage.cache_read_tokens` and `usage.cache_hit_ratio`[^pydantic-anthropic-2026]

Whether a model gets automatic caching is read from its profile — `supports_auto_cache` — for both `anthropic_cache` and the unified `cache` setting[^pydantic-anthropic-2026] `AsyncAnthropicBedrockMantle`, `AsyncAnthropicVertex` and `AsyncAnthropicFoundry` support it; the legacy `AsyncAnthropicBedrock` client uses it only on the models Anthropic documents as served from the Messages API infrastructure, and on other models falls back to per-block caching on the last user message, which gives multi-turn conversations the same benefit[^pydantic-anthropic-2026] If Pydantic AI does not yet know that a model or platform supports it, set the flag yourself with `AnthropicModelProfile(supports_auto_cache=True)`; setting it to `False` forces the per-block fallback, which is useful for Anthropic-compatible gateways that reject the top-level parameter[^pydantic-anthropic-2026]

**Per-block message caching.** `anthropic_cache_messages=True` — or `'5m'`/`'1h'` — puts `cache_control` on the last content block of the final message instead, for gateways and proxies such as MiniMax, OpenRouter or LiteLLM that accept Anthropic's message format without top-level automatic caching[^pydantic-anthropic-2026] It **cannot** be combined with `anthropic_cache`[^pydantic-anthropic-2026]

**Explicit breakpoints.** Three settings cover the static parts of a request — `anthropic_cache_instructions` after the system instructions, `anthropic_cache_tool_definitions` after the last tool definition — and a `CachePoint()` marker inside a user message caches everything before that point[^pydantic-anthropic-2026] All three settings take `True` for the 5-minute default or `'5m'`/`'1h'` explicitly[^pydantic-anthropic-2026]

The TTLs interact because Anthropic rejects a request whose one-hour breakpoint comes *after* a five-minute one, processing tools, then system instructions, then messages[^pydantic-anthropic-2026] When a one-hour breakpoint — including the automatic one at the end of the conversation — follows five-minute ones, Pydantic AI raises those earlier breakpoints to one hour[^pydantic-anthropic-2026] A mixed configuration therefore bills more than the TTLs written into the code suggest.

## Smart instruction caching

With `anthropic_cache_instructions`, Pydantic AI places the boundary at the static/dynamic split instead of at a fixed position: static instructions from `Agent(instructions=...)` sort before dynamic ones from `@agent.instructions` functions or toolsets, and the cache point goes after the last static part[^pydantic-anthropic-2026] Instructions with `on_change='append'` sort between the two, because their changes are appended to the history rather than rewriting the prefix, and get a second cache point after them[^pydantic-anthropic-2026]

The two points cover different conversations. The first is what a new conversation reads even when its append-mode instructions differ, which is what makes per-user memory cacheable; the second also covers append-mode instructions that are identical in every conversation, such as catalogs Pydantic AI computes[^pydantic-anthropic-2026] A dynamic instruction that *changes between requests* stays outside the cached prefix, so it does not invalidate the static instructions — but it does invalidate the cached conversation after them, which is the case `on_change='append'` exists for[^pydantic-anthropic-2026] The source's other warning is about content, not cost: keep untrusted text out of instructions[^pydantic-anthropic-2026]

## The four-point budget and its trimming order

Anthropic allows a maximum of **4 cache points per request**, and Pydantic AI manages the limit so a request never fails on it[^pydantic-anthropic-2026] Points come from five sources: automatic caching (1), `anthropic_cache_messages` (1), `anthropic_cache_instructions` (1, or 2 with append-mode instructions), `anthropic_cache_tool_definitions` (1), and `CachePoint` markers in messages (one each)[^pydantic-anthropic-2026]

Combining them is allowed except for the mutually exclusive pair, and over budget the trimming is ordered rather than arbitrary:

1. The cache point after append-mode instructions is dropped first, when another one ends the static instructions or system prompt — within a conversation the message cache points already cover those instructions[^pydantic-anthropic-2026]
2. Then excess `CachePoint` markers are removed from the oldest message content, keeping the most recent[^pydantic-anthropic-2026]
3. Tool cache points and the point after the static instructions are always preserved, so the critical caching survives while message-level caching absorbs the cut[^pydantic-anthropic-2026]

`anthropic_cache` counts as exactly one point, like `anthropic_cache_tool_definitions` and like `anthropic_cache_instructions` without append-mode instructions[^pydantic-anthropic-2026] In the documented example, three settings consume three of four slots and one `CachePoint` still fits[^pydantic-anthropic-2026]

## Reading usage and diagnosing a miss

`cache_write_tokens` counts all writes, and when some used the one-hour TTL — billed higher than the five-minute one — `cache_write_1h_tokens` separates those, which is what lets the reported cost price them at the one-hour rate[^pydantic-anthropic-2026] Anthropic's own counters are also carried in `usage.details` as `'ephemeral_1h_input_tokens'`, and writes made during compaction appear as `'compaction_ephemeral_1h_input_tokens'`[^pydantic-anthropic-2026]

A miss with no explanation is diagnosable. Setting `anthropic_cache_diagnostics=True` makes each request name the most recent Anthropic response in the history as the one to compare against, and when the prefix diverged that response's `provider_details` carries a `'cache_diagnostics'` key with Anthropic's verdict, such as `{'cache_miss_reason': {'type': 'tools_changed', 'cache_missed_input_tokens': 3713}}`[^pydantic-anthropic-2026] The `type` is one of `model_changed`, `system_changed`, `tools_changed`, `messages_changed`, `previous_message_not_found` or `unavailable`[^pydantic-anthropic-2026] Three states have to be told apart: the key is **absent** when Anthropic found no divergence, and holds `{'cache_miss_reason': None}` when the comparison had not finished[^pydantic-anthropic-2026]

Diagnostics are free and do not affect caching, but they are off by default because Anthropic keeps a short-lived fingerprint of each request that asks for them — hashes and token counts, not prompt content — and **rejects them for HIPAA-enabled organizations**[^pydantic-anthropic-2026] They exist only on the Claude API, so the setting is ignored on Bedrock, Vertex AI and Microsoft Foundry[^pydantic-anthropic-2026]

## Two history mechanisms that keep the prefix valid

Rewriting the front of a prompt invalidates every cached prefix behind it, and Anthropic offers two ways to avoid that for an instruction that arrives mid-conversation.

**Mid-conversation system messages.** A `SystemPromptPart` outside the first `ModelRequest` is rendered inside the conversation at the instruction's own position rather than ahead of it, so everything cached up to that point stays cached[^pydantic-anthropic-2026] There is nothing to turn on: any such part counts, whether it came from a stored `message_history` or from `ctx.enqueue(...)` during a run[^pydantic-anthropic-2026] This does not enable caching by itself — that still needs `anthropic_cache`, `anthropic_cache_messages` or a `CachePoint`[^pydantic-anthropic-2026] Placement then matters: a `CachePoint` at the end of an enqueued batch caches everything before it, the instruction included, while one with more content after it caches up to that point and leaves the instruction outside, because the instruction is sent after the content it accompanies[^pydantic-anthropic-2026]

Support varies by model and transport: Microsoft Foundry does not serve the role, some Claude models accept the entry without acting on it, and Pydantic AI falls back to a `<system>`-tagged user message at the same position so the instruction applies where it was put either way[^pydantic-anthropic-2026] The fallback is not equivalent in effect. Given the native entry, Claude will lift a restriction its top-level prompt set; given the identical text in a `<system>` tag, it refuses — which is why an instruction with nothing to distrust, such as a format change, works either way, and an untrusted one does not belong in a mid-conversation system message at all[^pydantic-anthropic-2026]

**Turn-scoped system messages.** A request-scoped `SystemPromptPart` (`scope='request'`) is sent as `{'role': 'system'}` with `clear_at: 'next_user_message'`, which the API stops rendering once a later user turn exists, including one carrying only tool results; Pydantic AI sends every one of them with every request and adds the `mid-conversation-system-clear-at-2026-08-21` beta header[^pydantic-anthropic-2026] This matters most on models with preserved thinking — Claude Opus 5.5, Sonnet 5.5, Fable 5.1 and 5.2 — which tie each thinking block to the exact conversation that produced it: *deleting* an earlier reminder from a later request invalidates every thinking block after it, while a *cleared* one left in place does not[^pydantic-anthropic-2026] A cleared entry costs no input tokens and is never part of a cache key, so `anthropic_cache_messages` and `anthropic_cache` put their breakpoints on the content before it[^pydantic-anthropic-2026]

Support follows mid-conversation system messages on the same transports and models, plus Claude Sonnet 5.5 and Haiku 5.5, whose lasting system messages are sealed `<system>` blocks and whose request-scoped prompt is the same sealed block inside the `clear_at` entry[^pydantic-anthropic-2026] Elsewhere — including on models that do not take the `system` role — a request-scoped prompt is sent as `<system>`-tagged user text with its own request only, and the cache breakpoint goes before it[^pydantic-anthropic-2026] To opt out of the beta on a model that has it, turn the profile flag off with `supports_request_scoped_system_prompts=False`; request-scoped prompts are then sent only while current[^pydantic-anthropic-2026]

## Limits

- The page names **no Pydantic AI version** and no date, so placements, flag names and beta ids here are version-unknown; the page is `draft` under the `pydantic-ai` domain rule[^pydantic-anthropic-2026]
- Evidence class is **Reported** throughout: no account, key or request was used, so no cache was written, read, missed or diagnosed, and the 1.25×/2×/0.1× multipliers are the vendor's numbers[^pydantic-anthropic-2026]
- The model lists for automatic caching and for mid-conversation and turn-scoped system messages are Anthropic's and this page's snapshot; the linked model-capability lists were read as links, not followed[^pydantic-anthropic-2026]
- The four-point trimming rules are stated as behaviour, not observed: which point is dropped in a given over-budget request was not reproduced[^pydantic-anthropic-2026]

## Relationships

- **Anthropic half of** [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), whose unified `cache`/`Caching()` switch this page maps onto Claude's breakpoints, and the counterpart of the OpenAI mechanics in [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md).
- **Requires** the route and transports in [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), since automatic caching is a per-client capability and the profile flag decides the fallback.
- **Keeps counters and diagnostics in** `ModelResponse` usage and `provider_details`, read through [observability](pydantic-ai-observability.md) and diagnosed through [prompt-cache health](pydantic-ai-prompt-cache-health.md), which owns the check order for a low hit rate.
- **Protects the prefix** that [run controls](pydantic-ai-run-controls.md) preserve with `on_change='append'`, and that [Anthropic request constraints](anthropic-request-constraints.md) records as the same instability thinking-block binding turns into a 400.
- **Relies on** [conversation state](pydantic-ai-conversation-state.md) when the history a request replays — and therefore the prefix it can cache — is stored rather than rebuilt.
- **Is the provider half of** [mid-run injection](pydantic-ai-mid-run-injection.md), which owns the framework-level standing-versus-mid-conversation split, `scope='request'` lifetimes and the enqueue drain points, while this page owns how Claude renders those parts and what each rendering costs the prefix.

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Prompt Caching" → "Unified cache setting" (raw lines 227–248) for the `cache=True`/`'1h'` placement at tool definitions and static instructions, the automatic-caching and legacy-Bedrock behaviour, the 1.25×/2×/0.1× prices and provider-field precedence; "Automatic Caching" (249–296) for the top-level `cache_control`, `cache_hit_ratio`, the supported-client list, the legacy-Bedrock fallback to the last user message, `supports_auto_cache` and the profile override both ways; "Per-block Message Caching" (297–329) for `anthropic_cache_messages`, the gateway use case and the incompatibility with `anthropic_cache`; "Explicit Cache Breakpoints" (330–367) for the three settings, `CachePoint`, and the raising of five-minute breakpoints to one hour; "Smart Instruction Caching" (368–400) for the static/append/dynamic ordering, the two cache points and the append-mode rationale; "Accessing Cache Usage Statistics" (422–445) for `cache_write_1h_tokens`, `usage.details['ephemeral_1h_input_tokens']` and `compaction_ephemeral_1h_input_tokens`; "Cache Diagnostics" (446–470) for the setting, the `cache_diagnostics` payload, the six miss types, the absent-versus-`None` states, the fingerprint, the HIPAA exclusion and the Claude-API-only scope; "Cache Point Limits" (471–566) for the four-point ceiling, the five sources and the trimming order. §"Mid-conversation system messages" (583–609) for the position-based rendering, `ctx.enqueue`, the `CachePoint` interaction, the Foundry non-support, the `<system>` fallback and the restriction-lifting difference; "Turn-scoped system messages" (614–633) for `scope='request'`, `clear_at`, the beta header, preserved-thinking models, token and cache-key cost, the sealed-block support and `supports_request_scoped_system_prompts`. Evidence class: **Reported** — vendor documentation; nothing was cached, read, missed or diagnosed.
