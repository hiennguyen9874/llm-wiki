---
type: Concept
title: Hy Memory SDK API, config and HTTP server
description: Public surface of the hy-memory SDK — HyMemoryClient methods, modes, env-driven MemoryConfig keys, the stdlib HTTP server routes, and input constraints.
tags: [agent-memory, hy-memory, sdk, api, configuration]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# Hy Memory SDK API, config and HTTP server

`HyMemoryClient` is a stateless, thread-safe client whose business isolation keys (user, agent, session, workspace) are passed per call; it is constructed with `mode` in `lite|pro|ultra` and an env-driven `MemoryConfig` (`hy_memory/client.py::HyMemoryClient.__init__`, `VALID_MODES`).[^hy-memory] A stdlib `ThreadingHTTPServer` wraps it for sidecar use (`hy_memory/server.py`).[^hy-memory]

## Client surface

- Methods: `add`/`async_add`, `add_extracted` (skip extraction, reconcile caller-supplied facts), `finalize_session`, `search`/`async_search`, `get`, `update`, `delete`, `delete_all`, `list_memories`, `memory_stats`, `get_user_basic_info`, `get_user_profile`, `clone_user`, `evolve`, `sweep`, `get_metrics`, `history`, `get_write_outcome`, `build_memory_graph`, `build_entity_store`, `close` (`hy_memory/client.py`, class body).[^hy-memory]
- Sync methods wrap async ones through persistent loop threads; `add()` uses the write loop and `search()` the search loop (`client.py::_LoopThread`, `search`). See [runtime and concurrency](hy-memory-runtime-concurrency-and-observability.md).[^hy-memory]
- Mode behaviour: `lite` forces `enable_graph=False` and searches raw-only, ignoring `layers`/`scene`/`search_mode`; `pro` reads `MEMORY_ENABLE_GRAPH` (default false); `ultra` forces graph on, and `evolve()` raises `RuntimeError` unless mode is `ultra` (`client.py::__init__`, `_async_search_impl` lite branch, `evolve`). System 2 never runs inside `add()` (`docs/usage.md::evolve`).[^hy-memory]
- Scene routing, per-call `embed_override`, `source` / `include_sources` / `exclude_sources` isolation, and automatic scene classification are described in `README.md::Routing, Source Isolation & Advanced APIs`; scenes are detailed in [Working and coding memory](hy-memory-working-coding-memory.md).[^hy-memory]

## Configuration keys

`MemoryConfig` aggregates vector, graph, cache, LLM, embedder, recall, time-window, extractor, API, pipeline-route, history, coding and basic-profile configs, each populated from env in `__post_init__` (`hy_memory/config.py::MemoryConfig`, `from_env`, `from_dict`).[^hy-memory]

| Area | Keys and defaults (`config.py` per-dataclass `__post_init__`) |
|---|---|
| Core | `MEMORY_MODE` (`pro`), `MEMORY_DATA_DIR` (`~/.hy_memory`), `MEMORY_LANGUAGE` |
| LLM | `MEMORY_LLM_MODEL` (`gpt-4.1-nano`), key falls back `MEMORY_LLM_API_KEY`→`LLM_API_KEY`→`OPENAI_API_KEY`, base URL likewise, temperature 0.1 (`none/omit/null` omits it), max tokens 1024 (agent 2000), timeout 180 s, retries 5, `…_EXTRA_HEADERS/BODY` JSON (invalid JSON silently ignored) |
| Embedder | `MEMORY_EMBEDDER_MODEL` (`text-embedding-3-small`), `MEMORY_EMBEDDING_DIMS` (1536), batch size 64 |
| Vector | `MEMORY_VECTOR_STORE` (`chroma`), `MEMORY_COLLECTION_NAME` (`agent_memories`), persist dir under data dir |
| Graph | `MEMORY_GRAPH_PROVIDER` (`kuzu`), `NEO4J_*`/`MEMGRAPH_*`, many `MEMORY_GRAPH_*` weights |
| Cache | `MEMORY_CACHE_BACKEND` (`sqlite`\|`mysql`, anything else raises) |

Recall defaults: `default_limit=10`, `max_limit=100` (`config.py:322` region).[^hy-memory] Prompt language precedence is per-call `language` > `MEMORY_LANGUAGE` > zh/en auto-detect; 11 languages ship (`hy_memory/prompts/__init__.py`; `docs/env_reference.md` core table).[^hy-memory]

## HTTP server

`python -m hy_memory.server` (default `127.0.0.1:19527`) exposes `POST /api/v1/{add,add_extracted,search,user_profile,list,delete_all}`, `GET|PUT|DELETE /api/v1/memories/{id}`, `GET /api/v1/metrics`, `GET /api/v1/status` (deep check), `GET /healthz` (static), `GET /health` (event-loop liveness, 503 `loop_blocked` on 2 s timeout), `GET /info`. Errors map `AmbiguousMemoryIdError`→409, `ValueError`→400, else 500. There is **no authentication** and CORS is `*`; it is intended for local/sidecar use (`hy_memory/server.py::do_GET/do_POST`, module docstring).[^hy-memory] `/add` and `/add_extracted` take `language`; `/search` does not (`server.py`).[^hy-memory]

## Constraints and gotchas

- `search()` requires non-empty `user_ids`; multiple `agent_ids` together with multiple `session_ids` is rejected; `statuses` is accepted only for explicit `L1_RAW` search (2.0.14) (`client.py::search`; `CHANGELOG.md::2.0.14`).[^hy-memory]
- MMR diversity applies only when `limit < 20`; `scene="all"` fuses chat/working/coding lanes with RRF `1/(60+rank)`, reporting a failed lane in `errors` (`client.py::search` docstring; `pipelines/_retrieval/diversity.py`).[^hy-memory]
- Embedding inputs are silently truncated to 8192−64 tokens; per-call `embed_override` may change only `base_url`/`api_key`/`extra_headers`/`timeout`, never model or dims (`core/embed_service.py::_truncate_for_embedding`; `client.py`).[^hy-memory]
- Only `meta` is persisted and returned; `metadata` is not guaranteed to round-trip (`docs/usage.md::add`).[^hy-memory]
- Writes fail closed since 2.0.13: model failures return `success:false` with `agent_error_code` (`RECONCILE_FAILED`/`LLM_ERROR`/`EMBEDDING_FAILED`) rather than storing everything as-is (`CHANGELOG.md::2.0.13`).[^hy-memory]
- `docs/usage.md` and `docs/monorepo.md` still pin `hy-memory==2.0.4` (Observed drift versus 2.0.14).[^hy-memory]
- Not traced end-to-end: which `GraphStoreConfig`/`RecallConfig` env vars are consumed at runtime (declared and env-bound only; Unverified).

## Relationships

- Part of: [Hy Memory and MemHub overview](hy-memory-overview.md).
- Uses: [Storage backends and re-embedding](hy-memory-storage-and-reembed.md); [Runtime, concurrency, observability](hy-memory-runtime-concurrency-and-observability.md).
- Used by: [OpenClaw and Hermes plugins](hy-memory-plugins-openclaw-hermes.md) (via the HTTP server); [MemHub architecture](memhub-product-architecture.md) (via public `HyMemoryClient`).

## Coverage and limits

Static inspection only (delegated). `client.py` is ~7.8k lines; method list and constraints came from signatures, docstrings and key branches, not a full read.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators are inline per claim as `path::symbol-or-section`. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
