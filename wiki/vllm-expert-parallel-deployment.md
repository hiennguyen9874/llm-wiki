---
type: Concept
title: vLLM Expert Parallel Deployment
description: Expert-parallel MoE serving with EP=TP×DP sharding, all-to-all backends, EPLB rebalancing, and prefill/decode disaggregation.
tags: [vllm, expert-parallel, moe, deployment, load-balancing]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:58:20Z }
sources:
  - id: ep-deploy
    resource: ../raw/vllm/serving/expert_parallel_deployment.md
    title: Expert Parallel Deployment
---

vLLM expert parallelism shards MoE expert layers across `TP × DP` ranks while attention layers stay replicated or tensor-parallel, with selectable all-to-all backends, optional expert load balancing, and prefill/decode-disaggregated operation[^ep-deploy].

## Prerequisites

- Install DeepEP kernels following the vLLM EP-kernels guide, plus the DeepGEMM library[^ep-deploy].
- For disaggregated serving also install `gdrcopy` via `install_gdrcopy.sh`; without it NIXL still works via pip with lower performance[^ep-deploy].
- On CUDA 13+, the `deepep_v2` backend requires NCCL >= 2.30.4; PyTorch ships an older NCCL so it must be upgraded before building or running DeepEP[^ep-deploy].

## All-to-all backend selection

Select with `--all2all-backend`[^ep-deploy]:

| Backend | Use case | Best for |
| ------- | -------- | -------- |
| `allgather_reducescatter` | Default all-to-all from allgather/reducescatter primitives | General purpose, any EP+DP configuration |
| `deepep_high_throughput` | Grouped GEMM with continuous layout | Prefill-dominated, high-throughput and multi-node prefill |
| `deepep_low_latency` | CUDA-graph support, masked layout | Decode-dominated, low-latency and multi-node decode |
| `flashinfer_nvlink_one_sided` | FlashInfer one-sided all-to-all | Multi-node NVLink high-throughput workloads |
| `flashinfer_nvlink_two_sided` | FlashInfer two-sided all-to-all | Systems with NVLink across nodes |

## Single-node configuration

Enable with `--enable-expert-parallel`; expert-parallel size is computed automatically as `EP_SIZE = TP_SIZE × DP_SIZE`[^ep-deploy].

Layer behavior with EP enabled[^ep-deploy]:

| Layer type | Behavior |
| ---------- | -------- |
| Expert (MoE) layers | Sharded across all EP ranks with expert parallelism of size `TP × DP` |
| Attention, `TP = 1` | Replicated across all DP ranks as data parallelism |
| Attention, `TP > 1` | Sharded with tensor parallelism across TP ranks within each DP group |

Example: `TP=2, DP=4` on 8 GPUs gives an EP group of size 8 for experts and TP=2 within each of 4 DP groups for attention[^ep-deploy].

Without `--enable-expert-parallel`, MoE layers would instead use tensor parallelism forming a TP group of size `TP × DP`, as for dense models[^ep-deploy].

Example single-node launch for `DeepSeek-V3-0324` with TP=1, DP=8, EP=8 on an 8-GPU H200/H20 node[^ep-deploy]:

```bash
vllm serve deepseek-ai/DeepSeek-V3-0324 \
  --tensor-parallel-size 1 \
  --data-parallel-size 8 \
  --enable-expert-parallel
```

## Multi-node deployment

Run one `vllm serve` command per node with a DeepEP backend; the first node handles requests and additional nodes run headless[^ep-deploy].

Example 2-node `DeepSeek-V3-0324` deployment with `deepep_low_latency`, total DP=16 and local DP=8 per node[^ep-deploy]:

```bash
# Node 1 (primary)
vllm serve deepseek-ai/DeepSeek-V3-0324 \
  --all2all-backend deepep_low_latency \
  --tensor-parallel-size 1 \
  --enable-expert-parallel \
  --data-parallel-size 16 \
  --data-parallel-size-local 8 \
  --data-parallel-address 192.168.1.100 \
  --data-parallel-rpc-port 13345 \
  --api-server-count=8

# Node 2 (secondary, worker only)
vllm serve deepseek-ai/DeepSeek-V3-0324 \
  --all2all-backend deepep_low_latency \
  --tensor-parallel-size 1 \
  --enable-expert-parallel \
  --data-parallel-size 16 \
  --data-parallel-size-local 8 \
  --data-parallel-start-rank 8 \
  --data-parallel-address 192.168.1.100 \
  --data-parallel-rpc-port 13345 \
  --headless
```

Key rules[^ep-deploy]:

- Secondary nodes use `--headless`; all client requests go to the primary.
- `--data-parallel-start-rank` equals the cumulative local DP size of previous nodes.
- Scale `--api-server-count` on the primary toward the local rank count for higher load.
- On InfiniBand clusters set `GLOO_SOCKET_IFNAME=eth0` so torch distributed discovery uses Ethernet and avoids initialization hangs.

## Expert Parallel Load Balancer (EPLB)

MoE training usually balances tokens across experts, but serving traffic can skew heavily; EPLB periodically redistributes expert mappings across EP ranks from per-forward-pass load statistics[^ep-deploy].

Enable with `--enable-eplb`; configure with `--eplb-config` JSON or dotted `--eplb-config.<key>` arguments[^ep-deploy]:

