---
type: Concept
title: SGLang PD Disaggregation
description: Separate prefill and decode instances in SGLang with Mooncake, NIXL, and Ascend KV transfer, PD-aware routing, and tuned timeouts.
tags: [sglang, disaggregated-inference, prefill-decode, mooncake, nixl, ascend]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-pd-disagg
    resource: ../raw/sglang/advanced_features/pd_disaggregation.mdx
    title: PD Disaggregation
  - id: qwen38-day0
    resource: ../raw/2026-08-12-qwen3-8-day0-support/index.md
    title: 'SGLang and Miles Add Day-0 Support for Qwen3.8'
---

SGLang PD disaggregation runs prefill and decode in separate instances connected by a KV-cache transfer engine and a PD-aware router, avoiding unified-scheduling prefill interruption and DP-attention imbalance[^sgl-pd-disagg].

## Motivation

LLM inference splits into compute-intensive prefill over the full input sequence and memory-intensive decode managing the KV cache for token generation[^sgl-pd-disagg]:

- **Prefill interruption:** incoming prefill batches interrupt ongoing decode batches, delaying token generation.
- **DP-attention imbalance:** one data-parallel worker may run prefill while another runs decode, inflating decode latency.

Separating the stages allows tailored optimization per stage[^sgl-pd-disagg].

## Transfer backends

Supported backends are Mooncake and NIXL, plus an Ascend backend for NPU deployments[^sgl-pd-disagg]:

- **Mooncake:** install with `uv pip install mooncake-transfer-engine`; select IB device with `--disaggregation-ib-device`, e.g. `mlx5_roce0`[^sgl-pd-disagg].
- **NIXL:** install with `pip install nixl`, or build from source against an existing UCX with `--config-settings=setup-args="-Ducx_path=/path/to/ucx"`; select with `--disaggregation-transfer-backend nixl`[^sgl-pd-disagg].
- **Ascend:** install `pip install memfabric-hybrid==1.0.5` and set `ASCEND_MF_STORE_URL="tcp://xxx.xx.xxx.xxx:xxxx"`; set `ASCEND_NPU_PHY_ID` in the container environment; select with `--disaggregation-transfer-backend ascend`[^sgl-pd-disagg].
- **Ascend via Mooncake:** set `ENABLE_ASCEND_TRANSFER_WITH_MOONCAKE=true` to use the Mooncake path on Ascend; details are in the Mooncake section of the source[^sgl-pd-disagg].

## Deployment shapes

All shapes use `--disaggregation-mode prefill|decode` plus a router launched with `--pd-disaggregation --prefill <prefill-url> --decode <decode-url>`[^sgl-pd-disagg].

### Mooncake single-node Llama

```bash
python -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --disaggregation-mode prefill \
  --port 30000 \
  --disaggregation-ib-device mlx5_roce0
python -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --disaggregation-mode decode \
  --port 30001 \
  --base-gpu-id 1 \
  --disaggregation-ib-device mlx5_roce0
python -m sglang_router.launch_router --pd-disaggregation --prefill http://127.0.0.1:30000 --decode http://127.0.0.1:30001 --host 0.0.0.0 --port 8000
```

Decode uses `--base-gpu-id 1` to place it on a different GPU in the example[^sgl-pd-disagg].

### NIXL single-node Llama

Same ports and router as Mooncake, but with `--disaggregation-transfer-backend nixl` and no `--disaggregation-ib-device`[^sgl-pd-disagg]:

```bash
python -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --disaggregation-mode prefill \
  --port 30000 \
  --disaggregation-transfer-backend nixl
python -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --disaggregation-mode decode \
  --port 30001 \
  --base-gpu-id 1 \
  --disaggregation-transfer-backend nixl
python -m sglang_router.launch_router --pd-disaggregation --prefill http://127.0.0.1:30000 --decode http://127.0.0.1:30001 --host 0.0.0.0 --port 8000
```

### Ascend single-node Llama

Same shape with `--disaggregation-transfer-backend ascend`[^sgl-pd-disagg].

### DeepSeek multi-node

Prefill and decode each span 2 nodes with separate `--dist-init-addr` masters, `--tp-size 16 --dp-size 8 --enable-dp-attention --moe-a2a-backend deepep --mem-fraction-static 0.8`, and `--max-running-requests 128` on decode nodes[^sgl-pd-disagg]:

- Mooncake variant adds `--disaggregation-ib-device ${device_name}`.
- NIXL variant adds `--disaggregation-transfer-backend nixl`.
- Ascend variant uses `--disaggregation-transfer-backend ascend` with `--nnodes 1 --node-rank 0 --tp-size 16` in the illustrated commands.

Router and load-balancing detail lives in the Model Gateway / Router guide, not in this source[^sgl-pd-disagg].

## Mooncake advanced configuration

### NVLink transport

For NVLink KV transfer with the Mooncake backend, e.g. NVL72 deployments[^sgl-pd-disagg]:

```bash
export SGLANG_MOONCAKE_CUSTOM_MEM_POOL=True
export MC_FORCE_MNNVL=True
```

Auxiliary data transfer still uses TCP as a temporary workaround[^sgl-pd-disagg].

