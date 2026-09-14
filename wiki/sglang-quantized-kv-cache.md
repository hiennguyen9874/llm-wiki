---
type: Concept
title: SGLang Quantized KV Cache
description: FP8 E4M3/E5M2 and experimental FP4 E2M1 KV-cache quantization for SGLang covering formats, scaling factors, memory savings, accuracy, and backend constraints.
tags: [sglang, kv-cache, quantization, fp8, fp4]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-kvquant
    resource: ../raw/sglang/advanced_features/quantized_kv_cache.mdx
    title: Quantized KV Cache
---

SGLang quantized KV cache stores key-value pairs in FP8 or experimental FP4 instead of BF16 to cache more tokens and raise throughput, with backend-fused dequantization required and format-dependent accuracy trade-offs[^sgl-kvquant].

## Purpose

During autoregressive generation LLMs cache previously computed key-value pairs to avoid redundant calculation; that cache dominates GPU memory for long sequences[^sgl-kvquant].

Quantized KV cache is primarily a memory optimization that benefits throughput by allowing more cached tokens or longer context within the same budget, with possible minimal accuracy degradation depending on format[^sgl-kvquant].

> **Performance warning:** when quantized KV cache must be dequantized before attention, unfused dequantization can be extremely slow and negate memory benefits. Always verify the chosen attention backend supports quantized KV cache[^sgl-kvquant].

## Supported formats

### FP8

Per OCP, SGLang supports two 8-bit floating-point formats[^sgl-kvquant]:

- **E5M2** — 5 exponent bits, 2 mantissa bits; larger dynamic range (±57344.0), lower precision.
- **E4M3** — 4 exponent bits, 3 mantissa bits; higher precision, smaller dynamic range (±240.0).

### FP4

FP4 quantization is currently experimental[^sgl-kvquant].

Per OCP MXFP4 microscaling, SGLang supports **E2M1** — 1 sign bit, 2 exponent bits, 1 mantissa bit — where tensors are divided into blocks sharing one 8-bit exponential scaling factor. OCP specifies blocks of 32 elements; SGLang currently uses blocks of 16 elements for KV cache[^sgl-kvquant].

## Usage

Enable with `--kv-cache-dtype` when launching the server[^sgl-kvquant]:

```bash
# FP8 E5M2
python3 -m sglang.launch_server \
    --model-path deepseek-ai/DeepSeek-R1-0528 \
    --kv-cache-dtype fp8_e5m2

# FP8 E4M3
python3 -m sglang.launch_server \
    --model-path deepseek-ai/DeepSeek-R1-0528 \
    --kv-cache-dtype fp8_e4m3

# FP4 E2M1
python3 -m sglang.launch_server \
    --model-path nvidia/DeepSeek-R1-0528-NVFP4 \
    --kv-cache-dtype fp4_e2m1
```

## Scaling factors

### FP8

FP8 requires scaling factors for quantize/dequantize; currently only per-tensor scalar factors are supported[^sgl-kvquant].

Sources:

- **Loaded from checkpoint:** pre-quantized models such as ModelOpt may include `k_scale` and `v_scale`, loaded automatically[^sgl-kvquant].
- **Provided via JSON:** supply with `--quantization-param-path` in this shape, where outer keys are tensor-parallel ranks and inner keys are layer indices[^sgl-kvquant]:

```json
{
  "kv_cache": {
    "dtype": "float8_e4m3fn",
    "scaling_factor": {
      "0": {
        "0": 1.0,
        "1": 1.0
      }
    }
  }
}
```

If factors are neither provided nor found in the checkpoint, they default to `1.0`, which may cause accuracy issues[^sgl-kvquant].

### FP4

Unlike FP8, FP4 MXFP4 computes block-based scaling factors automatically on the fly during quantization and dequantization; no pre-quantized model or external scaling-factor file is required[^sgl-kvquant].

## Memory savings

Quantized cache enables longer contexts or more concurrent requests in the same memory budget[^sgl-kvquant].

- **BF16 → FP4:** approximately 3.56× more tokens than BF16 after accounting for scaling-factor overhead[^sgl-kvquant].
- **FP4 versus FP8:** FP4 with block size 16 supports approximately 1.78× more tokens than FP8; the FP8/BF16 ratio can be derived from these two ratios[^sgl-kvquant].

