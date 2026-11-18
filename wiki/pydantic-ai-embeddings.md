---
type: Concept
title: Pydantic AI embeddings
description: Pydantic AI's Embedder — one embed_query/embed_documents pair over six embedding backends, the settings that merge model → embedder → call, and the token counting, test model and instrumentation around it.
tags: [pydantic-ai, embeddings, rag, providers]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-embeddings-guide-2026
    resource: ../raw/guides/embeddings/index.md
    scope: ../raw/guides/embeddings/
    kind: documentation
    revision: sha256:9d0040c53252208f9c0a33843750d2fbc79dda91dbd985a19a19356582e1c3ac
    title: "Embeddings"
---

Pydantic AI's embeddings surface is one class. `Embedder('openai:text-embedding-3-small')` takes the same `<provider>:<model>` string an agent takes (see [models and providers](pydantic-ai-models-and-providers.md)), exposes `embed_query()` for a single text and `embed_documents()` for a batch, and returns an `EmbeddingResult` carrying the vectors, token usage and a `cost()` helper[^pydantic-embeddings-guide-2026] Six backends sit behind it — OpenAI and anything OpenAI-compatible, Google through the Gemini API or Google Cloud, Cohere, VoyageAI, Bedrock, and local Sentence Transformers — and any other provider is a subclass of `EmbeddingModel`[^pydantic-embeddings-guide-2026] What the guide deliberately withholds is the retrieval framework around the call: chunking, vector storage, reranking and retrieval evaluation stay application decisions and are compiled in [RAG retrieval pipeline design](rag-retrieval-pipeline.md)[^pydantic-embeddings-guide-2026] The capture names no Pydantic AI release version anywhere, so every API on this page is version-unknown and the page is `draft` under the `pydantic-ai` domain rule.

## Two calls, one result

| Call | Input | Output |
| --- | --- | --- |
| `await embedder.embed_query(text)` | one query string | `EmbeddingResult` with one vector |
| `await embedder.embed_documents(docs)` | a list of documents | `EmbeddingResult` with one vector per document |

The result is indexable three ways — `result.embeddings[0]`, `result[0]`, and `result['Hello world']` by the original input text — and carries `result.usage.input_tokens` and `result.cost()`[^pydantic-embeddings-guide-2026] `cost()` needs `genai-prices` to hold pricing data for the model; the guide's own example prints `Cost: $0.000000` for two tokens, so the figure demonstrates the call rather than a price[^pydantic-embeddings-guide-2026]

## Provider matrix

| Prefix | Model class | Install extra | Credential | Example → dimensions printed |
| --- | --- | --- | --- | --- |
| `openai:` | `OpenAIEmbeddingModel` | `pydantic-ai-slim[openai]` | `OPENAI_API_KEY` | `text-embedding-3-small` → 1536 |
| `google:` | `GoogleEmbeddingModel` | `pydantic-ai-slim[google]` | `GOOGLE_API_KEY` | `gemini-embedding-001` → 3072 |
| `cohere:` | `CohereEmbeddingModel` | `pydantic-ai-slim[cohere]` | `CO_API_KEY` | `embed-v4.0` → 1024 |
| `voyageai:` | `VoyageAIEmbeddingModel` | `pydantic-ai-slim[voyageai]` | `VOYAGE_API_KEY` | `voyage-3.5` → 1024 |
| `bedrock:` | `BedrockEmbeddingModel` | `pydantic-ai-slim[bedrock]` | standard AWS credentials | `amazon.titan-embed-text-v2:0` → 1024 |
| `sentence-transformers:` | `SentenceTransformerEmbeddingModel` | `pydantic-ai-slim[sentence-transformers]` | none (local) | `lightonai/DenseOn` → 768 |

Only the VoyageAI and Sentence Transformers sections state the slim install alone; the other four say `pydantic-ai` or `pydantic-ai-slim` with the extra, which reads as the same choice rather than a different one[^pydantic-embeddings-guide-2026]

### OpenAI, and everything OpenAI-compatible

