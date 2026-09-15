---
type: Concept
title: vLLM KV Offloading Connector
description: Extending vLLM prefix cache with CPU and tiered offload via OffloadingConnector, covering specs, secondary tiers, P2P protocol, tuning, and per-request selective offload.
tags: [vllm, kv-cache, offloading, prefix-caching, disaggregated-prefill]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: kv-offload-usage
    resource: ../raw/vllm/features/kv_offloading_usage.md
    title: KV Offloading Usage Guide
  - id: tiered-kv-blog
    resource: ../raw/2026-09-10-tiered-kv-offloading/index.md
    title: Tiered KV Cache Offloading in vLLM
---

`OffloadingConnector` extends the vLLM prefix cache by offloading completed KV blocks to slower but larger tiers — CPU host memory plus optional secondary tiers — as they are produced; hits are promoted back to GPU on demand[^kv-offload-usage].

GPU↔CPU transfers use DMA (`cudaMemcpyAsync`) and run asynchronously alongside model computation, adding minimal CPU- and GPU-core overhead. The connector currently supports CUDA, ROCm, and XPU only[^kv-offload-usage].

## Specs and topology

Two specs are selected by `spec_name` in `kv_connector_extra_config`[^kv-offload-usage]:

- `CPUOffloadingSpec` (default): single CPU tier; completed GPU blocks are copied into pinned host memory.
- `TieringOffloadingSpec`: multi-tier; CPU primary tier plus one or more secondary tiers.

Only the CPU primary tier has direct GPU access. Secondary tiers cannot read from or write to GPU memory; all GPU↔secondary transfers are staged through the CPU primary tier[^kv-offload-usage]:

```text
GPU <--> CPU primary tier <--> Secondary tier 0, 1, ...
```

## Chunks

The unit of operation is a **chunk** — a fixed-size piece of KV data covering a group of tokens. By default a chunk maps to a single accelerator block; configurable `blocks_per_chunk` allows larger chunks, yielding larger I/Os to host and secondary tiers[^kv-offload-usage].

The tiered framework has been available in vLLM since v0.22[^tiered-kv-blog].

## Host-centric design

The core design principle is that **all KV data flows through host memory (CPU DRAM)**[^tiered-kv-blog]:

```text
accelerator <-> host primary tier <-> secondary tier 0, 1, ...
```

On offload, chunks move accelerator → host first, then cascade from the host copy to all secondary tiers. On reload, a secondary tier promotes data into host memory first, then it loads to the accelerator. The first tier holding a chunk serves it[^tiered-kv-blog].

### Just-in-time accelerator allocation

Copying accelerator → host is a fast local PCIe transfer. **Accelerator memory is freed as soon as this copy completes — before any secondary-tier transfer starts**; storage writes, network sends, and remote RDMA proceed from the host copy without touching accelerator memory again. On reload, accelerator memory is allocated only once the data is ready in host, not reserved in advance while waiting for tier transfers. Accelerator memory is therefore held only while actively needed[^tiered-kv-blog].

### Consolidated I/O

In multi-accelerator setups (e.g. `tensor_parallel_size=8`), each device holds a KV shard. The framework consolidates all shards into a single shared host memory region, so secondary tiers see fewer, larger I/O operations — improving storage and network throughput. Without consolidation, 8 accelerators × N blocks means 8N small I/Os; with consolidation, N larger merged I/Os[^tiered-kv-blog].

### Canonical memory layout

The host region uses a canonical layout: each page stores one block of one layer, with all KV heads from across TP ranks gathered into a single contiguous region, so locating any chunk is an offset calculation. The fixed host-side layout is configuration-independent — different accelerator types, attention backends (FlashAttention, FlashInfer, Triton), or parallelism configurations map to the same representation, so nodes with different setups (e.g. TP=2 and TP=4) share KV data directly with no remapping[^tiered-kv-blog].

### Simple secondary tiers

Because all data routes through host memory, secondary tiers are a single process per vLLM instance, transfer with standard CPU libraries (POSIX I/O, S3 SDKs, RDMA verbs), and never touch accelerator memory or APIs — no cross-process coordination or accelerator-layout knowledge required[^tiered-kv-blog].

