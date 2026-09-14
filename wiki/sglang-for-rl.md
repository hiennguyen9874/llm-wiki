---
type: Concept
title: SGLang for RL Systems
description: RL post-training integration for SGLang covering engine sleep/wake, three weight-refit paths, pause/continue generation, deterministic inference, and gateway routing.
tags: [sglang, rl, rollout, weight-update, memory-management, determinism]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:59:16Z }
sources:
  - id: sgl-rl
    resource: ../raw/sglang/advanced_features/sglang_for_rl.mdx
    title: SGLang for RL Systems
  - id: sgl-p2p-update
    resource: ../raw/2026-04-29-p2p-update/index.md
    title: "Updating 1T parameters in seconds — P2P weight transfer in Large Scale Distributed RL"
  - id: qwen38-day0
    resource: ../raw/2026-08-12-qwen3-8-day0-support/index.md
    title: 'SGLang and Miles Add Day-0 Support for Qwen3.8'
---

SGLang supports RL and post-training loops as flexible tooling ("be a library, not a framework") focused on rollout, evaluation, training, and weight-sync pain points: fine-grained sleep/wake, open refit paths, postponable generation, deterministic inference, and cache-aware routing[^sgl-rl].

## Engine sleep and wake

Co-located rollout and training contend for GPU memory; SGLang releases KV cache and weights while keeping the server alive, avoiding restarts, repeated disk I/O, and CUDA-graph recapture per RL step[^sgl-rl]. Implementation uses CUDA-graph-aware weight offload via `torch_memory_saver` to preserve virtual addresses for graph replay[^sgl-rl].

Enable with server flag[^sgl-rl]:

```text
--enable-memory-saver
```

- `POST /release_memory_occupation` with optional `tags` (`kv_cache`, `weights`; omitted means all)[^sgl-rl]. Asserts no ongoing requests, so call only when idle; releasing `kv_cache` flushes cache and later requests rebuild it[^sgl-rl].
- `POST /resume_memory_occupation` with optional `tags` (`kv_cache`, `weights`; omitted means all)[^sgl-rl].

## Weight refit paths

After each training step, rollout engines refit weights via one of three paths[^sgl-rl]:

| Path | Best for | Trade-off |
|---|---|---|
| From disk | Checkpoint-based updates, elastic scaling, HA | Extra I/O, simplest and safest |
| From tensor | Co-located training/rollout with in-memory tensors | Fast, requires shared tensor access and GPU-resident model |
| From distributed | Disaggregated training/rollout over NCCL/IB | No disk I/O, requires dedicated communication group |

### From disk

`POST /update_weights_from_disk` — save checkpoint, point rollout at it; new instances can join by loading the same checkpoint[^sgl-rl].

Request fields[^sgl-rl]:

- `model_path` (str, required): new weights path.
- `load_format` (str, default `None`).
- `abort_all_requests` (bool, default `False`).
- `weight_version` (str, default `None`): tracked version label.
- `is_async` (bool, default `False`).
- `torch_empty_cache` (bool, default `False`).
- `keep_pause` (bool, default `False`): keep scheduler paused after update.
- `recapture_cuda_graph` (bool, default `False`).
- `token_step` (int, default `0`): trainer step id for rollout bookkeeping.
- `flush_cache` (bool, default `True`).

Response fields: `success` (bool), `message` (str), `num_paused_requests` (int, default `0`)[^sgl-rl].

Python API: `engine.update_weights_from_disk(model_path, load_format=None)`[^sgl-rl].

### From tensor

`POST /update_weights_from_tensor` for fast co-located in-memory updates[^sgl-rl]. Training and rollout must share tensor access; keep the model on GPU because CPU offload breaks this path; co-location may limit some MoE or specialized-attention optimizations[^sgl-rl].

Request fields[^sgl-rl]:

- `serialized_named_tensors` (list[str], required): per-TP payloads created with `MultiprocessingSerializer.serialize(...)` as base64-safe strings.
- `load_format` (`None`, `direct`, `flattened_bucket`, or custom loader path; default `None`).
- `flush_cache` (bool, default `True`).
- `abort_all_requests` (bool, default `False`).
- `weight_version` (str, default `None`).

Python API: `engine.update_weights_from_tensor(named_tensors, load_format=None, flush_cache=True)`[^sgl-rl].

### From distributed group

Training workers gather weights (typically TP rank 0) and broadcast to the rollout group; each rollout TP shard loads its slice[^sgl-rl].

- `POST /init_weights_update_group`: `master_address` (str, required), `master_port` (int, required), `rank_offset` (int, required), `world_size` (int, required), `group_name` (str, default `weight_update_group`), `backend` (str, default `nccl`)[^sgl-rl].
- `POST /update_weights_from_distributed`: `names` (list[str], required), `dtypes` (list[str], required), `shapes` (list[list[int]], required), `group_name` (default `weight_update_group`), `flush_cache` (bool, default `True`), `abort_all_requests` (bool, default `False`), `weight_version` (str, default `None`), `load_format` (`None` or `flattened_bucket`, default `None`)[^sgl-rl].
- `POST /destroy_weights_update_group`: `group_name` (default `weight_update_group`)[^sgl-rl].

Python APIs: `engine.init_weights_update_group(...)`, `engine.update_weights_from_distributed(names, dtypes, shapes, ...)`, `engine.destroy_weights_update_group(group_name)`[^sgl-rl].

### P2P RDMA supplement

