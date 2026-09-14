---
type: Concept
title: vLLM NIXL Connector Usage
description: Installing, configuring, deploying, and observing NixlConnector for vLLM disaggregated prefill/decode, including bidirectional multi-turn transfer.
tags: [vllm, nixl, disaggregated-prefill, kv-cache, deployment, observability]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T20:00:00Z }
sources:
  - id: nixl-usage
    resource: ../raw/vllm/features/nixl_connector_usage.md
    title: NixlConnector Usage Guide
---

NixlConnector is the NIXL-backed, fully asynchronous KV-cache transfer connector for vLLM disaggregated prefill/decode, configured via `--kv-transfer-config` with producer/consumer roles, UCX-dominated transport selection, side-channel handshake ports, lease/TTL retention, single-host through multi-host proxy topologies, optional bidirectional decode-to-prefill reuse, and NIXL transfer logging plus Prometheus metrics[^nixl-usage].

## Prerequisites and install

- Install NIXL with `uv pip install nixl` as the NVIDIA quick start; required version is pinned in `requirements/kv_connectors.txt` and related configs[^nixl-usage].
- For ROCm, the ROCm Dockerfile builds NIXL and UCX with ROCm support from source[^nixl-usage].
- For non-CUDA platforms, install NIXL with UCX built from source via `python tools/install_nixl_from_source_ubuntu.py`[^nixl-usage].

## Transport configuration

- Underlying communication uses NIXL; UCX is the primary default transport[^nixl-usage].
- Configure UCX environment variables such as `UCX_TLS=all` and `UCX_NET_DEVICES=all`, adjusted to specific transports or NICs (for example `rc,ud,sm,^cuda_ipc` or `mlx5_0:1,mlx5_1:1`)[^nixl-usage].
- NCCL variables such as `NCCL_IB_HCA` or `NCCL_SOCKET_IFNAME` do not apply to NixlConnector; use UCX-specific variables instead[^nixl-usage].
- Select a non-default NIXL plugin via `kv_connector_extra_config.backends` in `--kv-transfer-config`, for example `{"backends":["LIBFABRIC"]}`; dotted CLI form `--kv-transfer-config.kv_connector_extra_config.backends+ LIBFABRIC` is also supported[^nixl-usage].
- Backend availability depends on how NIXL was built and which plugins are present[^nixl-usage].

## Basic same-host deployment

Producer (prefill) and consumer (decode) are separate `vllm serve` processes with complementary `kv_role` values and distinct side-channel ports[^nixl-usage]:

```bash
# Prefill on GPU 0
CUDA_VISIBLE_DEVICES=0 UCX_NET_DEVICES=all VLLM_NIXL_SIDE_CHANNEL_PORT=5600 \
vllm serve Qwen/Qwen3-0.6B --port 8100 --enforce-eager \
  --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_producer","kv_load_failure_policy":"fail"}'

# Decode on GPU 1
CUDA_VISIBLE_DEVICES=1 UCX_NET_DEVICES=all VLLM_NIXL_SIDE_CHANNEL_PORT=5601 \
vllm serve Qwen/Qwen3-0.6B --port 8200 --enforce-eager \
  --kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_consumer","kv_load_failure_policy":"fail"}'
```

Route requests through a proxy between the two ports[^nixl-usage]:

```bash
python tests/v1/kv_connector/nixl_integration/toy_proxy_server.py \
  --port 8192 --prefiller-hosts localhost --prefiller-ports 8100 \
  --decoder-hosts localhost --decoder-ports 8200
```

## Environment variables and retention tuning

- `VLLM_NIXL_SIDE_CHANNEL_PORT`: NIXL handshake port, default `5600`, required on both P and D; each worker on a host needs a unique port, while reuse of the same base number across hosts is fine; under TP/DP the per-worker port is `base_port + dp_rank`[^nixl-usage].
- `VLLM_NIXL_SIDE_CHANNEL_HOST`: side-channel host, default `localhost`; set when P and D are on different machines; connection info travels via `KVTransferParams` from P to D for handshake[^nixl-usage].
- `kv_lease_duration` in `kv_connector_extra_config`: seconds P holds finished prefill blocks awaiting D reads, default `30`; queued D requests extend it with periodic heartbeats whose interval and extension derive from this value; expiry without heartbeat or read frees the blocks[^nixl-usage].
- `decoder_kv_blocks_ttl` in `kv_connector_extra_config`: seconds D caches KV blocks for bidirectional reuse, default `480`; unlike the P lease it is not heartbeat-renewed[^nixl-usage].

