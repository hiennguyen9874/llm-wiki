---
type: Concept
title: ReAct reasoning-and-acting agent loop
description: ReAct interleaves language-model reasoning, environment actions, and observations so an agent can ground and revise local plans during multi-step work.
tags: [react, agents, reasoning, tool-use, prompting, planning]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:07:23Z }
sources:
  - id: yao-react-summary
    resource: ../raw/ReAct.md
    title: ReAct overview (Vietnamese summary)
---

# ReAct reasoning-and-acting agent loop

ReAct (*Reasoning + Acting*) is a prompting and control pattern in which a language model alternates between textual reasoning, an action such as a tool call, and the resulting observation. The feedback loop lets the agent use new environmental evidence to update a local plan rather than relying only on parametric knowledge; the supplied summary attributes the 2023 work to Shunyu Yao and collaborators and describes few-shot prompting of a frozen PaLM-540B model.[^yao-react-summary]

## Interaction model

A typical trajectory is `Thought → Action → Observation → … → Answer`. Thoughts record task decomposition, progress, or a decision about the next action; actions search, browse, query data, execute code, or operate an environment; observations return the action result to the context.[^yao-react-summary]

Formally, ReAct expands the action space from environment actions $A$ to $A \cup L$, where $L$ is language used for reasoning traces. A selected thought changes the next context but not the environment, whereas an environment action produces a new observation.[^yao-react-summary]

For long control trajectories, reasoning can be sparse: the model plans or reassesses at consequential points and executes simple intervening actions without emitting a thought at every step. A production controller still needs to maintain history, dispatch structured tool calls, stop on a final answer, and enforce a maximum-step budget.[^yao-react-summary]

## What the loop adds

Reasoning can select tools, formulate queries, track subgoals, and revise a plan after failure. Acting supplies external information that can test an assumption or fill a factual gap. The pattern is therefore an agent-control policy, not a particular tool protocol: function calling can provide a structured action interface, and a retriever can be one of the available tools.[^yao-react-summary]

## Appropriate boundary

ReAct is suited to tasks whose answer or completion requires adaptive multi-step retrieval or interaction in an uncertain environment. It is not evidence that every question needs a tool call: the source describes hybrid fallback strategies that combine ReAct with self-consistent CoT when either external retrieval or parametric reasoning alone is insufficient.[^yao-react-summary]

## Relationships

- **Extends:** [Chain-of-thought prompting](chain-of-thought-prompting.md) by placing intermediate reasoning in an action–observation feedback loop.[^yao-react-summary]
- **Uses:** [Retrieval-augmented generation operational pipeline and trust limits](retrieval-augmented-generation-operational-pipeline-and-trust-limits.md) as a possible retrieval tool, while choosing whether and how often to retrieve adaptively.[^yao-react-summary]
- **Contrasts with:** [Tree of Thoughts deliberate search](tree-of-thoughts-deliberate-search.md): ReAct revises one interaction trajectory from environment observations, whereas ToT uses an external controller to branch and evaluate alternative thought states.[^yao-react-summary]
- **Evaluated by:** [ReAct evaluation and operational limits](react-evaluation-and-operational-limits.md).

[^yao-react-summary]: “ReAct overview” (Vietnamese summary), [raw source](../raw/ReAct.md), Sections 1–5, 10, 14–15. This is secondary-source evidence summarizing Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models” (ICLR 2023); the primary paper has not been independently ingested here.
