---
type: Concept
title: "Pi Durable State Model: Journal-and-Reduce to Authoritative Snapshots"
description: How Pi Durable's persisted state reportedly moved from an event-sourcing-style journal-and-reduce in Harness v2 to complete, ID-keyed OperationState snapshots that are the authoritative recovery state rather than a cache that shortens replay.
tags: [pi-durable, durability, state-model, event-sourcing, crash-recovery]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T17:05:00Z }
stale_after: 2027-04-25
sources:
  - id: yaogangqiang-status
    resource: ../raw/yaogangqiang-status/index.md
    scope: ../raw/yaogangqiang-status/
    kind: social-post
    title: "Post by @yaogangqiang on X: Pi as a durable runtime, and its state model"
---

A short X post by @yaogangqiang frames Pi's work as upgrading the in-process agent loop into a durable runtime that survives process death, and — unlike any other source compiled here — describes the persisted state representation itself as having changed: Harness v2 reportedly used an event-sourcing-style *journal-and-reduce*, while the current specification writes a complete, ID-keyed `OperationState` snapshot on every state transition and points a slot at the newest version, so recovery reads authoritative state instead of replaying orchestration history.[^yaogangqiang-status] This page records that state-model history; the step-level durability mechanism it serves is [the effect sandwich](pi-durable-effect-sandwich.md), and the behavior built on it is [crash recovery](pi-durable-crash-recovery.md).

## Harness versus agent loop

The post's definition matches the harness/loop distinction recorded elsewhere: a loop's execution depends on the process it runs in, while a harness turns an accepted prompt into a persistent operation that can be recovered across processes.[^yaogangqiang-status] The framing is introductory rather than argued; it serves to set up the recovery question the state model has to answer.

## The recovery question

The question is stated directly: if the process dies while a model or tool is executing, how does the restarted process determine how far the work got, without losing already-committed work and without blindly re-running side effects?[^yaogangqiang-status] That is the same uncertainty the authors of Pi describe as the three crash windows around an effect, and it is why intent is written before an effect runs and its result after — see [the effect sandwich](pi-durable-effect-sandwich.md) and [replay safety](pi-durable-replay-safety.md).

## Harness v2: journal-and-reduce

Harness v2 is described as using something "similar to Event Sourcing": it continuously appended orchestration records, then replayed or reduced the current state from the records' order and from which records were present or absent.[^yaogangqiang-status] In that form, the current state is derived — it exists only as the output of replaying a log, which is the standard event-sourcing shape.

## The current specification: full-state snapshots

The current spec is described as a small snapshot at every state transition: it writes a complete `OperationState` that is primarily ID-based, then uses a slot to point at the latest version. Recovery reads that newest state and the references it carries; it does not replay the orchestration history.[^yaogangqiang-status]

The claim that matters for comparison is what the snapshot *is*. Unlike the periodic snapshots of a traditional event-sourcing system, which are derived caches that shorten replay, this snapshot is the authoritative state for recovery.[^yaogangqiang-status] Nothing is reconstructed: the recovered state is the stored state.

## What the trade-off buys and costs

The cost is stated plainly: the complete state is rewritten repeatedly instead of appending records. The benefit claimed is that crash states become explicit, enumerable, and testable.[^yaogangqiang-status] Read as a design argument (**Synthesis**), the move trades write amplification for inspectability: a recovery state is a first-class, assertable artifact rather than an emergent property of log order and absence, which is what makes crash scenarios enumerable in tests rather than sampled by replay.

## Limits: exactly-once is still not guaranteed

The post is explicit that the state model does not make external effects exactly-once. Its `intent → effect → settlement` sequence only makes the uncertain window explicit, after which the harness handles it by replay policy.[^yaogangqiang-status] This agrees with the per-operation account in [replay safety](pi-durable-replay-safety.md): durable state can tell a new process which step it was on, not whether an external system acted.

## Relationship to the authors' own account

