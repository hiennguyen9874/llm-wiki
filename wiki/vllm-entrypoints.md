---
type: Concept
title: vLLM Entrypoints
description: Offline LLM class versus online vllm serve server for model inference.
tags: [vllm, inference, entrypoints]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: arch-overview
    resource: ../raw/vllm/design/arch_overview.md
    title: Architecture Overview
---

vLLM exposes two primary interfaces: the `LLM` Python class for offline inference and the `vllm serve` HTTP server for online serving[^arch-overview].

## Offline inference

- `LLM` class is the primary Python interface for interacting with a model without a separate inference server[^arch-overview].
- Typical usage: construct `LLM(model=...)` with `SamplingParams`, then call `llm.generate(prompts, sampling_params)`[^arch-overview].
- Implementation: `vllm/entrypoints/llm.py`[^arch-overview].
- Further API detail is in the Offline Inference API docs, referenced but not ingested here[^arch-overview].

## Online serving

- Started with `vllm serve <model>`[^arch-overview].
- Serves HTTP traffic such as the OpenAI-compatible API and streams results back to clients; detailed behavior is in the Online Serving document, referenced but not ingested here[^arch-overview].
- CLI implementation: `vllm/entrypoints/cli/main.py`[^arch-overview].

## Coverage limits

- The source references an entrypoints relationship diagram (`entrypoints.excalidraw.png`); the image was not present in `raw/` and was not inspected[^arch-overview].

## Relationships

- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — online serving fans out to API server and engine-core processes.
- Uses [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — both entrypoints ultimately drive `LLMEngine` / workers.

[^arch-overview]: Architecture Overview — `../raw/vllm/design/arch_overview.md`, Entrypoints section.
