---
type: Concept
title: Writing Weights Index
description: A reported three-game index comparing language models on direct neural weight writing against PPO and random baselines.
tags: [ml, benchmarks, weight-space-programming]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:07:12Z }
stale_after: 2027-05-09
sources:
  - id: xingyudang2117428789068386630
    resource: ../raw/2117428789068386630/index.md
    scope: ../raw/2117428789068386630/
    kind: article
    title: "Post by @xingyudang on X"
---

**Reported:** @xingyudang presents a Writing Weights Index based on three games and says open-source models struggle at the task. The attached chart reports model comparisons, but the local capture does not establish the evaluation protocol or independently verify the results.[^xingyudang2117428789068386630]

## Definition and reported scores

The chart defines the index as the mean over three games of `100 × q / (1 + q)`, where `q = max(0, score − random) / (PPO 500M − random)`. **Synthesis:** When the denominator is positive, random-or-worse scores map to zero and matching the 500M-step PPO baseline maps to 50 per game; the transformation is nonlinear, so the aggregate is not a percentage of PPO's raw score.[^xingyudang2117428789068386630]

**Reported:** The chart gives GPT-6 Astra 60.7, Gemini 4 Carbon 57.7, Claude Opus 5.5 51.2, PPO 500M 50.0, Gemini 4 Argon 36.0, Kimi K3.1 Pro 29.8, and PPO 100M 25.2. It gives Qwen3.8 2.4T A95B 12.5, DeepSeek V4.1 Flash 1017 10.0, GLM-5.3 6.2, Mistral Large 4 2.6, MiniMax M3.1 Flash 0.2, Step 5 Preview 0.1, and uniform random 0.0.[^xingyudang2117428789068386630]

## Relationships

- This index compares systems on the policy-construction task described in [LLM-directed neural weight editing](llm-directed-neural-weight-editing.md); comparable settings cannot be assumed from the chart alone.[^xingyudang2117428789068386630]

## Evidence and coverage

The English X post, dated 2026-11-03 in the capture, and its local chart image were inspected. The shortened external link was not resolved or inspected; the capture does not specify the three games, individual scores, prompts, sampling, trials, uncertainty, code, license, or full protocol. The chart's denominator assumptions and comparability of model runs are not documented. Its results and model labels are source-reported, not reproduced or independently verified; draft status records these gaps. No executable content was identified.[^xingyudang2117428789068386630]

[^xingyudang2117428789068386630]: @xingyudang, post text and attached `assets/HWKcRSLWEAAHM77.jpg`, “Writing Weights Index” formula and bar labels.
