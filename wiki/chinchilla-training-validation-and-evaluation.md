---
type: Concept
title: Chinchilla training validation and evaluation
description: At roughly Gopher’s training-compute budget, the 70B-parameter Chinchilla model trained on about 1.3–1.4T tokens outperformed the 280B-parameter, 300B-token Gopher model on reported loss and downstream evaluations.
tags: [chinchilla, gopher, pre-training, evaluation, inference-efficiency]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:12:13+07:00 }
sources:
  - id: chinchilla-summary
    resource: ../raw/Chinchilla.md
    title: Chinchilla overview (summary)
---

# Chinchilla training validation and evaluation

The source presents Chinchilla as a large-scale check of its compute-allocation fit: a 70B-parameter model trained on about 1.3–1.4T tokens uses roughly Gopher’s training compute while being four times smaller and trained on about four times as many tokens. It reports lower loss and stronger results than Gopher on most evaluated downstream benchmarks.[^chinchilla-summary]

## Matched-compute comparison

| Model | Parameters | Training tokens |
| --- | ---: | ---: |
| Gopher | 280B | 300B |
| Chinchilla | 70B | about 1.3–1.4T |

The source attributes the minor 1.3T versus 1.4T discrepancy to rounding and reporting conventions. It reports that Chinchilla exceeded Gopher on 51 of 57 MMLU tasks, tied on two, and trailed on four.[^chinchilla-summary]

## Reported evaluation results

The summary reports 5-shot MMLU accuracy of 67.6% for Chinchilla versus 60.0% for Gopher; BIG-bench average performance over 62 tasks of 65.1% versus 54.4%; and higher scores on LAMBADA, RACE, Natural Questions, and TriviaQA in the cited settings.[^chinchilla-summary]

These results support the source’s claim that the additional training data improved downstream behavior as well as next-token loss. They do not isolate data quantity from data composition or establish that every benchmark is free from leakage; the source explicitly identifies contamination as a concern when models consume more web-scale data.[^chinchilla-summary]

## Serving implication

For a comparable training budget, a smaller model can reduce inference memory, latency, and per-token serving cost because fewer parameters must be processed at generation time. This is separate from the fixed-pretraining-compute objective and is the source’s rationale for considering more-token, smaller-model training when inference demand is substantial.[^chinchilla-summary]

## Relationships

- **Validates:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md) with a reported 70B-versus-280B large-scale comparison.
- **Contrasts with:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md), whose 175B parameters and 300B training tokens fall below this source’s approximate 20-token-per-parameter heuristic.

[^chinchilla-summary]: “Chinchilla overview (summary),” [raw source](../raw/Chinchilla.md), Sections 8–13. This is a secondary Vietnamese-language summary that cites the Chinchilla paper and related webpages; the primary paper has not been independently ingested here.
