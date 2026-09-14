---
type: Concept
title: vLLM Batch Invariance
description: Deterministic batch-size-independent inference via VLLM_BATCH_INVARIANT with hardware, backend, and model coverage.
tags: [vllm, determinism, batch-invariance, reproducibility]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:03:08Z }
sources:
  - id: batch-inv
    resource: ../raw/vllm/features/batch_invariance.md
    title: Batch Invariance
---

Batch invariance makes model output deterministic and independent of batch size or request order, enabled with `VLLM_BATCH_INVARIANT=1` for both offline and server inference[^batch-inv].

The feature is in beta and trades performance for reproducibility by using deterministic kernels and disabling certain non-deterministic optimizations[^batch-inv].

## Motivation

Deterministic batch-independent outputs support[^batch-inv]:

- Framework debugging with repeatable behavior across batch configurations.
- Model-implementation debugging with consistent behavior.
- Reinforcement-learning rollouts requiring reproducibility and stable training.
- Large-scale inference systems needing testing, validation, and consistency guarantees.

## Hardware and backend requirements

Supported platforms[^batch-inv]:

- NVIDIA GPUs with compute capability 8.0 or higher.
- Intel XPUs with Triton support.

On XPU, the Triton Attention backend is required[^batch-inv]:

```python
llm = LLM(model="Qwen/Qwen3-1.7B", attention_config={"backend": "TRITON_ATTN"})
```

```bash
VLLM_BATCH_INVARIANT=1 vllm serve Qwen/Qwen3-1.7B \
  --attention-config.backend TRITON_ATTN
```

## Enabling

Set the environment variable[^batch-inv]:

```bash
export VLLM_BATCH_INVARIANT=1
```

Online server mode[^batch-inv]:

```bash
VLLM_BATCH_INVARIANT=1 vllm serve meta-llama/Llama-3.1-8B-Instruct
```

With sampling seed set, OpenAI-compatible requests then produce deterministic outputs regardless of batching[^batch-inv].

Offline inference[^batch-inv]:

```python
import os
os.environ["VLLM_BATCH_INVARIANT"] = "1"
```

Construct `LLM` normally and call `llm.generate(prompts, sampling_params)` with a fixed `seed` in `SamplingParams`; outputs are deterministic regardless of batch size[^batch-inv].

## Tested models

Explicitly validated at source time[^batch-inv]:

- DeepSeek: `DeepSeek-V3`, `DeepSeek-V3-0324`, `DeepSeek-R1`, `DeepSeek-V3.1`.
- Qwen3 dense: `Qwen3-1.7B`, `Qwen3-8B`, `Qwen3-4B-AWQ`, `Qwen3-8B-AWQ`.
- Qwen3-VL: `Qwen3-VL-2B-Instruct`, `Qwen3-VL-4B-Instruct` with single image and video inputs.
- Qwen3 MoE: `Qwen3-30B-A3B`, `Qwen3-Next-80B-A3B-Instruct`, `Qwen3-30B-A3B-Thinking-2507-FP8`.
- Qwen2.5: `0.5B`, `1.5B`, `3B`, `7B`, `14B`, and `32B` Instruct variants.
- Llama 3: Llama 3.1 and 3.2 series, including `Llama-3.2-3B-Instruct`.
- GPT-OSS: `gpt-oss-20b`, `gpt-oss-120b`.
- Mistral: `Mistral-7B-v0.3`.
- Phi: `Phi-3.5-mini-instruct`.
- Granite 3.1 MoE: `granite-3.1-1b-a400m-instruct`, `granite-3.1-3b-a800m-instruct`.
- Granite 3.1 dense: `granite-3.1-2b-instruct`, `granite-3.1-8b-instruct`.
- EXAONE 4.0: `EXAONE-4.0-1.2B`, `EXAONE-4.0.1-32B`, `EXAONE-4.0-32B`.
- OLMo 2: `OLMo-2-0425-1B-Instruct`.

Other models may work but have not been explicitly validated; model-specific issues belong on the vLLM GitHub issue tracker[^batch-inv].

## Implementation and limits

When enabled, vLLM uses deterministic attention and related kernel implementations, keeps numerical behavior consistent across batch sizes, and disables optimizations that can introduce non-determinism such as custom all-reduce operations in tensor-parallel mode[^batch-inv].

Enabling batch invariance may reduce performance relative to default non-deterministic mode; the trade-off is intentional for reproducibility[^batch-inv].

Planned work covers additional GPU architectures, expanded model coverage, performance optimization, and further testing and validation[^batch-inv].

## Coverage limits

- Beta status; active development continues under the referenced tracking issue, which was not inspected beyond the source[^batch-inv].
- Validated model list is a point-in-time snapshot; unlisted models are unknown rather than unsupported[^batch-inv].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — XPU batch invariance requires the Triton attention backend.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — the same flag applies to offline `LLM` and online `vllm serve` paths.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — deterministic mode disables custom all-reduce optimizations in tensor-parallel mode.

[^batch-inv]: Batch Invariance — `../raw/vllm/features/batch_invariance.md`.
