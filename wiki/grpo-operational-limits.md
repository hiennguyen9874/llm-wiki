---
type: Concept
title: GRPO operational limits
description: GRPO trades critic memory for multiple on-policy rollouts and remains limited by group reward variance, reward design, coarse outcome credit assignment, and base-model exploration capacity.
tags: [grpo, reinforcement-learning, reasoning, limitations, reward-modeling]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:12:59Z }
sources:
  - id: grpo-summary
    resource: ../raw/GRPO.md
    title: "GRPO overview (Vietnamese summary)"
---

# GRPO operational limits

GRPO removes the memory and optimization burden of a learned critic, but it exchanges that burden for multiple on-policy completions per prompt. Its learning signal is only as useful as reward variation within each group and the reward or verifier’s alignment with the intended behavior; outcome-only rewards also give every token in a completion the same credit.[^grpo-summary]

## Group-signal and rollout limits

- If all completions for a prompt have the same reward, group standardization produces zero or near-zero advantages. Prompts that are too hard (all attempts fail) and too easy (all receive the same success reward) therefore provide weak policy-gradient signal. The source identifies difficulty selection or curriculum as important for maintaining informative groups.[^grpo-summary]
- Generating $G$ completions per prompt can dominate cost, particularly for long reasoning traces. Removing a critic lowers model-memory requirements but does not imply low end-to-end training cost.[^grpo-summary]
- Group-relative advantage is not an absolute quality measure: the least-bad completion in a poor group can receive positive advantage. Reward design, filtering, and curriculum must address this rather than treating positive advantage as evidence of an objectively good answer.[^grpo-summary]

## Reward and credit-assignment limits

- An outcome reward assigns one advantage to all tokens in a completion. It can reinforce redundant, irrelevant, or locally incorrect steps that happen to occur in an ultimately successful answer; process rewards can improve granularity but require a reliable step-level evaluator.[^grpo-summary]
- The policy optimizes the measured reward rather than intent. Final-answer-only, parser, or format rewards can be exploited through guessing, malformed-but-accepted answers, or other reward-hacking behavior unless the evaluator and output handling are robust.[^grpo-summary]
- Longer trajectories can create more opportunities for self-correction, which may put pressure on response length without guaranteeing proportional quality. The source recommends monitoring accuracy, length, entropy, KL, and reward-hacking behavior rather than reward alone.[^grpo-summary]

## Exploration boundary

GRPO can reinforce useful reasoning trajectories that the current policy samples, but it does not supply missing domain knowledge or detailed solutions when the base policy has essentially no chance of discovering them. Base-model capability, prompt distribution, sampling budget, verifier quality, and curriculum jointly constrain results.[^grpo-summary]

## Relationships

- **Qualifies:** [Group Relative Policy Optimization](group-relative-policy-optimization.md).
- **Shares a reward-proxy limitation with:** [InstructGPT behavioral evaluation and limitations](instructgpt-behavioral-evaluation-and-limitations.md); both require that an optimized score remain aligned with the desired behavior, though GRPO may use rule-based verifiers as well as learned rewards.[^grpo-summary]

[^grpo-summary]: “GRPO overview” (Vietnamese summary), [raw source](../raw/GRPO.md), Sections 9–10 and 13–14. This is secondary-source evidence linking to DeepSeek-AI, “DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models” (2024), DeepSeek-R1 (2025), and a cited 2025 critical-perspective paper; none has been independently ingested here.
