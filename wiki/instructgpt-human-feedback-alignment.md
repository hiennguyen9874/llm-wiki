---
type: Concept
title: InstructGPT human-feedback alignment
description: InstructGPT converts a pretrained GPT-3 policy into an instruction-following assistant through supervised demonstrations, ranked-response reward modeling, and KL-regularized PPO with an optional pretraining-data mix.
tags: [instructgpt, rlhf, instruction-tuning, reward-modeling, ppo, alignment]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:08:36Z }
sources:
  - id: instructgpt-summary
    resource: ../raw/InstructGPT.md
    title: "InstructGPT overview (Vietnamese summary)"
---

# InstructGPT human-feedback alignment

InstructGPT post-trains a pretrained GPT-3 policy to better follow user instructions by combining human-written demonstrations, human rankings of model outputs, and reinforcement learning against a learned reward model. The supplied summary characterizes the resulting recipe as SFT → reward model → PPO, with PPO-ptx additionally mixing a pretraining objective to reduce capability loss.[^instructgpt-summary]

## Three-stage procedure

1. **Supervised fine-tuning (SFT):** annotators write high-quality responses to prompts; the pretrained policy is fine-tuned by next-token likelihood on those demonstrations. The summary reports roughly 13,000 SFT prompts.
2. **Reward-model training:** annotators rank 4–9 candidate responses for a prompt. A scalar reward model is trained with a pairwise Bradley–Terry/logistic objective to score a preferred response above a dispreferred one. The summary reports roughly 33,000 ranking prompts and a 6B reward model, including for larger policies.
3. **Policy optimization:** PPO optimizes the SFT policy for reward-model score on a separate prompt set while applying a token-level KL penalty relative to the fixed SFT policy. The summary describes each generated response as a short contextual-bandit episode and reports roughly 31,000 PPO prompts.[^instructgpt-summary]

The reward model is a proxy for the preferences represented in its rankings, not a direct measure of factual correctness, safety, or universally shared values. The KL term constrains policy drift but does not make that proxy reliable outside its training and evaluation conditions.[^instructgpt-summary]

## PPO-ptx and alignment tax

PPO-ptx combines the PPO objective with gradients from the original pretraining distribution. The reported purpose is to reduce the **alignment tax**—loss of conventional language-model or benchmark performance caused by post-training—while retaining preference improvements. The summary reports that PPO-ptx reduces, but does not eliminate, degradation on some benchmarks relative to PPO alone.[^instructgpt-summary]

## Relationships

- **Post-trains:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md); the source describes InstructGPT as beginning from pretrained GPT-3 models.[^instructgpt-summary]
- **Addresses a limitation of:** [LLaMA evaluation, alignment, and limitations](llama-evaluation-alignment-and-limitations.md), which distinguishes base next-token prediction from instruction following and preference alignment.
- **Alternative approach:** [Direct Preference Optimization](direct-preference-optimization.md) directly optimizes preference pairs against a frozen reference instead of fitting this workflow’s separate reward model and running PPO; both commonly follow SFT.[^dpo-summary]
- **Evaluated by:** [InstructGPT behavioral evaluation and limitations](instructgpt-behavioral-evaluation-and-limitations.md).

[^dpo-summary]: “DPO overview” (Vietnamese summary), [raw source](../raw/DPO.md), Sections 1–2 and 11. This is secondary-source evidence; the primary DPO paper has not been independently ingested here.

[^instructgpt-summary]: “InstructGPT overview” (Vietnamese summary), [raw source](../raw/InstructGPT.md), Sections 1–7 and 10–13. This is secondary-source evidence that links to Ouyang et al., “Training language models to follow instructions with human feedback,” arXiv:2203.02155; the primary paper has not been independently ingested here.
