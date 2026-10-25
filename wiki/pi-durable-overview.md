---
type: Concept
title: Pi Durable Overview
description: An experimental TypeScript agent harness in which model turns, tool calls, and application state are committed to storage before display, so an interrupted process resumes where it stopped, built as a small general primitive rather than a feature of one product.
tags: [pi-durable, durable-agents, agent-harness]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:15:00Z }
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

`@earendil-works/pi-durable` is an experimental TypeScript agent harness: conversations, model turns, tool calls, and the host's own state are committed to storage before anything is shown, and reopening the storage after a process dies picks the work up where it stopped. It builds on `@earendil-works/pi-ai` for model access and `@earendil-works/chord` for document state; the README warns that its API changes without notice between releases.[^pi-durable-readme]

A third-party explainer describes the harness as five layers totaling approximately 15,000 lines of TypeScript; the captured text names two: `pi-ai` for models, providers, streaming, and sign-in, and an `ExecutionEnv` that gives tools files and shells, one per conversation if desired.[^tannermidd-durable]

## Why it was built as a primitive

The authors describe the harness as a small general primitive — "only like twelve thousand lines of code or so" — generic enough to build the next product on and powerful enough to cover what an agent needs out of the box, compaction included. The talk says the durability problem had been solved repeatedly inside individual products (Hermes, OpenClaw, and AMP's Orbs, which transfer sessions), but never as an off-the-shelf primitive that another project could take and own. It also concedes the point directly: you do not need Pi Durable, and you could build it yourself; the effort is in the core design that makes recovery trustworthy, not in the line count, and the design took roughly eight iterations.[^pi-durable-talk]

Portability is part of that pitch: the talk lists Vercel, Cloudflare Durable Objects, E2B, a laptop, and a phone as places the same harness can run, with [storage backends](pi-durable-storage.md) and the [Cloudflare deployment pattern](pi-durable-on-cloudflare.md) supplying the specifics. The enduring constraint is the same one Pi already had: the whole conversation tree must not be kept in memory, because a workspace bot can accumulate years of history even though the model only ever sees a window of it.[^pi-durable-talk]

The unit that makes all of this composable is described in [the effect sandwich](pi-durable-effect-sandwich.md): store intent, run the effect, store the result, and run each such step as a durable task.

## Object model

| Name | Role |
| --- | --- |
| **Harness** | One open storage plus the machinery that runs agents on it. All changes go through one line of atomic commits; nothing is shown before its commit is stored. |
| **Conversation** | A transcript. `root()` creates the root on first use; more can be created and forked. A handle holds no state, so compare handles by `id`. |
| **Entry** | One immutable transcript record: `pi.user`, `pi.assistant`, `pi.tool-result`, `pi.system`, `pi.reset`, or a host-defined kind. The model sees entries from the newest reset onward. |
| **Commit** | An atomic write that can append entries, edit documents, and create tasks together; all of it is stored or none of it. |
| **Document** | Typed JSON state stored next to the transcript. Built-ins hold agent choices (`pi.agent`), provider session identity (`pi.provider`), running generation and tools (`pi.live`), queued submissions (`pi.inbox`), and spend (`pi.usage`); hosts define their own as described in [documents and host state](pi-durable-documents.md). |
| **Task** | A durable state machine that checkpoints every step. Every task is owned by a conversation or another task. Built-in `pi.generation` tasks call the model, own the `pi.tool` tasks of their tool calls, wait for them, and hand the run to the next generation. |
| **Submission** | Input or a write handed to a conversation, which the caller can wait for. |
| **Turn / run** | A turn is one model response and its tool calls; a run spans from an input to its final answer. The conversation is busy while a run proceeds. |
| **Extension** | A named bundle of tools, system-prompt sections, hooks, wrappers, and tasks. |
| **Registry** | The extensions this process installed. It can change while the Harness runs, and new work uses the new state. |
| **Agent** | Model, thinking level, selected extensions, tools, instructions, and working directory. Stored per conversation as names in `pi.agent` and resolved against the registry at each use. |

An answered input flows through entries and tasks as follows: `submit(input)` appends `pi.user`; a `pi.generation` task writes `pi.system` only if the prompt or tools changed, then `pi.assistant` with tool calls; the generation owns and waits for `pi.tool` tasks that produce `pi.tool-result` entries; a further generation writes the final `pi.assistant` answer and settles the submission `done`.[^pi-durable-readme]

## Minimal setup

`npm install @earendil-works/pi-durable @earendil-works/pi-ai @earendil-works/chord` provides the packages, which the README licenses under MIT. The shape of the API is: open a `Harness` over a storage backend with models and a registry, obtain the root conversation, `submit()` an input, `wait()` for the settled submission, and commit the answer entry. `MemoryStorage` keeps everything in memory; durable backends are covered in [Storage backends](pi-durable-storage.md).[^pi-durable-readme]

Every async call takes a Chord `Context` carrying cancellation and the current telemetry span. `BACKGROUND_CONTEXT` never cancels and uses a NOOP span; the Harness owns the root adapter, and adapters are never stored in a `Context`. Cancelling a wait cancels only that wait, never the underlying work. `HarnessOptions.identity` sets provider-facing attribution, merged over `DEFAULT_HARNESS_IDENTITY`; it applies to generation, compaction, hooks, and tools, and can be set to `{ attribution: null }` to send none.[^pi-durable-readme]

## Evidence and limits

The source is package documentation, so its claims are **Reported**, not **Observed** or **Reproduced**: the package itself was not present in the repository, and none of its examples were run. Claims marked as behavior here are the README's account of that behavior. The experimental status and the `stale_after` date record that the API may move.

The Pi Pocket guide is also a secondary source: its simulations are illustrative, and its claims are **Reported**, not reproduced here. It gives no publication or revision date, and its captured text names only two of the five layers it advertises, so the layer count is a coverage limit.

The authors' talk is a third source and is **Reported** as well. It has no publication date, headings, or timestamps, and no code or crash was inspected through it; it contributes design intent — what durability means, why the primitive exists, what it deliberately avoids — rather than verified behavior. Its "twelve thousand lines" is an approximate spoken figure: it can be read as the `pi-durable` package alone, which is consistent with the larger five-layer total reported by the guide, and the two are not treated as a contradiction.[^pi-durable-talk]

Coverage exclusions: the README's generated table of contents is navigational; its Examples and Design Documents sections point to `test/examples` and `docs/spec.md`, which are outside the captured source and therefore unavailable rather than compiled; the License section is recorded as MIT.

## Relationships

- **Depends on** `@earendil-works/pi-ai` (model access) and `@earendil-works/chord` (document state and watches).
- **Uses** [storage backends](pi-durable-storage.md) as the durability substrate.
- **Runs** work as [durable tasks](pi-durable-tasks.md), driven by [conversations and submissions](pi-durable-conversations.md).
- **Persists host state as** [documents](pi-durable-documents.md).
- **Extends behavior through** [extensions, hooks, and per-conversation agents](pi-durable-extensions-hooks-agents.md).
- **Exposes tools via** [tools and nested calls](pi-durable-tools-nested-calls.md) and [code mode](pi-durable-code-mode.md).
- **Manages context with** [compaction](pi-durable-compaction.md) and **observes state through** [observability and telemetry](pi-durable-observability-telemetry.md).
- **Durability semantics are detailed in** [crash recovery and durability](pi-durable-crash-recovery.md), and its general step model is [the effect sandwich](pi-durable-effect-sandwich.md).
- **Deploys on Cloudflare Durable Objects** as a worked session-per-object pattern in [Pi Durable on Cloudflare](pi-durable-on-cloudflare.md).
- **Is positioned as a durability layer, not a deployment location, in** [home, cloud, and durable agents](agent-execution-models-home-cloud-durable.md).

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Concepts, §Quick Start, §Persist and Resume, §Storage.

[^tannermidd-durable]: Pi Pocket, “Pi Durable, explained” (`raw/tannermidd-durable/index.md`; <https://tannermidd.github.io/pi-pocket/durable.html>), locators: §Pi Durable, §Five layers and one sequence of commits.

[^pi-durable-talk]: Mario Zechner and Armin Ronacher, “Pi Durable: Agents That Survive Crashes” (`raw/Pi Durable: Agents That Survive Crashes.md`; <https://www.youtube.com/watch?v=ja_7AF54OtE>), locators by quoted phrase because the transcript has no headings or timestamps: “only like twelve thousand lines of code or so”, “generic enough”, “out of the box it can basically do everything you need from an agent”, “those are not generalized solutions”, “orbs where you can transfer sessions”, “You could totally build this yourself”, “the core design”, “eight iterations”, “easily deployable to a lot of places like Vercel, Cloudflare DO, E2B, your laptop, my phone”, “loaded the entire conversation”, “a Slack bot that lives in your Slack for years and years”.
