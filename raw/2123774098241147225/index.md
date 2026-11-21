---
title: "Post by @a1zhang on X"
author: "@a1zhang"
site: "X (Twitter)"
published: 2026-11-20
source: "https://x.com/a1zhang/status/2123774098241147225"
domain: "x.com"
language: "en"
description: "Harnesses used to be a crutch for weak LLMs. In 2026 and onward, with stronger models, harnesses now offer a mechanism for composing an LLM’"
word_count: 187
---

Harnesses used to be a crutch for weak LLMs. In 2026 and onward, with stronger models, harnesses now offer a mechanism for composing an LLM’s existing and new capabilities to generalize well beyond their training environments.

In our new paper, LM Harnesses are Compositional Generalizers, we explore how various harness abstractions enable LM systems to generalize over task length, task strategies, recursive task depth, and more through composing existing LLM capabilities. These abstractions provide a means for more data-efficient training, especially over long tasks, by keeping trajectories locally in-distribution (LID) — i.e., shaping all individual LLM calls to be in-distribution.

For tasks that take a very long time to roll out, this implies that we can even perform surrogate harness training, meaning we train an individual LLM call instead of doing the very long harness rollout, using purely synthetic tasks, with fake tool calls + sub-agents!

A common idea floating around is that LLMs will absorb harnesses and make them obsolete. We disagree, and argue that we haven’t sufficiently explored what harnesses can provide.

The full paper, logs, codebase, and data are available: [https://t.co/AXBjdoqmiz](https://t.co/AXBjdoqmiz)

w/ @SOURADIPCHAKR18 @lateinteraction
