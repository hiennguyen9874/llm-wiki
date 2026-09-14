---
type: Concept
title: vLLM HiSparse Local KV Offload
description: Local host-tier KV offload for sparse attention with coordinator-owned host blocks, spill-before-free residency, and fused GPU hot lookup.
tags: [vllm, kv-cache, offloading, sparse-attention]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: hisparse
    resource: ../raw/vllm/design/hisparse.md
    title: HiSparse local KV offload architecture
---

HiSparse is an experimental local KV connector that spills resident GPU blocks to pinned host memory and serves sparse-attention decode from resident pages first, then GPU hot rows, then pinned host memory inside one fused resolver[^hisparse].

> [!warning] Experimental design
> The source marks HiSparse as experimental and CUDA-only; ROCm is not currently supported[^hisparse].

## Three jobs

The design separates three responsibilities[^hisparse]:

1. Normal KV cache system manages GPU block pools and tables.
2. `HiSparseCoordinator` manages logical host blocks, source-prefix identity, and host/GPU residency transitions.
3. `HiSparseConnector` carries residency work between scheduler and worker; `HiSparseWorker` coordinates transfers, while per-cache `HiSparseRuntime` objects own host/hot views and GPU replacement state.

Neither worker-side object allocates or frees logical blocks. HMA provides the GPU allocation shared by resident and hot groups; it does not manage CPU memory or KV identity[^hisparse].

```text
request ────► HiSparseCoordinator ── source blocks + residency policy
                    │
                    ├──► KV cache manager ── resident/hot GPU leases (HMA)
                    │
                    └──► HiSparseConnector ── host bytes + copies + GPU LRU
```

This is a local KV connector. When P/D or another offload connector is also configured, `MultiConnector` composes it with `HiSparseConnector`[^hisparse].

## Ownership

Logical allocation versus contents is the key distinction: `HiSparseCoordinator` owns host block IDs and request/prefix associations, while `HiSparseWorker` and per-cache runtimes own the corresponding bytes. The normal cache manager sees only device pools[^hisparse].

| Thing | Owner |
| --- | --- |
| HiSparse source and prefix identity | `HiSparseCoordinator` maps tokens to logical host blocks |
| Resident GPU block leases | normal KV cache manager allocates and frees HMA blocks |
| Resident block tables | normal KV cache manager tells attention where resident pages are |
| Residency transitions | `HiSparseCoordinator` plans spill-before-free transactions |
| Logical host block allocation | `HiSparseCoordinator` owns the separate CPU block pool lifecycle |
| Pinned host-pool lifecycle | `HiSparseWorker` owns worker-wide backing and teardown |
| Per-cache host view and hot contents | `HiSparseRuntime` binds host/hot storage and fills cache-manager-provided hot leases |
| Hot row map and LRU | `HiSparseRuntime` resolves hits and chooses GPU victims |
| Resident-cache route | `HiSparseCacheHandle` exposes resident or host/hot resolution to attention |
| Sparse attention | attention backend consumes a device cache and physical row IDs |
| HMA | allocator provides GPU capacity with no KV meaning |

The source group has `block_pool_id=None`; device-pool consumers must narrow it before indexing, so host ownership cannot masquerade as a numeric GPU pool[^hisparse].

## Host capacity and tensor-parallel layout

`host_pool_gib` is configured on `HiSparseConnector` and is the usable host-cache capacity per data-parallel replica, not a node-wide memory budget. Tensor-parallel ranks hold replicated views of that logical cache. Those views may use private per-rank backing or one shared physical allocation without changing the configured capacity. Physical host memory consumption is therefore topology- and implementation-dependent. Realized capacity may be slightly smaller because the budget is rounded down to complete host blocks[^hisparse].

For single-node MP tensor parallelism, every TP worker maps the same pinned host pool and uses the same block and layer offsets. MLA source KV is replicated across TP ranks, so this stores one physical copy instead of one copy per rank. TP rank 0 writes the shared host pool; peers wait on its IPC events before reading it. Other executor and parallel layouts retain private per-rank pools[^hisparse].

The shared layout backs the per-replica logical capacity with one physical pool; the private layout allocates one physical pool per rank. Physical pool size includes block-stride alignment[^hisparse].