## Multi-instance and multi-host deployment

- Run each P and D on its own machine with its own `VLLM_NIXL_SIDE_CHANNEL_HOST` and port, same `--tensor-parallel-size`, and matching producer/consumer `--kv-transfer-config`; fan out with one proxy invocation listing all P hosts/ports and D hosts/ports[^nixl-usage].
- For multi-host data-parallel deployment, provide only the head-instance host/port to the proxy[^nixl-usage].

## Roles and failure policy

- `kv_producer`: prefill instances that generate KV caches[^nixl-usage].
- `kv_consumer`: decode instances that consume KV from prefill[^nixl-usage].
- `kv_both` is deprecated for NixlConnector, planned for removal; set explicit producer/consumer roles instead[^nixl-usage].
- `kv_load_failure_policy` controls D behavior when loading P blocks fails[^nixl-usage]:
  - `fail` (default): fail the request immediately, avoiding decode-side recomputation and tail-latency inflation[^nixl-usage].
  - `recompute`: recompute failed blocks locally on D, which can cause jitter and inefficiency because D is decode-optimized; discouraged for production[^nixl-usage].

## Platform special cases

- On NVIDIA GB-series GPUs with multi-node NVLink, register KV cache as VMM with `--enable-cumem-allocator` or `--enable-sleep-mode` plus `UCX_CUDA_IPC_ENABLE_MNNVL: 'y'`; otherwise cross-node transfers fall back to RDMA/TCP[^nixl-usage].
- Experimental heterogeneous-layout support (for example prefill `LBHNC` with decode `LBNHC`) is enabled with `--kv-transfer-config '{..., "enable_permute_local_kv":"True"}'`[^nixl-usage].

## Bidirectional KV transfer for multi-turn

Standard flow is P-to-D only, so every new turn recomputes prior-turn KV on P. Bidirectional mode lets P pull D-cached KV via RDMA and compute only new tokens, reducing TTFT for long multi-turn prompts[^nixl-usage].

