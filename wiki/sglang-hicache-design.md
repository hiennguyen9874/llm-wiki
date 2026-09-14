---
type: Concept
title: SGLang HiCache System Design
description: Three-tier KV-cache hierarchy with HiRadixTree metadata, local-match / prefetch / write-back workflow, multi-rank sync, and zero-copy transfer optimizations.
tags: [sglang, hicache, kv-cache, radix-attention, prefill-decode-disaggregation]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:58:50Z }
sources:
  - id: sgl-hicache-design
    resource: ../raw/sglang/advanced_features/hicache_design.mdx
    title: HiCache System Design and Optimization
---

SGLang HiCache extends RadixAttention with a CPU-inspired three-level KV cache — private L1 GPU and L2 host tiers plus shared L3 distributed storage — coordinated by HiRadixTree metadata through local-match, L3 prefetch, and write-back stages[^sgl-hicache-design].

## Hierarchy and sharing model

- L1 is GPU memory, L2 is host memory, L3 is distributed storage; L1/L2 are private per inference instance while L3 is shared across instances in the cluster[^sgl-hicache-design].
- Goal is to reuse identical prefix KV for shared prompts, expanding capacity beyond idle GPU memory while preserving read performance for multi-QA and long-context reuse[^sgl-hicache-design].
- L3 backends named: Mooncake, DeepSeek 3FS/HF3FS, NIXL, AIBrix KVCache; LMCache is described as an alternative solution, not a HiCache backend[^sgl-hicache-design].

## HiRadixTree metadata

- Extends RadixAttention's RadixTree: each node covers a consecutive token span and records which tiers hold its KV — GPU, CPU, L3, or several[^sgl-hicache-design].
- Local tiers keep precise addresses; L3 metadata is not stored or continuously synced — existence/server/location is queried from the backend in real time[^sgl-hicache-design].

## Workflow

Three operations per request: **local match**, **prefetch**, **write-back**. New tokens are matched in L1/L2, misses are prefetched from L3 into L2, everything required is loaded to GPU for prefill, then new KV is considered for L2/L3 write-back[^sgl-hicache-design].

### Local match

- Traverse HiRadixTree from the root along the request prefix; when `page_size > 1` compare at page granularity[^sgl-hicache-design].
- A mid-node termination splits the node to create an exact boundary for future matches[^sgl-hicache-design].
- Returns a continuous prefix with the first part in L1 and latter part in L2; only tree traversal, no data copy, so very fast[^sgl-hicache-design].

### Prefetch from L3

- After local match, query L3 metadata for the next continuous span; prefetch triggers when the L3 hit length exceeds a threshold (default 256 tokens, configurable)[^sgl-hicache-design].
- Termination strategies[^sgl-hicache-design]:
  - `best_effort`: stop as soon as GPU can run prefill; no wait, latency-sensitive.
  - `wait_complete`: wait for all prefetches; highest reuse.
  - `timeout`: bounded wait balancing latency and hit rate; recommended for production SLOs.
- Timeout formula[^sgl-hicache-design]:

```text
timeout = prefetch_timeout_base + prefetch_timeout_per_ki_token * num_token_to_fetch / 1024
```

- `prefetch_timeout_base` covers token-independent overhead such as scheduling/sync; `prefetch_timeout_per_ki_token` adds per-thousand-token cost; both plus `prefetch_threshold` pass via `--hicache-storage-backend-extra-config` as JSON string or `@config.(toml|json|yaml)` file[^sgl-hicache-design].

### Write-back

- Policies[^sgl-hicache-design]:
  - `write_through`: every access written to next level; strongest caching when bandwidth suffices.
  - `write_through_selective`: write only after access frequency exceeds threshold; backs up hot data, less I/O.
  - `write_back`: write to next level only on upper-level eviction; least I/O pressure when capacity-limited.
- L2→L3 transfers skip data already present in L3; L3-resident KV is shareable across SGLang instances depending on backend implementation[^sgl-hicache-design].

## Multi-rank synchronization

- Under tensor parallelism, ranks synchronize with `all_reduce(op=min)` on L3 hit counts before deciding the prefetch threshold was met, and again on successfully fetched prefix length after prefetch stops/terminates[^sgl-hicache-design].

