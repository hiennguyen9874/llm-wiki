---
type: Concept
title: Adaptive-depth trajectory–readout diagnostics
description: A controlled study attributes looped-transformer early-exit quality to both depth-supervised trajectory formation and exit readout, finding fixed-prior trajectories and simple post-hoc signals competitive with jointly trained gates.
tags: [adaptive-computation, early-exit, looped-transformers, reasoning, trajectory]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:59:36Z }
sources:
  - id: popescu2026adaptive
    resource: ../raw/arXiv-2607.20519v1/main.tex
    title: "Adaptive Depth in Looped Transformers: Diagnosing Learned Halting Gates and Trajectory Readouts"
---

# Adaptive-depth trajectory–readout diagnostics

This study separates adaptive depth into **trajectory formation** (which recurrent states become useful under the training loss) and **exit readout** (how inference chooses a state). In its controlled tasks, fixed, input-independent depth-loss priors produce trajectories on which confidence signals can make earlier exits than jointly trained PonderNet-style gates; frozen-trajectory gate fitting supports the authors' diagnosis that the joint objective's induced trajectory, rather than gate capacity alone, limits those gates.[^popescu2026adaptive]

## Decomposition and methods

- A learned gate produces an exit distribution that both weights the loss at each recurrent depth during training and selects the inference exit. The authors argue that this couples the readout to the trajectory it is supposed to read.[^popescu2026adaptive]
- Their fixed-prior alternative trains the shared recurrent block with a uniform or truncated geometric distribution of per-depth losses, but does not train an input-dependent halting policy. A post-hoc readout then exits using confidence (entropy, maximum probability, or logit margin) or convergence (prediction, logit, or hidden-state change) signals.[^popescu2026adaptive]
- They use forced exits at every loop to distinguish per-depth trajectory quality from the quality of an adaptive stopping rule, and calibrate post-hoc thresholds on held-out validation data before test evaluation.[^popescu2026adaptive]

## Reported controlled evidence

- On three-seed MANO modular-arithmetic experiments with six recurrent loops, a geometric fixed prior ($\lambda=0.3$) plus confidence readouts reached 99% test accuracy at roughly 1.5 average loops. The reported learned linear and MLP gates did not reach 99% in the summarized comparison, and required more average loops at the lower target accuracies.[^popescu2026adaptive]
- Fixed-prior prediction-space signals tracked MANO difficulty: harder expressions remained higher-entropy and lower-margin for more loops. The source reports the pattern also beyond MANO's training operation count and in a smaller parity diagnostic; these are trajectory diagnostics, not evidence of general language-model difficulty estimation.[^popescu2026adaptive]
- Training new linear or MLP gates on frozen fixed-prior trajectories recovered strong early-exit behavior, whereas fitting new gates over trajectories produced by joint gate training did not improve their frontier. This isolates the reported effect within the study's objectives and models, but does not establish a general causal mechanism for all learned halting methods.[^popescu2026adaptive]

## Evaluation on pretrained Ouro

Without retraining, the authors apply the same readout comparison to Ouro-1.4B and Ouro-2.6B over six multiple-choice benchmarks. In their 12 model--benchmark comparisons, the selected post-hoc readout had higher held-out accuracy in five, lower average loop count in seven, and both in three; the best heuristic varied by model and benchmark. The paper therefore supports that Ouro's ponder gate was not uniformly Pareto-optimal in this evaluation, not that a fixed heuristic generally dominates learned gates. Several differences are small and are reported on single runs.[^popescu2026adaptive]

The source also reports end-to-end latency measurements on an RTX 5070 Ti. For one MANO fixed-prior model, confidence exits preserved 100% accuracy while reducing six loops to 1.26 average loops and reported 1.29--1.36$\times$ speedups. Ouro-1.4B operating points likewise reported 1.24--1.58$\times$ speedups, but these are hardware-, batch-, and implementation-specific measurements.[^popescu2026adaptive]

## Trust boundary and limitations

The central trajectory--readout explanation is a source-supported interpretation of controlled synthetic-task and frozen-trajectory results, rather than a proven universal account of adaptive computation. The large-model component evaluates released Ouro checkpoints rather than retraining them with fixed-prior supervision; its benchmarks, threshold grids, splits, and latency environment are source-controlled. It establishes competitive alternative readouts in those settings, not general deployment gains or a replacement for trained gates.[^popescu2026adaptive]

## Relationships

- Evaluates: [Ouro looped language models](ouro-looped-language-models.md) — it compares Ouro's pretrained ponder gate with post-hoc confidence and convergence readouts while keeping the checkpoints fixed.[^popescu2026adaptive]
- Related to: [Loop-boundary early exit in looped language models](loop-boundary-early-exit-in-looped-language-models.md) — both assess non-gate early exits, but this study trains and diagnoses recurrent trajectories and reports latency, whereas the other uses entropy exits at loop boundaries and reports nominal FLOP savings.
- Related to: [Mixture-of-Recursions adaptive token computation](mixture-of-recursions-adaptive-token-computation.md) — both allocate recurrent computation adaptively, but this study diagnoses whole-input exit depth rather than MoR's token-level routing and cache policies.

[^popescu2026adaptive]: Popescu, Sáez de Ocáriz Borde, and Liò, *Adaptive Depth in Looped Transformers: Diagnosing Learned Halting Gates and Trajectory Readouts*, source manuscript, abstract, §§3--6, and appendices (arXiv:2607.20519v1, 2026).