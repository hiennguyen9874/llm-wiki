---
type: Concept
title: NVFP4 Format and Scale-Dependent Accuracy
description: NVIDIA NVFP4 hierarchical FP4 format with Blackwell acceleration and Red Hat scale-dependent BF16 accuracy-recovery evidence.
tags: [nvfp4, quantization, blackwell, accuracy, llm-compressor, vllm]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: redhat-nvfp4
    resource: ../raw/accelerating-large-language-models-nvfp4-quantization/index.md
    title: Accelerating large language models with NVFP4 quantization
---

NVFP4 is NVIDIA's 4-bit floating-point inference format that pairs compact FP4 storage with hierarchical high-precision scaling, and Red Hat's multi-model release shows BF16 accuracy recovery improving with scale — near-parity above ~70B and on MoE models, more variable at 7–14B[^redhat-nvfp4].

## Format

- FP4 values are stored as discrete codes in small groups of 16, each scaled by an FP8 group scale, with an additional FP32 tensor-level global scale capturing global magnitude[^redhat-nvfp4].
- Per-group scaling preserves local structure while the FP32 global scale restores dynamic range otherwise constrained by the more limited FP8 (E4M3) local scaling; together they retain more signal than integer quantization on wide weight distributions and handle outliers better[^redhat-nvfp4].
- Native FP4 tensor cores on NVIDIA Blackwell (B200) GPUs provide hardware-accelerated FP4 compute[^redhat-nvfp4].

## Storage effect

- Reported effective weight storage is roughly 1.5–1.8x smaller than FP8 and ~3x smaller than FP16, enabling higher batch sizes and concurrency[^redhat-nvfp4].
- On Qwen3-235B-A22B the source reports ~3.3x reduction versus BF16 and ~1.5–1.8x versus FP8-dynamic[^redhat-nvfp4].
- On Llama-4-Maverick-17B-128E-Instruct, INT4 (W4A16) has the smallest raw footprint while NVFP4 trades a slightly larger footprint for floating-point semantics and numerical robustness[^redhat-nvfp4].

## Release and toolchain

- Red Hat released NVFP4-quantized open models from 8B to 400B+ parameters covering large dense and MoE architectures, including instruction-tuned and reasoning variants, quantized with current NVFP4 support in LLM Compressor and deployable with vLLM[^redhat-nvfp4].
- Checkpoints are hosted in the RedHatAI NVFP4 Hugging Face collection and updated as architectures, tooling, and backends expand[^redhat-nvfp4].

## Scale-dependent accuracy recovery

Source-reported recovery bands versus BF16 baselines[^redhat-nvfp4]:

| Scale | Reported recovery |
| --- | --- |
| Large 70B–235B | ~99% |
| Mid-size ~30B | 97–99% |
| 7B–14B | ~95–98%, with larger degradation on Llama-3.1-8B; Qwen-8B and Qwen-14B near ~98% |
| MoE (Llama-4 Scout and Maverick, Qwen3-235B-A22B) | Exceptionally robust, large dense and MoE exceeding 99% |

Per-model average recovery aggregated across OpenLLMv1, OpenLLMv2, and HumanEval, as read from the release chart[^redhat-nvfp4]:

| Model | Avg. recovery vs BF16 |
| --- | ---: |
| Llama-3.1-8B | 97.14% |
| Llama-3.1-70B | 98.52% |
| Llama-3.3-70B | 97.17% |
| Llama-4-Scout | 99.63% |
| Llama-4-Maverick | 99.10% |
| Qwen3-8B | 98.45% |
| Qwen3-14B | 98.30% |
| Qwen3-32B | 99.30% |
| Mistral-Small-3.2-24B-Instruct | 98.58% |
| Qwen3-30B-A3B | 96.12% |
| Qwen3-235B-A22B-Instruct-2507 | 100.04% |

Qwen3-235B-A22B task detail (BF16 vs NVFP4), showing near-parity within ~1pp on most tasks but larger gaps on MATH 500 and GPQA Diamond[^redhat-nvfp4]:

