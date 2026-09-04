---
type: Concept
title: Ouro looped language models
description: Ouro applies a shared transformer stack recurrently and learns an early-exit distribution; the source reports parameter-efficient pretrained models but also exposes training, serving, and comparison limits.
tags: [adaptive-computation, kv-cache, parameter-sharing, recursive-transformers, reasoning]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:59:36Z }
sources:
  - id: zhu2025ouro
    resource: ../raw/arXiv-2510.25741v5/paper.tex
    title: "Scaling Latent Reasoning via Looped Language Models"
  - id: huang2026looped
    resource: ../raw/TowardsLoopedModelsDoneRight.md
    title: "Towards Looped Models Done Right"
  - id: popescu2026adaptive
    resource: ../raw/arXiv-2607.20519v1/main.tex
    title: "Adaptive Depth in Looped Transformers: Diagnosing Learned Halting Gates and Trajectory Readouts"
---

# Ouro looped language models

Ouro is a decoder-only Looped Language Model (LoopLM): it reapplies a shared stack of transformer blocks up to a maximum recurrence depth and predicts an exit distribution for adaptive inference. The source reports that its 1.4B and 2.6B, four-round models are competitive with selected larger open baselines after 7.7T-token pretraining, but differing training-token budgets and source-controlled evaluation constrain those comparisons.[^zhu2025ouro]

## Architecture and training

- Applying the same depth-$L$ stack $t$ times produces the $t$-round model; $t=1$ is the corresponding non-looped model. Ouro's 1.4B configuration has 24 base layers and its 2.6B configuration has 48; both generally train and evaluate at at most four rounds.[^zhu2025ouro]
- A per-token exit gate at each round induces a distribution over exit depths. Pretraining minimizes expected next-token loss under that distribution plus an entropy term, equivalent to KL regularization toward a uniform depth prior. At inference, a Q-exit threshold chooses the first round whose cumulative exit probability reaches the threshold.[^zhu2025ouro]
- The authors then freeze the language model and train the gate against a detached, per-token label derived from the marginal loss improvement of another loop. In their MMLU curve, this specialized gate reportedly reached about 66% at 2.5 average rounds versus about 64% for the jointly pretrained gate; the figure is a source-controlled trade-off, not an independent systems benchmark.[^zhu2025ouro]
- An initial eight-round pretraining phase showed loss spikes and gradient oscillations, so later stages used four rounds. The 2.6B model was formed by duplicating the 24-layer model's layers before continued training; this is a reported recipe rather than evidence that recurrence is generally stable or that upcycling is generally smooth.[^zhu2025ouro]

## Reported deployment findings

- During prompt prefilling, the source reports that each recurrence needs a separate KV cache; reusing one caused more than a 10-point GSM8K loss. During autoregressive decoding, keeping only the final-round cache gave 78.85 GSM8K and 80.40 MATH-500 versus 78.92 and 82.40 for four full caches, while reducing cache memory fourfold. First-round-only reuse failed badly.[^zhu2025ouro]
- Post-SFT reinforcement-learning attempts did not improve the final SFT checkpoint. The authors attribute one failure mode to fixed-path vLLM/SGLang rollouts being incompatible with variable-depth execution; this is an operational constraint in their implementation, not a proof of incompatibility for all RL systems.[^zhu2025ouro]

## Reported capability evidence

- The four-round 1.4B base model scored 67.35 MMLU, 71.02 BBH, 78.92 GSM8K, and 82.40 MATH500 in the source's base evaluation. Its four-round 2.6B counterpart scored 74.60, 80.46, 81.58, and 90.85, respectively.[^zhu2025ouro]
- On the source's reasoning-model comparison, Ouro-2.6B-Thinking at four rounds reported 76.4 on OlympiadBench and 39.0 on BeyondAIME, versus 75.3 and 38.0 for its listed Qwen3-8B baseline. Evaluation uses an in-house harness, an LLM-as-judge protocol, and fixed sampling; these results should not be read as a general model ranking.[^zhu2025ouro]

## Later controlled architecture comparison

A separate 2026 living article compares full-stack Ouro-style recurrence with a Huginn-style prelude–recurrent-core–coda design while matching stored parameter scale, logical depth, and training-token budgets. It reports that the sandwich envelope and persistent input access account for most of the latter design's gains, while random recurrent-state initialization has mixed effects. This is source-reported comparative evidence from a preliminary living article, not a revision of Ouro's original adaptive-exit results.[^huang2026looped]

## External readout evaluation

A subsequent source evaluates the released 1.4B and 2.6B Ouro checkpoints without retraining and compares their ponder gates with post-hoc confidence and convergence readouts. In that source's 12 model--benchmark comparisons, post-hoc readouts had higher held-out accuracy in five, used fewer average loops in seven, and improved both in three. This shows that the pretrained gate was not uniformly Pareto-optimal under its source-controlled thresholds and benchmarks; several differences are small and reported on single runs, so it does not establish that heuristics generally outperform learned gates.[^popescu2026adaptive]

## Trust boundary and limitations

The paper compares models trained with substantially different data budgets (for example, Ouro's 7.7T tokens versus listed Qwen and Gemma baselines ranging from 4T to 36T), as well as different model families and post-training. It therefore supports the reported measurements, not a controlled causal estimate of recurrence's parameter efficiency.[^zhu2025ouro]

Benchmark performance generally peaks at or near the trained four-round depth and then degrades for the reported base and thinking models. Adaptive depth changes inference compute but does not eliminate the prefill-cache cost.[^zhu2025ouro]

## Relationships

- Contrasts with: [Controlled looped-model architecture ablations](controlled-looped-model-architecture-ablations.md) — its source isolates the effects of moving from full-stack Ouro-style recurrence to a Huginn-style sandwich, rather than evaluating Ouro's adaptive exit design.[^huang2026looped]
- Related to: [Mixture-of-Recursions adaptive token computation](mixture-of-recursions-adaptive-token-computation.md) — both combine recurrent weight sharing with adaptive depth and cache design, but Ouro's exit gate is trained on loss improvement rather than MoR's routing scheme.
- Evaluated by: [Adaptive-depth trajectory–readout diagnostics](adaptive-depth-trajectory-readout-diagnostics.md) — a subsequent study compares this model family's pretrained gate with post-hoc readouts on fixed released checkpoints.[^popescu2026adaptive]
- Uses: [Loss scaling for looped language models](loss-scaling-for-looped-language-models.md) — the same source separately studies loss and performance trends by recurrence depth.
- Explores: [Recurrence and parametric knowledge manipulation](recurrence-and-parametric-knowledge-manipulation.md) — the source's proposed explanation for its recurrent-model gains.

[^zhu2025ouro]: Zhu et al., *Scaling Latent Reasoning via Looped Language Models*, source manuscript, abstract, §§3–5 and appendices (arXiv:2510.25741v5, 2025).
[^huang2026looped]: Huang et al., *Towards Looped Models Done Right*, living article, §§1–4 and conclusion (dated July 31, 2026; compiled from `raw/TowardsLoopedModelsDoneRight.md`).
[^popescu2026adaptive]: Popescu, Sáez de Ocáriz Borde, and Liò, *Adaptive Depth in Looped Transformers: Diagnosing Learned Halting Gates and Trajectory Readouts*, source manuscript, §§3–6 and appendices (arXiv:2607.20519v1, 2026).