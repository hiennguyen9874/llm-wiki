---
type: Concept
title: Pydantic AI Conversation state
description: Pydantic AI v2.55's Conversation object — serializable thread state that carries messages, running usage, a conversation id, and pending deferred tool requests across runs.
tags: [ml, pydantic-ai, agents, persistence]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:18:00Z }
stale_after: 2026-12-23
sources:
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
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
  - id: pydantic-persistence-docs
    resource: ../raw/core-concepts/persistence/index.md
    scope: ../raw/core-concepts/persistence/
    kind: documentation
    revision: sha256:32a52931f576332ecfef1bbaf12458296ffb58e5f850c656b73a8b264c1df051
    title: "Persistence"
---

`Conversation`, added in v2.55.0 on 2026-10-09, is Pydantic AI's serializable record of one chat thread: the messages, the running usage, a `conversation_id`, and any deferred tool requests the last run paused on. Every entry point accepts it as `conversation=`, and every result returns one as `result.conversation`[^dd-v2-tour-2026]

## Why store the object, not the messages

Continuing a thread from messages alone loses two things the object preserves[^dd-v2-tour-2026]:

| Lost with a bare message list | Preserved by `Conversation` |
| --- | --- |
| Usage budget continuity | `UsageLimits` covers the whole thread; each turn from messages restarts the budget at zero |
| Pending approvals | `deferred_tool_requests` records which unanswered tool calls still need approval |

The two losses are sharper than the table's wording. `usage` is the conversation's running total and includes `tool_calls`, which no message records, so continuing from messages alone restarts every turn's `UsageLimits` budget at zero[^pydantic-persistence-docs] And a run that paused for deferred tools leaves calls the messages show as unanswered without saying which need approval and which an external result, or what metadata they were deferred with — the conversation carries both[^pydantic-persistence-docs] Carrying usage changes nothing about tracing: each run's span still reports that run's own tokens, so a conversation's spend is the sum of its runs[^pydantic-persistence-docs]

What messages do carry is correlation: `run_id` and `conversation_id` are stamped onto each one, so a history reloaded from storage stays correlated in [Logfire](pydantic-ai-observability.md) with no bookkeeping of your own[^pydantic-persistence-docs]

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

## Storing it safely

A conversation id is a key, not a credential: check that the caller may access the conversation before you load it, and serialize concurrent updates to one conversation — a version column or a per-conversation lock — so two instances do not continue the same stored version[^pydantic-production-docs] The storage shape the vendor names is a `jsonb` column keyed by `conversation_id`, with `ConversationTypeAdapter` on either side of it[^pydantic-production-docs]

## What a round trip preserves — and what it normalizes

`ConversationTypeAdapter` round-trips with the same fidelity as the message history's own `ModelMessagesTypeAdapter`, including fields that are never sent to the model, such as a part's application-only `metadata`[^pydantic-persistence-docs] Because that field is typed `Any`, any value without a JSON form is normalized on the way through: a `tuple` reloads as a `list`, a `datetime` as its ISO string, and raw `bytes` as their base64 string[^pydantic-persistence-docs] The important compatibility claim is that no schema migration is needed when Pydantic AI adds a message part, because a conversation serialized by an older version still deserializes[^pydantic-persistence-docs] That closes the open migration question recorded under Limits on this page, for additions only.

## Rewrite the document, or append the turn

Rewriting the whole conversation on every turn keeps the code simple but makes each write as large as the conversation so far[^pydantic-persistence-docs] To keep writes proportional to the turn, store the messages in a table of their own, appending each run's `new_messages()` with `ModelMessagesTypeAdapter`, and keep the rest of the conversation beside them — its `usage`, its `conversation_id`, and its `deferred_tool_requests`, which a paused conversation cannot be resumed without — reassembling `Conversation(messages=..., usage=..., conversation_id=..., deferred_tool_requests=...)` to continue[^pydantic-persistence-docs] A [conversation store](pydantic-ai-conversation-store.md) does this for you, and adds the conflict check and branching that the manual split leaves to the caller.

