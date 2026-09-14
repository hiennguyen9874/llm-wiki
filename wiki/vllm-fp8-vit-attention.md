---
type: Concept
title: vLLM FP8 ViT Encoder Attention
description: Dynamic or calibrated FP8 QKV quantization for Qwen3-family vision attention on NVIDIA and AMD GPUs.
tags: [vllm, quantization, fp8, multimodal, attention]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:42:43Z }
sources:
  - id: fp8-vit
    resource: ../raw/vllm/features/quantization/fp8_vit_attn.md
    title: FP8 ViT Encoder Attention
---

vLLM can quantize ViT attention Q/K/V to FP8 immediately before attention, targeting visual workloads where large or multiple images make encoder attention a bottleneck—especially when a quantized text model shifts more runtime share to vision encoding[^fp8-vit].

## Applicability and requirements

- Current model coverage is the Qwen3-VL family and other models using Qwen3 ViT, including the listed `qwen3_vl`, `qwen3_vl_moe`, `qwen3_5`, and `qwen3_5_moe` families[^fp8-vit].
- NVIDIA requires FlashInfer cuDNN with cuDNN 9.17.1+; AMD requires AITER's variable-length per-tensor FP8 function on gfx942/MI300 or gfx950/MI350[^fp8-vit].
- Enable with `--mm-encoder-attn-dtype fp8` and select `FLASHINFER` on NVIDIA or `ROCM_AITER_FA` on AMD. AITER supports packed variable-length image/video batches[^fp8-vit].

## Dynamic and static scales

Without a scale file, dynamic mode keeps a 16-entry circular history of observed Q/K/V maxima and updates scales each forward pass. It requires no calibration and is reported to match BF16 accuracy, but adds overhead and is incompatible with ViT full CUDA graphs[^fp8-vit].

For production, the source recommends a calibrate-once flow: run `vllm bench mm-processor` on representative data with `--mm-encoder-fp8-scale-save-path`, then serve with `--mm-encoder-fp8-scale-path`. Saved maxima are multiplied by `--mm-encoder-fp8-scale-save-margin` (default 1.5) to accommodate unseen outliers. JSON entries are keyed by attention module and contain `q`, `k`, and `v` maxima; `q_scale`, `k_scale`, and `v_scale` aliases are accepted[^fp8-vit].

## Performance boundary

Quantization launches and unpadding can outweigh the faster attention kernel on smaller images. In the source's Qwen3-VL-30B-A3B-Instruct GB200 test with three images per request, FP8 was slower at HD, approximately equal at FullHD, 1.08× faster at QHD, and 1.18× at 4K. Core-kernel results were 1.12× on GB200 and 1.42× on GB300; MI300X complete-call results ranged from 1.06× to 1.38× over tested sequence lengths[^fp8-vit]. These are workload-specific reported measurements, not general guarantees.

A 500-sample ChartQA evaluation reported BF16, dynamic FP8, and static FP8 metrics within statistical noise; static scales calibrated on VisionArena-Chat used the default 1.5 margin[^fp8-vit].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — FlashInfer/cuDNN and ROCm AITER provide the platform kernels.
- Uses [vLLM Encoder CUDA Graphs for Vision Transformers](vllm-encoder-cuda-graphs.md) — dynamic scales are incompatible with ViT full CUDA graphs.
- Uses [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — image/video preprocessing feeds the encoder workload whose attention is quantized.

## Coverage limits

Benchmark methodology, raw samples, external backend implementations, and statistical significance were not independently verified. Performance and supported-model lists are point-in-time source claims.

[^fp8-vit]: FP8 ViT Encoder Attention — `../raw/vllm/features/quantization/fp8_vit_attn.md`.
