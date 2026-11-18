---
type: Concept
title: Pydantic AI history processors
description: How the ProcessHistory capability rewrites a Pydantic AI history before every request — trimming, summarizing into a CompactionPart, compacting at a context-window fraction, timing maintenance for a cold prompt cache, and testing what the provider actually receives.
tags: [pydantic-ai, agents, context-management, cost]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:45:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-message-history-docs
    resource: ../raw/core-concepts/message-history/index.md
    scope: ../raw/core-concepts/message-history/
    kind: documentation
    revision: sha256:1ce4fb2b993d082dda71e8dac360c83d1279820f53ec1ce7ab66dbb65d0cfdff
    title: "Messages and chat history"
---

`ProcessHistory` is a core [capability](pydantic-ai-capability-primitive.md) that wraps a callable taking a list of `ModelMessage` and returning a modified list of the same type, applied before each model request[^pydantic-message-history-docs] "Each" matters: it runs before every request inside a run, not only the first, so after a tool call it runs again and sees the run's own tool calls and results behind the earlier history. A processor that should see only history from *earlier* runs takes a `RunContext` and leaves unchanged the messages whose `run_id` equals `ctx.run_id`.

Processors are applied in sequence, each to the previous one's output, and may be synchronous or asynchronous[^pydantic-message-history-docs] Several can be attached at once, in which case the order in `capabilities=[...]` is the order of application. The reasons the vendor gives for wanting one are privacy filtering, token cost, and giving the model less context.

```python
agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[ProcessHistory(filter_responses), ProcessHistory(keep_recent_messages)],
)
```

Whether a processor wants the `RunContext` is detected by resolving its **type hints at runtime**, so every annotated type in its signature must be imported at runtime and not only under `if TYPE_CHECKING:`; an unresolvable annotation raises `UserError` rather than silently calling the processor without context[^pydantic-message-history-docs] With the context it can read dependencies, model information and usage — the vendor's example keeps only the last three messages once `ctx.usage.total_tokens` passes 1,000.

## Two rewriting patterns

**Keep the recent tail.** `messages[-5:]` when the list is longer than five is the shape of every simple trim[^pydantic-message-history-docs]

**Summarize the middle.** A cheaper model summarizes the older turns and the summary replaces them as a single `CompactionPart`, which every model then receives as framed user-voice text[^pydantic-message-history-docs] The example keeps the first request — the task — and the latest turn, and chooses the latest turn's start as a request that carries a user prompt and **no** tool results, so no tool call is cut off from its result. That rule is the one thing a hand-written summarizer has to respect: [repair](pydantic-ai-history-repair.md) will synthesize a return for a call it cannot pair, but the pair is what the model needs to reason about the step.

## Compacting when the window fills

The processors above rewrite on every run; a window-aware one waits. `ctx.context_window_used` returns the fraction of the model's window occupied after the latest response, or `None` when it cannot be computed reliably[^pydantic-message-history-docs] `None` must be read as *unknown*, not as an empty window: it comes back before the first model response, and whenever the window or the response usage is unknown. The documented pattern compacts above `0.8` and keeps the most recent complete user turn plus everything after it.

Accounting details decide whether the estimate is early enough[^pydantic-message-history-docs]:

| Case | Measured against |
| --- | --- |
| `FallbackModel` | the smallest window among its candidates, so compaction happens early enough for whichever answers |
| Anthropic response that ran a server-side tool loop or compaction | only its last pass, and only under a beta that reports the passes; [Anthropic context management](anthropic-context-management.md) carries the detail |
| Window unknown to `genai-prices` (custom or local model) | set it explicitly: `profile={'context_window': 128_000}` |

Two composition rules follow[^pydantic-message-history-docs] Instructions are sent with every request rather than stored in the history, so compaction cannot drop them — but if the agent uses `system_prompt` instead, put `ReinjectSystemPrompt` after the compaction processor so the prompt dropped with the old history comes back. And the example keeps everything from the latest plain user turn onward, which means a turn that pairs tool results with a new prompt is kept whole, so a run started that way may keep more history than needed.

## Timing maintenance for a cold cache

Rewriting history has two costs: the work, and a **cache cost** — the next request re-writes the whole prompt prefix at full input price because the mutated prefix can no longer hit the provider's cache[^pydantic-message-history-docs] That second cost is only real while the cache is warm. Once a conversation has been idle longer than the provider retains the prefix, the next request pays full price anyway, so that turn is a free moment for any deferrable maintenance.

The framework carries the documented default at the provider layer as `ModelProfile.default_cache_retention` — 5 minutes for Anthropic, 30 minutes for OpenAI's GPT-5.6 and later[^pydantic-message-history-docs] Where retention depends on account configuration rather than the model, as OpenAI's does for earlier models whose default hinges on Zero Data Retention, the field is left unset and the outlook is `'unknown'` unless a retention is passed. `prompt_cache_outlook(history, profile=..., now=...)` then predicts from the message history alone whether the next request is likely to hit a warm cache:

| Outlook | Meaning | Action |
| --- | --- | --- |
| `'cold'` | Idle past the retention window | Flush pending maintenance for free |
| `'warm'` | The mutation would sacrifice a live cache hit | Defer it if it can wait |
| `'unknown'` | No documented retention, or a history without timestamps | Treat like `'warm'` — never mutate on a guess |

