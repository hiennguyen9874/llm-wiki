---
type: Concept
title: W8A8 INT8 Accuracy and Performance Results
description: Llama 3.1 8B Instruct W8A8 INT8 case study where accuracy deltas stayed within benchmark noise while serving throughput and latency improved with load-dependent ITL overhead.
tags: [quantization, w8a8, evaluation, vllm, performance]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: w8a8-results
    resource: ../raw/understanding-w8a8-int8-llm-quantization-accuracy-and-performance-results/index.md
    title: 'Understanding W8A8 INT8 LLM quantization: Accuracy and performance results'
---

Llama 3.1 8B Instruct compressed from 14.9 GB to 8.0 GB with INT8 W8A8 quantization using SmoothQuant plus GPTQ and WikiText-2 calibration retained accuracy within benchmark noise across four tasks while improving concurrency, throughput, and latency on a single NVIDIA L40S, with inter-token latency gains narrowing under high concurrency because of dynamic activation-quantization overhead[^w8a8-results].

## Accuracy setup

- Evaluated base and compressed models with `lm-eval-harness` under identical zero-shot conditions, same tasks, and same hardware[^w8a8-results].
- Benchmarks covered factual knowledge with MMLU across 57 subjects, scientific reasoning with ARC Easy, commonsense reasoning with HellaSwag, and instruction following with IFeval[^w8a8-results].

## Accuracy results

| Benchmark | Base | Compressed | Delta |
| --- | --- | --- | --- |
| MMLU | 0.6322 | 0.6311 | -0.0011 |
| ARC Easy acc | 0.8136 | 0.8106 | -0.0030 |
| HellaSwag acc_norm | 0.7251 | 0.7277 | +0.0026 |
| IFeval inst strict | 0.8189 | 0.8237 | +0.0048 |

Table values are source-reported[^w8a8-results].

### Deltas versus standard error

| Benchmark | Delta | Standard error | Within noise? |
| --- | --- | --- | --- |
| MMLU | -0.0011 | ±0.0038 | Yes, about 3.5× smaller |
| ARC Easy | -0.0030 | ±0.0080 | Yes, about 2.7× smaller |
| HellaSwag | +0.0026 | ±0.0045 | Yes, about 1.7× smaller |
| IFeval | +0.0048 | not reported | Likely, similar magnitude |

The source interprets standard error as expected run-to-run score variation; every reported delta was smaller than that variation, so quantization did not measurably degrade accuracy on the tested benchmarks[^w8a8-results].

### MMLU by category

| Category | Base | Compressed | Delta |
| --- | --- | --- | --- |
| Humanities | 0.5864 | 0.5911 | +0.0047 |
| STEM | 0.5062 | 0.5043 | -0.0019 |
| Social Sciences | 0.7442 | 0.7394 | -0.0048 |
| Other | 0.7184 | 0.7132 | -0.0052 |

All four category deltas were described as within noise[^w8a8-results].

## W8A8 versus W8A16 context

- Red Hat AI published a W8A16 GPTQ version of the same model via llm-compressor with accuracy reported within 1% of baseline across MMLU, ARC-Challenge, HellaSwag, and others; the source treats this as consistent with its W8A8 preservation result[^w8a8-results].
- The comparison is directional rather than exact because the source used zero-shot raw-text log-likelihood scoring while the Red Hat AI evaluation used 5-shot chat-template generation-based scoring[^w8a8-results].
- The durable distinction is that W8A8 quantizes weights and activations to INT8 and can use faster INT8 tensor cores, while W8A16 quantizes only weights and still computes in BF16, saving memory without compute speedup[^w8a8-results].

## Performance setup

- Served both models with vLLM and drove production-like load with GuideLLM using 1,024 input tokens and 512 output tokens per synthetic request, sourced from *Pride and Prejudice* text at the time of the experiment[^w8a8-results].
- Used the same single NVIDIA L40S with 46 GB VRAM, same server configuration, and same ramp from synchronous requests to maximum throughput[^w8a8-results].

## Performance results

