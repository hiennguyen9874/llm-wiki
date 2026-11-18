---
type: Concept
title: Pydantic AI history repair
description: How Pydantic AI makes a crashed, cancelled or hand-built message history provider-valid before each request — the synthesized interrupted tool return, the orphaned results it removes, the merge that reorders turns, the live-frontier cases it leaves alone, and when to call repair_messages yourself.
tags: [pydantic-ai, agents, context-management, reliability]
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

Providers reject a request whose history pairs a tool call with no result, or a result with no call, and a run that was cancelled or crashed partway through leaves exactly that state — as does a hand-built, truncated or context-evicted history[^pydantic-message-history-docs] Pydantic AI repairs the history it was given before each model request, under one rule: **adapt to what the provider accepts without discarding anything you meant to send**. Repairs only add synthesized parts or remove parts no provider could accept, so a malformed frontier turns into a request that goes out rather than an exception. The repair is deterministic and idempotent, and the synthesized parts carry no wall-clock data, so reusing a repaired history does not invalidate provider prompt caches[^pydantic-message-history-docs]

## The pipeline

| Step | What happens |
| --- | --- |
| **Add** | A `ToolReturnPart` is synthesized for every tool call with no result, saying the call was interrupted before a result was produced |
| **Remove** | Every orphaned tool result is dropped — a `ToolReturnPart` of any outcome, or a legacy tool-bound `RetryPromptPart`, whose call is absent from the history, including one placed *before* its call |
| **Merge** | Consecutive compatible messages become one; two adjacent `ModelRequest`s form a single turn, with tool results ordered ahead of user parts |
| **Order** | Tool results answering one response are sent in the order of the calls they answer, however the history stores them |

The synthesized return is marked so application code can tell it apart: `outcome='interrupted'` — neutral, and unlike `'failed'` and `'retried'` not surfaced as a provider error — plus `{'pydantic_ai_synthesized_tool_return': True}` in its `metadata`[^pydantic-message-history-docs] A call whose arguments were cut off mid-stream is handled the same way: the call is kept as-is with its verbatim (invalid) arguments in the history, while the request serializers send them as `{"INVALID_JSON": "<raw args>"}` so a provider demanding an object still accepts the request.

Removal can cascade. If dropping an orphaned result empties an *interior* `ModelRequest`, that request is removed with it; if it empties the *last* message, an empty request is kept so the history still ends on a `ModelRequest`[^pydantic-message-history-docs] Merging then changes message boundaries while preserving content, which is why processed history you inspect afterwards may hold fewer messages than you passed in — the ordering rule also explains a mismatch after `end_strategy='early'` stores output tool results first, or after a UI client rebuilds them in completion order[^pydantic-message-history-docs]

## What the repair deliberately leaves alone

A tool call that can still receive a real result is not abandoned. When the history ends on a `ModelResponse` with tool calls, running without a new `user_prompt` executes them, and [deferred tool calls](pydantic-ai-deferred-approvals.md) are matched to their `deferred_tool_results` — including when a complete `ModelRequest` carrying the already-executed results follows the response[^pydantic-message-history-docs] Repair of that live frontier happens only when the interruption is evident:

- a **trailing request** with `state='interrupted'`, as left by a crash during tool execution, whose response's unanswered calls will never run;
- a **final response** with `state='interrupted'`, as left by a [cancelled stream](pydantic-ai-streamed-output.md) or by a token or cost [limit](pydantic-ai-run-controls.md) crossing, followed by a new user prompt.

Without a new prompt, a run executes an interrupted final response's tool calls like any other[^pydantic-message-history-docs] One case is left to the caller: a new user prompt on top of a history whose final response, **not** marked `state='interrupted'`, still has unanswered calls. Those calls can still be answered — by resuming, or with `deferred_tool_results` — so the framework raises rather than abandon them. When abandoning is intended, `repair_messages` runs the same pipeline on demand:

```python
runnable = repair_messages(stored)          # close out the frontier
# runnable can now be passed as message_history= with a new prompt
runnable = repair_messages(stored, repair_last_response=False)  # repair only the rest
```

`repair_messages` is also the tool for code outside a run — a store, a UI, or a capability recording a history a later run must be able to pick up[^pydantic-message-history-docs]

## Scope

The pipeline handles regular, locally-executed tool calls only[^pydantic-message-history-docs] Provider-native tool parts, produced and resolved inline by the provider, are left untouched and repaired by each model's own serializer. Two further classes stay out of scope and may still be rejected: duplicate tool results for one call, and provider-specific ordering rules beyond call/result pairing — where such a rule is known and verified, the model's serializer normalizes the request instead.

## Limits

- Single vendor page naming **no Pydantic AI version or date**, so the page is `draft` under the `pydantic-ai` domain rule[^pydantic-message-history-docs] `repair_messages` is dated only indirectly: [the v2 release](pydantic-ai-v2-release.md) lists it in the v2.53.0 row of 2026-10-01.
- **Reported** evidence throughout: no package was installed, no history repaired, no interrupted run created and no provider request attempted, so determinism, idempotency and cache safety are the vendor's claims, not measurements here.
- The guide names the pipeline's steps and their intent but not the exact part types it may synthesize beyond the interrupted return, nor the full compatible-message matrix behind "consecutive compatible messages".
- Which provider-specific ordering rules are known and normalized per serializer is stated to exist, not enumerated.

## Relationships

- **Operates on** the list defined in [message history](pydantic-ai-message-history.md), including the delta parts that record tool availability, capability loads and model-settings changes.
- **Is complemented by** [untrusted-history sanitization](pydantic-ai-client-supplied-history.md): sanitization narrows what a client may claim, repair makes the result acceptable to the provider — both run before a request, for different reasons.
- **Protects** [deferred tool approval](pydantic-ai-deferred-approvals.md) resumes and [durable execution](pydantic-ai-durable-execution.md) replays, where a process that died mid-tool leaves the frontier this page closes out.
- **Relies on** the `state='interrupted'` markers that [streamed output](pydantic-ai-streamed-output.md) cancellation and [run controls](pydantic-ai-run-controls.md) limits produce.
- **Interacts with** [prompt caching](pydantic-ai-prompt-caching.md): synthesized parts are timestamp-free so a repaired history resends the same bytes.

[^pydantic-message-history-docs]: Pydantic Docs, "Messages and chat history", <https://pydantic.dev/docs/ai/core-concepts/message-history/>, 15,322 words as declared and 15,615 by local `wc -w`, no date and no Pydantic AI version named; local capture `raw/core-concepts/message-history/index.md`, 1,477 lines, content digest sha256:1ce4fb2b. §"Making histories provider-valid" (raw lines 498–546) for the guiding rule, the add/remove/merge steps, `outcome='interrupted'` and its metadata key, the `{"INVALID_JSON": …}` serialization, the `ToolAvailabilityDeltaPart`/`CapabilityLoadDeltaPart`/`ModelSettingsDeltaPart` records, the ordering and `end_strategy='early'` caveat, the idempotency and cache claims, the live-frontier cases and `state='interrupted'` markers, the raising case, the `repair_messages` sample and `repair_last_response=False`, and the native-tool and out-of-scope limits. Evidence class: **Reported** — vendor documentation; nothing was executed.
