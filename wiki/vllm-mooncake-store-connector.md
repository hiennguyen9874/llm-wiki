---
type: Concept
title: vLLM Mooncake Store Connector
description: Shared distributed KV-cache pool via Mooncake store for CPU/disk offloading and cross-instance prefix reuse, with single-node, disaggregated, and standalone-store deployments.
tags: [vllm, kv-cache, mooncake, offloading, prefix-caching, disaggregated-prefill]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T17:00:00Z }
sources:
  - id: mooncake-store
    resource: ../raw/vllm/features/mooncake_store_connector_usage.md
    title: MooncakeStoreConnector Usage Guide
---

`MooncakeStoreConnector` uses `MooncakeDistributedStore` as a shared KV-cache pool for offload and cross-instance prefix reuse, unlike `MooncakeConnector` which does direct point-to-point prefill-to-decode transfer[^mooncake-store].

It supports CPU/disk offloading to extend effective KV capacity, hash-based prefix-cache sharing across vLLM instances, and both single-node and multi-node disaggregated deployments[^mooncake-store].

## Prerequisites

- Install via `uv pip install mooncake-transfer-engine`; the source points to the Mooncake official repository for more install/build instructions[^mooncake-store].
- Start the Mooncake master before vLLM; it manages metadata and coordinates the store[^mooncake-store]:

```bash
mooncake_master --port 50051
```

- Default RPC port is `50051`; multiple vLLM instances can share one master[^mooncake-store].
- Create a JSON config (e.g. `mooncake_config.json`) and point vLLM at it[^mooncake-store]:

```bash
export MOONCAKE_CONFIG_PATH=/path/to/mooncake_config.json
```

## Store config

Example baseline[^mooncake-store]:

```json
{
  "mode": "embedded",
  "metadata_server": "P2PHANDSHAKE",
  "master_server_address": "127.0.0.1:50051",
  "global_segment_size": "80GB",
  "local_buffer_size": "4GB",
  "protocol": "rdma",
  "device_name": "",
  "enable_offload": false
}
```

Fields[^mooncake-store]:

- `mode`: `"embedded"` (default, PR-40900 baseline) makes each vLLM rank contribute `global_segment_size` in-process; `"standalone-store"` makes ranks pure requesters while an external `mooncake_client` owns the CPU pool and optional SSD tier.
- `protocol`: `"rdma"` for best performance, `"tcp"` as fallback.
- `global_segment_size`: per-GPU CPU memory contributed to the pool; must be `> 0` in `embedded` mode and `0` in `standalone-store` mode.
- `local_buffer_size`: per-GPU private buffer for the node's own operations.
- `enable_offload`: when `true`, vLLM allocates a DirectIO staging buffer so large prefills do not exceed the owner's SSD-write budget; set together with matching `--enable_offload=true` on `mooncake_master` and on the external `mooncake_client` when present.
- `tenant_id`: optional tenant namespace; producers and consumers that should share data must use the same id; default `"default"`.

## Single-node offload

Extend effective cache with CPU memory[^mooncake-store]:

```bash
MOONCAKE_CONFIG_PATH=mooncake_config.json \
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --kv-transfer-config '{"kv_connector":"MooncakeStoreConnector","kv_role":"kv_both"}'
```

## Disaggregated prefill-decode

Combine P2P transfer with the shared pool through `MultiConnector`: `MooncakeConnector` for direct prefill-to-decode transfer plus `MooncakeStoreConnector` for cross-instance prefix sharing[^mooncake-store].

Prefiller[^mooncake-store]:

```bash
MOONCAKE_CONFIG_PATH=mooncake_config.json \
VLLM_MOONCAKE_BOOTSTRAP_PORT=50052 \
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --port 8100 \
    --kv-transfer-config '{
        "kv_connector": "MultiConnector",
        "kv_role": "kv_producer",
        "kv_connector_extra_config": {
            "connectors": [
                {"kv_connector": "MooncakeConnector", "kv_role": "kv_producer"},
                {"kv_connector": "MooncakeStoreConnector", "kv_role": "kv_both"}
            ]
        }
    }'
```

