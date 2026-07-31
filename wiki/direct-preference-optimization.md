---
type: Concept
title: Direct Preference Optimization
description: DPO directly trains a policy on chosen–rejected response pairs by classifying their reference-relative log-probability gap, avoiding a separate reward model and online PPO loop.
tags: [dpo, preference-optimization, rlhf, alignment, post-training]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:08:36Z }
sources:
  - id: dpo-summary
    resource: ../raw/DPO.md
    title: "DPO overview (Vietnamese summary)"
---

# Direct Preference Optimization

Direct Preference Optimization (DPO) post-trains a policy directly from preference triples $(x,y_w,y_l)$, where $y_w$ is preferred to $y_l$. Its logistic loss raises the policy’s probability of the chosen completion relative to both the rejected completion and a frozen reference policy; this replaces separate reward-model fitting and PPO optimization with teacher-forced likelihood training.[^dpo-summary]

## Objective and derivation

For the KL-regularized reward objective used in RLHF, the source gives the optimal policy as

$$
\pi_r(y\mid x) \propto \pi_{\mathrm{ref}}(y\mid x)\exp(r(x,y)/\beta).
$$

Rearranging expresses reward, up to a prompt-specific partition term, through the policy/reference log ratio:

$$
\hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}.
$$

Under a Bradley–Terry preference model, that partition term cancels when comparing completions for the same prompt. DPO therefore minimizes

$$
-\mathbb{E}\left[\log\sigma\left(\beta\left[
\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-
\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}
\right]\right)\right].
$$

This is not merely increasing $\log\pi_\theta(y_w\mid x)$ and decreasing $\log\pi_\theta(y_l\mid x)$: it favors a larger **change from the reference** for the chosen completion. The source describes the reference-relative ratio as an implicit reward model.[^dpo-summary]

## Training procedure

1. Start with an instruction-following SFT checkpoint; initialize the trainable policy and frozen reference from it.
2. Collect preference pairs, from people, AI feedback, verifiers, or another ranking source.
3. Sum token log-probabilities over response tokens (masking prompt tokens) for chosen and rejected completions under both models.
4. Apply the DPO logistic loss and update only the policy. Reference log-probabilities may be precomputed only if the reference and tokenization remain unchanged.[^dpo-summary]

The temperature-like coefficient $\beta$ is the KL-regularization coefficient in the derivation and also scales the loss logit. Its useful value depends on data noise, optimization choices, sequence length, and the policy/reference/data distributions; the source cautions against treating a smaller value as uniformly better.[^dpo-summary]

## Relationship to SFT and PPO-RLHF

SFT learns only to imitate chosen completions, while DPO also learns the observed preference boundary against rejected completions. Unlike PPO-based RLHF, DPO needs no separate reward or value model and does not generate on-policy responses during each training update. PPO can instead support iterative, online feedback and optimization over newly sampled outputs; DPO is principally an offline preference-optimization method.[^dpo-summary]

## Relationships

- **Alternative to:** [InstructGPT human-feedback alignment](instructgpt-human-feedback-alignment.md); DPO replaces its reward-model-plus-PPO stage with direct pairwise policy optimization, while both commonly follow SFT and use a frozen reference.[^dpo-summary]
- **Alternative to:** [Odds Ratio Preference Optimization](odds-ratio-preference-optimization.md); ORPO combines chosen-response NLL with an odds-ratio preference loss and has no frozen reference policy, whereas DPO optimizes a reference-relative likelihood gap.[^orpo-summary]
- **Qualified by:** [DPO operational limits](dpo-operational-limits.md), which records data, distribution, and evaluation limits.

[^dpo-summary]: “DPO overview” (Vietnamese summary), [raw source](../raw/DPO.md), Sections 1–12 and 16. This is secondary-source evidence that links to Rafailov et al., “Direct Preference Optimization: Your Language Model is Secretly a Reward Model,” NeurIPS 2023; the primary paper has not been independently ingested here.

[^orpo-summary]: “ORPO overview” (Vietnamese summary), [raw source](../raw/ORPO.md), Sections 1, 3, 6, 9–10, and 13. This is secondary-source evidence linking to Hong, Lee, and Thorne, “ORPO: Monolithic Preference Optimization without Reference Model,” EMNLP 2024; the primary paper has not been independently ingested here.
