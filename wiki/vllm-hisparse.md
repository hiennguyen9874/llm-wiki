---
type: Concept
title: vLLM HiSparse Local KV Offload
description: Hybrid pressure-driven host-tier KV offload for sparse attention with shared-pool hot buffers, three residency states, and GLM-5.3 deployment evidence.
tags: [vllm, kv-cache, offloading, sparse-attention, hybrid, glm-5.3]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: hisparse
    resource: ../raw/vllm/design/hisparse.md
    title: HiSparse local KV offload architecture
  - id: hybrid-blog
    resource: ../raw/2026-09-08-glm53-part1-hybrid-sparse-offloading/index.md
    title: 'GLM 5.3 Optimizations, Part 1: Hybrid HiSparse Offloading in vLLM'
---

HiSparse is an experimental local KV connector that spills resident GPU blocks to pinned host memory and serves sparse-attention decode from resident pages first, then GPU hot rows, then pinned host memory inside one fused resolver[^hisparse].

Hybrid HiSparse is a pressure-driven residency policy over the same mechanism: KV starts GPU-resident and only gives up residency page by page when the shared HMA pool runs short, so CPU–GPU transfer cost is paid only under KV-cache pressure at higher concurrency[^hybrid-blog].

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

## Hybrid residency policy

Dense offload still bounds concurrency by GPU memory because dense attention needs every token resident; preemption instead drops KV and pays full TTFT again on eviction[^hybrid-blog]. For sparse-MLA KV, the indexer selects top-K tokens and attends only to those, so HiSparse offloads everything except selected tokens to CPU and bounds per-request GPU memory[^hybrid-blog]. Indexer KV stays GPU-resident and grows with context, but it is much smaller, and GLM-5.3 IndexShare means one indexer layer per four sparse-MLA layers[^hybrid-blog].

Residency is tracked per page, with three states as pressure rises and falls[^hybrid-blog]:

- **Full residency**: all sparse-MLA KV stays GPU-resident while completed prefix pages are proactively materialized in host memory.
- **Mixed residency**: the request tail stays on GPU, older pages live only in CPU, and indexer-selected rows from those pages sit in hot buffers. The block table holds real blocks and null placeholders side by side, and the tail is never evicted.
- **No residency**: a new request reusing a CPU-only prefix starts with placeholders plus a hot page; rows arrive as the indexer selects them, paying for attended tokens rather than the whole history.

In mixed residency one fused kernel resolves top-K: resident tokens read in place, hot tokens read with LRU refresh, and a miss copies a single row from pinned host memory into an LRU slot. No decode-path step waits on a CPU decision, so the path stays CUDA-graph-capturable[^hybrid-blog].

## Shared-pool hot buffers and proactive staging

Hot buffers are not a separate allocation: a hot-buffer page is an ordinary KV-cache block leased from the same HMA pool and same KV-cache tensor as resident pages, taken when a request first needs one and returned when it does not[^hybrid-blog]. Hot-buffer pages are indexed by tokens, so one page can hold tokens drawn from many CPU blocks; tokens can coexist in hot buffers and GPU-resident pages, reducing CPU reloads[^hybrid-blog]. The resolver hands HMA row IDs for both locations and HMA gathers them with one stride; a block freed by one request can become hot-buffer capacity for another[^hybrid-blog].

HiSparse prepares before pressure arrives: when a cacheable prefix page completes, it queues a CPU copy while continuing to serve from GPU, so a later-full pool can release the GPU slot without another copy[^hybrid-blog]. Even when pressure reaches a newer page first, its GPU slot becomes reusable once the copy is queued, and the CPU copy becomes available for prefix reuse when the transfer completes[^hybrid-blog]. The `hisparse-glm` branch copies all sparse-MLA layers together in one launch after the forward pass, ordered on the model GPU stream[^hybrid-blog].

Defaults and layout from the blog[^hybrid-blog]:

