---
type: Concept
title: DeepSeek-V4 post-training and evaluation limits
description: DeepSeek-V4 trains domain-and-effort specialists with SFT and GRPO, consolidates more than ten teachers through full-vocabulary on-policy distillation, and reports strong long-context, reasoning, and agent results that remain author-run evaluations.
tags: [deepseek-v4, post-training, on-policy-distillation, grpo, evaluation, limitations]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T00:00:00Z }
sources:
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# DeepSeek-V4 post-training and evaluation limits

DeepSeek-V4’s post-training first builds domain specialists through supervised fine-tuning and GRPO, then merges more than ten teachers into one student by multi-teacher on-policy distillation (OPD). The report replaces V3.2’s mixed RL stage with OPD and computes reverse-KL distillation against full teacher vocabularies rather than a sampled token-level estimate; it presents this as a lower-variance, more stable procedure, not a generally proven advantage.[^deepseek-v4-2026]

## Specialists, rewards, and distillation

Reasoning-effort specialists use different RL length penalties and context windows for non-think, high, and max modes. For hard-to-verify tasks, the authors use rubric-guided data and a generative reward model, which is itself optimized with RL; this replaces a conventional scalar reward model but does not eliminate judge error or reward gaming.[^deepseek-v4-2026]

For scalable full-vocabulary OPD, teacher parameters are centrally stored and loaded on demand, while last-layer teacher hidden states—not full logits—are cached and later passed through a loaded prediction head. The report also applies FP4 QAT to MoE weights and CSA-indexer QK paths; its stated 99.7% KV-entry recall and $2\times$ top-$k$ selector speedup are configuration-specific author measurements.[^deepseek-v4-2026]

## Agent state and interface

The report defines an XML-like DSML tool-call format and preserves reasoning content across user turns in actual tool-calling conversations, but discards previous reasoning after a new user message in ordinary chat. Its preemptible rollout service appends every generated token to a write-ahead log and persists unfinished KV state; regenerating interrupted rollouts from scratch would bias training toward shorter outputs, according to the authors.[^deepseek-v4-2026]

## Reported results and limits

The report’s internal table gives Pro-Max scores of 83.5 on MRCR 1M and 62.0 on CorpusQA 1M, compared with 92.9/71.7 for Claude Opus 4.6 Max and 76.3/53.8 for Gemini 3.1 Pro under the authors’ setup. It also reports a 93.5 LiveCodeBench Pass@1 and 67.9% Terminal Bench 2.0 accuracy. Different output budgets, proprietary APIs, a partly internal Codeforces benchmark, in-house agent harnesses, unavailable competitor APIs, and undisclosed data/prompts mean these results are not independent general capability rankings.[^deepseek-v4-2026]

The authors call the model a preview and identify architecture complexity, incompletely understood stability interventions, sparse-model scaling, latency, long-horizon agents, multimodality, and data curation as continuing work. Benchmark, LLM-judge, and internal preference results do not independently establish safety, factuality, reliability, or real-world agent robustness.[^deepseek-v4-2026]

## Contradictions

- The report’s MRCR 1M table gives Pro-Max 83.5 and Flash-Max 78.7 MMR, whereas its embedded eight-needle MRCR curve shows Pro-Max 0.59 and Flash-Max 0.49 at 1,024K input tokens. Both are labeled MMR, but the source does not explain their differing setup or aggregation; they should not be compared as one directly reconciled result.[^deepseek-v4-2026]

## Relationships

- **Extends:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md).
- **Applies:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) to specialist training.
- **Related to:** [Kimi K3 agentic post-training](kimi-k3-agentic-post-training.md), another multi-teacher on-policy distillation pipeline.
- **Implemented by:** [DeepSeek-V4 training and serving infrastructure](deepseek-v4-training-and-serving-infrastructure.md).

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex) and included [evaluation tables](../raw/arXiv-2606.19348v1/tables/large_eval.tex), [small_eval.tex](../raw/arXiv-2606.19348v1/tables/small_eval.tex), and [code_agent_dsbench.tex](../raw/arXiv-2606.19348v1/tables/code_agent_dsbench.tex), Sections 6–7.