## Scheduler/worker boundary

```text
scheduler process                           worker process

HiSparseConnector                          HiSparseConnector
  └─ HiSparseCoordinator                         └─ HiSparseWorker
       │                                          │
       │ connector metadata                       ├─ host bytes
       │ - page transfers                         ├─ copy scheduling
       │ - block-table replacements               └─ per-layer hot state
       └───────────────────────────────────────────────►│
       ◄──────── connector worker metadata ─────────────┘
                    enqueued and completed transfer IDs
```

The command travels in `kv_connector_metadata`; transfer updates return in `KVConnectorOutput.kv_connector_worker_meta`. The model runner does not interpret page transfers. Enqueue acknowledgements let the scheduler release source leases in stream order; completion acknowledgements publish the copied host pages[^hisparse].

## Resident device pages and fused resolver

Resident pages are intentionally outside `HiSparseRuntime`. KV-cache initialization binds cache-manager allocations to the attention-facing `HiSparseCacheHandle` before constructing `HiSparseWorker`. That same handle's runtime retains the resident source index needed by a transfer plan. There is no second resident object or registration wrapper. `HiSparseWorker` registers the same `HiSparseCacheHandle` objects directly[^hisparse].

Every HiSparse decode batch uses the same fused resolver. It checks resident pages first, then hot rows, then pinned host memory. A resident hit exits inside the kernel before hot-LRU lookup or host copying; there is no framework-level residency route or separate CUDA graph. No CPU decision is added to the decode path. The resolver consumes the existing graph-stable request mapping from attention metadata; neither the worker nor individual cache handles keep a duplicate mapping[^hisparse].

Additional binding rules[^hisparse]:

- Attention construction links each layer to the most recent layer that actually owns an indexer. This releases a follower's duplicate LRU tensors before GPU memory profiling.
- Cache binding only attaches storage; it does not infer semantic groups from physical packed-tensor order.
- The construction cursor is discarded with the worker's pinned state.
- Speculative decoding resolves and consumes each verification step in order. Each step receives distinct replayable plan rows while sharing the request's hot-cache state, so a later step cannot reuse a hot row before an earlier step has consumed it.

## P/D import target

The decoder chooses the landing target once per request from the normal cache admission calculation. If the complete imported prefix fits the device pools, NIXL transfers it directly into resident GPU pages. Otherwise, if the fixed host-backed GPU footprint and host source blocks fit, the request imports into the host tier. There is no context-length threshold or other heuristic, and a request waiting for capacity retains its choice across admission retries[^hisparse].

A host import reads through a bounded decoder-GPU staging pool before copying into registered host memory. Pages needed immediately are mirrored into their resident destinations during that copy. Both landing targets then use the same fused decode resolver[^hisparse].

## Indexer KV offloading

HiSparse does not keep a private CPU copy of indexer KV. The indexer remains a normal prefix-cacheable GPU cache group. If `OffloadingConnector` is configured with HiSparse, it stores and restores that group through the generic KV offloading path; HiSparse continues to own only the sparse MLA host tier[^hisparse].

The two prefix sources can have different hit lengths. When the HiSparse host prefix extends beyond the GPU-resident indexer prefix, the scheduler asks `OffloadingConnector` to restore only the missing indexer suffix, capped at the host prefix boundary. If that suffix is unavailable, all groups fall back to the shorter prefix they share. NIXL P/D transfers continue to place indexer KV directly in its GPU group[^hisparse].

## Spill transaction

A resident block cannot be reused until its contents have been handed to the worker[^hisparse]:

```text
HiSparseCoordinator                            HiSparseWorker
          │                                     │
          │ pin source and destination leases   │
          │── SparseKVPageTransfer ─────────────►│
          │                                     │ enqueue GPU-to-host copy
          │◄── enqueued transfer ID ────────────│
          │ replace resident table entry        │
          │ release resident lease to HMA       │
          │                                     │ copy reaches its event
          │◄── completed transfer ID ───────────│
          │ mark host page valid                │
          │ release destination host lease      │
```