Decoder[^mooncake-store]:

```bash
MOONCAKE_CONFIG_PATH=mooncake_config.json \
VLLM_MOONCAKE_BOOTSTRAP_PORT=50053 \
vllm serve meta-llama/Llama-3.1-8B-Instruct \
    --port 8200 \
    --kv-transfer-config '{
        "kv_connector": "MultiConnector",
        "kv_role": "kv_consumer",
        "kv_connector_extra_config": {
            "connectors": [
                {"kv_connector": "MooncakeConnector", "kv_role": "kv_consumer"},
                {"kv_connector": "MooncakeStoreConnector", "kv_role": "kv_consumer"}
            ]
        }
    }'
```

A disaggregation proxy routes between prefiller and decoder; when `MooncakeConnector` P2P is also used, proxy setup follows its usage guide[^mooncake-store].

### Saving decode cache

To also offload newly completed decode blocks, set on the decoder's `MooncakeStoreConnector` entry[^mooncake-store]:

```json
{
    "kv_connector_extra_config": {
        "save_decode_cache": true
    }
}
```

When decode starts, the consumer fills any block-aligned prompt prefix missing from the store, then appends newly completed decode blocks; this keeps a complete reusable prefix and also covers prompt KV delivered directly by `MooncakeConnector`[^mooncake-store].

### Heterogeneous TP sharing

`store_tp_size` gives a common Store TP for endpoints with different local TP sizes[^mooncake-store]. When several prefillers use different TP sizes, opt in to a Store TP derived from their least common multiple[^mooncake-store]:

```json
{
    "kv_connector_extra_config": {
        "enable_store_tp_lcm": true,
        "prefill_tp_sizes": [4, 2]
    }
}
```

Rules[^mooncake-store]:

- Every prefiller and decoder sharing the entries must use the same list; the example selects Store TP 4, where a TP4 endpoint maps each rank to one shard and TP2 maps each rank to two shards, while runtime TP sizes are unchanged.
- A decoder with `"save_decode_cache": true` uses the same Store TP for decode KV from every prefiller.
- The list holds positive integer TP sizes; sharing requires Store TP at least the local TP and divisible by it, an LBHNC or LBNHC local KV cache, plus existing topology and KV-head constraints.
- The store namespace includes the attention backend's selected layout, so different layouts use separate entries.
- Malformed lists and unsupported endpoints fall back to an isolated rank-local key layout.
- When `enable_store_tp_lcm` is absent or false, `prefill_tp_sizes` has no effect and `store_tp_size` behavior is unchanged.

## Disk offloading

Disk offloading is most commonly run in `standalone-store` mode so one external `mooncake_client` owns the CPU pool and SSD tier instead of duplicating the SSD pool per rank, keeping DirectIO budget tracking on a single process[^mooncake-store].

Align three sides[^mooncake-store]:

1. Start `mooncake_master` with `--enable_offload=true`.
2. Start `mooncake_client` (owner) with `--enable_offload=true` plus an SSD path via `MOONCAKE_OFFLOAD_FILE_STORAGE_PATH`.
3. Set `"enable_offload": true` in the vLLM-side JSON config; this is read by the connector and is not an environment variable.

Example vLLM-side config[^mooncake-store]:

```json
{
  "mode": "standalone-store",
  "metadata_server": "P2PHANDSHAKE",
  "master_server_address": "127.0.0.1:50051",
  "global_segment_size": 0,
  "local_buffer_size": "4GB",
  "protocol": "rdma",
  "device_name": "mlx5_0",
  "enable_offload": true
}
```

Steer a rank to the local owner segment with[^mooncake-store]:

```bash
export MOONCAKE_PREFERRED_SEGMENT=127.0.0.1:50053
```

