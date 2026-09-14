---
type: Concept
title: SGLang Cleaner Quantization Stack
description: Scheme-based Config-Method-Scheme-Kernel refactor separating checkpoint format handling from hardware kernel execution.
tags: [sglang, quantization, architecture, ascend]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: cleaner-quant-stack
    resource: ../raw/2026-07-31-cleaner-quantization-stack/index.md
    title: "Toward a Cleaner Quantization Stack in SGLang"
---

SGLang is refactoring its quantization path into `Config -> Method -> Scheme -> Kernel` so checkpoint-format logic and hardware-backend logic can evolve independently, with multiple formats reusing the same kernel[^cleaner-quant-stack].

## Why the refactor

Production serving must handle diverse checkpoint formats such as AWQ, GPTQ, Compressed-Tensors, ModelSlim, and Quark; dense and MoE weights; KV-cache formats; attention kernels; and hardware backends across CUDA GPUs, Ascend NPUs, CPUs, and other backends[^cleaner-quant-stack].

In the old design a single quantization method often owned the entire path: defining parameters, loading weights, transforming layouts, selecting a backend, and launching the kernel. Supporting another platform meant adding more branches to the same format-facing class, even when much of the hardware logic could have been reused elsewhere[^cleaner-quant-stack].

This matters because quantization is central to deployment scale and serving performance. Lower-bit weights can reduce memory traffic in weight-bandwidth-bound workloads, especially during decode, while end-to-end benefit depends on kernel efficiency, quantization overhead, and the prefill/decode mix[^cleaner-quant-stack].

## Four-layer architecture

The refactoring proposed in SGLang issue #15194 divides the path into four focused layers[^cleaner-quant-stack]:

1. **Quant Config:** parses checkpoint metadata and selects the quantization path. Examples include `ModelSlimConfig` and `CompressedTensorsConfig`.
2. **Linear/MoE Method:** adapts the SGLang layer interface and delegates operations. Example: `ModelSlimLinearMethod`.
3. **Scheme:** defines format- and layer-specific parameters, shapes, and loading behavior. Example: `ModelSlimMXFP8Scheme`.
4. **Kernel:** performs backend-specific weight transformations and execution. Example: `NPUMXFP8LinearKernel`.

The key boundary is between schemes and kernels. A scheme describes how a checkpoint maps onto an SGLang layer, while a kernel implements the operations required by a particular backend[^cleaner-quant-stack].

Migration status and responsibilities in the source snapshot:

- SGLang is migrating incrementally. In the cleaned offline path, the scheme owns parameter definitions and weight loading, while the kernel handles post-load transformations and execution[^cleaner-quant-stack].
- The same kernel can also serve online quantization paths as a standalone runner, allowing backend support to be developed and tested independently[^cleaner-quant-stack].
- As migration continues, more backend selection is expected to move into SGLang's platform layer. Schemes can then remain hardware-agnostic while the platform selects a compatible built-in or third-party kernel before execution[^cleaner-quant-stack].

## Reuse and development benefits

- **Smaller, easier-to-review changes:** a new format can add its configuration and scheme without modifying unrelated backend code; a new kernel can be implemented and reviewed before it is connected to a checkpoint format[^cleaner-quant-stack].
- **More focused testing:** format detection, configuration parsing, parameter registration, and loading behavior can be tested on CPU-only machines. Hardware-specific tests can then focus on weight transformations, kernel correctness, and performance[^cleaner-quant-stack].
- **Less duplicated code:** multiple formats reuse the same hardware kernel instead of maintaining separate implementations for equivalent operations[^cleaner-quant-stack].
- **Clearer path beyond linear layers:** the same structure can extend to MoE experts, attention projections, KV caches, and communication operators[^cleaner-quant-stack].

Concrete reuse example from the source: `AWQ MoEMethod` with `AWQMoEAscendScheme`, `CompressedTensors FusedMoEMethod` with `NPUCompressedTensorsScheme`, and `GPTQ MoEMethod` with `GPTQMoEAscendScheme` all share one `WnA16 NPU Kernel` for optimized inference[^cleaner-quant-stack].

