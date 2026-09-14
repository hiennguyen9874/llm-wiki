---
type: Concept
title: vLLM Encoder CUDA Graphs for Vision Transformers
description: Budget-based CUDA Graphs capture and replay for vision encoders, with greedy packing, dual-path graphs, video support, and model opt-in protocol.
tags: [vllm, cuda-graphs, vision, multimodal]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:42:23Z }
sources:
  - id: encoder-cuda-graphs
    resource: ../raw/vllm/design/cuda_graphs_multimodal.md
    title: Vision Encoder (ViT) CUDA Graphs
---

vLLM captures the multimodal vision-encoder forward pass as budget-based CUDA Graphs independently from decoder graphs, replaying the smallest fitting token budget after greedy packing and falling back to eager execution on overflow[^encoder-cuda-graphs].

## Scope

- Targets encoder (ViT) execution such as Qwen3-VL; orthogonal to decoder graphs and can be enabled simultaneously[^encoder-cuda-graphs].
- Single-path image/video capture plus dual-path mode for two-tower encoders such as DeepSeek-OCR SAM plus CLIP with dynamic tiling[^encoder-cuda-graphs].
- Based on PR 35963 for ViT image graphs, PR 38061 for video, and PR 43586 for dual-path graphs[^encoder-cuda-graphs].

## Why budgets

Vision-encoder launch overhead dominates at small batch or image size; pre-capturing full encoder forwards at multiple token-budget levels during initialization removes host-side launch overhead at replay time[^encoder-cuda-graphs].

Dual-path motivation: global and local paths have independent token profiles, for example 272 tokens per global image versus 100 tokens per local patch in DeepSeek-OCR, so a monolithic graph would waste packing efficiency[^encoder-cuda-graphs].

## Core components

- `EncoderCudaGraphManager` in `vllm.v1.worker.encoder_cudagraph`: capture, replay, greedy packing, and data-parallel execution[^encoder-cuda-graphs].
- `SupportsEncoderCudaGraph` in `vllm.model_executor.models.interfaces`: runtime-checkable opt-in protocol for models[^encoder-cuda-graphs].
- `EncoderItemSpec` in `vllm.v1.worker.encoder_cudagraph_defs`: per-item input size, total `output_tokens`, and per-path `path_output_tokens`[^encoder-cuda-graphs].
- `BudgetGraphMetadata`: captured graph plus I/O buffers for one token budget, including `token_budget`, `max_batch_size`, `max_frames_per_batch`, `input_buffers`, and encoder-hidden-state `output_buffer`[^encoder-cuda-graphs].

## Budget capture

- Multiple graphs are pre-captured at token budgets such as `[2048, 4096, 8192, 13824]`; all budgets share one maximum batch size[^encoder-cuda-graphs].
- Auto-inference generates power-of-2 levels from `get_encoder_cudagraph_budget_range()`, always including the maximum even when off the power-of-2 grid; `encoder_cudagraph_token_budgets` overrides auto-inference[^encoder-cuda-graphs].
- Each `EncoderCudaGraphConfig.paths` entry defines an independently captured path with its own minimum budget and optional zero-token-batch support[^encoder-cuda-graphs].

## Runtime packing and replay

- Sort items by output tokens smallest-first, greedily pack into sub-batches within the largest token budget and `max_batch_size`, then replay the smallest fitting budget; repeat until exhausted[^encoder-cuda-graphs].
- Overflow items fall back to eager execution; manager logs hit/miss statistics[^encoder-cuda-graphs].
- Per replay: compute buffers via `prepare_encoder_cudagraph_replay_buffers()`, zero pre-allocated `input_buffers`, slice-copy replay values, replay graph, then clone outputs because buffers are reused[^encoder-cuda-graphs].
- Data-parallel mode with `mm_encoder_tp_mode="data"` uses load-balanced assignment via `get_load_balance_assignment`, local execution, then ordered gather via `tensor_model_parallel_all_gather`[^encoder-cuda-graphs].

## Multi-path graphs

