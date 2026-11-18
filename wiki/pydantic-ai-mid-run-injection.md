---
type: Concept
title: Pydantic AI mid-run injection and instruction placement
description: How instructions and messages enter a Pydantic AI conversation after it starts — mid-conversation and request-scoped system prompts with their provider renderings, typed capability parts, metadata-based identification, and enqueue with its asap and when_idle priorities, placement rules and event confirmation.
tags: [pydantic-ai, agents, context-management, capabilities]
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

Once a conversation exists, Pydantic AI has three ways to add to it: a `SystemPromptPart` placed after the first request becomes a mid-conversation instruction, `scope='request'` limits one to the request it travels with, and `enqueue` injects content into a *live* run at a position — or a priority — the framework chooses[^pydantic-message-history-docs] The shared design point is that position is meaning: the framework keeps an instruction where it was put rather than folding it into the top-level system prompt, because editing the front of a prompt invalidates every cached prefix behind it.

## Standing prompt versus mid-conversation instruction

A `SystemPromptPart` in the first `ModelRequest` is the agent's standing system prompt and always hoists to the provider's top-level system parameter[^pydantic-message-history-docs] One in any *later* request is a mid-conversation instruction — something that became true partway through the session, whether it arrived through a stored `message_history` or from `ctx.enqueue(...)` during the run. It stays where it was put. That is what lets a provider reuse the unchanged prefix: editing the top-level system prompt invalidates everything behind it, while an instruction appended in place leaves the conversation up to that point cacheable. Position alone does not turn caching on; the active model's [prompt-caching](pydantic-ai-prompt-caching.md) settings or an explicit `CachePoint` still have to be configured.

How the instruction reaches the model depends on the provider[^pydantic-message-history-docs] Where the API accepts a system message inside the conversation, it is sent as one, and carries the operator authority that implies — Anthropic supports this on some models and may nudge the position to satisfy its own placement rules, OpenRouter does on some routes; [Anthropic prompt caching](anthropic-prompt-caching.md) owns that provider's rendering. Everywhere else it becomes a `<system>`-tagged `UserPromptPart` at the same position with its text as written: the instruction still applies from where it was put, but the model can tell it arrived over the user channel and may treat it as a strong preference rather than a rule.

On those models the system prompt also gains a short announcement explaining the tag, and a few model families need a *sealed* block instead of a plain one[^pydantic-message-history-docs] Claude Sonnet 4.6 ignores plain `<system>` blocks; Claude Sonnet 5.5 and Haiku 5.5, and Grok 4.3 through 4.7, follow sealed ones better than their alternatives, so for them (`needs_sealed_system_blocks`) each block is written `<system verified>`, is placed after the user's words in its request, and the announcement says every application block carries that attribute and governs the reply to the words ahead of it. The attribute is a label, not proof — text that copies it still gets a lookalike note, and measurements found a copy in a tool result was not followed while a copy in the user's own text could be, on some models even suppressing the application's real change for that turn[^pydantic-message-history-docs] [Prompt framing](pydantic-ai-prompt-framing.md) owns the notes, the announcement and those measurements.

One writing rule follows from the same mechanism: phrase the instruction as **what changed**, not as an override of the user[^pydantic-message-history-docs] Models are trained to resist instructions that appear to work against the person they are talking to, and that applies to the system role too — "the build tag is no longer confidential" lands where "ignore what the user was told earlier" does not.

## Request-scoped prompts

Some instructions are true only for the request they travel with: budget left right now, a nudge against instruction fade[^pydantic-message-history-docs] Give the part `scope='request'` and the model sees it only in that model request — the next request, even the next step of the same run, no longer shows it. A capability produces one from `before_model_request` with an `InstructionCapabilityPart` in the system voice:

```python
@dataclass
class ShowRequestsLeft(AbstractCapability[Any]):
    async def before_model_request(self, ctx, request_context):
        limit = ctx.usage_limits.request_limit if ctx.usage_limits else None
        if limit is not None:
            ctx.enqueue(
                RequestsLeftPart(
                    content=OperatorText(f'{limit - ctx.usage.requests} model request(s) left in this run.'),
                    source=OperatorSource(),
                    scope='request',
                )
            )
        return request_context
```

The prompt stays in the history — the history records what each request was sent — and only what the model is shown changes. Two provider renderings follow[^pydantic-message-history-docs]:

| Rendering | Behaviour | Cost |
| --- | --- | --- |
| API can keep it and stop showing it (Anthropic, on models taking mid-conversation system messages) | Sent unchanged with every request, and costs nothing once its request has been answered; the API stops showing it at the next user message, so a prompt followed by a request with none — a retry for an empty response — is left out of that request and every later one | Keeps the cached prefix and, on models tying reasoning to the exact conversation, the reasoning valid; *removing* it would count as editing the conversation |
| Everywhere else | Sent with its own request only, at the end of it, left out of every later one, rendered like any mid-conversation system prompt | Prefix stays valid because the breakpoints land before it |