FP4 and FP8 both need extra memory for block-based scaling factors, so effective savings are smaller than raw bit-width reduction alone[^sgl-kvquant].

## Accuracy impact

### FP8

FP8 E4M3 typically introduces minimal degradation; impact depends on model architecture, sequence length, and format, with E4M3 generally more accurate than E5M2[^sgl-kvquant].

### FP4

FP4 gives large memory savings with workload-dependent accuracy impact. Preliminary results from SGLang PR #10078 for MLA and PR #12612 for MHA[^sgl-kvquant]:

**Large models — Qwen3-235B-A22B and DeepSeek-R1-0528** — FP4 stays close to FP8/BF16 on simpler datasets, with larger gaps on harder reasoning sets. Columns are KV16 baseline, KV8 FP8 E4M3, KV4 FP4 E2M1[^sgl-kvquant]:

| Model | Dataset | KV16 | KV8 | KV4 |
|---|---|---:|---:|---:|
| Qwen3-235B-A22B | gsm8k | 0.9168 | 0.9181 | 0.9186 |
| Qwen3-235B-A22B | aime25 | 0.7733 | 0.7333 | 0.6000 |
| Qwen3-235B-A22B | gpqa_diamond | 0.7010 | 0.6899 | 0.6778 |
| DeepSeek-R1-0528 | gsm8k | 0.9157 | 0.9154 | 0.9124 |
| DeepSeek-R1-0528 | aime25 | 0.5067 | 0.4934 | 0.4000 |
| DeepSeek-R1-0528 | gpqa_diamond | 0.7707 | 0.7697 | 0.7273 |

**Smaller model — GPT-OSS-120B** — FP4 shows more pronounced drops on challenging datasets[^sgl-kvquant]:

| Model | Dataset | KV16 | KV8 | KV4 |
|---|---|---:|---:|---:|
| GPT-OSS-120B | gsm8k | 0.9161 | 0.9163 | 0.9152 |
| GPT-OSS-120B | aime25 | 0.7533 | 0.7667 | 0.3533 |
| GPT-OSS-120B | gpqa_diamond | 0.5081 | 0.5434 | 0.3202 |

Key observations[^sgl-kvquant]:

- Simple datasets such as `gsm8k` keep FP4 accuracy close to FP8/BF16 across model sizes.
- Model size matters: 200B+ models generally tolerate FP4 better than smaller models.
- Long context may amplify degradation as quantization error accumulates.
- Evaluate FP4 on the specific model and workload; smaller models or complex reasoning may need FP8 or BF16.

## Best practices

- Prefer pre-quantized models with scaling factors already in the checkpoint[^sgl-kvquant].
- Choose `fp8_e4m3` for better accuracy as the recommended default, `fp8_e5m2` for larger dynamic range, or experimental `fp4_e2m1` for maximum memory savings[^sgl-kvquant].
- Verify attention-backend compatibility before enabling quantized KV cache[^sgl-kvquant].

## Relationships

- Uses [SGLang Attention Backends](sglang-attention-backends.md) — backend must provide fused quantized-KV support; MHA/MLA matrices record per-backend FP8/FP4 KV coverage.
- Uses [SGLang Quantization](sglang-quantization.md) — weight-quantization counterpart covering offline pre-quantized and online dynamic flows including ModelOpt FP8/FP4.
- Uses [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md) — vLLM analogue with FP8 formats, LLM Compressor calibration, and selective layer skips.
- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — advanced-features map whose listed Quantization area and unlisted-source note cover this feature.

## Coverage limits

- OCP specifications, linked SGLang PRs #10078 and #12612, and the `attention_backend`, `quantization`, and `server_arguments` linked pages were not independently inspected beyond this source[^sgl-kvquant].
- Accuracy numbers reflect the source snapshot for the listed models and datasets and may not generalize to other models, long-context workloads, or future kernels[^sgl-kvquant].

[^sgl-kvquant]: Quantized KV Cache — `../raw/sglang/advanced_features/quantized_kv_cache.mdx`.