## A history a chat UI sent you

A frontend on Vercel AI or AG-UI keeps a message list of its own, and the adapter serving it converts both ways without a request in hand: `load_messages` turns the protocol's messages into `ModelMessage`s and `dump_messages` turns them back[^pydantic-persistence-docs] The rule that follows is to store the Pydantic AI side and convert at the edge, rather than storing the protocol's shape: the wire formats have no place for everything a history carries, and the fields they drop are the ones the next model request needs[^pydantic-persistence-docs]

## Storage is not durability

The source quotes the persistence docs' warning that reaching for a durable engine merely to store a chat thread is the common mistake, and that a `jsonb` column keyed by `conversation_id` is enough. Durable execution solves a different problem: keeping a single run alive through crashes. When saved checkpoints that can be resumed or forked are the goal, Harness `StepPersistence` writes the save and load code instead[^dd-v2-tour-2026] See [Pydantic AI durable execution](pydantic-ai-durable-execution.md) for the engine tier.

`StepPersistence` complements this object rather than replacing it. It adds message-history snapshots at each settled tool-call boundary, to continue or fork a run from, plus a tool-effect ledger recording whether each tool call started, returned or raised — a call that never finished has an unknown outcome, so the external system has to be checked before it runs again[^pydantic-production-docs] Snapshots hold messages only, not the usage and pending deferred calls a `Conversation` carries, so both are stored[^pydantic-production-docs]

## Limits

