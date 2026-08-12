---
type: Concept
title: DSpark speculator evaluation and deployment
description: "DSpark cards report target-specific acceptance evidence: Kimi K3 holds about 4.26 at one-million-token context, while Nemotron averages 3.75 on SPEED-Bench without latency results."
tags: [speculative-decoding, evaluation, long-context, sglang, kimi-k3]
status: stable
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-12T14:46:56Z }
sources:
  - id: kimi-k3-dspark-card
    resource: ../raw/KimiK3DSparkspeculator.md
    title: "Kimi K3 DSpark speculator (Hugging Face model card)"
  - id: nemotron-dspark-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md
    title: NVIDIA Nemotron 3.5 Lightning DSpark model card
---

# DSpark speculator evaluation and deployment

The Kimi K3 DSpark speculator card reports SGLang `acc_len` between 2.99 and 5.51 across eight benchmarks, with average acceptance largely holding at about 4.26 even at one-million-token RULER V2 contexts. AIME26 acceptance dips for mid-length outputs and rebounds for very long outputs, while the card reports no end-to-end latency or speedup numbers. It also documents the SGLang serving configuration for the draft on a 1M-token Kimi K3 target.[^kimi-k3-dspark-card]

## Acceptance-length metric

`acc_len` is SGLang's histogram-native request acceptance length, averaged within each question and then equally across questions. It measures how many draft tokens are accepted per round on average — a proxy for draft–target alignment — not wall-clock speedup. Realized latency still depends on draft cost, verification width, batching, and serving overhead.[^kimi-k3-dspark-card]

## Reported results

| Dataset | Questions | acc_len |
|---|---:|---:|
| SWE-Rebench | 50 | **4.6594** |
| GSM8K | 1,319 | **5.4176** |
| MATH500 | 500 | **4.1329** |
| HumanEval | 164 | **5.5121** |
| MBPP | 257 | **5.1980** |
| MT-Bench | 80 | **3.9342** |
| AIME26 | 30 | **2.9893** |
| RULER V2 1M (MK/MV/QA) | 150 (50 per partition) | **4.2553** |

RULER V2 uses the 1M input configuration; actual prompts span 1,000,432–1,047,925 tokens. Partition acc_len is 4.4658 for MK, 4.3081 for MV, and 3.9919 for QA, so long-context acceptance does not collapse at one million tokens in this configuration.[^kimi-k3-dspark-card]

### AIME26 acc_len by output length

| Output-token bucket | Questions | Actual output range | acc_len |
|---|---:|---:|---:|
| 0–1K | 13 | 192–885 | **3.1310** |
| 1–2K | 5 | 1,359–1,828 | **2.5773** |
| 2–4K | 6 | 2,210–3,732 | **2.5632** |
| 4–8K | 4 | 5,187–7,750 | **2.7174** |
| 8–16K | 0 | — | — |
| 16–32K | 0 | — | — |
| 32K+ | 2 | 54,545–224,703 | **4.9194** |

Acceptance is weakest for 1–4K-token outputs (about 2.56–2.58) and strongest for the two very long outputs (about 4.92), suggesting acceptance varies with output regime rather than being constant per dataset.[^kimi-k3-dspark-card]

## Nemotron checkpoint comparison

For a draft length of seven, NVIDIA’s Nemotron 3.5 Lightning DSpark card reports SPEED-Bench accepted length from 2.83 (writing) to 4.55 (multilingual), averaging 3.75 across eleven categories at temperature 1.0/top-p 0.95. Its same-source DFlash card reports 3.16 overall under the stated matching setup, so DSpark has higher acceptance in every listed category. This does not establish lower latency: DSpark is also larger (967M versus 833M total parameters), and neither card supplies end-to-end speed, concurrency, memory, or confidence-scheduling measurements. The DSpark card also inconsistently lists llama.cpp under inference test engines after naming only vLLM as a supported runtime, so llama.cpp support remains unclear.[^nemotron-dspark-card]

## Serving configuration

The Kimi card points to the SGLang Cookbook recipe for Kimi K3 with DSPARK and highlights the draft-relevant flags:

- `--speculative-algorithm DSPARK` with `--speculative-draft-model-path RadixArk/Kimi-K3-DSpark`.
- `--speculative-dspark-block-size 7`, draft attention backend `trtllm_mha`, and `--enable-linear-replayssm-spec`.
- `--context-length 1048576` with `--chunked-prefill-size 16384`.
- YaRN-16 is enabled in the published draft config by default, so no separate draft config override is required.[^kimi-k3-dspark-card]

## Relationships

- **Evidences:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md) with concrete acceptance lengths at long context.
- **Measures:** [DSpark parallel-draft speculative decoding](dspark-parallel-draft-speculative-decoding.md).
- **Deploys with:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md) and the [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) target.

## Evidence limits

The card is an author-run artifact: `acc_len` is acceptance quality, not end-to-end speedup, and no TTFT, token-throughput, or latency measurements are provided. AIME26 has only 30 questions and no questions in the 8–16K or 16–32K output buckets; the 32K+ rebound rests on just two outputs. Each RULER V2 partition uses 50 questions. No comparison against the K3 report's EAGLE-3-style draft is included, and results may not transfer to other workloads, batch sizes, or serving conditions.[^kimi-k3-dspark-card]

[^kimi-k3-dspark-card]: RadixArk, “Kimi K3 DSpark speculator,” Hugging Face model card, [source](../raw/KimiK3DSparkspeculator.md), Evaluation Results and Serving with SGLang.

[^nemotron-dspark-card]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning DSpark,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md), Software Integration, Training Dataset, Inference, and Evaluation.
