---
type: Concept
title: UltraRAG generation backends
description: Local and API model generation, multimodal calls, concurrency, retries, and inference lifecycle constraints.
tags: [ml, ultrarag, inference]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e2032d9f134099405b8b483edbbad95274080
    title: UltraRAG repository
---

**Observed:** UltraRAG's generation server supports `vllm`, `openai`, `litellm`, and `hf` backends, presenting generation as MCP tools rather than embedding inference into the orchestration client. Tool surfaces include initialization, ordinary generation, multimodal generation, multi-turn generation, and vLLM shutdown. Backend availability depends on installed extras and external model/API resources.[^ultrarag]

## Backend selection and defaults

The committed parameter file selects `vllm` with `openbmb/MiniCPM4-8B`; sampling defaults there are temperature `0.7`, top-p `0.8`, and max tokens `2048`. vLLM tensor parallelism is derived from the configured comma-separated GPU IDs. These are snapshot defaults, not hardware-independent recommendations.[^ultrarag]

- **vLLM:** local inference with GPU/model loading and explicit cleanup.
- **OpenAI:** asynchronous API calls to a configured model/base URL.
- **LiteLLM:** a separate API-routing integration, installable without the heavy local `generation` extra.
- **HF:** local Transformers-based generation inside `generation.py`. Separately, `local_generation.py::LocalGenerationService` provides OpenAI-compatible streaming, including a multi-turn method; despite its filename, it is not the HF backend.[^ultrarag]

API credentials can come from configuration or `LLM_API_KEY`; credentials and private endpoints must not be copied into maintained examples. Multimodal and conversational tools carry additional formatting and model-capability assumptions; a backend name alone does not prove equivalent support for every tool.[^ultrarag]

## Demo/UI execution overrides

**Observed:** when `is_demo=True`, the client intercepts `generate` and `multimodal_generate` steps and substitutes `LocalGenerationService` rather than calling the generation MCP tool. This applies to CLI demo runs as well as UI chat. The UI builds the service with `backend="openai"` and forces generation/retriever overrides toward OpenAI-compatible APIs. A pipeline whose committed default is `vllm` therefore does **not** imply local vLLM inference during demo/chat: the service reads the `openai` configuration block and needs a reachable compatible endpoint.[^ultrarag]

## Concurrency and failure semantics

The committed API settings are concurrency `8`, retries `3`, and base delay `1.0`. **Observed:** retries are narrower than “retry all failures.” The OpenAI path immediately raises tool errors for non-server failures, while server failures can retry; the LiteLLM path explicitly handles transient timeout/connection/server cases. Exhausted retry paths can return the literal `"<error>"` as an answer. This describes the non-demo MCP generation path. Demo streaming instead can yield `[Error: ...]` text, and the client accumulates streamed content into `ans_ls`, potentially retaining a partial answer plus an error message. Downstream evaluation must distinguish both forms from legitimate responses.[^ultrarag]

Multimodal generation can pass through HTTP/data image URIs or base64-encode local image files. An image-tag count mismatch raises `ValueError`, while unreadable local files can be warned about and skipped. The HF branch forwards sampling parameters into Transformers; the shipped `max_tokens` vocabulary may need adaptation to `max_new_tokens` (**synthesis**, not a reproduced failure). These backend-specific semantics matter when migrating a pipeline.[^ultrarag]

The orchestration client attempts tools ending in `vllm_shutdown` during final cleanup and logs cleanup failures as warnings. This is best-effort lifecycle handling, not a guarantee that every driver/process resource is reclaimed.[^ultrarag]

## Evidence and limits

All runtime behavior above is **observed statically**. The repository contains a LiteLLM generation test file, but no test, provider call, model download, CUDA initialization, throughput measurement, or multimodal inference was performed during ingestion. No independent quality, latency, or compatibility claims are established.[^ultrarag]

## Relationships

- **Depends on:** [installation extras and CUDA choices](ultrarag-deployment.md).
- **Uses:** [prompt workflows](ultrarag-research-workflows.md) for model input construction.
- **Used by:** [evaluation](ultrarag-evaluation.md); error sentinels affect answer interpretation.

[^ultrarag]: Revision `185e2032d9f134099405b8b483edbbad95274080`: `servers/generation/parameter.yaml` `backend`, `model_name`, sampling and API concurrency/retry settings; `servers/generation/src/generation.py::generation_init`, `generate`, `multimodal_generate`, `multiturn_generate`, `vllm_shutdown`, nested `_generate` retry paths; `servers/generation/src/local_generation.py::LocalGenerationService` OpenAI-compatible streaming helper; `servers/generation/tests/test_litellm_backend.py`; `pyproject.toml` `[project.optional-dependencies]` `generation`/`litellm`; `src/ultrarag/client.py::execute_pipeline` cleanup and `_execute_steps` demo interception; `ui/backend/pipeline_manager.py` generation-service construction and backend override builder; `LocalGenerationService.generate_stream`, `multiturn_generate_stream`.
