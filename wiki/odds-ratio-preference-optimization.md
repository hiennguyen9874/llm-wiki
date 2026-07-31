---
type: Concept
title: Odds Ratio Preference Optimization
description: ORPO jointly optimizes chosen-response likelihood and an odds-ratio preference loss, enabling one-stage preference post-training without a reward or frozen reference model.
tags: [orpo, preference-optimization, alignment, post-training, supervised-fine-tuning]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:10:54Z }
sources:
  - id: orpo-summary
    resource: ../raw/ORPO.md
    title: "ORPO overview (Vietnamese summary)"
---

# Odds Ratio Preference Optimization

Odds Ratio Preference Optimization (ORPO) trains directly on preference triples $(x,y_w,y_l)$ by combining next-token likelihood for the chosen response $y_w$ with a loss that increases its odds relative to the rejected response $y_l$. The supplied summary presents this as a monolithic alternative to an SFT-then-DPO pipeline: it uses neither a separately fitted reward model nor a frozen reference policy.[^orpo-summary]

## Objective

For a length-normalized response probability $P_\theta(y\mid x)$, ORPO minimizes

$$
\mathcal L_{\mathrm{ORPO}} = \mathbb E_{(x,y_w,y_l)}\left[\mathcal L_{\mathrm{SFT}}+\lambda\mathcal L_{\mathrm{OR}}\right],
$$

where the SFT term is the chosen-response token negative log-likelihood and $\lambda$ controls the preference term. The summary defines odds as

$$
\operatorname{odds}_\theta(y\mid x)=\frac{P_\theta(y\mid x)}{1-P_\theta(y\mid x)}
$$

and gives the preference loss as

$$
\mathcal L_{\mathrm{OR}}=-\log\sigma\left(\log\frac{\operatorname{odds}_\theta(y_w\mid x)}{\operatorname{odds}_\theta(y_l\mid x)}\right).
$$

Thus SFT supplies an absolute signal to imitate $y_w$, while the odds-ratio term supplies a relative signal to rank it over $y_l$. The summary reports a pilot observation motivating the latter: SFT on chosen responses can raise log-probabilities of both chosen and rejected answers, rather than explicitly separating them.[^orpo-summary]

## Training and comparison with DPO

Each batch contains `prompt`, `chosen`, and `rejected` fields. Training masks prompt tokens, computes length-normalized response log-probabilities for both completions, applies NLL to the chosen completion, then applies the odds-ratio logistic loss. Implementations must handle padding, response-length normalization, and numerical stability in $\log(1-P_\theta)$.[^orpo-summary]

Unlike DPO, ORPO has no reference-policy log-probabilities to compute and incorporates the chosen-response SFT term in the same objective. The source therefore characterizes it as trainable from a base model in one stage, whereas DPO commonly starts from an SFT checkpoint and uses a frozen reference. In a conceptual per-pair accounting, ORPO needs policy evaluations of chosen and rejected responses only, versus policy and reference evaluations for both in DPO; this reduces model-memory requirements but does not imply a fixed 50% end-to-end training-time reduction.[^orpo-summary]

## Relationships

- **Alternative to:** [Direct Preference Optimization](direct-preference-optimization.md); both optimize winner–loser preference pairs without a reward model or PPO, but ORPO uses chosen-response NLL plus an odds ratio rather than DPO’s reference-relative ratio.[^orpo-summary]
- **Alternative to:** [InstructGPT human-feedback alignment](instructgpt-human-feedback-alignment.md); ORPO removes that workflow’s reward-model and PPO stages while retaining preference-supervised post-training.[^orpo-summary]
- **Qualified by:** [ORPO operational limits](orpo-operational-limits.md).

[^orpo-summary]: “ORPO overview” (Vietnamese summary), [raw source](../raw/ORPO.md), Sections 1–10, 13, and 15–17. This is secondary-source evidence linking to Hong, Lee, and Thorne, “ORPO: Monolithic Preference Optimization without Reference Model,” EMNLP 2024; the primary paper and implementation documentation have not been independently ingested here.
