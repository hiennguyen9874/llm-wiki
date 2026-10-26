---
type: Concept
title: Pydantic AI Conversation state
description: Pydantic AI v2.55's Conversation object — serializable thread state that carries messages, running usage, a conversation id, and pending deferred tool requests across runs.
tags: [ml, pydantic-ai, agents, persistence]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T05:12:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

`Conversation`, added in v2.55.0 on 2026-10-09, is Pydantic AI's serializable record of one chat thread: the messages, the running usage, a `conversation_id`, and any deferred tool requests the last run paused on. Every entry point accepts it as `conversation=`, and every result returns one as `result.conversation`[^dd-v2-tour-2026]

## Why store the object, not the messages

Continuing a thread from messages alone loses two things the object preserves[^dd-v2-tour-2026]:

| Lost with a bare message list | Preserved by `Conversation` |
| --- | --- |
| Usage budget continuity | `UsageLimits` covers the whole thread; each turn from messages restarts the budget at zero |
| Pending approvals | `deferred_tool_requests` records which unanswered tool calls still need approval |

The article's round-trip example stores the object as JSON and continues from it:

```python
conversation = (
    ConversationTypeAdapter.validate_json(db[conversation_id]) if conversation_id else None
)
result = agent.run_sync(
    prompt,
    conversation=conversation,
    usage_limits=UsageLimits(request_limit=20),  # budget for the whole thread
)
db[result.conversation_id] = ConversationTypeAdapter.dump_json(result.conversation)
```

Run against `TestModel` over two turns, the example printed `True 2`: the `conversation_id` survived the JSON round trip and usage counted two requests across two separate runs[^dd-v2-tour-2026]

## Storage is not durability

The source quotes the persistence docs' warning that reaching for a durable engine merely to store a chat thread is the common mistake, and that a `jsonb` column keyed by `conversation_id` is enough. Durable execution solves a different problem: keeping a single run alive through crashes. When saved checkpoints that can be resumed or forked are the goal, Harness `StepPersistence` writes the save and load code instead[^dd-v2-tour-2026] See [Pydantic AI durable execution](pydantic-ai-durable-execution.md) for the engine tier.

## Limits

- The serialization API was exercised only against `TestModel`, with a `dict` standing in for a database column; no real database, schema migration, or concurrent-writer behaviour was tested[^dd-v2-tour-2026]
- No guidance is given for versioning or migrating stored conversations when the message schema changes, so long-lived stored threads are an open compatibility question.
- Evidence class: **Reported** — the article states it executed this example; this ingest ran nothing and inspected no Pydantic AI package.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md) indirectly: capabilities attached to the agent shape what a run records.
- **Carries** the state needed to resume [deferred tool approvals](pydantic-ai-deferred-approvals.md).
- **Contrasts with** [durable execution](pydantic-ai-durable-execution.md): a conversation survives between runs, a durable engine survives inside one run.
- **Stops short of** [realtime voice sessions](pydantic-ai-realtime-voice.md), which hand a call to a text run at the `all_messages()` / `message_history=` level rather than as a `Conversation`.
- **Is generalized by** [self-improving agent loops](self-improving-agent-loops.md), whose conversation search reads a shared store across sessions and agents rather than one saved thread.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Example 3: store a conversation, not a pile of messages (v2.55)" (raw lines 214–248) for the `Conversation` contents, the usage-budget and `deferred_tool_requests` rationale, the JSON round-trip sample, and the printed `True 2`; §"Human approval without holding a process open" for deferred requests. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — the author reports type-checking against 2.57.0 and running against `TestModel`; no provider call, package, or database was touched in this ingest.
