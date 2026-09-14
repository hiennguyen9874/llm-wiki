---
type: Concept
title: vLLM Data Parallel Deployment
description: Replicated-weight data-parallel serving with internal, hybrid, and external load-balancing modes and MoE DP+EP coordination.
tags: [vllm, data-parallel, deployment, moe, load-balancing]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:58:20Z }
sources:
  - id: dp-deploy
    resource: ../raw/vllm/serving/data_parallel_deployment.md
    title: Data Parallel Deployment
---

vLLM data parallelism replicates model weights across separate ranks that process independent request batches, with single-endpoint internal, per-node hybrid, and per-rank external load-balancing modes for online serving[^dp-deploy].

## Core model

- Works with both dense and MoE models[^dp-deploy].
- Each DP rank runs as a separate engine-core process communicating with front-end API-server process(es) via ZMQ sockets[^dp-deploy].
- Data-parallel attention composes with tensor parallelism: each DP engine owns per-GPU worker processes equal to the configured TP size[^dp-deploy].
- Each DP engine has an independent KV cache; intelligent routing maximizes prefix-caching benefit[^dp-deploy].
- Load balancing should account for each engine's scheduled and waiting (queued) requests and KV-cache state[^dp-deploy].

## MoE coordination

- For MoE models such as DeepSeek with MLA, a useful pattern is data parallel for attention layers combined with expert or tensor parallel (EP or TP) for expert layers[^dp-deploy].
- In that pattern DP ranks are not fully independent: forward passes must align and expert layers across all ranks synchronize on every forward pass, even when fewer requests than DP ranks are active[^dp-deploy].
- When any rank has in-flight requests, idle ranks run empty "dummy" forward passes; a separate DP coordinator process communicates with all ranks, plus a collective every N steps to detect global idleness and pause ranks[^dp-deploy].
- By default expert layers form a tensor-parallel group of size `DP x TP`; pass `--enable-expert-parallel` (on all nodes multi-node) to use expert parallelism instead[^dp-deploy].
- With TP+DP, the expert group spans `DP x TP` whether TP or EP is selected[^dp-deploy].

## Admission control and sizing

- `--max-num-seqs` applies per DP rank[^dp-deploy].
- `--max-num-queued-reqs` and `--max-num-queued-tokens` apply to the whole server: each API server counts in-flight requests and prefill backlog across all DP ranks it routes to[^dp-deploy].
- Example: with `--data-parallel-size 4 --max-num-seqs 256 --max-num-queued-reqs 256`, new requests are rejected once 256 are in flight in total even though ranks could jointly run 1024[^dp-deploy].
- Sizing rule: set the queue cap to roughly `data-parallel-size * max-num-seqs` plus desired queue depth to keep ranks saturated[^dp-deploy].

## Internal load balancing

- Self-contained deployment exposing a single API endpoint; configure with e.g. `--data-parallel-size 4` (4 GPUs), combinable with `--tensor-parallel-size 2` (8 GPUs total)[^dp-deploy].
- Current internal balancing lives in the API-server process(es) and uses running and waiting queues per engine; KV-cache-aware logic is future work[^dp-deploy].
- At large DP sizes the API server can bottleneck; scale it on the head node with `--api-server-count` (e.g. 4) while keeping a single HTTP endpoint/port[^dp-deploy].
- Single-node example: `vllm serve $MODEL --data-parallel-size 4 --tensor-parallel-size 2` runs DP=4, TP=2 on one 8-GPU node[^dp-deploy].
- Multi-node uses one `vllm serve` per node with `--data-parallel-size-local`, `--data-parallel-start-rank`, `--data-parallel-address`, and `--data-parallel-rpc-port`; API servers run on one node only and need not be co-located with DP ranks[^dp-deploy].
- Rank-split example: ranks 0-1 on head node (`10.99.48.128`), ranks 2-3 headless on node 1; API-only-head variant uses `--data-parallel-size-local 0` on node 0 and `--headless ... --data-parallel-size-local 4` on node 1[^dp-deploy].
- Ray backend (`--data-parallel-backend=ray`): single launch command starts all local and remote ranks; no `--data-parallel-address` or `--data-parallel-rpc-port` needed; set `VLLM_RAY_DP_PACK_STRATEGY="span"` when one replica spans nodes (then `--data-parallel-size-local` is auto-determined); remote ranks allocate from Ray-cluster node resources[^dp-deploy].
- Offline DP+EP is also supported via the `LLM` class; the cited `examples/features/data_parallel/data_parallel_offline.py` example was not present in `raw/` and was not inspected[^dp-deploy].

## Hybrid load balancing

- Middle ground: each node runs its own API server(s) queuing only to co-located DP engines, with an upstream balancer (ingress/traffic router) spreading user requests across per-node endpoints[^dp-deploy].
- Enable with `--data-parallel-hybrid-lb` while launching every node with the global data-parallel size[^dp-deploy].
- Requires `--data-parallel-size-local` and `--data-parallel-start-rank` so each node knows its ranks; incompatible with `--headless` since every node exposes an API endpoint[^dp-deploy].
- Scale `--api-server-count` per node by local rank count; keeping scheduling local reduces cross-node traffic and avoids single-node bottlenecks at larger DP sizes[^dp-deploy].

## External load balancing

- Treats each DP rank as a separate deployment with its own endpoint behind an external router using real-time per-server telemetry; preferred for larger-scale deployments[^dp-deploy].
- For non-MoE models ranks are fully independent: launch independent instances with no `--data-parallel-*` arguments; external DP CLI options are only for MoE[^dp-deploy].
- MoE DP+EP topology: pass `--data-parallel-size` plus `--data-parallel-rank` per launch; co-located ranks share the default RPC port but need distinct `--port` values (e.g. `CUDA_VISIBLE_DEVICES=0 ... --data-parallel-rank 0 --port 8000`); multi-node also sets `--data-parallel-address` and `--data-parallel-rpc-port` with rank 0's address[^dp-deploy].
- The coordinator process runs co-located with the DP rank 0 engine in this mode[^dp-deploy].
- Each dotted box in the source's external-LB diagram is a separate `vllm serve` launch, e.g. separate Kubernetes pods[^dp-deploy].

## Coverage limits

- Referenced diagrams `../assets/deployment/dp_internal_lb.png` and `dp_external_lb.png` were absent from `raw/` and were not inspected[^dp-deploy].
- Expert-parallel detail is now compiled in [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md); the DP+EP summary above remains the DP-side view[^dp-deploy].

## Relationships

- Uses [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md) — EP+DP sharding (`EP = TP × DP`), `--enable-expert-parallel` switching, and EPLB/disaggregated options complementing the DP coordination above.
- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — DP rank count sets engine-core count, `--api-server-count` scales front ends, and the DP coordinator handles cross-rank synchronization.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — per-rank independent KV caches make prefix-aware routing valuable.
- Uses [vLLM Dual Batch Overlap (DBO)](vllm-dbo-dual-batch-overlap.md) — DBO builds on DP+EP with `--data-parallel-size N` plus `--enable-expert-parallel`.
- Uses [vLLM Context Parallel Deployment](vllm-context-parallel-deployment.md) — sibling parallelism strategy for long-context prefill/decode versus DP request-level replication.

[^dp-deploy]: Data Parallel Deployment — `../raw/vllm/serving/data_parallel_deployment.md`.
