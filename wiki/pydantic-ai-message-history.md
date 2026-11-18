---
type: Concept
title: Pydantic AI message history
description: How Pydantic AI records, reads, continues, serializes and correlates a conversation — the request and response fields that carry provenance, message_history and ReinjectSystemPrompt, ModelMessagesTypeAdapter round trips, run_id versus conversation_id, and reuse across models, agents and providers.
tags: [pydantic-ai, agents, context-management]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:10:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-message-history-docs
    resource: ../raw/core-concepts/message-history/index.md
    scope: ../raw/core-concepts/message-history/
    kind: documentation
    revision: sha256:1ce4fb2b993d082dda71e8dac360c83d1279820f53ec1ce7ab66dbb65d0cfdff
    title: "Messages and chat history"
---

A Pydantic AI conversation is a list of plain dataclasses — `ModelRequest` and `ModelResponse`, each holding a `parts` list — and that list is the framework's unit of continuation: hand it back as `message_history=` and the next run starts from it[^pydantic-message-history-docs] Because the format is model-independent, the same history can continue on a different model or a different agent, which is what makes agent hand-off and provider switching cheap. Everything else in the vendor's message-history guide builds on this contract: [repair](pydantic-ai-history-repair.md) makes a damaged list provider-valid, [sanitization](pydantic-ai-client-supplied-history.md) makes a client-supplied one safer, [processors](pydantic-ai-history-processors.md) rewrite it before sending, and [mid-run injection](pydantic-ai-mid-run-injection.md) adds to it while a run is live.

## Reading messages off a result

Both `RunResult` (from `Agent.run` / `run_sync`) and `StreamedRunResult` (from `Agent.run_stream`) expose two pairs: `all_messages()` / `all_messages_json()` for everything including prior runs, and `new_messages()` / `new_messages_json()` for only the current run[^pydantic-message-history-docs] On a streamed result the list is incomplete until the stream finishes — before the first text arrives it holds only the `ModelRequest` — so read messages after the stream, or take `StreamedRunResult.result` for the settled form[^pydantic-message-history-docs]

The printed shape of a two-message exchange shows what an entry carries[^pydantic-message-history-docs]:

| Field | On `ModelRequest` | On `ModelResponse` |
| --- | --- | --- |
| `parts` | `UserPromptPart(content='…', timestamp=…)` and siblings | `TextPart(content='…')` and siblings |
| `timestamp` | arrival time | completion time |
| `instructions` | the run's instructions | — |
| `usage` | — | `RequestUsage(cost=Decimal('0.00023'), input_tokens=55, output_tokens=12)` |
| `model_name` / `model_id` | — | provider-reported name and the selector string |
| `run_id`, `conversation_id` | both | both |

Three kinds of *delta* part are also recorded in the history rather than shown to the model, so a later replay reconstructs the same run conditions without a screenshot of them[^pydantic-message-history-docs] `ToolAvailabilityDeltaPart` records a tool addition authored by a `ToolReturn(tools=[...])` return, placed immediately after that `ToolReturnPart` in the same request with the call's `tool_call_id` as the causal link; names are de-duplicated in first-occurrence order, already-revealed names are omitted, and tool *removal* has no representation. `CapabilityLoadDeltaPart` records a [capability loaded from code](pydantic-ai-capability-primitive.md) on the request it takes effect on, after the return of the tool call that loaded it. `ModelSettingsDeltaPart` records a recorded model-settings change — today only thinking effort — at the end of the request it applies to, which is the history side of [reasoning effort changes](pydantic-ai-reasoning-effort-changes.md).

## Continuing a run

Pass the list to `message_history=` on `run`, `run_sync` or `run_stream`[^pydantic-message-history-docs] One consequence is easy to miss: **when `message_history` is non-empty, no new system prompt is generated**, because the framework assumes the history already carries one. A history that came from something which does not round-trip system prompts — a UI frontend, a database that did not persist them, a compaction pipeline — therefore loses the agent's `system_prompt` silently. The fix is the `ReinjectSystemPrompt` capability, which re-injects the configured `system_prompt` at the head of the first request only when it is missing:

```python
result2 = agent.run_sync('Explain?', message_history=result1.new_messages())
```

`new_messages()` is the right quantity for a chat server that appends per turn: `all_messages()` re-sends the whole thread, while `new_messages()` is just the delta[^pydantic-message-history-docs]

## Which model answered

`ModelResponse.model_id` is the string the model was selected by — `'openai:gpt-6.1-sol'`, or an alias a capability resolved — while `model_name` is what the provider reported, often a dated version and identical for two configurations of one model[^pydantic-message-history-docs] When a capability moves a request to another model, such as a [fallback](pydantic-ai-model-fallback.md) candidate, the response records that candidate, so a later run continuing the history can tell which of the configured models answered and route a request back to it[^pydantic-message-history-docs]

## Two identifiers, two jobs

Every request and response carries `run_id` and `conversation_id`, and confusing them breaks `new_messages()`[^pydantic-message-history-docs]

| | `run_id` | `conversation_id` |
| --- | --- | --- |
| Scope | one `Agent.run` call | every run built on the same history |
| Inheritance | never inherited from `message_history` | inherited through `message_history` |
| Elsewhere | `RunContext.run_id`, `AgentRunResult.run_id`, `gen_ai.agent.call.id` span attribute | `AgentRunResult.conversation_id`, `gen_ai.conversation.id` |
| Override | `run_id='<your-id>'` for an ID minted by your application | `conversation_id='<your-id>'`, or `'new'` to fork |

A fresh `run_id` is generated per run, and each `Agent.run` — including a [deferred-tool resume](pydantic-ai-deferred-approvals.md) — counts as its own run. Passing `run_id=''`, or one already present in `message_history`, raises `UserError`, because both break new-message boundary detection; a retry of a failed run under the same `run_id` has to rebuild the history without the failed attempt's messages[^pydantic-message-history-docs] Pause/resume and multi-turn work correlate on `conversation_id` instead. `conversation_id='new'` forks a thread without the caller having to mint an ID. The [UI adapters](pydantic-ai-multimodal-input.md) auto-populate `conversation_id` from the protocol's own thread or chat ID, but protocol-level run IDs such as AG-UI's `runId` are **not** mapped onto `run_id` — pass it explicitly if you need them to match[^pydantic-message-history-docs]

## Serializing to JSON

`ModelMessagesTypeAdapter` is the intended codec, and a plain `TypeAdapter(list[ModelMessage])` is equivalent[^pydantic-message-history-docs] A round trip through `to_jsonable_python` / `validate_python`, or `to_json` / `validate_json`, produces a history the next run accepts, which is what makes Python–TypeScript sharing, eval fixtures and database storage possible:

```python
as_python_objects = to_jsonable_python(history_step_1)
same_history = ModelMessagesTypeAdapter.validate_python(as_python_objects)
```

Storing the whole `AgentRunResult` instead preserves the output, the messages, the new-message boundary, the output tool name, usage, run and conversation IDs, metadata and trace context; run-local state used only while executing is not stored. `StreamedRunResult` lasts only as long as its stream, so take `streamed.result` and store that[^pydantic-message-history-docs]

For a thread you mean to continue, the messages are not quite the whole conversation: `usage`, `conversation_id` and any [deferred tool requests](pydantic-ai-deferred-approvals.md) travel beside them[^pydantic-message-history-docs] Losing `usage` is the damaging case — passing `message_history` without it restarts every turn's `UsageLimits` budget at zero, so a cap set across the conversation is never reached. `conversation=` carries all three at once, raises `UserError` if combined with any of them, and works on a copy of the usage so the same bundle can be continued twice as a branch point; [conversation state](pydantic-ai-conversation-state.md) owns that object, its `revision`/`new_message_index` fields and its store. The Harness adds three capabilities that keep more than the conversation: `StepPersistence` (message snapshots at settled points plus an event log and tool-effect ledger, keyed by `conversation_id` and `run_id`), `ConversationSearch` (ranks what `StepPersistence` stored and lets the model pull earlier turns back into context), and `Memory` (markdown notes that outlive any one conversation, in a namespace you choose)[^pydantic-message-history-docs]

