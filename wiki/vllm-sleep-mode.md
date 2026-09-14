---
type: Concept
title: vLLM Sleep Mode
description: Releasing GPU memory via levelled sleep/wake with partial weights and KV-cache restore for RLHF and colocation.
tags: [vllm, inference, memory-management, rlhf]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: sleep-mode
    resource: ../raw/vllm/features/sleep_mode.md
    title: Sleep Mode
---

vLLM Sleep Mode temporarily releases most GPU memory used by a model, including weights and KV cache, without stopping the server or unloading the container, enabling fast resume and GPU sharing for RLHF, training, and cost-saving colocation[^sleep-mode].

## Capabilities

- Frees up to 90%+ GPU memory by offloading weights to CPU RAM and discarding KV cache[^sleep-mode].
- Fast resume without full model reload[^sleep-mode].
- Control via Python API or HTTP endpoints[^sleep-mode].
- Supports distributed workloads including tensor parallelism and pipeline parallelism[^sleep-mode].
- Fine-grained partial wake-up of weights only or KV cache only to avoid OOM during weight updates[^sleep-mode].
- Supported on CUDA and ROCm platforms[^sleep-mode].

## Sleep levels

- **Level 1:** offloads model weights to CPU and discards KV cache; KV content is forgotten. Weights are backed up in CPU memory, so sufficient CPU RAM is required. Intended for sleeping and waking the same model[^sleep-mode].
- **Level 2:** discards both model weights and KV cache, while keeping model buffers in CPU such as RoPE scaling tensors. Both weights and KV content are forgotten. Intended for running a different model after wake-up or updating weights, for example RLHF weight updates. Also useful when CPU memory cannot hold a weights backup, for example when a colocated trainer already offloads its own state; after wake-up restore weights with `collective_rpc("reload_weights")`[^sleep-mode].

## Offline inference

Enable with `enable_sleep_mode=True` in the `LLM` class[^sleep-mode]:

```python
from vllm import LLM
llm = LLM("Qwen/Qwen3-0.6B", enable_sleep_mode=True)
```

Level 1 sleep/wake[^sleep-mode]:

```python
llm.sleep(level=1)
llm.wake_up()
```

Level 2 sleep with staged wake-up[^sleep-mode]:

```python
llm.sleep(level=2)
llm.wake_up(tags=["weights"])
llm.collective_rpc("reload_weights")
llm.wake_up(tags=["kv_cache"])
```

For RLHF weight updates, wake only `tags=["weights"]`, perform the update, then wake `tags=["kv_cache"]` to minimize peak memory and avoid OOM with large models. `is_sleeping` reports `true` until all components are awake[^sleep-mode].

## Online serving

Start the server with development mode and the sleep-mode flag; development endpoints must not be exposed to users[^sleep-mode]:

```bash
VLLM_SERVER_DEV_MODE=1 vllm serve Qwen/Qwen3-0.6B \
  --enable-sleep-mode \
  --port 8000
```

Level 1 example[^sleep-mode]:

```bash
curl -X POST 'http://localhost:8000/sleep?level=1'
curl -X POST 'http://localhost:8000/wake_up'
```

Level 2 example with staged wake-up[^sleep-mode]:

```bash
curl -X POST 'http://localhost:8000/sleep?level=2'
curl -X POST 'http://localhost:8000/wake_up?tags=weights'
curl -X POST 'http://localhost:8000/collective_rpc' -H 'Content-Type: application/json' -d '{"method":"reload_weights"}'
curl -X POST 'http://localhost:8000/wake_up?tags=kv_cache'
```

HTTP endpoints[^sleep-mode]:

- `POST /sleep?level=1` — put model to sleep.
- `POST /wake_up` — wake model; supports optional `tags` query parameter for partial wake-up, for example `?tags=weights`.
- `POST /collective_rpc` — perform collective RPC.
- `GET /is_sleeping` — check sleeping state.

These endpoints are only available with `VLLM_SERVER_DEV_MODE=1`[^sleep-mode].

## Limitations

On ROCm, virtual-memory allocation uses chunked allocation controlled by `VLLM_ROCM_SLEEP_MEM_CHUNK_SIZE` in MB, default 256MB. Larger chunks are faster but risk OOM; reduce chunk size on OOM. Power-of-2 values are recommended[^sleep-mode].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — sleep/wake is exposed through both offline `LLM` APIs and online serving endpoints.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — sleep mode works across tensor-parallel and pipeline-parallel deployments.

[^sleep-mode]: Sleep Mode — `../raw/vllm/features/sleep_mode.md`.
