---
type: Concept
title: Test-time compute allocation
description: Test-time compute allocation adaptively chooses an inference budget and reasoning strategy per prompt, treating runtime compute as a capability resource distinct from model size.
tags: [test-time-scaling, inference-time-compute, adaptive-inference, reasoning, compute-allocation]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:24:25Z }
sources:
  - id: test-time-scaling-summary
    resource: ../raw/Test-TimeScaling.md
    title: Test-Time Scaling overview (Vietnamese summary)
---

# Test-time compute allocation

Test-time (or inference-time) scaling spends additional runtime compute to improve an answer rather than only scaling training data or parameter count. The supplied summary argues that the budget should be allocated adaptively—by prompt difficulty and the base model's chance of finding a useful solution—across generation, selection, verification, and refinement rather than uniformly increasing output length.[^test-time-scaling-summary]

## Allocation problem

Given a fixed inference budget, a policy can choose both a method and its budget: one answer, multiple independent trajectories, longer sequential reasoning, or verifier-guided search. Easy prompts may need little extra compute; moderate prompts can benefit from additional sampling or search; and for extremely hard prompts, more samples have limited value if the base model rarely produces a viable path.[^test-time-scaling-summary]

For independent samples with per-sample probability $p$ of a correct solution, the probability of generating at least one correct solution in $N$ samples is $1-(1-p)^N$. This improves the *candidate set*, not necessarily the final answer: the system must still select the correct candidate reliably.[^test-time-scaling-summary]

## Reported compute-optimal findings

The summary attributes to Snell et al. an adaptive strategy that chooses a method and compute budget from estimated prompt difficulty. In its reported setup, this exceeded pure best-of-$N$ by more than fourfold in compute efficiency, and a smaller model with suitable test-time compute surpassed a model reported as 14 times larger in FLOPs-matched comparison. These are experiment-specific results, conditional on a capable base model and selection mechanism, not a general parameter-count replacement rule.[^test-time-scaling-summary]

The summary also describes s1's *budget forcing*: stopping a reasoning trace early or preventing its termination and prompting it to continue (for example with “Wait”). It reports an AIME24 increase from about 50% to 57% under extended reasoning, while also reporting eventual saturation and context-window limits.[^test-time-scaling-summary]

## Operational policy

A practical adaptive-inference loop estimates uncertainty or difficulty, selects a budget and strategy, generates candidates, applies a verifier or tool where available, and stops when confidence or budget criteria are met. Quality, latency, cost per correct answer, and verifier reliability are joint objectives; raw token count or FLOPs alone is insufficient.[^test-time-scaling-summary]

## Relationships

- **Uses:** [Test-time scaling strategies and verification limits](test-time-scaling-strategies-and-verification-limits.md) for the parallel, sequential, and search mechanisms that an allocation policy selects.
- **Includes:** [Tree of Thoughts deliberate search](tree-of-thoughts-deliberate-search.md) as a search-based allocation of inference compute across intermediate reasoning states.
- **Extends:** [Chain-of-thought prompting](chain-of-thought-prompting.md) by optionally allocating more compute to a reasoning trace or to alternative traces.

[^test-time-scaling-summary]: “Test-Time Scaling overview” (Vietnamese summary), [raw source](../raw/Test-TimeScaling.md), Sections 1–6 and 8–10. This is secondary-source evidence that links to Snell et al. (arXiv:2408.03314), Wu et al. (arXiv:2408.00724), Muennighoff et al. (arXiv:2501.19393), and a 2025 survey (arXiv:2503.24235); their primary texts have not been independently ingested here.