## Reuse across agents, models and providers

The same `message_history=` works when the next run uses a different `Agent`, which is the mechanism behind programmatic agent hand-off: one agent answers, the next receives the conversation so far as context[^pydantic-message-history-docs] Passing `model=` to the next run reuses the same history on another model, and provider-specific metadata degrades on the way — [citations](pydantic-ai-citations.md), for instance, arrive at a different provider as plain text while staying on the stored messages, and only Anthropic web search and OpenAI Responses web/file citations are replayed as citations at all[^pydantic-message-history-docs]

What a provider will take back is decided by two rules, because a response may hold material only its author can verify[^pydantic-message-history-docs] **Server-side state** — stored response, item, conversation and container IDs — is judged per endpoint: it is sent only to a provider with the same `provider_name` whose base URL matches the response's `provider_url` (URLs compared ignoring scheme and host case, a default port and a trailing `/`), and a hand-built response with no `provider_url` is judged by name alone. **Stateless signed or encrypted data** — OpenAI encrypted reasoning and compaction items, Anthropic thinking signatures and redacted thinking, Gemini thought signatures, xAI encrypted reasoning and tool results, OpenRouter and Snowflake reasoning details — is judged per *canonical system*: it goes back to a provider with the same `canonical_system`, or to one that lists it in `compatible_systems`. Anything unsendable falls back rather than failing: thinking is written out as text, a foreign OpenAI compaction item is dropped along with the history before it (so the model gets that history in full), and a Gemini function call gets the documented `skip_thought_signature_validator` signature.

| Provider | Canonical system |
| --- | --- |
| `openai`, `openai-codex`, the Gateway's OpenAI route | `openai` |
| `azure`, `OpenAIProvider` over an `AsyncAzureOpenAI` client | `azure` |
| `anthropic` over any client (Anthropic API, Bedrock, Claude Platform on AWS, Vertex AI, Foundry), Bedrock Converse with a Claude model, the Gateway's Anthropic route | `anthropic` |
| `bedrock` with any other model | `bedrock` |
| `google` / `google-cloud` over a Google Cloud client, the Gateway's Google route | `google-cloud` |
| `google` / `google-cloud` over a Gemini API client | `google` |
| Everything else, including `bedrock-mantle`, `openai-chatgpt`, `openrouter`, `snowflake` | its own name |

`ModelResponse.canonical_system` is recorded when it differs from `provider_name`, and always when it depends on the client — which is how a Gemini API response and a Google Cloud one, both named `google`, are told apart, since the two reject each other's thought signatures[^pydantic-message-history-docs] [Google models in Pydantic AI](google-models-in-pydantic-ai.md) carries that pair's substitution rule. The canonical system names the *service*, not the wire protocol: `azure` and OpenAI-speaking providers such as DeepSeek each have their own, and a renamed subclass keeps its parent's except under `OpenAIProvider`, whose subclasses are assumed to talk elsewhere. Code that decides by service rather than by provider name reads it too — the Harness `Advisor` uses it to tell whether an executor takes Anthropic or OpenRouter advisor model IDs.

Two predicates answer the question for a given part or response: `Model.accepts_stateless_artifacts()` and `Model.accepts_server_state()`, with `Provider.shares_server_state_with()` overridable when two URLs reach the same stored state, as a proxy alias does[^pydantic-message-history-docs] `UploadedFile` is deliberately outside these rules: it is sent to the endpoint of whichever model you pass it to, so pass it to one that can read it.

Some providers accept data they cannot use without failing: OpenAI ignores encrypted reasoning from another organization, and Claude models with account-bound thinking ignore thinking from another account[^pydantic-message-history-docs]

## Editing a history

Build new objects rather than mutating old ones: copy a message with `dataclasses.replace` and pass a new `parts` list of new or reused parts, or prune and rewrite through a [history processor](pydantic-ai-history-processors.md)[^pydantic-message-history-docs] Replacing a message in the list and reassigning its `parts` list are both stated as safe; in-place mutation of a part is what the framework's own documentation avoids.

