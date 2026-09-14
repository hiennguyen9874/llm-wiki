---
type: Concept
title: vLLM b12x Quantized Linear and MoE Backends
description: Optional SM120/SM121 linear and MoE kernels for FP8, MXFP8, NVFP4, and MXFP4 model configurations.
tags: [vllm, quantization, b12x, blackwell, moe]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:42:43Z }
sources:
  - id: b12x-quant
    resource: ../raw/vllm/features/quantization/b12x.md
    title: b12x Linear and MoE Backends
---

b12x supplies optional CUDA linear and MoE kernels for NVIDIA SM120/SM121 GPUs. After installing `vllm[b12x]`, its linear kernels participate in automatic selection after established optimized backends and before emulation, or can be pinned independently with `--linear-backend b12x` and `--moe-backend b12x`[^b12x-quant].

## Supported configurations

- Linear: per-tensor FP8, 128×128 block FP8, MXFP8, NVFP4, and MXFP4.
- MoE: tensor-parallel MXFP4 weights with BF16 or MXFP8 activations; NVFP4 weights with BF16, NVFP4, or MXFP8 activations.
- MXFP4 MoE defaults to MXFP8 activations, with BF16 fallback when the A8 path does not support the model configuration. NVFP4 MoE uses the checkpoint's activation format.
- `VLLM_B12X_MOE_FP4_FORCE_A16=1` forces BF16 activations for either FP4 weight format[^b12x-quant].

Only pin the MoE backend for a compatible NVFP4/MXFP4 MoE model. Dense W4A16 layers remain on another compatible backend such as Marlin, and b12x MoE does not support expert parallelism, expert maps, EXL3, or NF3[^b12x-quant].

## Relationships

- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — broader checkpoint-format and backend-selection context.
- Uses [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — expert kernels must match activation and quantization formats.
- Related to [vLLM Attention Backends](vllm-attention-backends.md) — b12x also has a separately selected attention backend for the same GPU family.

## Coverage limits

The b12x package implementation, exact automatic priority registry, and performance characteristics were not independently inspected.

[^b12x-quant]: b12x Linear and MoE Backends — `../raw/vllm/features/quantization/b12x.md`.