`text-embedding-3-*` accepts dimension reduction through `EmbeddingSettings(dimensions=256)`, which changes the printed vector length to 256[^pydantic-embeddings-guide-2026] Because `OpenAIEmbeddingModel` reuses the same provider system as `OpenAIChatModel`, three other routes work unchanged: an `AsyncAzureOpenAI` client handed to `OpenAIProvider(openai_client=...)`, a generic `OpenAIProvider(base_url=..., api_key=...)` for any compatible endpoint, and the shorthand prefixes `azure:`, `ollama:` and `vllm:` when a dedicated provider class exists[^pydantic-embeddings-guide-2026] The `vllm:` route reads `VLLM_BASE_URL` and, when the server is authenticated, `VLLM_API_KEY`[^pydantic-embeddings-guide-2026]

### Google: two endpoints and two conditioning schemes

`google:` reaches the Gemini API and `google-cloud:` reaches Google Cloud (formerly Vertex AI), the latter configured with `GoogleCloudProvider(project=..., location=...)`[^pydantic-embeddings-guide-2026] Dimension reduction works here too — `gemini-embedding-001` printed at 768[^pydantic-embeddings-guide-2026]

The conditioning mechanism splits by model, and the two settings are not interchangeable:

| Model family | Setting | Default per call type | Opt-out |
| --- | --- | --- | --- |
| `gemini-embedding-2` | `google_task`, which prepends a task instruction to the text | `'search result'` when unset | `google_task='raw'` embeds text verbatim |
| other Google models | `google_task_type` | `embed_query()` → `RETRIEVAL_QUERY`, `embed_documents()` → `RETRIEVAL_DOCUMENT` | set the field explicitly |

`google_task` accepts `'search result'`, `'question answering'`, `'fact checking'`, `'code retrieval'`, `'classification'`, `'clustering'` and `'sentence similarity'`; the retrieval-style tasks prefix queries and documents differently, and the same task applies to both sides of a pair[^pydantic-embeddings-guide-2026] The wrong pairing is ignored with a warning rather than an error — `google_task` on any other model, `google_task_type` on `gemini-embedding-2`[^pydantic-embeddings-guide-2026]

Usage accounting has a Gemini-specific hole: when the API omits token usage, `result.usage.unmeasured_requests` is `1`, instrumentation omits the automatic `operation.cost` estimate, and an explicit `result.cost()` computes from zero token counts — so it can return a zero estimate even when pricing data exists[^pydantic-embeddings-guide-2026]

### Cohere and VoyageAI

Cohere exposes `cohere_truncate='END'` to truncate over-long inputs instead of erroring, plus `cohere_max_tokens` to cap tokens per input, alongside `dimensions`[^pydantic-embeddings-guide-2026] VoyageAI exposes `dimensions` and `voyageai_input_type='document'`, which overrides the query/document distinction for every request the embedder makes[^pydantic-embeddings-guide-2026] The guide's own model table routes VoyageAI's `voyage-code-3`, `voyage-law-2` and `voyage-finance-2` at domain-specific retrieval[^pydantic-embeddings-guide-2026]

### Bedrock: three model families with different limits

| Family | Model | Dimensions | Input limit |
| --- | --- | --- | --- |
| Titan | `amazon.titan-embed-text-v1` | 1536, fixed | 8K tokens |
| Titan | `amazon.titan-embed-text-v2:0` | 256/384/1024, default 1024 | 8K tokens |
| Cohere Embed | `cohere.embed-english-v3` | 1024, fixed | 512 tokens |
| Cohere Embed | `cohere.embed-multilingual-v3` | 1024, fixed | 512 tokens |
| Cohere Embed | `cohere.embed-v4:0` | 256/512/1024/1536, default 1536 | 128K tokens |
| Nova | `amazon.nova-2-multimodal-embeddings-v1:0` | 256/384/1024/3072, default 3072 | 8K tokens |

Per-family settings follow the same split[^pydantic-embeddings-guide-2026]: Titan v2 gets `bedrock_titan_normalize` (default `True`, unsupported on v1); Cohere gets `bedrock_cohere_input_type` (default `'search_query'`/`'search_document'`, also `'classification'`/`'clustering'`), `bedrock_cohere_truncate` (default `'NONE'`, meaning error on overflow) and `bedrock_cohere_max_tokens` (default 128000, v4 only); Nova gets `bedrock_nova_truncate` and `bedrock_nova_embedding_purpose` (default `'GENERIC_RETRIEVAL'`/`'GENERIC_INDEX'`, also `'TEXT_RETRIEVAL'`, `'CLASSIFICATION'`, `'CLUSTERING'`).

