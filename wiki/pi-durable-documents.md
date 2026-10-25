---
type: Concept
title: Pi Durable Documents and Host State
description: How pi-durable defines typed documents for host state, controls history and fork behavior, commits edits atomically, and defers cheap writes.
tags: [pi-durable, documents, state, persistence]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:07:19Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-readme
    resource: ../raw/pi-durable-readme.md
    kind: docs
    title: "@earendil-works/pi-durable README"
  - id: tannermidd-durable
    resource: ../raw/tannermidd-durable/index.md
    scope: ../raw/tannermidd-durable/
    kind: article
    title: "Pi Durable, explained (Pi Pocket guide)"
  - id: pi-durable-talk
    resource: "../raw/Pi Durable: Agents That Survive Crashes.md"
    kind: video-transcript
    title: "Pi Durable: Agents That Survive Crashes — Mario Zechner & Armin Ronacher (YouTube)"
---

Documents are typed JSON objects stored next to a conversation's transcript and changed inside atomic commits. Built-in documents hold agent choices, provider identity, live generation state, the inbox, and usage (see [the object model](pi-durable-overview.md)); hosts can define their own with `defineDoc`, edit them through `tx.doc()` in a commit, and read a committed snapshot with `harness.snapshot(doc, conversationId, context)`.[^pi-durable-readme]

## Defining a document

`defineDoc` requires a `kind`, `version`, `scope`, `initial`, and `checkpointWhen`, plus choices for `history` and `fork`:[^pi-durable-readme]

```typescript
const Todos = defineDoc<{ items: string[] }>({
	kind: "app.todos",
	version: 1,
	scope: "conversation",
	history: "latest",       // or "rewindable" to read old values with snapshotAsOf()
	fork: "initial",         // what a fork starts with: "initial", "current", or "asOf"
	initial: () => ({ items: [] }),
	checkpointWhen: () => false, // required: true stores this change as a complete base, bounding replay
});
```

`checkpointWhen` is required even when it always returns false: returning true marks a change as a complete base, which bounds replay. `history` and `fork` interact with the deferred-write optimization below, so they are policy choices rather than cosmetic ones. The guide names the three `scope` values — `session`, `conversation`, and `task` — and the two `history` values, `latest` and `rewindable`; `asOf` needs `rewindable` because it reads old values.[^pi-durable-readme][^tannermidd-durable]

## Why application state is versioned against the transcript

The authors describe the store as a miniature document database with one extra property: a document value can be associated with a position in the transcript. As the conversation proceeds, a to-do list or drawing changes; rewinding to an earlier point may need the value as it was then, while other reads want the latest value regardless of position. Both are supported, and the talk treats that pair — versioned documents plus tasks — as enough to build most of what the harness needs.[^pi-durable-talk]

The concrete example is a canvas: the drawing is a document holding a list of strokes that can be replayed, so it evolves alongside the conversation and an earlier point in the conversation can be shown the earlier drawing. The talk frames this as the application-state half of the durability design; the execution half is [the effect sandwich](pi-durable-effect-sandwich.md).[^pi-durable-talk]

## Patches and the proxy

Version differences are stored as operations on a JSON object, not as whole snapshots. The authors looked at JSON Patch, the RFC for exactly that, and found it lacking for this use case, so they wrote a similar operation format optimized for agentic use. On top of it sits a proxy: a document handed to host code looks and behaves like a JavaScript object, and an assignment such as `object.x = 10` is recorded as an operation and applied to the stored document. The talk calls the proxy "a hack, a slow hack, to be exact", says it works well for what an agent harness needs, and acknowledges related foot guns without listing them.[^pi-durable-talk]

The broader complaint is that structural updates to nested data still have no agreed standard: Immer mostly gets it right, Automerge's CRDT proxy "has so many holes in it", and React's state transitions never produced a shared notation. That is why the harness carries its own small format instead of adopting one.[^pi-durable-talk]

## Committing and reading

