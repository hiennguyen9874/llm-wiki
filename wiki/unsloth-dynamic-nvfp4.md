---
type: Concept
title: Unsloth Dynamic NVFP4 Quantization
description: Blackwell-only 4-bit quantization combining native NVFP4 with per-layer dynamic FP8/BF16 retention for faster inference and lower VRAM.
tags: [unsloth, quantization, nvfp4, blackwell, deployment]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:00:00Z }
sources:
  - id: nvfp4-guide
    resource: ../raw/unsloth/basics/nvfp4.md
    title: Run Unsloth Dynamic NVFP4 Guide
---

Unsloth Dynamic NVFP4 is a Blackwell-only quantized model format for fast, accurate 4-bit inference that combines NVIDIA native NVFP4 precision with Unsloth Dynamic 2.0 per-layer quantization, keeping sensitive layers in FP8 or BF16 and the rest in W4A4 to use FP4 tensor cores[^nvfp4-guide].

## Method

- Dynamic layer selection: important layers remain in FP8 (W8A8) or BF16 while the rest run in W4A4, explicitly not W4A16, instead of forcing every layer into FP4[^nvfp4-guide].
- W4A4 execution uses Blackwell FP4 tensor cores, supporting the reported up-to-2.5x faster inference claim[^nvfp4-guide].
- FP8 KV-cache calibration is provided for all quants and is reported to allow 2x longer context lengths[^nvfp4-guide].
- MTP tensors are built directly into the quants for additional speedups[^nvfp4-guide].
- Reported accuracy work includes Qwen3.6 chat-template updates for coding and tool-calling consistency and reduced looping, plus calibration on a coding, tool-calling, and chat mix alongside UltraChat[^nvfp4-guide].

## Why FP4 and why NVFP4 over MXFP4

- The source rationale is that lowering numerical precision reduces matrix-multiplication transistor cost roughly with the square of the mantissa; FP4 with 1 mantissa bit and 2 exponent bits is presented as ~179x less space than FP32, enabling proportionally more FP4 FLOPs in the same area[^nvfp4-guide].
- NVFP4 is presented as more accurate than MXFP4 because it uses block size 16 versus 32, isolating outliers with finer-grained scales, and uses E4M3 (FP8) per-block scales instead of E8M0 powers-of-two scaling[^nvfp4-guide].

## Hardware scope and reported VRAM

NVFP4 requires NVIDIA Blackwell GPUs such as RTX 50-series, B200/B300, RTX PRO 6000, and DGX Spark; for older GPUs the source points to GGUFs[^nvfp4-guide].

Reported Gemma 4 Dynamic NVFP4 requirements versus BF16[^nvfp4-guide]:

| Gemma 4 variant | Required VRAM | Faster than BF16 |
| --- | ---: | ---: |
| E2B | 7 GB | 1.12x faster |
| E4B | 9 GB | 1.22x faster |
| 12B Unified | 11 GB | 1.26x faster |
| 26B-A4B MoE | 26 GB | 1.41x faster |
| 31B dense | 32 GB | 1.45x faster |

Reported Qwen3.6 Dynamic NVFP4 versus other NVFP4 quants[^nvfp4-guide]:

| Qwen3.6 variant | Required VRAM | Faster than other NVFP4 quants |
| --- | ---: | ---: |
| 27B | 24 GB | 2.5x faster |
| 35B-A3B | 32 GB | 1.56x faster |
| 35B-A3B Fast | 32 GB | 1.79x faster |

Other reported throughput points include up to 1.44x on Gemma 4 at 128 concurrency on 1x B200 versus BF16, 1.38x for Qwen3.5-122B-A10B, 1.27x for GLM-4.7-Flash, and up to 17,561 tokens/s for the 35B class at higher concurrency[^nvfp4-guide].

## Reported accuracy

The source reports MMLU-Pro, GPQA, and AIME 2025 for Unsloth versus NVIDIA NVFP4, FP8, and BF16, with comparable output lengths so speed is not offset by longer generations[^nvfp4-guide].

Qwen3.6-27B NVFP4[^nvfp4-guide]:

| Provider | MMLU-Pro | GPQA | AIME 2025 |
| --- | ---: | ---: | ---: |
| Unsloth | 86.25 | 86.34 | 93.12 |
| NVIDIA | 85.96 | 86.87 | 93.12 |
| FP8 | 86.11 | 86.87 | 93.75 |
| BF16 | 85.96 | 88.13 | 93.33 |

Qwen3.6-35B-A3B NVFP4[^nvfp4-guide]:

| Provider | MMLU-Pro | GPQA | AIME 2025 |
| --- | ---: | ---: | ---: |
| Unsloth | 85.85 | 86.74 | 92.29 |
| Unsloth Fast | 85.58 | 87.75 | 91.67 |
| NVIDIA | 85.60 | 87.12 | 91.88 |
| FP8 | 85.75 | 86.74 | 93.12 |
| BF16 | 85.75 | 86.36 | 92.50 |

The 35B-A3B Fast variant is described as full W4A4 and fastest, while the non-Fast 35B-A3B is slightly bigger but more accurate; decode speed is reported as 1.03x faster for 27B and 1.17x/1.22x faster for the 35B variants[^nvfp4-guide].

