---
type: Concept
title: Pi Durable Compaction
description: Manual and automatic compaction summarizes old entries into a pi.compaction entry, respects per-model token budgets, and governs how a too-long context recovers or fails.
tags: [pi-durable, compaction, context-window, tokens]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:02:23Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-readme
    resource: ../raw/pi-durable-readme.md
    kind: docs
    title: "@earendil-works/pi-durable README"
  - id: flaviocopes-pi-durable
    resource: ../raw/flaviocopes-pi-durable/index.md
    scope: ../raw/flaviocopes-pi-durable/
    kind: article
    title: "How to build agents that survive crashes with Pi Durable"
---

Compaction shrinks what the model sees: it summarizes older entries and appends a `pi.compaction` entry holding the summary and heading the first entry it keeps. Older entries stay in storage, and the conversation keeps working while the summary is made. The summary is placed at once when the conversation is idle, otherwise at the next turn boundary.[^pi-durable-readme]

A summary can omit details, so facts the application must preserve — an incident ID, repository, or associated pull request — belong in structured documents or another database rather than only in the transcript.[^flaviocopes-pi-durable]

## Manual compaction

`root.compact("Keep the failing test names", context)` starts a manual compaction with optional instructions and returns a task ID. Waiting for that task yields an outcome; if it completed with a `submissionId`, waiting for that submission shows `done`, or `unanswered` with reason `stale`. Esc (`abort()`) cancels a manual compaction; automatic compaction is controlled by settings.[^pi-durable-readme]

## Automatic thresholds

```typescript
settings: {
  compaction: {
    enabled: true,              // automatic compaction; manual compact() always works
    reserveTokens: 16384,       // above contextWindow - reserveTokens, the next request waits for a compaction
    keepRecentTokens: 20000,    // roughly how much recent context stays verbatim
    backgroundTokens: 32768,    // this far below that, a compaction starts in the background; 0 disables it
    modelOverrides: {
      // exact "provider/modelId"; each field set here replaces the one above for that model
      "local/small-32k": { reserveTokens: 4096, keepRecentTokens: 8000, backgroundTokens: 4096 },
    },
  },
}
```

Fixed token counts rarely suit both a 32k and a 1M context window, so `modelOverrides` lets one harness serve both. The conversation's current model selects the override at the threshold check, after a context overflow, and when a compaction selects what to summarize.[^pi-durable-readme]

When a provider rejects a request because the context is too long, generation compacts and retries once. A summary that would cut before the start of the current context settles `stale` when placed, so when several are in flight, the furthest cut stays in effect. Summarization spend counts in `pi.usage`. A `beforeCompact` hook on `CompactionTask` can decline or supply its own summary.[^pi-durable-readme]

## Failures and visibility

When a compaction that a generation waits for at the blocking threshold fails, the generation fails too without sending a request: its inputs settle `unanswered` with `model_error` and detail `Compaction failed: <error>`. A compaction that finds nothing to compact or is declined lets the request go ahead.[^pi-durable-readme]

Running compactions are listed in `docs["pi.live"].compactions` with reason, attempt, and retry backoff. The newest failure stays in `docs["pi.live"].compactionFailure` (task, reason, error) until a compaction produces a summary. Agent events add `compaction_start` and `compaction_end` (with `error` on failure) plus `compactions` and `compactionFailure` in the snapshot.[^pi-durable-readme]

## Contradictions

The README's "Compaction" example calls `harness.submission(outcome.result.submissionId, context)` with a context argument, while its "Persist and Resume" section calls `harness.submission(id)` without one. Both are recorded; this wiki does not choose between them.

## Evidence and limits

Compaction behavior is **Reported** documentation; no compaction was run, and the "roughly" nature of `keepRecentTokens` and the provider-specific overflow behavior are unverified. The tutorial's advice to keep must-preserve facts in structured documents is also **Reported** guidance, not a measured summary-loss rate.

## Relationships

- **Runs as** a [durable task](pi-durable-tasks.md) that can be aborted or waited for.
- **Uses** the conversation's [agent](pi-durable-extensions-hooks-agents.md) to pick the summarizing model.
- **Affects** [conversation](pi-durable-conversations.md) submissions and context, and appears in [observability](pi-durable-observability-telemetry.md) live state and events.
- **Counts spend in** `pi.usage`, persisted through [storage](pi-durable-storage.md).

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Compaction, §Persist and Resume, §Agent Events (Experimental), §Usage and Cost, §Settings.

[^flaviocopes-pi-durable]: Flavio Copes, “How to build agents that survive crashes with Pi Durable” (`raw/flaviocopes-pi-durable/index.md`, published 2026-10-16), locators: §Long conversations still have context limits.
