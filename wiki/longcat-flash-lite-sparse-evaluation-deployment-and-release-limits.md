---
type: Concept
title: LongCat-Flash-Lite-Sparse evaluation, deployment, and release limits
description: The LongCat-Flash-Lite-Sparse card reports mixed sparse-versus-dense benchmark changes, native one-million-token long-context results, and an SGLang serving example, but no reproducible evaluation or serving measurements.
tags: [longcat, evaluation, deployment, sparse-attention, long-context, licensing]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:07:56Z }
sources:
  - id: longcat-flash-lite-sparse-card-2026
    resource: ../raw/LongCat-Flash-Lite-Sparse.md
    title: LongCat-Flash-Lite-Sparse model card
---

# LongCat-Flash-Lite-Sparse evaluation, deployment, and release limits

The LongCat-Flash-Lite-Sparse model card reports that its sparse variants improve several agentic coding, tool-use, search, and selected reasoning measures over [LongCat-Flash-Lite evaluation, deployment, and release limits](longcat-flash-lite-evaluation-deployment-and-release-limits.md), while some general, mathematical, and coding measures decline. It also lists long-context benchmark results and an SGLang serving command, but supports neither reproducible capability rankings nor deployment-efficiency conclusions.[^longcat-flash-lite-sparse-card-2026]

## Reported evaluation

The card compares Lite-Dense, Lite-Sparse without Hierarchical Indexing (HI), and Lite-Sparse with HI. Selected reported outcomes illustrate the mixed result:[^longcat-flash-lite-sparse-card-2026]

| Benchmark | Dense | Sparse w/o HI | Sparse w/ HI |
| --- | ---: | ---: | ---: |
| SWE-Bench Verified (acc) | 54.40 | 68.20 | 65.20 |
| SWE-Bench Multilingual (acc) | 38.10 | 59.33 | 56.00 |
| TerminalBench 2.0 (acc) | 33.75 | 33.70 | 32.58 |
| τ²-Telecom (avg@4) | 72.80 | 95.18 | 96.05 |
| MMLU (acc) | 85.52 | 85.31 | 85.14 |
| MATH500 (acc) | 96.80 | 95.80 | 96.80 |

Sparse variants add reported scores where the dense baseline is unavailable, including 48.62/48.18 on BrowseComp (pass@1), 68.50/66.00 on RWSearch (pass@1), and 65.73/64.90 on AIME 2026 (avg@32), without/with HI respectively. The card also gives sparse-only long-context results: for example, MRCR (8-needle) is 44.66/44.47, GraphWalks Extend is 66.27/65.63, and LongBench-v2 is 52.50/53.64, without/with HI.[^longcat-flash-lite-sparse-card-2026]

These are vendor-reported point estimates. The card does not provide prompts, run counts, variance, decoding or tool settings, benchmark versions, contamination controls, long-context input construction, or evaluation code. It identifies dense values as sourced from the predecessor’s technical report, which was not inspected here.[^longcat-flash-lite-sparse-card-2026]

## Deployment

The card states that a basic SGLang adaptation exists and gives a `launch_server` example using `--trust-remote-code`, up to 64 running requests, bfloat16 KV cache, and `--nsa-prefill-backend fa3`. It says the model can run on one node such as 1×H20-141G. This is an example configuration, not evidence of its supported hardware envelope, usable one-million-token concurrency, throughput, latency, memory use, or production reliability.[^longcat-flash-lite-sparse-card-2026]

## License and usage boundary

The card says the weights and source code are MIT licensed, while withholding rights to Meituan trademarks and patents. It states that downstream developers must assess accuracy, safety, fairness, data protection, content safety, and legal compliance, particularly for sensitive or high-risk uses.[^longcat-flash-lite-sparse-card-2026]

## Relationships

- **Evaluates and releases:** [LongCat-Flash-Lite-Sparse attention architecture](longcat-flash-lite-sparse-attention-architecture.md).
- **Can use:** [LLM inference serving stack](llm-inference-serving-stack.md); the referenced SGLang adaptation was not inspected.[^longcat-flash-lite-sparse-card-2026]

## Evidence limits

This synthesis is bounded to the supplied vendor model card. The source contains prose and tables but no weights, configuration, source code, benchmark harness, evaluation artifacts, performance traces, or locally attached deployment materials. No model execution or benchmark reproduction was performed.[^longcat-flash-lite-sparse-card-2026]

[^longcat-flash-lite-sparse-card-2026]: Meituan LongCat team, “LongCat-Flash-Lite-Sparse,” [model card](../raw/LongCat-Flash-Lite-Sparse.md), Evaluation Results, Long-Context Benchmarks, Deployment, License Agreement, and Usage Considerations.