## Offload and reload lifecycle

Offload path: new KV chunks move accelerator → host via async DMA and accelerator memory is freed immediately, before secondary transfer begins. The tiering manager then cascades chunks to **all** configured secondary tiers simultaneously from the host copy[^tiered-kv-blog].

The host primary tier is a **proper LRU/ARC cache, not a staging buffer**: chunks remain in host memory and serve future hits directly; only when host capacity is exhausted are least-recently-used chunks evicted, and they survive in whichever secondary tier received them[^tiered-kv-blog].

Reload path: the scheduler checks host first for an immediate hit. On host miss, secondary tiers are queried in configured order and the first holder serves the chunk; the tier promotes it back into host asynchronously while the scheduler receives a `RETRY` and re-checks next cycle. Different chunks of the same request can come from different tiers (e.g. one from filesystem, another from a remote peer)[^tiered-kv-blog].

Filesystem and object-store tiers use content-addressed naming — identical token sequences map to the same key, so matching inputs share cached data automatically; multiple instances sharing the same mount or bucket share KV data with no extra configuration[^tiered-kv-blog].

## Setup

Single-tier (CPU only)[^kv-offload-usage]:

```bash
vllm serve <model> \
  --kv-transfer-config '{
    "kv_connector": "OffloadingConnector",
    "kv_role": "kv_both",
    "kv_connector_extra_config": {
      "block_size": 64,
      "cpu_bytes_to_use": 1000000000
    }
  }'
```

Multi-tier[^kv-offload-usage]:

```bash
vllm serve <model> \
  --kv-transfer-config '{
    "kv_connector": "OffloadingConnector",
    "kv_role": "kv_both",
    "kv_connector_extra_config": {
      "spec_name": "TieringOffloadingSpec",
      "cpu_bytes_to_use": 10737418240,
      "block_size": 16,
      "eviction_policy": "lru",
      "secondary_tiers": [
        {
          "type": "fs",
          "root_dir": "/mnt/kv_cache",
          "n_read_threads": 32,
          "n_write_threads": 16
        }
      ]
    }
  }'
```

`secondary_tiers` is ordered: tier 0 is consulted before tier 1, and so on[^kv-offload-usage].

## `kv_connector_extra_config` reference

| Key | Required | Default | Scope | Notes |
| --- | --- | --- | --- | --- |
| `spec_name` | no | `CPUOffloadingSpec` | both | Set to `TieringOffloadingSpec` for multi-tier. |
| `cpu_bytes_to_use` | yes | — | both | Total host bytes reserved for CPU tier across all workers, not per-worker. |
| `block_size` | no | GPU block size | both | Offloaded block size in tokens; must be a multiple of GPU block size. Mutually exclusive with `blocks_per_chunk`. |
| `blocks_per_chunk` | no | `1` | both | Chunk size in GPU blocks; must be > 0. Alternative to `block_size` for models whose KV groups have different block sizes. |
| `eviction_policy` | no | `lru` | both | Primary-tier policy: built-in `lru`/`arc` or custom `CachePolicy` name. |
| `cache_policy_module_path` | no | — | both | Import path for out-of-tree `CachePolicy`; required only when `eviction_policy` is not built-in and was not pre-registered. |
| `store_threshold` | no | `0` | single-tier | Minimum lookups before a block is offloaded. Values ≥ 2 are rejected by `TieringOffloadingSpec`. |
| `max_tracker_size` | no | `64000` | single-tier | Maximum entries in the lookup tracker. |
| `secondary_tiers` | no | `[]` | multi-tier | List of secondary-tier configs. |
| `offload_prompt_only` | no | `true` | both | If `true`, only prompt (prefill) blocks are offloaded; decode blocks are skipped. |
| `self_describing_kv_events` | no | `false` | both | Opt-in block-granular `BlockStored`/`BlockRemoved` payloads when KV events are enabled; otherwise placeholder fallback. See limits below. |
| `spec_module_path` | no | — | both | Import path for custom `OffloadingSpec` not in the built-in registry. |

