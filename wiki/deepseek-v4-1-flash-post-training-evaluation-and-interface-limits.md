---
type: Concept
title: DeepSeek-V4.1-Flash post-training, evaluation, and interface limits
description: DeepSeek-V4.1-Flash reports synthesis-heavy SFT, asynchronous RL and multi-teacher distillation, effort-conditioned token penalties, scaffold-sensitive agent results, and preliminary multi-agent gains.
tags: [deepseek-v4-1, post-training, reasoning-effort, agentic-evaluation, multimodal, deployment]
status: draft
created: 2026-09-11
generated: { by: llm-wiki-agent/1, at: 2026-09-11T05:35:45Z }
sources:
  - id: deepseek-v41-tech-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
  - id: deepseek-v41-flash-readme
    resource: ../raw/DeepSeek-V4.1-Flash/README.md
    title: "DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression"
  - id: deepseek-v41-inference-readme
    resource: ../raw/DeepSeek-V4.1-Flash/inference/README.md
    title: DeepSeek-V4.1-Flash minimal inference
  - id: deepseek-v41-evaluation-readme
    resource: ../raw/DeepSeek-V4.1-Flash/evaluation/README.md
    title: Running DeepSWE with dsh-minimal and mini-swe-agent
---

# DeepSeek-V4.1-Flash post-training, evaluation, and interface limits

DeepSeek-V4.1-Flash’s README says post-training retains the SFT → RL → on-policy-distillation sequence without algorithmic changes, while scaling automatically synthesized agent tasks, environments, and rollouts. The released interface accepts an integer reasoning-effort setting from 1 to 100. Author-run results at effort 100 are strong on several code and agent tasks but mixed against listed frontier systems, and scaffold, context, sampling, tool, and judge choices prevent reading the tables as a model-only ranking.[^deepseek-v41-flash-readme]

## Post-training and reasoning control

The report attributes gains to automated task and environment production rather than a new optimization algorithm. A task is treated as a problem–environment–verifier triplet and repeatedly audited using solver trajectories. General-agent environments mock interfaces observed in voluntarily returned workflow data; coding environments derive from selected sessions and public GitHub repositories, then use separate construction, solving, inspection, and repair agents to build containerized, automatically verified tasks. Mixture sizes, acceptance rates, contamination controls, and component ablations remain undisclosed.[^deepseek-v41-tech-report]

For effort level $b\in[1,100]$, RL mean-centers advantages within responses sharing the same prompt and effort instead of comparing effort levels directly. It adds a capped per-token deduction whose coefficient decreases exponentially with effort, so higher settings permit longer reasoning. The appendix derives only a local affine relationship between preferred length and effort under an assumed exponentially decaying marginal benefit; it explicitly does not guarantee measured monotonicity.[^deepseek-v41-tech-report]

The report’s aggregate Figure 9 shows output length increasing with effort and average reasoning accuracy rising from 67.1% at effort 25 to 76.3% at 100, with roughly 2.5 times the output tokens. However, per-scaffold Figure 11 contains accuracy dips and plateaus even while token counts rise monotonically. Effort is therefore a reliable prompt-and-length control in these tests, not a pointwise guarantee of better answers.[^deepseek-v41-tech-report]

## Reported evaluation

The base-model table is mixed rather than uniformly dominant. DeepSeek-V4.1-Flash-Base leads the listed models on MMLU-Pro (74.1), BigCodeBench (60.6), HumanEval (79.4), and GSM8K (93.0), while DeepSeek-V4-Pro-Base leads several knowledge, reasoning, math, and long-context rows. The new model is the only one of those three with reported multimodal scores in that table, so those rows are not comparative evidence.[^deepseek-v41-flash-readme]

At maximum reasoning effort, notable author-reported agent results include 90.6 on Terminal-Bench 2.1, 74.2 resolved on DeepSWE v1.1, 88.1 on CyberGym, 54.8 on AutomationBench, and 31.8 on Agent’s Last Exam. It trails the strongest listed comparator on Terminal-Bench 3.0 and 4.0, ProgramBench, NL2Repo-Bench, SEC-Bench Pro, ExploitGym, and all three visual-agent rows. The table mixes unavailable entries, different systems, and both public and potentially internal harness choices; no uncertainty intervals or independent replication are supplied.[^deepseek-v41-flash-readme]

## Scaffold and multi-agent sensitivity

Under common decoding settings, the same checkpoint ranges from 65.5 to 74.2 resolved on DeepSWE v1.1 and from 84.1 to 90.6 on Terminal-Bench 2.1 across eight scaffold configurations. These tests use eight samples per DeepSWE task, three per Terminal-Bench task, up to 500 generation rounds, a one-million-token limit, and no network for Terminal-Bench. They show that agent scores are model–scaffold–evaluation-system results.[^deepseek-v41-tech-report]

