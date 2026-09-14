---
type: Concept
title: SGLang Hyperparameter Tuning
description: Offline batch-inference throughput tuning for SGLang covering queue depth, KV-cache utilization, memory fraction, chunked prefill, CUDA graphs, and parallelism.
tags: [sglang, throughput, tuning, kv-cache, cuda-graph, parallelism]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:01:05Z }
sources:
  - id: sgl-hypertune
    resource: ../raw/sglang/advanced_features/hyperparameter_tuning.mdx
    title: Hyperparameter Tuning
---

For offline batch inference, the largest throughput lever is achieving a large batch size; steady-state `Decode batch` logs (`#running-req`, `#token`, `token usage`, `cuda graph`, `gen throughput`, `#queue-req`) show whether submission speed, KV-cache utilization, and graph capture sustain full load[^sgl-hypertune].

## Request flow and queue depth

`#queue-req` is queued-request count[^sgl-hypertune]:

- Frequently `0` means client submission is too slow.
- Healthy range is `100-2000`.
- Too large increases server scheduling overhead.

## Token usage and schedule conservativeness

`token usage` is KV-cache memory utilization; `> 0.9` is good utilization[^sgl-hypertune].

- `token usage < 0.9` with `#queue-req > 0` means the server is too conservative about admitting requests; decrease `--schedule-conservativeness` to around `0.3`[^sgl-hypertune]. This happens when many requests declare large `max_new_tokens` but stop early via EOS or stop strings[^sgl-hypertune].
- Very high `token usage` with frequent `KV cache pool is full. Retract requests. #retracted_reqs: ..., #new_token_ratio: ...` warnings means the server is too aggressive; increase `--schedule-conservativeness` to around `1.3`[^sgl-hypertune]. Occasional retraction, about once per minute, is acceptable[^sgl-hypertune].

## Memory layout and mem-fraction-static

Total memory is[^sgl-hypertune]:

```text
Total = model weights + KV cache pool + CUDA graph buffers + activations
```

`--mem-fraction-static` controls the first two terms[^sgl-hypertune]:

```text
mem_fraction_static = (model weights + KV cache pool) / GPU memory capacity
```

To support higher concurrency, maximize KV-cache capacity by setting `--mem-fraction-static` as high as possible while reserving enough memory for activations and CUDA-graph buffers; SGLang heuristics set a default but workload-specific tuning helps[^sgl-hypertune].

Rule of thumb is to reserve 5–8 GB for activations. Before the server is ready, check logs like[^sgl-hypertune]:

```text
max_total_num_tokens=665690, chunked_prefill_size=8192, max_prefill_tokens=16384, max_running_requests=4096, context_len=65536, available_gpu_mem=13.50 GB
```

- `available_gpu_mem` 5–8 GB is good.
- 10–20 GB means increase `--mem-fraction-static` to give more memory to KV cache.
- Too low risks later OOM, so decrease `--mem-fraction-static`[^sgl-hypertune].

A simpler empirical method is to raise `--mem-fraction-static` in `0.01` increments until OOM for the target workload[^sgl-hypertune].

## OOM triage

- OOM during prefill: reduce `--chunked-prefill-size` to `4096` or `2048`; this saves memory but slows prefill for long prompts[^sgl-hypertune].
- OOM during decode: lower `--max-running-requests`[^sgl-hypertune].
- Either phase: reduce `--mem-fraction-static` to e.g. `0.8` or `0.7`; this shrinks the KV-cache pool and prevents OOM but limits maximum concurrency and peak throughput[^sgl-hypertune].

## CUDA graphs

By default CUDA graphs cover only small batch sizes, e.g. under `160` or `256`; for some models, especially at large tensor-parallelism sizes, graphs help up to batch `512` or `768`, so increasing `--cuda-graph-max-bs` can help[^sgl-hypertune]. CUDA graphs consume extra memory, so reducing `--mem-fraction-static` may be needed together[^sgl-hypertune].

## Data and tensor parallelism

Data parallelism is better for throughput; with enough GPU memory, favor data parallelism[^sgl-hypertune]. The source recommends the SGLang Model Gateway (former Router) for better data parallelism instead of the `dp_size` parameter[^sgl-hypertune].

## Other options

- `--enable-torch-compile`: `torch.compile` accelerates small models at small batch sizes[^sgl-hypertune].
- `--quantization fp8`: FP8 quantization example[^sgl-hypertune].
- Other parallelism: expert parallelism, or DP attention for DeepSeek models with `--enable-dp-attention --dp-size 8`[^sgl-hypertune].
- `--schedule-policy lpm`: when workloads share many prefixes, longest-prefix-match reorders requests for more cache hits at higher scheduling overhead[^sgl-hypertune].

## Relationships

- Uses [SGLang Expert Parallelism](sglang-expert-parallelism.md) — alternative parallelism strategy named as a tuning option for MoE and DeepSeek-style workloads.
- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) — shares `--mem-fraction-static` sizing; HiCache examples use `0.85` alongside hierarchical-cache flags.
- Uses [vLLM Chunked Prefill](vllm-chunked-prefill.md) — companion decode-prioritized chunking model useful for comparing SGLang `--chunked-prefill-size` OOM versus prefill-speed trade-offs.
- Uses [vLLM Memory Conservation](vllm-memory-conservation.md) — companion GPU-memory controls for comparing KV-cache pool, context/batch caps, and CUDA-graph sizing.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — companion DP/TP trade-off for comparing SGLang favor-DP throughput guidance.

## Coverage limits

- The linked SGLang Model Gateway (former Router) page and external expert-parallelism blog post were not inspected; gateway-based DP detail and EP kernel detail beyond the flag names above are not compiled here[^sgl-hypertune].
- No measured throughput numbers, model-specific defaults for `--cuda-graph-max-bs`, `--schedule-conservativeness`, or `--schedule-policy`, nor online-serving latency trade-offs beyond batch throughput were in the source[^sgl-hypertune].

[^sgl-hypertune]: Hyperparameter Tuning — `../raw/sglang/advanced_features/hyperparameter_tuning.mdx`.
