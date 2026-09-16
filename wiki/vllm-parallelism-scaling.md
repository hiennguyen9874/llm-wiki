---
type: Concept
title: vLLM Tensor and Pipeline Parallel Scaling
description: Single-replica tensor/pipeline strategy selection, multi-node Ray and multiprocessing runtimes, and InfiniBand/GPUDirect networking for vLLM scaling.
tags: [vllm, tensor-parallel, pipeline-parallel, deployment, multi-node]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: para-scale
    resource: ../raw/vllm/serving/parallelism_scaling.md
    title: Parallelism and Scaling
---

vLLM scales a single-model replica with tensor parallelism inside a node and tensor plus pipeline parallelism across nodes, using Ray or multiprocessing as the distributed runtime and InfiniBand with GPUDirect RDMA for efficient cross-node tensor-parallel communication[^para-scale].

## Single-replica strategy selection

Choose by whether the model fits[^para-scale]:

- Single GPU, no distribution: model fits on one GPU.
- Single-node multi-GPU tensor parallel: model exceeds one GPU but fits on one node; set `tensor_parallel_size` to the GPU count, e.g. `tensor_parallel_size=4` on a 4-GPU node.
- Multi-node tensor plus pipeline parallel: model exceeds one node; set `tensor_parallel_size` to GPUs per node and `pipeline_parallel_size` to node count, e.g. `tensor_parallel_size=8` and `pipeline_parallel_size=2` for 2 nodes with 8 GPUs each.

General rule: add GPUs and nodes until GPU memory holds the model, keeping TP at GPUs-per-node and PP at node count[^para-scale].

## KV-cache capacity check

After provisioning, run `vllm` and inspect startup logs such as[^para-scale]:

```text
INFO 07-23 13:56:04 [kv_cache_utils.py:775] GPU KV cache size: 643,232 tokens
INFO 07-23 13:56:04 [kv_cache_utils.py:779] Maximum concurrency for 40,960 tokens per request: 15.70x
```

- `GPU KV cache size` is total tokens storable in GPU KV cache at once.
- `Maximum concurrency` estimates concurrently servable requests for the stated tokens-per-request, taken from `ModelConfig.max_model_len` (40,960 in the example).
- If either is below throughput requirements, add GPUs or nodes.

## Edge case: uneven GPU splits

If the model fits on one node but the GPU count does not evenly divide the model, use pipeline parallelism because it splits along layers and supports uneven splits: set `tensor_parallel_size=1` and `pipeline_parallel_size` to the GPU count[^para-scale].

If node GPUs lack NVLINK interconnect (example given: L40S), prefer pipeline parallelism over tensor parallelism for higher throughput and lower communication overhead[^para-scale].

## MoE pointer

For Mixture of Experts models, vLLM supports combining data-parallel attention with expert- or tensor-parallel MoE layers; the source defers detail to Data Parallel Deployment[^para-scale].

## Single-node deployment

vLLM implements distributed tensor- and pipeline-parallel inference and serving, including Megatron-LM's tensor-parallel algorithm[^para-scale].

- Offline multi-GPU: set `tensor_parallel_size` in the `LLM` class, e.g. `LLM("facebook/opt-13b", tensor_parallel_size=4)`[^para-scale].
- Online multi-GPU: pass `--tensor-parallel-size`, e.g. `vllm serve facebook/opt-13b --tensor-parallel-size 4`[^para-scale].
- Add pipeline parallelism with `--pipeline-parallel-size`, e.g. 8 GPUs as `--tensor-parallel-size 4 --pipeline-parallel-size 2`[^para-scale].

## Distributed executor backends

Default runtimes are native Python `multiprocessing` for single-node inference and Ray for multi-node inference[^para-scale].

Override with `distributed_executor_backend` in the `LLM` class or `--distributed-executor-backend` on the server: `mp` for multiprocessing, `ray` for Ray[^para-scale].

## Multi-node prerequisites

Every node must provide an identical execution environment, including model path and Python packages; container images are recommended to keep environments consistent and hide host heterogeneity[^para-scale].

Ray is an optional dependency installed explicitly, e.g. `pip install "ray[cgraph]"`[^para-scale].

## Ray-cluster setup

Ray manages distributed task execution and placement for multi-node vLLM; Ray also offers higher-level offline batch and online serving APIs with fault tolerance, scaling, and observability that can use vLLM as the engine[^para-scale].

Container setup uses the helper script `examples/ray_serving/run_cluster.sh` (not present in `raw/` and not inspected)[^para-scale]:

- Head node: `bash run_cluster.sh vllm/vllm-openai <HEAD_NODE_IP> --head /path/to/huggingface/home -e VLLM_HOST_IP=<HEAD_NODE_IP>`.
- Each worker: same script with `--worker` and per-worker `-e VLLM_HOST_IP=<WORKER_NODE_IP>`.
- By default the script runs Docker without admin privileges, blocking GPU performance counters during profiling/tracing; add `--cap-add=CAP_SYS_ADMIN` to enable them.
- Keep the launch shells open; closing one terminates the cluster.
- All nodes must reach each other by IP; set `VLLM_HOST_IP` to a private-network address because this traffic is unencrypted and endpoints exchange data in a format exploitable for arbitrary code execution if an adversary gains network access.
- Verify from inside a container with `ray status` and `ray list nodes`.
- KubeRay is named as an alternative cluster-setup path.

