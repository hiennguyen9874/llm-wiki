---
type: Concept
title: vLLM CUDA Graphs Modes and Dispatch
description: Configurable CUDA Graphs modes, runtime dispatcher, nested wrappers, and attention-backend compatibility for vLLM v1.
tags: [vllm, cuda-graphs, compilation, attention]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:38:18Z }
sources:
  - id: cuda-graphs
    resource: ../raw/vllm/design/cuda_graphs.md
    title: CUDA Graphs
---

vLLM v1 decouples CUDA Graphs capture from compilation with a single `CompilationConfig.cudagraph_mode` knob, a central `CudagraphDispatcher` that picks a runtime mode plus dispatch key per batch, and nested `CUDAGraphWrapper` instances that capture or replay full versus piecewise graphs from one piecewise FX graph[^cuda-graphs].

## Batch vocabulary

- **Uniform decode** means pure decode (`max_query_len=1`) or speculative decode (`max_query_len=1+num_spec_tokens`); the opposite is a **non-uniform** batch such as prefill or mixed prefill-decode[^cuda-graphs].
- Prior piecewise compilation captured piecewise graphs while leaving CUDA-Graphs-incompatible operations, mainly attention, eager; later non-piecewise compilation enabled full graphs but coupled compilation to capture in an all-or-nothing way[^cuda-graphs].
- The redesign explicitly separates prefill/mixed versus uniform-decode capture, makes full capture possible without compilation, dispatches full versus piecewise at runtime by batch composition, and centralizes control to reduce complexity[^cuda-graphs].

## `CUDAGraphMode` options

`CUDAGraphMode` in `CompilationConfig.cudagraph_mode` supports[^cuda-graphs]:

| Mode | Behavior |
|---|---|
| `NONE` | CUDA Graphs off; good for debugging. |
| `PIECEWISE` | Single-mode past default; attention or other incompatible operations stay eager while everything else uses CUDA Graphs; requires piecewise compilation. |
| `FULL` | Single-mode capturing only full CUDA Graphs for non-uniform batches, with uniform-decode batches of the same batch size reusing the compatible non-uniform graph; good for small models or small prompts. |
| `FULL_DECODE_ONLY` | Full CUDA Graphs for uniform decode only, no graphs for prefill/mixed; suitable for decode instances in P/D disaggregation and saves `PIECEWISE` graph memory. |
| `FULL_AND_PIECEWISE` | Default when available: full graphs for uniform decode plus piecewise graphs for other batches; generally most performant especially for low latency with small models or MoEs, but uses the most memory and takes longest to capture. |

Defaults: on v1 with piecewise compilation the default is `FULL_AND_PIECEWISE`, except pooling models which remain `PIECEWISE`; when piecewise compilation is unavailable the default is `NONE`[^cuda-graphs].

Single-mode `NONE`, `PIECEWISE`, and `FULL` correspond to past eager, piecewise-graph, and full-graph behavior, while dual-mode `FULL_DECODE_ONLY` and `FULL_AND_PIECEWISE` dynamically dispatch to a member runtime mode plus a possible `NONE` fallback when no suitable graph exists[^cuda-graphs].

Cascade attention is never CUDA-Graph compatible but works with every mode configuration by always dispatching to `PIECEWISE` when available and otherwise `NONE`[^cuda-graphs].

Not every mode works with every attention backend; vLLM automatically downgrades to the closest supported mode, for example converting `FULL` to `FULL_AND_PIECEWISE` when piecewise compilation is enabled and to `FULL_DECODE_ONLY` otherwise if a backend only supports pure-decode/uniform batches[^cuda-graphs].

## Architecture

Core components[^cuda-graphs]:

- `CUDAGraphWrapper` (`vllm.compilation.cuda_graph`): captures and replays graphs around a wrapped callable.
- `CudagraphDispatcher` (`vllm.v1.cudagraph_dispatcher`): central controller and single source of truth for available graphs and runtime dispatch.
- `CUDAGraphMode` (`vllm.config.compilation`): configured and runtime modes.
- `BatchDescriptor` (`vllm.forward_context.BatchDescriptor`): unique padded-batch representation used as dispatch key.

Previously graphs and compilation were tightly coupled inside `PiecewiseBackend` with implicit dispatch by batch size; now wrapper logic is separated into `CUDAGraphWrapper` for both full and piecewise abilities and dispatch is explicit through runtime mode plus `BatchDescriptor` via `CudagraphDispatcher`[^cuda-graphs].