All rows from the source table are preserved here[^kv-offload-usage].

`self_describing_kv_events` takes effect only when `true` *and* KV cache events are enabled via `--kv-events-config` with `enable_kv_cache_events`. It emits constituent block hashes, whole-chunk `token_ids`, per-block `block_size`, parent hash, and LoRA plus group/cache-spec metadata so external consumers can index offloaded blocks; otherwise inert[^kv-offload-usage]. Limits[^kv-offload-usage]:

- With `TieringOffloadingSpec`, a CPU promotion is self-describing only when a local request observes its primary-tier `HIT` before event translation; otherwise the stored event may retain the placeholder, while a later `HIT` can backfill metadata for removal.
- Pending-removal/re-promotion races and externally initiated promotions may also produce placeholders; consumers must ignore removals for unknown hashes.
- Partial recurrent tails emit the hash-aligned portion from the physical block start through the tail boundary. Other sliding-window/SSM chunks keep the placeholder fallback.
- In chunk mode (`block_size` > GPU block size, or `blocks_per_chunk` > 1), overlapping chunks re-announce shared per-block hashes, so consumers must reference-count repeated store/remove announcements.

## Custom eviction policies

`eviction_policy` resolves through `CachePolicyFactory` (`vllm/v1/kv_offload/cpu/policies/factory.py`), which pre-registers built-in `lru` and `arc`[^kv-offload-usage].

Out-of-tree (recommended): implement `CachePolicy` (`vllm/v1/kv_offload/cpu/policies/base.py`) in your own package and point config at it directly — no fork required[^kv-offload-usage]:

```json
{
  "cpu_bytes_to_use": 10737418240,
  "eviction_policy": "MyCachePolicy",
  "cache_policy_module_path": "my_package.my_module"
}
```

`eviction_policy` is checked against the built-in registry first; if unregistered, vLLM imports `cache_policy_module_path` and looks up the class name there — the same fallback `spec_module_path` provides for custom `OffloadingSpec`[^kv-offload-usage].

In-process friendly short name: if you control the process constructing the engine, call `CachePolicyFactory.register_cache_policy("my_policy", "my_package.my_module", "MyCachePolicy")` once at startup, then set `"eviction_policy": "my_policy"`. This takes effect only within that process and does not help when the server is launched as a separate process via `vllm serve`, where the `cache_policy_module_path` config is the only option[^kv-offload-usage].

## Secondary tiers

Each entry has a required `type` plus tier-specific fields and an optional `module_path` for out-of-tree tiers[^kv-offload-usage].

Filesystem and object-store tiers can publish hash-only `BlockStored` KV events for successfully stored blocks. Both use the coarse-grained wire medium `STORAGE`, which does not distinguish filesystem from object-store storage. Set the optional `locality` field (`LOCAL`/`REMOTE`) to tell consumers whether the tier is local to the publishing instance; vLLM does not infer it from tier type, so an `obj` tier is not implicitly `REMOTE`. A KV event includes `locality` only when explicitly configured, without implying that a consumer can already route requests to its blocks. Opt in with `enable_kv_events: true` in the tier entry plus global `--kv-events-config`[^kv-offload-usage].

### Filesystem tier

`type: "fs"` writes blocks to a filesystem directory[^kv-offload-usage]:

| Key | Required | Default | Notes |
| --- | --- | --- | --- |
| `type` | yes | — | Must be `fs`. |
| `root_dir` | yes | — | Base directory; vLLM creates subdirectories beneath it. |
| `n_read_threads` | no | `16` | Read-priority I/O threads (load path). |
| `n_write_threads` | no | `16` | Write-priority I/O threads (store path). |
| `enable_kv_events` | no | `false` | Publish `BlockStored` events (medium `STORAGE`) for stored blocks. |
| `locality` | no | unspecified | `LOCAL` or `REMOTE` relative to publishing instance. |

Each thread group prefers its own queue but pulls from the other when its primary queue is empty, so write-heavy or read-heavy bursts do not starve the off-priority queue. Size totals to the storage's effective concurrency[^kv-offload-usage].

