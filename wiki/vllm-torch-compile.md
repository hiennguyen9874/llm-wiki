---
type: Concept
title: vLLM torch.compile Integration
description: Default V1 torch.compile pipeline covering cache, dynamic shapes, Dynamo capture, Inductor compilation, and piecewise CUDA graphs.
tags: [vllm, torch-compile, compilation, cudagraphs, inductor]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:45:36Z }
sources:
  - id: torch-compile
    resource: ../raw/vllm/design/torch_compile.md
    title: '`torch.compile` integration'
---

In vLLM V1, `torch.compile` is enabled by default and treated as a critical path; the source walks through it with `VLLM_LOGGING_LEVEL=DEBUG vllm serve meta-llama/Llama-3.2-1B`[^torch-compile].

## Compilation cache

- Compiled artifacts live under `~/.cache/vllm/torch_compile_cache/<config-hash>/rank_0_0`; copying that tree to deployment hosts saves warm-up / startup compilation time[^torch-compile].
- Cache key considers related configs via `compute_hash` in the config folder, PyTorch configs via `compute_hash` in `compiler_interface.py`, and the model forward plus functions it calls[^torch-compile].
- The cache is considered safe and enabled by default; disable for debugging or suspected staleness with `VLLM_DISABLE_COMPILE_CACHE=1`[^torch-compile].
- vLLM guarantees compilation finishes before serving any request, so no request triggers a new compilation and latency spikes from on-demand compiles are avoided[^torch-compile].
- Default save format is `binary`; set `compile_cache_save_format=unpacked` in the compilation config or `VLLM_COMPILE_CACHE_SAVE_FORMAT=unpacked` to inspect generated code for debugging[^torch-compile].

## Dynamic shapes and guard dropping

`torch.compile` prefers to guard on dynamic shapes, while vLLM wants to drop many of those guards as immaterial[^torch-compile].

- **Backed** symbols can gain guards from user code, Dynamo, Inductor, or autograd, plus unconditional 0/1 specialization to `0`, `1`, or `>=2` even without branching on the range[^torch-compile].
- **Unbacked** symbols are guaranteed not to be guarded and are not 0/1 specialized, but an unhandled branch on their value can throw a data-dependent error; the framework is moving toward general paths instead of errors, at the cost of missed optimizations, fixed hint inputs, and conservative handling such as cloning in `contiguous()` / `reshape()` when contiguity cannot be proven[^torch-compile].
- **`backed_size_oblivious`** treats backed symbols as unbacked wherever explicit unbacked handling exists, mostly avoiding 0/1 specialization in framework code without guaranteeing no guards from user code or custom passes; it is experimental in PyTorch and may be deprecated, but is safer than plain backed with lower perf risk than unbacked[^torch-compile].

### Configuration

`DynamicShapesConfig.type` selects `BACKED` (default), `UNBACKED`, or `BACKED_SIZE_OBLIVIOUS`[^torch-compile].

Offline `LLM` class[^torch-compile]:

```python
from vllm import LLM, SamplingParams
from vllm.config.compilation import CompilationConfig, DynamicShapesConfig, DynamicShapesType

llm = LLM(
    model="meta-llama/Llama-3.2-1B",
    compilation_config=CompilationConfig(
        dynamic_shapes_config=DynamicShapesConfig(
            type=DynamicShapesType.BACKED_SIZE_OBLIVIOUS
        )
    )
)
```

Online serving[^torch-compile]:

```bash
vllm serve meta-llama/Llama-3.2-1B \
  --compilation-config '{"dynamic_shapes_config": {"type": "unbacked"}}'

vllm serve meta-llama/Llama-3.2-1B -cc.dynamic_shapes_config.type=unbacked
```

### Choosing a mode

- **BACKED:** maximal performance, accepting potentially unsafe dropped guards[^torch-compile].
- **UNBACKED:** strongest guarantee against guards, most conservative, may miss optimizations[^torch-compile].
- **BACKED_SIZE_OBLIVIOUS:** balance between guard avoidance and performance; experimental but safer than backed[^torch-compile].

## Dynamo Python capture

