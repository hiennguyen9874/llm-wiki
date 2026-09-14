---
type: Concept
title: vLLM IR Functional Intermediate Representation
description: Functional IR dialect separating op semantics from kernel implementations with late priority-based dispatch and compile lowering.
tags: [vllm, ir, torch-compile, kernels, fusion]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:00:00Z }
sources:
  - id: vllm-ir
    resource: ../raw/vllm/design/vllm_ir.md
    title: 'vLLM IR: Functional Intermediate Representation'
---

vLLM IR is a functional intermediate representation filling the gap between low-level `torch` ops and vLLM layers such as `RMSNorm` and quantization operators, separating operator semantics from implementation and dispatching as a dialect in the torch FX representation[^vllm-ir].

## Design principles

- Eager-compile consistency: identical behavior barring minor numerics in eager and compiled modes[^vllm-ir].
- Simple, transparent, yet powerful kernel selection with good visibility and control for debugging[^vllm-ir].
- Convention over configuration: near-zero boilerplate to register ops and implementations[^vllm-ir].
- Extensibility: ops and implementations registered anywhere, in-tree or out-of-tree[^vllm-ir].
- Interoperability: fully compatible with regular torch ops and custom torch ops/kernels, allowing piecewise migration from `CustomOp`[^vllm-ir].

Delaying kernel selection until late in compilation lets the compiler operate on a higher-level representation, so fusion passes need one simple pattern per op, out-of-tree backends can lower from the higher level, and future autotuning can range over available implementations[^vllm-ir].

## Operation declaration

IR ops are declared with `@register_op` plus a native PyTorch implementation, for example `rms_norm` in `vllm/ir/ops/layernorm.py`[^vllm-ir].

The native implementation serves as semantic definition including shapes and strides, default implementation when no better one exists, and reference for testing other implementations[^vllm-ir].

`@register_op` options[^vllm-ir]:

- `name`: defaults to function name.
- `activations`: parameters considered activations, typically consumed by `maybe_inplace`; defaults to params starting with `x`.
- `allow_inplace`: whether to create a `maybe_inplace` overload.

## Implementation registration

Kernels register with `ir.ops.<op>.register_impl`, for example `rms_norm` provider `vllm_c` calling `torch.ops._C.rms_norm`[^vllm-ir]:

- `provider`: unique identifier; `native` is reserved for the native torch implementation[^vllm-ir].
- `supported`: static boolean checked once, for example `current_platform.is_cuda_alike()`[^vllm-ir].
- `supports_args`: `(*args, **kwargs) -> bool` dynamic argument check[^vllm-ir].
- `inplace`: whether the implementation reuses input memory for outputs[^vllm-ir].

Provider naming conventions include `vllm_c` for C++/CUDA via `torch.ops._C`, `aiter` for AMD AITER, `xpu_kernels` for SYCL kernels in `vllm-xpu-kernels`, `triton_*` for Triton kernels, and platform or library names otherwise[^vllm-ir].

Support predicates are called with fake tensors during compilation and real tensors in eager dispatch, should not check batch sizes or add value-based guards, and batch-invariant kernels are automatically selected when `VLLM_BATCH_INVARIANT=1`[^vllm-ir].

## Kernel selection

Selection is controlled by priority lists; the first supported implementation passing both `supported` and `supports_args` is selected, using the same dispatch logic in eager dispatch and compile lowering[^vllm-ir].

Command line[^vllm-ir]:

```bash
vllm serve meta-llama/Llama-3.2-1B --ir-op-priority.rms_norm=vllm_c
vllm serve meta-llama/Llama-3.2-1B --ir-op-priority.rms_norm=aiter,vllm_c,native
```

Python via `KernelConfig.ir_op_priority`[^vllm-ir]:

```python
KernelConfig(ir_op_priority={"rms_norm": ["vllm_c", "native"]})
```

Platform defaults are applied automatically; user-specified priorities are prepended, so unspecified implementations are appended automatically[^vllm-ir]. Documented examples are CUDA/XPU/ROCm with Inductor defaulting to `native`, CUDA eager or Dynamo-only defaulting to `vllm_c,native`, ROCm future default `aiter,vllm_c,native`, and XPU eager or Dynamo-only defaulting to `xpu_kernels,native`[^vllm-ir].

## `maybe_inplace` overload

`maybe_inplace` signals that activation inputs need not be preserved, allowing in-place implementations to reuse input memory; using a donated input afterwards is undefined behavior[^vllm-ir].

```python
out, res_out = ir.ops.fused_add_rms_norm(x, residual, weight, epsilon)  # preserves inputs
out, res_out = ir.ops.fused_add_rms_norm.maybe_inplace(x, residual, weight, epsilon)  # may modify x, residual
```