Preliminary Agent Team experiments compare the strongest observed multi-agent setup with the strongest available single-agent baseline rather than a controlled matched architecture. Multi-agent leads at every tested deadline: ProgramBench peaks at 30.04% Almost@1 at eight hours versus 20.39%, and FrontierSWE v2 reaches 32.90 Mean@5 at 20 hours versus 28.20. The reward includes task success, collaboration, and a critical-path-derived latency penalty; benchmark filtering, configuration selection, and long wall-clock budgets limit generalization.[^deepseek-v41-tech-report]

## Contradictions

The Markdown extraction of technical-report Table 3 is internally inconsistent with its surrounding prose and Figure 1. Its visible last numeric column is labeled as DeepSeek-V4.1-Flash but contains predecessor values such as 54.4 on DeepSWE and 82.7 on Terminal-Bench 2.1, while the prose and Figure 1 report 74.2 and 90.6 for V4.1. It similarly prints 3289 for Codeforces before prose claims 3471. The maintained benchmark summary therefore uses the mutually consistent prose, figures, and release README, while treating extracted Table 3 as malformed rather than silently resolving individual cells.[^deepseek-v41-tech-report][^deepseek-v41-flash-readme]

## Prompt, inference, and reproduction boundary

The release declares no Jinja chat template and instead supplies the standalone [DeepSeek-V4.1 prompt encoder](deepseek-v4-1-chat-tool-and-reasoning-encoding.md). The README recommends `temperature=1.0`, `top_p=0.95` or `1.0`, a 1M-token context, and at least 256K output tokens; these are vendor recommendations rather than generally validated defaults.[^deepseek-v41-flash-readme]

The bundled inference path is explicitly a readable reference rather than a production server. It covers model components and tensor-parallel checkpoint conversion, but generation is plain autoregressive sampling even though the model exposes a DSpark forward path; its self-test uses uninitialized weights and checks shapes/kernel plumbing rather than numerical correctness.[^deepseek-v41-inference-readme]

The DeepSWE recipe pins Pier and DeepSWE commits, supplies a reference patch, and documents container constraints, result artifacts, and repeated runs. Reproduction still requires Docker, Python/uv, external repositories and images, a compatible hosted endpoint, a user-provided API credential, and—for `dsh-minimal`—a separately installed Harness SDK artifact. The source contains only a placeholder credential, not a live secret.[^deepseek-v41-evaluation-readme]

## Relationships

- **Evaluates:** [DeepSeek-V4.1-Flash architecture and pretraining](deepseek-v4-1-flash-architecture-and-pretraining.md).
- **Uses:** on-policy distillation in the same broad post-training family described for [DeepSeek-V4 post-training and evaluation limits](deepseek-v4-post-training-and-evaluation-limits.md), though this README does not disclose the V4.1 implementation.
- **Depends on:** agent scaffolds and inference settings for the reported agentic results.
- **Supported by:** [DeepSeek-V4.1 training, serving, and agent infrastructure](deepseek-v4-1-training-serving-and-agent-infrastructure.md), including resumable asynchronous rollouts and DSec sandboxes.
- **Encoded by:** [DeepSeek-V4.1 chat, tool, and reasoning encoding](deepseek-v4-1-chat-tool-and-reasoning-encoding.md).

## Evidence limits

The evaluations are author-run; some use internal data, internal frameworks, filtered subsets, or LLM judges. The report supplies effort curves and scaffold settings but no confidence intervals, contamination audit, matched token-budget comparison, independent replication, comprehensive safety evaluation, or end-to-end latency/cost measurements. Multi-agent results are explicitly preliminary and compare selected strongest configurations. The reproducibility recipe was not executed because it requires model weights, external services, containers, credentials, and substantial compute.[^deepseek-v41-tech-report][^deepseek-v41-evaluation-readme]

[^deepseek-v41-tech-report]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [technical report](../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md), Sections 5–6, Tables 2–5, Figures 8–12, and Appendix C.

[^deepseek-v41-flash-readme]: DeepSeek-AI, “DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression,” [release README](../raw/DeepSeek-V4.1-Flash/README.md), Evaluation Results, Prompt Encoding, Minimal Inference, and Reproducing DeepSWE Benchmark Results.

[^deepseek-v41-inference-readme]: DeepSeek-AI, [DeepSeek-V4.1-Flash minimal inference](../raw/DeepSeek-V4.1-Flash/inference/README.md), conversion, execution, and self-test documentation.

[^deepseek-v41-evaluation-readme]: DeepSeek-AI, [DeepSWE reproduction guide](../raw/DeepSeek-V4.1-Flash/evaluation/README.md), prerequisites, pinned repositories, patch behavior, execution, and result artifacts.
