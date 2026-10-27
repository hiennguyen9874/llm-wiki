---
type: Concept
title: LightRAG query results, citations, streaming, and caches
description: Structured retrieval and answer APIs, prompt-based citations, NDJSON streaming, answer-cache identity, and no-context semantics.
tags: [rag, api, citations, caching]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:15:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
---

**Observed:** LightRAG separates retrieval data from generated answers, constructs references from surviving chunks, and instructs rather than deterministically enforces the LLM's citation prose. Streaming carries generation after retrieval; caches can turn a streaming request into a plain cached result. **Synthesis:** retrieved references are evidence availability, not proof that every generated assertion cites or faithfully uses that evidence.[^lightrag-aaebfe1]

## SDK and HTTP contracts

| Surface | Behavior observed in implementation |
| --- | --- |
| `aquery` / sync wrapper | Projects answer content or response iterator from the richer result |
| `aquery_data` | Retrieval-only structured data; forces context-only and non-streaming |
| `aquery_llm` | Retrieval data plus `llm_response` |
| `POST /query` | Non-streaming answer; reference exposure controlled at HTTP layer |
| `POST /query/data` | Structured retrieval with references |
| `POST /query/stream` | `application/x-ndjson` |

**Observed:** all core queries reject empty text; non-bypass queries require at least three English-equivalent characters (CJK/Hangul count two each). Query API ceilings include 64 Ki characters, top-k 1,000, and individual token-budget limits of 1,000,000. No-result paths can return failure/no-results metadata and a canned response marked `llm_generated=False`, rather than invoking a model to improvise unsupported evidence. Bypass returns generation without retrieval data.[^lightrag-aaebfe1]

## References versus answer citations

**Observed:** `generate_reference_list_from_chunks` groups surviving chunks by file path, sorts files by chunk frequency then first occurrence, and assigns reference IDs. Unknown/empty source paths do not receive normal references. The first reference therefore need not be the top-ranked retrieval hit. Rendered chunks carry reference IDs into the prompt.[^lightrag-aaebfe1]

**Observed:** default RAG/naive prompts request a `### References` section, at most five relevant citations, and no footnote syntax. The inspected answer path does not parse/repair emitted citation markers. The HTTP `references` array is generated independently and may be longer or ordered differently. `include_chunk_content` optionally attaches retrieved text to each file reference. The core `QueryParam.include_references` declaration is not the controlling HTTP gate.[^lightrag-aaebfe1]

**Observed documentation/UI tension:** shipped suggested user prompts can ask for ignoring the references format or using footnotes despite the default system prompt forbidding them. **Synthesis:** citation style is a configurable prompt convention, not an invariant enforced by a citation validator.[^lightrag-aaebfe1]

## NDJSON and progress

- Default stream: optional references line, then response-fragment lines. A cached/plain result may be emitted as one answer line with the generated flag.
- With `include_progress=True`, progress can precede references; a final response-time line is also emitted. Clients must not assume references are always the first line.
- Observed progress vocabulary includes keyword extraction, entities, relations, chunks, reranking, and generation. Retrieval/context preparation normally finishes before generation fragments begin.
- Model streams are not saved as answer-cache values. A `stream=True` request can read a cached string instead of receiving an iterator. Truncated non-streaming answers are excluded from cache writes.[^lightrag-aaebfe1]

## Cache identity and durability

**Observed:** keys are flattened as `{mode}:{cache_type}:{hash}`. Keyword caches include mode, query, language and keyword-role identity. Answer keys include mode/query, response type, retrieval counts/budgets, keyword lists, composed user instructions, the `enable_rerank` flag and content-headings flag, effective graph chunk-selection settings, caller system prompt, and query-role identity. History-bearing requests bypass answer-cache reads and writes; conversation history is not simply omitted while continuing to cache answers.[^lightrag-aaebfe1]

**Observed:** retrieval and reranking execute before the answer-cache read. A hit reuses answer text while structured data/references come from the current retrieval. `MIN_RERANK_SCORE`, rerank binding/model/host, and embedding model are not answer-key components. **Synthesis:** cached prose can therefore accompany a changed reference set after ranking/model changes; a cache hit is not a frozen evidence bundle.[^lightrag-aaebfe1]

**Observed:** query/keyword cache and extraction-mode cache have separate enable flags, both default true. Non-secret model identity includes role/binding/model/host but deliberately excludes credentials and provider options. **Synthesis:** changing provider generation options alone is not guaranteed to produce a distinct cache identity; inspect effective prompt/model configuration when diagnosing stale answers. `_query_done` uses a chunk-before-cache fence rather than independently publishing unreachable extraction cache rows.[^lightrag-aaebfe1]

## Relationships

- **Uses:** [Retrieval and ranking](lightrag-retrieval.md) to establish the surviving context.
- **Depends on:** [Concurrency/durability](lightrag-concurrency.md) for cache publication ordering.
- **Used by:** [API and frontend](lightrag-api-ui.md).
- **Uses:** [Model roles](lightrag-models.md) for distinct keyword and answer identities.

## Evidence limits

Static implementation and selected assertion inspection, not executed protocol or citation-accuracy validation. Provider tokenization/reasoning streams and all client reconnect/error scenarios remain unverified; see [source map](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`: `lightrag/lightrag.py::LightRAG.aquery, aquery_data, aquery_llm, _query_done`; `query_validation.py::MIN_RAG_QUERY_WEIGHT, meets_min_rag_query_weight, validate_rag_query`; `constants.py` request ceilings; `api/routers/query_routes.py::QueryRequest, _build_stream_generator` and query/data/stream handlers; `operate.py::QueryProgress, _answer_cache_kv, kg_query, naive_query, extract_keywords_only`; `utils.py::generate_reference_list_from_chunks, render_chunks_context_text, handle_cache, save_to_cache, get_llm_cache_identity`; `prompt.py::PROMPTS[rag_response, naive_rag_response, kg_query_context, naive_query_context]`; `lightrag_webui/src/lib/queryDefaults.ts::suggestedUserPrompts`; selected assertions in `tests/llm/test_query_cache_conversation_history.py`, `test_query_cache_kg_chunk_selection.py`, `test_query_cache_user_prompt_prefix.py`, `test_query_truncated_response_not_cached.py`.