Turn 1 is a cache miss (full prefill on P, D pulls from P, proxy caches D's returned `kv_transfer_params` by `conversation_id`); turn 2+ is a cache hit (proxy attaches cached D `remote_block_ids` to P, P pulls from D, then D pulls the new blocks from P and the proxy updates the cache)[^nixl-usage]. This requires a stateful proxy to track and forward `kv_transfer_params` between turns[^nixl-usage].

Enable on both P and D[^nixl-usage]:

```bash
--kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_producer","kv_connector_extra_config":{"bidirectional_kv_xfer":true}}'
--kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_consumer","kv_connector_extra_config":{"bidirectional_kv_xfer":true}}'
```

| Parameter | Default | Meaning |
|---|---|---|
| `bidirectional_kv_xfer` | `false` | Enable D-to-P pull path[^nixl-usage]. |
| `kv_recompute_threshold` | `64` | Minimum remote tokens to justify a D-to-P pull; below this P recomputes locally to amortize transfer latency[^nixl-usage]. |
| `decoder_kv_blocks_ttl` | `480` | Seconds D retains cacheable blocks for bidirectional reuse, not heartbeat-renewed[^nixl-usage]. |

Multi-turn proxy and client contract:

- Serve through `examples/disaggregated/disaggregated_serving/disagg_proxy_multiturn.py` with P/D host/port arguments; multiple P/D instances use plural `--prefiller-hosts/--prefiller-ports` and `--decoder-hosts/--decoder-ports` with round-robin[^nixl-usage].
- Clients must send a non-standard `conversation_id` field consumed by the proxy and not forwarded to the engine; without it every turn is a cache miss[^nixl-usage].
- Benchmark with `benchmarks/multi_turn/benchmark_serving_multi_turn.py --send-conversation-id`; the flag is off by default for strict OpenAI-compatible frontends, and omitting it against the multi-turn proxy never exercises the bidirectional path[^nixl-usage].

Limitations:

- Currently CUDA device-buffer KV only; host-buffer support (for example Intel XPU) is planned[^nixl-usage].
- Reasoning models that strip `<think>...</think>` traces break the prefix assumption: D blocks cover the full sequence including thinking tokens, while P's next-turn prompt is missing middle tokens, so block-aligned pulls transfer wrong-position cache and produce incorrect results; the router is expected to detect such mismatch[^nixl-usage].

## Observability

Periodic `KV Transfer metrics` log lines summarize successful transfers in the interval: count, mean and P90 transfer time (`xferDuration`, post-to-completion including data movement), mean and P90 post time (`postDuration`, synchronous RDMA submit cost), mean MB per transfer, aggregate throughput MB/s, and mean descriptor count; failed transfers are counted separately in Prometheus[^nixl-usage].

Prometheus metrics when NixlConnector is active[^nixl-usage]:

| Metric | Type | Meaning |
|---|---|---|
| `vllm:nixl_xfer_time_seconds` | Histogram | Per-transfer RDMA copy duration[^nixl-usage]. |
| `vllm:nixl_post_time_seconds` | Histogram | RDMA submit duration[^nixl-usage]. |
| `vllm:nixl_bytes_transferred` | Histogram | Bytes per transfer[^nixl-usage]. |
| `vllm:nixl_num_descriptors` | Histogram | Descriptors per transfer[^nixl-usage]. |
| `vllm:nixl_num_failed_transfers` | Counter | Cumulative failed KV-block transfers[^nixl-usage]. |
| `vllm:nixl_num_failed_notifications` | Counter | Cumulative failed `send_notif` completions[^nixl-usage]. |
| `vllm:nixl_num_kv_expired_reqs` | Counter | P-side requests expired before D read; high values mean `kv_lease_duration` is too short[^nixl-usage]. |

## Example scripts

- `tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh`, `toy_proxy_server.py`, and `test_accuracy.py` are the referenced vLLM-repo examples[^nixl-usage].

## Relationships

- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — general P/D split, connector catalog, and transfer abstractions; this concept covers only NixlConnector install, transport, deployment, bidirectional, and metrics operation.
- Uses [vLLM NIXL Connector Compatibility](vllm-nixl-connector-compatibility.md) — supported architectures, TP/layout/quantization and handshake rules; this concept covers only operational setup, not compatibility.
- Uses [vLLM NIXL KV Cache Lease Renewal](vllm-nixl-kv-lease.md) — heartbeat, interval/extension derivation, and bidirectional-TTL design behind `kv_lease_duration` and `decoder_kv_blocks_ttl`; this concept covers only the operator-visible defaults and tuning.
- Uses [vLLM NIXL Push-Mode KV Transfer](vllm-nixl-kv-push-connector.md) — push WRITE is the alternative to the pull READ path assumed here; this concept covers only pull-mode usage plus bidirectional pulls.
- Uses [vLLM Metrics and Observability](vllm-metrics.md) — general vLLM Prometheus/logging architecture; this concept covers only NixlConnector transfer log fields and `vllm:nixl_*` metrics.

## Coverage limits

- Compatibility details live in [vLLM NIXL Connector Compatibility](vllm-nixl-connector-compatibility.md) and were not recompiled here; only the pointer from this source is covered[^nixl-usage].
- Referenced repo files outside `raw/` (`requirements/kv_connectors.txt`, ROCm Dockerfile, `tools/install_nixl_from_source_ubuntu.py`, proxy/benchmark/example scripts, and linked GitHub issues) were not inspected; claims about them follow this source's text alone[^nixl-usage].
- Mermaid flow diagram semantics are summarized as turn-1 versus turn-2+ steps; visual styling is not part of verified scope[^nixl-usage].

[^nixl-usage]: NixlConnector Usage Guide — `../raw/vllm/features/nixl_connector_usage.md`, covering NIXL install paths, UCX transport and `backends` selection, same-host P/D plus toy-proxy commands, side-channel port/host and `kv_lease_duration` / `decoder_kv_blocks_ttl` semantics, bidirectional sequence, `bidirectional_kv_xfer` / `kv_recompute_threshold` config, multi-turn proxy/client/benchmark contract with reasoning-trace warning, multi-instance and multi-host proxy shape, `kv_both` deprecation, `fail` versus `recompute` policy, GB-series VMM requirement, experimental layout permute flag, KV-transfer log and Prometheus metric definitions, and example-script pointers.
