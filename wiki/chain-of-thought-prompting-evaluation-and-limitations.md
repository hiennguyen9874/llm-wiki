---
type: Concept
title: Chain-of-thought prompting evaluation and limitations
description: The supplied summary reports that few-shot chain-of-thought prompting improved large-model multi-step reasoning benchmarks, with scale- and prompt-dependent gains that do not establish faithful internal reasoning.
tags: [chain-of-thought, evaluation, reasoning, prompting, limitations]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:02:02Z }
sources:
  - id: wei-cot-summary
    resource: ../raw/Chain-of-ThoughtPrompting.md
    title: Chain-of-Thought Prompting overview (Vietnamese summary)
  - id: yao-tot-summary
    resource: ../raw/TreeofThoughts.md
    title: Tree of Thoughts overview (Vietnamese summary)
---

# Chain-of-thought prompting evaluation and limitations

The supplied summary reports that few-shot CoT improves arithmetic, commonsense, and symbolic-reasoning evaluations chiefly for sufficiently large models and difficult multi-step items. Its results are contingent on the model, prompt demonstrations, and task; fluent rationales neither guarantee correct answers nor establish that they expose the model's actual internal reasoning.[^wei-cot-summary]

## Reported evaluation

The source says the paper evaluated LaMDA, GPT-3, and PaLM across arithmetic word problems, commonsense questions, and symbolic tasks including last-letter concatenation and coin flips. It reports that PaLM 540B with eight CoT demonstrations attained about 57% on GSM8K, versus about 18% for standard prompting, and exceeded the then-reported 55% best result.[^wei-cot-summary]

On symbolic tasks, the source reports better transfer to sequences longer than the prompt demonstrations for sufficiently large models. It also reports that CoT gains were largest for semantically complex, multi-step tasks; adding rationales to simple one-operation problems provided little benefit and could hurt.[^wei-cot-summary]

## Scale and ablations

The reported benefit was scale-sensitive: smaller models could produce fluent but logically deficient explanations, while gains became pronounced at very large scale in the evaluated model families. The summary labels this an emergent ability, but explicitly cautions that an approximately 100B-parameter threshold is an observation from the 2022 settings rather than a general law.[^wei-cot-summary]

The source further reports that emitting equations alone, unstructured extra text, or explanations after the answer did not match full CoT performance on difficult word problems. These ablations support the limited conclusion that structured intermediate content before an answer mattered in those experiments, not that output length alone caused the gain.[^wei-cot-summary]

## Limitations

- A correct final answer can accompany invalid reasoning, and a plausible rationale can be wrong; generated CoT is not assured to be a faithful trace of internal computation.[^wei-cot-summary]
- An early incorrect step can propagate through subsequent steps, so CoT makes a response more inspectable without making it self-verifying.[^wei-cot-summary]
- Results varied substantially with the particular human-written demonstrations, including on the coin-flip task.[^wei-cot-summary]
- Longer rationales increase generated-token cost, latency, context use, and the risk of irrelevant or erroneous text.[^wei-cot-summary]

## Relationships

- **Evaluates:** [Chain-of-thought prompting](chain-of-thought-prompting.md).
- **Contrasts with:** [Tree of Thoughts evaluation and trade-offs](tree-of-thoughts-evaluation-and-trade-offs.md): ToT's intermediate state selection and backtracking aim to avoid linear error propagation, but add search cost and evaluator risk.[^yao-tot-summary]

[^wei-cot-summary]: “Chain-of-Thought Prompting overview” (Vietnamese summary), [raw source](../raw/Chain-of-ThoughtPrompting.md), Sections 4–11. This is secondary-source evidence that links to Wei et al., “Chain-of-Thought Prompting Elicits Reasoning in Large Language Models,” arXiv:2201.11903; the primary paper has not been independently ingested here.

[^yao-tot-summary]: “Tree of Thoughts overview” (Vietnamese summary), [raw source](../raw/TreeofThoughts.md), Sections 2, 6, and 11. This is secondary-source evidence that summarizes Yao et al., “Tree of Thoughts: Deliberate Problem Solving with Large Language Models” (NeurIPS 2023); the primary paper has not been independently ingested here.
