---
type: Concept
title: Parcae recurrence scaling laws
description: Small-scale Parcae experiments fit compute-optimal training recurrence and tokens with power laws and test-time loss with a training-depth-conditioned saturating exponential.
tags: [compute-scaling, recurrent-depth, scaling-laws, test-time-compute]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T04:08:40Z }
sources:
  - id: prairie2026parcae
    resource: ../raw/arXiv-2604.12946v1/main.tex
    title: "Parcae: Scaling Laws For Stable Looped Language Models"
---

# Parcae recurrence scaling laws

In source-controlled 140M and 370M Parcae experiments, recurrence acts as a useful training-compute allocation axis at fixed stored parameters: fitted isoFLOP optima increase both mean recurrence and training tokens as budgets grow. At inference, validation loss approaches a finite floor with additional loops and is fit better by a saturating exponential than tested power-law alternatives. These are empirical fits over a small architecture and budget grid, not established universal scaling laws.[^prairie2026parcae]

## Compute-optimal training allocation

- The isoFLOP sweep varies mean training recurrence over $\{2,4,6,8,10,12\}$ while reducing tokens to hold estimated training FLOPs fixed. It covers six budgets from $10^{18}$ to $64\times10^{18}$ FLOPs for 140M models and three from $32\times10^{18}$ to $128\times10^{18}$ for 370M models, totaling 54 looped runs plus fixed-depth controls.[^prairie2026parcae]
- Parabolic fits to each budget produce optimal recurrence exponents of approximately $0.40$ at 140M and $0.38$ at 370M, and optimal-token exponents of $0.77$ and $0.78$. The source therefore interprets recurrence and data as jointly increasing allocations rather than spending all added compute on tokens.[^prairie2026parcae]
- A Chinchilla-style parametric fit replaces stored parameter count with the parameter count of an untied unrolling, $N(\mu_{\mathrm{rec}})$: $\widehat L_{\mathrm{train}}=E+A N(\mu_{\mathrm{rec}})^{-a}+B D^{-b}$. It predicts held-out 140M and 370M validation losses within 1.3% and 0.8%, respectively.[^prairie2026parcae]
- The fitted optimal recurrence frontier has lower validation loss than the source’s fixed-depth Parcae controls. Downstream Core/Core-Extended gains are mixed at smaller budgets and favor optimal looping more consistently at larger tested budgets, so lower fitted loss should not be read as uniform task-level dominance.[^prairie2026parcae]

The FLOP estimate distinguishes recurrence steps with and without gradient computation: $C=(2\hat N_1+6\hat N_2)D$, plus estimated attention cost. It is an analytical compute estimate, not measured accelerator time or energy, and “effective parameters” represent repeated computation rather than additional stored capacity.[^prairie2026parcae]

## Test-time saturation

- Models trained on 11.2B tokens at mean recurrence $2$–$12$ were evaluated through test-time depth 24. Across those curves, the source’s three-parameter saturating exponential $L(T)=L_\infty+Ze^{-zT}$ fit better than shifted and unshifted power-law alternatives both on all points and when extrapolating beyond training recurrence.[^prairie2026parcae]
- For 140M–1.3B end-to-end models trained at mean recurrence eight, perplexity and aggregate benchmark scores largely plateau near that depth. Extra test-time loops therefore approach a training-determined ceiling rather than providing unbounded depth extrapolation.[^prairie2026parcae]
- The fitted floor $L_\infty$ closely matches loss at the mean training recurrence. Conditioning the decay rate on $T/\mu_{\mathrm{rec}}$ supports a unified fit whose floor comes from the training law; on held-out 140M and 370M runs it reports 0.85–1.31% average prediction error, falling to 0.10–0.17% when given the empirical floor.[^prairie2026parcae]

The manuscript notes that exponential loss decay is consistent with convergence in stable linear systems, but labels that connection speculative. The fit does not establish that hidden-state convergence causes the observed loss curve.[^prairie2026parcae]

## Scope and trust boundary

The training-law evidence spans only two stored model sizes and a limited recurrence range; the 770M and 1.3B models test end-to-end quality and saturation but not the isoFLOP law. Fits use one architecture, data/training recipes derived from nanochat, source-generated evaluation, and no reported independent replication. Extrapolation to larger budgets, different loop placement, sparse models, latency-constrained serving, or jointly scaling stored parameters remains unknown.[^prairie2026parcae]

## Relationships

- Depends on: [Parcae stable looped transformers](parcae-stable-looped-transformers.md) — the scaling grid relies on Parcae’s constrained dynamics and variable-depth training recipe.
- Contrasts with: [Loss scaling for looped language models](loss-scaling-for-looped-language-models.md) — that Ouro study varies stored parameters, data, and maximum recurrence on a fixed-token grid, whereas Parcae directly searches recurrence–data allocations under estimated isoFLOP budgets and models inference saturation.

[^prairie2026parcae]: Prairie et al., *Parcae: Scaling Laws For Stable Looped Language Models*, source manuscript, abstract; §4; appendices “FLOP Estimate of Parcae,” “Expanded Setup For Training and Test-Time Scaling Laws,” “Fitting a Parametric Function for Looping,” and “Fitting Parametric Functions to Test-Time Looping” (arXiv:2604.12946v1, 2026).
