---
type: Concept
title: SGLang ViT CUDA Graphs for Multimodal Encoders
description: Per-sequence-length CUDA Graph capture and replay for SGLang vision encoders via ViTCudaGraphRunner, enabled by SGLANG_VIT_ENABLE_CUDA_GRAPH.
tags: [sglang, cuda-graphs, vision, multimodal, vit]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-vit-cg
    resource: ../raw/sglang/advanced_features/cuda_graph_for_multi_modal_encoder.mdx
    title: Cuda Graph for Multi-Modal Encoder in SGLang
---

SGLang optionally captures the vision-transformer `blocks + merger + deepstack merger` forward pass as CUDA Graphs keyed by sequence length `S`, replaying the cached graph for identical shapes to remove ViT kernel-launch overhead[^sgl-vit-cg].

## Motivation

Multimodal serving ViTs combine many layers with fragmented operators — LayerNorm, QKV projections, attention, MLP, residual connections — producing very frequent kernel launches[^sgl-vit-cg].

Server-side batches are commonly small or latency-sensitive, sometimes effectively batch 1 after flattening, so launch overhead is a large share of end-to-end latency[^sgl-vit-cg].

Input patch count `S` varies with image/video resolution and batch composition, which conflicts with CUDA Graphs' fixed-shape requirement and motivates per-`S` graph caching[^sgl-vit-cg].

## Captured scope

Implementation is built on `ViTCudaGraphRunner`, which captures the `blocks + merger + deepstack merger (optional)` portion of the vision transformer and replays it for identical shapes[^sgl-vit-cg].

## Dynamic shapes via graph cache

Variable sequence length `S` is handled by caching one graph per `S` with `graph_key = S`: the first occurrence captures a new graph and later occurrences replay it[^sgl-vit-cg].

Many distinct `S` values increase VRAM usage because each graph holds private memory pools[^sgl-vit-cg].

## Stable addresses

Parameter-like tensors are converted to static buffers so replay modifies contents without swapping tensor objects[^sgl-vit-cg]:

- `block_input` / `block_ws` / `block_output`
- `cu_full_len` / `cu_window_len` and their `kk` variants
- `sin_cos_ws`

## Attention-backend constraints

Attention arguments are frozen inside the captured graph[^sgl-vit-cg]:

- Triton attention expects `[cu_seqlens, cu_seqlens_kk, max_len]`.
- FA3 expects `[cu_seqlens, max_len]`.
- `max_len` is frozen as an integer constant.
- `cu_seqlens` is cached in a dictionary during `create_graph()` and not updated on replay.

For the same `graph_key = S`, replay additionally requires an identical segmentation pattern in `cu_seqlens` and window sequence lengths; mismatched segmentation causes incorrect attention partitioning[^sgl-vit-cg].

## Rotary buffer management

The feature reallocates a larger `sin_cos_ws` when sequence length grows, using `max_content_len` to bound the maximum allocated rotary-buffer size[^sgl-vit-cg].

## Enablement

Set `SGLANG_VIT_ENABLE_CUDA_GRAPH=1`[^sgl-vit-cg]:

```bash
SGLANG_VIT_ENABLE_CUDA_GRAPH=1 \
python3 -m sglang.launch_server \
  --model Qwen/Qwen3-VL-8B-Instruct
```

Compatible with piecewise CUDA Graphs by also passing `--enable-piecewise-cuda-graph`[^sgl-vit-cg]:

```bash
SGLANG_VIT_ENABLE_CUDA_GRAPH=1 \
python3 -m sglang.launch_server \
  --model Qwen/Qwen3-VL-8B-Instruct \
  --piecewise-cuda-graph-max-tokens 4096 \
  --enable-piecewise-cuda-graph \
  --piecewise-cuda-graph-compiler eager
```

## Supported models

Known supported models at time of writing[^sgl-vit-cg]:

- Qwen2.5-VL
- Qwen3-VL

## Relationships

- Uses [SGLang Attention Backends](sglang-attention-backends.md) — Triton versus FA3 argument shapes frozen in the ViT graph follow the same SGLang backend families.
- Uses [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — companion budget-based encoder-graph design in vLLM; both target ViT launch overhead but differ in per-`S` caching versus token-budget capture.

[^sgl-vit-cg]: Cuda Graph for Multi-Modal Encoder in SGLang — `../raw/sglang/advanced_features/cuda_graph_for_multi_modal_encoder.mdx`, covering ViT motivation, `ViTCudaGraphRunner` scope, per-`S` caching, static buffers, attention-backend freezing, rotary management, enablement commands, and supported Qwen-VL models.