On-disk layout under `root_dir`[^kv-offload-usage]:

```text
<root_dir>/
  <model>_<digest>/
    config.json
  <model>_<digest>_r<rank>/
    <hhh>/
      <hh>_g<group_idx>/
        <hash_hex>.bin
```

- `<model>` replaces `/` with `_` so HuggingFace IDs do not nest.
- `<digest>` is a short SHA256 prefix derived from run configuration (model, block size, parallelism, dtype, etc.). Same-configuration runs share a subdirectory; different configurations live side-by-side without colliding.
- `config.json` records the run and is written on first start.
- Blocks are sharded across hash-prefix subdirectories to limit fan-out; each rank writes under its own `_r<rank>` sibling directory so ranks can share `root_dir`.

### Object-store tier

`type: "obj"` offloads to an S3-compatible store through the NIXL OBJ backend[^kv-offload-usage]:

| Key | Required | Default | Notes |
| --- | --- | --- | --- |
| `type` | yes | — | Must be `obj`. |
| `store_config` | yes | — | Connection parameters (see below). |
| `prefix` | no | `""` | Key prefix prepended to all object keys. |
| `io_threads` | no | `4` | NIXL OBJ backend I/O threads. |
| `enable_kv_events` | no | `false` | Publish `BlockStored` events (medium `STORAGE`). |
| `locality` | no | unspecified | `LOCAL` or `REMOTE`. |

`store_config` fields[^kv-offload-usage]:

| Key | Required | Default | Notes |
| --- | --- | --- | --- |
| `bucket` | yes | — | Bucket name. |
| `endpoint_override` | yes | — | Endpoint host; URL scheme is set separately via `scheme`. |
| `scheme` | no | `http` | `http` or `https`. |
| `access_key`, `secret_key`, `session_token` | no | `""` | Explicit credentials. When empty, the NIXL OBJ plugin falls back to the AWS SDK default credential chain (IAM roles, environment variables, credential files), enabling workload-identity auth on Kubernetes. |
| `region` | no | `""` | Bucket region if required. |
| `ca_bundle` | no | `""` | CA bundle path for TLS verification. |

Object keys follow the same run-configuration digest scheme as the filesystem tier under the optional `prefix`. Cross-process sharing behavior applies to shared buckets. At startup the tier probes connectivity and fails fast if the bucket is unreachable[^kv-offload-usage].

### Cross-process sharing

Sharing the same `root_dir` (e.g. via a shared PVC) or bucket across vLLM instances works by default: `NONE_HASH` (chain-hash seed for block content hashes) derives from a fixed default seed, so identical token content produces identical filenames/keys across instances. To use a custom shared seed, set the same `PYTHONHASHSEED` on every instance[^kv-offload-usage]:

```bash
PYTHONHASHSEED=<shared-value> vllm serve ...
```

Exception: non-cryptographic `xxhash` and `xxhash_cbor` values of `--prefix-caching-hash-algo` seed `NONE_HASH` randomly per process so the seed stays unpredictable; sharing across instances with those algorithms requires setting the same `PYTHONHASHSEED`[^kv-offload-usage].

### P2P tier

`type: "p2p"` shares completed KV blocks between vLLM instances over RDMA via NIXL. Each instance binds a control socket on `host:port` and exchanges blocks directly with peers — no shared filesystem required[^kv-offload-usage].

Block hashes must match across instances. This works by default via the deterministic `NONE_HASH` seed, so `PYTHONHASHSEED` is optional but must match on all nodes if set. Each peer's effective seed is verified during the connect handshake — mismatched seeds are rejected. With `xxhash`/`xxhash_cbor` the seed is random per process, so `PYTHONHASHSEED` must be set on every peer[^kv-offload-usage].

