---
type: Concept
title: SGLang P2P Weight Transfer for RL
description: RDMA peer-to-peer trainer-to-inference weight sync via CPU engine replicas and Mooncake TransferEngine for seconds-scale 1T-parameter RL updates.
tags: [sglang, rl, weight-update, p2p, rdma, mooncake, miles]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:37:22Z }
sources:
  - id: p2p-update
    resource: ../raw/2026-04-29-p2p-update/index.md
    title: "Updating 1T parameters in seconds — P2P weight transfer in Large Scale Distributed RL"
---

SGLang with Miles adds an RDMA-based peer-to-peer weight-update path for large distributed RL that supplements NCCL broadcast, using a source-side CPU engine replica plus Mooncake TransferEngine zero-copy transfers to cut 1T-parameter Kimi-K2 FP8 sync from ~53s to ~7.2s at the cost of one ~32 GB CPU replica per training rank[^p2p-update].

## Why NCCL broadcast bottlenecks RL

In large distributed RL, trainer-to-inference weight transfer is critical-path: both trainer and inference stall with resources idle while weights move, across multiple hosts and racks fighting for limited bandwidth[^p2p-update].

NCCL is the default for symmetric training via auto-detected ring/tree `all-gather` and `broadcast`, but it requires lock-step collective semantics with matching shapes on every rank, so one slow receiver hangs the group[^p2p-update]. Open-source RL stacks on miles/slime/verl broadcast full weights from a single source rank via `update_weights_from_distributed`, which becomes the bottleneck[^p2p-update].

RDMA instead allows independent concurrent endpoint pairs with kernel bypass, zero-copy DMA between registered memory regions, and one-sided READ/WRITE without remote CPU participation[^p2p-update].

Existing NCCL broadcast challenges called out[^p2p-update]:

- **Redundancy:** identical data sent multiple times across the network.
- **Inactivity:** most trainer ranks idle while only a few broadcast.
- **Rigidity:** NCCL group is fixed once defined; dynamically adding engine instances requires group rebuild.

Strategy comparison for ~1 TB 1T FP8 Kimi-K2 transfer, excluding colocated-only `update_weights_from_tensor`[^p2p-update]:

| Strategy | Efficiency | Open source | Dynamic | Training support | Complexity |
| --- | --- | --- | --- | --- | --- |
| Disk I/O (`update_weights_from_disk`) | ~several minutes | Yes | Yes | Megatron, FSDP | Simple, single API |
| NCCL broadcast (`update_weights_from_distributed`) | ~50s | Yes | No, rebuild needed | Megatron, FSDP | Simple, single API |
| Perplexity fabric-lib P2P | ~1.2s | No, RDMA lib only | Yes | FSDP2 DTensor only | Very complex, write-only |
| **RDMA P2P (this design)** | **~7s** | **Yes** | **Yes** | **Megatron, FSDP** | **Complex, multiple APIs** |

## Design

Shift from centralized broadcast to distributed P2P mapping over RDMA while reusing existing model and parallelism interfaces[^p2p-update]:

- **Source-side engine replicas:** model replicas in training-rank CPU memory avoid wasting GPU VRAM and avoid repetitive registration/deregistration.
- **P2P mapping heuristics:** every trainer rank participates by sending its specific shard directly to its target(s), instead of a few ranks broadcasting everything.
- **Zero-copy transfer:** TransferEngine memory is registered once at startup, bypassing CUDA IPC handle serialization and kernel-side copies.

Reused infrastructure[^p2p-update]:

