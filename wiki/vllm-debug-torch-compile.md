---
type: Concept
title: Debugging vLLM-torch.compile Integration
description: Isolating vLLM-compile failures with tlparse logs and per-subsystem disable flags for Dynamo, dynamic shapes, Inductor, cache, and CUDAGraphs.
tags: [vllm, torch-compile, debugging, cudagraphs, inductor]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: debug-compile
    resource: ../raw/vllm/design/debug_vllm_compile.md
    title: How to debug the vLLM-torch.compile integration
---

vLLM-compile is a custom compiler built on internal PyTorch Compile APIs (not plain `torch.compile`), running a four-stage pipeline — dynamic-batch TorchDynamo capture, graph split/specialize plus TorchInductor compilation with vLLM passes, compile-cache save, and CUDAGraph application — where each stage has a dedicated isolation flag so a failure can be narrowed with minimal performance loss[^debug-compile].

## Pipeline and isolation flags

- Stages: (1) full-graph TorchDynamo capture dynamic on batch size / token count, (2) optional split/specialize then TorchInductor compile per graph including vLLM custom passes and IR lowering, (3) save to vLLM compile cache, (4) CUDAGraphs to cut CPU overhead[^debug-compile].
- Isolation principle: turn off the minimal subsystem that restores reliability, and attach `tlparse` logs to bug reports[^debug-compile].
- Online `-cc` is short for `--compilation_config`[^debug-compile].
- Key flags (online / offline / effect)[^debug-compile]:

| Online | Offline | Effect |
|---|---|---|
| `--enforce-eager` | `enforce_eager=True` | Disable torch.compile and CUDAGraphs |
| `-cc.mode=0` | `CompilationMode.NONE` | Disable torch.compile only |
| `-cc.mode=1` | `CompilationMode.STOCK_TORCH_COMPILE` | Disable vLLM-compile modifications, use stock torch.compile |
| `-cc.cudagraph_mode=NONE` | `CUDAGraphMode.NONE` | Disable CUDAGraphs only |
| `-cc.backend=eager` | `backend='eager'` | Disable TorchInductor |
| `-cc.ir_enable_torch_wrap=False` | `ir_enable_torch_wrap=False` | Disable vLLM IR wrapping (captures eager-mode IR dispatch; only on by default with `mode=VLLM_COMPILE` + `backend="inductor"`) |

## Capture torch.compile logs with tlparse

- Install with `pip install tlparse` and set `TORCH_TRACE=<dir>`; one log file per rank is written there[^debug-compile].
- Offline: `TORCH_TRACE=~/trace_dir python my_script.py`; serving: `TORCH_TRACE=~/trace_dir vllm serve`, then Ctrl-C out[^debug-compile].
- Open with `tlparse ~/trace_dir/<rank_0_log_file>`, which emits HTML (e.g. `./tl_out/index.html`) showing compilation stages and fused kernels; send these logs with bug reports when possible[^debug-compile].
- `TORCH_LOGS=output_code <command>` prints Inductor output code directly[^debug-compile].
- `TORCH_LOGS=+dynamic vllm serve <model>` shows guard activity; look for `[guard added]` to find where guards originate[^debug-compile].

## TorchDynamo full-graph capture

- Model code must be capturable into a full graph via TorchDynamo; in fullgraph mode unsupported Python features error as graph breaks[^debug-compile].
- On a graph break, the guidance is to file an issue to `pytorch/pytorch` and rewrite the code to avoid the break; the source points to the Dynamo programming-model guide[^debug-compile].

## Dynamic shapes on batch size

- The forward pass must capture into one graph dynamic on batch size (token count), reused for all batch sizes[^debug-compile].
- Branching on token count (e.g. `if data.size[0] % 128 == 0: foo(...) else: bar(...)`) is not capturable into a single graph and can cause silent incorrectness, loud errors, or CUDA illegal memory accesses[^debug-compile].
- Diagnose with tlparse `compilation_metrics`: any symbolic constraint restricting batch sizes indicates a problem[^debug-compile].
- Fixes: avoid branching on token count, or wrap the branching logic in a custom operator since TorchDynamo does not trace into custom operators[^debug-compile].

## Dynamic-shape guards and constraint violations

- Dynamic-shape guards are Dynamo guards attached to dynamic dimensions (e.g. `seq_len`) to keep the artifact valid; branching on a dynamic value such as `if x > 10` creates a guard for the traced path[^debug-compile].
- vLLM assumes all torch.compile-added guards are safe to drop without constraining the graph to specific shapes; violations surface as runtime errors or `ConstraintViolationErrors` (a dynamic shape constrained to a single value)[^debug-compile].
- Debug with stricter dynamic-shape modes[^debug-compile]:

```sh
vllm serve meta-llama/Llama-3.2-1B -cc.dynamic_shapes_config.type=unbacked
vllm serve meta-llama/Llama-3.2-1B -cc.dynamic_shapes_config.type=backed_size_oblivious
```

```py
from vllm.config.compilation import CompilationConfig, DynamicShapesConfig, DynamicShapesType
LLM(model, compilation_config=CompilationConfig(
    dynamic_shapes_config=DynamicShapesConfig(type=DynamicShapesType.UNBACKED)))
LLM(model, compilation_config=CompilationConfig(
    dynamic_shapes_config=DynamicShapesConfig(type=DynamicShapesType.BACKED_SIZE_OBLIVIOUS)))
```

- `unbacked` uses unbacked symints that disallow guards, exposing incorrect guard insertion; `backed_size_oblivious` is stricter about guarding[^debug-compile].
- Design detail lives in the torch.compile integration doc section on dynamic shapes and guard dropping, referenced but not ingested here[^debug-compile].

## TorchInductor

- Inductor lowers the captured graph to Python code calling one or more Triton kernels; rare incorrect kernels manifest as silent incorrectness, CUDA illegal memory accesses, or loud errors[^debug-compile].
- Runtime assertions: on torch < 2.12 vLLM disables Inductor `assert_size_stride` / `assert_alignment` to avoid ~2ms per-forward overhead on large models; `VLLM_LOGGING_LEVEL=DEBUG` re-enables them, or set explicitly via `-cc.inductor_compile_config='{"size_asserts": true, "alignment_asserts": true, "scalar_asserts": true}'`; on torch >= 2.12 PyTorch's assert-once strategy means vLLM no longer suppresses them[^debug-compile].
- To test whether Inductor is at fault, set `backend='eager'` (`vllm serve -cc.backend=eager`); if confirmed, file a bug to `pytorch/pytorch` and optionally inspect the Triton kernels in the tlparse-located Inductor output[^debug-compile].
- Editable output code: set `VLLM_COMPILE_CACHE_SAVE_FORMAT=unpacked` or `-cc.compile_cache_save_format=unpacked` (default is `binary`); useful for breakpoints such as `torch.distributed.breakpoint()` and print statements[^debug-compile].

## Compile cache

- vLLM's cache layers over torch.compile's compiler cache so artifacts compile once and reload; torch.compile's cache is described as rock-stable while vLLM's is not always correct[^debug-compile].
- Disable with `VLLM_DISABLE_COMPILE_CACHE=1`; slower warm starts are the trade-off when serialization fails or correctness is suspect[^debug-compile].
- Manual purge: `rm -rf ~/.cache/vllm` (confirm location in logs) for vLLM's cache, `rm -rf /tmp/torchinductor_$(whoami)` for torch.compile's caches[^debug-compile].
- Wrong-cache cause: the cache key combines factors such as config flags and model name, so a missing factor yields stale hits; the source cites model-key computation in `vllm/config/model.py`[^debug-compile].
- Cached code must be serializable or saving errors; remedies are rewriting non-serializable pieces, filing a bug, or setting `VLLM_DISABLE_COMPILE_CACHE=1`[^debug-compile].

## CUDAGraphs

- CUDAGraphs capture a callable launching 1+ CUDA kernels into a replayable graph pinned to the memory regions used during capture; reuse on new data requires copying into the capture buffers, and only CUDA-kernel work (not CPU work) is captured[^debug-compile].
- vLLM uses the raw, unsafe-if-misused CUDAGraphs API[^debug-compile].
- Disable only CUDAGraphs with `vllm serve -cc.cudagraph_mode=NONE` or `LLM(model, compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE))`[^debug-compile].

## Coverage limits

- The vLLM-compile design diagram, both tlparse screenshots, and the dynamic-shapes constraint screenshot under `raw/vllm/assets/design/debug_vllm_compile/` were referenced but absent from `raw/` and were not inspected[^debug-compile].
- Linked design docs (`torch_compile.md`, `vllm_ir.md`), the vLLM torch.compile blog post, and the cited Office Hours / PyTorch Conference talks were not ingested here[^debug-compile].

[^debug-compile]: How to debug the vLLM-torch.compile integration — `../raw/vllm/design/debug_vllm_compile.md`, covering pipeline overview, tlparse usage, subsystem disable flags, Dynamo, dynamic shapes, guards, Inductor, compile cache, and CUDAGraphs sections.