For large MoE RL, Miles with SGLang supplements NCCL broadcast with an RDMA peer-to-peer path using source-side CPU replicas and Mooncake TransferEngine, cutting 1T-parameter sync from ~53s to ~7.2s; it reuses the same pause-update-continue discipline and is enabled via `--update-weight-transfer-mode p2p`[^sgl-p2p-update]. Detail is maintained in [SGLang P2P Weight Transfer for RL](sglang-p2p-weight-transfer.md).

## Postponable generation

Multi-turn rollouts stall on long-tail requests; SGLang lets operators pause slow requests and continue later rather than discarding partial work, matching patterns such as APRIL-style early termination and incomplete-response recycling[^sgl-rl].

Correct weight-update flow is `pause_generation` — update weights — `continue_generation`, because updates require the engine to be idle[^sgl-rl].

- `POST /pause_generation` with `mode` (default `abort`)[^sgl-rl]:
  - `abort`: as `abort` endpoint with `abort_all`; returns pending `waiting_queue` and `running_queue` requests to callers.
  - `retract`: enters paused state, moves running requests back to waiting queue; KV cache can be flushed and recomputed later.
  - `in_place`: enters paused state without moving requests; running requests depend on live KV cache, so later `flush_cache` will fail.
- `POST /continue_generation`: resumes generation; no request body documented in this source[^sgl-rl].

## Deterministic inference

Rollout/training kernel and batching differences can drift token probabilities even with identical weights, breaking the on-policy assumption; SGLang's deterministic mode reduces batch-shape non-determinism, while true on-policy training additionally requires matching deterministic kernels on the training side[^sgl-rl].

Enable with[^sgl-rl]:

```text
--enable-deterministic-inference
```

Detail, backend matrix, and seeded sampling are maintained in [SGLang Deterministic Inference](sglang-deterministic-inference.md).

## Gateway routing for rollouts

SGLang Model Gateway is the recommended control plane for large-scale rollouts, deployed for GLM 4.5+ training: async non-blocking serving, independent rollout/reward servers, training-inference alignment ("What You See Is What You Get"), and request-level dynamic dispatch across multi-turn conversations to mitigate long tails[^sgl-rl].

Benefits claimed in this source[^sgl-rl]:

- Maximum GPU saturation and continuous batching without manual concurrency logic.
- Fault tolerance: failed rollout/reward servers drain via router redirect.
- Same gateway stack for training and inference avoids backend-mismatch score gaps.
- Cross-server per-turn dispatch instead of static partitioning.

Deployment and policy detail is maintained in [SGLang Model Gateway](sglang-model-gateway.md).

## Qwen3.8 colocated LoRA verification

Qwen3.8 Day-0 RL instantiates colocated training with Miles: a BF16 Megatron trainer plus native NVFP4 SGLang rollout engines sharing the same 64 GB300s, with rank-32 adapters on attention projections trained with GRPO; a short GSM8K run shows steadily climbing reward/eval with flat train/rollout KL[^qwen38-day0]. Full inference and kernel context is maintained in [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md).

## Relationships

- Uses [SGLang P2P Weight Transfer for RL](sglang-p2p-weight-transfer.md) — RDMA P2P supplement to NCCL broadcast with CPU replicas and TransferEngine for large-MoE RL updates.
- Uses [SGLang Deterministic Inference](sglang-deterministic-inference.md) — RL on-policy use of `--enable-deterministic-inference`.
- Uses [SGLang Model Gateway](sglang-model-gateway.md) — cache-aware gateway routing and fault tolerance for large-scale rollouts.
- Uses [vLLM Sleep Mode](vllm-sleep-mode.md) — vLLM counterpart for levelled sleep/wake and partial weights/KV-cache restore in RLHF colocation.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — launch surface for `--enable-memory-saver` and `--enable-deterministic-inference`.
- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — Day-0 verified RL pipeline pairing SGLang rollout with Miles Megatron training, FP8/QAT/R3 stability, and DAPO verification.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — Qwen3.8 colocated BF16-trainer plus NVFP4-rollout rank-32 LoRA GRPO verification on 64 GB300s.
- Related to [Miles DeepSeek-V4.1 Verified RL](miles-deepseek-v41-rl.md) — V4.1 colocated training and rollout with shared attention state, FP4/FP8 QAT, and bucketed BF16 weight transfer on 16 GB300s.

## Coverage limits

- Linked `torch_memory_saver`, verl memory-management post, weight-update tutorial, APRIL paper, Miles true-on-policy examples, and mismatch blog were not inspected beyond this source[^sgl-rl].
- Inline code comment pins release/resume `tags` to `kv_cache` and `weights` via `io_struct.py`; current server code was not inspected[^sgl-rl].
- Throughput, stability, and GLM-scale efficiency claims are source statements without supporting measurements in this source[^sgl-rl].

[^sgl-rl]: SGLang for RL Systems — `../raw/sglang/advanced_features/sglang_for_rl.mdx`, covering library-not-framework rationale, `--enable-memory-saver` with `/release_memory_occupation` and `/resume_memory_occupation`, disk / tensor / distributed weight-refit APIs, `/pause_generation` modes with `/continue_generation`, `--enable-deterministic-inference`, and Model Gateway rollout routing.

[^sgl-p2p-update]: Updating 1T parameters in seconds — P2P weight transfer in Large Scale Distributed RL — `../raw/2026-04-29-p2p-update/index.md`, covering RDMA P2P supplement with CPU replicas and TransferEngine, Kimi-K2 53s→7.2s result, and `--update-weight-transfer-mode p2p` usage.
[^qwen38-day0]: SGLang and Miles Add Day-0 Support for Qwen3.8 — `../raw/2026-08-12-qwen3-8-day0-support/index.md`, covering colocated BF16-trainer plus NVFP4-rollout rank-32 LoRA GRPO GSM8K verification on 64 GB300s.
