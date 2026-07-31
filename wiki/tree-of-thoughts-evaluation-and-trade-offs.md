---
type: Concept
title: Tree of Thoughts evaluation and trade-offs
description: The supplied summary reports that Tree of Thoughts improved its three search-oriented evaluations over linear prompting baselines, at substantially greater inference cost and with limits from self-evaluation and task-specific search design.
tags: [tree-of-thoughts, evaluation, reasoning, search, limitations]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:02:02Z }
sources:
  - id: yao-tot-summary
    resource: ../raw/TreeofThoughts.md
    title: Tree of Thoughts overview (Vietnamese summary)
---

# Tree of Thoughts evaluation and trade-offs

The supplied secondary summary reports that ToT outperformed the evaluated input-output and chain-of-thought baselines on Game of 24, constrained creative writing, and mini crosswords. Those findings support using search where intermediate choices can be judged, not a general claim that ToT improves every LLM task.[^yao-tot-summary]

## Reported evaluations

For Game of 24, the summary reports 74% success for BFS ToT with beam width $b=5$, compared with 4% for ordinary CoT and 9% for CoT self-consistency with 100 samples. It also reports that a later repository rerun achieved 69%, qualifying the published percentage as decoding-sensitive rather than fixed.[^yao-tot-summary]

For creative writing, ToT generated and selected plans before generating prose. The summary reports GPT-4 coherence scores of approximately 7.56 for ToT, 6.93 for CoT, and 6.19 for input-output prompting; a small blind human comparison preferred ToT in 41 cases, CoT in 21, and found 38 ties. The automatic score and author-run human study limit the independence of that evidence.[^yao-tot-summary]

For mini crosswords, the summary reports 78% correct letters, 60% correct words, and 20% fully solved games for DFS ToT, compared with 40.6%, 15.6%, and 1% for CoT. Its reported ablations found reduced performance when pruning or backtracking was removed.[^yao-tot-summary]

## Cost and scaling

Search multiplies model calls for generation and evaluation. The source reports 5.5k completion tokens and a then-estimated $0.74 per Game of 24 instance for ToT, versus 6.7k and $0.47 for CoT best-of-100; these 2023 API prices are historical, not current pricing. It further estimates that ToT may consume roughly 5–100 times CoT's tokens depending on the task and search configuration.[^yao-tot-summary]

Unpruned branching can grow exponentially with depth. Beam-width or DFS pruning limits the explored frontier, but effectiveness depends on choosing a useful thought unit, generator, evaluator, search policy, and stopping rule for the specific task.[^yao-tot-summary]

## Reliability limits

- The same LLM that generates and evaluates candidates can favor fluent but wrong paths, produce poorly calibrated scores, or miss computational errors.[^yao-tot-summary]
- Search cannot supply external knowledge that the model lacks; the summary reports only small gains on StrategyQA and attributes the bottleneck to missing knowledge rather than search.[^yao-tot-summary]
- The three reported headline tasks are small and selected to emphasize search, so their gains do not transfer automatically to production tasks.[^yao-tot-summary]

## Relationships

- **Evaluates:** [Tree of Thoughts deliberate search](tree-of-thoughts-deliberate-search.md).
- **Contrasts with:** [Chain-of-thought prompting evaluation and limitations](chain-of-thought-prompting-evaluation-and-limitations.md): ToT allocates compute using intermediate state evaluation and backtracking, whereas CoT's linear rationale can propagate an early error.

[^yao-tot-summary]: “Tree of Thoughts overview” (Vietnamese summary), [raw source](../raw/TreeofThoughts.md), Sections 6, 10–12, and 13. This is secondary-source evidence that summarizes Yao et al., “Tree of Thoughts: Deliberate Problem Solving with Large Language Models” (NeurIPS 2023); the primary paper and repository have not been independently ingested here.
