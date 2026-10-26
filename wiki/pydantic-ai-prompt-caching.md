---
type: Concept
title: Pydantic AI prompt caching
description: Pydantic AI v2.55's unified cache setting and Caching capability, the provider-by-provider effect, and the cache-write cost that keeps caching opt-in.
tags: [ml, pydantic-ai, agents, cost]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T03:59:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

Prompt caching became one switch in v2.55.0: a `cache` model setting and a `Caching` [capability](pydantic-ai-capability-primitive.md) that are equivalent, so `Caching()` and `model_settings={'cache': True}` do the same thing. Retention accepts `True`, `False`, `'5m'`, `'30m'` or `'1h'`, snapped to the tiers each provider supports[^dd-v2-tour-2026]

## What the switch does depends on the provider

| Without `Caching()` | Providers | With `Caching()` |
| --- | --- | --- |
| Nothing cached | Anthropic (direct, Bedrock, Vertex AI, Microsoft Foundry, OpenRouter's Anthropic models), Bedrock Claude and Nova | Tool definitions, instructions and the conversation are cached |
| Cached implicitly | OpenAI GPT-5.6 and later, Gemini 2.5 and later on OpenRouter | Explicit breakpoints are added on top, such as one after the instructions |
| Cached implicitly | Older OpenAI models, Gemini, DeepSeek, xAI | No effect |

The first row carries the cost: a Claude agent without the capability pays full input price for its instructions, tools and history on every step of every run, whether it calls Anthropic directly or routes through Bedrock, Vertex AI, Foundry or OpenRouter[^dd-v2-tour-2026]

## Why it stays opt-in

Caching is off by default because a cache write costs more than uncached input — the source cites 1.25x for Anthropic's 5-minute cache, 2x for the 1-hour cache, and 0.1x for reads — so a prefix that is never read back costs more with caching than without. For agents that mostly make one-off requests with long shared instructions, `Caching(messages=False)` caches only the stable prefix[^dd-v2-tour-2026]

v2.55.0 also turned prompt caching on by default in the Harness `Coder` capability and halved `import pydantic_ai` time by lazy-loading `pydantic_ai.mcp`[^dd-v2-tour-2026]

## Observing cache health

Model-request spans carry `pydantic_ai.cache.*` attributes from v2.55: a per-request hit ratio, the size of the established cached prefix, a `pydantic_ai.cache.collapse` event when a prefix is lost unexpectedly, and a `pydantic_ai.cache.not_enabled` flag when a request long enough to cache goes to a model that needs caching configured[^dd-v2-tour-2026] See [Pydantic AI observability](pydantic-ai-observability.md).

## Keeping the prefix stable

Cache hits depend on the prompt prefix staying byte-stable. v2.59.0's `on_change='append'` instruction mode exists for that reason: it adds changes to the end of the prompt instead of rewriting the prefix, so a value that changes between turns stops breaking the cache[^dd-v2-tour-2026] See [Pydantic AI run controls](pydantic-ai-run-controls.md).

## Limits

- The provider matrix and the price multipliers are the article's summary of the caching docs; no provider account, invoice, or cache-hit measurement was reproduced here[^dd-v2-tour-2026]
- Provider support moves quickly, and the matrix is tied to v2.59-era provider behaviour, hence the short `stale_after`.
- The `Caching()` example in the article is attached to an agent that was run against `TestModel`, where no real cache exists, so the caching path itself is **Reported**, not reproduced.

## Relationships

- **Is a** [capability](pydantic-ai-capability-primitive.md) in core `pydantic-ai`, alongside `Hooks`, `MCP`, `LocalWorkspace`, `Thinking` and `ToolSearch`.
- **Exposes** its health through [observability](pydantic-ai-observability.md) span attributes.
- **Depends on** stable prompt prefixes, which [run controls](pydantic-ai-run-controls.md) preserve with append-only instructions.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Caching is now one switch (v2.55)" (raw lines 249–264) for the setting equivalence, retention tiers, the provider matrix, write-versus-read pricing, `Caching(messages=False)`, the Coder default, and the lazy `pydantic_ai.mcp` import; §"Observability: Logfire or any OpenTelemetry backend" for the `pydantic_ai.cache.*` attributes; §"What changed in v2.58 and v2.59" for `on_change='append'`. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — a docs-derived summary by a third party; nothing was executed or measured.