To preserve an input, use the default overload or clone before `maybe_inplace`[^vllm-ir].

Compilation behavior: the pre-grad inplace-functionalization pass validates donated inputs are not used again, converts `maybe_inplace` to the functional `default` overload, and tracks donated graph inputs in `PassContext` for later clone elimination[^vllm-ir].

Eager behavior: `maybe_inplace` dispatches directly to `impl_fn(*args)`, while `default` clones activation inputs first when the selected implementation is `inplace`[^vllm-ir].

This enables zero-allocation transformer residual patterns when model code uses `maybe_inplace` with an in-place kernel, reusing for example hidden states and residual inputs for norm outputs in both eager and compiled modes[^vllm-ir].

## Compilation pipeline

1. **Dynamo tracing:** IR ops appear as opaque `torch.ops.vllm_ir.*` custom ops directly in the FX graph without decomposition[^vllm-ir].
2. **AOTAutograd and functionalization:** mutating ops become functional; vLLM manually converts `maybe_inplace` to `default` in the pre-grad hook and records donated inputs before AOTAutograd functionalization[^vllm-ir].
3. **IR fusion and transformation passes:** custom passes fuse high-level IR ops, distribute for sequence parallelism, and transform without matching low-level torch ops, per-implementation variants, or custom-kernel functionalization issues[^vllm-ir].
4. **IR lowering:** `VllmIRLoweringPass` traces the selected implementation with `make_fx` / `replace_by_example` and substitutes its nodes for each IR node; `inplace=True` implementations get clones inserted to preserve functional semantics[^vllm-ir].
5. **Clone cleanup:** `UnsafeCloneEliminationPass` removes unnecessary lowering clones when the cloned input is locally created and unused afterwards or is a donated graph parameter[^vllm-ir].
6. **Inductor optimization and codegen:** remaining standard torch ops and platform custom ops go through Inductor lowering, pointwise fusion, memory planning, kernel generation, and autotuning[^vllm-ir].

Eager mode dispatches directly by priority list with minimal overhead, while compile mode keeps IR ops in the FX graph and lowers with fake tensors; this consistency supports eager prototyping, debugging with compilation disabled, and gradual migration to compiled execution[^vllm-ir].

## Out-of-tree implementations

External packages register without modifying vLLM via `ir.ops.<op>.register_impl("my_platform", supported=...)`, configure platform defaults through `Platform.get_default_ir_op_priority()`, and still allow user override through the same `ir_op_priority` mechanism[^vllm-ir].

## Debugging and observability

- Enable `VLLM_LOGGING_LEVEL=DEBUG` to log selected implementations, rejection reasons, compilation cache hits or misses, and IR lowering statistics[^vllm-ir].
- After compilation, inspect `backend.lowering_pass.selected_impls` for per-node implementation choices[^vllm-ir].

## Migration from CustomOp

IR coexists with and gradually replaces `CustomOp` incrementally, one operation at a time[^vllm-ir]:

1. Convert the `CustomOp` class and move `forward_native` to a `@register_op` function.
2. Register implementations with `@ir.ops.op_name.register_impl` instead of overriding methods.
3. Replace `self.op(...)` layer usage with `ir.ops.op_name(...)`.
4. Migrate `--compilation-config.custom-ops` configuration to `--ir-op-priority`.

## Coverage limits

- Python excerpts for op declaration, impl registration, model usage, dispatch, functionalization, lowering, and OOT registration are summarized rather than reproduced in full[^vllm-ir].
- `VLLM_BATCH_INVARIANT` automatic selection, future autotuning over implementations, in-progress OOT-backend lowering, and planned lowering functionalization change are reported as stated without independent verification[^vllm-ir].

## Relationships

- Uses [vLLM torch.compile Integration](vllm-torch-compile.md) — Dynamo tracing, AOTAutograd functionalization, and Inductor codegen stages host the IR pipeline.
- Uses [vLLM torch.compile Fusion Passes](vllm-fusion-passes.md) — post-grad fusion and sequence-parallelism transforms operate on high-level IR ops before lowering.
- Uses [vLLM CustomOp Dispatch and Registration](vllm-custom-op.md) — IR interoperates with regular and custom torch ops and provides the incremental migration path from `CustomOp`.

[^vllm-ir]: vLLM IR: Functional Intermediate Representation — `../raw/vllm/design/vllm_ir.md`, covering motivation and principles, op and implementation registration, model usage, priority-based kernel selection, six-stage compilation pipeline, `maybe_inplace` semantics, eager versus compile behavior, OOT implementations, debugging, and `CustomOp` migration.