| Benchmark | BF16 | NVFP4 |
| --- | ---: | ---: |
| ARC Challenge | 72.78% | 72.27% |
| MMLU | 87.48% | 87.08% |
| MMLU Pro | 63.51% | 63.33% |
| IFEval | 90.17% | 91.01% |
| MATH 500 | 94.20% | 89.20% |
| GPQA Diamond | 69.19% | 64.65% |
| HumanEval | 96.67% | 96.46% |

Capability splits add nuance: HumanEval code generation stays within ~1–2pp of BF16 for most models, with larger gaps on Llama-3.3-70B (88.69% vs 84.77%) and Qwen3-30B-A3B (93.62% vs 91.13%), while a few small cases slightly exceed BF16 (Llama-3.1-70B, Llama-4-Scout, Qwen3-32B)[^redhat-nvfp4]. MMLU shows wider small-model gaps, largest on Llama-3.1-8B (69.37% vs 65.95%, −3.42pp), versus sub-1pp gaps on Qwen3-235B-A22B (87.46% vs 87.08%) and Qwen3-32B (81.84% vs 81.23%)[^redhat-nvfp4].

## Calibration guidance

- Larger models achieved strong, stable recovery with the standard straightforward NVFP4 workflow; extra tuning was applied only on clear empirical benefit, keeping the simplest configuration that met accuracy targets[^redhat-nvfp4].
- For a subset of 8B–14B models the authors explored MSE-based calibration observers and SmoothQuant, which is fully compatible with NVFP4, with mixed results — modest gains on some models, similar or better results without them on others — so small-scale deployment may need model-specific tuning rather than one recipe[^redhat-nvfp4].

## Limits

- This source covers accuracy recovery only; throughput and latency analysis is explicitly deferred to a follow-up performance blog, so do not cite this release for speed claims[^redhat-nvfp4].
- All deltas are source-reported chart and prose values, not independently reproduced; benchmark harnesses and calibration details beyond the observers/SmoothQuant note are not specified in the inspected text[^redhat-nvfp4].

## Relationships

- Uses [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — complementary NVFP4 rationale (block-16 versus MXFP4 block-32, E4M3 versus E8M0 scales) and Blackwell serving context for this format-level evidence.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — format-selection and hardware-target context for deploying NVFP4 checkpoints.
- Uses [vLLM LLM Compressor Quantization Workflows](vllm-llm-compressor-workflows.md) — offline calibration and compressed-tensors export context behind the LLM Compressor NVFP4 recipe used here.
- Uses [SGLang Quantization](sglang-quantization.md) — adjacent ModelOpt FP4 offline-quantization path for Blackwell deployment.
- Uses [vLLM b12x Quantized Linear and MoE Backends](vllm-b12x-quantization-backends.md) — SM120/SM121 kernel context for NVFP4-class execution on Blackwell-class GPUs.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — single-task accuracy recovery here should be complemented with distribution-level and leakage-controlled checks before treating parity as fidelity.

## Coverage limits

- All six release figures were visually inspected and cross-checked against the prose; numeric chart values above are read from rendered labels and carry chart-reading precision limits.
- Remote Hugging Face collection, LLM Compressor and vLLM repositories, and the promised performance follow-up were not inspected.

[^redhat-nvfp4]: Shubhra Pandit, “Accelerating large language models with NVFP4 quantization,” Red Hat Developer, 2026-02-04 — `../raw/accelerating-large-language-models-nvfp4-quantization/index.md` plus `assets/Figure1_0.png.webp`, `assets/Figure2_0.png.webp`, `assets/Figure3.png.webp`, `assets/Figure4_0.png.webp`, `assets/Figure5_0.png.webp`, and `assets/Figure6_0.png.webp`; NVFP4 hierarchical format, Blackwell FP4 compute, storage ratios, LLM Compressor plus vLLM release scope, scale-dependent recovery bands and chart values, and calibration guidance.
