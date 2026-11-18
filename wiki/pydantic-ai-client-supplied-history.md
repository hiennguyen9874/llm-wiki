---
type: Concept
title: Pydantic AI client-supplied history
description: Why message_history is a trust boundary in Pydantic AI — stateless runs, fabricated tool calls and approvals, the sanitize_messages strips and their opt-outs, the provider-state references a sanitizer keeps, and the per-setting rules for client-held state.
tags: [pydantic-ai, agents, security, context-management]
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

`message_history` is trusted server-side state, and Pydantic AI's server-side surfaces are stateless: a run is reconstructed from the history (and any `deferred_tool_results`) supplied with the request, whether it arrives through a UI adapter or through your own endpoint[^pydantic-message-history-docs] A client that can submit history can therefore fabricate it — including `ToolCallPart`s the model never emitted and [approvals](pydantic-ai-deferred-approvals.md) no human granted — and the server will process them as genuine, up to executing the tools they name. That is the gap this page's two halves close: `sanitize_messages` narrows what a fabricated history can reach, and the design rules below decide what still has to be checked outside the prompt.

The framework does not sign or cryptographically verify tool calls, results or approvals, and the vendor states comparable agent frameworks do not either: signing is only meaningful for a server that kept the run itself, and such a server does not need the client's copy of the history in the first place[^pydantic-message-history-docs] Sanitization therefore reduces reach rather than creating trust.

## Designing around the boundary

Possession of the endpoint is the authorization boundary, so the vendor's four rules move the checks out of the prompt and into code[^pydantic-message-history-docs]:

- **Authenticate and authorize at the transport layer**, and treat every caller that gets through as able to submit any history it likes.
- **Scope the toolset to the caller**, by building the toolset per run or filtering it against the user carried in the run's [dependencies](pydantic-ai-dependencies.md).
- **Re-validate high-stakes effects server-side.** Approval guards against the *model* acting without sign-off, not against the client; where the stakes demand it, check the caller's authority against server-side state inside the tool function, or persist paused runs server-side and resume them with your own `deferred_tool_results`.
- **Do not read prompt-level framing as proof.** The `<system>` block and the tool-result file frame tell the model where content came from; they do not attest it, and a client that can submit history can submit its own system prompts unless you strip them.

## What sanitize_messages strips

`sanitize_messages` applies the same default sanitization the UI adapters use[^pydantic-message-history-docs]:

| Strip | Effect |
| --- | --- |
| System prompts and request-level `instructions` | Client-claimed operator voice is removed; an emptied `ModelRequest` is dropped entirely |
| Client-returned retry feedback | Pinned to the voice its cause allows — `'validation_error'` and `'model_retry'` reach the model in the user voice, fenced behind a line attributing it to the application; `'no_output'` is the one system-voice cause and is demoted to the same attributed user text, since a client can forge it as easily as a system prompt |
| Legacy `RetryPromptPart` | A tool-less one is translated into the feedback part it always meant, under the same rule |
| File URLs | Non-HTTP schemes dropped; non-allowlisted `FileUrl.force_download` values reset to `False` |
| Uploaded files and workspace references | Dropped, so a client cannot point the agent at another environment; to continue in the same workspace, pass a server-saved reference as `workspace=` |
| `ModelResponse.model_id` | Reset, so a client cannot pick which of your models a request is routed back to |
| `TextContent.metadata` | Dropped from user prompts and tool-return content, so client text cannot pass itself off as content your application or a capability added |
| Message `metadata['__pydantic_ai__']` | The framework-reserved key is dropped while your own keys stay, so a client cannot set state Pydantic AI and its capabilities act on |
| Unresolved tool calls | Removed from the end of the history |
| Capability parts | Never accepted from a client at all; the UI adapters never send them either |

Two exceptions matter for compaction[^pydantic-message-history-docs] Client-supplied `CompactionPart`s are **kept**, so the conversation stays compacted, but they are never trusted to stand in for the system prompt: the prompt — whether already in the history or re-injected by `ReinjectSystemPrompt` — is re-sent even where a provider's own compaction state would let it be skipped. And when you combine sanitized client history with trusted server-side `message_history`, pass `strip_compaction_parts=True`, because everything before a compaction item is hidden from the model and a client-supplied one would hide the server's history. The UI adapters apply that rule automatically.