| Key | Required | Default | Notes |
| --- | --- | --- | --- |
| `type` | yes | — | Must be `p2p`. |
| `host` | no | `$VLLM_P2P_SIDE_CHANNEL_HOST` (`localhost`) | Bind address, used verbatim as the identity peers dial back. `localhost` binds loopback only — cross-host P2P must set a routable IP. |
| `port` | no | `$VLLM_P2P_SIDE_CHANNEL_PORT` (`5710`) | Base control-socket port. Bound port is `base + data_parallel_index` (one socket per DP replica). |
| `backends` | no | `["UCX"]` | NIXL transport backends. |
| `num_threads` | no | `4` | NIXL agent worker threads; only used when `backends` is UCX-only, ignored otherwise. |

`backends` and `num_threads` mirror `NixlConnector` logic: any non-UCX backend initializes NIXL with `backends=...`, otherwise falls back to a UCX-only agent with `num_threads`. This lets the P2P tier use a different transport (e.g. `MOONCAKE`, `GDS_MT`, `LIBFABRIC`) than the main `NixlConnector` in the same process[^kv-offload-usage].

Environment variables (explicit `host`/`port` keys take precedence)[^kv-offload-usage]:

- `VLLM_P2P_SIDE_CHANNEL_HOST` (default `localhost`): bind address used verbatim as bind plus dial-back identity; no auto-detection. Default binds loopback only, so cross-host deployments must set the node's routable IP (e.g. pod IP). The NIXL agent name is a separate per-process identifier, so peers sharing `host:port` never collide.
- `VLLM_P2P_SIDE_CHANNEL_PORT` (default `5710`): base port. The bound port is `base + data_parallel_index`. The peer's port is passed as `remote_port` in `kv_transfer_params`; the router/EPP selecting the DP rank (e.g. via `X-data-parallel-rank`) computes `remote_port = base + rank`. The offset separates replicas within one deployment; two co-located deployments (prefiller and decoder on the same host) still need distinct base ports (e.g. decoder base `5711`) to avoid collision.

### P2P orchestration protocol

The P2P tier does not decide which peer to pull from — the orchestration layer (router/EPP and scheduler) does. It drives every transfer through a request's `kv_transfer_params` dict: picks the role, allocates a unique transaction ID, and supplies the remote address. Lookup, hash matching, and NIXL transfer happen below; the orchestrator only sets role keys and enforces combinations[^kv-offload-usage].

Every instance is a symmetric peer: per request it acts as consumer (pulls from remote CPU cache), producer (serves from own CPU cache), or both on the same session for different requests. Roles are per-request; there are no fixed prefiller/decoder processes. All role keys are optional; a request with none uses the tier only as local CPU cache. Each key names the remote counterpart, not this peer's own role[^kv-offload-usage]:

| Key | Set on | Value fields | Meaning |
| --- | --- | --- | --- |
| `remote_decoder` | prefill producer request | `kv_request_id` | Compute KV and keep it in CPU cache for the remote decoder to pull. |
| `remote_prefiller` | decode consumer request | `kv_request_id`, `remote_host`, `remote_port` | Pull KV from the remote prefiller (classic P/D disaggregation). |
| `remote_kv_source` | P2P consumer request | `kv_request_id`, `remote_host`, `remote_port` | Look up and pull whatever the remote source currently holds. |

- `kv_request_id` (str): orchestrator-allocated transaction ID pushed to every involved peer; correlates lookup, fetch, and transfer-done messages. The producer serves whatever hashes it holds for that ID.
- `remote_host` (str): remote peer's control-socket IP/hostname; must be routable.
- `remote_port` (int): peer's bound port (`base + data_parallel_index`).

Only `remote_decoder` + `remote_kv_source` may combine: a prefill producer may also act as P2P consumer for the same request — skipping prefix prefill while keeping its own blocks for a downstream decoder. Forbidden: `remote_prefiller` + `remote_decoder`, `remote_prefiller` + `remote_kv_source`, and all three together[^kv-offload-usage]:

```python
# Prefill producer
kv_transfer_params = {"remote_decoder": {"kv_request_id": "<unique-transfer-id>"}}

# Decode consumer (classic P/D)
kv_transfer_params = {
    "remote_prefiller": {
        "kv_request_id": "<unique-transfer-id>",
        "remote_host": "<prefiller-node-ip>",
        "remote_port": 5710,
    }
}

# P2P consumer
kv_transfer_params = {
    "remote_kv_source": {
        "kv_request_id": "<unique-transfer-id>",
        "remote_host": "<source-node-ip>",
        "remote_port": 5710,
    }
}
```