- DeepSeek-OCR configures `global` and `local` paths under `budget_graphs["global"]` and `budget_graphs["local"]`[^encoder-cuda-graphs].
- Example budgets capped at the same `max_budget`: global power-of-2 from its minimum such as `[272, 544, 1088, 2176, 4352, 8704, 13824]`; local power-of-2 from its minimum with `0` included when `allow_zero_tokens=True`, such as `[0, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 13824]` for images at or below 640x640 with no local patches[^encoder-cuda-graphs].
- Packing constrains every path simultaneously using `path_output_tokens`: sort by total tokens, add an image only when every accumulated path count stays within that path's maximum and image count stays within `max_batch_size`, then choose the smallest fitting budget independently per path[^encoder-cuda-graphs].
- Partial fallback is per path: replay the fitting graph for non-empty paths, run only the overflowing path eagerly, skip zero-token paths, and never capture or replay a `0`-budget graph[^encoder-cuda-graphs].
- Paths may use different buffer keys; the manager iterates each graph's own `input_buffers.keys()` rather than a shared list, for example DeepSeek-OCR `pixel_values` shape `[B, 3, 1280, 1280]` versus `images_crop` shape `[P, 3, 1024, 1024]`[^encoder-cuda-graphs].
- `postprocess_encoder_output` receives path-keyed outputs; DeepSeek-OCR reshapes global to `[B, 272, n_embed]` and local to `[P, 100, n_embed]`, assembles patch grids with newline tokens, and concatenates `[patches_grid, global, view_separator]` per image[^encoder-cuda-graphs].
- Benefit: one path can hit while the other runs eager, avoiding zero-padded patch compute and graph invalidation from variable `crop_shape`[^encoder-cuda-graphs].

## Video support

- PR 38061 generalizes the manager to image keys `pixel_values` plus `image_grid_thw` and video keys `pixel_values_videos` plus `video_grid_thw`; video needs larger `cu_seqlens` because each item contributes `T` sequences[^encoder-cuda-graphs].
- Mixed image-plus-video prompts are supported[^encoder-cuda-graphs].
- Video graphs auto-disable when EVS or VidCom2 token pruning is enabled because data-dependent token counts are incompatible with capture[^encoder-cuda-graphs].

## Model opt-in protocol

Models implement `SupportsEncoderCudaGraph` without changing the manager[^encoder-cuda-graphs]:

- `get_encoder_cudagraph_config()` — modalities, buffer keys, hidden size, padding, max frames per video.
- `get_encoder_cudagraph_budget_range(vllm_config)` — `(min_budget, max_budget)`.
- `get_encoder_cudagraph_item_specs(mm_kwargs)` — per-item specs.
- `select_encoder_cudagraph_items(mm_kwargs, indices)` — sub-batch extraction for packing and DP sharding.
- `prepare_encoder_cudagraph_capture_inputs(..., path="default")` — dummy capture inputs; `"global"` or `"local"` selects the path.
- `prepare_encoder_cudagraph_replay_buffers(..., path="default")` — replay values keyed to match captured `input_buffers`.
- `encoder_cudagraph_forward(inputs, path="default")` — fixed-shape forward for capture and replay.
- `encoder_eager_forward(mm_kwargs, path="default")` — eager fallback, optionally per path.
- `postprocess_encoder_output(outputs, ...)` — assemble path-keyed outputs.

## Compatibility

Image graphs are supported for all listed architectures; video and multi-path coverage is narrower[^encoder-cuda-graphs]:

- Video ✅: `Glm4v`, `Gemma4`, `InternVLChatModel`, `Qwen2VL`, `Qwen2_5_VL`, `Qwen3VL`, `Qwen3_5`, `Qwen3_5Moe`, `MiniCPMV` 2.6 and 4.0.
- Video ❌: `DeepseekOCR`, `Ernie4_5_VLMoe`, `Gemma3`, `KimiVL`, `Llama4`, `Step3VL`, `MiniCPMV` 2.5.
- Multi-path ✅: only `DeepseekOCRForCausalLM` and `Step3VLForConditionalGeneration`; all other listed architectures ❌.

