---
type: Concept
title: SGLang Quantization
description: Offline pre-quantized and online dynamic quantization for SGLang covering FP8, AWQ, GPTQ, ModelOpt, torchao, and AMD Quark flows.
tags: [sglang, quantization, fp8, deployment]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T14:00:00Z }
sources:
  - id: sgl-quant
    resource: ../raw/sglang/advanced_features/quantization.mdx
    title: Quantization
  - id: modelopt-sgl-blog
    resource: ../raw/2025-12-02-modelopt-quantization/index.md
    title: "Boost SGLang Inference: Native NVIDIA Model Optimizer Integration for Seamless Quantization and Deployment"
  - id: cleaner-quant-stack
    resource: ../raw/2026-07-31-cleaner-quantization-stack/index.md
    title: "Toward a Cleaner Quantization Stack in SGLang"
---

SGLang supports offline quantization that loads pre-quantized weights and online quantization that computes scaling factors at runtime; offline quantization is recommended for performance, usability, and convenience[^sgl-quant].

The implementation is moving to a `Config -> Method -> Scheme -> Kernel` structure that keeps checkpoint-format handling in hardware-agnostic schemes while backend-specific transforms and execution live in reusable kernels; see [SGLang Cleaner Quantization Stack](sglang-cleaner-quantization-stack.md) for the full architecture, reuse example, and roadmap[^cleaner-quant-stack].

## Offline versus online

- Offline quantization loads pre-quantized model weights directly during inference. It is required for GPTQ and AWQ, which collect and pre-compute statistics from original weights with a calibration dataset[^sgl-quant].
- Online quantization dynamically computes scaling parameters such as weight maximum/minimum values at runtime, analogous to delayed scaling in NVIDIA FP8 training, converting high-precision weights to lower precision on the fly[^sgl-quant].
- Do not combine a pre-quantized model with `--quantization` for online quantization, except for the explicit per-channel `w8a8` kernel override below[^sgl-quant].
- Published quality-validated quantized checkpoints include Unsloth, NVIDIA ModelOpt, and NeuralMagic collections on Hugging Face. Quantized models must be benchmark-validated after quantization to guard against abnormal quality regressions[^sgl-quant].

## Loading offline-quantized models

Already-quantized models normally load from weights and config with no `--quantization` argument; SGLang parses the method from the Hugging Face config. DeepSeek V3/R1 models are already FP8, so no redundant quantization flag is needed[^sgl-quant].

```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```

Exception: a per-channel quantized INT8 or FP8 model with per-token dynamic activation quantization can pass `--quantization w8a8_int8` or `--quantization w8a8_fp8` to use the corresponding CUTLASS `int8_kernel` or `fp8_kernel` in `sgl-kernel`. This ignores the Hugging Face config quantization setting and instead uses SGLang `W8A8Fp8Config` rather than `CompressedTensorsConfig` for vLLM kernels[^sgl-quant]:

```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```

## Offline quantization toolchains

- Unsloth is the strongly suggested path for quantizing and loading models; follow the Unsloth SGLang deployment and inference guide for details[^sgl-quant].
- Intel auto-round supports LLM quantization with `AutoRound` and VLM quantization with `AutoRoundMLLM`, plus CLI use on Gaudi, CPU, Intel GPU, and CUDA. Example schemes include `W2A16`, `W3A16`, `W4A16`, `W8A16`, `NVFP4`, `MXFP4` without real kernels, and `GGUF:Q4_K_M`[^sgl-quant].
- GPTQModel quantizes from a calibration sample, for example 1,024 texts from `allenai/c4`, with a `QuantizeConfig(bits=4, group_size=128)` followed by `quantize` and `save`[^sgl-quant].
- LLM Compressor one-shot quantization supports flows such as FP8 dynamic quantization of linear layers while ignoring `lm_head`; the exported directory then launches without a quantization flag[^sgl-quant].
- NVIDIA ModelOpt provides `modelopt_fp8` for NVIDIA Hopper and Blackwell GPUs and `modelopt_fp4` for Blackwell GPUs, with quantization, checkpoint save/restore, Hugging Face-format export, and deployment using `--quantization modelopt`[^sgl-quant].

Auto-round has known SGLang loading limits: mixed-bit quantization is not fully supported because vLLM layer fusion such as QKV fusion cannot mix bit-widths within one fused layer; quantized MoE models may fail from missing kernel support such as `mlp.gate` quantization, so skip those layers; and quantized VLMs vary by format — the source reports Qwen2.5-VL-7B works with `auto_awq`/AWQ, fails with GPTQ size alignment, and has near-zero accuracy with `auto_round:auto_gptq`[^sgl-quant].