Runtime handshake once keys are set[^kv-offload-usage]:

1. Both peers already listen on their control sockets.
2. **Lookup.** In P2P mode the tier returns `None` and registers the key. At `on_schedule_end` the consumer sends one `LookupMsg` (`kv_request_id` + block hashes) per request per step.
3. Producer matches hashes against local CPU cache and replies with `LookupRespMsg` carrying hits.
4. **Resolve.** Retried lookups return hit/miss/in-flight. Consumer calls `submit_load` for hits only, allocating CPU slots only for hits.
5. Consumer sends `FetchMsg` (`kv_request_id`, block hashes, destination indexes).
6. Producer performs the NIXL WRITE transfer and sends `TransferDone` with success status.
7. On `get_finished`, hits load into GPU as ordinary cache hits; misses are recomputed.

In classic P/D mode (`remote_prefiller` set, no `remote_kv_source`) the lookup phase is skipped: the consumer assumes the prefiller holds all blocks, every `lookup()` returns an immediate hit, and it jumps to `FetchMsg`. The `LookupMsg`/`LookupRespMsg` round-trip happens only in P2P mode where the consumer does not know the peer's cached set[^kv-offload-usage].

### Out-of-tree secondary tiers

Implement `SecondaryTierManager` (`vllm/v1/kv_offload/tiering/base.py`) in your own package and point the tier config at it directly[^kv-offload-usage]:

```json
{
  "spec_name": "TieringOffloadingSpec",
  "cpu_bytes_to_use": 10737418240,
  "secondary_tiers": [
    {
      "type": "MyCustomTier",
      "module_path": "my_package.my_module",
      "custom_param": "value"
    }
  ]
}
```

`type` is checked against the built-in registry first; if unregistered, vLLM imports `module_path` and looks up `type` as a class name there[^kv-offload-usage].

## Tuning

- `cpu_bytes_to_use`: bigger CPU tier means fewer trips to slower tiers and higher hit rate. The value is total across workers; leave headroom for the rest of the host workload[^kv-offload-usage].
- For single-tier CPU-only setups, set `cpu_bytes_to_use` larger than the aggregate GPU KV cache. Because offloading is immediate, a smaller CPU tier just mirrors what the GPU already holds and adds no hit rate[^kv-offload-usage].
- `block_size` / `blocks_per_chunk`: larger chunks reduce per-block bookkeeping but increase lookup granularity[^kv-offload-usage].
- FS thread counts: tune `n_read_threads` and `n_write_threads` to storage concurrency. Reads are latency-sensitive on the prefill path, so prefer more read threads when prefill hit rates are high[^kv-offload-usage].
- Sharing `root_dir`: same model, `block_size`, parallelism, and dtype share files under the same digest subdirectory. Changing any produces a new subdirectory; old ones are orphaned but harmless — delete to reclaim disk[^kv-offload-usage].

## Per-request selective offload

Individual requests can cap offload-eligible tokens with `max_offload_tokens` in `kv_transfer_params`. Only the first `max_offload_tokens` tokens are offloaded; later blocks are skipped on the store path. Useful when a known prefix (system prompt or shared context) is worth caching but later request-specific tokens are not[^kv-offload-usage].

| Key | Type | Notes |
| --- | --- | --- |
| `max_offload_tokens` | non-negative `int` | Upper bound on tokens to offload. `0` disables offload for the request; omit or `None` for no cap. Non-`int`, negative, or `bool` values are rejected with a warning and treated as no cap. |

`max_offload_tokens` is experimental and subject to change[^kv-offload-usage]:

```json
{
  "model": "<model>",
  "prompt": "...",
  "kv_transfer_params": {
    "max_offload_tokens": 1024
  }
}
```

## P2P use cases

