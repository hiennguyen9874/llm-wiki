---
type: Concept
title: Pydantic AI conversation store
description: How a Pydantic AI ConversationStore keeps a thread as an append-only log — load and save around a run, revision conflicts, scope as ownership, branch versus fork, entry ids, the failed run that can still be stored, and the five primitives a database backend implements.
tags: [pydantic-ai, agents, persistence]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:15:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-persistence-docs
    resource: ../raw/core-concepts/persistence/index.md
    scope: ../raw/core-concepts/persistence/
    kind: documentation
    revision: sha256:32a52931f576332ecfef1bbaf12458296ffb58e5f850c656b73a8b264c1df051
    title: "Persistence"
---

A `ConversationStore` keeps conversations for you as a log in which each message is stored once: saving a continued conversation appends only its new messages, and a `fork` shares the history it keeps instead of copying it[^pydantic-persistence-docs] That is the whole difference from storing a `Conversation` by hand — the same bytes in your database, with append-only writes, conflict detection, ownership scoping and branching moved out of your request handler[^pydantic-persistence-docs]

## Load, run, save

`load` and `save` bracket each run, and a missing conversation is created rather than looked up:

```python
conversation = await store.load(conversation_id) or Conversation(conversation_id=conversation_id)
result = await agent.run(prompt, conversation=conversation)
await store.save(result)
```

`save` accepts a run's result or a `Conversation`, and advances the conversation's revision, so `result.conversation` can be continued or saved again afterwards[^pydantic-persistence-docs]

## Every save is checked against a revision

`load` records a `revision` on the conversation, a run carries it through to its result, and `save` checks it before writing[^pydantic-persistence-docs] If someone else saved the conversation in between, or a new conversation reuses a stored conversation's ID, `save` raises `ConversationConflict` instead of overwriting it, and the caller loads again and retries[^pydantic-persistence-docs] This is the compare-and-swap that [conversation state](pydantic-ai-conversation-state.md) has to hand-roll as a version column or a per-conversation lock when it manages the column itself.

## Scope is the ownership boundary

`save(..., scope=...)` records whose conversation it is, such as a user ID, and `list_conversations` reads by that scope, most recently saved first, with `limit=` for the newest few[^pydantic-persistence-docs] Passing the same `scope=` to `load` and the other methods that read or change a conversation keeps it to its owner: a conversation saved under another scope is treated as one the store does not have, so a guessed `conversation_id` does not reach it[^pydantic-persistence-docs] The ID is therefore an address and the scope is the access check, which is the same conclusion [client-supplied history](pydantic-ai-client-supplied-history.md) reaches from the untrusted-input side.

## The stored conversation only grows

`load` records where the stored messages end as the conversation's `new_message_index`, and a run carries it to its result, so `save` appends just the messages the run added[^pydantic-persistence-docs] The rule survives history rewriting: when a capability trims or rewrites what a run is sent — `ProcessHistory` keeping the last few turns, for instance — the model sees the trimmed history and the store keeps the whole one[^pydantic-persistence-docs] A run that only needs recent context is served from the same store with `load(conversation_id, limit=20)`, which loads the last 20 messages, and saving that result still appends to the whole conversation[^pydantic-persistence-docs] A message appended to a loaded conversation before the run, such as the user's new turn, is saved together with what the run added[^pydantic-persistence-docs]

## Branch to edit, fork to explore

To regenerate a reply or edit an earlier turn, `branch` the conversation from the message before it and then run and save as usual, so the new turn goes onto the branch[^pydantic-persistence-docs] The history it left stays stored and is listed in the record's `branches`, so the conversation can branch back to it with `from_entry=`[^pydantic-persistence-docs] To explore from a point without moving the conversation — several approaches side by side — `fork` a new conversation from it for each, sharing the history rather than copying it[^pydantic-persistence-docs]

## Entries are the unit to bill or rate

Each stored message is a `ConversationEntry` with an `id` of its own, which is what a rating or a billing row is tied to; `save` returns the entries it stored and `load_entries` loads a conversation's history together with them[^pydantic-persistence-docs] This is the granularity the conversation object itself does not expose — a `Conversation` is a whole thread with a single revision, while the store addresses individual messages.

## Backends

`InMemoryConversationStore` is for tests and examples[^pydantic-persistence-docs] For a real database, `ConversationStore` is subclassed: it implements loading, saving and forking on five storage primitives, so a backend only reads and writes records and entries[^pydantic-persistence-docs] The five primitives are named but not enumerated here or in the source, so the size of the surface a backend must implement is an open question (see Limits).

## A failed run can still be stored

