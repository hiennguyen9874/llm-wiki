---
type: Concept
title: Hindsight LLM, embedding and reranker providers
description: Which LLM, embedding and reranker providers Hindsight supports, their defaults, and the provider abstraction in code.
tags: [agent-memory, hindsight, llm, embeddings, reranker]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: config-code
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/config.py
    kind: code
    revision: eb963cb
    title: HindsightConfig
  - id: config-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/configuration.mdx
    kind: documentation
    revision: eb963cb
    title: Configuration developer doc
---

Hindsight needs an LLM (fact extraction, consolidation, reflect), an embedding model and optionally a reranker; all three are pluggable through env vars, and the LLM layer is a provider interface with ~30 implementations.[^readme][^config-code] The provider list changes quickly, hence the `stale_after` date.

## LLM providers

- **Interface:** `engine/llm_interface.py::LLMInterface`; factory `engine/llm_wrapper.py::create_llm_provider`; implementations in `engine/providers/` (OpenAI-compatible, OpenAI Responses, Anthropic, Gemini, LiteLLM and LiteLLM router, llama.cpp, plus subscription-backed `claude_code`, `codex`, `cursor`, `github_copilot`, `chatgpt`) (Observed).[^config-code]
- **Names in `PROVIDER_DEFAULT_MODELS`:** openai, openai-responses, anthropic, gemini, groq, minimax, deepseek, zai, opencode-go, atlas, meta, ollama, ollama-cloud, llamacpp, lmstudio, vertexai, openai-codex, chatgpt, claude-code, cursor, github-copilot, mock, none, litellm, bedrock, volcano, openrouter, requesty, fireworks, nous, xai-oauth; `litellmrouter` is added in the factory.[^config-code]
- README advertises "25+ providers" and subscription-based auth without API keys (openai-codex, claude-code, cursor, github-copilot) (Reported).[^readme]
- Config also supports multi-LLM failover/round-robin and a built-in llama.cpp provider that auto-downloads a small Gemma model (~3.5 GB) (Reported).[^config-doc]

## Embeddings and rerankers

| Role | Env var | Default | Options |
| --- | --- | --- | --- |
| Embeddings | `HINDSIGHT_API_EMBEDDINGS_PROVIDER` | `local` (`BAAI/bge-small-en-v1.5`) | local, onnx, tei, openai, gemini/google, openrouter, requesty, hindsight, zeroentropy, nvidia, cohere |
| Reranker | `HINDSIGHT_API_RERANKER_PROVIDER` | `local` (`hindsight-ai/hs-rerank-1`) | local, tei, cohere, openrouter, flashrank, onnx, litellm, litellm-sdk, zeroentropy, siliconflow, nvidia, google, alibaba, decision_model |
| Decision model | `HINDSIGHT_API_DECISION_MODEL_PROVIDER` | `none` | none, hindsight, typesafe, cloudflare, openai — see [Decision models](hindsight-decision-models.md) |

Observed in `config.py` and `engine/cross_encoder.py::_create_cross_encoder_backend`.[^config-code]

## Relationships

Set via [Storage and configuration](hindsight-storage-and-configuration.md); used by [Retain](hindsight-retain-pipeline.md) (extraction, embeddings) and [Recall](hindsight-recall-pipeline.md) (reranker). Per-bank LLM routing is available through the `bank-llm-routing` extension ([Extensions](hindsight-extensions-defense-webhooks.md)).

[^readme]: `README.md` § "Quick Start → Docker".
[^config-code]: `hindsight-api-slim/hindsight_api/config.py::PROVIDER_DEFAULT_MODELS`; `engine/llm_wrapper.py`; `engine/providers/`; `engine/cross_encoder.py`.
[^config-doc]: `hindsight-docs/docs/developer/configuration.mdx` § LLM provider, multi-LLM failover.
