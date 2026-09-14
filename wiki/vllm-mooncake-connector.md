---
type: Concept
title: vLLM Mooncake Connector
description: RDMA-based disaggregated prefill/decode KV transfer via Mooncake with producer/consumer roles, bootstrap and RDMA-registration tuning, and proxy fan-out.
tags: [vllm, disaggregated-prefill, kv-cache, mooncake, rdma]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T17:00:00Z }
sources:
  - id: mooncake-connector
    resource: ../raw/vllm/features/mooncake_connector_usage.md
    title: MooncakeConnector Usage Guide
---

MooncakeConnector moves KV caches from a prefill producer to a decode consumer over the Mooncake transfer engine, using zero-copy (GPUDirect) RDMA over multi-NIC DRAM/SSD pooling, with `kv_role` selecting producer/consumer/symmetric behavior and a disaggregation proxy fanning requests out to both legs[^mooncake-connector].

## Background

- Mooncake builds a multi-level caching pool on high-speed interconnected DRAM/SSD resources, aimed at LLM inference efficiency especially in slow object-storage environments[^mooncake-connector].
- Compared with traditional caching, it transfers data directly zero-copy via (GPUDirect) RDMA while maximizing multi-NIC resources on a single machine[^mooncake-connector].

## Installation

- Install via `uv pip install mooncake-transfer-engine-cuda13`[^mooncake-connector].
- vLLM defaults to CUDA 13; on a CUDA 12 environment install `mooncake-transfer-engine` instead — the two are the same release built against different CUDA majors, and the wrong one fails to import with `libcudart.so.<major>: cannot open shared object file`[^mooncake-connector].
- The source points to the Mooncake official repository for further installation instructions[^mooncake-connector].

## Deployment shape

Prefill producer, decode consumer, and proxy[^mooncake-connector]:

```bash
# Prefiller node (example 192.168.0.2)
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8010 --kv-transfer-config '{"kv_connector":"MooncakeConnector","kv_role":"kv_producer"}'
```

```bash
# Decoder node (example 192.168.0.3)
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8020 --kv-transfer-config '{"kv_connector":"MooncakeConnector","kv_role":"kv_consumer"}'
```

```bash
# Proxy
python examples/disaggregated/mooncake_connector/mooncake_connector_proxy.py --prefill http://192.168.0.2:8010 --decode http://192.168.0.3:8020
```

- Requests go to the proxy server through port 8000[^mooncake-connector].

## KV roles

- **kv_producer:** prefiller instances that generate KV caches[^mooncake-connector].
- **kv_consumer:** decoder instances that consume KV caches from prefiller[^mooncake-connector].
- **kv_both:** symmetric mode where the connector acts as both producer and consumer, for experimental setups and scenarios where the role distinction is not predetermined[^mooncake-connector].

## Connector extra config

`kv_connector_extra_config` fields[^mooncake-connector]:

| Field | Meaning | Default |
|-------|---------|---------|
| `num_workers` | Thread-pool size for one prefiller worker to transfer KV caches by Mooncake | `10` |
| `mooncake_protocol` | Mooncake connector protocol | `"rdma"` |
| `device_name` | Comma-separated RDMA-device whitelist (e.g. `"mlx5_0,mlx5_1"`) restricting topology discovery; empty discovers every device | empty |

- `device_name` is useful on hosts exposing a mix of InfiniBand and RoCE ports, where both peers must settle on the same link layer[^mooncake-connector].

## Environment variables

- `VLLM_MOONCAKE_BOOTSTRAP_PORT`: port for the Mooncake bootstrap server[^mooncake-connector].
  - Default `8998`[^mooncake-connector].
  - Required only for prefiller instances[^mooncake-connector].
  - For headless instances, must be the same as the master instance[^mooncake-connector].
  - Each instance needs a unique port on its host; using the same port number across different hosts is fine[^mooncake-connector].
- `WITH_NVIDIA_PEERMEM`: selects how Mooncake registers GPU memory for RDMA; read by Mooncake, not vLLM[^mooncake-connector].
  - Default `1`, which uses `ibv_reg_mr()` and requires the `nvidia-peermem` kernel module to be loaded[^mooncake-connector].
  - Set to `0` to use the DMA-BUF path, which does not need that module; required on hosts where `nvidia-peermem` is not loaded, such as GB200[^mooncake-connector].
  - With the container image, pass it at run time: `docker run -e WITH_NVIDIA_PEERMEM=0 ...`[^mooncake-connector].
  - Symptom when left unset on such a host: `Failed to register memory <addr>: Bad address [14]` from `rdma_context.cpp`, and KV transfers fail[^mooncake-connector].
- `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT`: timeout in seconds for automatically releasing the prefiller's KV cache for a request; optional, default `480`[^mooncake-connector].
  - If a request is aborted and the decoder has not yet notified the prefiller, the prefill instance releases its KV-cache blocks after this timeout to avoid holding them indefinitely[^mooncake-connector].

## Relationships

- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — general prefill/decode split and connector catalog; this concept covers only the MooncakeConnector setup, roles, tuning, and proxy shape.
- Uses [vLLM Mooncake Store Connector](vllm-mooncake-store-connector.md) — shared-store pool leg combined with this P2P connector via `MultiConnector`; this concept covers only the direct transfer leg.

## Coverage limits

- Referenced example scripts `examples/disaggregated/mooncake_connector/run_mooncake_connector.sh` and `examples/disaggregated/mooncake_connector/mooncake_connector_proxy.py` were not present under `raw/` and were not inspected; synthesis follows the usage-guide text and quoted commands alone[^mooncake-connector].
- Linked Mooncake project and documentation sites were not inspected; background claims beyond the quoted DRAM/SSD pool and RDMA zero-copy description are outside verified scope[^mooncake-connector].
- Store-pool setup is now compiled in [vLLM Mooncake Store Connector](vllm-mooncake-store-connector.md)[^mooncake-connector].

[^mooncake-connector]: MooncakeConnector Usage Guide — `../raw/vllm/features/mooncake_connector_usage.md`, covering Mooncake background, CUDA-major install selection, prefiller/decoder/proxy commands, `kv_producer` / `kv_consumer` / `kv_both` roles, `num_workers` / `mooncake_protocol` / `device_name` extra config, `VLLM_MOONCAKE_BOOTSTRAP_PORT` / `WITH_NVIDIA_PEERMEM` / `VLLM_MOONCAKE_ABORT_REQUEST_TIMEOUT` behavior, and example-script references.
