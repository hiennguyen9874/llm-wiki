---
type: Concept
title: SGLang Data-Parallel Multimodal Encoder
description: Hybrid DP vision encoder with TP language decoder via --mm-enable-dp-encoder for lower TTFT and higher throughput.
tags: [sglang, multimodal, vision, data-parallel, vit]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T12:00:00Z }
sources:
  - id: sgl-dp-mm-enc
    resource: ../raw/sglang/advanced_features/dp_for_multi_modal_encoder.mdx
    title: DP for Multi-Modal Encoder in SGLang
---

SGLang can place the vision encoder in batch-level data parallelism while keeping the language decoder in tensor parallelism, lowering TTFT and raising end-to-end throughput by reserving collectives and interconnect bandwidth for the LLM[^sgl-dp-mm-enc].

## Architecture

A typical VLM has a multimodal encoder plus a text-decoder LLM; most VLMs use a Vision Transformer (ViT) to extract visual features for the decoder[^sgl-dp-mm-enc].

ViT size is very small compared to language decoders, so tensor parallelism gives relatively little gain while incurring significant all-reduce communication after every layer[^sgl-dp-mm-enc].

The hybrid layout makes the vision front-end parallel and lightweight while scarce interconnect bandwidth and collective ops are reserved for the LLM[^sgl-dp-mm-enc].

Data parallelism here replicates the entire model across multiple GPU sets and processes different batches of requests in parallel[^sgl-dp-mm-enc].

## Enablement

Enable batch-level DP with `mm-enable-dp-encoder`[^sgl-dp-mm-enc]:

```shell
python3 -m sglang.launch_server \
    --model-path Qwen/Qwen2.5-VL-7B-Instruct \
    --tp 2 \
    --mm-enable-dp-encoder
```

## Supported models

Known supported models at time of writing[^sgl-dp-mm-enc]:

- Qwen2.5-VL
- Qwen3-VL
- InternVL
- GLM-4.5V and GLM-4.6V

## Relationships

- Uses [SGLang ViT CUDA Graphs for Multimodal Encoders](sglang-vit-cuda-graph.md) — companion ViT launch-overhead optimization; DP parallelism and CUDA-Graph capture address different encoder bottlenecks.
- Uses [vLLM Multimodal Caching and Encoder Batch Parallelism](vllm-multimodal-caching.md) — vLLM analog via `mm_encoder_tp_mode="data"` that shards encoder input batches rather than weights for the same small-encoder TP-overhead reason.

[^sgl-dp-mm-enc]: DP for Multi-Modal Encoder in SGLang — `../raw/sglang/advanced_features/dp_for_multi_modal_encoder.mdx`, covering VLM encoder/decoder split, ViT TP overhead rationale, hybrid DP+TP layout, batch-level DP definition, `--mm-enable-dp-encoder` command with Qwen2.5-VL-7B `--tp 2` example, and Qwen2.5-VL, Qwen3-VL, InternVL, GLM-4.5V/4.6V support with PR links.