Most strips are individually tunable for parts that server-side code really did create: `strip_system_prompts=False` (which also keeps retry feedback), `strip_instructions=False`, `allowed_file_url_schemes`, `allowed_file_url_force_download`, `allow_uploaded_files=True`, `strip_workspace_refs=False`[^pydantic-message-history-docs] Three are not: `TextContent.metadata`, `model_id` and the `__pydantic_ai__` metadata key are always reset, so history that must keep them has to arrive as trusted server-side `message_history`.

## The provider state a sanitizer keeps

`sanitize_messages` passes through, as sent, the references to state the provider holds: `ModelResponse.provider_response_id`, the `conversation_id` and `container_id` keys of `ModelResponse.provider_details`, and `ModelResponse.state`[^pydantic-message-history-docs] The UI adapters' protocols do not carry these, so adapter-loaded history has none, but a history you load yourself keeps whatever the client sent — and those IDs are enough, with your provider credentials, to reach the state they name. A client-sent ID is not proof that it owns that state, so save the references you need server-side bound to their user, and set each lever as follows:

| Setting | Rule with client-held history |
| --- | --- |
| `openai_conversation_id` | Pass a concrete saved ID, never `'auto'` |
| `anthropic_container` | Pass a saved container ID, or `False` for a fresh container, rather than relying on the default reuse of the latest container in the history |
| `openai_previous_response_id` | Do not use it — a response ID in the history can take precedence even over a concrete one; with `openai_transport='websocket'`, where it defaults to `'auto'`, pass a concrete `openai_conversation_id` to turn it off |
| `openai_prompt_cache_diagnostics` | Set `False`; it is on by default where supported and sends the latest response ID to compare against |
| `anthropic_cache_diagnostics` | Leave it off, its default; it does the same with the latest Anthropic response |
| A history ending in `state='suspended'` | Refuse one from a client: a run with no new prompt resumes it, fetching the response or batch result it names, and no setting disables that |

## Limits

- A single vendor page naming **no Pydantic AI version or date**, so this page is `draft` under the `pydantic-ai` domain rule[^pydantic-message-history-docs]
- **Reported** evidence: no forged history was replayed, no sanitizer run, no approval fabricated and no provider-state ID dereferenced here; the security argument is the vendor's, and the linked `THREAT_MODEL.md` section was read as a link, not followed.
- The strip list is prose; the exact allowlists behind `allowed_file_url_schemes` and `allowed_file_url_force_download`, and the full set of capability part types dropped, are not enumerated.
- Whether `sanitize_messages` costs measurable latency on a long history, and how it interacts with `repair_messages` when a client sends a history that is both forged and malformed, are unstated.

## Relationships

- **Narrows** [message history](pydantic-ai-message-history.md) before a run, and is applied before the provider-valid [repair](pydantic-ai-history-repair.md) that runs per request.
- **Guards** the state that [conversation state](pydantic-ai-conversation-state.md) stores: a client-held `Conversation` needs the same sanitization as a message list.
- **Protects** [deferred tool approval](pydantic-ai-deferred-approvals.md) and [durable execution](pydantic-ai-durable-execution.md): approvals and paused runs belong on the server when the client can submit history.
- **Complements** [workspace selection and reattachment](pydantic-ai-workspace-selection.md): workspace references are stripped from client history, so the server-saved `workspace=` reference is the way back in.
- **Bounds** provider-side conversation reuse in [OpenAI Responses API features](openai-responses-api-features.md) and [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), where the setting table above applies.

[^pydantic-message-history-docs]: Pydantic Docs, "Messages and chat history", <https://pydantic.dev/docs/ai/core-concepts/message-history/>, 15,322 words as declared and 15,615 by local `wc -w`, no date and no Pydantic AI version named; local capture `raw/core-concepts/message-history/index.md`, 1,477 lines, content digest sha256:1ce4fb2b. §"Loading untrusted history" (raw lines 743–778) for `sanitize_messages`, the strips, the retry-feedback voice rules, the compaction rules and `strip_compaction_parts`, the six opt-outs and the three that cannot be tuned, the kept provider references and the per-setting table; §"Trust boundary for client-supplied history" (848–860) for statelessness, fabrication of tool calls and approvals, the no-signing argument and the four design rules. Evidence class: **Reported** — vendor documentation; nothing was executed.