- Hot buffers default to 2× top-K rows per request for high hit rates at small size.
- MLA KV is identical across TP ranks, so the pinned host pool is allocated per DP replica and shared across its local TP ranks; TP rank 0 writes the shared copy, every rank reads it, with a CUDA event preserving stream ordering.
- `host_pool_gib` is per DP replica and rounded to whole host blocks.

## Composition with vLLM KV machinery

Hybrid HiSparse is a residency policy over the shared HMA pool and a connector alongside other KV machinery; other cache groups keep normal prefix caching, transfer, and offloading[^hybrid-blog]. Specifically:

- Indexer KV is untouched by HiSparse and can be offloaded independently by the standard OffloadingConnector with ordinary block-granular storage[^hybrid-blog].
- P/D disaggregation imports can land host-side when a prefix does not fit resident[^hybrid-blog].
- Speculative decoding works through per-step replayable resolver plans sharing the request hot state[^hybrid-blog].

## GLM-5.3 8×H200 deployment evidence

On a single aggregated 8×H200 node tight on memory for GLM-5.3, Hybrid HiSparse enables full 1M context length — previously impossible on that hardware — with substantially higher concurrency across context lengths[^hybrid-blog].

Benchmark setup both sides used TP8, MTP3, FP8 KV cache, 142K admission limit, `max_num_batched_tokens=32768`, `max_num_seqs=256`, and `gpu_memory_utilization=0.92` on an OpenHands multi-turn agentic workload: 13-turn conversations with 74,160-token first turn, 753-token later turns, and fixed 220-token outputs[^hybrid-blog]. The same host budget was split as 512 GiB offload pool for the baseline versus 384 GiB HiSparse pool plus 128 GiB offloading for cache groups HiSparse does not manage, including indexer KV[^hybrid-blog].

Reproduction pins vLLM `e8ef1e07bd`, planned for wide availability in vLLM v0.30, NVIDIA-only at publication time[^hybrid-blog]:

```bash
vllm serve zai-org/GLM-5.3 \
  --tensor-parallel-size 8 --kv-cache-dtype fp8 \
  --gpu-memory-utilization 0.92 --max-model-len 142000 \
  --max-num-batched-tokens 32768 --max-num-seqs 256 \
  --enable-prefix-caching \
  --attention-config '{"hisparse_config":{"host_pool_gib":384}}' \
  --kv-transfer-config '{"kv_connector":"OffloadingConnector","kv_role":"kv_both","kv_connector_extra_config":{"spec_name":"TieringOffloadingSpec","cpu_bytes_to_use":137438953472}}' \
  --speculative-config '{"method":"mtp","num_speculative_tokens":3}' \
  --enable-auto-tool-choice --tool-call-parser glm47 --reasoning-parser glm45
```

Omit `--speculative-config` for no-MTP HiSparse; for the no-HiSparse MTP3 baseline omit `--attention-config` and set `cpu_bytes_to_use` to `549755813888` (512 GiB); omit both for the no-MTP baseline[^hybrid-blog]. The padded OpenHands sweep recipe ships `build_openhands_padded_dataset.py`, `install_evalscope_deps.sh`, and `evalscope-all-nodeps.txt` with EvalScope pinned at `acd09b44384d53174768bb1063f675420f76fae9`; interactivity is `1000 / mean_TPOT_ms` and per-GPU logical throughput is EvalScope total divided by eight[^hybrid-blog].

## Capacity-planning notes

The blog calculator estimates ordinary GPU-resident versus hybrid-sparse concurrency from the same available HBM, including the minimum HiSparse host pool needed so CPU memory does not cap the concurrency that GPU-side indexer plus hot buffers can sustain[^hybrid-blog]. Modeling rules and caveats:

