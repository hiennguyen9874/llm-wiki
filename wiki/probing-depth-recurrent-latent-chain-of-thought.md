---
type: Concept
title: Probing depth-recurrent latent chain-of-thought
description: In one probe study of Huginn-3.5B, recurrence depth did not yield clear rank-trajectory evidence of latent chain-of-thought and gave only small no-CoT GSM8K gains.
tags: [chain-of-thought, depth-recurrence, mechanistic-interpretability, reasoning]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:17:57Z }
sources:
  - id: lu2025latent
    resource: ../raw/arXiv-2507.02199v2/colm2025_conference.tex
    title: "Latent Chain-of-Thought? Decoding the Depth-Recurrent Transformer"
---

# Probing depth-recurrent latent chain-of-thought

A probe study of the depth-recurrent Huginn-3.5B transformer finds little evidence that its hidden-state token-rank trajectories implement structured latent chain-of-thought (CoT) on arithmetic tasks when explicit CoT is suppressed. Increasing recurrent steps gave modest no-CoT GSM8K gains that remained far below the paper's explicit-CoT result; these are results for this model, prompting setup, and probes, not a general disproof of latent reasoning.[^lu2025latent]

## Method and probe validity

- Huginn uses two prelude blocks, four recurrent blocks reused for each recurrent step, and two coda blocks. The authors unroll this computation and decode hidden states with both a logit lens and a *coda lens*, which passes a state through the model's learned two-block coda before unembedding.[^lu2025latent]
- On 100 one-digit composite-arithmetic questions, decoded final-token ranks oscillated strongly by recurrent-block position. In particular, the logit lens made $R_4$ outputs largely non-numeric/uninterpretable, while the coda lens made those outputs predominantly numeric; other blocks exhibited the opposing pattern.[^lu2025latent]
- The paper therefore concludes that lens applicability must be established per layer in this architecture, rather than treating an intermediate-state decoder as uniformly faithful.[^lu2025latent]

## Reported evidence on latent CoT

- The authors selected 67 correctly answered arithmetic examples whose distinct intermediate and final results were single tokens. At logit-lens $R_3$ and coda-lens $R_4$—the selected interpretable block positions—both intermediate and final-token ranks improved early in recurrence without the predicted delayed final-token improvement. They interpret the missing phase separation as little evidence for a stepwise latent-CoT trajectory.[^lu2025latent]
- A rank reversal near recurrence step 6 appeared in most examples, which the authors identify as a possible re-evaluation signal rather than establish as evidence of latent CoT.[^lu2025latent]
- With explicit CoT suppressed in an 8-shot GSM8K evaluation, accuracy rose from 3.11% at 4 recurrent steps to 4.93% at 32 steps and plateaued at the tested higher depths. The paper reports 24.87% strict and 38.13% flexible accuracy for Huginn with explicit CoT at 64 steps, compared with 4.70%/4.70% without it at 64 steps.[^lu2025latent]

## Trust boundary and limitations

The work examines one 3.5B depth-recurrent model, selected arithmetic probes, and rank-based decoders. Its negative result does not rule out a more distributed or subtler latent computation; the authors propose methods such as activation patching for further investigation. The GSM8K comparison changes prompting as well as the availability of explicit CoT, so it supports the reported practical gap in this setup rather than isolating a causal effect of recurrence alone.[^lu2025latent]

[^lu2025latent]: Lu et al., *Latent Chain-of-Thought? Decoding the Depth-Recurrent Transformer*, source manuscript, abstract, §§2–3, and appendix (2025).