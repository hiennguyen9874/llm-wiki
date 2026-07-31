---
type: Concept
title: Chain-of-thought prompting
description: Few-shot chain-of-thought prompting supplies worked natural-language rationales before answers so a language model can generate intermediate reasoning steps without updating its weights.
tags: [chain-of-thought, prompting, few-shot-learning, in-context-learning, reasoning]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:07:23Z }
sources:
  - id: wei-cot-summary
    resource: ../raw/Chain-of-ThoughtPrompting.md
    title: Chain-of-Thought Prompting overview (Vietnamese summary)
  - id: yao-tot-summary
    resource: ../raw/TreeofThoughts.md
    title: Tree of Thoughts overview (Vietnamese summary)
  - id: yao-react-summary
    resource: ../raw/ReAct.md
    title: ReAct overview (Vietnamese summary)
---

# Chain-of-thought prompting

Few-shot chain-of-thought (CoT) prompting demonstrates a question, a natural-language sequence of intermediate steps, and a final answer; the model then continues that pattern for a new question. It elicits multi-step outputs through in-context examples rather than fine-tuning or weight updates.[^wei-cot-summary]

## Prompting pattern

A CoT demonstration has the form `question → worked rationale → final answer`, unlike standard few-shot prompting's `question → answer` form. The generated rationale can state intermediate quantities, transformations, or conditions before the final response.[^wei-cot-summary]

The source characterizes the original 2022 method as *few-shot* CoT. It distinguishes this from later zero-shot instructions such as “Let's think step by step,” which were not the technique evaluated in the cited paper.[^wei-cot-summary]

## Proposed role

CoT exposes intermediate textual state, which can decompose a multi-step task into smaller conditional predictions and give decoding more tokens in which to carry forward results. This is a proposed account of the reported behavior, not proof that the text faithfully records the model's internal computation.[^wei-cot-summary]

## Use boundaries

CoT is most relevant when a task requires multiple dependent steps, an adequate model can follow the demonstrated structure, and accuracy merits additional output tokens. It can add latency, token cost, and opportunities for error; simple one-step tasks may gain little or lose accuracy.[^wei-cot-summary]

## Relationships

- **Uses:** [GPT-3 in-context learning evaluation and results](gpt-3-in-context-learning-evaluation-and-results.md)'s few-shot conditioning mechanism, while changing the demonstrations to include rationales.
- **Evaluated by:** [Chain-of-thought prompting evaluation and limitations](chain-of-thought-prompting-evaluation-and-limitations.md), which records the reported task results, scale dependence, prompt sensitivity, and faithfulness limits.
- **Extended by:** [Tree of Thoughts deliberate search](tree-of-thoughts-deliberate-search.md), which retains and searches multiple intermediate paths rather than committing to one linear rationale.[^yao-tot-summary]
- **Extended by:** [ReAct reasoning-and-acting agent loop](react-reasoning-and-acting-agent-loop.md), which uses reasoning traces to select actions and revise its local plan from observations.[^yao-react-summary]

[^wei-cot-summary]: “Chain-of-Thought Prompting overview” (Vietnamese summary), [raw source](../raw/Chain-of-ThoughtPrompting.md), Sections 1–3, 6–8, and 11–13. This is secondary-source evidence that links to Wei et al., “Chain-of-Thought Prompting Elicits Reasoning in Large Language Models,” arXiv:2201.11903; the primary paper has not been independently ingested here.

[^yao-tot-summary]: “Tree of Thoughts overview” (Vietnamese summary), [raw source](../raw/TreeofThoughts.md), Sections 2 and 7. This is secondary-source evidence that summarizes Yao et al., “Tree of Thoughts: Deliberate Problem Solving with Large Language Models” (NeurIPS 2023); the primary paper has not been independently ingested here.

[^yao-react-summary]: “ReAct overview” (Vietnamese summary), [raw source](../raw/ReAct.md), Sections 1–3 and 10. This is secondary-source evidence summarizing Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models” (ICLR 2023); the primary paper has not been independently ingested here.