The owner's SSD directory, on-disk eviction policy, and DirectIO staging-buffer size are controlled on the `mooncake_client` side via standard Mooncake variables (`MOONCAKE_OFFLOAD_FILE_STORAGE_PATH`, `MOONCAKE_BUCKET_EVICTION_POLICY`, `MOONCAKE_USE_URING`, `MOONCAKE_OFFLOAD_LOCAL_BUFFER_SIZE_BYTES`, `MOONCAKE_OFFLOAD_TOTAL_SIZE_LIMIT_BYTES`, etc.), independent of the vLLM JSON config[^mooncake-store].

## Tenant isolation

Set `tenant_id` in the Mooncake JSON config when deployments need separate namespaces[^mooncake-store]:

```json
{
  "mode": "embedded",
  "metadata_server": "P2PHANDSHAKE",
  "master_server_address": "127.0.0.1:50051",
  "global_segment_size": "80GB",
  "local_buffer_size": "4GB",
  "protocol": "rdma",
  "device_name": "",
  "enable_offload": false,
  "tenant_id": "tenant-a"
}
```

Strict isolation requires a master started with `--enable_multi_tenants=true` plus a tenant quota policy registering each tenant; non-default `tenant_id` also requires a Mooncake version whose `MooncakeDistributedStore.setup()` accepts `tenant_id`[^mooncake-store]. In `standalone-store` mode start the external `mooncake_client` with the matching tenant id because that process owns the real store client[^mooncake-store].

## Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `MOONCAKE_CONFIG_PATH` | Path to Mooncake JSON config file | required |
| `VLLM_MOONCAKE_BOOTSTRAP_PORT` | Bootstrap port for `MooncakeConnector` P2P transfer, disagg mode only | `8998` |
| `MOONCAKE_PREFERRED_SEGMENT` | Pin rank replicas to a specific owner segment `host:port`; used in `standalone-store` mode | — |
| `MOONCAKE_REQUESTER_LOCAL_HOSTNAME` | Override hostname the vLLM rank registers as a requester; defaults to resolved IP | — |
| `VLLM_MOONCAKE_STORE_TIER_LOG` | When `1`, logs per-batch tier summary (memory vs disk hits) | disabled |
| `VLLM_MOONCAKE_DISK_STAGING_USABLE_RATIO` | Fraction of owner DirectIO staging buffer filled in one `batch_get_into_multi_buffers` call; lower is more conservative pre-split with more round trips | `0.9` |

All rows from the source table are preserved here[^mooncake-store].

## KV roles

- `kv_producer`: instances that store KV caches to the pool[^mooncake-store].
- `kv_consumer`: instances that load KV caches from the pool[^mooncake-store].
- `kv_both`: instance both stores and loads; use for single-node CPU offloading or prefiller instances[^mooncake-store].

## `kv_connector_extra_config`

- `load_async` (bool): async loading for compute/I-O overlap; default `true`[^mooncake-store].
- `lookup_async` (bool): run external prefix-cache lookup on a background thread so it never blocks the scheduler step; the request is held until the in-flight lookup completes, then resumed on a later step; default `false`[^mooncake-store].
- `lookup_rpc_port` (int): custom port for the ZMQ lookup RPC socket; default `0`[^mooncake-store].
- `cache_prefix` (str): namespace prepended to every store key so deployments sharing one master do not pollute each other; instances with different prefixes never see each other's blocks even for identical prompts, while instances that should share must use the same value; default `""`, where keys are byte-identical to the unprefixed format[^mooncake-store].
- `save_decode_cache` (bool): offload decode tokens' KV; a `kv_consumer` does not save during prefill, but when decode starts it fills missing block-aligned prompt prefix before appending completed decode blocks; default `false`[^mooncake-store].
- `store_tp_size` (int): common Store TP for different local TP sizes; supports LBHNC and LBNHC local caches with `store_tp_size >= local_tp_size` and `store_tp_size % local_tp_size == 0`; current topology is one full-attention cache group with PCP/DCP disabled and cross-layer blocks disabled; for GQA/MHA total KV-head count must be divisible by `store_tp_size`; shards hold fixed global KV-head ranges in the local layout; shared endpoints use the same KV layout, pipeline-parallel size, and Store TP; the namespace includes layout and PP size; unsupported configurations use a topology-specific rank-local namespace[^mooncake-store].

