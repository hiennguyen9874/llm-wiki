---
type: Concept
title: Recursive language models
description: An inference scaffold that externalizes prompts and uses code to orchestrate language-model calls over their parts.
tags: [language-models, inference, long-context]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T17:01:33Z }
sources:
  - id: rlm-paper-v3
    resource: ../raw/arXiv-2512.24601v3/main.tex
    scope: ../raw/arXiv-2512.24601v3/
    kind: paper
    revision: arXiv-2512.24601v3
    title: Recursive Language Models
  - id: rlm-blog
    resource: ../raw/alexzhang13-rlm/index.md
    scope: ../raw/alexzhang13-rlm/
    kind: article
    title: Recursive Language Models — Alex L. Zhang
  - id: alve-rlm
    resource: ../raw/rlm/index.md
    scope: ../raw/rlm/
    kind: article
    title: Recursive Language Models — Om Alve
---

A recursive language model (RLM) is an inference scaffold that stores the prompt in an external environment, lets a root language model write code to inspect and transform it, and permits programmatic model calls over constructed parts. This extends the system's effective input and output handling without increasing the underlying model's context window; practical processing remains bounded by resources, model reliability, and implementation limits. **Reported**, not independently reproduced.[^rlm-paper-v3]

## Mechanism

1. Initialize a persistent REPL with the input as a variable and a callable sub-model or sub-RLM. The root receives metadata rather than the entire input.
2. The root emits code, which runs against persistent state; truncated output or metadata returns to the root. Code may search, chunk, loop, delegate semantic work, and save intermediate answers.
3. Return an environment variable holding the result, allowing output assembled outside the root's own generation limit. The implementation also permits a direct final answer.[^rlm-paper-v3]

The paper distinguishes three design choices: a symbolic input handle, symbolic output, and sub-calls from inside code rather than only separately verbalized delegation. The authors call the no-sub-call ablation depth 0, plain sub-LM calls depth 1, and nested RLMs depths greater than 1. In GPT-5 experiments the root is GPT-5 and leaf calls use GPT-5-mini. Abstract unboundedness is an expressivity goal, not a claim that actual deployment has infinite memory, cost, or correctness.[^rlm-paper-v3]

The earlier blog frames this as **context-centric** rather than task-centric decomposition: the model chooses at inference time whether to peek at structure, grep, partition and map semantic labeling across sub-calls, or summarize. It also describes an illustrative diff-history task processed programmatically; this is an example, not a benchmark-wide success rate. The blog's experimental sub-calls have depth 1, although the abstract definition allows nested RLMs. **Reported.**[^rlm-blog]

Alve contrasts RLM context access with retrieval-augmented generation, conversation compaction and context folding. The article presents RLMs as avoiding compaction, but this is a characterization of the scaffold rather than a prohibition on sub-call summaries: the author's blog explicitly includes summarization among possible strategies. **Synthesis** from the two accounts.[^alve-rlm][^rlm-blog] Alve's illustrative diagram shows the root delegating over part of a corpus and then inspecting a source excerpt in the REPL; it is an example, not evidence of general reliability. **Observed** in the diagram.[^alve-rlm]

## Operational limitations

**Reported:** decomposition and prompt examples affect results; coding and syntax failures, inappropriate final-answer tags, excessive sub-calls, and lost intermediate results can undermine a run. The paper's main implementation uses blocking sequential sub-calls, producing long latency tails; guardrails, sandboxing, and cost control are underexplored. A model-specific prompt cautions Qwen against excessive calls. The Qwen3-8B prompt gives conflicting character approximations for a 32k-token limit, so its character limits should not be treated as reliable defaults.[^rlm-paper-v3]

## Relationships

- **Synthesis:** [Prime Intellect RLM scaffold](prime-intellect-rlm.md) describes a depth-one implementation with delegated tools and editable answer state.
- **Synthesis:** [RLM workflows in Deep Agents](deep-agents-rlm-workflows.md) describes a reported interpreter and subagent application of this approach.
- **Synthesis:** [Recursive-llm implementation](recursive-llm-grishahq.md) is an independent implementation with bounded execution and document citation checks.
- **Synthesis:** [rlm.pi implementation](rlm-pi-implementation.md) applies the scaffold as a Pi plugin, with a Python worker that is not a security boundary.
- **Synthesis:** [Compositional generalization in LM harnesses](compositional-generalization-in-lm-harnesses.md) examines how this scaffold can transfer learned decompositions.
- **Synthesis:** [Surrogate harness training](surrogate-harness-training.md) targets orchestration behavior in this scaffold using synthetic tasks.
- **Synthesis:** [Prime Agent harness](prime-agent.md) applies recursive inference with asynchronous persistent subagent sessions.
- **Synthesis:** [RLM evaluation and benchmarks](rlm-evaluation.md) measures this scaffold against direct calls, agents, and compaction.
- **Synthesis:** [Training recursive language models](training-recursive-language-models.md) studies training the root to operate this scaffold.

## Source and coverage

Zhang, Kraska and Khattab, *Recursive Language Models*, arXiv:2512.24601v3; [upstream paper](https://arxiv.org/abs/2512.24601v3), [authors' code](https://github.com/alexzhang13/rlm). Source package is LaTeX; no experiment or document build was run, and external code and license were not checked. Main sections, benchmark, methods, training, negative-result and quantitative appendices, tables and trajectory descriptions were inspected as text; architecture, training and error plots were visually inspected. Bibliography and style/macros were inventoried but not fully reviewed; other figures and trajectory screenshots remain pending visual inspection, including the scaling PDF. Their captions or textual descriptions inform only qualified claims. No independent verification of reported experimental results was performed. Draft status records these coverage limits.[^rlm-paper-v3]

The [author's blog](../raw/alexzhang13-rlm/index.md) is dated 2025-10-15 but includes later paper-acceptance and code links without an update date; its license and capture date are not specified. The entry text and three benchmark charts were inspected; external links were not fetched and no code was executed. Architecture diagrams `teaser.png`, `api.png`, and `repl.png` are covered by their captions and prose; `pumpkin.png` is decorative. The six trajectory screenshots (`1.png`–`6.png`) are illustrative and not visually inspected; their fine-grained details remain pending. The preliminary blog results and paper results use different samples and must not be merged as one experiment. No independent verification was performed.[^rlm-blog]

Om Alve's [article](../raw/rlm/index.md), published 2026-07-23, is a secondary explanation citing Zhang's blog. Its capture date and license are not specified. The entry and its sole local diagram were inspected; external links were not fetched and no code or experiments were run. The diagram's example is illustrative, not independently verified.[^alve-rlm]

[^alve-rlm]: [Article capture](../raw/rlm/index.md), “The problem”, “How RLM works”, “Why this works”, and “Depth limit”; `assets/Pasted-image-20260723215142.webp`, REPL environment diagram.

[^rlm-blog]: [Blog capture](../raw/alexzhang13-rlm/index.md), “Recursive Language Models”, “What is the RLM doing?”, “Limitations”, and “What We’re Thinking Now & for the Future”.

[^rlm-paper-v3]: [Paper source](../raw/arXiv-2512.24601v3/main.tex), abstract and §2; `sections/sec3-rlm.tex`, `tables/pseudocode.tex`, `sections/sec4-results.tex` §§Methods and Analyses, `sections/sec7-limitations.tex`, `appendix/failed.tex`, `appendix/sec3-methods.tex` §Prompts; `figures/Fig2.png`.
