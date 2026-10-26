---
type: Concept
title: "OpenRAG chat, streaming, and nudges"
description: "Agent prompt rules, distinct browser NDJSON and public SSE contracts, conversation identity, and nudge generation limits."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10ee3d0dedc842d244ec2b63fd9791
    title: OpenRAG repository
---

**Observed:** OpenRAG chat is Langflow-agent-driven, but its browser and public integration transports are different: the browser consumes newline-delimited JSON from `/langflow`, while `/v1/chat` transforms output into SSE. Both sit above ownership-aware conversation logic; payload fields and continuation IDs should not be copied interchangeably.[^openrag-repo]

## Agent behavior

The committed agent template enables streaming, up to 15 iterations, 100 history messages, calculator and current-date tools, and parsing-error handling. Its prompt separates retrieval, conversation history, uploaded context, URL ingestion, and general knowledge. It requires inline `(Source: <chunk_id>)` citations for sourced content and bans a trailing bibliography; for unsupported knowledge-base questions it prescribes a fixed no-support answer, while ordinary general knowledge can be uncited. These are **Observed prompt instructions**, not demonstrated model compliance or a guarantee every answer performs retrieval.[^openrag-repo]

Document chunks are explicitly untrusted data, with marker escaping in [retrieval](openrag-hybrid-retrieval.md). Template model descriptors are overridden by runtime configuration and are not a reliable statement of the selected deployed model.[^openrag-repo]

## Transport contracts

| Client | Wire format | Main request fields |
| --- | --- | --- |
| Browser `useChatStreaming` | NDJSON, trailing partial line retained | `prompt`, `previous_response_id`, `conversation_id`, filters, limit/threshold |
| Public `/v1/chat` | `text/event-stream` | `message`, `chat_id`, filters, `stream` |

Public SSE emits `content` with `delta`, `sources` with source records, and `done` with `chat_id`. There is no dedicated error-event type in the inspected transformer. **Synthesis:** clients should distinguish receiving `done` from an abruptly ended stream, rather than treating any EOF as successful completion.[^openrag-repo]

The browser has an initial-response timeout, per-chunk resets, cancellation, stream-generation guards against stale chunks, preservation of partial content, and several parser formats. A Granite-specific heuristic can infer a retrieval call from tool-shaped content; this is client compatibility behavior, not evidence that a genuine tool call occurred.[^openrag-repo]

## Conversation identity and interruption

**Reported by current documentation:** `conversation_id` is the sidebar thread, while `previous_response_id` continues a Langflow response/session and may change. Response aliases belong to a canonical conversation; deletion revokes aliases and attempts associated Langflow-session cleanup. New response IDs are disclosed only after durable ownership persistence (file, DB, or hybrid fallback); interrupted streams retain partial answers but do not automatically replay ingestion/tool calls.[^openrag-repo]

The public handlers perform ownership checks on continuation/deletion. However, the full internal streaming producer and durable-write failure paths were not audited in this ingest, so the stronger interruption guarantees above remain **Reported**, not reproduced.[^openrag-repo]

## Nudges

The nudge prompt asks for exactly three short English suggestions, about 40 characters each, newline-separated, history-preferred, and blank on error. The flow uses low temperature and disables streaming. **Unverified:** exact output count, usefulness, and latency were not measured.[^openrag-repo]

## Relationships

- Uses [Langflow workflows](openrag-langflow-workflows.md), [retrieval](openrag-hybrid-retrieval.md), and [security/ownership](openrag-auth-security.md).
- Consumed by the [frontend](openrag-frontend.md), [public API](openrag-public-api.md), and [SDKs](openrag-sdks.md).

## Coverage limits

No interrupted-stream, model, tool-routing, or citation-compliance test was executed. Internal chat producer and full ownership repository coverage remain pending; see [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d3ec10ee3d0dedc842d244ec2b63fd9791`: `flows/openrag_agent.json::Agent-Nfw7u` and system prompt; `flows/openrag_nudges.json::Prompt Template-Wo6kR`; `frontend/hooks/useChatStreaming.ts::{sendMessage,startTimeout}`; `frontend/lib/chat-stream-parsers.ts` parser functions and `detectImplicitToolCall`; `src/api/v1/chat.py::{chat_create_endpoint,chat_delete_endpoint,_transform_stream_to_sse}`; `src/services/chat_service.py::{langflow_chat,langflow_nudges_chat}`; `src/api/nudges.py`; `docs/docs/core-components/chat.mdx` §§ Interrupted chat responses, Nudges, Upload documents to the chat.