The Pi authors say of the current design, "We don't do event sourcing", without naming the problems they attribute to it.[^pi-durable-talk] This post supplies a compatible history rather than a contradiction — v2 was journal-based, the current spec is snapshot-based — and it offers the trade-off the talk leaves implicit. Neither source can be ordered against the other: the post is dated 2026-08-11, while the captured talk carries no publication date. The denial is therefore best read as applying to the current specification, not to every Pi design generation, a qualification now recorded in [the effect sandwich](pi-durable-effect-sandwich.md).

## Evidence and limits

**Reported** throughout, from a single short post (334 words in the capture). No code, schema, or specification was inspected, and no crash or recovery was reproduced here, so every mechanism claim is the author's summary, not an observed implementation detail.

Material limits:

- Provenance is thin: the capture identifies only the handle @yaogangqiang, gives no role or affiliation, and does not establish that the author is a Pi maintainer. The post summarizes a design rather than citing code, so it is authoritative about neither the implementation nor the roadmap.
- "Current specification" (当前规范) is the post's own term. It does not say which release implements it, whether it ships, or how the `OperationState` slot maps onto the entries, documents, and commits described in [crash recovery](pi-durable-crash-recovery.md) and [documents](pi-durable-documents.md). Any mapping between the two vocabularies is **Synthesis** and untested.
- The post's closing `t.co` link is unresolved in `raw/`, so whatever it points at — a demo, repository, or longer write-up — is unavailable here and is a recorded coverage limit; if it contains the v2 design or the specification, this page records only the summary.
- The captured frontmatter labels the language `en` while the body is Chinese; quotes are reproduced from the Chinese body and paragraph locators follow the capture's order.
- The trade-off is asserted, not measured: no write-amplification figure, schema size, or test suite is given to support "explicit, enumerable, testable".

## Relationships

- **Explains the design history of** [the effect sandwich](pi-durable-effect-sandwich.md), whose authors deny event sourcing for the current design.
- **Refines** the "we don't do event sourcing" position recorded in [the effect sandwich](pi-durable-effect-sandwich.md) by identifying the earlier journal-based generation.
- **Is the state representation behind** [crash recovery](pi-durable-crash-recovery.md), which resumes from committed state.
- **Leaves exactly-once external effects to** [replay safety and external effects](pi-durable-replay-safety.md) through the `intent → effect → settlement` sequence.
- **Is persisted by** [storage backends](pi-durable-storage.md), which supply the commit boundary the snapshots rely on.

[^pi-durable-talk]: Mario Zechner and Armin Ronacher, “Pi Durable: Agents That Survive Crashes” (`raw/Pi Durable: Agents That Survive Crashes.md`; <https://www.youtube.com/watch?v=ja_7AF54OtE>), quoted phrase: “We don't do event sourcing.”

[^yaogangqiang-status]: @yaogangqiang, “Post by @yaogangqiang on X” (`raw/yaogangqiang-status/index.md`, published 2026-08-11; <https://x.com/yaogangqiang/status/2087108405337153953>), locators by body paragraph in capture order because the post has no headings: ¶1 “Pi 正在把进程内的 Agent Loop，升级为可跨进程恢复的 Durable Runtime”; ¶2 “Loop 的执行依赖当前进程；Harness 将已接受的 Prompt 变成可跨进程恢复的持久化 Operation”; ¶3 “重启后如何确定做到哪一步，既不丢失已提交工作，也不盲目重跑副作用”; ¶4 “Harness v2 采用类似 Event Sourcing 的 journal-and-reduce”“持续追加编排记录”“根据记录的顺序、存在与缺失，replay/reduce 出当前状态”; ¶5 “当前规范则类似于每次状态转换都打一个小快照”“写入完整、以 ID 为主的 OperationState，再用 slot 指向最新版”“恢复直接读取最新状态及其引用，不再 replay 编排历史”; ¶6 “不是用于缩短 event replay 的派生缓存，而是恢复的权威状态”; ¶7 “它仍不能保证外部效果 exactly-once”“intent → effect → settlement 只是将不确定窗口显式化，再按 replay 策略处理”“代价是重复写入完整状态，换来显式、可枚举、可测试的崩溃状态”.