- Model size: 14.9 GB to 8.0 GB, about 46% smaller[^w8a8-results].
- Maximum concurrency: 34 to 44 requests, +29%, attributed to roughly 7 GB freed for KV cache where each concurrent request keeps its own per-layer keys and values[^w8a8-results].
- Time to first token: 115.9 ms to 87.9 ms synchronous, -24%; 147.0 ms to 119.7 ms at maximum load, -19%. Prefill over all 32 Llama 3.1 8B layers benefits from INT8 matrix multiplication[^w8a8-results].
- Inter-token latency: 22.2 ms to 14.7 ms synchronous, -34%; 39.6 ms to 34.5 ms at maximum load, -13%[^w8a8-results].
- Output throughput at maximum load: 576.5 to 829.7 tokens/sec, +44%, combining faster per-token generation and higher concurrency[^w8a8-results].
- Request latency: 11.4 s to 7.6 s synchronous, -33%; 20.4 s to 17.8 s at maximum load, -13%[^w8a8-results].
- ITL degradation ratio from synchronous to maximum load: base 39.6 / 22.2 = 1.78× versus compressed 34.5 / 14.7 = 2.34×. The compressed model degraded faster but remained absolutely faster at maximum tested load[^w8a8-results].
- Service-level check of p95 TTFT ≤ 200 ms at maximum concurrency: base 162.4 ms at 34 requests passed and compressed 136.0 ms at 44 requests passed[^w8a8-results].

## Why the gain narrows under load

- W8A8 adds per-layer runtime activation quantization and dequantization around the faster INT8 matrix multiplication: measure activation range, compute scale, convert to INT8, run INT8 MatMul, then convert back to BF16[^w8a8-results].
- Activations use per-token quantization with one shared scale across that token's channels; the source describes per-channel activation quantization as mathematically impractical and adds that separate scales for all 4,096 channels would add substantial overhead[^w8a8-results].
- At 44 concurrent requests across 32 layers, the source counts 44 × 32 = 1,408 quantize-dequantize cycles per decode step, none of which exist in the base model[^w8a8-results].
- The source explanation is that INT8 matrix multiplication becomes compute-bound because weights load once and reuse across requests, while quantize and dequantize remain memory-bound per activation, so their share grows with concurrency and shrinks the synchronous 34% ITL advantage to 13% at maximum load[^w8a8-results].

## Fit, watchouts, and next steps

Consider W8A8 INT8 when memory constrains single-GPU deployment, server throughput and concurrency matter, faster time to first token is needed, both memory and compute savings are wanted rather than W8A16 memory-only savings, or older Ampere GPUs and CPUs with W8A8 INT8 support must be used while W8A8 FP8 needs newer Hopper or Blackwell hardware[^w8a8-results].

Watch calibration data, layer selection, and high-concurrency behavior:

- Monitor ITL scaling for very high-concurrency workloads because dynamic activation-quantization overhead grows with load[^w8a8-results].
- Prefer calibration data matched to deployment domain and style over generic WikiText-2; the source names UltraChat as a chat-application example[^w8a8-results].
- Keep the `lm_head` layer in full precision to protect token-selection quality[^w8a8-results].

The source suggests domain-matched calibration experiments, W4A16 where memory savings outweigh compute speedup, FP8 on newer GPU architectures, and multi-GPU serving to distribute dynamic-quantization overhead[^w8a8-results].

## Relationships

- Complements [W8A8 INT8 Quantization Mechanics](w8a8-int8-quantization-mechanics.md) — part-1 mechanics for the same Llama 3.1 8B experiment covering naive-quantization failure, GPTQ Hessian compensation, SmoothQuant gamma smoothing, and calibration guidance.
- Uses [vLLM LLM Compressor Quantization Workflows](vllm-llm-compressor-workflows.md) — provides measured accuracy and serving evidence for the SmoothQuant plus GPTQ INT8 W8A8 recipe.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — broader hardware and format context for choosing W8A8 INT8 versus W8A16 or FP8.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — complementary evaluation perspective emphasizing KL divergence, trajectory checks, and calibration leakage beyond single-task accuracy deltas.

## Coverage limits

- Both local figures were inspected: the base-versus-compressed performance bar chart and the per-layer BF16 versus W8A8 inference flowchart matched the surrounding prose.
- Numbers, hardware behavior, and method explanations are source-reported and were not independently reproduced.
- The source's end-to-end `model-serve-flow` repository link was recorded as a search-URL string in the source and was not verified as a resolvable repository address.

[^w8a8-results]: Sana Fayyaz, Understanding W8A8 INT8 LLM quantization: Accuracy and performance results — `../raw/understanding-w8a8-int8-llm-quantization-accuracy-and-performance-results/index.md`, accuracy tables and standard-error interpretation, MMLU category breakdown, W8A16 comparison, vLLM plus GuideLLM performance setup and L40S results, TTFT/ITL/throughput/latency/SLO figures, dynamic activation-quantization overhead model, fit/watchout/next-step recommendations, and benchmark references.
