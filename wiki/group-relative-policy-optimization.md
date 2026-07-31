---
type: Concept
title: Group Relative Policy Optimization
description: GRPO is an on-policy, PPO-style LLM post-training method that replaces a learned critic with reward-normalized comparisons among multiple completions for the same prompt.
tags: [grpo, reinforcement-learning, post-training, reasoning, policy-optimization]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:12:59Z }
sources:
  - id: grpo-summary
    resource: ../raw/GRPO.md
    title: "GRPO overview (Vietnamese summary)"
---

# Group Relative Policy Optimization

Group Relative Policy Optimization (GRPO) is an on-policy reinforcement-learning method for LLM post-training. For each prompt, it samples a group of completions, scores them, and uses each completion’s reward relative to that group as its policy-gradient advantage. This replaces the learned value/critic model commonly used in PPO-style RL with a prompt-dependent Monte Carlo baseline, while retaining clipped importance-ratio updates and a reference-policy KL penalty.[^grpo-summary]

## Group-relative advantage

For a prompt $q$, an old policy samples $G$ completions $o_1,\ldots,o_G$ and a reward function assigns $r_i=r(q,o_i)$. In the outcome-supervision form described by the source, GRPO standardizes reward within that prompt’s group:

$$
\hat A_i = \frac{r_i-\operatorname{mean}(r_1,\ldots,r_G)}{\operatorname{std}(r_1,\ldots,r_G)+\delta}.
$$

Completions above the group mean receive positive advantage and those below it receive negative advantage. The baseline is prompt-dependent, so a reward is judged relative to alternative attempts at the same problem rather than against rewards from prompts of potentially different difficulty.[^grpo-summary]

With outcome rewards, the same $\hat A_i$ is normally assigned to every completion token. The source also describes process-supervision variants that can supply rewards and advantages at reasoning-step granularity.[^grpo-summary]

## PPO-style update without a critic

At each completion token, GRPO compares the current policy with the rollout policy through an importance ratio $\rho_{i,t}=\pi_\theta/\pi_{\theta_{\mathrm{old}}}$. It maximizes the clipped PPO surrogate

$$
\min\!\left(\rho_{i,t}\hat A_{i,t},\operatorname{clip}(\rho_{i,t},1-\epsilon,1+\epsilon)\hat A_{i,t}\right)
$$

and penalizes divergence from a fixed reference policy with a KL term. Thus GRPO’s useful informal description is group-normalized REINFORCE plus PPO-style clipping and KL control; it is not simply PPO with a component deleted.[^grpo-summary]

A typical iteration samples $G$ diverse completions per prompt, evaluates rewards from a reward model or verifier, normalizes rewards independently within each group, masks and averages token-level loss over completions, and performs one or more updates before collecting fresh rollouts.[^grpo-summary]

## Reasoning and verifier-oriented use

The source presents GRPO as introduced in DeepSeekMath and later used in DeepSeek-R1-Zero and DeepSeek-R1 training. It is especially compatible with tasks whose outputs have checkable signals, such as mathematical answers, code tests, symbolic verification, and output-format checks. For DeepSeek-R1-Zero, the source reports accuracy and format rewards and describes a pipeline that later combined cold-start SFT, reasoning RL, rejection sampling plus SFT, and general RL; GRPO was therefore one component rather than the complete training recipe.[^grpo-summary]

## Relationships

- **Related method:** [InstructGPT human-feedback alignment](instructgpt-human-feedback-alignment.md) uses KL-regularized PPO after reward-model training; GRPO likewise uses on-policy policy optimization and a reference KL constraint, but derives relative advantages from grouped completions instead of a learned critic.[^grpo-summary]
- **Qualified by:** [GRPO operational limits](grpo-operational-limits.md).

[^grpo-summary]: “GRPO overview” (Vietnamese summary), [raw source](../raw/GRPO.md), Sections 1–8 and 11–12. This is secondary-source evidence linking to DeepSeek-AI, “DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models” (2024) and “DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning” (2025); the primary papers and implementation documentation have not been independently ingested here.