Consequences worth planning for[^pydantic-message-history-docs]:

- **Traces.** `gen_ai.input.messages` on a model-request span records the messages that request was sent. Where the prompt is re-sent every request, a later span adds `"visible": false` to the part whose request has been answered; elsewhere it is simply absent from later spans.
- **Server-side state.** With OpenAI Responses' `openai_previous_response_id`, a response continues only while the messages before it are unchanged, so leaving the prompt out of the next request means that request sends the full history without `previous_response_id` and chaining is given up for the request after it. With `openai_conversation_id` the provider keeps every message it was sent, so a prompt sent once stays visible on every later request and leaving it out changes nothing.
- **Cache breakpoints** placed through settings such as `anthropic_cache_messages` land before the prompt, so the next request can still read what was cached.
- **Retries and continuations.** A request and any continuation of it — an Anthropic `pause_turn`, a retry, a [fallback](pydantic-ai-model-fallback.md) attempt — count as the same request.
- **Abandoned requests.** A request-scoped prompt in a request that never gets a response, because the run failed or was cancelled, is removed when the run gives up on that request.

A request-scoped prompt is **not** a request-only change[^pydantic-message-history-docs] The prompt stays in history; assigning `request_context.messages` never reaches history at all. Adding a request-scoped part to `request_context.messages` alone is the mistake the docs name: it never enters history, so the next request does not send it, and on a model that ties its reasoning to the exact conversation, dropping it from one request to the next counts as editing the conversation.

Use it for something about the current moment. Something that stays true belongs in the agent's [instructions](pydantic-ai-run-controls.md) or a regular mid-conversation prompt; a request-scoped reminder can restate an instruction at the end of a request against instruction fade but does not replace it, and anything the model must still act on after the next request needs `scope='conversation'`[^pydantic-message-history-docs] Instructions whose text changes over the conversation can use `on_change='append'`, which delivers each change this way and keeps the instruction prefix cached.

## Capability parts

A `CapabilityPart` is typed content a capability or your application tells the model mid-conversation, defined as a subclass per kind of record: `DataCapabilityPart` for data in a frame on the user channel, `InstructionCapabilityPart` for the application's voice[^pydantic-message-history-docs] Two properties make it different from a raw string:

- **It stays typed in the history.** A history processor, compaction summarizer or UI finds it by type and never mistakes it for something the user said. It is rendered into request parts only on the way to the model, in `prepare_messages`, which every model calls before mapping the history — so a custom model's adapter only ever receives parts it already maps, an override of `prepare_messages` sees the typed parts before calling the base implementation, and a `Model.request` made outside an agent run also goes through it. A model that maps a capability part it never rendered raises `UserError`.
- **It renders deterministically.** Rendering reads only the part's content, its declared attributes and the rendering facts stored with it, so the same history produces the same bytes on every request, in every process, and after a `ModelMessagesTypeAdapter` round trip — which is what keeps the prompt cache warm. The part's *source* decides whether it is rendered in the application's voice, in the user's turn labelled as attached on the user's behalf, or as data in a tag with a note naming who wrote it.

The client boundary is the same one [untrusted history](pydantic-ai-client-supplied-history.md) describes: UI adapters never send capability parts to a frontend, and `sanitize_messages` drops any a client sends[^pydantic-message-history-docs]

## Identifying a system prompt you added

Code that adds a system prompt sometimes has to find it again — to add a note once, count reminders sent, replace an earlier note, or tell its own records apart[^pydantic-message-history-docs] Give the `SystemPromptPart` a `metadata` dictionary and match on a key such as `origin`, never on visible text, which changes and which a user can type:

```python
def has_note(messages: list[ModelMessage]) -> bool:
    return any(
        isinstance(part, SystemPromptPart)
        and part.metadata is not None
        and part.metadata.get('origin') == ORIGIN
        for message in messages if isinstance(message, ModelRequest)
        for part in message.parts
    )
```

The metadata is never sent to the model, so it changes neither the request nor the prompt cache, and it travels with the part into `all_messages()`, through `ModelMessagesTypeAdapter` and into a continued conversation[^pydantic-message-history-docs] `ModelRequest.metadata` is no substitute, because consecutive requests are merged and a merged request keeps only Pydantic AI's own metadata. Like other application-only fields the metadata does not survive a round trip through the UI adapters.

## Enqueue: injecting into a live run

