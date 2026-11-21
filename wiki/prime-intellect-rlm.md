---
type: Concept
title: Prime Intellect RLM scaffold
description: An experimental depth-one RLM variant with parallel sub-models, delegated tools, and an editable answer variable.
tags: [language-models, inference, long-context]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:53:08Z }
sources:
  - id: prime-rlm-blog
    resource: ../raw/primeintellect-rlm/index.md
    scope: ../raw/primeintellect-rlm/
    kind: article
    title: "Recursive Language Models: the paradigm of 2026"
---

Prime Intellect describes an experimental [recursive language model](recursive-language-models.md) scaffold in `verifiers`: a root model operates a persistent Python REPL, can batch sub-model calls, and delivers its answer through mutable REPL state. The configuration and experiments are **reported** for the January 2026 article, not a verified description of current software.[^prime-rlm-blog]

## Interface and boundaries

- The prompt enters the root context; optional extra input is held in a Python variable and must be inspected programmatically. REPL output shown to the root is limited to 8,192 characters per turn by default, adjustable by the user.
- `llm_batch` allows parallel sub-model prompts. Environment tools other than Python are available only to sub-models, shielding the root from verbose tool output. The article reports isolated sandbox execution and installable Python packages; it does not establish a security audit.
- The root edits `answer["content"]` and sets `answer["ready"] = True` to finish. The article calls this iterative answer construction “diffusion”; it does not establish a diffusion-model mechanism. Its example initializer omits quotes around the `ready` key, so do not copy that initializer literally.
- The described implementation has recursion depth one. Depth zero, nested recursion, custom REPL functions, better multimodal handling, and multi-turn compression are future plans, not established capabilities.[^prime-rlm-blog]

## Interpretation and limits

The article proposes context folding as complementary to long-context attention and predicts reinforcement-learning training will improve scaffold use. That is a hypothesis, not a measured effect of training in this article. Its statement that the approach “never actually summarizes” is too broad: its own DeepDive tips instruct sub-models to extract and summarize information. Programmatic access may retain the underlying input, but a sub-model summary can still lose information.[^prime-rlm-blog]

## Relationships

- **Synthesis:** [RLM evaluation and benchmarks](rlm-evaluation.md#prime-intellect-ablation) records this implementation's separate ablations and trade-offs.
- **Synthesis:** [Prime Agent harness](prime-agent.md) is a related later Prime Intellect recursive harness, not the same implementation or experiment.

## Source and coverage

Sebastian Müller, Prime Intellect blog, published 2026-01-01; [original article](https://www.primeintellect.ai/blog/rlm). The local article and all 22 result figures were inspected; the architecture image `assets/69547363bbe8773f072cdd0b_rlm.png` was not visually inspected because the article describes the relevant interface. Linked datasets, code, documentation and sandbox guarantees were not fetched or executed. No experiment was reproduced; license, capture date, immutable code revision, and chart underlying data are unspecified. The prose mentions Needle in Haystack in timing despite the four-environment setup and plot; that item is not used. Draft status reflects unavailable code and data and unverified results.[^prime-rlm-blog]

[^prime-rlm-blog]: [Article capture](../raw/primeintellect-rlm/index.md), “The RLM”, “Experimental setup”, “Results”, “RLM Or long context attention for long running agent?”, and “Future Work”; `assets/*rlm-result-1.png` through `*rlm-result-22.png` (visually inspected).
