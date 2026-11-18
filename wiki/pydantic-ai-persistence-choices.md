---
type: Concept
title: Pydantic AI persistence choices
description: The five places a Pydantic AI agent's state can live — a stored Conversation, a ConversationStore, StepPersistence, Memory, durable execution, or a provider's own thread — which question each one answers, and why holding a chat thread does not need a durable engine.
tags: [pydantic-ai, agents, persistence]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:10:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-persistence-docs
    resource: ../raw/core-concepts/persistence/index.md
    scope: ../raw/core-concepts/persistence/
    kind: documentation
    revision: sha256:32a52931f576332ecfef1bbaf12458296ffb58e5f850c656b73a8b264c1df051
    title: "Persistence"
---

"Persistence", "memory" and "sessions" are three names for problems that a Pydantic AI deployment has to keep apart, because each one has a different answer and a different lifetime[^pydantic-persistence-docs] The vendor's entry point is a five-row table of *what you want* against *what you use* and *where it lives*, and the useful unit of knowledge is that mapping rather than any one mechanism[^pydantic-persistence-docs]

| You want to… | Use | Where it lives |
| --- | --- | --- |
| Save a conversation and pick it up later — a chat thread, a support ticket, an assistant that remembers yesterday | Store its `Conversation` in a column of your own database | Core |
| The same, with each message stored once, conflicting saves caught, and forking built in | A `ConversationStore` on your own database | Core |
| A log of what each run did, a ledger of its tool side effects, and snapshots to recover a run from | `StepPersistence` (not for storing sessions) | Pydantic AI Harness |
| The agent to remember what it learned about someone *across* conversations | `Memory` | Pydantic AI Harness |
| A run to survive the process dying mid-tool-call, replaying completed steps and retrying the one in flight | Durable execution | Core |

## Storing the history is the whole of intra-thread memory

For most of what people mean by "giving the agent memory", the first two rows are the answer: an agent's memory of the conversation it is having *is* its message history, and there is no separate memory system to add — storing the history and passing it back is the mechanism[^pydantic-persistence-docs] Memory becomes its own thing only once it has to outlive the thread, which is the `Memory` row and a different key[^pydantic-persistence-docs] The mechanics of the object being stored are on [Pydantic AI conversation state](pydantic-ai-conversation-state.md), and the log-shaped store on [Pydantic AI conversation store](pydantic-ai-conversation-store.md).

## The rows compose rather than compete

A durable engine keeps one run alive, `StepPersistence` records what each run did, a stored conversation is what you hand to the next run, and `Memory` is what is left when the thread is over[^pydantic-persistence-docs] That composition is what makes the choice legible: they sit at different layers of the same deployment and usually co-exist.

The common mistake the vendor names is reaching for a durable engine because you wanted to store a chat thread — a `jsonb` column is enough for that[^pydantic-persistence-docs] The split behind the warning is that a run's survival *inside* one execution is [durable execution](pydantic-ai-durable-execution.md)'s problem, while a thread's survival *between* executions is a row in your database.

## Checkpoints stop at settled tool-call boundaries

`StepPersistence` saves a message-history snapshot at each settled tool-call boundary of a run, so the run can be continued later or forked from a saved snapshot; to resume a run that crashed partway *through* a step, the answer is durable execution rather than a snapshot[^pydantic-persistence-docs] The guide states the resulting gap plainly: nothing it describes snapshots state in the middle of a step, so there is no "rewind to step 4 of a half-finished run and replay from there" inside a single run — snapshots are taken at settled tool-call boundaries, not mid-node[^pydantic-persistence-docs]

`StepPersistence` also remains supported while no longer being the way to store a session: it is for recovering runs, its snapshots hold messages only (not the usage and pending deferred tool requests a `Conversation` carries), and a documented move copies sessions stored with it into a `ConversationStore`[^pydantic-persistence-docs] What it adds instead is an append-only event log of what the agent did at each boundary, continuable snapshots, and a tool-effect ledger recording whether each call started, returned or raised — after a crash, a call that never finished has an unknown outcome and one that raised may still have had its effect, so the external system is checked before the call runs again[^pydantic-persistence-docs] `ConversationSearch` builds on that store without writing anything of its own, ranking the history `StepPersistence` already wrote and letting the model pull earlier turns back into context, including turns compaction dropped[^pydantic-persistence-docs]

