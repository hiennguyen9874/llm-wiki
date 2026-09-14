---
type: Concept
title: vLLM Quantization Methods and Toolchains
description: Choosing vLLM quantization formats, offline toolchains, hardware targets, and out-of-tree integrations.
tags: [vllm, quantization, deployment, hardware]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:42:43Z }
sources:
  - id: quantization-overview
    resource: ../raw/vllm/features/quantization/README.md
    title: Quantization
  - id: auto-awq
    resource: ../raw/vllm/features/quantization/auto_awq.md
    title: AutoAWQ
  - id: bitsandbytes
    resource: ../raw/vllm/features/quantization/bnb.md
    title: BitsAndBytes
  - id: gguf
    resource: ../raw/vllm/features/quantization/gguf.md
    title: GGUF
  - id: gptqmodel
    resource: ../raw/vllm/features/quantization/gptqmodel.md
    title: GPTQModel
  - id: intel-quant
    resource: ../raw/vllm/features/quantization/inc.md
    title: Intel Quantization Support
  - id: modelopt
    resource: ../raw/vllm/features/quantization/modelopt.md
    title: NVIDIA Model Optimizer
  - id: quark
    resource: ../raw/vllm/features/quantization/quark.md
    title: AMD Quark
  - id: torchao
    resource: ../raw/vllm/features/quantization/torchao.md
    title: TorchAO
---

vLLM supports multiple checkpoint formats and quantization toolchains rather than one universally best method. Selection depends on target hardware, whether calibration and checkpoint export are acceptable, the desired weight/activation precision, and the maturity of the serving integration; hardware compatibility is explicitly described as changing over time, so deployment should verify the current runtime and kernel registry[^quantization-overview].

## Toolchain selection

| Method | Durable use in vLLM | Important constraints |
| --- | --- | --- |
| AWQ / AutoAWQ | 4-bit weight quantization and existing AWQ checkpoints | AutoAWQ is deprecated; use LLM Compressor's AWQ flow for new work[^auto-awq]. |
| BitsAndBytes | Calibration-free in-flight 4-bit conversion or pre-quantized checkpoints | Requires the out-of-tree `vllm-bnb-plugin`; pre-quantized models are normally inferred from `config.json`, while in-flight conversion uses `quantization="bitsandbytes"`[^bitsandbytes]. |
| GGUF | Memory-reduced local files or Hugging Face `repo_id:quant_type` models | Experimental, under-optimized, potentially incompatible with other features, and now provided by `vllm-gguf-plugin`; use the base-model tokenizer because GGUF tokenizer conversion is slow and unstable[^gguf]. |
| GPTQModel | Calibrated INT4/INT8 checkpoints, including per-module dynamic quantization | Supports optimized Marlin/Machete execution on NVIDIA Ampere/Hopper-class GPUs; quantization itself needs a representative calibration dataset[^gptqmodel]. |
| Intel AutoRound | Intel-oriented W4A16/W8A16 deployment plus export to AutoRound, AutoAWQ, AutoGPTQ, and GGUF | vLLM's currently documented Intel recipes are W4A16 and W8A16; broader AutoRound formats do not imply equivalent vLLM support[^intel-quant]. |
| NVIDIA Model Optimizer | PTQ/QAT checkpoints in FP8, NVFP4, W4A16_NVFP4, and MXFP8 families | vLLM detects `hf_quant_config.json`; explicit quantization/backend names vary by format, and unsupported native FP4 execution can fall back to Marlin W4A16 with lower compute-bound throughput[^modelopt]. |
| AMD Quark | Offline weight, activation, and KV-cache quantization; OCP MX formats; layerwise mixed precision | Offline export uses Hugging Face safetensors and can apply AWQ/GPTQ/rotation/SmoothQuant-style recovery. Quark also ships `quark_online` presets and per-layer matching, including re-quantizing supported checkpoints at load time[^quark]. |
| TorchAO | Producing TorchAO-quantized Hugging Face checkpoints with native PyTorch composition | The source documents checkpoint creation and recommends a matching nightly TorchAO build, but does not provide a vLLM serving command or compatibility matrix[^torchao]. |