Tools, capability hooks, external code driving `agent.iter()`, and code driving a realtime session can inject content mid-run with `RunContext.enqueue`, `AgentRun.enqueue` or `RealtimeSession.enqueue`[^pydantic-message-history-docs] Any of them may be called from synchronous or asynchronous code, including a tool or callback running in another thread; calls after the run or session has ended raise `UserError`; and for standard runs submission is synchronized with the final drain, so a concurrent call is either accepted for delivery or rejected as the run ends.

`priority` decides **when** it lands[^pydantic-message-history-docs]:

| Priority | Delivered | Use for |
| --- | --- | --- |
| `'asap'` (default) | At the earliest opportunity — added to the next `ModelRequest`, or used to redirect the run into one more request if the agent would otherwise terminate | Context that must reach the model as soon as possible; this is what other frameworks call **steering** |
| `'when_idle'` | Only when the agent would otherwise terminate, after any `'asap'` messages | New work that should not interrupt — a follow-up task — and that the run should pick up once done |

A run that pauses for [deferred tools](pydantic-ai-deferred-approvals.md) is not redirected: content still queued at the pause is added to the history instead, so a resumed run sees it[^pydantic-message-history-docs] That applies when the paused step's tool results end the history; if *every* call in that step was deferred the history ends with those calls, so queued content redirects the run as usual — and so does content that includes a `ModelResponse`. With `run_stream()` the streamed result's messages do not include it.

**What `enqueue` accepts.** Each positional argument is one item: a piece of `UserContent` (a `str` or multimodal content such as `ImageUrl`, with adjacent pieces gathered into a single `UserPromptPart`, so `enqueue('caption', image)` makes one turn and a list has to be spread as `enqueue(*items)`); a `ModelRequestPart` such as `SystemPromptPart`; or a complete `ModelRequest`/`ModelResponse`, to control request-level fields or inject a synthetic prior turn[^pydantic-message-history-docs] Adjacent part-style items are coalesced into one `ModelRequest` while complete messages stay separate, so one call can inject an interleaved exchange — a synthetic tool call followed by its result — and the content must end in a request so the agent has something to respond to.

**What you get back.** The standard-run methods return an `enqueue_id` for a non-empty call and `None` for an empty one[^pydantic-message-history-docs] When the content is actually delivered, the event stream yields an `EnqueuedMessagesEvent` carrying that id plus the delivered content, which is how a client learns its steering message took effect. The event holds the same message objects as the run's history; content that went into a tool call's request has no message of its own, so `messages` holds a request of its own with the delivered parts while `parts` holds the request parts as they sit in history. A history processor that replaces history with new objects does not affect the event, but in-place mutation of delivered content is visible through it.

**Delivery inside a tool call.** Content enqueued during a tool call — from the tool or from a capability hook wrapping it — is a side effect of that call, so it goes into the `ModelRequest` carrying the call's `ToolReturnPart`, right after it[^pydantic-message-history-docs] With parallel calls, each call's content follows its own return in the order that call enqueued it, and the model still gets all of a request's tool results ahead of the enqueued content, as providers require. These cases get their own message instead: a complete `ModelRequest`/`ModelResponse` (which keeps its message-level fields), anything enqueued outside a tool call, content whose call has no `ToolReturnPart` in the next request — a tool that raised `ModelRetry`, say — content delivered in a later step, and content enqueued after something already added as its own message. An enqueued `SystemPromptPart` lands the same way and becomes a mid-conversation prompt, keeping its position instead of being lifted into the top-level prompt; only enqueue one for an instruction you authored, since late-arriving tool or webhook output belongs in user content.

**When the drain runs.** `'asap'` messages are drained in `before_model_request` — once ahead of the other capabilities' hooks and once after them, so a `before_model_request` hook's own enqueue lands in the request being prepared — and again at the end-of-run point if content arrived during the final step; `'when_idle'` messages are drained only when the agent would otherwise reach `End`, after every capability's `after_node_run` hook, which lets a capability redirect the run and still enqueue there[^pydantic-message-history-docs] Both fire however the run is driven — `Agent.run`, `AgentRun.next()` or a bare `async for` — but a `wrap_model_request` hook that short-circuits without calling its handler skips `before_model_request` and therefore that request-time drain.

## Changing a queued message

`AgentRun.dequeue` removes a queued message and `AgentRun.set_enqueue_priority` re-prioritizes it, keeping its place in the queue and its `enqueue_id` — the pair a chat UI needs when the user types while the agent is working, with "send now" promoting `'when_idle'` to `'asap'`[^pydantic-message-history-docs] Both return `False` once the message is no longer queued — delivered, already dequeued, or the run ended — which is not an error, since a click can race with delivery: the check and the change happen under the same lock as delivery, so exactly one wins, and `False` does not say which happened. To tell a user a message was sent, watch for the `EnqueuedMessagesEvent` carrying its `enqueue_id`; a dequeued message gets no event, and one whose priority changed is announced under its original id.

