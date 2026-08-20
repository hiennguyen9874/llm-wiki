---
type: Concept
title: DFlash 2 evaluation and deployment
description: DFlash 2 reports higher accepted lengths than DFlash, DSpark, or native MTP in selected author-run benchmarks, with claimed 2.7–4.6× autoregressive throughput that remains workload- and runtime-dependent.
tags: [speculative-decoding, dflash, evaluation, deployment, throughput]
status: stable
created: 2026-08-20
generated: { by: llm-wiki-agent/1, at: 2026-08-20T08:49:07Z }
sources:
  - id: inco-dflash2-2026
    resource: ../raw/DFlash2.md
    title: "DFlash 2: Keep Drafting Parallel"
---

# DFlash 2 evaluation and deployment

Inco AI reports that its combined DFlash 2 selector and convolution increase accepted tokens over its DFlash and DSpark baselines in selected Qwen and Muse evaluations. The source claims 2.7–3.4× autoregressive throughput for Qwen3.8-27B and 3.1–4.6× for Muse Glimmer, but these are vendor-reported, task- and concurrency-specific figures rather than deployment guarantees.[^inco-dflash2-2026]

## Reported acceptance results

All values below are per-request mean acceptance length; they are not latency or throughput measurements.

| Target and comparison | Mean acceptance length |
|---|---:|
| Qwen3.5-4B MTP / DFlash / DSpark / DFlash 2 | 4.54 / 4.92 / 5.49 / **5.97** |
| Qwen3.8-27B MTP / DSpark / DFlash 2 | 4.28 / 3.62 / **4.80** |
| Muse Glimmer DFlash / DSpark / DFlash 2 | 4.44 / 4.48 / **5.70** |

For the Qwen3.5-4B comparison, the source states matched training for DFlash and DSpark and native MTP supplied by the model. It reports a 21% (1.05-token) mean gain over DFlash and 0.48 over DSpark, with the combined modules adding 1.3% to the five-layer draft–verify cycle latency. The Qwen3.8-27B and Muse Glimmer comparisons use their respective native MTP or official DFlash path and community DSpark drafters; those baseline provenance differences limit cross-method attribution.[^inco-dflash2-2026]

## Availability and integration boundary

The source announces DFlash 2 drafters for `Qwen3.8-27B` and Meta’s Muse Glimmer, and shows integrations or experimental branches for SGLang, vLLM, llama.cpp, Ollama, and oMLX. The examples configure a DFlash draft model and a short speculative block (typically seven tokens for Qwen3.8-27B); the exact package revisions include repository commits and pull-request branches. They show point-in-time integration instructions, not stable compatibility commitments or validated production configurations.[^inco-dflash2-2026]

The source states that rejection sampling preserves the target output distribution. That guarantee concerns sampling semantics, conditional on correct implementation, and should not be conflated with its acceptance results or throughput claims.[^inco-dflash2-2026]

## Relationships

- **Measures:** [DFlash 2 parallel selection and local convolution](dflash-2-parallel-selection-and-local-convolution.md).
- **Extends evidence for:** [DFlash evaluation and serving trade-offs](dflash-evaluation-and-serving-trade-offs.md), but uses different targets, drafters, and measurement conditions.
- **Qualified by:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md), because acceptance length alone cannot determine end-to-end speed.

## Evidence limits

The source is an Inco AI product announcement and reports no independent replication, full harness, hardware configuration, latency distribution, memory footprint, or training-cost amortization. Its reported acceptance and throughput can vary with target, dataset, sampling, speculative block size, batch/concurrency, backend, model quantization, and draft cost. The source’s ecosystem-adoption and download claims were not independently verified and are not used here as evidence of performance or maturity.[^inco-dflash2-2026]

[^inco-dflash2-2026]: Inco AI, “DFlash 2: Keep Drafting Parallel” (August 2026), [source](../raw/DFlash2.md), “Putting It Together,” “Two Drafters, Out Today,” “Run It Now,” and “The Bottom Line.”
