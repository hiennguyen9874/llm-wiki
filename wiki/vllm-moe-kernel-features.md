---
type: Concept
title: vLLM Fused MoE Kernel Features
description: Selecting vLLM modular MoE All2All backends and experts kernels by activation format, quantization, and compatibility families.
tags: [vllm, moe, kernels, expert-parallelism, quantization]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: moe-kernel-features
    resource: ../raw/vllm/design/moe_kernel_features.md
    title: Fused MoE Kernel Features
---

vLLM composes modular fused-MoE kernels from an All2All `FusedMoEPrepareAndFinalizeModular` backend plus a `FusedMoEExpertsModular` experts kernel, selected by matching activation format, quantization type/format, async needs, and tested families[^moe-kernel-features].

## Modular All2All backends

Each `FusedMoEPrepareAndFinalizeModular` subclass wraps one All2All backend for expert parallelism in the `MoERunner` layer[^moe-kernel-features].

Contract details[^moe-kernel-features]:

- All `prepare` methods expect standard-format activations; all `finalize` methods return standard format.
- Output activation format is the `prepare`-step output, which `finalize` must also accept.
- `prepare` output is the quantized type; `finalize` generally takes the original activation type. Example: bf16 input with fp8 per-tensor scales means `prepare` returns fp8/per-tensor activations while `finalize` takes bf16 activations.
- Quantization may happen before or after dispatch depending on backend support.
- Async backends support DBO (Dual Batch Overlap) and shared-expert overlap during combine.
- Some models require topk weights applied to input activations when topk==1, e.g. Llama; modular kernels handle this in the prepare/finalize subclass, non-modular kernels in the experts function.
- Selection is via `--all2all-backend` or `all2all_backend` in `ParallelConfig` unless noted otherwise.
- All backends except `flashinfer` only work with EP+DP or EP+TP; `flashinfer` can work with EP or DP without EP.

| Backend | Output act. format | Quant. types | Quant. format | Async | Apply weight on input | Subclass |
| ------- | ------------------ | ------------ | ------------- | ----- | --------------------- | -------- |
| naive | standard | all: mxfp4, nvfp4, int4, int8, fp8 | G, A, T | N | depends on experts implementation | `MoERunner` no-op dispatcher; not selectable via env; for testing/adapting experts to `fused_experts` API |
| deepep_high_throughput | standard | fp8 | G(128), A, T; A/T quantized after dispatch | Y | Y | `DeepEPHTPrepareAndFinalize` |
| deepep_low_latency | batched | fp8 | G(128), A, T; all quantized after dispatch | Y | Y | `DeepEPLLPrepareAndFinalize` |
| flashinfer_nvlink_two_sided | standard | nvfp4, fp8 | G, A, T | N | N | `FlashInferNVLinkTwoSidedPrepareAndFinalize` |
| flashinfer_nvlink_one_sided | standard | nvfp4, bf16, mxfp8, fp8 | G, A, T | N | N | `FlashInferNVLinkOneSidedPrepareAndFinalize` |

Quantization-format key: G grouped, G(N) grouped with block size N, A per-activation-token, T per-tensor[^moe-kernel-features].

Modular kernels are supported by these `FusedMoEMethodBase` classes[^moe-kernel-features]:

- `ModelOptFp8MoEMethod`
- `Fp8MoEMethod`
- `CompressedTensorsW4A4Nvfp4MoEMethod`
- `CompressedTensorsW8A8Fp8MoEMethod`
- `GptOssMxfp4MoEMethod`
- `UnquantizedFusedMoEMethod`

## Fused experts kernels

Most experts kernels follow the base Triton `fused_experts` API, and most include a modular `FusedMoEExpertsModular` adapter[^moe-kernel-features].

Contract details[^moe-kernel-features]:

- Each kernel requires a supported input activation format; some flavors expose both formats via separate entry points, e.g. `TritonExperts` and `BatchedTritonExperts`.
- Batched-format kernels are currently only needed to match certain All2All backends, e.g. `DeepEPLLPrepareAndFinalize`.
- Non-modular experts receive original-type activations and quantize internally; modular experts expect already-quantized activations; both yield outputs in the original activation type.
- Compatibility with a prepare/finalize subclass requires matching activation format, quantization type, and quantization format.
- The Apply-weight-on-input column below applies to non-modular experts; modular-kernel behavior is handled by the prepare/finalize side.