Hardware at time of writing: NV Blackwell ✅ and NV Ampere ✅ for all listed architectures; AMD MI300X unknown ❔ for all; AMD MI350X/MI355X ✅ except `MiniCPMV` unknown ❔[^encoder-cuda-graphs].

Tested encoder attention backends: `--mm-encoder-attn-backend=FLASH_ATTN` and `FLASHINFER` on Blackwell; Qwen2-VL and Qwen2.5-VL only FA2 and FA3 tested; MI350X gfx950 used ROCm-default `FLASH_ATTN`[^encoder-cuda-graphs].

## Configuration

`CompilationConfig` fields[^encoder-cuda-graphs]:

- `cudagraph_mm_encoder` (`bool`, default `False`) — enable encoder graph capture per budget.
- `encoder_cudagraph_token_budgets` (`list[int]`, default `[]`) — explicit budgets; empty means auto-inferred power-of-2 levels.
- `encoder_cudagraph_max_vision_items_per_batch` (`int`, default `0`) — max images/videos per batch; `0` means `max_budget // min_budget`.
- `encoder_cudagraph_max_frames_per_batch` (`int`, default `None`) — max video frames per batch; `None` means items-per-batch times model `max_frames_per_video`; forced to `0` for image-only mode when video count per prompt is `0`.

Multi-path minima and `allow_zero_tokens` are model-level `EncoderCudaGraphPathConfig`; the manager reuses one execution loop for single- and multi-path models[^encoder-cuda-graphs].

## Usage

```bash
vllm serve Qwen/Qwen3-VL-32B \
  --compilation-config '{"cudagraph_mm_encoder": true}'
```

```bash
vllm serve Qwen/Qwen3-VL-32B \
  --compilation-config '{"cudagraph_mm_encoder": true, "encoder_cudagraph_token_budgets": [2048, 4096, 8192, 13824], "encoder_cudagraph_max_vision_items_per_batch": 8}'
```

```python
compilation_config = {
    "cudagraph_mm_encoder": True,
}
model = vllm.LLM(
    model="Qwen/Qwen3-VL-32B",
    compilation_config=compilation_config,
)
```

Video adds `encoder_cudagraph_max_frames_per_batch`; Llama 4 image-only example also sets `--limit-mm-per-prompt '{"image": 1}'`[^encoder-cuda-graphs].

## Benchmarks

GB200 `vllm bench mm-processor` results reported in source; see PR 35963 for full details and PR 38061 for A100 video details[^encoder-cuda-graphs]:

- 1x GB200, Qwen3-VL-30B-A3B-Instruct, VisionArena-Chat 3000 prompts: FLASH_ATTN mean +11.8% and P99 +31.6%; FLASHINFER mean +19.6% and P99 +40.3%.
- 4x GB200 TP=4 DP=4, Qwen3-VL-32B-Instruct, random-mm 20 336x336 images/request: FLASH_ATTN mean +18.4% and P99 +14.0%; FLASHINFER mean +44.4% and P99 +84.9%.

Reproduce with explicit budgets such as `[512, 1024, 1536, 2048, 2560, 3072, 3584, 4096, 4864]` and `--mm-encoder-attn-backend FLASH_ATTN|FLASHINFER`; multi-GPU adds `--tensor-parallel-size 4 --mm-encoder-tp-mode data`[^encoder-cuda-graphs].

## Relationships

- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — decoder full versus piecewise modes and dispatcher are orthogonal to encoder budget graphs; both can be enabled together.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — encoder backend selection through `--mm-encoder-attn-backend` determines tested encoder-graph support.

[^encoder-cuda-graphs]: Vision Encoder (ViT) CUDA Graphs — `../raw/vllm/design/cuda_graphs_multimodal.md`, covering orthogonal encoder graphs, dual-path design, budget capture, greedy packing, video support, `SupportsEncoderCudaGraph` protocol, compatibility matrices, configuration, usage, and benchmarks.
