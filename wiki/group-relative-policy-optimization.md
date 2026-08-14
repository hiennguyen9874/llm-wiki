---
type: Concept
title: Group Relative Policy Optimization
description: GRPO is an on-policy, PPO-style LLM post-training method that replaces a learned critic with reward-normalized comparisons among multiple completions for the same prompt.
tags: [grpo, reinforcement-learning, post-training, reasoning, policy-optimization]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-14T06:56:09Z }
sources:
  - id: grpo-summary
    resource: ../raw/GRPO.md
    title: "GRPO overview (Vietnamese summary)"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
  - id: deepseek-v3-2-2025
    resource: ../raw/arXiv-2512.02556v1/main.tex
    title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
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

## DeepSeek-V2 application

DeepSeek-V2 applies GRPO in two stages: code-and-math reasoning alignment with a reasoning reward model, then preference alignment with helpfulness, safety, and rule-based reward models. Its report also describes an inference/training hybrid engine, vLLM large-batch generation, and CPU/GPU offloading, showing that critic removal does not remove rollout and systems costs.[^deepseek-v2-2024]

## DeepSeek-V3 application

DeepSeek-V3 also applies GRPO after a 1.5M-example SFT stage. Its reported rewards are rule based where answers or code can be checked and model based for free-form tasks; the reward model is trained from V3 SFT checkpoints. The authors include chains of thought in reward-model preference data to mitigate reward hacking, but this is a design claim rather than an external robustness evaluation.[^deepseek-v3-2024]

## DeepSeek-V4 specialist training

DeepSeek-V4 uses SFT followed by GRPO to create specialists for domains and reasoning-effort levels, then consolidates their capabilities through multi-teacher on-policy distillation. For harder-to-verify tasks, its report assigns trajectory evaluation to a generative reward model that is also optimized with RL. This demonstrates GRPO’s use inside a larger specialist-and-distillation pipeline; it does not validate the reward model’s judgments or solve reward-proxy risks.[^deepseek-v4-2026]

## V3.2 rollout-consistency controls

DeepSeek-V3.2 documents controls for scaling GRPO in a sparse MoE policy. Its displayed outcome advantage is mean-centered within each rollout group, $\hat A_i=R_i-\operatorname{mean}(\mathbf R)$; this is a report-specific formulation and need not match every GRPO implementation’s normalization.[^deepseek-v3-2-2025]

The report corrects its KL estimate for samples drawn from the rollout policy by including the current-to-rollout importance ratio. It masks only negative-advantage sequences whose average rollout-versus-current log-probability divergence exceeds a threshold, retaining positive sequences. It also reuses the sampled MoE routing path during training and reapplies the rollout-time top-$p$/top-$k$ truncation mask to the current policy. These controls target inference/training mismatch and off-policy drift; the source reports stability observations, not comparative ablations that establish their independent effects.[^deepseek-v3-2-2025]

## GLM-5 synchronous and asynchronous variants

GLM-5 reasoning RL retains group-standardized advantages and PPO-style clipping but multiplies updates by an IcePop-style training/inference mismatch ratio only within a bounded range, removes KL regularization, and reports group size 32. Its asynchronous agentic stage instead uses recorded rollout log-probabilities as the behavior proxy, masks tokens outside a double-sided importance interval, and drops stale trajectories. These are report-specific GRPO-derived controls for inference/training and policy-lag mismatch, not changes implied by GRPO itself.[^glm5-report-2026]

The final GLM-5 cross-stage distillation replaces reward advantage with a stopped teacher/student log-probability gap and uses group size 1. That stage reuses the surrounding optimizer machinery but no longer estimates a group-relative reward advantage, so it should be understood as on-policy distillation rather than ordinary GRPO.[^glm5-report-2026]

## Relationships

- **Applied by:** [DeepSeek-V2 alignment, evaluation, and limitations](deepseek-v2-alignment-evaluation-and-limitations.md) in a two-stage reward-model recipe and [DeepSeek-V3 post-training, evaluation, and limitations](deepseek-v3-post-training-evaluation-and-limitations.md) with rule- and model-based rewards.[^deepseek-v2-2024][^deepseek-v3-2024]
- **Related method:** [InstructGPT human-feedback alignment](instructgpt-human-feedback-alignment.md) uses KL-regularized PPO after reward-model training; GRPO likewise uses on-policy policy optimization and a reference KL constraint, but derives relative advantages from grouped completions instead of a learned critic.[^grpo-summary]
- **Qualified by:** [GRPO operational limits](grpo-operational-limits.md).
- **Applied by:** [DeepSeek-V4 post-training and evaluation limits](deepseek-v4-post-training-and-evaluation-limits.md) for specialist training before on-policy distillation.[^deepseek-v4-2026]
- **Applied by:** [DeepSeek-V3.2 post-training, agentic synthesis, and evaluation limits](deepseek-v3-2-post-training-agentic-evaluation.md), which reports rollout-consistency controls for its mixed-RL stage.[^deepseek-v3-2-2025]

[^grpo-summary]: “GRPO overview” (Vietnamese summary), [raw source](../raw/GRPO.md), Sections 1–8 and 11–12. This is secondary-source evidence linking to DeepSeek-AI, “DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models” (2024) and “DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning” (2025); the primary papers and implementation documentation have not been independently ingested here.

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Section 4.2.

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Section 6.2.

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Section 6.1.

[^deepseek-v3-2-2025]: DeepSeek-AI, “DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models,” arXiv:2512.02556v1, [source](../raw/arXiv-2512.02556v1/main.tex), Sections 3.1–3.2.

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [post-training](../raw/arXiv-2602.15763v2/3_posttrain.tex), Reasoning RL and cross-stage distillation; [agentic RL](../raw/arXiv-2602.15763v2/3.1_agenticRL.tex), asynchronous stability controls.