## Limits

- Vendor documentation that names **no Pydantic AI version, author, publication date or licence**; every API name here is version-unknown, and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-message-history-docs]
- Nothing was installed, no agent run, no history serialized, no provider switched and no ID minted: every claim is **Reported**, none **Observed** or **Reproduced**.
- The guide states the round-trip properties of `ModelMessagesTypeAdapter` and of a stored `AgentRunResult` but enumerates neither the serialized schema nor its compatibility guarantees, so what happens when a stored history meets a changed message schema is unstated.
- `all_messages_json()` and `new_messages_json()` are named only; their encodings and size behaviour are not described.
- The `StepPersistence`, `ConversationSearch` and `Memory` rows come from a three-row summary table whose own pages were read as links, not followed, so their backends and scoping details beyond the table are unverified here; [persistence choices](pydantic-ai-persistence-choices.md) now maps the whole tier set and [conversation store](pydantic-ai-conversation-store.md) carries the append-only store mechanics.

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) for the delta parts a capability records, and on `prepare_messages` for rendering parts a provider cannot map.
- **Feeds** [history repair](pydantic-ai-history-repair.md), [untrusted-history sanitization](pydantic-ai-client-supplied-history.md) and [history processors](pydantic-ai-history-processors.md), each of which transforms the list this page defines.
- **Extends into** [conversation state](pydantic-ai-conversation-state.md): `Conversation` wraps messages, usage, the conversation id and deferred tool requests into one storable value.
- **Underpins** [mid-run injection](pydantic-ai-mid-run-injection.md), where `enqueue` appends to the same list during a run.
- **Constrains** [model fallback](pydantic-ai-model-fallback.md) and [models and providers](pydantic-ai-models-and-providers.md): the canonical system decides what a fallback candidate is sent back.
- **Carries citations selectively**, per the round-trip table in [Pydantic AI citations](pydantic-ai-citations.md): every citation object is stored, but only Anthropic web search and OpenAI Responses web/file citations (with message IDs sent) go back to the provider as citations, and an edited answer's `citations` and `provider_details['citations']` have to be cleared by hand.
- **Contrasts with** provider-held state in [OpenAI Responses API features](openai-responses-api-features.md) and [Anthropic server-side tools](anthropic-server-side-tools.md): `openai_conversation_id` and containers keep the conversation on the provider's side, while this page's history is the application's copy — and the vendor notes a provider chain still bills earlier input tokens and is unavailable under Zero Data Retention.

[^pydantic-message-history-docs]: Pydantic Docs, "Messages and chat history", <https://pydantic.dev/docs/ai/core-concepts/message-history/>, 15,322 words as declared and 15,615 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/core-concepts/message-history/index.md`, 1,477 lines, content digest sha256:1ce4fb2b. §"Accessing Messages from Results" (raw lines 13–141) for `all_messages`/`new_messages` and their JSON variants, the printed request and response fields, and the incomplete streamed list; §"Using Messages as Input for Further Agent Runs" (142–223) for `message_history=`, the no-new-system-prompt rule and `ReinjectSystemPrompt`; §"Which model answered" (646–649) for `model_id` versus `model_name`; §"Correlating runs with run_id and conversation_id" (585–645) for both identifiers, their inheritance rules, the `UserError` cases, the span attributes, the fork and the UI-adapter mapping; §"Storing and loading messages (to JSON)" (650–704), "Storing complete run results" (705–742) and "Carrying a conversation whole" (783–847) for the codec, the stored run result's preserved fields, `streamed.result`, the `Conversation` bundle, the `UserError` on mixed arguments, the store's `revision`/`new_message_index` and the three Harness rows; "Other ways of using messages" (861–948) for cross-model and cross-agent reuse and the citations degradation; "Sending history to another provider" (949–979) for the two judging rules, the canonical-system table, the fallbacks, `canonical_system`, the base-URL comparison, the two predicates, `UploadedFile` and the ignored-data cases; "Editing existing messages" (1015–1018) for immutable edits. Evidence class: **Reported** — vendor documentation; no package installed, no run made, no history serialized.
