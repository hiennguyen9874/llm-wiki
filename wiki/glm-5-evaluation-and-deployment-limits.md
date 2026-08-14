---
type: Concept
title: GLM-5 evaluation and deployment limits
description: GLM-5 reports strong open-model coding, reasoning, and agent results, but harness changes, internal benchmarks, judge models, context management, safety omissions, and workload-specific deployment claims bound interpretation.
tags: [glm-5, evaluation, coding-agents, long-context, deployment, evidence-limits]
status: stable
created: 2026-08-14
generated: { by: llm-wiki-agent/1, at: 2026-08-14T06:56:09Z }
sources:
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
---

# GLM-5 evaluation and deployment limits

GLM-5 reports broad gains over GLM-4.7 and leading open-model results on many coding and agentic evaluations, while remaining task-dependent against proprietary systems. Interpretation requires preserving exact harnesses, judges, context policies, modified benchmark variants, and internal-suite boundaries; the report is not evidence that DSA, asynchronous RL, or any single component caused the whole-model gains.[^glm5-report-2026]

## Reported external results

Selected reported results include 77.8 on SWE-bench Verified, 73.3 on SWE-bench Multilingual, 56.2 on Terminal-Bench 2.0 (60.7/61.1 on the authors’ verified variant under two harnesses), 62.0 on BrowseComp and 75.9 with context management, 89.7 on $\tau^2$-Bench, 67.8 on the MCP-Atlas public set, and a $4,432 final Vending-Bench 2 balance. These results place GLM-5 ahead of compared open models on many rows, but not uniformly ahead of Claude Opus 4.5, Gemini 3 Pro, or GPT-5.2.[^glm5-report-2026]

Harness details materially change the comparisons: SWE-bench uses OpenHands and a tailored prompt; Terminal-Bench uses either Terminus-2 or Claude Code and a separately corrected task set; CyberGym uses Claude Code; MCP-Atlas extends timeout to ten minutes and uses Gemini 3 Pro as judge; $\tau^2$-Bench modifies simulator prompts and Airline domains; reasoning tasks may generate up to 131,072 tokens and HLE-with-tools up to 202,752.[^glm5-report-2026]

## Real-world engineering suite

CC-Bench-V2 evaluates frontend, backend, repository exploration, and chained development. GLM-5 reports 98% frontend build success, 25.8 backend Pass@1, 65.6 repo-exploration Pass@1, and 52.3 chained-task Pass@1. Claude Opus 4.5 remains ahead on strict frontend instance success, backend, and chained tasks, while GLM-5 is slightly ahead on repo exploration.[^glm5-report-2026]

Frontend Agent-as-a-Judge uses Claude Code with Claude Sonnet 4.5, Playwright, source inspection, screenshots, and terminal output. The report gives 94% agreement with humans over 130 check-items and 85.7% Spearman ranking correlation across eight models; disagreements concentrate on subjective visual quality. CC-Bench-V2 is internal, iteratively curated, partly LLM-generated, and not independently auditable from this bundle.[^glm5-report-2026]

On the fresher SWE-rebench January 2026 slice, GLM-5 reports 42.1% resolved, only 0.8 points above GLM-4.7 and below five listed proprietary systems. This provides an important counterweight to stronger static SWE-bench claims.[^glm5-report-2026]

## Deployment claims

For seven Chinese accelerator platforms, the report describes W8A8 attention/dense MLP plus W4A8 experts, fused DSA indexer and sparse-attention kernels, MLA preprocessing fusion, asynchronous scheduling, prefix caching, attention data parallelism plus expert parallelism, and MTP. The Ascend case claims one-node fit for the roughly 750B model and 50% lower long-sequence deployment cost, but gives no model-quality table, hardware-normalized latency/throughput, workload definition, or reproducible baseline.[^glm5-report-2026]

## Relationships

- **Evaluates:** [GLM-5 architecture, pre-training, and systems](glm-5-architecture-pretraining-and-systems.md) and [GLM-5 post-training and asynchronous agentic RL](glm-5-post-training-and-asynchronous-agentic-rl.md).
- **Depends on:** [Test-time compute allocation](test-time-compute-allocation.md) and context-management policy for several high-budget agentic results.

## Evidence limits

All model results except the separately run Vending-Bench evaluation are reported or selected by the GLM-5 team. Several baselines use proprietary models, judges, non-identical harnesses, or benchmark fixes; internal data and CC-Bench-V2 aren’t supplied. The paper gives no contamination audit, complete training-data provenance, safety evaluation, model-card risk analysis, energy accounting, statistical uncertainty for most scores, or controlled attribution across model scale, 28.5T-token training, DSA, post-training, and inference-time compute.[^glm5-report-2026]

[^glm5-report-2026]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” arXiv:2602.15763v2, [main source](../raw/arXiv-2602.15763v2/0_main.tex), [evaluation](../raw/arXiv-2602.15763v2/4_evaluation.tex), [evaluation appendix](../raw/arXiv-2602.15763v2/9_appendix.tex), and [Chinese accelerator adaptation](../raw/arXiv-2602.15763v2/3.2_domestic.tex); included [ARC](../raw/arXiv-2602.15763v2/figures/arc_clean.pdf), [CC-Bench-V2](../raw/arXiv-2602.15763v2/figures/cc-bench-v2.pdf), and [Agent-as-a-Judge](../raw/arXiv-2602.15763v2/figures/agent-as-judge.pdf) figures were visually inspected.