Available checkpoints named in the source include Qwen3.8-27B NVFP4, Qwen3.6-27B NVFP4, Qwen3.6-35B-A3B NVFP4, Qwen3.6-35B-A3B NVFP4 Fast, and Gemma 4 E2B, E4B, 12B Unified, 26B-A4B, and 31B NVFP4 variants[^nvfp4-guide].

## Serving in vLLM

- Leave backend selection automatic; do not pin an MoE backend for general Blackwell serving because Marlin does not support W4A4 well and can cause ~2.5x degradation — use CUTLASS, FlashInfer-TRTLLM, or Cute-DSL via auto-selection[^nvfp4-guide].
- Install with at least `vllm>=0.25.0`, `flashinfer-python>=0.6.13`, and `nvidia-cutlass-dsl>=4.5.2`[^nvfp4-guide]:

```bash
uv venv unsloth-nvfp4-env --python 3.13
source unsloth-nvfp4-env/bin/activate
uv pip install "vllm>=0.25.0" "flashinfer-python>=0.6.13" "nvidia-cutlass-dsl>=4.5.2" \
  --torch-backend=auto
```

- Serve, substituting the desired NVFP4 checkpoint name[^nvfp4-guide]:

```bash
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast
```

- Optional MTP/speculative decoding for faster decode at somewhat lower throughput[^nvfp4-guide]:

```bash
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast \
  --speculative-config '{"method": "mtp", "num_speculative_tokens": 2}'
```

- Torchcodec failure workaround is installing `ffmpeg` then relaunching vLLM[^nvfp4-guide]:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

Reported backend contrast on the source B200 setup shows auto-selected Cute-DSL fastest on throughput, while Marlin is much slower on W4A4 throughput despite competitive decode tokens/s in some rows[^nvfp4-guide].

## DGX Spark serving

- First verify b12x GEMM/MoE availability; failure means serving would degrade toward Marlin W4A16[^nvfp4-guide]:

```bash
python -c "
import torch; from vllm.utils.flashinfer import has_flashinfer_b12x_gemm as g, has_flashinfer_b12x_moe as m
cap = torch.cuda.get_device_capability(); print('cap', cap, '| b12x gemm', g(), '| b12x moe', m()); assert cap[0] == 12 and g() and m(), 'b12x unavailable: serving would degrade to marlin W4A16'"
```

- Serve with the Spark-specific architecture and MoE backend[^nvfp4-guide]:

```bash
export CUTE_DSL_ARCH=sm_121a
vllm serve unsloth/Qwen3.6-35B-A3B-NVFP4-Fast --moe-backend flashinfer_b12x
```

## Serving in SGLang

Substitute the desired model path[^nvfp4-guide]:

```bash
python -m sglang.launch_server --model-path unsloth/Qwen3.6-27B-NVFP4 --speculative-algorithm NEXTN \
  --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
```

```bash
python -m sglang.launch_server --model-path unsloth/Gemma-4-31B-NVFP4 --speculative-algorithm NEXTN \
  --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4
```

## Relationships

- Uses [Unsloth Dynamic GGUF Quantization](unsloth-dynamic-gguf.md) — shares Unsloth Dynamic per-layer and calibration lineage, here applied to NVFP4 rather than GGUF.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — NVFP4 checkpoint and backend-selection context, including ModelOpt FP4 families and Marlin W4A16 fallback behavior.
- Uses [vLLM b12x Quantized Linear and MoE Backends](vllm-b12x-quantization-backends.md) — SM120/SM121 NVFP4/MXFP4 linear and MoE kernel context relevant to RTX 50-series and DGX Spark.
- Uses [SGLang Quantization](sglang-quantization.md) — SGLang offline ModelOpt FP4 and Unsloth quantized-checkpoint context.
- Uses [vLLM Quantized KV Cache](vllm-quantized-kv-cache.md) — FP8 KV-cache scaling, calibration, and backend constraints behind the 2x context claim.
- Uses [SGLang Quantized KV Cache](sglang-quantized-kv-cache.md) — FP8/FP4 KV-cache format and backend context.
- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native MTP speculation matching the built-in MTP tensors and vLLM MTP serve flag.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — EAGLE/NEXTN draft-decoding context for the SGLang NEXTN launch flags.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — need to validate quantized checkpoints beyond single accuracy numbers and check for generation-length confounds.

## Coverage limits

- Embedded throughput, accuracy, decode-speed, and output-length plots were not visually inspected; all benchmark deltas are source-reported, not independently verified.
- Remote Hugging Face collection and checkpoint links, Unsloth model docs links, and vLLM/SGLang guide links were not inspected.
- Version floor (`vllm>=0.25.0` and related package minima) and DGX Spark environment variables reflect this source snapshot and may go stale.

[^nvfp4-guide]: Run Unsloth Dynamic NVFP4 Guide — `../raw/unsloth/basics/nvfp4.md`, Dynamic NVFP4 method and W4A4/FP8-layer design, FP4 and NVFP4-versus-MXFP4 rationale, Gemma 4 and Qwen3.6 VRAM/speed tables, MMLU-Pro/GPQA/AIME tables, MTP and calibration notes, and vLLM/DGX Spark/SGLang run commands and backend guidance.
