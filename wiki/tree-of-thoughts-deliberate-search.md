---
type: Concept
title: Tree of Thoughts deliberate search
description: Tree of Thoughts organizes LLM reasoning as an inference-time search over semantically meaningful intermediate states, using the model to propose and evaluate candidate thoughts.
tags: [tree-of-thoughts, reasoning, search, planning, prompting]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:02:02Z }
sources:
  - id: yao-tot-summary
    resource: ../raw/TreeofThoughts.md
    title: Tree of Thoughts overview (Vietnamese summary)
---

# Tree of Thoughts deliberate search

Tree of Thoughts (ToT) treats an LLM's intermediate natural-language reasoning units as states in a search tree. At inference time, an external controller expands multiple candidate thoughts, evaluates the resulting states, retains or revisits promising branches, and stops on a solution; it does not inherently require changing model weights.[^yao-tot-summary]

## State and thought design

A state comprises the problem and its preceding thoughts, while a *thought* is a task-dependent unit that is larger than a token but small enough to branch and evaluate. Examples in the source include an intermediate arithmetic operation for Game of 24, a candidate crossword entry, or a plan for a creative-writing passage.[^yao-tot-summary]

Thought granularity is a task-design choice: token-level nodes give little useful intermediate evaluation, whereas whole solutions leave little opportunity for branching.[^yao-tot-summary]

## Search loop

For each frontier state, ToT has the LLM generate $k$ candidate thoughts, converts them to successor states, evaluates them, and selects states for continued exploration. Generation may sample independent continuations or ask for several distinct proposals in one call. Evaluation may assign each state an absolute value (for example, `sure`, `maybe`, or `impossible`) or have the LLM vote among candidate states.[^yao-tot-summary]

The controller can use breadth-first search (BFS), retaining the top $b$ states at every depth, or depth-first search (DFS), following a branch and backtracking on a dead end. The summary reports BFS for Game of 24 and creative writing, and DFS with backtracking for mini crosswords.[^yao-tot-summary]

## Implementation boundary

A request for a model to list and select alternatives in a single prompt can imitate the pattern, but it does not by itself provide a persistent search tree, controlled frontier, or reliable backtracking. A system implementation needs an external controller to track state ancestry, duplicate states, pruning, stopping conditions, and call/token budgets.[^yao-tot-summary]

For tasks with programmatically checkable constraints, the source recommends an external verifier for validity rather than relying solely on LLM self-evaluation.[^yao-tot-summary]

## Appropriate use

ToT is most appropriate for constrained or multi-step tasks where early decisions matter, partial solutions can be assessed, and quality justifies more inference work—for example, planning, puzzles, debugging, or writing under multiple constraints. It is generally a poor default for simple knowledge questions, summarization, translation, easy classification, or latency-sensitive tasks.[^yao-tot-summary]

## Relationships

- **Extends:** [Chain-of-thought prompting](chain-of-thought-prompting.md) from one generated rationale to a controller-managed search over multiple intermediate paths.
- **Evaluated by:** [Tree of Thoughts evaluation and trade-offs](tree-of-thoughts-evaluation-and-trade-offs.md), which records the reported task results, computation costs, and reliability limits.

[^yao-tot-summary]: “Tree of Thoughts overview” (Vietnamese summary), [raw source](../raw/TreeofThoughts.md), Sections 1–5, 7–9, and 12. This is secondary-source evidence that summarizes Yao et al., “Tree of Thoughts: Deliberate Problem Solving with Large Language Models” (NeurIPS 2023); the primary paper and repository have not been independently ingested here.