All P2P transfers are host-to-host — no accelerator memory on either side. The P2P tier uses ZMQ for coordination and RDMA via NIXL for bulk transfer[^tiered-kv-blog].

- **Prefill/decode disaggregation:** the prefill instance computes KV chunks and holds them in its host tier; the decode instance pulls them via RDMA. Consolidated I/O turns many small per-GPU transfers into fewer, larger RDMA operations, and with chunked prefill each completed prefill-chunk becomes immediately available for transfer, overlapping computation and movement and reducing time-to-first-token[^tiered-kv-blog].
- **Load balancing:** pull KV chunks from an overloaded instance to one with available capacity; any node can pull from any peer[^tiered-kv-blog].

Secondary tiers also make KV shareable across nodes for horizontal cache scaling, warm-starting new instances from shared storage, and peer transfer for disaggregated serving or load balancing[^tiered-kv-blog].

## Hybrid model support

The framework integrates with vLLM's hybrid memory allocator and handles models mixing full attention, sliding window, MLA, and Mamba transparently[^tiered-kv-blog].

The canonical layout normalizes all KV formats into a uniform byte-buffer representation with a **fixed byte size per host chunk**, regardless of layer types; different layer types pack different numbers of tokens into the same chunk (e.g. Mamba state layers cover many more tokens per chunk than full-attention layers, so they offload less frequently)[^tiered-kv-blog].

Consequences[^tiered-kv-blog]:

- Sliding-window layers reload only tokens within their window, not full history.
- State-space (Mamba) layers offload and reload state alongside attention KV.

Reported support includes DeepSeek V4, GLM 5.3, Nemotron 3, and others[^tiered-kv-blog].

## Observability and KV events

The framework exposes Prometheus metrics via the standard `/metrics` endpoint[^tiered-kv-blog]:

- Host cache utilization (primary-tier fill ratio).
- Transfer throughput (bytes and time for accelerator ↔ host).
- Per-tier lookup and transfer latencies.
- Per-tier hit rates.

Secondary tiers can define custom counters, histograms, and gauges that are automatically registered and exposed with no framework changes[^tiered-kv-blog].

As chunks move, the framework emits structured **KV events** reporting which chunks were stored or evicted, from which tier, and with what locality (local vs. remote); secondary tiers can emit their own events. External orchestrators such as llm-d and Dynamo consume these events to route requests to the instance most likely to hit and to orchestrate P2P transfers[^tiered-kv-blog].

## Custom secondary-tier interface

The secondary-tier interface is four core methods[^tiered-kv-blog]:

```python
class SecondaryTierManager(ABC):
    def lookup(self, key, req_context) -> LookupResult: ...  # HIT, MISS, or RETRY
    def submit_store(self, job_metadata: JobMetadata) -> None: ...  # async host -> tier
    def submit_load(self, job_metadata: JobMetadata) -> None: ...   # async tier -> host
    def get_finished_jobs(self) -> Iterable[JobResult]: ...  # poll completed transfers
```

Each tier receives a direct memoryview into the shared host region at construction; `submit_store` reads and `submit_load` writes directly with no intermediate copies or serialization. Each tier manages its own eviction policy independently. A complete in-memory reference implementation lives at `vllm/v1/kv_offload/tiering/example/`; out-of-tree tiers specify `module_path` and load without vLLM code changes[^tiered-kv-blog].

Filesystem-tier highlights from this source are non-blocking lookups, atomic writes, and separate read/write thread pools[^tiered-kv-blog].

## Performance evidence

Main benefit: avoiding repeated prefills by reloading from a cheaper tier instead of recomputing[^tiered-kv-blog].

Source-reported scaling shape (multi-turn workload below)[^tiered-kv-blog]:

- Up to ~64 conversations: HBM holds the working set; all methods perform well.
- 64–128 conversations: HBM fills; throughput drops without offloading while CPU offloading maintains performance.
- Beyond 128 conversations: CPU also fills; storage offloading sustains a high hit ratio and more than doubles throughput versus alternatives.

Storage latency is higher than CPU memory so it does not reach peak throughput, but at scale a storage-backed hit beats full recompute decisively[^tiered-kv-blog].