[LLM Compressor](vllm-llm-compressor-workflows.md) is the recommended vLLM-oriented path for new AWQ work and supports FP4, FP8, INT8, INT4, mixed precision, calibration algorithms, and compressed-tensors export.

## Hardware map

The overview's compatibility matrix reports[^quantization-overview]:

- AWQ and GPTQ support across several NVIDIA generations plus Intel GPU and x86 CPU, while their optimized kernel paths vary.
- LLM Compressor FP8 W8A8 on Ada/Hopper and AMD GPU; INT8 W8A8 across Turing through Hopper plus x86/Arm CPUs; W4A8 only on Arm CPU in that matrix.
- BitsAndBytes and DeepSpeedFP across the listed NVIDIA generations, but not AMD/Intel GPU or CPU targets.
- GGUF across the listed NVIDIA generations and AMD GPU, with no listed Intel GPU/CPU support.
- Marlin for GPTQ/AWQ/FP8/FP4 from Turing onward except MXFP4 on Turing; no listed AMD, Intel, or CPU support.

Architecture labels in that source map Volta/Turing/Ampere/Ada/Hopper to SM 7.0/7.5/8.0–8.6/8.9/9.0. The table is a point-in-time guide, not a guarantee; Google TPU support is delegated to separate TPU documentation, and Intel Gaudi support has moved to vLLM-Gaudi[^quantization-overview].

## Loading and backend behavior

- Pre-quantized formats may be auto-detected from checkpoint metadata, but some integrations require an explicit `quantization` value; follow the format-specific requirement rather than assuming uniform behavior[^bitsandbytes][^modelopt].
- Quantized linear and MoE kernels can have separate selectors. ModelOpt documents `--linear-backend` for linear layers, while MoE uses `--moe-backend`; explicit unsupported backends error instead of silently falling back in the documented paths[^modelopt].
- Offline quantization generally offers accuracy-recovery algorithms and a compact reusable checkpoint, at the cost of calibration/export time and another model artifact. [Online quantization](vllm-online-quantization.md) avoids export and calibration but uses dynamic activation scaling and may offer less accuracy recovery[^quark].

## Out-of-tree quantization plugins

A custom method subclasses `QuantizationConfig`, registers with `@register_quantization_config("name")`, declares supported activation dtypes, minimum capability, config filenames, config parsing, and layer dispatch, then returns an appropriate `QuantizeMethodBase` for linear layers or `FusedMoEMethodBase` for MoE layers. Importing the plugin module registers it before `LLM(..., quantization="name")` is constructed[^quantization-overview].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — quantized checkpoints and online schemes are loaded through the offline `LLM` API or `vllm serve`.
- Uses [vLLM Plugin System](vllm-plugin-system.md) — BitsAndBytes, GGUF, Quark online, and custom methods can be supplied out of tree.
- Uses [vLLM Fused MoE Kernel Features](vllm-moe-kernel-features.md) — MoE backend compatibility additionally depends on activation and weight formats.
- Uses [vLLM b12x Quantized Linear and MoE Backends](vllm-b12x-quantization-backends.md) — SM120/SM121 systems can select optional kernels for specific FP8/FP4 formats.

## Coverage limits

- External toolkit documentation, model collections, generated runtime registries, benchmarks, and linked source code were not independently inspected.
- Compatibility claims reflect these source snapshots and can become stale as plugins and kernels evolve.

[^quantization-overview]: Quantization — `../raw/vllm/features/quantization/README.md`, supported-format list, hardware matrix, caveats, and custom quantization registration example.
[^auto-awq]: AutoAWQ — `../raw/vllm/features/quantization/auto_awq.md`.
[^bitsandbytes]: BitsAndBytes — `../raw/vllm/features/quantization/bnb.md`.
[^gguf]: GGUF — `../raw/vllm/features/quantization/gguf.md`.
[^gptqmodel]: GPTQModel — `../raw/vllm/features/quantization/gptqmodel.md`.
[^intel-quant]: Intel Quantization Support — `../raw/vllm/features/quantization/inc.md`.
[^modelopt]: NVIDIA Model Optimizer — `../raw/vllm/features/quantization/modelopt.md`.
[^quark]: AMD Quark — `../raw/vllm/features/quantization/quark.md`.
[^torchao]: TorchAO — `../raw/vllm/features/quantization/torchao.md`.