## `BatchDescriptor`

```python
class BatchDescriptor(NamedTuple):
    num_tokens: int
    num_reqs: int
    uniform: bool = False
    has_lora: bool = False
```

`num_tokens` may be padded length and `uniform` means all requests share the same query length; many backends only support full graphs for uniform batches, and spec-decode validation can make a decode batch uniform with query length `1+num_spec_tokens` rather than `num_tokens == num_reqs`[^cuda-graphs].

The structure is intended to identify a padded batch with minimal fields for a graph key; future extensions may add items such as `uniform_query_len` or fields for non-token-length-aware multimodal inputs[^cuda-graphs].

## `CudagraphDispatcher`

The dispatcher maintains separate valid key sets for `FULL` and `PIECEWISE` runtime modes, accepts an initial rough descriptor for the padded input, returns the selected runtime mode and final descriptor, and publishes that decision through forward contexts for wrappers to trust blindly[^cuda-graphs].

Keys are initialized by `initialize_cudagraph_keys`, called by the GPU model runner after attention backends initialize; currently it appends available combinations from the mode's `decode_mode`/`mixed_mode` and `cudagraph_capture_sizes`, with room for fancier future preparation[^cuda-graphs].

Runtime dispatch follows the priority `FULL > PIECEWISE > None`; an absent key falls back to `NONE` eager execution[^cuda-graphs]:

```python
batch_descriptor = BatchDescriptor(num_tokens=num_input_tokens, uniform_decode=...)
runtime_mode, batch_descriptor = cudagraphdispatcher.dispatch(batch_descriptor)
with set_forward_context(..., cudagraph_runtime_mode=runtime_mode, batch_descriptor=batch_descriptor):
    output = self.model(...)
```

## `CUDAGraphWrapper` and nested design

Each wrapper is bound to one runtime mode, either `PIECEWISE` or `FULL`, and either calls its runnable directly or captures/replays a graph[^cuda-graphs]:

1. Inspect `runtime_mode` and `batch_descriptor` from the global forward context.
2. On `NONE` or a mode mismatch, call the runnable directly.
3. On a mode match, capture a new cache entry when the key is absent or replay the cached graph when present.

Trusting the dispatcher-supplied forward context lets the same wrapper class serve both modes and avoids mismatched wrapper/dispatcher state[^cuda-graphs].

Full and piecewise graphs coexist through nesting over a single piecewise FX graph: a `FULL` wrapper surrounds the entire model while `PIECEWISE` wrappers sit inside each piecewise backend, so full capture/replay bypasses the inactive piecewise wrappers, piecewise execution bypasses the inactive full wrapper, and `NONE` leaves both inactive for eager execution[^cuda-graphs].

## Capture and warm-up

Capture occurs on the runner's first model forward, a `_dummy_run`, using a non-`NONE` runtime mode; for full graphs the runner sets attention metadata so backends launch the intended kernel routine, principally using `max_query_len` to distinguish uniform decode (`uniform_query_len`) from non-uniform batches (`num_tokens`) for most backends[^cuda-graphs].

The wrapper no longer owns warm-up; the GPU model runner performs eager warm-up under `NONE`, including explicitly running attention during the warm-up `dummy_run` needed for full-graph preparation[^cuda-graphs].

## Attention-backend compatibility

`AttentionCGSupport` (`vllm.v1.attention.backend`) ranks backend capability as `ALWAYS=3 > UNIFORM_BATCH=2 > UNIFORM_SINGLE_TOKEN_DECODE=1 > NEVER=0`, excluding cascade attention which is treated as never supported[^cuda-graphs]:

- `ALWAYS`: mixed prefill-decode supported.
- `UNIFORM_BATCH`: only batches whose query lengths are equal, covering spec-decode decodes of length `1+num_speculative_tokens`.
- `UNIFORM_SINGLE_TOKEN_DECODE`: only batches containing `query_len==1` decodes.
- `NEVER`: no support.

Hybrid models use the minimum capability across backends and downgrade the requested mode to the best fit; for example `FULL` becomes `FULL_AND_PIECEWISE` when the minimum is `UNIFORM_BATCH` or `PIECEWISE` when the minimum is `NEVER` under `-O3` compilation, with the complete policy in `GPUModelRunner._check_and_update_cudagraph_mode`[^cuda-graphs].

Reported backend support at the time of writing[^cuda-graphs]:

| Backend | Support | Note |
|---|---|---|
| FlashAttention v2 | `UNIFORM_BATCH` | Effectively `ALWAYS`, downgraded as a performance workaround toward `FULL_AND_PIECEWISE`. |
| FlashAttention v3 | `ALWAYS` | Unified routine for both batch kinds, so `FULL` works. |
| Triton Attention | `ALWAYS` | Prefers `FULL_AND_PIECEWISE` because prefill/mixed and pure-decode kernels differ. |
| AITER FlashAttention | `UNIFORM_BATCH` | — |
| FlashInfer | `UNIFORM_SINGLE_TOKEN_DECODE` | Becomes `UNIFORM_BATCH` with TRTLLM attention on Blackwell. |
| FlashMLA | `UNIFORM_BATCH` | — |
| FlashInferMLA | `UNIFORM_BATCH` | — |
| FlashInferMLASparse | `UNIFORM_BATCH` | — |
| AITER MLA | `UNIFORM_SINGLE_TOKEN_DECODE` | — |
| CUTLASS MLA | `UNIFORM_SINGLE_TOKEN_DECODE` | — |
| Mamba attention | `UNIFORM_SINGLE_TOKEN_DECODE` | — |

Unlisted backends are declared `NEVER`[^cuda-graphs].

## Usage

CLI uses the uppercase mode string[^cuda-graphs]:

```bash
vllm serve --model meta-llama/Llama-3.1-8B-Instruct --compilation-config '{"cudagraph_mode": "FULL_AND_PIECEWISE"}'
```

Python example[^cuda-graphs]:

```python
import os
os.environ.setdefault("VLLM_LOGGING_LEVEL", "DEBUG")

import vllm
from vllm.config import CUDAGraphMode

compilation_config = {"mode": 3, "cudagraph_mode": "FULL_AND_PIECEWISE"}
model = vllm.LLM(
    model="meta-llama/Llama-3.1-8B-Instruct",
    dtype="auto",
    compilation_config=compilation_config,
)
sampling_params = vllm.SamplingParams(temperature=0, max_tokens=1024)
outputs = model.generate(["My name is John and"], sampling_params=sampling_params)
```

All `PIECEWISE`-related modes require piecewise compilation and all `FULL`-related modes require backend CUDA-Graph support[^cuda-graphs].

## Piecewise compilation versus whole-graph passes

`AttnQuantFusionPass` and `SequenceParallelismPass` must see the whole graph and are incompatible with piecewise compilation; as a short-term fix vLLM disables piecewise compilation with `splitting_ops=[]` when attention fusion is enabled and uses `FULL` or `FULL_DECODE_ONLY` according to backend support, at the cost of another optimization incompatibility[^cuda-graphs].

Longer term, graph partitioning can move into Inductor with `CompilationConfig.use_inductor_graph_partition=True`, currently experimental and requiring `torch>=2.9`; it compiles the whole graph without reusing piecewise artifacts, increasing compilation time, but is planned as the default once vLLM supports Torch 2.9 and is also expected to speed up piecewise graph capture[^cuda-graphs].

Performance examples are linked from the source PR discussion rather than reproduced here[^cuda-graphs].

## Coverage limits

- The before/after design diagrams and executor-runtime/wrapper-flow figures under `../assets/design/cuda_graphs/` are referenced but absent from `raw/` and were not inspected[^cuda-graphs].
- Linked `torch_compile.md`, the source PR 20059 implementation, and performance-issue comments were not ingested here[^cuda-graphs].
- ViT/multimodal encoder graphs are compiled separately in [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md)[^cuda-graphs].

## Relationships

- Depends on [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md) — that pipeline's CUDAGraph stage and `cudagraph_mode=NONE` isolation flag are the debugging entry point for the modes and dispatcher compiled here.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — backend selection determines full-graph capability and automatic mode downgrades.
- Uses [vLLM Model Runner V2](vllm-model-runner-v2.md) — model-runner warm-up, dummy runs, and explicit graph management are the execution context for dispatcher keys and nested wrappers.
- Uses [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — vision-encoder budget graphs are orthogonal to the decoder modes and dispatcher compiled here and can be enabled simultaneously.

[^cuda-graphs]: CUDA Graphs — `../raw/vllm/design/cuda_graphs.md`, covering motivation, `CudagraphModes`, dispatcher/wrapper design, `BatchDescriptor`, attention-backend compatibility, usage, whole-graph passes, and performance links.