Benchmark setup[^tiered-kv-blog]:

- Model: Qwen/Qwen3.6-35B-A3B on 2× NVIDIA H100 (TP=2).
- Storage: filesystem backend on local NVMe.
- Workload: multi-turn conversations, 12K-token initial prompts + 4K tokens per round, 8 rounds; max request concurrency 64; prefiller throughput only (prefill-decode disaggregated).
- Full results and reproduction scripts: `neuralmagic/fs-offload-experiments` (linked in source, not inspected).

## Relationships

- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — offloading extends prefix-cache reuse beyond GPU memory; hits promote back to GPU while hash, salt, and block-granularity semantics remain prefix-cache concepts.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — `OffloadingConnector` is one catalogued KV-transfer connector; this concept covers its standalone tiered-cache setup while disaggregated prefill covers the prefill/decode split. P2P host-to-host RDMA plus chunked-prefill overlap is the offloading-side mechanism for that split.
- Uses [vLLM HiSparse Local KV Offload](vllm-hisparse.md) — when `OffloadingConnector` is configured with HiSparse it stores and restores the indexer KV group through the generic offload path while HiSparse retains its sparse host tier.
- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — fixed-byte host chunks normalizing full-attention, sliding-window, MLA, and Mamba formats are the offloading-side counterpart to unified page-size grouping and per-group allocation.
- Uses [vLLM Metrics and Observability](vllm-metrics.md) — `/metrics` Prometheus endpoint and per-tier utilization, throughput, latency, and hit-rate signals extend the base V1 metrics model with offloading-specific observability.

## Coverage limits

- Linked `disagg_prefill.md` and `nixl_connector_usage.md` backend-selection details were not recompiled here; only the P2P-tier `backends`/`num_threads` mirroring rule stated in this source is covered[^kv-offload-usage].
- Cited implementation paths (`vllm/v1/kv_offload/cpu/policies/`, `vllm/v1/kv_offload/tiering/base.py`, `vllm/v1/kv_offload/tiering/example/`) were not inspected; claims rest on usage-guide and blog prose[^kv-offload-usage][^tiered-kv-blog].
- All four local diagrams (`architecture.svg`, `offload-flow.svg`, `consolidated-io.svg`, `performance.svg`) were visually inspected and are reflected in the host-centric, just-in-time, consolidation, and scaling sections[^tiered-kv-blog].
- Linked usage guide, `llm-d`, Dynamo, and `neuralmagic/fs-offload-experiments` reproduction scripts were not inspected; benchmark figures are source-reported[^tiered-kv-blog].

[^kv-offload-usage]: KV Offloading Usage Guide — `../raw/vllm/features/kv_offloading_usage.md`, covering `OffloadingConnector` DMA-based async offload with CUDA/ROCm/XPU support, `CPUOffloadingSpec` versus `TieringOffloadingSpec` topology with CPU-staged secondary access, chunk sizing, single- and multi-tier setup, full `kv_connector_extra_config` reference, custom eviction policies, filesystem/object-store/P2P secondary tiers with on-disk layout, cross-process hash sharing, P2P environment and `kv_transfer_params` orchestration protocol with handshake, out-of-tree tiers, tuning guidance, and experimental `max_offload_tokens` selective offload.

[^tiered-kv-blog]: Tiered KV Cache Offloading in vLLM — `../raw/2026-09-10-tiered-kv-offloading/index.md` (vLLM blog, 2026-09-10), covering host-centric design with just-in-time accelerator release, consolidated I/O, canonical layout, and CPU-only secondary tiers; LRU/ARC host cache with cascade-to-all offload and RETRY-based reload; filesystem/object/P2P tiers with content-addressed sharing and P/D plus load-balancing uses; hybrid full-attention/sliding-window/MLA/Mamba normalization; Prometheus metrics and KV events for llm-d/Dynamo routing; four-method `SecondaryTierManager` zero-copy interface; and Qwen3.6-35B-A3B 2×H100 NVMe scaling evidence (HBM to ~64, CPU to ~128, storage >2× beyond).
