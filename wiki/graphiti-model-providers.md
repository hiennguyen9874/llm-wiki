---
type: Concept
title: Graphiti model and provider configuration
description: OpenAI, Azure OpenAI, Gemini, and OpenAI-compatible clients, structured-output modes, per-prompt model routing, and decision-model dedupe.
tags: [rag, ml, models, providers]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:45:00Z }
stale_after: 2027-01-24
sources:
  - id: graphiti-readme
    resource: ../raw/graphiti.md
    kind: documentation
    title: Graphiti README — A Framework for Building Temporal Knowledge Graphs (getzep/graphiti)
---

**Reported:** Graphiti takes three pluggable model roles — LLM client, embedder, and cross-encoder reranker — and defaults all of them to OpenAI; Azure OpenAI, Google Gemini, and any OpenAI-compatible `/v1` endpoint (hosted or local) are supported through alternative client classes, with structured JSON output treated as a compatibility requirement rather than an option.[^graphiti-readme] **Synthesis:** the notable design choice is that model choice can be routed *per prompt stage* through `llm_runtime`, which turns dedupe and extraction into separately tunable cost/quality levers instead of one global model setting.[^graphiti-readme]

## Client matrix

| Target | Documented binding |
| --- | --- |
| OpenAI (default) | Library default for both inference and embeddings; requires `OPENAI_API_KEY` |
| Azure OpenAI | `AzureOpenAILLMClient` + `AzureOpenAIEmbedderClient` over a standard `AsyncOpenAI` client pointed at `https://<resource>.openai.azure.com/openai/v1/`; deployment names must match Azure deployment names |
| Google Gemini | `GeminiClient`, `GeminiEmbedder`, `GeminiRerankerClient` via the `google-genai` extra; API key and model IDs configured per client |
| OpenAI-compatible hosted or local | `OpenAIGenericClient` (explicitly *not* `OpenAIClient`) plus `OpenAIEmbedder` and `OpenAIRerankerClient` with a custom `base_url` |
| Anthropic / Groq | Available as LLM extras alongside the OpenAI default |

The Gemini reranker defaults to `gemini-2.5-flash-lite` and uses the same boolean-classification approach as the OpenAI reranker, relying on log probabilities to rank passage relevance.[^graphiti-readme]

## Structured output compatibility

`OpenAIGenericClient` exposes `structured_output_mode` with two documented values: `json_schema` (the default; requests native structured output through `response_format`, best where the provider enforces the schema via constrained decoding) and `json_object` (plain JSON mode with the schema injected into the prompt, recommended where a server accepts `json_schema` but does not actually constrain output).[^graphiti-readme] The generic client also raises the default max-token limit to 16K versus 8K for local models, strips Markdown ` ```json ` fences from responses, and is paired with the standing advice to keep `SEMAPHORE_LIMIT` low for local servers.[^graphiti-readme]

## Prompt-level routing with `llm_runtime`

An opt-in runtime lets one Graphiti instance route different prompt stages to different provider models: each `LLMTransport` wraps one provider client and enumerates its models, each `LLMModel` binds a model ID to that transport, and `PromptRoutes` assigns models to stages such as `extract_nodes` (`extract_attributes`) and `dedupe_edges` (`resolve_edge`); unrouted prompts use the default model.[^graphiti-readme]

Documented constraints: `llm_runtime` cannot be combined with `llm_client` or `prompt_library`; response schemas stay fixed; `LLMModel` has no `small_id`, and the runtime passes `model_size` only for legacy compatibility, so a "small" model is chosen by explicitly routing to it rather than by size metadata.[^graphiti-readme] Without `llm_runtime`, legacy `LLMConfig.small_model` behaviour is retained. GLiNER2 binds model objects at initialization and does not support per-prompt routing.[^graphiti-readme]

## Dedupe decision models

Node dedupe and edge resolution can be routed to specialised decision models instead of a generative LLM: `JevClient` (TypeSafe-hosted, requires `JEV_API_KEY`, defaults of **0.7** duplicate threshold and **0.8** contradiction threshold) and `OpenAIDecisionsClient` (OpenAI Decisions API) both answer typed questions with probabilities and do not generate text.[^graphiti-readme] The README restricts them to `dedupe_nodes.nodes` and `dedupe_edges.resolve_edge`, and warns against using them for extraction, summaries, or other generation tasks.[^graphiti-readme]

**Privacy consequence (Reported):** because Jev is a hosted decision service, "Graphiti sends dedupe prompt content to TypeSafe".[^graphiti-readme]

## Relationships

- **Part of:** [Graphiti](graphiti.md).
- **Used by:** [episode ingestion](graphiti-episode-ingestion.md) for extraction and deduplication, and [retrieval and ranking](graphiti-retrieval.md) for embeddings and reranking.
- **Constrains:** [security boundaries](graphiti-security-telemetry.md) — third-party provider and decision-service routing moves episode content off-host.

## Evidence limits

**Reported only.** Model names, default reranker choice, token limits, and thresholds come from README prose and code samples; no client was instantiated, no provider was called, and no extraction-quality or cost comparison exists here. Provider-side structured-output behaviour, the `spec/llm-runtime.md` reference, and the Jev/OpenAI Decisions example directories were not inspected.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): “Installation” (requirements, provider extras, structured-output IMPORTANT note), “Using Graphiti with Azure OpenAI”, “Using Graphiti with Google Gemini”, “Using Graphiti with OpenAI-compatible providers and local LLMs” (incl. “Structured output and small models”), “Configurable Prompts” (prompt library and `llm_runtime` routing), and “Jev dedupe” / “OpenAI Decisions dedupe”.