- **Enqueued** means the copy has entered the worker stream. Stream ordering makes it safe to reuse the resident GPU block for later work, but the host page is not yet published.
- **Completed** means the worker has observed the copy's event; only then does the coordinator publish the host page for prefix reuse and release its destination lease.
- A host-write event separately protects direct CPU readers from writes already queued on the accelerator.
- The worker transfer contains only its transfer ID and physical copy coordinates. Request identity and logical page state remain in the scheduler[^hisparse].

## Hot lookup and LRU

The NVIDIA CUDA path keeps replacement entirely on the accelerator[^hisparse]:

```text
top-K logical positions
        │
        ▼
resident page? ── yes ──► resident physical row
        │ no
        ▼
hot row? ──────── yes ──► existing hot physical row + update GPU LRU
        │ no
        ▼
choose GPU LRU victim ──► copy pinned host row ──► hot physical row
```

ROCm is not currently supported because the fused HiSparse cache operations are implemented only by CUDA kernels. A future platform-specific worker may provide the same command, output, and cache-resolution boundaries[^hisparse].

## Main classes

| Class | Inherits / implements | Responsibility |
| --- | --- | --- |
| `HiSparseCoordinator` | plain scheduler component | host allocation, source prefixes, resident leases, and spill state machine |
| `HiSparseConnector` | `KVConnectorBase_V1`, `SupportsHMA` | scheduler/worker metadata and lifecycle boundary |
| `HiSparseResidentManager` | `SingleTypeKVCacheManager` | normal block-pool bookkeeping with host-backed holes |
| `PagedCacheView` | immutable data object | shared resident/hot HMA tensor binding |
| `HiSparseWorker` | connector-owned worker component | worker-wide transfer scheduling and host-pool lifecycle |
| `HiSparseRuntime` | plain worker-owned component | per-cache host/hot tensors, GPU LRU, and fused resolution |
| `SparseKVOffloadCommand` | dataclass | opaque scheduler-to-worker work |
| `HiSparseCacheHandle` | plain attention component | resident view and fused cache resolution |

Table content follows the source's class summary[^hisparse].

## Performance invariants

- Resident hits bypass hot-LRU lookup and host copies inside the fused resolver.
- Hot lookup, victim selection, and LRU updates stay on the GPU.
- A hot miss still copies directly from registered pinned host memory.
- Top-K resolution stays inside the attention invocation and remains graph capturable.
- Compatible layers still share one miss plan.
- Index-sharing followers release their private LRU state before memory sizing.
- Indexer KV is untouched by HiSparse unless a generic KV offloader is configured.
- Resident and hot leases can still share one packed HMA allocation.
- No device scalar readback or CPU/device metadata round trip is added.
- The abstraction wraps the fused kernel; it does not add another kernel launch.
- When HiSparse is disabled, the scheduler does not construct an offload command or empty update table[^hisparse].

## What remains platform-specific

The command/result and attention-layer boundaries can be shared. The host allocator, copy implementation, hot layout, and replacement policy should stay platform-specific. NVIDIA uses the current accelerator LRU and fused host/hot kernel. AMD or other accelerator backends can implement their own worker without forcing NVIDIA's policy into the shared boundary[^hisparse].

## Relationships

- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) per-group allocation pattern; `HiSparseResidentManager` extends `SingleTypeKVCacheManager` with host-backed holes.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) identity and reuse model; the coordinator's source-prefix mapping and completed-spill publication feed host-page prefix reuse.
- Uses [vLLM NIXL KV Cache Lease Renewal](vllm-nixl-kv-lease.md) transfer path for the P/D import landing decision; NIXL places fitting prefixes directly in resident pages.
- Depends on [vLLM Attention Backends](vllm-attention-backends.md) sparse-attention consumption of a device cache and physical row IDs.
- Depends on [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) graph-capturable execution; the fused resolver adds no separate CUDA graph.

## Coverage limits

- Compiled from the design document alone; implementation classes, `MultiConnector`, `OffloadingConnector`, HMA, and NIXL behavior were not verified beyond this source[^hisparse].
- No local attachments were referenced by the source, so no additional `raw/` evidence was inspected.

[^hisparse]: HiSparse local KV offload architecture — `../raw/vllm/design/hisparse.md`, short version, ownership, code boundary, resident pages, P/D import, indexer offloading, spill transaction, hot lookup and LRU, main classes, performance invariants, and platform-specific sections.
