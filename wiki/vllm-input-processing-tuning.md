---
type: Concept
title: vLLM Input Processing Performance
description: fastokens Rust BPE backend and API-server scale-out for tokenizer and media bottlenecks.
tags: [vllm, tokenizer, fastokens, api-server, input-processing]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: opt-input
    resource: ../raw/vllm/configuration/optimization.md
    title: Optimization and Tuning
---

vLLM accelerates tokenizer-bound input and output paths with the optional `fastokens` Rust backend and scales API-server input processing independently of engine-core execution[^opt-input].

## fastokens backend

By default vLLM uses Hugging Face `tokenizers` for the fast tokenizer. For BPE tokenizers (Qwen, Llama, DeepSeek, GPT-OSS, and similar) `fastokens` is a drop-in Rust replacement that is substantially faster at encode, decode, and streaming detokenization[^opt-input].

Enable with `VLLM_USE_FASTOKENS=1` (available in vLLM v0.23.0 and later; upgrade if the variable is unrecognized)[^opt-input]:

```console
VLLM_USE_FASTOKENS=1 vllm serve Qwen/Qwen3-8B
```

```python
import os
os.environ["VLLM_USE_FASTOKENS"] = "1"

from vllm import LLM
llm = LLM(model="Qwen/Qwen3-8B")
```

Requirements and scope[^opt-input]:

- Requires `fastokens` Python package `>= 0.2.0`; vLLM raises `ImportError` at tokenizer load when missing.
- Applies to any `--tokenizer-mode` that loads an HF fast tokenizer (`hf`, `deepseek_v32`, `deepseek_v4`, and similar).
- Ignored by models without an HF fast tokenizer (`mistral`, `kimi_audio`).

Largest wins are tokenizer-bound workloads such as long shared prefixes, bursty short prompts, and batch detokenization; GPU prefill/decode-bound serving is unlikely to show end-to-end change[^opt-input].

## Parallel API-server processing

Run input processing in parallel via API-server scale-out when P0 work (inside the API server) bottlenecks P1 model execution (inside engine core) and excess CPU is available[^opt-input]:

```console
# 4 API processes and 1 engine core process
vllm serve Qwen/Qwen2.5-VL-3B-Instruct --api-server-count 4

# 4 API processes and 2 engine core processes
vllm serve Qwen/Qwen2.5-VL-3B-Instruct --api-server-count 4 -dp 2
```

Constraints[^opt-input]:

- Online inference only.
- By default each API server uses 8 CPU threads to load media items; when scaling out, adjust `VLLM_MEDIA_LOADING_THREAD_COUNT` to avoid CPU exhaustion.
- Scale-out disables multimodal IPC caching because that cache needs one-to-one API-to-engine correspondence; processor caching is unaffected.

## Relationships

- Uses [vLLM Hugging Face Integration](vllm-huggingface-integration.md) — HF fast-tokenizer loading that `VLLM_USE_FASTOKENS` replaces for BPE models.
- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — P0 API-server versus P1 engine-core split and `A + DP + N` process counts behind scale-out sizing.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — internal load-balancing deployment that API-server scale-out builds on.
- Uses [vLLM Multimodal Caching and Encoder Batch Parallelism](vllm-multimodal-caching.md) — processor cache survives scale-out while IPC cache does not; media-thread tuning complements multimodal cache sizing.

## Coverage limits

- `fastokens` upstream benchmarks and implementation, `../serving/data_parallel_deployment.md` internal-LB detail, and media-loading thread internals were not inspected beyond this source[^opt-input].

[^opt-input]: Optimization and Tuning — `../raw/vllm/configuration/optimization.md`, fastokens Backend and Parallel Processing sections covering BPE scope, `VLLM_USE_FASTOKENS` enablement and version/package requirements, tokenizer-mode scope and ignores, workload wins, `--api-server-count` examples with `-dp 2`, online-only scope, `VLLM_MEDIA_LOADING_THREAD_COUNT` warning, and IPC-cache interaction.