## ModelOpt workflow

Install ModelOpt directly or as `sglang[modelopt]`, with the latter recommended[^sgl-quant]:

```bash
python examples/usage/modelopt_quantize_and_export.py quantize \
    --model-path TinyLlama/TinyLlama-1.1B-Chat-v1.0 \
    --export-dir ./quantized_tinyllama_fp8 \
    --quantization-method modelopt_fp8
```

The Python path configures `ModelConfig` with `quantization="modelopt_fp8"` or `"modelopt_fp4"`, uses `LoadConfig` with `modelopt_export_path` and optionally `modelopt_checkpoint_save_path`, then loads through `get_model_loader`; deployment uses the exported directory with `quantization="modelopt"` or `sgl.Engine` with the same setting[^sgl-quant].

Advanced ModelOpt use includes saving a fake quantized checkpoint with `--checkpoint-save-path` for reuse without recalibration, and an export-only workflow that restores an existing checkpoint through `modelopt_checkpoint_restore_path` plus `modelopt_export_path`[^sgl-quant].

## Online quantization

Enable online quantization with `--quantization`, for example FP8 for Llama-3.1-8B-Instruct[^sgl-quant]:

```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --quantization fp8 \
    --port 30000 --host 0.0.0.0
```

The source lists `awq`, `gptq`, `marlin`, `gptq_marlin`, `awq_marlin`, `bitsandbytes`, and `gguf` as forthcoming online methods under development, not current support[^sgl-quant].

### torchao

Specify a torchao scheme with `--torchao-config`, for example `int4wo-128`[^sgl-quant]:

```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --torchao-config int4wo-128 \
    --port 30000 --host 0.0.0.0
```

Supported torchao values are `int8dq`, `int8wo`, `fp8wo`, `fp8dq-per_tensor`, `fp8dq-per_row`, `int4wo-32`, `int4wo-64`, `int4wo-128`, and `int4wo-256`[^sgl-quant]. `int8dq` has a known interaction with CUDA graph capture, so disable CUDA graphs when using it[^sgl-quant]:

```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --torchao-config int8dq \
    --disable-cuda-graph \
    --port 30000 --host 0.0.0.0
```

### AMD Quark MoE

On AMD CDNA3 or CDNA4 GPUs, `--quantization quark_int4fp8_moe` replaces high-precision MoE layers in bfloat16, float16, or float32 with weights dynamically quantized to INT4, upcast to FP8 during inference, while activations are dynamically quantized to FP8; other layers such as attention projections are quantized online directly to FP8[^sgl-quant].

## Relationships

- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — quantization is one listed advanced-feature area.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — overlapping GPTQ, AWQ, ModelOpt, torchao, and Quark formats with different serving integrations.
- Uses [vLLM Online Quantization](vllm-online-quantization.md) — load-time dynamic quantization analogue for global, per-layer, mixed-format, and exclusion controls.
- Uses [vLLM LLM Compressor Quantization Workflows](vllm-llm-compressor-workflows.md) — offline FP8 and INT4 compressed-tensors recipes related to the SGLang LLM Compressor flow.
- Uses [SGLang Native ModelOpt Quantization](sglang-modelopt-quantization.md) — dedicated native ModelOpt quantize-export-deploy path for NVFP4, MXFP4, and FP8 with reported throughput gains[^modelopt-sgl-blog].
- Uses [SGLang Cleaner Quantization Stack](sglang-cleaner-quantization-stack.md) — scheme-based `Config -> Method -> Scheme -> Kernel` refactor separating format handling from hardware kernels[^cleaner-quant-stack].

## Coverage limits

- External guides, model collections, generated export artifacts, benchmarks, and linked source files were not independently inspected.
- Forward-looking online-method support and auto-round failure cases reflect this source snapshot and may change with SGLang updates.

[^sgl-quant]: Quantization — `../raw/sglang/advanced_features/quantization.mdx`.
[^modelopt-sgl-blog]: Boost SGLang Inference: Native NVIDIA Model Optimizer Integration for Seamless Quantization and Deployment — `../raw/2025-12-02-modelopt-quantization/index.md`.
[^cleaner-quant-stack]: Toward a Cleaner Quantization Stack in SGLang — `../raw/2026-07-31-cleaner-quantization-stack/index.md`.
