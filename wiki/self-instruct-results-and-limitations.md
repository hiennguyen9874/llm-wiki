---
type: Concept
title: Self-Instruct results and limitations
description: The supplied Self-Instruct summary reports large instruction-following gains from synthetic SFT, while qualifying the result by synthetic-data quality, teacher-capability, bias, and evaluation limits.
tags: [self-instruct, synthetic-data, evaluation, limitations, instruction-tuning]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:29:08+07:00 }
sources:
  - id: self-instruct-summary
    resource: ../raw/Self-Instruct.md
    title: "Self-Instruct overview (Vietnamese summary)"
---

# Self-Instruct results and limitations

The supplied summary reports that Self-Instruct expanded 175 human seed tasks into 52,445 instructions and 82,439 instances, and that SFT on those examples improved its GPT-3 evaluation result on Super-NaturalInstructions. These are conditional results from the reported generation, filtering, model, and benchmark setup—not evidence of open-ended self-improvement or general reliability.[^self-instruct-summary]

## Reported data and evaluation

- The resulting set comprises 11,584 classification and 40,861 non-classification instructions; 35,878 instances have no separate input field.[^self-instruct-summary]
- On 119 Super-NaturalInstructions tasks with 100 instances per task, the summary reports ROUGE-L of 39.9 for GPT-3 Self-Instruct versus 6.8 for vanilla GPT-3. It reports 40.8 for InstructGPT-001, 49.5 for GPT-3 trained on Super-NaturalInstructions, and 51.6 when that training is combined with Self-Instruct data.[^self-instruct-summary]
- The source also describes human evaluation on user-oriented task categories and reports that Self-Instruct outperformed several GPT-3 baselines trained on public instruction datasets, with an approximately five-percentage-point absolute gap to InstructGPT-001. It does not make that result a general safety or factuality guarantee.[^self-instruct-summary]

## Limits

- Heuristic filtering and lexical ROUGE-L deduplication cannot reliably detect hallucination, subtle reasoning errors, unsafe outputs, executable-code failures, or semantic task duplication.[^self-instruct-summary]
- Because the generator supplies both much of the data and its answers, the method can reproduce its errors and biases. The source characterizes it as improving the use of existing capabilities, not guaranteeing new capabilities beyond the teacher model.[^self-instruct-summary]
- The pipeline still depends on human seed tasks, prompt and filter design, inference budget, SFT infrastructure, and external evaluation. “Low human annotation” therefore does not mean no human input or no generation cost.[^self-instruct-summary]
- The source notes that newer synthetic-data pipelines may add model-based judging, reward models, execution feedback, embedding-based deduplication, factual verification, or diversity and difficulty scoring; these are not properties established for the reported Self-Instruct pipeline.[^self-instruct-summary]

## Relationships

- **Evaluates:** [Self-Instruct synthetic instruction data](self-instruct-synthetic-instruction-data.md).
- **Compared with:** [InstructGPT behavioral evaluation and limitations](instructgpt-behavioral-evaluation-and-limitations.md); both report instruction-following improvements but use different supervision and evaluation conditions.[^self-instruct-summary]
- **Shares limitations with:** [InstructGPT behavioral evaluation and limitations](instructgpt-behavioral-evaluation-and-limitations.md), including that a training signal need not ensure truthfulness, safety, or representative values.[^self-instruct-summary]

[^self-instruct-summary]: “Self-Instruct overview” (Vietnamese summary), [raw source](../raw/Self-Instruct.md), Sections 5–10. It cites Wang et al., “Self-Instruct: Aligning Language Models with Self-Generated Instructions,” ACL 2023; the primary paper has not been independently ingested here.
