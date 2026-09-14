---
type: Concept
title: SGLang Deterministic Inference
description: Batch-invariant deterministic inference via --enable-deterministic-inference with FlashInfer, FA3, and Triton backend compatibility and seeded sampling.
tags: [sglang, determinism, batch-invariance, reproducibility]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:55:00Z }
sources:
  - id: sgl-det
    resource: ../raw/sglang/advanced_features/deterministic_inference.mdx
    title: Deterministic Inference
---

SGLang provides fully deterministic inference with batch-invariant operators, enabled by `--enable-deterministic-inference` on FlashInfer, FlashAttention 3, or Triton backends while retaining CUDA Graph, chunked prefill, and seeded non-greedy sampling support[^sgl-det].

Determinism matters for reinforcement-learning stability via consistent logprobs, reproducible testing and debugging, and production reliability; even `temperature=0` can otherwise diverge across runs because dynamic batching changes reduction order[^sgl-det].

## Root cause

Varying batch sizes cause GPU kernels to split reductions differently, changing floating-point addition order; because floating-point addition is non-associative (`(a + b) + c ≠ a + (b + c)`), identical inputs can yield different results[^sgl-det].

## Solution basis

The implementation builds on Thinking Machines Lab batch-invariant operators and is designed to remain compatible with chunked prefill, CUDA Graphs, radix cache, and non-greedy sampling; the feature roadmap is tracked in sglang issue `10278`[^sgl-det].

## Supported backends

Deterministic inference supports only FlashInfer, FlashAttention 3 (FA3), and Triton[^sgl-det]:

| Attention backend | CUDA Graph | Chunked prefill | Radix cache | Non-greedy sampling |
|---|---|---|---|---|
| FlashInfer | Yes | Yes | No | Yes |
| FlashAttention 3 (FA3) | Yes | Yes | Yes | Yes |
| Triton | Yes | Yes | Yes | Yes |

## Enabling

Add the flag and select a supported backend[^sgl-det]:

```bash
python3 -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --attention-backend fa3 \
    --enable-deterministic-inference
```

Server arguments in this source[^sgl-det]:

- `--enable-deterministic-inference`: flag, default disabled; enables batch-invariant operations.
- `--attention-backend`: string among `flashinfer`, `fa3`, or `triton`; source table lists default `fa3`.

Representative configurations[^sgl-det]:

```bash
# Qwen3-8B
python3 -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --attention-backend flashinfer \
    --enable-deterministic-inference

# Llama
python3 -m sglang.launch_server \
    --model-path meta-llama/Llama-3.1-8B-Instruct \
    --attention-backend fa3 \
    --enable-deterministic-inference

# Qwen3-30B-A3B MoE
python3 -m sglang.launch_server \
    --model-path Qwen/Qwen3-30B-A3B \
    --attention-backend fa3 \
    --enable-deterministic-inference
```

## Non-greedy sampling with seeds

Deterministic non-greedy sampling uses `sampling_seed`; the default seed is `42`, so an unseeded `temperature > 0` request reproduces across runs[^sgl-det].

For diverse but reproducible sampling, for example GRPO, send different seeds for the same prompt; each seed gives a different response, while reusing a seed reproduces that response[^sgl-det]:

```python
responses = []
for seed in [42, 43, 44, 45, 46]:
    response = requests.post(
        "http://localhost:30000/generate",
        json={
            "text": "Tell me a joke",
            "sampling_params": {
                "temperature": 0.8,
                "max_new_tokens": 128,
                "sampling_seed": seed,
            },
        },
    )
    responses.append(response.json())
```

## Verification

Run the deterministic test suite and expect `Unique samples: 1`[^sgl-det]:

```bash
# Same prompt under varying batch sizes
python3 -m sglang.test.test_deterministic --test-mode single --n-trials 50

# Prompts with different prefix lengths
python3 -m sglang.test.test_deterministic --test-mode prefix --n-trials 50

# Cached versus uncached prefill
python3 -m sglang.test.test_deterministic --test-mode radix_cache
```

## Coverage limits

- Performance cost, hardware requirements, and model-specific validation are not quantified in this source[^sgl-det].
- Roadmap issue `10278` and Thinking Machines Lab operator internals were not inspected beyond this source[^sgl-det].

## Relationships

- Uses [SGLang Attention Backends](sglang-attention-backends.md) — deterministic mode is restricted to the FlashInfer, FA3, and Triton subset selected via `--attention-backend`.
- Uses [vLLM Batch Invariance](vllm-batch-invariance.md) — vLLM counterpart via `VLLM_BATCH_INVARIANT` for comparing deterministic-inference enablement and RL reproducibility use cases.

[^sgl-det]: Deterministic Inference — `../raw/sglang/advanced_features/deterministic_inference.mdx`.
