---
type: Concept
title: LightRAG model roles and integrations
description: Independent extraction, keyword, answer and vision roles, embedding shape contracts, provider bindings, and concurrency limits.
tags: [rag, ml, integrations]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:55:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
---

**Observed:** LightRAG routes extraction, keyword generation, answer generation and vision analysis through four role-specific callables and queues. Embeddings and reranking have separate contracts and concurrency groups. **Synthesis:** a provider adapter, a server-selectable binding, and a model supporting every role are distinct integration claims; none establishes real-provider compatibility without execution.[^lightrag-aaebfe1]

## Role configuration

`ROLES` declares `extract`, `keyword`, `query`, and `vlm`, with `EXTRACT_`, `KEYWORD_`, `QUERY_`, and `VLM_` environment prefixes. README news uses the plural “KEYWORDS”, but the inspected registry/configuration uses singular `KEYWORD`. `RoleLLMConfig` supports function, kwargs, max-async, timeout and metadata overrides; missing values generally inherit base settings. Queue wrappers are built per role; the base callable is not itself the universal role queue.[^lightrag-aaebfe1]

**Observed:** runtime builder/metadata methods support updating role configurations and rebuilding wrappers. Effective kwargs distinguish inherited settings from cross-provider overrides. Secret-looking metadata keys are scrubbed for observability; this is not a guarantee that arbitrary provider/model output or every log is secret-free.[^lightrag-aaebfe1]

## Provider surfaces

| Surface | Server-selectable choices observed |
| --- | --- |
| LLM | lollms, Ollama, OpenAI, openai-ollama, Azure OpenAI, Bedrock, Gemini |
| Embeddings | lollms, Ollama, OpenAI, Azure OpenAI, Bedrock, Jina, Gemini, VoyageAI |
| Rerank | null, Cohere, Jina, Aliyun |

**Observed:** default LLM and embedding binding is Ollama. The repository contains additional adapter modules, but module presence does not mean those names are accepted by server CLI choices. SDK users can inject callables. The empty `llm/__init__.py` does not re-export a unified adapter catalog. OpenAI's adapter accepts dict response-format payloads, rejects typed/Pydantic formats, retains a deprecated keyword-extraction shim, and distinguishes selected retryable errors. Other provider implementations were not comparably audited.[^lightrag-aaebfe1]

## Embedding contract

**Observed:** `EmbeddingFunc` declares dimension, wrapped callable, optional token size/model name, dimension forwarding and asymmetric support. Results must be a two-dimensional batch with the expected row count and embedding dimension; the wrapper does not silently reshape, pad or slice. Nested wrappers may be unwrapped with bounded depth. Query/document context supports asymmetric prefixes; retrieval passes `context="query"`.[^lightrag-aaebfe1]

**Synthesis:** supplying the same vector dimension does not prove the same semantic embedding space. Model changes need the [embedding recovery workflow](lightrag-embedding-recovery.md), not merely a new endpoint. README model recommendations and advertised quality are Reported guidance, not checked evaluations.[^lightrag-aaebfe1]

## Concurrency and timeout boundaries

**Observed:** `priority_limit_async_func_call` uses a priority queue and optional global concurrency-group coordination. With a configured base timeout, its execution timeout is twice that setting and maximum task duration adds a further 15 seconds. Defaults include LLM timeout 240 seconds, embedding timeout 30 seconds, and rerank timeout 30 seconds. Role limits can override the base LLM limit; document task fan-out is a separate layer and does not change just because a role limit changes.[^lightrag-aaebfe1]

**Observed:** embedding and rerank wrappers have distinct concurrency groups, rather than sharing the answer-role slots. Provider retries, wrapper deadlines, and pipeline cancellation are layered; doubling the configured timeout is a wrapper property, not evidence of a provider's own timeout semantics.[^lightrag-aaebfe1]

## Relationships

- **Used by:** [Extraction and merge](lightrag-extraction.md), [retrieval](lightrag-retrieval.md), and [multimodal analysis](lightrag-parsing-multimodal.md).
- **Depends on:** [Packaging/deployment](lightrag-deployment.md) for optional SDKs and offline assets.
- **Related:** [RAG-Anything runtime stack](rag-anything-stack-operations.md) describes a separate older package's dependency constraint, not guaranteed interchangeability with this integrated release.

## Evidence limits

Role runtime and selected OpenAI/rerank paths inspected statically; most provider bodies, actual rate limits, model output schemas, asymmetric-prefix correctness, queue timing and live hot updates remain unverified. See [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`: `lightrag/llm_roles.py::ROLES, RoleLLMConfig, _RoleLLMMixin`; `lightrag.py::LightRAG.__post_init__, _build_global_config`; `api/config.py` binding choices and role options; `api/lightrag_server.py::initialize_rag`; `utils.py::EmbeddingFunc, priority_limit_async_func_call, get_llm_cache_identity`; `constants.py::DEFAULT_LLM_TIMEOUT, DEFAULT_EMBEDDING_TIMEOUT, DEFAULT_RERANK_TIMEOUT`; `llm/openai.py::_validate_openai_response_format, openai_complete_if_cache`; `llm/__init__.py` empty file; `rerank.py` adapters; README role guidance and concurrency section; adapter directory inventory (presence only).