## Data transfer optimization

- **Zero-copy L2→L3**: pass memory address plus size directly to the L3 backend[^sgl-hicache-design].
- **Batch-oriented pages**: L3 stores/transfers at page granularity; `page_first` and `page_first_direct` place all KV of one page contiguously so it ships as a single zero-copy object, unlike `layer_first`[^sgl-hicache-design].
- **L2→GPU layout tradeoff**: GPU computes layer-by-layer (`layer_first`), so `page_first` L2→GPU moves one token per layer; `page_first_direct` groups all tokens of a layer within a page so transfers aggregate at page-layer granularity[^sgl-hicache-design].
- **CPU→GPU**: overlap layer N compute with layer N+1 KV load during prefill to hide transfer latency; GPU-assisted I/O kernels on top of `cudaMemcpyAsync` reach up to 3x baseline transfer speed[^sgl-hicache-design].
- **MLA write-back**: MHA under multi-TP shards each token (`1/tp_size` per rank) while MLA replicates complete identical KV on every rank, so only one rank performs write-back[^sgl-hicache-design].

## PD-disaggregation integration

- HiCache can run on prefill nodes, decode nodes, or both when SGLang uses Mooncake TransferEngine PD disaggregation; when enabled on decode nodes, decode output is also written back to L3[^sgl-hicache-design].

## Storage interface

- All L3 read/write/query operations are encapsulated in `class HiCacheStorage(ABC)` with uniform interfaces[^sgl-hicache-design].
- Backend notes[^sgl-hicache-design]:
  - Mooncake: RDMA + multi-NIC zero-copy transfers.
  - HF3FS: Kubernetes-native distributed storage with operator deployment.
  - NIXL: unified API over plugins including 3FS, GPU Direct Storage, S3-compatible storage.
  - AIBrix KVCache: production offload framework for memory tiering and cross-engine reuse.
  - HiCacheFile: simple file backend for demonstration.

## Key parameters

- `--enable-hierarchical-cache`: required master switch[^sgl-hicache-design].
- `--hicache-ratio`: host pool as multiple of device pool, must be > 1[^sgl-hicache-design].
- `--hicache-size`: host pool GB per rank (1GB = 1e9 bytes), overrides ratio when set; e.g. 30 with 8 ranks = 240GB total; must exceed device KV pool; larger size improves hits with diminishing returns once hot tokens are cached[^sgl-hicache-design].
- `--page-size`: tokens per page; larger pages cut metadata overhead and help I/O but can lower hit rate on partial-page matches — prefer larger for long common prefixes[^sgl-hicache-design].
- `--hicache-storage-prefetch-policy {best_effort,wait_complete,timeout}`[^sgl-hicache-design].
- `--hicache-write-policy {write_back,write_through,write_through_selective}`[^sgl-hicache-design].
- `--hicache-io-backend {direct,kernel}`: `direct` is plain CUDA copy, `kernel` is GPU-assisted I/O[^sgl-hicache-design].
- `--hicache-mem-layout {layer_first,page_first,page_first_direct}`[^sgl-hicache-design].
- `--hicache-storage-backend {file,mooncake,hf3fs,nixl,aibrix,dynamic}` plus `--hicache-storage-backend-extra-config` for JSON or `@file` backend options; dynamic mode needs `backend_name`, `module_path`, `class_name`[^sgl-hicache-design].
- `--enable-lmcache`: select LMCache instead of HiCache[^sgl-hicache-design].

## Relationships

- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) for deployment-tuned flag combinations, layout/backend compatibility constraints, and HF3FS/Mooncake examples.
- Depends on [SGLang Attention Backends](sglang-attention-backends.md) for the MHA/MLA execution context underlying the transfer and write-back optimizations.

## Coverage limits

- Linked benchmark blog, L3 backend guides, and PD-disaggregation doc were not inspected; no measured hit-rate, latency, or throughput numbers were compiled[^sgl-hicache-design].
- Architecture diagrams in the source were not inspected beyond captions[^sgl-hicache-design].

[^sgl-hicache-design]: HiCache System Design and Optimization — `../raw/sglang/advanced_features/hicache_design.mdx`.