## Performance evidence

Reported Qwen3-30B-A3B comparison on Ascend with TP=4, `--device npu`, and `--attention-backend ascend`[^cleaner-quant-stack]:

| Model | Quant Scheme | E2E(s) | TTFT(ms) | ITL(ms) | Accuracy(%) | Weights size(GB) |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen3-30B-A3B | BF16 | 57.12 | 2084.41 | 26.23 | 91.1 | 61.08 |
| Qwen3-30B-A3B | W8A8 | 54.94 | 2553.06 | 24.60 | 90.8 | 31.29 |
| Qwen3-30B-A3B | W4A4_W8A8 | 52.97 | 2299.51 | 23.84 | 89.4 | 21.59 |

Serving measurement used `bench_serving` with 64 prompts, max-concurrency 64, 2048 input and output tokens, and a random dataset derived from `ShareGPT_V3_unfiltered_cleaned_split.json`; accuracy used `benchmark/gsm8k/bench_sglang.py` with 1319 questions[^cleaner-quant-stack].

The table shows lower end-to-end time, lower per-token latency, and much smaller weight size for quantized variants, with small accuracy drops and higher time-to-first-token than the BF16 baseline in this configuration[^cleaner-quant-stack].

Reproduction uses public ModelScope checkpoints for BF16, W8A8, and W4A4 variants, launches with `--mem-fraction-static 0.8` on port 30088, then runs the serving and GSM8K bench commands detailed in the source appendix[^cleaner-quant-stack].

## Future work

Live plan is tracked in SGLang Quantization Roadmap - 2026 H2 (#31783)[^cleaner-quant-stack]:

- **Complete the architecture:** finish the `Config -> Method -> Scheme -> Kernel` refactor, separate offline checkpoint loading from online quantization, standardize post-load weight processing, and add a machine-readable capability registry to validate format, layer, model, and backend compatibility before execution[^cleaner-quant-stack].
- **Expand production coverage:** broaden W8A8, W4A8, W4A4, NVFP4, MXFP4, and MXFP8 support across CUDA, ROCm, Ascend NPU, CPU, and other backends, including MoE, VLM, diffusion, quantized attention, KV cache, communication, and disaggregated KV transfer[^cleaner-quant-stack].
- **Evaluate new low-bit methods:** prototype and compare approaches such as MXFP6, MXINT8, rotation-based quantization, vector quantization, two-bit KV caches, ternary inference, and sparse-plus-low-bit execution[^cleaner-quant-stack].

## Relationships

- Uses [SGLang Quantization](sglang-quantization.md) — this scheme-kernel refactor is the structural evolution of the broader offline pre-quantized and online dynamic quantization landscape.
- Uses [SGLang Native ModelOpt Quantization](sglang-modelopt-quantization.md) — concrete NVFP4, MXFP4, and FP8 quantize-export-deploy path whose formats benefit from shared-kernel reuse.
- Uses [SGLang Quantized KV Cache](sglang-quantized-kv-cache.md) — FP8 and FP4 KV-cache quantization is an explicit extension target beyond linear layers.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — platform-layer backend selection is the intended future home for hardware dispatch, analogous to attention-backend selection.
- Uses [SGLang Expert Parallelism](sglang-expert-parallelism.md) — MoE expert layers are a primary reuse case, with multiple MoE quantization schemes sharing one NPU kernel.

## Coverage limits

- Architecture diagrams were visually inspected; class names and data-flow summaries reflect the source text and diagrams.
- Performance and accuracy numbers are as reported for the listed Ascend TP=4 configuration and were not independently verified.
- Issue numbers #15194 and #31783, roadmap priorities, and contributor lists reflect the July 2026 source snapshot and may change.
- Acknowledgements and community credits were excluded as non-durable operational knowledge.

[^cleaner-quant-stack]: Toward a Cleaner Quantization Stack in SGLang — `../raw/2026-07-31-cleaner-quantization-stack/index.md`.