| Kernel | Input act. format | Quant. types | Quant. format | Activation function | Apply weight on input | Modular | Source |
| ------ | ----------------- | ------------ | ------------- | ------------------- | --------------------- | ------- | ------ |
| triton | standard | all: mxfp4, nvfp4, int4, int8, fp8 | G, A, T | silu, gelu, swigluoai, silu_no_mul, gelu_no_mul | Y | Y | `fused_experts`, `TritonExperts` |
| triton (batched) | batched | all | G, A, T | silu, gelu | only handled/supported with modular kernels | Y | `BatchedTritonExperts` |
| deep gemm | standard, batched | fp8 | G(128), A, T | silu, gelu | only handled/supported with modular kernels | Y | `DeepGemmExperts`, `BatchedDeepGemmExperts` |
| cutlass_fp4 | standard, batched | nvfp4 | A, T | silu | Y | Y | `CutlassExpertsFp4` |
| cutlass_fp8 | standard, batched | fp8 | A, T | silu, gelu | Y | Y | `CutlassExpertsFp8`, `CutlasBatchedExpertsFp8` |
| flashinfer | standard | nvfp4, fp8 | T | `activation` ignored, SwiGLU by default | N | Y | `FlashInferExperts` |
| gpt oss triton | standard | N/A | N/A | `activation` ignored, SwiGLU by default | Y | Y | `triton_kernel_fused_experts`, `OAITritonExperts` |
| marlin | standard, batched | uint4, uint8, fp8, fp4 / N/A | corresponding / N/A | silu, swigluoai | Y | Y | `fused_marlin_moe`, `MarlinExperts`, `BatchedMarlinExperts` |
| trtllm | standard | mxfp4, nvfp4 | G(16), G(32) | `activation` ignored, SwiGLU by default | N | Y | `TrtLlmMxfp4ExpertsMonolithic`, `TrtLlmMxfp4ExpertsModular`, `TrtLlmNvFp4ExpertsMonolithic`, `TrtLlmNvfp4ExpertsModular` |
| hpc | standard | fp8 | G(128), T | silu | Y | Y | `HPCExperts` |
| rocm aiter moe | standard | mxfp4, fp8 | G(32), G(128), A, T | silu, gelu, swigluoai | Y | N | `rocm_aiter_fused_experts`, `AiterExperts` |
| cpu_moe | standard | N/A | N/A | silu, gelu, gelu_tanh, swigluoai | Y | N | `X86CPUUnquantizedExperts`, `ArmCPUUnquantizedExperts`, `CPUUnquantizedExperts` |
| naive batched | batched | int8, fp8 | G, A, T | silu, gelu | only handled/supported with modular kernels | Y | `NaiveBatchedExperts`; naive batched implementation mainly for testing |

The source also notes a dispatcher wrapper around triton and deep-gemm experts that selects by type, shape, and quantization params[^moe-kernel-features].

## Modular kernel families

Tested combinations intended to work together[^moe-kernel-features]:

| Backend | `FusedMoEPrepareAndFinalizeModular` | Compatible `FusedMoEExpertsModular` |
| ------- | ----------------------------------- | ----------------------------------- |
| deepep_high_throughput | `DeepEPHTPrepareAndFinalize` | `DeepGemmExperts`, `TritonExperts`, `TritonOrDeepGemmExperts`, `CutlassExpertsFp8`, `MarlinExperts` |
| deepep_low_latency | `DeepEPLLPrepareAndFinalize` | `BatchedDeepGemmExperts`, `BatchedTritonExperts`, `CutlassBatchedExpertsFp8`, `BatchedMarlinExperts` |
| flashinfer | `FlashInferCutlassMoEPrepareAndFinalize` | `FlashInferExperts` |

Some untested combinations may work but are not guaranteed, e.g. flashinfer with other fp8 experts[^moe-kernel-features].

## Coverage limits

- Architecture, lifecycle, and extension workflow are compiled in [vLLM Fused MoE Modular Kernel](vllm-fused-moe-modular-kernel.md); standard versus batched activation shapes and prepare/finalize type details there complement the selection tables here[^moe-kernel-features].
- MkDocs API cross-links in the source tables were reduced to class/function names; exact module paths remain in raw evidence[^moe-kernel-features].

## Relationships

- Uses [vLLM Fused MoE Modular Kernel](vllm-fused-moe-modular-kernel.md) — modular kernel architecture, prepare/finalize plus experts lifecycle, and extension workflow behind the selection tables here.
- Depends on [vLLM Model Runner V2](vllm-model-runner-v2.md) — model execution context that invokes MoE layers; MoE kernel choice affects expert-parallel execution path.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — parallel backend-selection problem: attention selects kernels by hardware/dtype constraints while MoE selects prepare/finalize plus experts by format/quantization compatibility.

[^moe-kernel-features]: Fused MoE Kernel Features — `../raw/vllm/design/moe_kernel_features.md`.
