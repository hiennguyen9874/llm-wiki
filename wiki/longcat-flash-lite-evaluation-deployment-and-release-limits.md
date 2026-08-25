---
type: Concept
title: LongCat-Flash-Lite evaluation, deployment, and release limits
description: LongCat-Flash-Lite reports matched base-model, agentic, and coding gains plus optimized 8×H800 decoding, but author-run evaluation and serving evidence lack reproducible artifacts.
tags: [longcat, evaluation, deployment, agentic-systems, tool-use, licensing]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:09:50Z }
sources:
  - id: longcat-flash-lite-card-2026
    resource: ../raw/LongCat-Flash-Lite.md
    title: LongCat-Flash-Lite model card
  - id: longcat-flash-lite-sparse-card-2026
    resource: ../raw/LongCat-Flash-Lite-Sparse.md
    title: LongCat-Flash-Lite-Sparse model card
  - id: longcat-embedding-scaling-2026
    resource: ../raw/2601.21204_ScalingEmbeddingsOutperformsScalingExpertsinLanguageModels/longcat.tex
    title: "Scaling Embeddings Outperforms Scaling Experts in Language Models"
---

# LongCat-Flash-Lite evaluation, deployment, and release limits

LongCat-Flash-Lite’s technical report supplies an author-run matched base-model comparison, agentic/coding/general/math tables, and an 8×H800 decoding figure; its card adds a Transformers tool-use example and SGLang instructions. Neither artifact provides sufficient evaluation or serving materials for independent capability or efficiency conclusions.[^longcat-embedding-scaling-2026][^longcat-flash-lite-card-2026]

## Reported evaluation

The card lists LongCat-Flash-Lite scores of 58.00/73.10/72.80 on Tau2-Airline/Retail/Telecom, 54.40 on SWE-Bench, 33.75 on TerminalBench, 85.52 on MMLU, and 96.80 on MATH500. Its table compares Kimi-Linear-48B-A3B, Qwen3-Next-80B-A3B-Instruct, and Gemini 2.5 Flash-Lite; values marked with an asterisk are stated to come from public reports.[^longcat-flash-lite-card-2026]

The report’s matched base-model table at 1.3T tokens compares LongCat-Flash-Lite with a parameter-identical model that converts its N-gram parameters to extra experts. LongCat-Flash-Lite wins 9 of 11 listed base-model benchmarks, including BBH (43.67 vs. 38.54), GPQA (29.66 vs. 25.37), DROP (52.43 vs. 47.92), and BigCodeBench (36.05 vs. 33.42), while the expert-scaled baseline is higher on MMLU (64.81 vs. 64.01) and MultiPL-E (30.20 vs. 30.03). This is direct but author-run evidence for that allocation, not a general MoE ranking.[^longcat-embedding-scaling-2026]

The sources provide no prompts, benchmark versions, tool environments, sampling and reasoning budgets, run counts, variance, scoring code, contamination controls, or matching procedure for the wider cross-model comparison. The listed values therefore do not establish a controlled ranking or the claimed competitiveness.[^longcat-embedding-scaling-2026][^longcat-flash-lite-card-2026]

## Reported inference optimization

For decoding, the report uses Eagle3 with three-step speculative decoding, wide expert parallelism, and single-batch overlap. It describes device-resident N-gram-ID handling and an N-gram cache; kernel fusion; a split-KV attention-combine kernel claimed to halve combine latency; and programmatic dependent launch. Its one plotted throughput result is on 8×H800-80G with a 4K input and 1K output length; no numeric result table, concurrency protocol, runtime version, or end-to-end comparison configuration is supplied.[^longcat-embedding-scaling-2026]

## Interface and deployment

The Transformers example requires `trust_remote_code=True`, builds input with the checkpoint chat template, and shows a structured function call whose `arguments` field is an object. It imports response parsing from `parse_model_response.py`, but that referenced local file is absent from the supplied raw artifact; its parser behavior was not inspected.[^longcat-flash-lite-card-2026]

For direct Transformers use, the card says at least two 80-GB GPUs are needed and lists Python 3.10+, PyTorch 2.6+, Transformers 4.57.6+, and Accelerate 1.10.0+. Separately, it says an SGLang adaptation can serve the model on one node such as 8×H20-141G with tensor and expert parallelism, and provides an `ep=8`, `tp=8` launch example. These are vendor configuration examples, not evidence of a generally supported hardware envelope, throughput, latency, memory use, concurrency, or 256K-context performance.[^longcat-flash-lite-card-2026]

## License and usage boundary

The card releases weights and source code under MIT while withholding rights to Meituan trademarks and patents. It states that the model was not comprehensively evaluated for every downstream use and assigns users responsibility for accuracy, safety, fairness, data protection, content safety, and legal compliance, especially in sensitive or high-risk applications.[^longcat-flash-lite-card-2026]

## Relationships

- **Evaluates and releases:** [LongCat-Flash-Lite N-gram-embedding architecture](longcat-flash-lite-ngram-embedding-architecture.md).
- **Can use:** [LLM inference serving stack](llm-inference-serving-stack.md); the referenced SGLang adaptation was not inspected.[^longcat-flash-lite-card-2026]
- **Baseline for reported comparison by:** [LongCat-Flash-Lite-Sparse evaluation, deployment, and release limits](longcat-flash-lite-sparse-evaluation-deployment-and-release-limits.md).[^longcat-flash-lite-sparse-card-2026]

## Evidence limits

This synthesis is bounded to a vendor card and technical report. No weights, configuration, parser file, SGLang code, benchmark harness, traces, raw measurements, or model execution were available. The report’s figure attachments were visually inspected; the linked SGLang pull request was not.[^longcat-embedding-scaling-2026][^longcat-flash-lite-card-2026]

[^longcat-flash-lite-card-2026]: Meituan LongCat team, “LongCat-Flash-Lite,” [model card](../raw/LongCat-Flash-Lite.md), Evaluation Results, Quick Start, Deployment, License Agreement, and Usage Considerations.

[^longcat-flash-lite-sparse-card-2026]: Meituan LongCat team, “LongCat-Flash-Lite-Sparse,” [model card](../raw/LongCat-Flash-Lite-Sparse.md), Evaluation Results.