- The serialization API was exercised only against `TestModel`, with a `dict` standing in for a database column; no real database, schema migration, or concurrent-writer behaviour was tested[^dd-v2-tour-2026]
- The storage discipline — the id as an access key, serialized concurrent updates, the `jsonb` column and the message-only limit of a `StepPersistence` snapshot — is the vendor's prose in its production page. No version column, lock or checkpoint was written here, and the page gives no schema or migration guidance for either store[^pydantic-production-docs]
- No guidance is given for versioning or migrating stored conversations when a message *part* is added — the persistence guide states that an older serialized conversation still deserializes and that no schema migration is needed for an addition[^pydantic-persistence-docs] — but nothing is said about a part being removed or its shape changed, so a breaking change to a stored thread remains an open compatibility question.
- The round-trip and write-size rules are the vendor's prose in its persistence guide; no conversation was serialized, no `metadata` value was normalized in transit here, and no table split was implemented[^pydantic-persistence-docs]
- Evidence class: **Reported** — the article states it executed this example; this ingest ran nothing and inspected no Pydantic AI package.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md) indirectly: capabilities attached to the agent shape what a run records.
- **Carries** the state needed to resume [deferred tool approvals](pydantic-ai-deferred-approvals.md).
- **Must be stored rather than reconstructed** for a paused run: [Pydantic AI deferred tools](pydantic-ai-deferred-tools.md) records that history shows which calls are unanswered but not which kind each one is or what metadata the tool attached, which is why `deferred_tool_requests` travels on the conversation and a resumed `build_results()` is validated against it.
- **Carries** the loaded set of [on-demand capabilities](pydantic-ai-on-demand-capabilities.md): the capability ids and revealed tool names are reconstructed from the recorded load exchange or `CapabilityLoadDeltaPart` and `ToolAvailabilityDeltaPart`, so a resumed conversation does not rediscover them.
- **Contrasts with** [durable execution](pydantic-ai-durable-execution.md): a conversation survives between runs, a durable engine survives inside one run.
- **Is stored alongside** [Pydantic AI production readiness](pydantic-ai-production-readiness.md), whose checkpointer split separates the stored conversation from the engine journal and from `StepPersistence` snapshots.
- **Contrasts with** OpenAI's provider-side thread in [OpenAI Responses API features](openai-responses-api-features.md): `openai_conversation_id` keeps the conversation at OpenAI and cannot be rewritten from the client, while `Conversation` is an object the application owns and persists[^pydantic-openai-2026].
- **Stops short of** [realtime voice sessions](pydantic-ai-realtime-voice.md), which hand a call to a text run at the `all_messages()` / `message_history=` level rather than as a `Conversation` — and whose seeding path skips history processors, so filtering or redaction has to happen before the session opens.
- **Is generalized by** [self-improving agent loops](self-improving-agent-loops.md), whose conversation search reads a shared store across sessions and agents rather than one saved thread.
- **Carries the work of** [file understanding](pydantic-ai-file-understanding.md) when history stays server-side: the recorded file description lives in request metadata inside the persisted messages, so a stored conversation is described once rather than once per turn.
- **Persists the parts described in** [multimodal input](pydantic-ai-multimodal-input.md) and [structured content](pydantic-ai-structured-content.md), including a structured item's value beside its frozen rendering.
- **Wraps** the list defined in [message history](pydantic-ai-message-history.md): `Conversation` adds usage, the conversation id and deferred tool requests to messages that `ModelMessagesTypeAdapter` can round-trip on their own — and it needs the same [client-history sanitization](pydantic-ai-client-supplied-history.md) when it arrives from a client.
- **Is stored through** a [conversation store](pydantic-ai-conversation-store.md) when each message should be written once and conflicting saves caught: the store's `revision` check is the conflict discipline this page leaves to a version column or a lock.
- **Is one of five places state can live**, per [persistence choices](pydantic-ai-persistence-choices.md): the row for a saved chat thread, distinct from `StepPersistence`, `Memory`, durable execution and a provider-held thread.
- **Round-trips through** the codec described in [message history](pydantic-ai-message-history.md), with the same fidelity and the same JSON-normalization edges for application-only metadata.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Example 3: store a conversation, not a pile of messages (v2.55)" (raw lines 214–248) for the `Conversation` contents, the usage-budget and `deferred_tool_requests` rationale, the JSON round-trip sample, and the printed `True 2`; §"Human approval without holding a process open" for deferred requests. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — the author reports type-checking against 2.57.0 and running against `TestModel`; no provider call, package, or database was touched in this ingest.

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. §"How do I keep conversation state?" (raw lines 183–187) for the `Conversation` contents, the `jsonb` column keyed by `conversation_id`, the key-versus-credential rule and the version-column or lock requirement; §"What happens when the process crashes mid-run?" and "What you get compared to a checkpointer" (lines 126–142) for the `StepPersistence` snapshots, the tool-effect ledger, the unknown outcome of an unfinished call, and the messages-only limit of a snapshot. Evidence class: **Reported** — vendor documentation; no store, lock or checkpoint was written.

[^pydantic-persistence-docs]: Pydantic Docs, "Persistence", <https://pydantic.dev/docs/ai/core-concepts/persistence/>, 2,451 words as declared and 2,500 by local `wc -w`, 160 lines, `domain: pydantic.dev`, `language: en`, no publication date, author, licence or Pydantic AI version; local capture `raw/core-concepts/persistence/index.md`, content digest sha256:32a52931. §"Why a conversation rather than its messages" (raw lines 85–91) for the `tool_calls` that no message records, the per-run span accounting, the deferred-call metadata, and the `run_id`/`conversation_id` correlation; §"Storing a conversation yourself" (29–59) for the `ConversationTypeAdapter` round-trip fidelity, the `Any`-typed `metadata` normalization, the additive-change rule, and the per-turn append with `new_messages()` plus reassembly; §"Storing a history a chat UI sent you" (61–83) for `load_messages`/`dump_messages` and the store-the-Pydantic-AI-side rule. Evidence class: **Reported** — vendor documentation; nothing was serialized, normalized or stored.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Using durable conversations" (raw lines 424–464) for `openai_conversation_id`, `provider_details['conversation_id']`, and the rule that OpenAI keeps the conversation so client-side changes to earlier messages never reach the model. Evidence class: **Reported** — vendor documentation; no conversation was created or continued here.
