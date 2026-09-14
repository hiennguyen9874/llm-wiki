---
type: Concept
title: vLLM Fused MoE Modular Kernel
description: Architecture, components, initialization, and extension workflow for vLLM's modular fused MoE kernel.
tags: [vllm, moe, kernels, expert-parallelism, all2all]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: fused-moe-modular
    resource: ../raw/vllm/design/fused_moe_modular_kernel.md
    title: Fused MoE Modular Kernel
---

vLLM's `FusedMoEModularKernel` composes a fused MoE implementation from an All2All-backed `FusedMoEPrepareAndFinalizeModular` plus a compute-backed `FusedMoEExpertsModular`, bridged by a `TopKWeightAndReduce` policy that decides where top-k weight application and reduction run[^fused-moe-modular].

## Activation formats

The All2All dispatch determines the activation format[^fused-moe-modular]:

- Contiguous / Standard / Non-Batched (terms used interchangeably): contiguous `(M, K)` activations plus top-k ids and weights of shape `(M, num_topk)`. Example: `DeepEPHTPrepareAndFinalize`.
- Batched: `(num_experts, max_tokens, K)` activations with tokens for the same expert batched together, accompanied by `expert_num_tokens[num_experts]` marking valid entries. Example: `DeepEPLLPrepareAndFinalize`.

Both variants run quantization, dispatch/combine, permute/unpermute, expert GEMMs, and activation; the main operation-level difference is the permute/unpermute steps[^fused-moe-modular].

## Why modular

The operation count multiplied by per-operation implementation choices makes ad-hoc fused MoE combinations intractable and duplicated. Grouping operations into three logical components keeps combinations manageable, decouples All2All dispatch/combine from expert compute for independent development and testing, and provides abstract base classes as extension skeletons[^fused-moe-modular].

## Components

`FusedMoEModularKernel` splits the operation into[^fused-moe-modular]:

1. `TopKWeightAndReduce`
2. `FusedMoEPrepareAndFinalizeModular`
3. `FusedMoEExpertsModular`

### TopKWeightAndReduce

Top-k weight application and reduction logically sit after unpermute and before All2All combine. `FusedMoEExpertsModular` owns unpermute while `FusedMoEPrepareAndFinalizeModular` owns combine, so either side may do this step; the abstract `TopKWeightAndReduce` class preserves that flexibility[^fused-moe-modular].

Coordination protocol[^fused-moe-modular]:

- `FusedMoEPrepareAndFinalizeModular::finalize()` accepts a `TopKWeightAndReduce` argument and invokes it.
- `FusedMoEExpertsModular::finalize_weight_and_reduce_impl()` returns `TopKWeightAndReduceNoOp` when the experts implementation already applied weights and reduced.
- It returns `TopKWeightAndReduceContiguous`, `TopKWeightAndReduceNaiveBatched`, or `TopKWeightAndReduceDelegate` when `finalize()` must do that work.
- Implementations live in `vllm/model_executor/layers/fused_moe/topk_weight_and_reduce.py` per raw source paths.

### FusedMoEPrepareAndFinalizeModular

Exposes `prepare`, `prepare_no_receive`, and `finalize`[^fused-moe-modular]:

- `prepare`: input-activation quantization plus All2All dispatch.
- `prepare_no_receive`: like `prepare` but returns a receiver callback instead of waiting, enabling overlap of communication with work such as shared experts. Support is optional.
- `finalize`: All2All combine, optionally including top-k weight application and reduction via the injected `TopKWeightAndReduce`.

### FusedMoEExpertsModular

Holds the core MoE compute and exposes[^fused-moe-modular]:

- `apply()`: permute, matmul with `W1`, act-plus-mul, quantization, matmul with `W2`, unpermute, and possibly top-k weight application plus reduction.
- `workspace_shapes()`: declares two workspace shapes, workspace dtype, and fused-MoE output shape so `FusedMoEModularKernel::forward()` can allocate `workspace_13`, `workspace_2`, and output tensors once and reuse them as intermediate buffers.
- `finalize_weight_and_reduce_impl()`: returns the `TopKWeightAndReduce` object that `finalize()` should use.

## Kernel composition

`FusedMoEModularKernel` holds one prepare/finalize object and one experts object. Its `forward` flow is: `prepare` dispatch output → query `workspace_shapes` and allocate workspaces → `apply` experts compute → query `finalize_weight_and_reduce_impl` for the weight-and-reduce policy → `finalize` combine[^fused-moe-modular].

