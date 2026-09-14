---
type: Concept
title: vLLM LLM Compressor Quantization Workflows
description: Offline FP8, INT4 W4A16, INT8 W4A8, and INT8 W8A8 recipes that export compressed-tensors checkpoints for vLLM.
tags: [vllm, quantization, llm-compressor, calibration]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:42:43Z }
sources:
  - id: compressor-overview
    resource: ../raw/vllm/features/quantization/llm_compressor/README.md
    title: LLM Compressor
  - id: compressor-fp8
    resource: ../raw/vllm/features/quantization/llm_compressor/fp8.md
    title: FP8 W8A8
  - id: compressor-int4
    resource: ../raw/vllm/features/quantization/llm_compressor/int4.md
    title: INT4 W4A16
  - id: compressor-w4a8
    resource: ../raw/vllm/features/quantization/llm_compressor/int8_w4a8.md
    title: INT8 W4A8
  - id: compressor-w8a8
    resource: ../raw/vllm/features/quantization/llm_compressor/int8_w8a8.md
    title: INT8 W8A8
---

LLM Compressor applies one-shot quantization and calibration recipes to Hugging Face models, exports compressed-tensors checkpoints, and leaves serving and evaluation to vLLM. It supports AWQ, GPTQ, AutoRound, RTN, transformed and mixed-precision methods across FP4/FP8/INT8/INT4, including KV-cache and attention quantization[^compressor-overview].

## Recipe choice

| Recipe | Quantization and calibration | Documented deployment fit |
| --- | --- | --- |
| FP8 `FP8_DYNAMIC` | Static per-channel FP8 weights plus dynamic per-token activations; RTN requires no calibration data[^compressor-fp8] | W8A8 compute on NVIDIA Ada/Hopper/Blackwell and AMD MI300X; Turing/Ampere run weight-only W8A16 via Marlin. Source reports about 2× model-memory reduction and up to 1.6× throughput, workload-dependent[^compressor-fp8]. |
| INT4 `W4A16` | GPTQ-calibrated 4-bit grouped weights, 16-bit activations; typical group size 128[^compressor-int4] | Memory savings and low-latency, low-QPS workloads; documented for NVIDIA compute capability above 8.0[^compressor-int4]. |
| INT8 `W4A8` | GPTQ-calibrated INT4 weights with dynamic per-token INT8 activations; groupwise favors accuracy, channelwise favors inference speed[^compressor-w4a8] | Documented acceleration through KleidiAI on Arm CPUs[^compressor-w4a8]. |
| INT8 `W8A8` | SmoothQuant followed by GPTQ; INT8 weights and activations[^compressor-w8a8] | NVIDIA Turing through Hopper; explicitly not supported on Blackwell compute capability 10.0+, where FP8 is recommended[^compressor-w8a8]. |

## Common offline workflow

1. Install `llmcompressor` for checkpoint production, and use a separate environment for vLLM plus `lm-eval` because the packages may conflict[^compressor-fp8][^compressor-int4].
2. Load the Hugging Face model and tokenizer. For calibrated recipes, construct representative tokenized data using the deployed chat/instruction template[^compressor-int4][^compressor-w4a8][^compressor-w8a8].
3. Build a `QuantizationModifier` or `GPTQModifier` recipe, normally targeting `Linear` and ignoring `lm_head`; W8A8 adds `SmoothQuantModifier` first[^compressor-fp8][^compressor-int4][^compressor-w8a8].
4. Run `oneshot`, then save the model and tokenizer; calibrated integer examples use `save_compressed=True`[^compressor-int4][^compressor-w4a8][^compressor-w8a8].
5. Load the exported directory with `LLM(path)` and compare task accuracy with `lm_eval` before deployment[^compressor-fp8][^compressor-int4].

## Calibration and evaluation guidance

- Start calibrated integer recipes around 512 representative samples and sequence length 2048, increasing or tuning when accuracy drops. Prefer deployment-like or fine-tuning data and the model's own template[^compressor-int4][^compressor-w4a8][^compressor-w8a8].
- INT4 GPTQ exposes accuracy/stability controls such as `dampening_frac` and `actorder`; lower dampening may improve accuracy but can become numerically unstable, while weight activation ordering can improve accuracy without added serving latency[^compressor-int4].
- Quantized evaluations can be sensitive to beginning-of-sequence handling; the examples pass `add_bos_token=True` to `lm_eval`[^compressor-fp8][^compressor-int4][^compressor-w4a8][^compressor-w8a8].
- FP8 E4M3 trades range for precision relative to E5M2: E4M3 reaches approximately ±448, while E5M2 reaches approximately ±57344 and supports infinities[^compressor-fp8].

## Runtime kernel selection

For FP8 linear layers, vLLM selects a compatible GEMM at load time and logs it. The documented CUDA order for block-quantized checkpoints includes a FlashInfer/DeepGEMM hybrid, DeepGEMM, CUTLASS, Marlin, Triton, Humming, then PyTorch fallback; older GPUs use W8A16 Marlin. `--linear-backend` and `--moe-backend` control distinct layer families, and an explicitly incompatible backend raises an error[^compressor-fp8].

## Relationships

- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — broader method, plugin, and hardware selection context.
- Produces input for [vLLM Entrypoints](vllm-entrypoints.md) — exported checkpoints load through `LLM` or serving interfaces.
- Calibrates [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md) — LLM Compressor provides the recommended dataset-based KV scale pathway.
- Contrasts with [vLLM Online Quantization](vllm-online-quantization.md) — online conversion avoids checkpoint export and calibration.

## Coverage limits

The linked example repositories, checkpoint collections, accuracy baselines, kernel implementations, and hardware benchmark methodology were not independently inspected. Performance figures are source-reported and not reproduced here.

[^compressor-overview]: LLM Compressor — `../raw/vllm/features/quantization/llm_compressor/README.md`.
[^compressor-fp8]: FP8 W8A8 — `../raw/vllm/features/quantization/llm_compressor/fp8.md`.
[^compressor-int4]: INT4 W4A16 — `../raw/vllm/features/quantization/llm_compressor/int4.md`.
[^compressor-w4a8]: INT8 W4A8 — `../raw/vllm/features/quantization/llm_compressor/int8_w4a8.md`.
[^compressor-w8a8]: INT8 W8A8 — `../raw/vllm/features/quantization/llm_compressor/int8_w8a8.md`.
