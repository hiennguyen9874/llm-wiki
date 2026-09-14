---
type: Concept
title: SGLang Expert Parallelism
description: Expert-parallel MoE serving with selectable all-to-all and grouped-GEMM backends, TBO/SBO overlap, EPLB rebalancing, and Ascend NPU guidance.
tags: [sglang, expert-parallel, moe, deepep, load-balancing]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:56:45Z }
sources:
  - id: sgl-ep
    resource: ../raw/sglang/advanced_features/expert_parallelism.mdx
    title: Expert Parallelism
---

SGLang expert parallelism distributes MoE expert weights across devices to relieve memory bottlenecks in large MoE models, using all-to-all token dispatch plus grouped GEMMs with modular backend selection and communication-computation overlap[^sgl-ep].

## Backend selection

Select separately with `--moe-a2a-backend` for all-to-all communication and `--moe-runner-backend` for MoE computation[^sgl-ep].

Example with DeepEP dispatch and DeepGEMM compute for DeepSeek-V3[^sgl-ep]:

```bash
python -m sglang.launch_server --model-path deepseek-ai/DeepSeek-V3 \
  --moe-a2a-backend deepep --moe-runner-backend deep_gemm --tp 8 --ep 8
```

## All-to-all backends

| Backend | Description | Use cases |
|---|---|---|
| `none` (default) | Disables all-to-all; uses All-Reduce or All-Gather for token dispatch | Hybrid EP and TP setups |
| `deepep` | DeepEP token shuffling for MoE | Large-scale EP deployments |
| `mooncake` | DeepEP extension for elastic inference with RDMA transfers | Elastic EP serving |
| `flashinfer` | FlashInfer all-to-all | Large-scale EP deployments |
| `ascend_fuseep` | Ascend NPU native fused all-to-all | Ascend NPU deployments |

DeepEP and Mooncake dispatch modes[^sgl-ep]:

- `normal`: optimized for prefill throughput.
- `low_latency`: optimized for decode latency with CUDA Graph compatibility.
- Recommended: `--deepep-mode auto` for automatic runtime switching; explicit `normal` or `low_latency` is mainly for debugging.

Constraint: DeepEP and Mooncake currently require `ep_size = tp_size`; hybrid `ep_size < tp_size` supports only the `none` All-Reduce/All-Gather path[^sgl-ep].

## MoE runner backends

`auto` (default) picks the runner from model architecture, NVIDIA architecture such as Ampere/Hopper/Blackwell, quantization such as FP8/FP4, and runtime conditions[^sgl-ep].

| Backend | Description | Use cases |
|---|---|---|
| `triton` | Triton grouped GEMMs; tuned configs recommended for performance | Custom kernels, extensibility, Torch compilation |
| `deep_gemm` | DeepGEMM MoE GEMMs, contiguous layouts for prefill and masked layouts for decode, often JIT-compiled | Large-scale EP with FP8 block-wise quantization |
| `cutlass` | CUTLASS GEMMs | NVIDIA architectures with CUTLASS support |
| `flashinfer_trtllm` | FlashInfer plus TensorRT-LLM, with FP4 communication operators | Blackwell with TRT-LLM |
| `flashinfer_cutlass` | FlashInfer plus CUTLASS grouped GEMMs for FP4/FP8 | Blackwell with FP4/FP8 models |
| `flashinfer_mxfp4` | FlashInfer variant for MXFP4 low-precision inference | MXFP4 models |
| `flashinfer_cutedsl` | FlashInfer with custom DSL kernel generation plus ModelOpt FP4 | NVFP4 low-precision models |

## Extensible EP framework

`FusedMoE` is the unified entry point, decoupling one MoE forward pass into dispatch, pre-permute, core runner, post-permute, and combine stages so custom kernels and backends integrate without refactoring core logic[^sgl-ep].

Key components[^sgl-ep]:

- `Dispatcher`: dispatch/combine per backend via `BaseDispatcher` subclasses, e.g. DeepEP.
- `MoeRunner`: grouped-GEMM orchestration via `MoeRunnerCore` implementations, e.g. `TritonRunnerCore`.
- `PermuteMethodPool`: auto-registered layout conversions via `register_pre_permute` and `register_post_permute` for dynamic mode, or `register_fused_func` for static torch.compile-compatible fused operations.
- TopK router: backend-agnostic expert selection with quantization integrated through a standardized `apply()` method.