- [TransferEngine](https://kvcache-ai.github.io/Mooncake/python-api-reference/transfer-engine.html) as transport for CPU-to-GPU RDMA zero-copy.
- Weight-registration info reuse through R-Fork remote-instance weight loading.
- Standard `load_weight(huggingface_tensor)` supporting quantization and sharding.

New SGLang-side interfaces on the `sglang-miles` branch[^p2p-update]:

- Expose model parallelism for replica creation: PR #20907.
- Map Hugging Face tensor to SGLang tensor shard: PR #17326.
- Post-process engine call for GPU-local post-quantization: similar to PR #15245.

### Initialization

| Step | Description |
| --- | --- |
| `get_remote_instance_transfer_engine_info` | Get weight registration info via SGLang API |
| `get_parallelism_info` | Get TP/EP and other parallelism definition |
| `build_transfer_plan` | Construct training-to-inference rank mapping |
| `create_engine_replica` | Create CPU engine replica |

### Per-update flow

| Step | Description |
| --- | --- |
| `pause_and_register_engine` | Pause engine and register replica weights, once |
| `update_weight` | Bucketed update, non-expert then expert weights |
| `post_process_weights` | GPU-local post-processing such as quantization |
| `update_weight_version` | Update weight version |
| `continue_generation` | Resume rollout |

Caller flow preserves the pause-update-continue requirement documented in [SGLang for RL Systems](sglang-for-rl.md)[^p2p-update].

## Memory versus network trade-off

Notation: M source training ranks, N target SGLang ranks, source `pp_size` pp, target `ep_size` ep, P parameters per engine rank, K bucketed all-gather buffer, expert-weights-only assumption[^p2p-update]:

|  | Participating source ranks | Params received per inference rank | Extra buffer on source | Extra buffer on target |
| --- | --- | --- | --- | --- |
| NCCL broadcast | pp | ep * P | K | K |
| RDMA P2P | M | P | K\* + P | 0 |

P2P sends only necessary tensors with all sources participating, trading extra source-CPU allocation P for less network traffic and no receiver-side allocation; K\* is slightly larger than K because multi-to-one mappings such as `q_proj,k_proj,v_proj -> qkv_proj` need local caching before the full SGLang tensor is ready[^p2p-update]. Flow diagram inspected from `assets/blog-1.png`: NCCL left shows per-PP gathered tensor broadcast from head rank to every engine rank; P2P right shows all-gather followed by load into per-rank CPU replica shards sent as tensor shards to mapped SGLang ranks[^p2p-update].

## Performance results

Profiled on H100 8-GPU hosts with InfiniBand, timed between engine-pause return and `continue_generation`[^p2p-update]:

| Model | Total params | Train config | Inference config | NCCL (ms) | RDMA (ms) | Speedup |
| --- | --- | --- | --- | --- | --- | --- |
| GLM-Z1-9B-0414 | 9B | TP=2,PP=1,CP=2,EP=1,1 node | TP=4,EP=1,1 node | 694.6 | 707.1 | 0.98x |
| Moonlight-16B-A3B | 16B(3B) | TP=2,PP=1,CP=1,EP=8,1 node | TP=8,EP=8,1 node | 1482.0 | 1073.3 | 1.38x |
| GLM-4.7-9B-Flash | 30B(3B) | TP=4,PP=1,CP=1,EP=8,1 node | TP=4,EP=4,1 node | 2508.6 | 4229.0 | 0.59x |
| Qwen3-30B-A3B | 30B(3B) | TP=4,PP=1,CP=1,EP=8,2 nodes | TP=8,EP=8,2 nodes | 2670.0 | 2160.2 | 1.24x |
| GLM-4.5-Air | 106B(12B) | TP=1,PP=4,CP=1,EP=8,4 nodes | TP=8,EP=8,4 nodes | 5001.1 | 2637.2 | 1.90x |
| Qwen3-235B-A22B | 235B(22B) | TP=4,PP=4,CP=2,EP=16,8 nodes | TP=32,EP=32,8 nodes | 10753.6 | 3162.0 | 3.40x |
| GLM-5 | 744B(40B) | TP=4,PP=8,CP=2,EP=16,16 nodes | TP=64,EP=64,16 nodes | 58301.5 | 8479.7 | 6.88x |
| Kimi-K2-FP8, 64-block-quant | 1T(64B) | TP=8,PP=8,CP=4,EP=32,32 nodes | TP=32,EP=32,32 nodes | 53279.1 | 7227.3 | 7.37x |

Gains concentrate in large MoE architectures with high rollout expert parallelism; at small node/EP counts local CPU-replica load cost can outweigh P2P benefit, as in the GLM-4.7-Flash 0.59x case, while P2P scales better as node count grows[^p2p-update].

## Usage

In Miles enable P2P with[^p2p-update]:

```text
--update-weight-transfer-mode p2p
```

Engines register weight memories via `--sglang-remote-instance-weight-loader-start-seed-via-transfer-engine`, selecting P2P flow over NCCL broadcast; requires Miles-dependent `sglang-miles` SGLang branch with experimental P2P support[^p2p-update]. Run instructions and supported-model list are linked in the source as [miles P2P weight-transfer docs](https://github.com/radixark/miles/blob/main/docs/en/advanced/p2p-weight-transfer.md)[^p2p-update].

## Engineering details

**CPU over GPU replica.** Initial GPU-side replica wasted training VRAM and forced pipelined register/transfer/deregister work; registration dominated transfer time at tens of seconds for the full replica, so moving the replica to CPU resolved it[^p2p-update].

**Memory reuse.** Naively replicating every target rank on every source rank OOMs CPU because all SGLang ranks are homogeneous; final design reuses the same underlying physical memory and orchestrates transfers to different engine shards sequentially[^p2p-update].

**P2P transfer plan.** Round-robin assignment with load balancing to minimize RDMA sessions per source: first ranks get 1:1 mapping, remaining targets distribute evenly, and identical engine ranks reuse existing sources[^p2p-update]. Example with training `pp=4`, 32 training ranks, 2 SGLang instances of 16 ranks: for `pp_rank=0`, map 8 training ranks to 32 targets via `src 0 -> tgt 0 ... src 7 -> tgt 7`, repeat for `tgt 8-15`, then attach identical ranks `tgt 16,24` to the same sources, yielding e.g. `src 0 -> [tgt [0,16], tgt [8,24]]`[^p2p-update].

**Tensor identification.** Bucketed transfer needs to know when a SGLang tensor is ready after each `model.load_weight()` via HF-to-SGLang mapping[^p2p-update]:

```text
sglang_name, shard_id, num_shards, expert_id, num_local_experts = parameter_mapper.map(hf_tensor)
```

Example: `model.layers.0.mlp.experts.3.down_proj.weight -> model.layers.0.mlp.experts.w2_weight, w2, 2, 3, 5`; a SGLang tensor sends only after all `num_shards` for all `num_local_experts` are updated[^p2p-update].

**Shared-replica flow.** Threadpool task pool plus cache buffer for partially updated tensors; TransferEngine releases GIL for multithread parallelism; critical-path transfers wait inline while the last engine-rank update goes to the pool[^p2p-update]. Diagram inspected from `assets/blog-2.png`: all-gathered `v_proj` joins buffered `q_proj/k_proj` as one HF tensor input, readiness gates `update 1/send 1` to engine rank 0 on the critical path and `update 2/send 2` to engine rank 1 off the critical path using the same underlying replica[^p2p-update]. One bucket may lack all shards for a SGLang tensor, so shared-replica buffering exceeds 1; worst case is `num_shard` times the base buffer, but `named_parameters` ordering keeps related tensors together so extra need is small in practice[^p2p-update].

**Quantization and post-load.** Not all needed tensors appear in `model.named_parameters()`; e.g. DeepSeekV3-lineage MLA local `w_kc`/`w_vc` are generated in `post_weight_load()` after full load, and much custom quantization/hardware logic cannot run on the CPU replica and must run GPU-local via post-process calls[^p2p-update].

## Future plans

- Official GB200 support, SGLang-side pipeline parallel, more quantizations, and merging SGLang-side changes to main[^p2p-update].
- Huge-page GPU allocation in TransferEngine to cut registration/deregistration cost and enable in-place GPU replica creation and registration at transfer time, instead of permanently allocating CPU memory[^p2p-update].

## Relationships

- Uses [SGLang for RL Systems](sglang-for-rl.md) — P2P supplements the NCCL `update_weights_from_distributed` path and reuses the pause-update-continue generation discipline.
- Uses [SGLang R-Fork](sglang-rfork.md) — reuses R-Fork remote-instance weight registration info and TransferEngine seed-service mechanism for the P2P transport.
- Related to [SGLang Checkpoint Engine Integration](sglang-checkpoint-engine.md) — alternative parallel weight-loading path for boot-up via checkpoint-engine workers, distinct from this trainer-to-rollout RL update path.
- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — Miles Megatron RL pipeline that exposes `--update-weight-transfer-mode p2p` for this flow.

## Coverage limits

- Both local attachments `assets/blog-1.png` and `assets/blog-2.png` were inspected as rendered images; numeric benchmark claims come from source prose/tables without independent re-measurement[^p2p-update].
- Linked Miles P2P docs, SGLang PRs #20907/#17326/#15245, TransferEngine API reference, and R-Fork blog were not inspected beyond this source[^p2p-update].
- Kimi-K2 result uses adjusted `[64,64]` block-quant FP8 to fit the profiling configuration[^p2p-update].

[^p2p-update]: Updating 1T parameters in seconds — P2P weight transfer in Large Scale Distributed RL — `../raw/2026-04-29-p2p-update/index.md`, covering RDMA P2P motivation versus NCCL broadcast, CPU-replica plus TransferEngine design, init/update APIs, memory/network trade-off, 9B–1T benchmarks including Kimi-K2 53s→7.2s, Miles `--update-weight-transfer-mode p2p` usage, and replica/mapping/buffering/quantization appendix.