Throughput is a deployment decision, not a provider default: Titan and Nova do not support batch embedding, so each input is its own API request, run concurrently with a maximum of 5 in flight by default and adjustable through `bedrock_max_concurrency`[^pydantic-embeddings-guide-2026] Routing has three layers — geographic prefixes (`us.`, `eu.`, `apac.`) inside the model string, `bedrock_inference_profile` for an application inference profile ARN while the base model name still drives capability detection, and a hand-built `BedrockProvider(region_name=..., aws_access_key_id=..., aws_secret_access_key=...)` for explicit credentials[^pydantic-embeddings-guide-2026]

### Sentence Transformers: no API call at all

`SentenceTransformerEmbeddingModel` runs the model in process, downloaded from Hugging Face on first use, and the guide sells it on privacy, volume cost, offline use and picking a model per language or domain[^pydantic-embeddings-guide-2026] Asymmetric models are handled for you: `lightonai/DenseOn` (149M parameters) gets its `query:` / `document:` prompts applied by `embed_query()` and `embed_documents()` automatically[^pydantic-embeddings-guide-2026] Device and normalization are settings (`sentence_transformers_device='cuda'`, `sentence_transformers_normalize_embeddings=True`), and an already-built `SentenceTransformer` can be wrapped in `SentenceTransformerEmbeddingModel(st_model)` when initialization needs to happen outside Pydantic AI[^pydantic-embeddings-guide-2026]

## Settings merge in one direction

`EmbeddingSettings` carries two provider-neutral fields: `dimensions` (OpenAI, Google, Cohere, Bedrock, VoyageAI) and `truncate`, which turns an over-length input into a truncated one instead of an error (Cohere, Bedrock, VoyageAI)[^pydantic-embeddings-guide-2026] Settings layer model → embedder → individual call, and merge key by key: a later layer overrides the same key, while a key set only in an earlier layer survives — so `EmbeddingSettings(dimensions=512)` on the embedder plus `EmbeddingSettings(dimensions=256)` on one call prints 256 for that call[^pydantic-embeddings-guide-2026]

## Counting tokens before you spend them

`await embedder.count_tokens(text)` returns a count without embedding, and `await embedder.max_input_tokens()` returns the model's limit or `None` when unknown[^pydantic-embeddings-guide-2026] The guide's printed values are 7 tokens for a short sentence and `Max tokens: 1024` for `text-embedding-3-small`; the latter is recorded as printed, and neither the capture nor this ingest reconciles it against OpenAI's model documentation[^pydantic-embeddings-guide-2026]

## Failure, testing and instrumentation

Embedding requests raise the same taxonomy as chat requests — a `ModelAPIError`, and an instance of a category such as `ModelRateLimitError` or `ModelUnavailableError` when the provider explains itself — so one `except` clause covers agents and embedders alike[^pydantic-embeddings-guide-2026] See [model API errors](pydantic-ai-model-api-errors.md) for the categories and the retry rule.

`TestEmbeddingModel` makes embeddings deterministic — the assertion in the guide's test is `[1.0] * 8` — and is installed per embedder with `with embedder.override(model=test_model)`, which also records the settings used in `test_model.last_settings`[^pydantic-embeddings-guide-2026] `ALLOW_MODEL_REQUESTS = False` extends the model-level guard to embedding calls, so a forgotten override raises; `TestEmbeddingModel` and `SentenceTransformerEmbeddingModel` keep working because neither reaches a provider[^pydantic-embeddings-guide-2026] The guard reaches `count_tokens()` only when tokenization is server-side: Google and Cohere count through an API call and are blocked, OpenAI tokenizes locally with `tiktoken` and is not[^pydantic-embeddings-guide-2026]

Instrumentation is the same switch as for models: `Embedder('openai:...', instrument=True)` for one embedder or `Embedder.instrument_all()` globally, with `logfire.configure()` doing the export[^pydantic-embeddings-guide-2026] See [Pydantic AI observability](pydantic-ai-observability.md).

## Writing an embedding model

A custom provider subclasses `EmbeddingModel`, implements `model_name`, `system` and `async embed(inputs, *, input_type: EmbedInputType, settings)`, calls `self.prepare_embed(inputs, settings)` first, and returns an `EmbeddingResult(embeddings=..., inputs=..., input_type=..., model_name=..., provider_name=...)`[^pydantic-embeddings-guide-2026] `WrapperEmbeddingModel` is the narrower hook for adding caching or logging around an existing model rather than implementing a provider[^pydantic-embeddings-guide-2026]

