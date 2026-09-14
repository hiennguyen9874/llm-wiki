---
type: Concept
title: vLLM Online Quantization
description: Load-time quantization of linear and MoE weights with global, per-layer, mixed-format, and exclusion controls.
tags: [vllm, quantization, online-quantization, moe]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:42:43Z }
sources:
  - id: online-quant
    resource: ../raw/vllm/features/quantization/online.md
    title: Online Quantization
---

vLLM online quantization converts BF16/FP16 linear and MoE weights while loading a model and dynamically scales activations during forward passes, avoiding a pre-quantized checkpoint, calibration dataset, export step, and duplicate on-disk model[^online-quant].

## Built-in schemes

| Shorthand | Weight format | Activation behavior |
| --- | --- | --- |
| `fp8_per_tensor` | FP8 E4M3 with FP32 scale per tensor | FP8 E4M3 per tensor; some Ada/Hopper linear paths use per-token scaling for performance. |
| `fp8_per_block` | FP8 E4M3 with FP32 scale per 128×128 block | FP8 E4M3 with scale per 1×128 block. |
| `mxfp8` | FP8 E4M3 with E8M0 scale per 1×32 block | Same; W8A8 requires SM100+, while older GPUs use W8A16 fallback. |
| `mxfp4` | FP4 E2M1 with E8M0 scale per 1×32 block | Linear activation dtype depends on the selected backend and may be FP4 or BF16; MoE uses MXFP4 activation quantization. |

Enable with `LLM(model, quantization="<scheme>")` or `vllm serve <model> --quantization <scheme>`[^online-quant].

## Configuration model

`quantization_config` can separately set `linear` and `moe` weight/activation recipes and list `ignore` patterns. Each layer-kind value may be a complete `{weight, activation}` object or a shorthand string; missing fields inherit the top-level shorthand or, for pre-quantized models, checkpoint metadata[^online-quant].

- Use different schemes for dense linear layers and MoE experts by overriding only `linear` or `moe`.
- Existing MXFP4 MoE checkpoints can override activation format, for example `--quantization-config.moe.activation mxfp8`, and combine it with `--moe-backend`.
- Partially quantized checkpoints retain their original quantization method for existing quantized layers while online quantization handles selected unquantized layers.
- `ignore` accepts exact names, `re:` regular expressions, and `fnmatch` patterns; fused layers can match the fused name or all unfused shard names. This exclusion is online-only and does not replace a checkpoint format's own ignore semantics.
- XPU non-block FP8 linear layers default to W8A16; `--linear-backend xpu` or `torch` forces W8A8, while `xpu_woq` explicitly selects W8A16[^online-quant].

## Per-layer targets

With `quantization="online"`, `targets` maps exact, `re:`, or `fnmatch` layer patterns to shorthands such as `fp8_per_tensor`, `fp8_per_block`, `fp8_per_channel`, `mxfp8`, `int8_per_channel_weight_only`, or `nvfp4_per_token`[^online-quant].

Rules are strict:

- `targets` is mutually exclusive with online `linear` and `moe` settings.
- Unmatched layers remain at checkpoint dtype.
- A layer matching both `targets` and `ignore`, or multiple target patterns, raises an error.
- `fnmatch` matching is specific to online quantization and is not applied to Quark or compressed-tensors checkpoint configuration.

## Tradeoffs

Online conversion is operationally useful for rapid scheme experiments, avoiding extra storage, and adding quantization to unquantized portions of a checkpoint. Because it has no calibration/export pass and scales activations dynamically, it lacks the accuracy-recovery opportunities of offline GPTQ/AWQ/rotation/SmoothQuant workflows and can pay recurring dynamic-scaling overhead[^online-quant].

## Relationships

- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — format and hardware context.
- Contrasts with [vLLM LLM Compressor Quantization Workflows](vllm-llm-compressor-workflows.md) — calibrated, exported compressed-tensors checkpoints.
- Uses [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — effective MoE support depends on selected weight and activation formats.

## Coverage limits

The source points to `QUANT_KEY_NAMES` and backend implementation details in a live vLLM checkout; these registries were not present in the supplied directory and were not independently inspected.

[^online-quant]: Online Quantization — `../raw/vllm/features/quantization/online.md`.
