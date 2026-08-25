---
type: Concept
title: Ling-3.0-tiny evaluation, serving, and evidence limits
description: Ling-3.0-tiny’s card reports agentic, coding, long-context, reasoning, and instruction-following scores plus SGLang, custom-vLLM, and experimental Apple-Silicon Ollama paths, but results and speed claims are configuration-bound.
tags: [ling-3-0-tiny, evaluation, agents, serving, local-deployment, limitations]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:21:40Z }
sources:
  - id: ling3-tiny-card-2026
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny.md
    title: Ling-3.0-tiny model card
  - id: ling3-tiny-benchmarks-2026
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny-benchmark.png
    title: Ling-3.0-tiny benchmark comparison chart
---

# Ling-3.0-tiny evaluation, serving, and evidence limits

Ling-3.0-tiny’s card and included chart report results across agentic, coding, long-context, knowledge, reasoning, and instruction-following tasks, and provide SGLang, custom-vLLM, and experimental MLX/Ollama instructions. These are vendor-supplied results and recipes, not independent validation of capability, throughput, memory, or local deployment.[^ling3-tiny-card-2026][^ling3-tiny-benchmarks-2026]

## Reported benchmark results

The chart reports 772.00 on GDPval v2-AA; 20.80 on TAU3-Banking-AA; 62.72 on BFCL-v4 (FC); 27.70 on Terminal-Bench 2.1; 47.93 on ArtifactsBench; 24.20 on SciCode; and 58.70 on AA-LCR. It also lists 8.52 AA-Omniscience Accuracy, 69.54 AA-Omniscience Non-Hallucination rate, 73.40 GPQA Diamond, 9.30 HLE, 70.31 HMMT-Feb26, 71.03 IMO-AnswerBench, 63.61 IFBench, 62.30 LIFEBench, and 83.15 Multi-IF.[^ling3-tiny-benchmarks-2026]

The card additionally reports an Artificial Analysis Intelligence Index v4.1.1 score of 25 and Agentic Index score of 16. It says Artificial Analysis testing measured more than 160 output tokens/s and about 18 seconds end-to-end latency for a 500-token response including reasoning. The supplied artifacts do not give complete harnesses, comparison configurations, raw score files, or error estimates, so the chart is a heterogeneous vendor release comparison rather than a normalized quality ranking.[^ling3-tiny-card-2026][^ling3-tiny-benchmarks-2026]

## Deployment envelope

The card offers BF16, FP8, and INT4 weights, and says it validated local deployments on DGX Spark, Apple-Silicon MacBook, and Mac mini. It reports FP8 throughput of roughly 100–105 tokens/s on DGX Spark and 86–90 tokens/s on an M4 Pro MacBook, with about 8.34 GiB peak memory at 8K context. Hardware, quantization, context length, batching, sampling, and measurement method make these figures incomparable to the separate Artificial Analysis measurement without further data.[^ling3-tiny-card-2026]

The SGLang low-latency recipe uses an image specialized for this model, 256K YaRN context, and built-in MTP/NEXTN on one 141GB-class GPU or a one-GPU Blackwell node. The custom-vLLM path requires an InclusionAI fork and Ling-specific tool/reasoning parsers. The Ollama instructions require building an unmerged pull-request branch and are limited to MLX on Apple Silicon; the card only says that configuration was verified on an M4 Pro Mac with 48GB unified memory.[^ling3-tiny-card-2026]

Thinking is enabled by default. The card recommends temperature 1.0, top-p 0.95, and top-k 20, and exposes `enable_thinking` through the chat template. These are integration and sampling recommendations, not evidence of reliable reasoning, tool use, safety, or performance in every compatible server.[^ling3-tiny-card-2026]

## Relationships

- **Evaluates:** [Ling-3.0-tiny hybrid architecture](ling-3-0-tiny-hybrid-architecture.md).
- **Can operationalize:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) through the declared MTP/NEXTN SGLang path; its implementation and speed effect are undisclosed.[^ling3-tiny-card-2026]
- **Uses:** [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md) terms: the cited 8.34-GiB peak is explicitly at 8K context, while the separate latency result includes generation and reasoning.

## Evidence limits

The local bundle contains a model-card narrative and two images, but no weights, code, raw benchmark artifacts, detailed test configurations, training-data disclosure, safety report, or reproducible local measurements. The card links to external cookbooks and repositories that were not included or inspected. Placeholder values such as `HF_TOKEN=<your-hf-token>` are examples, not credentials. All quality, speed, memory, and “validated” deployment claims remain vendor- and configuration-bounded.[^ling3-tiny-card-2026][^ling3-tiny-benchmarks-2026]

[^ling3-tiny-card-2026]: InclusionAI, “Ling-3.0-tiny,” [model card](../raw/Ling-3.0-tiny/Ling-3.0-tiny.md), Introduction, Evaluation, and Quickstart.

[^ling3-tiny-benchmarks-2026]: InclusionAI, “Ling-3.0-tiny benchmark comparison,” [included chart](../raw/Ling-3.0-tiny/Ling-3.0-tiny-benchmark.png).