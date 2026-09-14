---
type: Concept
title: vLLM Engine, Worker, and Model Hierarchy
description: LLMEngine, workers, model runner, model objects, and VllmConfig design rationale.
tags: [vllm, architecture, engine, workers, configuration]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: arch-overview
    resource: ../raw/vllm/design/arch_overview.md
    title: Architecture Overview
---

The vLLM execution stack layers `LLMEngine` / `AsyncLLMEngine` over per-GPU workers, each containing one model runner and one `torch.nn.Module`, with a shared `VllmConfig` enabling extensibility, uniform construction, and initialization-time sharding and quantization[^arch-overview].

## Engine layer

- `LLMEngine` receives client requests and produces model outputs through input processing and tokenization, scheduling, possibly distributed model execution, and output detokenization[^arch-overview].
- Code: `vllm/engine/llm_engine.py`[^arch-overview].
- `AsyncLLMEngine` wraps `LLMEngine` with an `asyncio` background loop for online serving, supporting concurrent requests and output streaming[^arch-overview].
- The OpenAI-compatible API server uses `AsyncLLMEngine`; a simpler demo server is referenced under `examples/applications/api_server/server.py`[^arch-overview].
- Code: `vllm/engine/async_llm_engine.py`[^arch-overview].

## Worker, model runner, and model

- A worker is the process running inference for one accelerator; with tensor parallelism 2 and pipeline parallelism 2 there are 4 workers[^arch-overview].
- Workers carry global `rank` for orchestration and `local_rank` for device assignment and local resources such as filesystem and shared memory[^arch-overview].
- Every worker has one model runner responsible for loading and running the model, including input-tensor preparation and CUDA-graph capture[^arch-overview].
- Every model runner has one model object, the actual `torch.nn.Module`; model-class selection is delegated to the Hugging Face integration document, referenced but not ingested here[^arch-overview].

## Class-hierarchy design choices

- **Extensibility through shared configuration:** all hierarchy classes accept the encompassing `VllmConfig` object, so a runner-only feature only needs a new `VllmConfig` option without changing engine, worker, or model constructors[^arch-overview].
- **Uniformity through a common constructor:** model constructors use keyword-only `def __init__(self, *, vllm_config: VllmConfig, prefix: str = "")`, letting the runner instantiate any of 50+ supported models and compose vision plus language submodels without per-model inspection logic[^arch-overview].
- Out-of-tree models bridging pre- and post-`0.6.4` vLLM can shim the old `(config, cache_config, quant_config, lora_config, prefix)` signature behind the new `VllmConfig`-based subclass[^arch-overview].
- **Sharding and quantization at initialization:** weights are sharded or quantized during construction rather than after full-model load, so each GPU only materializes its shard; the source illustrates a 405B / ~810GB model needing only ~50GB per GPU across 16 H100 80GB GPUs[^arch-overview].
- `prefix` (empty for the top-level model, e.g. `vision` or `language` for submodels) supports non-uniform quantization and generally matches checkpoint state-dict names[^arch-overview].
- Trade-off: isolated unit testing is harder because components need a complete config; mitigation is a default config with fields set to `None`, overridden only for tested fields, alongside prevalent end-to-end tests[^arch-overview].
- In effect, `VllmConfig` acts as engine-level shared global state[^arch-overview].

## Coverage limits

- The `LLMEngine` diagram and class-hierarchy image (`hierarchy.png`) were referenced but absent from `raw/` and were not inspected[^arch-overview].

## Relationships

- Used by [vLLM Entrypoints](vllm-entrypoints.md) — entrypoints drive these engine and worker objects.
- Used by [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — engine-core and GPU-worker processes host this hierarchy.

[^arch-overview]: Architecture Overview — `../raw/vllm/design/arch_overview.md`, LLM Engine, Worker, Model Runner, Model, and Class Hierarchy sections.