## A provider can hold the thread instead

One row is not in the table: some providers keep conversation state on their side and reconstruct earlier turns, so each request carries only what is new — on the OpenAI Responses API that is `openai_conversation_id`[^pydantic-persistence-docs] It is weighed against a store of your own on three counts the guide states outright: it is one provider's feature, OpenAI documents that earlier input tokens in a chain are still billed, and it is unavailable to organizations with Zero Data Retention enabled[^pydantic-persistence-docs] The provider-side mechanics and their asymmetry with a client-owned thread are on [OpenAI Responses API features](openai-responses-api-features.md).

## Limits

- Vendor documentation naming no Pydantic AI or Harness version, date, author or licence, so the page is `draft` under the `pydantic-ai` domain rule and every API name in the table is version-unknown[^pydantic-persistence-docs]
- Nothing was installed, no conversation stored, no snapshot taken, no engine replayed and no memory notebook written: every claim is **Reported**.
- The `StepPersistence`, `Memory`, `ConversationSearch` and durable-execution pages this guide links to were read as links, not followed, so their backends, configuration and concurrency boundaries are only as deep as this page states them; the compiled detail lives on [durable execution](pydantic-ai-durable-execution.md), [Harness memory](pydantic-ai-harness-memory.md) and [conversation store](pydantic-ai-conversation-store.md).
- "A `jsonb` column is enough" is a sizing judgement about one thread with no message count, byte size, retention period or concurrent-writer measurement behind it, and the guide gives no retention or deletion policy for any tier.
- The table's `ConversationStore` row says "on your own database" while its own sample uses `InMemoryConversationStore`, which the store section reserves for tests and examples — the row is the intended production shape, not the sampled one[^pydantic-persistence-docs]

## Relationships

- **Depends on** [Pydantic AI conversation state](pydantic-ai-conversation-state.md) for the `Conversation` object the first two rows store, and on [message history](pydantic-ai-message-history.md) for the list it wraps.
- **Separates** [durable execution](pydantic-ai-durable-execution.md) — a run surviving its process — from session storage, which is what the "common mistake" warning is about.
- **Places** [Harness memory](pydantic-ai-harness-memory.md) as the only row keyed by something other than the conversation, which is why it outlives the thread.
- **Places** the [Pydantic AI Harness](pydantic-ai-harness.md) at the run-record tier rather than the session-store tier.
- **Contrasts** a provider-held thread in [OpenAI Responses API features](openai-responses-api-features.md) with every client-side row: the provider's copy cannot be rewritten from the client and bills earlier input tokens again.

[^pydantic-persistence-docs]: Pydantic Docs, "Persistence", <https://pydantic.dev/docs/ai/core-concepts/persistence/>, 2,451 words as declared and 2,500 by local `wc -w`, 160 lines, `domain: pydantic.dev`, `language: en`, no publication date, author, licence or Pydantic AI version; local capture `raw/core-concepts/persistence/index.md`, content digest sha256:32a52931. §"Start here" decision table (lines 13–27) for the five rows, their where-it-lives column, the checkpoint paragraph, the memory-is-message-history rule, the composition, and the durable-engine mistake; §"Recording what each run did" (134–140) for `StepPersistence` remaining supported but not for sessions, the messages-only snapshot limit, the move to a `ConversationStore`, the event log, tool-effect ledger and unknown-outcome rule, and `ConversationSearch`; §"Letting a provider hold it" (152–156) for `openai_conversation_id`, the still-billed input tokens and the Zero Data Retention exclusion; §"What isn't here" (158–160) for the no-mid-step-snapshot rule. Evidence class: **Reported** — vendor documentation; nothing was installed, stored, snapshotted, replayed or searched.
