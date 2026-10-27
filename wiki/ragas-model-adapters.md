---
type: Concept
title: Ragas model adapters, prompts and caching
description: Client-supplied structured LLMs and dual embedding interfaces drive scores, while shared cache keys can omit model-instance configuration.
tags: [ml, rag, operations, models, caching]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:20:38Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234
    title: Ragas repository
---

**Observed:** `llm_factory` requires a non-empty model and caller client, then selects Instructor/LiteLLM adapter behavior. Collections metrics expect InstructorBaseRagasLLM and modern BaseRagasEmbedding where applicable; legacy wrappers and embedding APIs coexist for compatibility. Model, provider, adapter, prompt and cache choices are part of the evaluation protocol.[^ragas-298b682]

## Model interfaces and defaults

- Instructor client setup chooses provider-specific helpers or a generic patcher; OpenAI/generic paths default to JSON mode.
- InstructorModelArgs defaults include temperature 0.01, top_p 0.1 and max_tokens 1024. Reasoning-model mapping can force temperature 1, remove top_p and rename output-token parameters; Google mapping uses generation_config.
- Sync/async client detection and sync-in-loop bridging differ across wrappers. Do not infer async safety merely from factory acceptance.
- Modern embedding methods are `embed_text(s)` / `aembed_text(s)`; legacy LangChain-style methods are `embed_query/documents`. `embedding_factory` retains auto/legacy branches when clients are omitted, so an explicit modern provider/client avoids ambiguous interface selection.
- The legacy evaluator may construct an OpenAI client/model and inferred embeddings when metric resources were omitted. **Synthesis:** configure resources explicitly to avoid unintended network/billing destinations; no default-client call ran during this compilation.

The default tokenizer is lazily initialized tiktoken o200k_base; HuggingFace tokenization accepts a supplied tokenizer or model path and may load via AutoTokenizer. Offline assets and dependency behavior were not verified.[^ragas-298b682]

## Prompt paths

Legacy PydanticPrompt carries typed input/output models, instructions and examples. Collections prompts use `ragas.prompt.metrics.base_prompt.BasePrompt` rendering plus structured Instructor outputs; custom SimpleLLMMetric can use a formatted string prompt. There is no single BasePrompt abstraction shared by every path. Prompt translation and optimization are covered [separately](ragas-prompt-optimization.md).[^ragas-298b682]

## Cache identity and isolation

`DiskCacheBackend` defaults to `.cache` under process CWD; caching is opt-in. The cacher hashes callable qualified name, normalized args and kwargs, excluding callbacks. Bound-method instance configuration is not automatically included. **Synthesis:** sharing a cache across model/provider objects can reuse a result for identical call arguments even when model configuration differs; namespace cache storage by the full evaluation configuration or explicitly include it in cache-key inputs. Inspecting the key builder establishes this risk, not an executed cross-model collision.[^ragas-298b682]

The source's picklability workaround indicates object persistence concerns, but installed diskcache serialization internals were not inspected. Treat cache directories as trusted local state; this review does not claim reproduced deserialization exploitation.

## Relationships and limits

- Used by [RAG metrics](ragas-rag-metrics.md), [specialized metrics](ragas-specialized-metrics.md), [synthetic data](ragas-testset-generation.md) and [optimizers](ragas-prompt-optimization.md).
- Outbound provider calls and local cache contents are distinct from default analytics; see [security](ragas-security.md).
- No model downloaded, wrapper imported, cache round-trip performed or provider compatibility tested. Adapter/provider bodies were inspected at varying depth.

[^ragas-298b682]: Ragas `298b68274234`, `src/ragas/llms/base.py::llm_factory/_get_instructor_client/InstructorModelArgs/InstructorLLM._map_openai_params/_map_google_params`; `src/ragas/llms/adapters/__init__.py::auto_detect_adapter`; `src/ragas/embeddings/base.py::BaseRagasEmbedding/BaseRagasEmbeddings/embedding_factory`; `src/ragas/evaluation.py::aevaluate`; `src/ragas/tokenizers.py::TiktokenWrapper/HuggingFaceTokenizer/get_default_tokenizer`; `src/ragas/cache.py::DiskCacheBackend/_generate_cache_key/cacher`; `tests/unit/test_cache.py::test_generate_cache_key_bound_method`; `src/ragas/prompt/pydantic_prompt.py::PydanticPrompt`; `src/ragas/prompt/metrics/base_prompt.py::BasePrompt`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