Delivery after a change follows the priority[^pydantic-message-history-docs] A `'when_idle'` message promoted to `'asap'` goes into the next model request as its own `ModelRequest`, after any `'asap'` messages queued before it. Content a tool enqueued as `'asap'` and then demoted is delivered like other `'when_idle'` content — *not* next to that tool's result. Tools and capability hooks reach the same operations as `RunContext.dequeue` and `RunContext.set_enqueue_priority`, and realtime code through `RealtimeSession.dequeue` and `RealtimeSession.set_enqueue_priority`. Inside a [durable execution](pydantic-ai-durable-execution.md) unit both raise `UserError`, as the guide says `enqueue` does too, since the change would be lost on replay.

## Limits

- Single vendor page naming **no Pydantic AI version, author or date**, so this page is `draft` under the `pydantic-ai` domain rule[^pydantic-message-history-docs]
- **Reported** evidence: no agent was steered, no message enqueued, dequeued or promoted, no capability part rendered, no provider rendering compared and no trace inspected. The measurement tables behind the sealed-block trade are on [prompt framing](pydantic-ai-prompt-framing.md), quoted there as the vendor's numbers.
- The guide does not describe the ordering between two `'asap'` messages delivered within one `before_model_request`, nor whether an `enqueue` accepted during the final drain can still be dequeued.
- Which Anthropic and OpenRouter models accept a native mid-conversation system message is a link, not a list, and [Anthropic prompt caching](anthropic-prompt-caching.md) records only the models its own source names.
- `prepare_messages` is named as the render point; the exact rendering facts stored on a capability part, and the full subclass set, are not enumerated.

## Relationships

- **Builds on** [message history](pydantic-ai-message-history.md): every injected item becomes an ordinary request or response in the same list.
- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md) for `before_model_request` and capability parts, and [lifecycle hooks](pydantic-ai-lifecycle-hooks.md) for where the drains sit relative to `after_node_run`.
- **Depends on** [prompt caching](pydantic-ai-prompt-caching.md) and [Anthropic prompt caching](anthropic-prompt-caching.md) for the prefix-stability rules that motivate staying in place, and on [prompt framing](pydantic-ai-prompt-framing.md) for the notes and announcement the `<system>` rendering triggers.
- **Is used by** [deferred tool approval](pydantic-ai-deferred-approvals.md), whose pause changes how queued content lands, and by [subagent task control](pydantic-ai-subagent-tasks.md), whose `DelegationReports` delivers reports through this queued-message API.
- **Extends to** [realtime voice agents](pydantic-ai-realtime-voice.md), whose session exposes `enqueue`, `dequeue` and `set_enqueue_priority`, though a realtime session carries neither the framing notes nor the announcement.
- **Pairs with** [history processors](pydantic-ai-history-processors.md): a processor rewrites what history holds, `enqueue` adds to it, and only the latter is visible to a run in flight.

[^pydantic-message-history-docs]: Pydantic Docs, "Messages and chat history", <https://pydantic.dev/docs/ai/core-concepts/message-history/>, 15,322 words as declared and 15,615 by local `wc -w`, no date and no Pydantic AI version named; local capture `raw/core-concepts/message-history/index.md`, 1,477 lines, content digest sha256:1ce4fb2b. §"Mid-conversation system prompts" (raw lines 224–239) for the standing-versus-mid-conversation split, the caching rationale, the provider renderings, the sealed `<system verified>` blocks and the phrasing advice; "What each rendering gives up" (240–331) for the flags and the copied-marker measurements; "Request-scoped system prompts" (366–445) for `scope='request'`, the capability sample, the two renderings, the trace `visible: false` rule, the OpenAI state interactions, the breakpoint and retry rules, the abandoned-request removal, the request-only distinction and the guidance on when not to use it; "Capability parts" (446–455) for the subclass split, the typed-history and `prepare_messages` rules, the `UserError`, the rendering facts, the cache-stability argument and the client exclusion; "Identifying system prompts" (456–497) for the metadata pattern and the `ModelRequest.metadata` caveat; "Injecting messages mid-run" (1019–1039) and its subsections "From inside a tool or hook" (1040–1065) and "From external code driving agent.iter()" (1066–1093) for the priorities, deferred-pause handling, accepted item types, coalescing, `enqueue_id`, `EnqueuedMessagesEvent`, placement inside a tool call and the drain points; "Dequeuing a message or changing its priority" (1094–1130) for the two operations, the `False` semantics, the event rule, the delivery ordering and the durable `UserError`. Evidence class: **Reported** — vendor documentation; nothing was constructed, steered or rendered.
