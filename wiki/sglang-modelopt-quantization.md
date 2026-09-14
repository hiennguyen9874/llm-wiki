---
type: Concept
title: SGLang Native ModelOpt Quantization
description: Native NVIDIA Model Optimizer quantization in SGLang covering NVFP4, MXFP4, and FP8 quantize-export-deploy workflow and throughput gains.
tags: [sglang, quantization, modelopt, nvfp4, fp8]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:27:17Z }
sources:
  - id: modelopt-sgl-blog
    resource: ../raw/2025-12-02-modelopt-quantization/index.md
    title: "Boost SGLang Inference: Native NVIDIA Model Optimizer Integration for Seamless Quantization and Deployment"
---

SGLang natively integrates NVIDIA Model Optimizer quantization APIs so a full-precision model can be quantized, exported, and served as a high-performance quantized endpoint entirely within SGLang, with NVFP4 showing up to 2x better per-GPU throughput than an FP8 baseline in reported InferenceMAX results[^modelopt-sgl-blog].

## Native integration scope

- Native ModelOpt support arrived via SGLang PRs [#7149](https://github.com/sgl-project/sglang/pull/7149), [#9991](https://github.com/sgl-project/sglang/pull/9991), and [#10154](https://github.com/sgl-project/sglang/pull/10154), eliminating the prior multi-step workflow with separate optimization and deployment tools[^modelopt-sgl-blog].
- Supported low-precision targets named in the source are NVFP4, MXFP4, and FP8[^modelopt-sgl-blog].
- Optimizations stack with the NVIDIA software-hardware stack across Blackwell embodiments from DGX Spark to GB300 NVL72[^modelopt-sgl-blog].
- Full workflow demo lives in `examples/usage/modelopt_quantize_and_export.py`; the environment needs `nvidia-modelopt` and `accelerate` installed in the SGLang environment[^modelopt-sgl-blog].

## Quantize-export-deploy workflow

Three steps, all inside SGLang[^modelopt-sgl-blog]:

1. **Quantize**: call ModelOpt quantization APIs from SGLang code.
2. **Export**: save optimized artifacts in SGLang-runtime-compatible form.
3. **Deploy**: load the quantized model directly into the SGLang runtime on NVIDIA platforms.

### Quantize and export

Configure `ModelConfig` with `quantization="modelopt_fp8"` or `"modelopt_fp4"`, `LoadConfig` with `modelopt_export_path` and optional `modelopt_checkpoint_save_path` for a fake quantized checkpoint, then load through `get_model_loader` — export happens automatically[^modelopt-sgl-blog]:

```python
import sglang as sgl
from sglang.srt.configs.device_config import DeviceConfig
from sglang.srt.configs.load_config import LoadConfig
from sglang.srt.configs.model_config import ModelConfig
from sglang.srt.model_loader.loader import get_model_loader

model_config = ModelConfig(
    model_path="Qwen/Qwen3-8B",
    quantization="modelopt_fp8",  # or "modelopt_fp4"
    trust_remote_code=True,
)

load_config = LoadConfig(
    modelopt_export_path="./quantized_qwen3_8b_fp8",
    modelopt_checkpoint_save_path="./checkpoint.pth",  # optional, fake quantized checkpoint
)
device_config = DeviceConfig(device="cuda")

model_loader = get_model_loader(load_config, model_config)
quantized_model = model_loader.load_model(
    model_config=model_config,
    device_config=device_config,
)
```

### Deploy

Serve the exported directory with `--quantization modelopt`[^modelopt-sgl-blog]:

```bash
python -m sglang.launch_server \
   --model-path ./quantized_qwen3_8b_fp8 \
   --quantization modelopt \
   --port 30000 --host 0.0.0.0
```

Or via the offline Engine API with tokenizer chat-template formatting[^modelopt-sgl-blog]:

```python
import sglang as sgl
from transformers import AutoTokenizer

llm = sgl.Engine(
    model_path="./quantized_qwen3_8b_fp8",
    quantization="modelopt"
)
```

## Performance outcomes

- As measured by InferenceMAX results cited in the source, ModelOpt plus SGLang optimizations deliver up to 2x better per-GPU throughput comparing NVFP4 against an original FP8 baseline[^modelopt-sgl-blog].
- The attached chart shows NVIDIA B200 per-GPU token throughput versus end-to-end latency for DeepSeek-R1-0528 at ISL/OSL 1K/1K, with the ModelOpt NVFP4 curve above Original FP8 across the latency range and reaching roughly 840 tok/s/GPU near 26.5 s latency and about 1610 tok/s/GPU near 29.5 s, versus about 590 tok/s/GPU for Original FP8 near 23 s[^modelopt-sgl-blog].
- The source explicitly cautions that DeepSeek-R1-0528 is not yet supported in the initial API release, and describes these performance benefits as coming soon through the native integration[^modelopt-sgl-blog].

## Relationships

- Uses [SGLang Quantization](sglang-quantization.md) — this native ModelOpt API is the dedicated quantize-export-deploy path within the broader SGLang offline and online quantization landscape.
- Uses [Unsloth Dynamic NVFP4 Quantization](unsloth-dynamic-nvfp4.md) — alternative Blackwell NVFP4 path with per-layer dynamic retention, useful for comparing local versus SGLang-server NVFP4 tradeoffs.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — overlapping FP8 and NVFP4 format choices with different serving integrations.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical reference for `--model-path`, `--quantization`, `--port`, and `--host` launch flags used in deployment.

## Coverage limits

- Attached performance chart was visually inspected; exact plotted values are approximate and test configuration beyond ISL/OSL 1K/1K, B200, and InferenceMAX sourcing was not independently verified.
- Model support snapshot, PR numbers, and install requirements reflect the Dec 2, 2025 source and may change with SGLang and ModelOpt updates.
- Community channel and acknowledgements were excluded as non-durable operational knowledge.

[^modelopt-sgl-blog]: Boost SGLang Inference: Native NVIDIA Model Optimizer Integration for Seamless Quantization and Deployment — `../raw/2025-12-02-modelopt-quantization/index.md`.
