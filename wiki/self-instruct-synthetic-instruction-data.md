---
type: Concept
title: Self-Instruct synthetic instruction data
description: Self-Instruct bootstraps instruction tuning data by prompting a language model to generate diverse tasks and instances, filtering them, then supervised-fine-tuning the model on the retained examples.
tags: [self-instruct, synthetic-data, instruction-tuning, supervised-fine-tuning, data-generation]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:29:08+07:00 }
sources:
  - id: self-instruct-summary
    resource: ../raw/Self-Instruct.md
    title: "Self-Instruct overview (Vietnamese summary)"
---

# Self-Instruct synthetic instruction data

Self-Instruct is a synthetic-data bootstrapping procedure for instruction following: begin with human-written seed tasks, use a language model to generate new instructions and examples, filter the generations, and apply standard supervised fine-tuning (SFT) to the resulting instruction–input–output triples.[^self-instruct-summary]

## Generation and filtering loop

The reported experiment starts with 175 human-authored tasks. For each generation prompt, it samples eight task instructions—six human seeds and two previously model-generated instructions—to elicit novel instructions. Retained instructions re-enter the pool, so later prompts can expand beyond the original seeds.[^self-instruct-summary]

The procedure separates tasks whose outputs come from a small finite label set from open-ended tasks:

- For **non-classification** tasks, it generates an input and then its output.
- For **classification** tasks, it uses **output-first** generation: select or generate a label, then generate an input matching that label. The source says this avoids the label imbalance observed when inputs are generated first.[^self-instruct-summary]

A candidate instruction is retained only when its maximum ROUGE-L similarity to the existing task pool is below 0.7. The reported heuristics also remove instructions requiring unsupported visual inputs, duplicate or conflicting instances, malformed or truncated generations, extreme-length fields, and cases whose output merely repeats the input.[^self-instruct-summary]

## Training implication

The retained triples are formatted with several instruction/input prompt templates and used for next-token SFT of GPT-3; the source explicitly distinguishes this from reinforcement learning. This transfers behavior elicited in few-shot context into model weights, but does not establish that the process supplies knowledge or reasoning beyond the generator's existing capabilities.[^self-instruct-summary]

## Relationships

- **Post-trains:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md); the reported main experiment generates data with and then fine-tunes GPT-3.[^self-instruct-summary]
- **Contrasts with:** [InstructGPT human-feedback alignment](instructgpt-human-feedback-alignment.md); Self-Instruct uses generated instruction-response data and SFT, whereas InstructGPT's documented procedure additionally learns from human rankings and PPO.[^self-instruct-summary]
- **Evaluated by:** [Self-Instruct results and limitations](self-instruct-results-and-limitations.md).

[^self-instruct-summary]: “Self-Instruct overview” (Vietnamese summary), [raw source](../raw/Self-Instruct.md), Sections 1–4 and 8–10. It cites Wang et al., “Self-Instruct: Aligning Language Models with Self-Generated Instructions,” ACL 2023; the primary paper has not been independently ingested here.