## Limits

- Single vendor guide for its own library, naming no Pydantic AI version, no publication date and no release in which `Embedder` appeared; every API, default and printed vector length above is **Reported** from that guide and dated only by this capture[^pydantic-embeddings-guide-2026]
- No package was installed, no provider called, no vector computed, no embedding written, no test run and no span exported in this ingest, so nothing here is **Reproduced**.
- The printed outputs (`1536`, `3072`, `1024`, `768`, `Tokens: 7`, `Max tokens: 1024`, `Cost: $0.000000`) are the guide's own example output, not measurements; the `max_input_tokens()` figure in particular is unreconciled[^pydantic-embeddings-guide-2026]
- Prices are absent: the guide shows how to compute cost, never what a model costs, and the `genai-prices` requirement is stated without a coverage list — [Jev structured scoring judge](jev-structured-scoring-judge.md) records a sibling case where a missing pricing entry left cost empty.
- The model-name table (embedding models per use case) is a snapshot of what existed when the guide was written; only MTEB and the model cards are offered as the current source of truth[^pydantic-embeddings-guide-2026]

## Relationships

- **Shares its addressing scheme with** [models and providers](pydantic-ai-models-and-providers.md): one `<provider>:<model>` string, the same provider classes, and the same OpenAI-compatible escape hatch.
- **Feeds** the retrieval half in [RAG retrieval pipeline design](rag-retrieval-pipeline.md), which covers the chunking, storage, reranking and evaluation the guide leaves open.
- **Raises** the shared taxonomy in [model API errors](pydantic-ai-model-api-errors.md).
- **Is traced by** [Pydantic AI observability](pydantic-ai-observability.md) through `instrument=True` or `Embedder.instrument_all()`.
- **Mirrors** the direct-call shape of [image generation](pydantic-ai-image-generation.md): a generator/embedder you call yourself, beside the agent capability that lets a model call it.

[^pydantic-embeddings-guide-2026]: Pydantic Docs, "Embeddings", <https://pydantic.dev/docs/ai/guides/embeddings/>, 4,090 words as declared, 4,271 by local `wc -w`, no publication date and no version named; local capture `raw/guides/embeddings/index.md`, content digest sha256:9d0040c5. §"Quick Start" (lines 20–49) for `Embedder`, `embed_query`/`embed_documents` and the 1536/3-document output; §"Embedding Result" (lines 50–84) for the three access paths, `usage.input_tokens`, `cost()` and `genai-prices`; §"Choosing a model" (lines 85–97) for the use-case-to-model table and the MTEB/model-card/own-evaluation advice; §"Providers" (lines 153–837) for the six provider sections, the install extras, the credentials, the OpenAI-compatible routes and `VLLM_BASE_URL`/`VLLM_API_KEY`, `google-cloud:` with `GoogleCloudProvider`, the dimension-control examples, `google_task`/`google_task_type` and their defaults and warnings (lines 369–411), the `unmeasured_requests`/`operation.cost` note (line 320), Cohere and VoyageAI settings, the Bedrock model table and per-family settings (lines 584–668), `bedrock_max_concurrency` (lines 669–693), regional prefixes and `bedrock_inference_profile` (lines 694–752), and the Sentence Transformers device/instance wrappers (lines 753–837); §"Settings" (lines 838–870) for `dimensions`/`truncate` and the model→embedder→call merge order; §"Token Counting" (lines 871–897) for `count_tokens`/`max_input_tokens` and the printed 7/1024; §"Handling Errors" (lines 898–901) for the shared `ModelAPIError` taxonomy; §"Testing" (lines 902–929) for `TestEmbeddingModel`, `override`, `last_settings`, `ALLOW_MODEL_REQUESTS` and the per-provider tokenization caveat; §"Instrumentation" (lines 930–951) for `instrument=True` and `instrument_all()`; §"Building Custom Embedding Models" (lines 985–1027) for `EmbeddingModel`, `prepare_embed`, `EmbedInputType`, `EmbeddingResult` and `WrapperEmbeddingModel`. Evidence class: **Reported** — vendor documentation for its own library; nothing was installed, called or measured.
