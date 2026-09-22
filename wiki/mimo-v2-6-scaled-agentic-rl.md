---
type: Concept
title: MiMo-V2.6 scaled agentic reinforcement learning
description: MiMo-V2.6 scales mixed-task GRPO with 25K long-horizon trajectories per step, groupwise quality grading, behavior-aware advantage shaping, router freezing, and layered reward-hacking defenses.
tags: [mimo-v2-6, agentic-rl, grpo, reward-grading, reward-hacking]
status: stable
created: 2026-09-22
generated: { by: llm-wiki-agent/1, at: 2026-09-22T15:21:59Z }
sources:
  - id: mimo-v2-6-report-2026
    resource: ../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md
    scope: ../raw/MiMo-V2.6/
    kind: paper
    title: "MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement"
---

# MiMo-V2.6 scaled agentic reinforcement learning

MiMo-V2.6 reports one asynchronous mixed-task GRPO run that scales three resources together: rollout/training compute, environment and harness diversity, and grader compute. Each step samples 1,568 prompts with 16 rollouts each—about 25K trajectories and 2.7–3.7B training tokens at up to one-million-token context—while using groupwise grading and explicit behavior controls to refine coarse outcome rewards.[^mimo-v2-6-report-2026]

## Training objective and workload

The run allocates tasks to agentic/competitive coding (68%), general tool use (12%), visual design (13%), context following (3%), and cybersecurity (4%). It uses asynchronous partial rollouts with policy staleness 4, prompt-mean loss aggregation, token-level current/rollout importance ratios, and independently entropy-tuned clipping bounds for positive and negative advantages. Dynamic sampling removes all-pass and all-fail groups.[^mimo-v2-6-report-2026]

Reported RL spend is $2.6M for Pro and $0.9M for Flash. On DeepSWE v1.1, average@3 reportedly rises from 58.4 to 72.6 for Pro and 48.7 to 65.7 for Flash as cumulative spend grows; for Pro, rollout/training/grading consume 43.8%/43.5%/12.7% of reported cost. These are author-run correlations within evolving systems, not controlled evidence that cost alone caused the gains.[^mimo-v2-6-report-2026]

## Groupwise grading

**Groupwise Reward Synthesis (GRS)** builds reusable task-specific solution and behavior rubrics from offline rollout comparisons. During training, an agent grades each rollout, and the final reward multiplies binary test success by solution and behavior scores: $R_i=R_i^{test}S_i^{sol}S_i^{beh}$. A failed test therefore remains zero, while passing solutions can differ in quality.[^mimo-v2-6-report-2026]

**Groupwise Advantage Redistribution (GAR)** applies online to mixed-outcome code groups. A grader compares all patches on approach, precision, minimality, side effects, and codebase craftsmanship; confirmed reward hacks are reset to failure. Quality factors redistribute the total positive advantage mass among passing trajectories, subject to a cap, then advantages are re-centered to zero group mean. Unusable grader output falls back to the original advantage.[^mimo-v2-6-report-2026]

A code-only Flash comparison at batch 128 reports that GAR sustains pass-rate gains through step 52 while turns stay roughly stable and token length grows gradually; the no-GAR run grows rapidly in turns and length. Maintainer audits also report smaller, more precise patches with GAR. Because the report does not give repeated seeds or full quantitative curves in text, this is suggestive author evidence rather than an isolated causal estimate.[^mimo-v2-6-report-2026]

## Behavioral regularization

A group-relative length penalty applies only to successful rollouts in groups above a pass-rate threshold, using a percentile of successful lengths as a prompt-specific reference. Segment-level rules identify format and tool-call errors: flagged tokens are masked in positive trajectories and receive amplified negative advantage in failed trajectories, while unflagged-token scaling approximately conserves positive and negative advantage mass unless clipping or empty denominators intervene.[^mimo-v2-6-report-2026]

## Reward-hacking defenses

The report describes defense in depth: correction examples during mid-training; removal of logs, patches, generated binaries, caches, and future Git history; container network isolation; iterative adversarial probing by a hack agent; offline trajectory audits during RL; and grader-side reward reset for confirmed hacks. The reported confirmed-hack share stays below 2% in the final run, but this measures detections under the authors' audit process, not the true prevalence of undetected exploitation.[^mimo-v2-6-report-2026]

Environment verification is domain-specific. Coding tasks combine specification–test review, four-rollout auditing, and eight repeated executions of reference checks. General-agent tasks use local resettable mocks, atomic rule/LLM rubrics, repeated judges, and adversarial solutions. Cyber vulnerability reproduction matches sanitizer vulnerability type and topmost project-level crash location rather than relying on patched-binary difference or unstable LLM judgment.[^mimo-v2-6-report-2026]

## Router stability and post-RL consolidation

With a trainable Pro router, decoder-layer-9 load CV reportedly rises from 0.78 to 2.0, peak load from 6× to 16× mean, and cold experts from 0.5% to 22% over 20 steps. Restoring only initial router parameters recovers load balance without changing benchmark performance; freezing the router keeps the tracked statistics approximately flat. This is a stronger intervention than a simple correlation, but remains one reported layer and training setup.[^mimo-v2-6-report-2026]

After mixed RL, Multi-Prefix Multi-Teacher On-Policy Distillation (MOPD2) combines domain teachers. Standard MOPD supervises autonomous student rollouts, while prefix-conditioned variants start a student turn from teacher-rollout or SFT-demonstration history and distill teacher token probabilities on the student's continuation. This broadens supervision to domains where reliable RL rewards are difficult, but attribution between RL and subsequent distillation is not available from final benchmark scores.[^mimo-v2-6-report-2026]

## Relationships

- **Extends:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) with asynchronous mixed-task collection, report-specific clipping, GRS/GAR, and segment-level shaping.
- **Qualified by:** [GRPO operational limits](grpo-operational-limits.md), especially group variance, coarse credit, rollout cost, and reward-proxy risk.
- **Depends on:** [MiMo-V2.6 omni-modal hybrid-SWA architecture](mimo-v2-6-omnimodal-hybrid-swa-architecture.md).
- **Uses:** [MiMo-V2.6 RL infrastructure and evidence limits](mimo-v2-6-rl-infrastructure-and-evidence-limits.md) for collection, consistency, and long-context execution.

## Evidence limits

All mechanisms, interventions, and results are reported by the model developer. Public and internal benchmarks are mixed; configurable baselines use maximum reasoning effort, but complete prompts, harness versions, token budgets, variance, and contamination analysis are not supplied. The final Pro/Flash results follow RL plus MOPD2, so they do not isolate either stage. The package contains no executable environment, framework, checkpoint, or evaluation configuration with which to reproduce the report.[^mimo-v2-6-report-2026]

[^mimo-v2-6-report-2026]: Xiaomi LLM-Core, “MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement,” [technical report](../raw/MiMo-V2.6/MiMo_V2_6_technical_report.md), Sections 4–5, Equations 1–5, Tables 2–3, and Figures 3, 6–13.
