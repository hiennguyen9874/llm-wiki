---
type: Concept
title: vLLM Quantized KV Cache
description: FP8 KV-cache formats, calibration strategies, selective layer skips, and attention-backend constraints.
tags: [vllm, quantization, kv-cache, fp8, attention]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:42:43Z }
sources:
  - id: quantized-kv
    resource: ../raw/vllm/features/quantization/quantized_kvcache.md
    title: Quantized KV Cache
---

FP8 KV-cache storage reduces per-token cache memory, allowing more cached tokens, higher throughput, or longer contexts, but accuracy depends on scale choice and backend support. FlashAttention 3 also executes attention in FP8 when the KV cache is FP8, quantizing queries as well as keys and values[^quantized-kv].

## Formats and scaling

- Per-tensor quantization uses one independent scale for each Q, K, and V tensor.
- Per-attention-head quantization uses one Q scale per query head and one K/V scale per KV head; it currently requires FlashAttention and LLM Compressor calibration.
- `kv_cache_dtype="auto"` retains the model default, `fp8_e4m3` is documented for CUDA 11.8+ and ROCm, and `fp8_e5m2` for CUDA 11.8+[^quantized-kv].

## Calibration choices

The simplest configuration, `kv_cache_dtype="fp8"`, uses scales of `1.0`. The recommended accuracy-oriented path calibrates on a representative dataset with LLM Compressor, using a `QuantizationModifier` whose attention input activations produce Q scales and whose `kv_cache_scheme` produces K/V scales[^quantized-kv].

The documented example uses 512 shuffled chat samples at sequence length 2048, then saves a compressed checkpoint. These values are starting points rather than universal optima; dataset and sequence distribution should represent deployment traffic[^quantized-kv].

## Selective layer exceptions

`--kv-cache-dtype-skip-layers` or `kv_cache_dtype_skip_layers` leaves sensitive layers in model-native dtype while quantizing the rest. It accepts layer indices or layer-type names such as `sliding_window`, enabling hybrid cache precision where sliding-window attention is more sensitive[^quantized-kv].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — per-head scales and FP8 attention behavior are backend-dependent.
- Uses [vLLM LLM Compressor Quantization Workflows](vllm-llm-compressor-workflows.md) — supplies the recommended dataset calibration pathway.
- Uses [vLLM Hybrid KV Cache Manager](vllm-hybrid-kv-cache-manager.md) — selective native/FP8 layer dtypes interact with heterogeneous attention-layer cache organization.
- Used by [vLLM NIXL Connector Compatibility](vllm-nixl-connector-compatibility.md) — disaggregated prefill/decode requires matching cache dtypes and supports static, not runtime-dynamic, transferred scales.

## Coverage limits

The source does not provide a complete backend-by-format matrix or quantified end-to-end memory, throughput, and accuracy results. The linked LLM Compressor examples and attention implementations were not independently inspected.

[^quantized-kv]: Quantized KV Cache — `../raw/vllm/features/quantization/quantized_kvcache.md`.
