---
type: Concept
title: vLLM MoRI-IO Connector
description: ROCm MoRI-IO disaggregated prefill/decode KV transfer with WRITE/READ modes, RDMA/xGMI transports, control-plane ports, and vllm-router proxy routing.
tags: [vllm, disaggregated-prefill, kv-cache, mori, rocm, rdma]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T18:00:00Z }
sources:
  - id: moriio-connector
    resource: ../raw/vllm/features/moriio_connector_usage.md
    title: MoRIIOConnector Usage Guide
---

MoRIIOConnector is a high-performance KV connector for prefill-decode disaggregated deployments on ROCm, built on the MoRI-IO point-to-point communication library for ultra-low-overhead transfer[^moriio-connector].

## Installation

- MoRI ships in the official ROCm vLLM image `vllm/vllm-openai-rocm:nightly`[^moriio-connector].
- Manual install via `pip install amd_mori`; the source points to `docker/Dockerfile.rocm_base` and the official MoRI repository for base-image details and source builds[^moriio-connector].
- RDMA deployments also need NIC userspace libraries matching the host kernel module and firmware; see [NIC libraries](#nic-userspace-libraries)[^moriio-connector].

## Deployment shape

Start the proxy first; producer and consumer instances retry registration until the proxy is reachable[^moriio-connector].

Single-host example uses `Qwen/Qwen3-235B-A22B-FP8` with `-tp 4`, `VLLM_ROCM_USE_AITER=1`, split GPUs `0,1,2,3` for prefill and `4,5,6,7` for decode, and `--gpu-memory-utilization 0.9`[^moriio-connector]:

```bash
# Prefiller / producer
vllm serve Qwen/Qwen3-235B-A22B-FP8 -tp 4 --port 20005 \
  --kv-transfer-config '{
    "kv_connector": "MoRIIOConnector",
    "kv_role": "kv_producer",
    "kv_connector_extra_config": {
      "proxy_ip": "127.0.0.1",
      "proxy_ping_port": "36367",
      "http_port": "20005",
      "handshake_port": "6301",
      "notify_port": "6105"
    }
  }'
```

```bash
# Decoder / consumer
vllm serve Qwen/Qwen3-235B-A22B-FP8 -tp 4 --port 40005 \
  --kv-transfer-config '{
    "kv_connector": "MoRIIOConnector",
    "kv_role": "kv_consumer",
    "kv_connector_extra_config": {
      "proxy_ip": "127.0.0.1",
      "proxy_ping_port": "36367",
      "http_port": "40005",
      "handshake_port": "7301",
      "notify_port": "7501"
    }
  }'
```

Multi-node 1P1D example runs `deepseek-ai/DeepSeek-R1-0528` with `--tensor-parallel-size 8`, `--enable-expert-parallel`, `--gpu-memory-utilization 0.8`, and `--trust-remote-code` in privileged host-network containers exposing `/dev/kfd`, `/dev/dri`, and `/dev/infiniband`; the proxy runs on the prefill node and both legs set `proxy_ip` to `PREFILL_IP`, with prefill on port `8100` and decode on port `8200` sharing `handshake_port 6301` and `notify_port 61005` in the quoted commands[^moriio-connector].

## Proxy

- `vllm-router` is the recommended proxy; it can run as a Docker container or via `pip install vllm-router`[^moriio-connector]:

```bash
vllm-router \
  --vllm-pd-disaggregation \
  --kv-connector moriio \
  --vllm-discovery-address "0.0.0.0:36367"
```

- Port `36367` in the proxy command is the `proxy_ping_port` configured on each vLLM instance[^moriio-connector].
- A reference toy proxy ships with vLLM at `examples/disaggregated/disaggregated_serving/moriio_toy_proxy_server.py` and needs `quart aiohttp msgpack`[^moriio-connector].

## Application-level configuration

### WRITE versus READ mode

- **WRITE mode (default):** the producer actively pushes computed KV blocks after every layer into consumer memory[^moriio-connector].
- **READ mode:** the consumer pulls all KV blocks at once after being notified they are ready; enable with `kv_connector_extra_config.read_mode: true`[^moriio-connector].

### Control-plane ports

KV bytes move over RDMA/xGMI, while out-of-band TCP channels carry handshake, block-id exchange, liveness, and completion signaling under `kv_connector_extra_config`[^moriio-connector]:

| Key | Meaning |
|-----|---------|
| `proxy_ip` | IP of the disaggregation proxy/router; instances register and heartbeat here so the proxy can route requests |
| `proxy_ping_port` | TCP port on `proxy_ip` where the proxy listens for registration and heartbeats; used to detect dead instances and refresh routing tables |
| `http_port` | OpenAI-compatible HTTP port this instance exposes; the proxy registers it and forwards selected requests to it |
| `handshake_port` | TCP port for the one-time MoRI engine handshake exchanging RDMA engine descriptors before transfer |
| `notify_port` | TCP port for control/synchronization, used differently per mode (below) |

- WRITE mode: decoder notifies prefiller of its block ids for placement (**block allocation**); prefiller notifies decoder when all blocks are transferred (**completion**)[^moriio-connector].
- READ mode: decoder notifies prefiller after it has read all blocks so the prefiller can free its KV blocks (**completion**)[^moriio-connector].
- `notify_port` is a base port: each `(DP rank, TP rank)` pair uses `notify_port + offset`, so the range starting at `notify_port` must be free on the host[^moriio-connector].

## Transport configuration

- Select backend with `kv_connector_extra_config.backend`: `rdma` (default, use for multi-node) or `xgmi`[^moriio-connector].
- Use xGMI when prefiller and decoder run on the same physical host so transfers use the AMD GPU fabric and skip the NIC[^moriio-connector].

### RDMA backend

- `qp_per_transfer`: RDMA Queue Pairs striped per transfer; more QPs increase NIC concurrency at higher RDMA-resource cost[^moriio-connector].
- `post_batch_size`: RDMA Work Requests batched per `ibv_post_send` doorbell; `-1` means backend default, and larger batches reduce per-WR posting overhead[^moriio-connector].
- `num_workers`: worker threads MoRI uses to post and poll completions[^moriio-connector].
- Advanced MoRI library variables such as `MORI_IO_QP_MAX_SEND_WR` and `MORI_IO_QP_MAX_CQE` are separate from vLLM's own `VLLM_MORIIO_*` settings; the source defers to the MoRI repository for details[^moriio-connector].

### xGMI backend

- Currently configured only through MoRI-specific environment variables; the source defers to the MoRI repository[^moriio-connector].

## Troubleshooting

- `availDevices.size() > 0` assertion from `mori::io::RdmaManager` with `libibverbs` warnings such as `Driver bnxt_re does not support the kernel ABI` means the installed RDMA userspace libraries do not match the host driver and firmware version[^moriio-connector].
- Fix by installing NIC userspace libraries matching the RDMA kernel module and firmware version[^moriio-connector].

## NIC userspace libraries

The official `vllm/vllm-openai-rocm:nightly` image pre-installs userspace libraries for[^moriio-connector]:

- AINIC (AMD Pensando Pollara): version `1.117.5-a-77`, ships `libionic1=54.0-187-1`, tested with `ionic-dkms=26.03.3.001`[^moriio-connector].
- Thor2 (Broadcom): version `235.2.86.0`, tested with `bnxt-en-dkms=1.10.3.235.2.86.0` and `bnxt-re-dkms=235.2.86.0`[^moriio-connector].

For other NICs, kernel modules, or firmware, follow the vendors' installation instructions; the source points to `docker/Dockerfile.rocm` for image details[^moriio-connector].

## Relationships

- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — general prefill/decode split and connector catalog; this concept covers only the MoRIIOConnector setup, modes, transports, ports, proxy, and NIC-library troubleshooting.

## Coverage limits

- `docker/Dockerfile.rocm_base`, `docker/Dockerfile.rocm`, the official MoRI repository, and the linked inference-disaggregation blog were not inspected; install, build, backend-variable, and background claims beyond the quoted text are outside verified scope[^moriio-connector].
- Example proxy `examples/disaggregated/disaggregated_serving/moriio_toy_proxy_server.py` was not present under `raw/` and was not inspected; synthesis follows the usage-guide commands alone[^moriio-connector].

[^moriio-connector]: MoRIIOConnector Usage Guide — `../raw/vllm/features/moriio_connector_usage.md`, covering MoRI-IO background, `amd_mori` / ROCm-image install, single-host and two-node producer/consumer/proxy commands, `vllm-router` versus toy proxy, WRITE default versus `read_mode`, `proxy_ip` / `proxy_ping_port` / `http_port` / `handshake_port` / `notify_port` control plane with base-port behavior, `rdma` versus `xgmi` backends with `qp_per_transfer` / `post_batch_size` / `num_workers`, `availDevices.size() > 0` userspace-mismatch fix, and AINIC/Thor2 library versions.
