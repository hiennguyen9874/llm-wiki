---
type: Concept
title: vLLM TurboQuant KV-Cache Quantization
description: Storage-only 3–4-bit KV-cache compression whose accuracy and serving trade-offs were measured against FP8 and BF16 across long-context and reasoning workloads.
tags: [vllm, quantization, kv-cache, turboquant, fp8]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T00:00:00Z }
sources:
  - id: turboquant-study
    resource: ../raw/2026-05-11-turboquant/index.md
    title: 'A First Comprehensive Study of TurboQuant: Accuracy and Performance'
---

TurboQuant compresses only KV-cache storage to 3–4 bits and dequantizes to BF16 for attention, while FP8 KV-cache also quantizes the attention computation with hardware-native FP8 Tensor Core operations; in the Red Hat AI vLLM study FP8 remained the best default at 2x capacity with negligible accuracy loss, TurboQuant 4-bit-NC traded extra capacity for moderate accuracy, latency, and throughput costs, and aggressive 3-bit variants degraded accuracy and performance enough to avoid in production[^turboquant-study].

## Mechanism and variants

- TurboQuant is storage-only compression: low-bit KV storage, BF16 attention after dequantization. FP8 stores queries, keys, and values in FP8 and executes attention in FP8[^turboquant-study].
- Studied flags are `--kv-cache-dtype turboquant_{k8v4, 4bit_nc, k3v4_nc, 3bit_nc}` versus BF16 and `--kv-cache-dtype fp8`[^turboquant-study].
- `k8v4` uses 8-bit keys and 4-bit values; `4bit_nc` uses 4-bit keys and values with norm correction; `k3v4_nc` uses 3-bit keys and 4-bit values with norm correction; `3bit_nc` uses 3-bit keys and values with norm correction[^turboquant-study].
- Example usage[^turboquant-study]:

```bash
# FP8 KV-cache for all layers
vllm serve MiniMaxAI/MiniMax-M2.7 --kv-cache-dtype fp8

# TurboQuant KV-cache
vllm serve MiniMaxAI/MiniMax-M2.7 --kv-cache-dtype turboquant_4bit_nc
```

- At the time of writing TurboQuant supported only standard attention mechanisms such as GQA; sliding-window or hybrid attention models were unsupported[^turboquant-study].

## Study scope

- Models: `Llama-3.3-70B-Instruct`, `Qwen3-30B-A3B-Instruct-2507`, `Qwen3-30B-A3B-Thinking-2507`, and `MiniMax-M2.7`, spanning dense and MoE architectures from 30B to 200B+ parameters[^turboquant-study].
- Long-context retrieval used `openai/mrcr` multi-round retrieval up to each model's maximum length, reporting pass@1 per length bucket and AUC aggregate; reasoning used AIME25, GPQA:Diamond, MATH500, and LiveCodeBench-v6 with model-creator non-greedy sampling[^turboquant-study].
- Performance used vLLM `0.20.2` with `Qwen3-30B-A3B-Instruct-2507` on 2xH100 and `Llama-3.3-70B-Instruct` on 4xH100, measuring latency (`bench latency`, 1024 input / 256 output, batch 1/8/32/64), offline throughput (`bench throughput`, 200 prompts, 256/256, 1024/512, 4096/256), and serving TPOT plus P99 TTFT (`bench serve`, 1024/512, 300 prompts, rates 2/8/burst)[^turboquant-study].

## Accuracy findings

- Long context on Llama-3.3-70B up to 64k: higher-bit `k8v4` and `4bit_nc` preserved retrieval with competitive AUC near 52%; `k3v4_nc` at 48.6% and `3bit_nc` at 50.3% degraded consistently, widening to about 8 points at 64k. At 128k the BF16 baseline itself collapsed below 10%[^turboquant-study].
- Long context on Qwen3-30B-A3B-Instruct up to 256k: BF16 45.8%, FP8 43.1%, `k8v4` 43.0%, and `4bit_nc` 42.3% stayed competitive, while `k3v4_nc` fell to 33.5% and `3bit_nc` to 31.2% AUC, about 30% relative degradation concentrated at 128k–256k, suggesting low-bit errors accumulate with sequence length[^turboquant-study].
- Reasoning on Qwen3-30B-A3B-Thinking: FP8 and `k8v4` recovered over 98% of BF16 average accuracy; `4bit_nc` recovered about 96%; `k3v4_nc` and `3bit_nc` dropped by roughly 20 points on hard tasks, with even MATH500 down about 4 points[^turboquant-study].
- Reasoning on MiniMax-M2.7: FP8 and `k8v4` maintained over 99% recovery; `4bit_nc` showed a modest drop; aggressive variants still lost up to about 8 points on AIME25 and LiveCodeBench-v6 despite larger-model robustness[^turboquant-study].