To add a backend: implement a `BaseDispatcher` subclass for all-to-all, a `MoeRunnerCore` subclass for grouped GEMMs, define dispatcher/runner input/output formats such as `RunnerInput`/`RunnerOutput`, and register fused or pre/post-permute conversions for compatibility; reference implementation is `moe_runner/triton.py`[^sgl-ep].

## Computation-communication overlap

Two-Batch Overlap (TBO) splits requests into micro-batches and interleaves attention with dispatch/combine via execution-graph yield points, without peak-memory spikes; enable with `--enable-two-batch-overlap` for up to ~2x throughput[^sgl-ep].

Single-Batch Overlap (SBO) uses a dispatcher-hook system running before/after `dispatch` and `combine` to overlap work within one batch, e.g. shared-expert compute with DeepEP combine, without modifying core MoE modules; enable with `--enable-single-batch-overlap`[^sgl-ep].

## Workload balancer

SGLang integrates DeepSeek's Expert Parallelism Load Balancer (EPLB) to counter serving-time routing imbalance: it analyzes expert activation statistics and rearranges or replicates experts to reduce GPU utilization variance and idle cycles[^sgl-ep].

Enable with `--enable-eplb`; for best results use larger batch sizes to stabilize activation statistics and configure periodic rebalancing, e.g. every 1000 requests[^sgl-ep].

## Speculative decoding

For MTP speculative decoding on MoE models, `--speculative-moe-runner-backend` and `--speculative-moe-a2a-backend` override the draft-model MoE behavior and default to the target-model settings, allowing different precisions per model[^sgl-ep].

Example: NVFP4 target with `flashinfer_trtllm` and BF16 draft with Triton[^sgl-ep]:

```text
--moe-runner-backend flashinfer_trtllm \
--speculative-moe-runner-backend triton \
```

## Ascend NPU guidance

- `--moe-a2a-backend` supports only `deepep` and `ascend_fuseep`; `ascend_fuseep` is a large fused operator covering dispatch through combine, used only for decode in PD disaggregation mode[^sgl-ep].
- `--moe-runner-backend` does not need configuration on Ascend[^sgl-ep].
- `--deepep-mode`: use `auto` in PD mixed mode; in PD disaggregation use `normal` for prefill and `low_latency` for decode[^sgl-ep].

DeepEP Ascend supports an ant-moving function that streams long sequences in rounds to bound collective-communication buffers in prefill[^sgl-ep]:

- `DEEPEP_NORMAL_LONG_SEQ_PER_ROUND_TOKENS`: per-round tokens per rank in dispatch, default 8192.
- `DEEPEP_NORMAL_LONG_SEQ_ROUND`: rounds per rank in dispatch, default 1.
- `DEEPEP_NORMAL_COMBINE_ENABLE_LONG_SEQ`: enable in combine, default 0 (disabled).
- Enable both phases when input length exceeds 8192; product of the first two variables is the input sequence length.

Size `HCCL_BUFFSIZE` (MB) as[^sgl-ep]:

```text
# With ant-moving
HCCL_BUFFSIZE >= 2 * (102MB + 4MB + DEEPEP_NORMAL_LONG_SEQ_PER_ROUND_TOKENS * (hidden_size + hidden_size + hidden_size) * topk) + PADDING_BUFFSIZE

# Without ant-moving
HCCL_BUFFSIZE >= 2 * (102MB + 4MB + TOTAL_SEQ_LEN * (hidden_size + hidden_size) * topk) + PADDING_BUFFSIZE
```

Use `hidden_size` from the model config, `topk` selected experts, `TOTAL_SEQ_LEN` input length, and `PADDING_BUFFSIZE >= 20`[^sgl-ep].

## Coverage limits

- Linked MoE refactor roadmap, implementation PR, Triton runner source, large-scale EP blog, EPLB blog/repository, SBO PR, and Triton tuning README were not inspected beyond this source's summary[^sgl-ep].
- Quantitative TBO/EPLB throughput claims are reported from the source without independent validation[^sgl-ep].

## Relationships

- Uses [vLLM Expert Parallel Deployment](vllm-expert-parallel-deployment.md) — companion EP design for comparing SGLang `--moe-a2a-backend`/`--moe-runner-backend` selection and DeepEP modes against vLLM all-to-all backends, plus shared EPLB rebalancing concept.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — attention-backend choice complements MoE runner choice in hybrid prefill/decode and Blackwell FP4 deployments.

[^sgl-ep]: Expert Parallelism — `../raw/sglang/advanced_features/expert_parallelism.mdx`.