| Parameter | Description | Default |
| --------- | ----------- | ------- |
| `window_size` | Engine steps tracked for rebalancing decisions | 1000 |
| `step_interval` | Rebalance every N engine steps | 3000 |
| `log_balancedness` | Log avg-tokens-per-expert ÷ max-tokens-per-expert | `false` |
| `num_redundant_experts` | Extra global experts per EP rank beyond equal distribution | `0` |
| `use_async` | Non-blocking EPLB for reduced latency overhead | `true` |
| `policy` | Load-balancing policy type | `"default"` |
| `communicator` | Weight-transfer backend: `"torch_nccl"`, `"torch_gloo"`, `"pynccl"`, `"nixl"`, or `null` (auto) | `null` |

Example[^ep-deploy]:

```bash
vllm serve Qwen/Qwen3-30B-A3B \
  --enable-eplb \
  --eplb-config '{"window_size":1000,"step_interval":3000,"num_redundant_experts":2,"log_balancedness":true}'
```

Distribution and cost[^ep-deploy]:

- Default per rank: `NUM_TOTAL_EXPERTS ÷ NUM_EP_RANKS`; with redundancy: `(NUM_TOTAL_EXPERTS + NUM_REDUNDANT_EXPERTS) ÷ NUM_EP_RANKS`.
- Redundant experts consume GPU memory: `NUM_MOE_LAYERS * BYTES_PER_EXPERT * (NUM_TOTAL_EXPERTS + NUM_REDUNDANT_EXPERTS) ÷ NUM_EP_RANKS`; about `2.4 GB` for one redundant expert per EP rank on DeepSeekV3.
- EPLB may therefore not suit memory-constrained deployments or tight KV-cache budgets.
- Add the same EPLB flags on every node multi-node; for large-scale use the source recommends `--eplb-config '{"num_redundant_experts":32}'` so popular experts stay available.

## Advanced configuration

- DeepEP `high_throughput` and `low_latency` kernels target disaggregated serving and may perform poorly on mixed workloads[^ep-deploy].
- Use `--enable-dbo` to overlap all-to-all communication with compute; async scheduling via `--async-scheduling` is experimental[^ep-deploy].
- For balanced-routing benchmarks set `VLLM_MOE_ROUTING_SIMULATION_STRATEGY=uniform_random` and `VLLM_RANDOMIZE_DP_DUMMY_INPUTS=1`[^ep-deploy].

Troubleshooting[^ep-deploy]:

| Symptom | Fix |
| ------- | --- |
| `non-zero status: 7 cannot register cq buf` on InfiniBand/RoCE | Ensure host VM and pods show `ulimit -l` as `unlimited` |
| `init failed for transport: IBGDA`, or `NVSHMEM API called before NVSHMEM initialization has completed` | Run `tools/ep_kernels/configure_system_drivers.sh` on each GPU node and reboot to install InfiniBand GDA kernel modules |
| NVSHMEM peer disconnect | Usually network misconfiguration; on Kubernetes verify `hostNetwork: true` and `securityContext.privileged: true` for InfiniBand access |

## Disaggregated prefill/decode serving

For strict time-to-first-token and inter-token-latency SLAs, run independent prefill and decode instances and transfer KV cache between them[^ep-deploy]:

- Prefill instance uses `deepep_high_throughput`; decode instance uses `deepep_low_latency`.
- Connect instances with NIXL or another KV connector.
- Configure both with e.g. `--kv-transfer-config '{"kv_connector":"NixlConnector","kv_role":"kv_both"}'`, optionally naming NIXL backends such as `UCX` and `GDS` in `kv_connector_extra_config`[^ep-deploy].
- For non-CUDA UCX builds, run the `install_nixl_from_source_ubuntu.py` script[^ep-deploy].
- Client orchestration uses a shared `X-Request-Id`: a prefill-only request with `max_tokens=1` and `do_remote_decode: True` returns `kv_transfer_params`, which the decode request replays with the same request ID; the prompt must exceed the 16-token block size for this flow[^ep-deploy].

Benchmarking aids[^ep-deploy]:

- Profile decode in isolation with `--kv-transfer-config '{"kv_connector":"DecodeBenchConnector","kv_role":"kv_both"}'`, which populates KV cache with random values.
- Save KV cache and capture CUDA graphs for decode only with `--compilation_config '{"cudagraph_mode": "FULL_DECODE_ONLY"}'`.

## Coverage limits

- `../../tools/ep_kernels`, `install_gdrcopy.sh`, `install_nixl_from_source_ubuntu.py`, DeepGEMM install docs, and gdrcopy OS-version links were outside `raw/` and were not inspected beyond the deployment note's summary[^ep-deploy].
- The full Python prefill/decode orchestration script is summarized, not reproduced; exact client fields remain in raw evidence[^ep-deploy].
- Sibling DP mechanics, DBO overlap internals, and modular All2All/experts kernel compatibility are compiled in their own concepts and only summarized here[^ep-deploy].

## Relationships

- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — EP is typically coupled with DP; `EP = TP × DP`, shared multi-node rank/address/port flags, and MoE dummy-forward synchronization come from DP.
- Uses [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — `--all2all-backend` values here select the modular prepare/finalize backends and compatible experts kernels tabulated there.
- Uses [vLLM Dual Batch Overlap (DBO)](vllm-dbo-dual-batch-overlap.md) — `--enable-dbo` overlaps the EP all-to-all communication configured here with compute in DP+EP deployments.
- Uses [vLLM NIXL Push-Mode KV Transfer](vllm-nixl-kv-push-connector.md) — push-based NIXL KV transfer is one connector option for the disaggregated prefill/decode topology here.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — `deepep_low_latency` relies on CUDA-graph support and decode-only graph capture is recommended for disaggregated decode benchmarking.

[^ep-deploy]: Expert Parallel Deployment — `../raw/vllm/serving/expert_parallel_deployment.md`.