- Native indexer offloading is a separate total CPU pool: it extends the prefix cache, but active indexer history still consumes HBM and stays in the running-request limit[^hybrid-blog].
- Hot buffers add fixed GPU cost per request, so ordinary residency can fit more requests at short contexts; at longer contexts bounding sparse-MLA residency lets HiSparse sustain more[^hybrid-blog].
- Increasing hot-buffer size trades capacity for hot-cache coverage[^hybrid-blog].
- MTP can further limit concurrency because hot buffers must hold all verification tokens at once: at publication `(num_speculative_tokens + 2) × top-K` per buffer, subject to change and not yet in the calculator[^hybrid-blog].
- Estimates are planning aids, not guaranteed serving limits; runtime workspaces, length skew, and scheduling can lower realized concurrency[^hybrid-blog].

Part 2 scope: Hybrid HiSparse matters most on the decode side of P/D deployments where contexts are longest and KV pressure highest, combined with Prefill Context Parallelism, Decode Context Parallelism, and adaptive verification[^hybrid-blog].

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
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) identity and reuse model; the coordinator's source-prefix mapping and completed-spill publication feed host-page prefix reuse. Hybrid proactive staging extends this by queueing CPU copies of completed prefix pages before pressure arrives[^hybrid-blog].
- Uses [vLLM KV Offloading Connector](vllm-kv-offloading.md) for indexer KV that HiSparse does not manage, via `OffloadingConnector` with `TieringOffloadingSpec` alongside the 384 GiB HiSparse pool in the GLM-5.3 recipe[^hybrid-blog].
- Uses [vLLM NIXL KV Cache Lease Renewal](vllm-nixl-kv-lease.md) transfer path for the P/D import landing decision; NIXL places fitting prefixes directly in resident pages. Hybrid imports can land host-side when the prefix does not fit resident[^hybrid-blog].
- Depends on [vLLM Attention Backends](vllm-attention-backends.md) sparse-attention consumption of a device cache and physical row IDs.
- Depends on [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) graph-capturable execution; the fused resolver adds no separate CUDA graph.
- Related to [vLLM Decode Context Parallelism](vllm-decode-context-parallelism.md) and [vLLM Adaptive Verification for Speculative Decoding](vllm-adaptive-verification.md) — Part 2 combines both with Hybrid HiSparse on the decode side of large P/D deployments[^hybrid-blog].
- Related to [SGLang HiSparse Hierarchical Sparse-Attention Memory](sglang-hisparse.md) — SGLang-side counterpart keeping full KV in host with a hot device buffer and swap-in kernel; compare with vLLM Hybrid policy that keeps KV GPU-resident until pressure forces page-wise spill[^hybrid-blog].

## Coverage limits

- Design internals compiled from the design document; Hybrid policy, residency states, composition, benchmarks, and deployment recipe compiled from the GLM-5.3 Part 1 blog[^hisparse][^hybrid-blog].
- Implementation classes, `MultiConnector`, `OffloadingConnector`, HMA, and NIXL behavior were not verified beyond these sources.
- All three source SVG attachments were inspected via aria-labels plus prose captions (two-request preempt-vs-offload comparison, three-state residency over one shared pool, OpenHands Pareto plus occupancy chart); numeric chart values beyond the prose benchmark setup were not independently extracted.
- The interactive concurrency calculator iframe, full-screen calculator page, EvalScope repro scripts, HiSparse arXiv paper, and IndexShare paper were not inspected.

[^hisparse]: HiSparse local KV offload architecture — `../raw/vllm/design/hisparse.md`, short version, ownership, code boundary, resident pages, P/D import, indexer offloading, spill transaction, hot lookup and LRU, main classes, performance invariants, and platform-specific sections.

[^hybrid-blog]: GLM 5.3 Optimizations, Part 1: Hybrid HiSparse Offloading in vLLM — `../raw/2026-09-08-glm53-part1-hybrid-sparse-offloading/index.md`, covering pressure-driven hybrid policy, three residency states, shared-pool hot buffers, proactive staging, composition with HMA/offloading/P-D/spec-decode, 2× top-K and per-DP host-pool layout, 8×H200 OpenHands benchmark setup and host-budget split, v0.30/NVIDIA-only status, launch-command appendix, capacity-calculator caveats including MTP buffer sizing, and Part 2 roadmap.
