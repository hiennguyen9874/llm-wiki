---
type: Concept
title: SGLang HiCache Best Practices
description: Hierarchical KV-cache tuning for SGLang covering memory layout, prefetch policies, PD disaggregation, HF3FS and Mooncake deployment, and custom backends.
tags: [sglang, hicache, kv-cache, prefill-decode-disaggregation, hf3fs, mooncake]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:59:44Z }
sources:
  - id: sgl-hicache-bp
    resource: ../raw/sglang/advanced_features/hicache_best_practices.mdx
    title: SGLang HiCache Best Practices
---

SGLang HiCache extends RadixAttention with a three-tier hierarchical KV cache across GPU memory, host memory, and external storage, improving hit rates for long-context and multi-turn workloads by relieving GPU capacity limits[^sgl-hicache-bp].

## Core parameters

Enable and size HiCache with[^sgl-hicache-bp]:

- `--page-size 64`: page size for cache management.
- `--enable-hierarchical-cache`: enable HiCache.
- `--hicache-ratio 2`: host memory as multiple of GPU memory.
- `--hicache-size 100`: host memory size in GB; overrides `--hicache-ratio` when set.
- `--hicache-io-backend kernel`: CPU-GPU transfer backend.
- `--hicache-write-policy write_through`: GPU-to-CPU write policy.
- `--hicache-storage-backend`: optional external store such as `hf3fs` or `mooncake`.

Storage backends can also be attached or detached at runtime without restart via HTTP admin endpoints; see [SGLang HiCache Runtime Storage Attach/Detach](sglang-hicache-runtime-attach-detach.md) for the endpoint workflow[^sgl-hicache-bp].

## Memory layout

- `page_first`: I/O-efficient zero-copy layout, recommended with the `kernel` backend[^sgl-hicache-bp].
- `page_first_direct`: direct-I/O layout with the same zero-copy performance as `page_first`; compatible with FA3[^sgl-hicache-bp].
- `layer_first`: alternative layer-major layout[^sgl-hicache-bp].

Compatibility constraint: `page_first` works only with the `kernel` I/O backend and automatically falls back to `layer_first` with the `direct` backend; use `page_first_direct` when running `direct`[^sgl-hicache-bp].

```bash
--hicache-mem-layout page_first
--hicache-mem-layout page_first_direct
--hicache-mem-layout layer_first
```

## Prefetch policies

- `best_effort`: abort storage prefetch when resources are needed elsewhere[^sgl-hicache-bp].
- `wait_complete`: wait for full prefetch; higher cache reuse at higher latency cost[^sgl-hicache-bp].
- `timeout`: bounded wait balancing completion against best-effort behavior[^sgl-hicache-bp].

```bash
--hicache-storage-prefetch-policy best_effort
--hicache-storage-prefetch-policy wait_complete
--hicache-storage-prefetch-policy timeout
```

## PD disaggregation integration

Two supported patterns[^sgl-hicache-bp]:

1. **Prefill-only HiCache**: enable HiCache on prefill nodes for KV sharing across prefill instances; suited to shared system-prompt reuse.
2. **Full HiCache with async offload**: enable HiCache on prefill nodes plus `--disaggregation-decode-enable-offload-kvcache` on decode nodes so prefill can reuse decode-offloaded KV in multi-turn dialogue.

Both example deployments use `--page-size 64`, `--hicache-ratio 2`, `--hicache-size 0`, `--hicache-mem-layout page_first_direct`, `--hicache-io-backend direct`, `--hicache-write-policy write_through`, `--hicache-storage-backend hf3fs`, `--hicache-storage-prefetch-policy wait_complete`, plus `--disaggregation-mode prefill|decode`, `--disaggregation-transfer-backend mooncake`, and `--disaggregation-ib-device mlx5_0`; the prefill example adds `--mem-fraction-static 0.85` with `--enable-metrics` and `--enable-cache-report`[^sgl-hicache-bp].

## HF3FS deployment

DeepSeek-R1 example combines `--enable-hierarchical-cache`, `--mem-fraction-static 0.85`, `--page-size 64`, `--hicache-ratio 2`, `--hicache-size 0`, `--hicache-mem-layout page_first_direct`, `--hicache-io-backend direct`, `--hicache-write-policy write_through`, `--hicache-storage-backend hf3fs`, and `--hicache-storage-prefetch-policy wait_complete`[^sgl-hicache-bp].

## Mooncake deployment

Qwen3-235B-A22B-Instruct-2507 example sets Mooncake environment variables before launch[^sgl-hicache-bp]:

```bash
export MOONCAKE_TE_META_DATA_SERVER="http://127.0.0.1:8080/metadata"
export MOONCAKE_GLOBAL_SEGMENT_SIZE=816043786240
export MOONCAKE_PROTOCOL="rdma"
export MOONCAKE_DEVICE="$DEVICE_LIST"
export MOONCAKE_MASTER=127.0.0.1:50051
```

Launch flags use `--hicache-mem-layout page_first_direct`, `--hicache-io-backend direct`, `--hicache-storage-backend mooncake`, `--hicache-write-policy write_through`, and `--hicache-storage-prefetch-policy timeout` with `--page-size 64`, `--enable-hierarchical-cache`, and `--hicache-ratio 2`[^sgl-hicache-bp].

## Custom storage backends

Implement `get(key)`, `exists(key)`, and `set(key, value)`, then register the backend in HiCache `BackendFactory`; the HiCache controller handles scheduling and synchronization[^sgl-hicache-bp].

To avoid hard-coding, use dynamic loading[^sgl-hicache-bp]:

```bash
--hicache-storage-backend dynamic \
--hicache-storage-backend-extra-config '{"backend_name":"custom_backend_name", "module_path": "your_module_path", "class_name": "YourHiCacheClassName"}'
```

Extra-config fields are `backend_name`, `module_path`, `class_name`, and `interface_v1` (`0`/`1`) controlling use of `batch_get_v1` and `batch_set_v1`[^sgl-hicache-bp].

## Relationships

- Uses [SGLang HiCache Runtime Storage Attach/Detach](sglang-hicache-runtime-attach-detach.md) for the runtime attach/detach HTTP workflow and idle-state safety checks.

## Coverage limits

- HF3FS setup guide, Mooncake store guide, and `BackendFactory` registration code were linked but not inspected; only the flag and interface names above were compiled[^sgl-hicache-bp]. Runtime attach/detach endpoint syntax is compiled in [SGLang HiCache Runtime Storage Attach/Detach](sglang-hicache-runtime-attach-detach.md).
- No measured hit-rate, latency, or throughput numbers, `hicache-size 0` semantics, or `kernel` versus `direct` selection guidance beyond layout compatibility were in the source[^sgl-hicache-bp].

[^sgl-hicache-bp]: SGLang HiCache Best Practices — `../raw/sglang/advanced_features/hicache_best_practices.mdx`.