LBHNC/HND is strongly recommended for TP-sharded Store when supported; LBNHC/NHD creates many transfer segments and may significantly reduce PUT/GET performance[^mooncake-store].

Example: with prefill TP 4, decode TP 2, and eight KV heads, set `store_tp_size` to 4 on both; each decode rank reads/writes two of the four shards[^mooncake-store].

MQA with one total KV head uses a replicated-head layout: for the supported prefill TP 4 to decode TP 2 case every rank uses the same rank-0 key namespace; the four prefill replicas stripe block PUTs so each object is stored once, while both decode ranks GET every block into their local replica; `store_tp_size` does not appear in MQA keys, so identical MQA objects written at different store TP sizes share the same pool entry when PP sizes match[^mooncake-store].

Tensor-parallel collectives and low-precision arithmetic are not bitwise invariant across TP sizes, so heterogeneous-TP reuse does not guarantee the same greedy output as recomputing the prefix at the decode TP size[^mooncake-store].

## Reproducible block hashes

The connector relies on consistent block hashes across processes sharing the store; hashes chain from `NONE_HASH`, derived from a fixed default seed, so identical prompts produce identical hashes by default and get cross-process prefix hits without extra configuration[^mooncake-store].

The exception is non-cryptographic `xxhash`/`xxhash_cbor` values of `--prefix-caching-hash-algo`, which seed `NONE_HASH` randomly per process; sharing a store with those requires `PYTHONHASHSEED`[^mooncake-store].

To use a custom shared seed, set the same `PYTHONHASHSEED` on every instance sharing the store (DP ranks, separate prefiller/decoder nodes, and any other vLLM process pointed at the same store)[^mooncake-store]:

```bash
PYTHONHASHSEED=<shared-value> vllm serve ...
```

## Relationships

- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — general prefill/decode split and connector catalog; this concept covers only the Mooncake-store pool setup, `MultiConnector` combination, and store-TP sharing.
- Uses [vLLM Mooncake Connector](vllm-mooncake-connector.md) — direct P2P KV leg combined with the store pool via `MultiConnector`, shared bootstrap-port convention, and proxy setup; this concept covers only the store-pool leg and its extra config.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — hash-chained full-block reuse extended across instances through the store; this concept covers the cross-process hash, seed, `cache_prefix`, and async-lookup mechanics.
- Uses [vLLM KV Offloading Connector](vllm-kv-offloading.md) — alternative local/tiered CPU offload path; this concept covers the external distributed-store offload, disk tier, and tenant isolation instead.

## Coverage limits

- Linked Mooncake project repository and build documentation were not inspected; install claims rest on the quoted `uv pip install mooncake-transfer-engine` line[^mooncake-store].
- Proxy setup defers to `mooncake_connector_usage.md`; only the deferral stated in this source is covered, with full P2P proxy detail in [vLLM Mooncake Connector](vllm-mooncake-connector.md)[^mooncake-store].
- Referenced `mooncake_master`, `mooncake_client`, and Mooncake environment-variable behaviors are reported as documented without inspecting their implementations[^mooncake-store].

[^mooncake-store]: MooncakeStoreConnector Usage Guide — `../raw/vllm/features/mooncake_store_connector_usage.md`, covering store-vs-P2P distinction, master/config prerequisites, `embedded` versus `standalone-store` modes, single-node and `MultiConnector` disaggregated commands, `save_decode_cache`, `store_tp_size` and `enable_store_tp_lcm` heterogeneous-TP sharing, disk-offload alignment, `tenant_id` isolation, environment variables, `kv_connector_extra_config` reference with MQA and bitwise-invariance caveats, and `PYTHONHASHSEED` reproducible-hash guidance.