A run that fails can be stored so the user sees what it did before it stopped[^pydantic-persistence-docs] `AgentRunError` — `UsageLimitExceeded`, a model API error — carries the conversation as far as it got as `error.conversation`, including a response cut short with `state='interrupted'`, so `store.save(error.conversation)` appends the failed turn[^pydantic-persistence-docs] The attribute is set once the error leaves the `run`, `iter` or `run_stream` call or block, so the catch has to sit outside the `async with`[^pydantic-persistence-docs]

Two escapes exist for everything else. An arbitrary exception, including one a tool's own code raises and the `FallbackExceptionGroup` raised when every fallback model fails, is captured by wrapping the run in `capture_run_conversation`[^pydantic-persistence-docs] And under [Temporal](pydantic-ai-temporal.md) the error a client receives keeps only the error's type and message, without its `conversation`, so the error is caught inside the workflow and `error.conversation` is saved through an activity, as a successful run's would be[^pydantic-persistence-docs]

## UI adapters can drive it

Passing a store as `conversation_store` to a UI adapter makes the adapter load and save each chat request's conversation through it[^pydantic-persistence-docs] One error contract comes with that: a `UserError` the store raises is sent to the client as-is, so queries, hostnames and credentials must be kept out of its message, while any other exception is warned on the server and answered with a generic message[^pydantic-persistence-docs] The adapter also has a conversion half, `load_messages` and `dump_messages`, which is covered on [conversation state](pydantic-ai-conversation-state.md).

## Limits

- Vendor documentation naming no Pydantic AI version, date, author or licence, so the page is `draft` under the `pydantic-ai` domain rule and every API name is version-unknown[^pydantic-persistence-docs]
- Nothing was installed, no store created, no conversation loaded, saved, branched, forked or listed, and no failed run stored: every claim is **Reported**, none **Observed** or **Reproduced**.
- The five storage primitives are not enumerated, and neither `ConversationStore`'s method signatures, the `ConversationRecord`/`ConversationEntry` schemas, the `ConversationConflict` payload, nor what `branch` takes beyond the message entry are given — the named API pages were read as links in the source, not followed.
- No retention, deletion, compaction or size policy is stated for a store that only ever grows, which is a real cost for a long-lived support thread.
- `scope=` is called ownership, not authorization: the guide states that a mismatched scope hides a conversation, not that a store enforces tenant separation anywhere else, and the traversal rules for `list_conversations` across scopes are unstated.
- The vendor's own production page separately asks for serialized updates to one conversation; whether a store's revision check alone satisfies that under two concurrent writers is not stated[^pydantic-persistence-docs]

## Relationships

- **Stores** the object owned by [Pydantic AI conversation state](pydantic-ai-conversation-state.md), whose `revision` and `new_message_index` fields are what make append-only saves and conflict detection possible.
- **Replaces the hand-rolled column** described there for a thread that needs each message written once: the same `jsonb`-shaped decision, with the log, conflict and branch logic supplied.
- **Wraps** the message list of [message history](pydantic-ai-message-history.md), appending a run's `new_messages()` rather than rewriting the thread.
- **Depends on** the trimming behaviour of [history processors](pydantic-ai-history-processors.md): the store keeps what the model no longer sees, so a processor's rewrite is not a deletion.
- **Holds** the paused state described in [deferred tools](pydantic-ai-deferred-tools.md) when the last run left `deferred_tool_requests`, which a resumed conversation cannot be rebuilt without.
- **Keeps** the per-run record that [durable execution](pydantic-ai-durable-execution.md) does not: a stored conversation survives between runs, while the engine journal survives inside one.
- **Complements** `capture_run_conversation` and the Temporal activity rule, which are the two ways a failed run's conversation reaches the store.

[^pydantic-persistence-docs]: Pydantic Docs, "Persistence", <https://pydantic.dev/docs/ai/core-concepts/persistence/>, 2,451 words as declared and 2,500 by local `wc -w`, 160 lines, `domain: pydantic.dev`, `language: en`, no publication date, author, licence or Pydantic AI version; local capture `raw/core-concepts/persistence/index.md`, content digest sha256:32a52931. §"Using a conversation store" (raw lines 93–132) for the log semantics, the `load`/`save` sample, `ConversationConflict` and revisions, `AgentRunError.conversation` and `state='interrupted'`, `capture_run_conversation`, the Temporal caveat, `scope=`/`list_conversations`, `new_message_index` and trimming, `limit=20`, `branch`/`branches`/`from_entry=`, `fork`, `ConversationEntry` ids, `load_entries`, `InMemoryConversationStore`, the five storage primitives, and the UI-adapter `UserError` rule; §"Starting here" (lines 15–17) for the "each message stored once, conflicting saves caught, forking built in" row that scopes the store to your own database. Evidence class: **Reported** — vendor documentation; no store, revision, branch, fork or conflict was exercised.
