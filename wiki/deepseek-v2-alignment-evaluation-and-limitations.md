---
type: Concept
title: DeepSeek-V2 alignment, evaluation, and limitations
description: DeepSeek-V2 post-training uses 1.5M SFT examples and two-stage GRPO, reporting stronger open-ended and reasoning results while documenting benchmark trade-offs, evaluation constraints, and bilingual coverage limits.
tags: [deepseek-v2, alignment, supervised-fine-tuning, grpo, evaluation, limitations]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:08:42Z }
sources:
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
---

# DeepSeek-V2 alignment, evaluation, and limitations

DeepSeek-V2’s reported post-training applies SFT to 1.5M conversational instances, then two-stage GRPO: code-and-math reasoning alignment followed by multi-reward human-preference alignment. The authors report improved code, math, and open-ended-chat scores, while explicitly observing an alignment tax on some standard benchmarks and retaining general LLM reliability and bilingual-coverage limits.[^deepseek-v2-2024]

## SFT and reinforcement learning

The SFT data comprise 1.2M helpfulness and 0.3M safety instances; the model is trained for two epochs. The report says changes from the initial release target hallucinated responses and writing quality, but does not publish the datasets or an external factuality audit.[^deepseek-v2-2024]

For RL, the first stage trains a reasoning reward model for code and math. The second combines helpfulness, safety, and rule-based reward models. GRPO samples multiple completions per prompt, normalizes their rewards within the group to form advantages, applies clipped policy updates, and penalizes KL divergence from a reference policy. The report also describes a hybrid training engine, vLLM large-batch inference, and CPU/GPU model offloading to manage RL resource use.[^deepseek-v2-2024]

## Reported outcomes

Relative to the SFT model, the RL model reports higher HumanEval (81.1 vs. 76.8), MBPP (72.0 vs. 70.4), MATH (53.9 vs. 52.7), and LiveCodeBench (32.5 vs. 28.7) scores in the authors’ table. It also reports MT-Bench 8.97 and AlpacaEval 2.0 length-controlled win rate 38.9, versus 8.62 and 30.0 for SFT. The paper cautions that format noncompliance can underestimate some chat-model few-shot scores in its evaluation framework.[^deepseek-v2-2024]

On the GPT-4-0613-rated AlignBench leaderboard included in the report, DeepSeek-V2 Chat (RL) scores 7.91 overall, 7.45 on reasoning, and 8.36 on language. These results and comparisons are author-provided and include a mixture of reported, API-evaluated, and open-weight model results; they do not establish independent ranking or general human preference.[^deepseek-v2-2024]

## Limitations and trade-offs

- The authors observe that human-preference RL can improve open-ended benchmarks while degrading some standard benchmarks such as BBH; their mitigation is reported as a “tolerable” rather than eliminated trade-off.[^deepseek-v2-2024]
- Reducing SFT data below 10K instances reportedly caused substantial IFEval degradation in their experiments. This supports a requirement for their recipe, not a universal minimum SFT dataset size.[^deepseek-v2-2024]
- The model can lack post-training knowledge updates, generate non-factual or unverified advice, and hallucinate. Its primarily Chinese-and-English corpus may limit other-language proficiency.[^deepseek-v2-2024]
- The paper filters content it considers contentious to reduce regionally introduced bias. In a manual annotation of 420 MMLU Humanity-Moral examples, agreement with the benchmark label ranged from 42.1% to 66.7%; this raises a benchmark-value ambiguity but neither validates the filtering policy nor establishes absence of bias.[^deepseek-v2-2024]

## Relationships

- **Applies:** [Group Relative Policy Optimization](group-relative-policy-optimization.md) with a reasoning-reward stage followed by multi-reward preference alignment.
- **Qualifies:** [GRPO operational limits](grpo-operational-limits.md) with a reported alignment-tax example and RL serving/training overhead.
- **Extends:** [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md) into instruction-tuned and RL-aligned variants.

## Evidence limits

The bundled technical report is primary evidence for this reported recipe and its tables, but all training, reward-model, and evaluation details are author-controlled. It does not provide a causal ablation of the SFT, each reward source, GRPO, or engineering components, nor an independent safety, bias, factuality, or long-horizon behavior evaluation.[^deepseek-v2-2024]

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex) and included [chat-results table](../raw/arXiv-2405.04434v5/tables/chat_results.tex) and [AlignBench table](../raw/arXiv-2405.04434v5/tables/alignbench.tex), Sections 4–5 and Appendix E–F.
