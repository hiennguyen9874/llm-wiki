---
type: Concept
title: DeepSeek-V3 post-training, evaluation, and limitations
description: DeepSeek-V3 post-training combines 1.5M SFT examples, R1-derived reasoning data, rule- and model-based rewards, and GRPO, with strong author-reported results qualified by internal evaluation and deployment limits.
tags: [deepseek-v3, alignment, supervised-fine-tuning, grpo, evaluation, limitations]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:38:26Z }
sources:
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# DeepSeek-V3 post-training, evaluation, and limitations

DeepSeek-V3’s reported post-training fine-tunes the base model for two epochs on 1.5M examples, using DeepSeek-R1-derived reasoning data and V2.5-generated non-reasoning data, then applies Group Relative Policy Optimization (GRPO) with rule- and model-based rewards. The report presents strong open-weight benchmark results, but its comparisons are author-run or API-mediated and remain bounded by output limits, benchmark coverage, and large-scale deployment requirements.[^deepseek-v3-2024]

## SFT, distillation, and rewards

For math, coding, and logic, the authors train specialist models with SFT plus RL, use DeepSeek-R1 outputs with prompts encouraging reflection and verification, then rejection-sample training examples for the final model. They state that this aims to preserve R1’s accuracy while controlling overlong, poorly formatted reasoning. For creative writing, role-play, and simple QA, V2.5 generates responses that human annotators verify.[^deepseek-v3-2024]

RL uses deterministic rule-based rewards where answers or code tests can be checked, and a model-based reward model for free-form tasks. GRPO groups rollouts for a prompt, standardizes group rewards for advantages, uses clipped policy updates, and constrains divergence from a reference policy. The report says its reward model is trained from V3 SFT checkpoints and includes chains of thought in preference data to mitigate reward hacking; this is a mitigation claim, not an independent robustness result.[^deepseek-v3-2024]

## Reported evaluation and trade-offs

The authors’ chat-model table reports V3 scores including 89.1 MMLU-Redux, 91.6 DROP F1, 48.7 LongBench v2 accuracy, 40.5 LiveCodeBench CoT Pass@1, 90.2 MATH-500 exact match, and 64.8 Chinese SimpleQA correctness, under an 8K output cap. Results are internally evaluated for several open models and via APIs for proprietary models, so they should not be treated as independent capability rankings.[^deepseek-v3-2024]

A V2.5 ablation reports that R1 distillation improves LiveCodeBench CoT from 31.1 to 37.4 and MATH-500 from 74.6 to 83.2, while increasing average output length substantially (718 to 783 and 769 to 1,510 tokens, respectively). The authors therefore frame reasoning distillation as an accuracy–generation-cost trade-off rather than a free improvement.[^deepseek-v3-2024]

## Limitations

- The recommended deployment units are large, which the report says can burden small teams; its stated decoding deployment uses 320 GPUs.[^deepseek-v3-2024]
- The report states that V3’s end-to-end generation speed is over twice V2’s, but leaves further speed improvement as future work and does not establish a general serving throughput comparison.[^deepseek-v3-2024]
- Benchmark scores and LLM-as-judge results do not independently establish factuality, safety, bias, robustness, agentic reliability, or general user preference.[^deepseek-v3-2024]

## Relationships

- **Extends:** [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md) with SFT and RL.
- **Applies:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) with rule- and model-based rewards.
- **Uses:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) at inference only when speculative decoding is enabled.

## Evidence limits

All recipe details, ablations, and evaluation values are from the authors’ technical report. Training data, prompts, reward models, systems, and most evaluation harness details are not sufficiently available here for independent reproduction or causal attribution.[^deepseek-v3-2024]

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex) and included [chat evaluation table](../raw/arXiv-2412.19437v2/tables/chat_evaluation.tex), Sections 6–7 and Table 5.