### Prefill server variables

- `SGLANG_DISAGGREGATION_THREAD_POOL_SIZE` — worker threads for KV transfer per TP rank; dynamic default `int(0.75 * os.cpu_count()) // 8`, clamped to `>4` and `<12`[^sgl-pd-disagg].
- `SGLANG_DISAGGREGATION_QUEUE_SIZE` — parallel transfer queues sharding requests from multiple decode instances; default `4`; `1` means one-by-one FCFS transfer[^sgl-pd-disagg].
- `SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT` — seconds to receive destination KV indices during request init; default `300`; relaxing to `600` tolerates higher mean TTFT but delays prefill memory cleanup when a decode node disconnects[^sgl-pd-disagg].

### Decode server variables

- `SGLANG_DISAGGREGATION_HEARTBEAT_INTERVAL` — seconds between health checks to prefill bootstrap servers; default `5.0`[^sgl-pd-disagg].
- `SGLANG_DISAGGREGATION_HEARTBEAT_MAX_FAILURE` — consecutive heartbeat failures before marking a prefill server offline; default `2`[^sgl-pd-disagg].
- `SGLANG_DISAGGREGATION_WAITING_TIMEOUT` — seconds to receive KV cache after request init; default `300`; relaxing to `600` tolerates higher mean TTFT[^sgl-pd-disagg].

## NIXL advanced configuration

`SGLANG_DISAGGREGATION_NIXL_BACKEND` selects the NIXL plugin backend; default is `UCX`, with `LIBFABRIC` or any installed NIXL plugin as alternatives[^sgl-pd-disagg]:

```bash
export SGLANG_DISAGGREGATION_NIXL_BACKEND=LIBFABRIC
python -m sglang.launch_server \
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --disaggregation-mode prefill \
  --disaggregation-transfer-backend nixl \
  --port 30000
```

## Profiling and routing integration

- Profile prefill and decode workers separately with dedicated command-line options because of torch-profiler limitations; procedure is in the Benchmark and Profiling guide section `Profile In PD Disaggregation Mode`[^sgl-pd-disagg].
- For scale deployment with load balancing and fault tolerance, front prefill/decode instances with the SGLang Router / Model Gateway using `--pd-disaggregation` and routing policies; setup is in that guide, not repeated here[^sgl-pd-disagg].

## Qwen3.8 three-state transfer with staging buffer

Qwen3.8 extends PD transfer beyond KV cache to all three GDN serving states through a typed registry, with independent `q`/`k`/`v` convolution-window resharding across TP ranks and MTP draft KV, hidden states, and top-k metadata in the same payload so speculation continues on decode[^qwen38-day0]. A GPU staging buffer coalesces per-layer slices into one bulk RDMA transfer per chunk under a chunk-index plus watermark contract, letting PP prefill and wide-EP decode use independent layouts and be sized in parallel[^qwen38-day0]. Detail and 8K/1K PD endpoints are maintained in [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md).

## Relationships

- Uses [SGLang EPD Disaggregation](sglang-epd-disaggregation.md) — three-tier extension separating the vision encoder from the prefill/decode split covered here.
- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) — prefill-only versus full HiCache with decode offload patterns that compose with this PD split.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — vLLM analog separating prefill and decode with connector-mediated KV transfer to tune TTFT/ITL independently.
- Uses [vLLM Mooncake Connector](vllm-mooncake-connector.md) — vLLM-side Mooncake RDMA transfer analog for the prefill-to-decode leg.
- Uses [vLLM NIXL Connector Usage](vllm-nixl-connector-usage.md) — vLLM-side NIXL deployment analog for the prefill-to-decode leg.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — Qwen3.8 three-state typed transfer with convolution-window resharding and watermarked staging-buffer bulk RDMA.

## Coverage limits

- Design-doc link, Benchmark and Profiling guide, and Model Gateway / Router guide were referenced but not inspected; profiling flags, router policies, and fault-tolerance behavior beyond the quoted `--pd-disaggregation --prefill --decode` invocation are outside verified scope[^sgl-pd-disagg].
- No latency, throughput, TTFT/ITL, or transfer-bandwidth measurements were in the source[^sgl-pd-disagg].

[^sgl-pd-disagg]: PD Disaggregation — `../raw/sglang/advanced_features/pd_disaggregation.mdx`, covering prefill/decode resource profiles and unified-scheduling prefill interruption plus DP-attention imbalance, Mooncake and NIXL plus Ascend transfer backends with install and `--disaggregation-mode` / `--disaggregation-transfer-backend` / `--disaggregation-ib-device` launch shapes for single-node Llama and multi-node DeepSeek with router commands, Mooncake NVLink variables and prefill/decode thread-pool / queue / bootstrap / heartbeat / waiting timeouts, and `SGLANG_DISAGGREGATION_NIXL_BACKEND` plugin selection.
[^qwen38-day0]: SGLang and Miles Add Day-0 Support for Qwen3.8 — `../raw/2026-08-12-qwen3-8-day0-support/index.md`, covering typed three-state transfer with convolution-window resharding and watermarked staging-buffer bulk RDMA.