A commit callback receives a transaction and can edit the document directly, for example pushing to `(await tx.doc(Todos, conversationId)).items`. The read after commit uses `harness.snapshot`. `watchDoc()` watches one document like `watch()` watches a conversation view, so a UI can render host state without polling.[^pi-durable-readme]

## Deferred persistence

A commit whose changes are cheap to lose — typically streamed progress — can be shown at once and stored later with `{ persistence: { kind: "deferred", withinMs: 1_000 } }`; without `withinMs` it uses `settings.progress.persistWithinMs`. Watches and the view see it immediately, while storage receives it with the next commit that reads or writes the document, before the document leaves memory, at close, and no later than about `withinMs`; `subscribeCommits()` then sees exactly what was stored. A crash loses what was not stored, so durable state must not be derived from a deferred value outside a commit that reads it.[^pi-durable-readme]

Only a commit that changes nothing but existing documents with `history: "latest"` and `fork: "initial"` can be deferred. Anything else in it — an entry, a new document, or a task state — stores at once.[^pi-durable-readme]

## Giving every conversation its documents

`HarnessOptions.conversationCreated(tx, conversation)` runs in every commit that creates or forks a conversation, including a tool's raw `tx.createConversation()`, so every conversation gets the host's documents. `init` in `createConversation()`, `fork()`, and `root()` writes per-call data in the same commit. An extension's tools, sections, and hooks read their own documents through `api` or `input.read` and treat an absent one as its default; the README's extension-state example (`10-extension-state.ts`) is not present in `raw/`, which is a coverage limit.[^pi-durable-readme]

## Evidence and limits

Document semantics are **Reported** documentation; no document was defined, watched, or deferred. The guide corroborates the scope and policy vocabulary without adding an independent test. The exact replay bounding performed by `checkpointWhen` is asserted but not demonstrated, and the README does not enumerate the validation rules for `kind` or `version` beyond the built-in `pi.` namespace.

The design rationale is a third **Reported** source: the authors' talk, with no date or timestamps, in which the patch format and proxy are described verbally. No patch stream, proxy trap, or replay was inspected, so the operation vocabulary and the unnamed foot guns remain uncovered, and the format's "optimized for agentic use" claim is not independently assessed.[^pi-durable-talk]

## Relationships

- **Is stored by** [storage](pi-durable-storage.md) and follows the deferred-commit rules in [crash recovery](pi-durable-crash-recovery.md).
- **Belongs to** [conversations](pi-durable-conversations.md), which also receive them through `conversationCreated` and `init`.
- **Is read by** [extensions and agent configuration](pi-durable-extensions-hooks-agents.md) through `api` or `input.read`.
- **Is watched through** [observability](pi-durable-observability-telemetry.md) and summarized in the [object model](pi-durable-overview.md).
- **Supplies the application-state half of** [the effect sandwich](pi-durable-effect-sandwich.md), while tasks supply the execution half.

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Concepts, §Your Own State, §Watching a Conversation, §Settings, §Per-Conversation Agent.

[^tannermidd-durable]: Pi Pocket, “Pi Durable, explained” (`raw/tannermidd-durable/index.md`), locators: §Documents and forks.

[^pi-durable-talk]: Mario Zechner and Armin Ronacher, “Pi Durable: Agents That Survive Crashes” (`raw/Pi Durable: Agents That Survive Crashes.md`; <https://www.youtube.com/watch?v=ja_7AF54OtE>), locators by quoted phrase because the transcript has no headings or timestamps: document-database analogy “Do you know document databases like MongoDBs”, “associated with any position inside of your transcript”, “I want the old to do list when I was at this point in time”, “Other times, I just want the latest version”, canvas “a list of strokes that I can replay to draw the drawing”; patches “there's something called JSON patch, which is an RFC”, “I found it to be lacking f for this use case”, “optimized to the agentic. stuff”, “we also use a proxy approach”, “object.x equals ten”, “it's a hack, a slow hack, to be exact”, “foot guns”, “Immer, right, which kinda mostly get it right”, “automerge”, “It has so many holes in it”, “well understood standard”.