Retention requested through settings replaces the provider default: the unified `cache='1h'`, `anthropic_cache='1h'`, or `openai_prompt_cache_retention='24h'` on OpenAI models before GPT-5.6[^pydantic-message-history-docs] `Model.resolve_cache_retention()` works it out from the settings a request is made with and returns `None` when they ask for nothing, so passing its result as `retention=` keeps the profile's default exactly when the request does not override it. A `before_model_request` [hook](pydantic-ai-lifecycle-hooks.md) has both the model and the request's settings in hand, which is the documented place to decide whether to do the expensive work this turn:

```python
@hooks.on.before_model_request
async def compact_when_cold(ctx, request_context):
    outlook = prompt_cache_outlook(
        request_context.messages,
        profile=request_context.model.profile,
        retention=request_context.model.resolve_cache_retention(request_context.model_settings),
    )
    if len(request_context.messages) > 10 and (ctx.usage.total_tokens > 100_000 or outlook == 'cold'):
        request_context.messages = request_context.messages[:1] + request_context.messages[-4:]
    return request_context
```

`CachePoint(ttl='1h')` markers already in the history extend the boundary the same way, when the provider supports that retention (one of the profile's `supported_cache_retentions`)[^pydantic-message-history-docs] The exceptions are worth knowing before relying on it: OpenAI ignores `CachePoint.ttl`, so a one-hour marker does not extend GPT-5.6's 30 minutes, and Azure and providers without a single documented default leave the field unset, producing `'unknown'` unless the settings request a retention or you pass one explicitly. [Prompt caching](pydantic-ai-prompt-caching.md) owns the framework-wide switch; this section owns *when* to spend a mutation.

## Testing a processor

`FunctionModel` is the seam: the model function receives the messages the provider would actually get, so a test can capture them and assert on the processed list rather than on the processor's return value[^pydantic-message-history-docs] The documented test asserts that a client-supplied question and a `Question 2` prompt arrive as two adjacent `ModelRequest`s after the response-filtering processor ran — the same shape as [model and provider testing](pydantic-ai-models-and-providers.md) uses for `TestModel` and `FunctionModel`.

## Limits

- Single vendor page naming **no Pydantic AI version, author or date**, so this page is `draft` under the `pydantic-ai` domain rule; `ProcessHistory` is described as a capability, which [capability primitive](pydantic-ai-capability-primitive.md) records as v2's unit[^pydantic-message-history-docs]
- **Reported** evidence: no processor was attached, no history trimmed or summarized, no window measured, no cache outlook computed and no test executed.
- The processor API is shown as `ProcessHistory(callable)`; the capability's full constructor surface, whether a processor may raise to abort the run, and what happens when a processor returns an invalid ordering are unstated.
- The cache-retention defaults are the vendor's documentation snapshot and are explicitly account- and model-dependent for OpenAI's earlier models; no provider was queried to confirm them.
- The summarization example is illustrative: its summary model, prompt and `CompactionPart` construction are shown, but the cost or quality of summarizing versus trimming is not measured.

## Relationships

- **Operates on** [message history](pydantic-ai-message-history.md) and writes what the [repair](pydantic-ai-history-repair.md) pipeline and the provider serializer consume.
- **Is a** [capability](pydantic-ai-capability-primitive.md) that fits beside `ReinjectSystemPrompt`, whose ordering relative to a compaction processor decides whether the system prompt survives.
- **Depends on** [prompt caching](pydantic-ai-prompt-caching.md) economics: the cache cost is why maintenance is scheduled rather than continuous, and `CachePoint` is why a retention can be extended in history.
- **Overlaps with** [Anthropic context management](anthropic-context-management.md) and the Harness compaction strategies, which do provider-side or packaged versions of the same trimming — the guide points to them as the fuller picture.
- **Runs inside** the `before_model_request` stage of [lifecycle hooks](pydantic-ai-lifecycle-hooks.md), where a hook can make the same decision with the request's own settings.
- **Contrasts with** [mid-run injection](pydantic-ai-mid-run-injection.md): a processor changes what is sent from existing history; `enqueue` adds new content to a live run.

[^pydantic-message-history-docs]: Pydantic Docs, "Messages and chat history", <https://pydantic.dev/docs/ai/core-concepts/message-history/>, 15,322 words as declared and 15,615 by local `wc -w`, no date and no Pydantic AI version named; local capture `raw/core-concepts/message-history/index.md`, 1,477 lines, content digest sha256:1ce4fb2b. §"Processing Message History" (raw lines 1131–1138) and "Usage" (1139–1174) for the per-request scope, sequencing, sync/async processors and the reasons; "Keep Only Recent Messages" (1175–1195); "RunContext parameter" (1196–1224) for the runtime type-hint resolution and the `UserError`; "Summarize Old Messages" (1225–1278) for the middle-summary pattern, the latest-turn rule and the `CompactionPart`; "Compact when the context window fills" (1279–1327) for `ctx.context_window_used`, `None` as unknown, the `0.8` threshold, the `FallbackModel` and Anthropic measurement rules, `ReinjectSystemPrompt` ordering and `profile={'context_window': …}`; "Scheduling maintenance into cache-cold windows" (1328–1398) for the two costs, `default_cache_retention`, `prompt_cache_outlook`, the retention settings, `resolve_cache_retention`, the hook example, `CachePoint(ttl='1h')` and the OpenAI/Azure exceptions; "Testing History Processors" (1399–1450); "Multiple Processors" (1451–1474). Evidence class: **Reported** — vendor documentation; nothing was executed.
