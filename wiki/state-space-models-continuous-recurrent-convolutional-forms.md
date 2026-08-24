---
type: Concept
title: State-space models: continuous, recurrent, and convolutional forms
description: A linear time-invariant state-space model becomes a discrete recurrence after discretization, and the same recurrence induces an SSM convolution kernel.
tags: [sequence-modeling, s4, ssm]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T04:57:05Z }
sources:
  - id: bourdois-2024
    resource: ../raw/IntroductiontoStateSpaceModels.md
    title: "Introduction to State Space Models (SSM)"
---

# State-space models: continuous, recurrent, and convolutional forms

A linear time-invariant (LTI) state-space model maintains a latent state driven by input and read out as output. Discretizing it yields a sequential recurrence; unrolling that recurrence yields a convolution kernel. These are equivalent views of the same linear system, with different training, inference, and continuous-data trade-offs.[^bourdois-2024]

## Continuous model

With state $x(t)\in\mathbb{C}^n$, input $u(t)\in\mathbb{C}^m$, and output $y(t)\in\mathbb{C}^p$, the source gives the continuous LTI system

$$
x'(t)=Ax(t)+Bu(t),\qquad y(t)=Cx(t)+Du(t).
$$

In the deep-learning presentation, the $Du(t)$ term may instead be treated as a separately computed skip connection, leaving the state path $x'=Ax+Bu$, $y=Cx$.[^bourdois-2024]

## Discrete recurrence and convolution

The source uses trapezoidal (bilinear) discretization with step $\Delta$, defining

$$
\bar A=(I-\tfrac{\Delta}{2}A)^{-1}(I+\tfrac{\Delta}{2}A),\qquad
\bar B=(I-\tfrac{\Delta}{2}A)^{-1}\Delta B,\qquad \bar C=C.
$$

The resulting recurrence is $x_k=\bar A x_{k-1}+\bar B u_k$, $y_k=\bar Cx_k$. For a zero initial state, unrolling produces the kernel sequence $(\bar C\bar B,\ \bar C\bar A\bar B,\ldots,\ \bar C\bar A^k\bar B)$, so the output can be computed as its causal convolution with the input.[^bourdois-2024]

The source presents the recurrent form as favorable for constant-time state updates during inference and the convolutional form as parallelizable for training. It also notes that a fixed convolution kernel does not fit online/autoregressive updates as directly, while the continuous form can represent irregularly sampled continuous data but is not its efficient deep-learning execution path.[^bourdois-2024]

## S4-oriented parameterization

This educational S4 account identifies the discretization choice and the definition or initialization of $A$ as key architecture choices. It describes diagonal or normal forms as making powers of $A$ inexpensive, and presents HiPPO-based initialization and normal-plus-low-rank decomposition as the S4 approach for efficiently structured dynamics rather than arbitrary random $A$ initialization.[^bourdois-2024]

## Relationships

- **Foundation for:** [Mamba selective state spaces and architecture](mamba-selective-state-spaces-and-architecture.md), which changes fixed LTI SSM parameters into input-dependent dynamics. This lineage link is maintained synthesis.
- **Foundation for:** [Structured State Space Duality](structured-state-space-duality.md), which gives certain selective recurrences a semiseparable matrix form. This lineage link is maintained synthesis.

## Evidence limits

This is a secondary educational source centred on S4, not a primary-paper verification of S4, HiPPO, LMU, or the performance comparisons it summarizes. The source’s figures and benchmark tables are externally hosted and were not independently inspected, so this concept excludes their quantitative claims. Its discretization and efficiency discussion should not be read as a claim that all SSM variants use trapezoidal discretization or share the same training and inference behavior.

[^bourdois-2024]: Loïck Bourdois, “Introduction to State Space Models (SSM),” Hugging Face blog, source snapshot [IntroductiontoStateSpaceModels.md](../raw/IntroductiontoStateSpaceModels.md), sections “Definition of an SSM in deep learning” through “Learning matrices.”