Run Ray-container commands inside the containers (e.g. via `docker exec -it <container_name> /bin/bash`), not on the host[^para-scale].

## Running vLLM on a Ray cluster

Once Ray is running, all cluster resources are visible to vLLM, so one `vllm` command on one node suffices[^para-scale].

Common practice is TP = GPUs per node and PP = node count; e.g. 16 GPUs across 2 nodes with 8 GPUs each[^para-scale]:

```bash
vllm serve /path/to/the/model/in/the/container \
    --tensor-parallel-size 8 \
    --pipeline-parallel-size 2 \
    --distributed-executor-backend ray
```

Alternatively set `tensor_parallel_size` to the cluster-wide GPU total[^para-scale]:

```bash
vllm serve /path/to/the/model/in/the/container \
     --tensor-parallel-size 16 \
     --distributed-executor-backend ray
```

## Multiprocessing multi-node deployment

Multi-node deployments can also use `multiprocessing` instead of Ray. Example for 2 nodes with 8 GPUs each, `tp_size=8`, `pp_size=2`[^para-scale]:

```bash
# Head node (node-rank 0)
vllm serve /path/to/the/model/in/the/container \
  --tensor-parallel-size 8 --pipeline-parallel-size 2 \
  --nnodes 2 --node-rank 0 \
  --master-addr <HEAD_NODE_IP>

# Worker node (node-rank 1)
vllm serve /path/to/the/model/in/the/container \
  --tensor-parallel-size 8 --pipeline-parallel-size 2 \
  --nnodes 2 --node-rank 1 \
  --master-addr <HEAD_NODE_IP> --headless
```

## Network optimization

Efficient tensor parallelism needs fast internode communication, preferably InfiniBand. For the container helper script, append arguments such as `--privileged -e NCCL_IB_HCA=mlx5`; consult the system administrator for required flags[^para-scale].

### GPUDirect RDMA

GPUDirect RDMA lets network adapters access GPU memory directly, bypassing CPU and system memory to reduce latency and CPU overhead for large cross-node transfers[^para-scale].

Required configuration[^para-scale]:

- `IPC_LOCK` capability to lock memory pages and prevent swapping.
- Shared memory via `/dev/shm` for interprocess communication.

Docker example[^para-scale]:

```bash
docker run --gpus all \
    --ipc=host \
    --shm-size=16G \
    -v /dev/shm:/dev/shm \
    vllm/vllm-openai
```

Kubernetes pod-spec pattern: add `IPC_LOCK` under `securityContext.capabilities`, mount `/dev/shm` from an in-memory `emptyDir` volume named `dshm`, and request/limit `nvidia.com/gpu: 8`[^para-scale].

Confirm operation with detailed NCCL logs (`NCCL_DEBUG=TRACE vllm serve ...`)[^para-scale]:

- `[send] via NET/IB/GDRDMA` means NCCL uses InfiniBand with GPUDirect RDMA (efficient).
- `[send] via NET/Socket` means NCCL fell back to raw TCP sockets (inefficient for cross-node tensor parallelism).

## Operational tips

- Consumer-GPU P2P unlock: on RTX 3090-class rigs without factory P2P, a community driver patch plus vLLM check override and fused-MoE tuning is reported to restore direct GPU-to-GPU transfer; see [Consumer-GPU P2P Unlock and vLLM Tuning](vllm-consumer-gpu-p2p-unlock.md) for procedure, IOMMU tradeoff, and single-rig limits.

- Pre-download Hugging Face models: download on every node to the same path or place the model on a distributed filesystem accessible to all nodes, then pass the path instead of the repository ID; otherwise supply a token via `-e HF_TOKEN=<TOKEN>` to the cluster script[^para-scale].
- For distributed-debugging detail, the source points to `distributed_troubleshooting.md`, which was absent from `raw/` and was not inspected[^para-scale].

## Coverage limits

- `examples/ray_serving/run_cluster.sh`, `distributed_troubleshooting.md`, the Megatron-LM paper, Ray/KubeRay docs, and InfiniBand hardware flags were not inspected beyond this source's summary[^para-scale].
- `../assets/deployment/dp_internal_lb.png`-style diagrams are not referenced by this source; no embedded figures required inspection here[^para-scale].

## Relationships

- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — data-parallel attention combined with expert/tensor-parallel MoE layers complements the single-replica TP/PP strategy above.
- Uses [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md) — MoE expert-parallel sharding and DeepEP backends extend TP/PP for expert layers.
- Uses [vLLM Context Parallel Deployment](vllm-context-parallel-deployment.md) — sibling parallelism strategy for long-context prefill/decode, versus TP/PP model-weight sharding here.
- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — engine-core, API-server, and worker process layout underlies the Ray versus multiprocessing executor choice.
- Uses [vLLM Python Multiprocessing Method Selection](vllm-python-multiprocessing.md) — fork/spawn selection and worker constraints apply to the `mp` distributed-executor backend.
- Related to [Consumer-GPU P2P Unlock and vLLM Tuning](vllm-consumer-gpu-p2p-unlock.md) — community BAR1 patch plus vLLM override that restores P2P transfer on consumer GPUs lacking factory support.

[^para-scale]: Parallelism and Scaling — `../raw/vllm/serving/parallelism_scaling.md`.
