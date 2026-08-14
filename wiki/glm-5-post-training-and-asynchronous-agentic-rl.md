---
type: Concept
title: GLM-5 post-training and asynchronous agentic RL
description: GLM-5 progresses through SFT and reasoning, agentic, and general RL before cross-stage distillation, using asynchronous rollouts and explicit controls for policy, tokenization, DSA, and environment mismatch.
tags: [glm-5, post-training, reinforcement-learning, agents, grpo, asynchronous-systems]
status: stable
created: 2026-08-14
generated: { by: llm-wiki-agent/1, at: 2026-08-14T06:56:09Z }
sources:
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
---

# GLM-5 post-training and asynchronous agentic RL

GLM-5 applies multi-task SFT, reasoning RL, agentic RL, and general RL, then uses on-policy cross-stage distillation to recover skills degraded by sequential optimization. Its distinctive agentic contribution is a decoupled rollout/training design paired with controls for stale policies, exact sampled tokens, sparse-attention selection, failed environments, and long-context KV locality.[^glm5-report-2026]

## Progressive post-training

SFT covers general chat, reasoning, coding, and agents at up to 202,752 tokens. The chat format supports reasoning before each response/tool call, preservation of prior thinking blocks across turns, and per-turn thinking control. Agent trajectories retain erroneous segments but mask them from loss, exposing correction context without directly reinforcing the failed action.[^glm5-report-2026]

Reasoning RL mixes math, science, code, and tool-integrated reasoning. Its GRPO-derived loss uses IcePop-style training/inference mismatch filtering, removes KL regularization, and reports group size 32, batch size 32, mismatch bound $\beta=2$, and asymmetric PPO clipping at 0.2/0.28. For DSA, deterministic `torch.topk` replaces nondeterministic index selection and indexer parameters are frozen; the report says nondeterministic alternatives caused rapid entropy and performance collapse, but provides no controlled curves.[^glm5-report-2026]

General RL combines rule-based rewards, outcome reward models, and generative reward models across correctness, emotional intelligence, and task-specific quality. Human-authored responses serve as style anchors. Final cross-stage distillation samples on-policy outputs while using earlier stage checkpoints as teachers; replacing reward advantage with a stopped teacher/student log-probability gap permits group size 1 and a reported batch size of 1,024.[^glm5-report-2026]

## Asynchronous agentic RL

Inference workers continuously produce trajectories while a separate training engine updates the policy and periodically pushes weights back every $K$ updates. A central service orchestrator controls task ratios, standardizes heterogeneous agent traces into message lists, and reportedly supports more than 1,000 concurrent rollouts. Resetting optimizer state after each rollout-policy weight synchronization is a report-specific stabilization choice.[^glm5-report-2026]

Key mismatch controls are:

- **Token-in-token-out gateway:** preserves rollout token IDs, boundaries, and metadata instead of decoding and re-tokenizing text.
- **Direct double-sided importance sampling:** uses current-policy versus recorded rollout log-probabilities directly and masks tokens outside an asymmetric trust interval, avoiding historical checkpoint inference at the cost of residual off-policy bias.
- **Staleness and failure filtering:** drops trajectories whose oldest rollout weight version exceeds a threshold and excludes sandbox-collapse failures; incomplete GRPO groups are repeated only when more than half remain valid, otherwise dropped.
- **DP-aware routing:** consistently hashes every turn of one rollout to the same data-parallel rank, preserving prefix KV locality while dynamically rebalancing the hash space.[^glm5-report-2026]

The slime serving stack further uses FP8 rollouts, MTP, prefill/decode disaggregation, heartbeat-based failure removal, and multi-node attention/expert parallelism to target tail latency rather than aggregate throughput.[^glm5-report-2026]

## Environment and context scaling

The report describes more than 10K verifiable SWE environments across nine languages, thousands of synthesized terminal environments, difficult multi-hop search tasks built from a web knowledge graph, and an HTML slide-generation environment with static, runtime-layout, and visual rewards. Search inference folds observations older than five rounds, then discards all tool history above a 32K threshold; BrowseComp rises from a reported 55.3% without keep-recent to 62.0%, and hierarchical context management reaches 75.9%, but the strategy was parameter-searched on the evaluated setting.[^glm5-report-2026]

## Relationships

- **Post-trains:** [GLM-5 architecture, pre-training, and systems](glm-5-architecture-pretraining-and-systems.md).
- **Extends:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) with training/inference mismatch suppression and an asynchronous rollout variant.[^glm5-report-2026]
- **Evaluated by:** [GLM-5 evaluation and deployment limits](glm-5-evaluation-and-deployment-limits.md).

## Evidence limits

The report does not disclose total SFT or RL token counts, GPU counts, wall-clock speedups, clipping/staleness ablations, environment release coverage, or independent replications. Its top-level asynchronous objective is written as an expectation of mean-centered rewards without an explicit policy-gradient term, while later text supplies a token-level log-policy objective; this makes the exact complete optimization formulation unclear. Asynchrony improves utilization only if added inference capacity, policy lag, sample filtering, and orchestration overhead are favorable.[^glm5-report-2026]

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [main source](../raw/arXiv-2602.15763v2/0_main.tex), [post-training](../raw/arXiv-2602.15763v2/3_posttrain.tex), and [agentic RL](../raw/arXiv-2602.15763v2/3.1_agenticRL.tex); the [training-pipeline figure](../raw/arXiv-2602.15763v2/figures/overall_pipeline.pdf) and [context-management figure](../raw/arXiv-2602.15763v2/figures/GLM5-BC-cm.pdf) were visually inspected.
