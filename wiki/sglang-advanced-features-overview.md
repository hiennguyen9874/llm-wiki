---
type: Concept
title: SGLang Advanced Features Overview
description: SGLang advanced-features map linking server arguments, tuning, backends, decoding, structured outputs, quantization, parallelism, adapters, caching, and observability.
tags: [sglang, advanced-features, overview]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:14:43Z }
sources:
  - id: sgl-overview
    resource: ../raw/sglang/advanced_features/overview.mdx
    title: Advanced Features
---

SGLang groups server arguments, hyperparameter tuning, attention backends, speculative decoding, structured outputs, quantization, expert parallelism, LoRA, PD disaggregation, pipeline parallelism, HiCache, and observability under Advanced Features[^sgl-overview].

## Listed scope

The source is a navigation map with no prose or parameters beyond these links[^sgl-overview]:

- Server Arguments
- Hyperparameter Tuning
- Attention Backend
- Speculative Decoding
- Structured Outputs
- Quantization
- Expert Parallelism
- LoRA
- PD Disaggregation
- Pipeline Parallelism
- HiCache — linked to `hicache_best_practices`
- Observability
- And more… — duplicate link to `server_arguments`

## Compiled coverage

Detail for these listed areas is maintained in dedicated concepts, not duplicated here:

- [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) covers the listed Hyperparameter Tuning entry.
- [SGLang Attention Backends](sglang-attention-backends.md) covers the listed Attention Backend entry.
- [SGLang Expert Parallelism](sglang-expert-parallelism.md) covers the listed Expert Parallelism entry.
- [SGLang LoRA Serving](sglang-lora-serving.md) covers the listed LoRA entry.
- [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) covers the listed HiCache entry, with related design and runtime detail in [SGLang HiCache System Design](sglang-hicache-design.md) and [SGLang HiCache Runtime Storage Attach/Detach](sglang-hicache-runtime-attach-detach.md).
- [SGLang Observability](sglang-observability.md) covers the listed Observability entry.
- [SGLang PD Disaggregation](sglang-pd-disaggregation.md) covers the listed PD Disaggregation entry.
- [SGLang Pipeline Parallelism](sglang-pipeline-parallelism.md) covers the listed Pipeline Parallelism entry.
- [SGLang Quantization](sglang-quantization.md) covers the listed Quantization entry.
- [SGLang Server Arguments](sglang-server-arguments.md) covers the listed Server Arguments entry.
- [SGLang Speculative Decoding](sglang-speculative-decoding.md) covers the listed Speculative Decoding entry.
- [SGLang Structured Outputs](sglang-structured-outputs.md) covers the listed Structured Outputs entry.

## Relationships

- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — listed advanced-feature area for offline batch-inference throughput tuning.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — listed advanced-feature area for attention backend selection and extension.
- Uses [SGLang Expert Parallelism](sglang-expert-parallelism.md) — listed advanced-feature area for MoE expert-parallel serving.
- Uses [SGLang LoRA Serving](sglang-lora-serving.md) — listed advanced-feature area for multi-LoRA serving.
- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) — listed HiCache entry point for hierarchical KV-cache tuning.
- Uses [SGLang Observability](sglang-observability.md) — listed advanced-feature area for metrics, logging, and dump/replay debugging.
- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — listed advanced-feature area for separated prefill/decode serving.
- Uses [SGLang Pipeline Parallelism](sglang-pipeline-parallelism.md) — listed advanced-feature area for pipeline-parallel long-context serving.
- Uses [SGLang Quantization](sglang-quantization.md) — listed advanced-feature area for offline and online quantization.
- Uses [SGLang Structured Outputs](sglang-structured-outputs.md) — listed advanced-feature area for constrained JSON-schema, regex, EBNF, and structural-tag generation.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — listed advanced-feature area for launch and configuration flags.
- Uses [SGLang Speculative Decoding](sglang-speculative-decoding.md) — listed advanced-feature area for EAGLE-2/EAGLE-3 speculation, FR-Spec, and MTP usage.

## Coverage limits

- This source contains only navigation links with frontmatter title and description; it states no behavior, defaults, procedures, or trade-offs[^sgl-overview].
- The `raw/sglang/advanced_features/` directory contains additional sources not listed in this overview, including checkpoint engine, multimodal-encoder CUDA graphs, deterministic inference, multimodal-encoder data parallelism, EPD disaggregation, forward hooks, HiCache design and runtime storage detail, quantized KV cache, and other feature pages; their absence from the map is a source-coverage gap, not evidence they are out of scope.
- The final "And more…" entry links to the same `server_arguments` target as the first entry, so it adds no new scope[^sgl-overview].

[^sgl-overview]: Advanced Features — `../raw/sglang/advanced_features/overview.mdx`.