- Dynamo traces the model `forward` (example: `vllm/model_executor/models/llama.py:339`) plus inlined helpers such as `torch/nn/modules/module.py` attribute access and vLLM communication, attention, activation, norm, linear, rotary, embedding, and custom-op files[^torch-compile].
- All traced files feed the cache-directory decision, so any code change in them causes a cache miss and recompilation[^torch-compile].
- Outputs are `transformed_code.py` (Dynamo-transformed function that unpacks module tensors and calls the graph) and `computation_graph.py` (traced computation graph) under the rank cache directory[^torch-compile].

## Graph processing and splitting

- Graph inputs are input IDs, position IDs, model weights, and buffers; outputs are final hidden states, excluding LM-head projection and sampling[^torch-compile].
- Weights and buffers are static; only input and position IDs carry symbolic shapes sharing the same symbols, so the only varying dimension is the token / batch size[^torch-compile].
- Attention plus KV-cache interaction is opaque to Dynamo via the custom op `torch.ops.vllm.unified_attention_with_output`, preserving a full graph from Dynamo's perspective because attention output shares the query shape[^torch-compile].
- The graph is split by `splitting_ops` (usually attention) into indexed submodules: attention itself plus the segments between attentions; each submodule is processed individually[^torch-compile].

## Inductor compilation and specific shapes

- Each split piece with symbolic shape `None` is compiled by Inductor to a keyed Python artifact under `inductor_cache/..`; repeat runs log `Directly load ...` and bypass Inductor by loading from disk[^torch-compile].
- Pieces that recur share keys: for a Llama-style model there are effectively three unique subgraphs — pre-first-attention, repeated middle attention-to-attention segments, and post-last-attention[^torch-compile].
- Default compilation is symbolic / general-shape; explicit static sizes enable autotuned kernels[^torch-compile]:

```bash
vllm serve meta-llama/Llama-3.2-1B \
  --compilation-config '{"compile_sizes": [1, 2, 4, 8]}'
```

- Static-shape compilation turns on autotuning (example: `mm(8x2048, 2048x3072)` trying Triton configs beating cuBLAS dispatch), which takes seconds to minutes on first run but is cached; it stays off by default for user-friendliness and is recommended when maximum performance matters[^torch-compile].

## Piecewise CUDA graphs

- V1 captures piecewise CUDA graphs aligned with piecewise compilation: token-wise segments between attentions (including pre-first and post-last) are graphed, while attention stays eager because it is harder to make CUDA-graph compatible[^torch-compile].
- Fine-grained memory management keeps allocation and non-attention modules in the graph while excluding only the attention kernel; this motivates the attention custom op taking its output tensor as an input[^torch-compile].
- The compiler backend captures and manages graphs and intermediate buffers; the model runner only manages input buffers correctly[^torch-compile].
- vLLM picks a default capture-size set; override explicitly with[^torch-compile]:

```bash
vllm serve meta-llama/Llama-3.2-1B \
  --compilation-config '{"cudagraph_capture_sizes": [1, 2, 4, 8]}'
```

- Full-graph capture including attention is possible with a CUDA-graph-compatible attention backend and can help decode for small models or MoEs; see [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) for modes and compatibility[^torch-compile].

## Coverage limits

- `compute_hash` implementations in `vllm/config` and `vllm/compilation/compiler_interface.py`, plus the vLLM torch.compile blog post linked from the source, were not inspected[^torch-compile].
- Verbose Dynamo / Inductor / autotune logs and cache-directory listings are summarized here rather than reproduced in full[^torch-compile].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — attention is opaque custom-op code during capture, and backend choice determines full-graph eligibility.
- Depends on [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md) — that pipeline's per-stage disable flags and `tlparse` workflow are the debugging entry point for failures in the cache, Dynamo, dynamic-shape, Inductor, and CUDA-graph stages compiled here.
- Uses [vLLM torch.compile Fusion Passes](vllm-fusion-passes.md) — custom Inductor fusion passes run inside the Inductor stage compiled here.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — dispatcher, `CUDAGraphMode`, and backend-compatibility policy extend the piecewise-capture basis compiled here.

[^torch-compile]: `torch.compile` integration — `../raw/vllm/design/torch_compile.md`, covering default V1 enablement, compilation cache, dynamic shapes and guard dropping, Dynamo capture, graph processing/splitting, Inductor compilation with `compile_sizes`, and piecewise cudagraph capture.