Defined in `vllm/model_executor/layers/fused_moe/modular_kernel.py` per raw source paths[^fused-moe-modular].

## Initialization via FusedMoEMethodBase

Three methods collectively build the kernel[^fused-moe-modular]:

- `maybe_make_prepare_finalize`: constructs a `FusedMoEPrepareAndFinalizeModular` when appropriate, e.g. base-class handling for EP+DP; derived classes such as `ModelOptNvFp4FusedMoE` may override for other cases such as EP+TP with `FlashInferCutlassMoEPrepareAndFinalize`.
- `select_gemm_impl`: abstract in the base class; each derived quantization method (`UnquantizedFusedMoEMethod`, `CompressedTensorsW8A8Fp8MoEMethod`, `CompressedTensorsW8A8Fp8MoECutlassMethod`, `Fp8MoEMethod`, `ModelOptNvFp4FusedMoE`) constructs the appropriate `FusedMoEExpertsModular`.
- `init_prepare_finalize`: builds the prepare/finalize object from settings, queries `select_gemm_impl` for the experts object, and assembles the `FusedMoEModularKernel`.

When a valid modular kernel can be built, it overrides `FusedMoEMethodBase::fused_experts`, keeping derived `apply` methods agnostic to which fused MoE implementation runs[^fused-moe-modular].

## Adding implementations

A prepare/finalize type is typically backed by one All2All dispatch/combine kernel family, e.g. DeepEP high-throughput versus DeepEP low-latency[^fused-moe-modular]:

1. Add an All2All manager in `vllm/distributed/device_communicators/all2all.py` to set up the dispatch/combine handles.
2. Subclass `FusedMoEPrepareAndFinalizeModular`, using the closest existing backend as reference. Key members: `prepare`, `has_prepare_no_receive`, `prepare_no_receive`, `finalize`, `activation_format` (`BatchedExperts` versus `Standard`), `topk_indices_dtype` (None when no strict kernel requirement, otherwise forwarded to expert selection), `max_num_tokens_per_rank`, and `num_dispatchers` (sizes dispatch output as `(num_local_experts, max_num_tokens, K)`).

A new experts type subclasses `FusedMoEExpertsModular`, declaring supported input/output activation formats via `activation_formats`, expert-map support via `supports_expert_map`, plus `workspace_shapes`, `apply`, and `finalize_weight_and_reduce_impl`[^fused-moe-modular].

## Testing, compatibility, and profiling

- Unit tests in `tests/kernels/moe/test_modular_kernel_combinations.py` iterate over prepare/finalize × experts combinations and run correctness checks when compatible. Register new types in `MK_ALL_PREPARE_FINALIZE_TYPES` and `MK_FUSED_EXPERT_TYPES` (`tests/kernels/moe/modular_kernel_tools/mk_objects.py`) and update the `Config::is_*` predicates in `tests/kernels/moe/modular_kernel_tools/common.py`[^fused-moe-modular].
- The same test module runs as a standalone compatibility checker, e.g. `--pf-type DeepEPLLPrepareAndFinalize --experts-type BatchedTritonExperts`; incompatible pairs error[^fused-moe-modular].
- `tests/kernels/moe/modular_kernel_tools/profile_modular_kernel.py` emits Torch traces for one `forward()` call for a compatible pair[^fused-moe-modular].
- Final implementation lists for prepare/finalize backends and experts kernels are maintained in the companion [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) concept.

## Coverage limits

- The four embedded PNG operation/block diagrams were not present under `raw/` and were not inspected; per-step dtype detail above comes from prose only[^fused-moe-modular].
- Linked Python modules, GitHub revision links, and test/profile scripts are outside `raw/` and were not inspected; file paths and CLI examples are reported as given[^fused-moe-modular].
- This page focuses on the contiguous/non-batched case as the source does; batched-case extrapolation is source-stated as straightforward but not independently verified[^fused-moe-modular].

## Relationships

- Uses [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — that concept holds the selectable backend/experts tables and compatibility families; this concept holds the architecture, lifecycle, and extension workflow.
- Depends on [vLLM Model Runner V2](vllm-model-runner-v2.md) — model execution context that invokes MoE layers built from these modular pieces.

[^fused-moe-modular]: Fused MoE Modular Kernel — `../raw/vllm/design/fused_moe_modular_kernel.md`.