## Performance findings

- Latency overhead versus BF16: FP8 had negligible or no overhead across models and batch sizes; TurboQuant added about 10–60% on Qwen3-30B and 10–68% on Llama-70B, with Llama overhead tending to increase with batch size because dequantization cost grows with accessed KV volume[^turboquant-study].
- Offline throughput versus BF16: FP8 matched BF16; TurboQuant was strictly below BF16, about 80% for `k8v4` down to 73% for `3bit_nc` on Qwen3-30B and 75% down to 66% on Llama-70B, with more aggressive packing yielding lower throughput[^turboquant-study].
- Serving TPOT: FP8 tracked or beat BF16 at all request rates; TurboQuant added per-token overhead growing with load, and at Llama-70B burst FP8 was nearly 2x faster than BF16 while TurboQuant variants were 1.5–2.5x slower[^turboquant-study].
- Serving P99 TTFT: on Qwen3-30B with memory headroom FP8 matched BF16 while TurboQuant was consistently slower up to 2x at burst; on memory-constrained Llama-70B burst, BF16 exploded to about 17s from KV saturation and queuing, TurboQuant stayed under 3.5s, and FP8 was lowest at about 1.3s[^turboquant-study].
- Pareto summary: on Llama-70B FP8 gave about 2.6x higher burst throughput than BF16 at 2x KV capacity, with all TurboQuant variants trading throughput for extra memory; on Qwen3-30B FP8 matched BF16 throughput at 2x capacity while TurboQuant extended capacity to about 2.3–3.7x at 40–52% throughput reduction[^turboquant-study].
- Reported capacities: FP8 2x, `k8v4` about 2.4x, and `4bit_nc` up to about 3.4x KV-cache capacity[^turboquant-study].

## Recommendations from the study

- Stay with FP8 as the default KV-cache quantization: 2x capacity, no throughput cost, negligible accuracy loss, and sometimes better performance through quantized attention[^turboquant-study].
- Do not prefer `k8v4` over FP8: its extra saving of about 2.4x versus 2x did not justify consistent throughput and latency penalties[^turboquant-study].
- Consider `4bit_nc` only under KV-cache memory pressure or edge memory constraints where burst-TTFT improvement outweighs moderate accuracy, latency, and throughput costs; validate accuracy on the target workload first because degradation is typically 1–4 points[^turboquant-study].
- Avoid `k3v4_nc` and `3bit_nc` in production without thorough validation because of large drops on reasoning and very long-context tasks plus dequantization-driven performance loss[^turboquant-study].
- Stay with BF16 when memory is not a bottleneck: short contexts, low concurrency, or ample hardware give the best accuracy-performance trade-off without quantization artifacts[^turboquant-study].

## Relationships

- Uses [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md) — FP8 storage, calibration, layer skips, and backend constraints that form the baseline this TurboQuant comparison is judged against.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — broader weight and KV format selection context for choosing between BF16, FP8, and TurboQuant paths.

## Coverage limits

- Plot images under `../raw/2026-05-11-turboquant/assets/` were not visually re-measured; numerical claims follow the post text and figure captions.
- Linked TurboQuant paper, vLLM TurboQuant API documentation, FP8 KV-cache post, and Context Arena methodology were not independently inspected.
- Results are point-in-time vendor-reported evidence for the listed models, benchmarks, H100 topologies, and vLLM `0.20.2`; do not generalize to other hardware, backends, or hybrid/sliding-window attention.

[^turboquant-study]: Eldar Kurtić, Michael Goin, Alexandre Marques (Red Hat AI), A First Comprehensive Study of TurboQuant: Accuracy and Performance — `../raw/2026-05-11-turboquant/index.md` (2026-05-11), covering TurboQuant versus BF16/FP8 architecture, four variants, four dense/MoE models, mrcr plus four reasoning benchmarks, H100 latency/throughput/serve methodology, AUC and accuracy-recovery numbers, throughput/TTFT trade-offs, capacity multipliers, and deployment recommendations.
