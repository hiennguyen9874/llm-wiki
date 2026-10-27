---
type: Concept
title: txtai API, clustering, and MCP
description: Configuration-selected FastAPI routes, OpenAI-compatible dispatch, shared-token authentication, MCP limits, and shard fan-out.
tags: [rag, operations, txtai, api, mcp]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:18:00Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccb
    title: txtai repository
---

**Observed:** txtai serves a configuration-selected FastAPI application, with ordinary embeddings/pipeline/agent/workflow routes, a separate OpenAI-compatible selector, optional MCP mounting, and an HTTP shard client. Authentication and exposure depend on startup configuration; these are several invocation surfaces over shared application objects, not independent authorization domains.[^txtai-repo]

## Startup and route selection

`create` installs the built-in authorization dependency only when `TOKEN` is set, plus custom dependencies resolved from `DEPENDENCIES`. `lifespan` reads `CONFIG`, creates global `INSTANCE` (optionally through `API_CLASS`), includes configured routers, executes `EXTENSIONS`, and mounts MCP when configured. Cluster and embeddings configuration also add special-case routers. `routes.<name>: false` suppresses the corresponding router, not removal of the underlying configured object.[^txtai-repo]

`TOKEN` stores the **SHA-256 digest** of the accepted raw bearer token. `Authorization` hashes incoming credentials and compares with `hmac.compare_digest`. Sending the stored digest itself is not equivalent to knowing the raw token. The inspected built-in dependency is a shared-token check, not principal/role/tenant authorization; custom dependencies and an external proxy may add policy. See [security](txtai-security.md).[^txtai-repo]

Embeddings endpoints include query/index management, vector operations, and object/image ingestion. Search also accepts SQL-shaped queries rather than only semantic text. Application write/reindex flags gate mutations; they do not grant distinct privileges to different bearer holders. Encoding routes support JSON or MessagePack content negotiation.[^txtai-repo]

## OpenAI-compatible surface

`/v1/chat/completions` resolves the `model` string in order: named agent, `embeddings`, configured non-LLM pipeline, named workflow, then default LLM. Non-default branches use the latest message content; the default LLM receives the full messages list. **Observed:** this is a routing selector, not a general dynamic model registry. The embeddings compatibility endpoint transforms with the configured embedding model; its `model` field does not independently load another model.[^txtai-repo]

Chat SSE emits OpenAI-shaped chunks and `data: [DONE]`. Audio speech/transcription/translation routes delegate to configured pipelines. Supported inputs/parameters are the inspected subset, not a claim of complete OpenAI API compatibility. Some handlers omit falsy optional values while building kwargs.[^txtai-repo]

**Observed exposure caveat:** the selector checks configured pipeline objects, not their router-enabled status. Disabling a pipeline's ordinary router therefore does not by itself prevent invocation through an enabled OpenAI chat selector. Assess the combined surface before treating route suppression as an access-control boundary.[^txtai-repo]

## MCP boundary

When `mcp` is enabled, `createmcp` constructs an `httpx.AsyncClient` over `ASGITransport` and supplies it to external `FastApiMCP`. Internal client defaults are base URL `http://apiserver` and timeout 100; `clientargs`/`mcpargs` can override options. Documentation describes enabled API endpoints becoming tools and a `/mcp` route.[^txtai-repo]

**Limit:** the default internal client has no explicitly supplied bearer header in this code. External fastapi-mcp behavior and header propagation were not inspected or executed; neither an authentication bypass nor successful authorized calls are established. The sampled MCP test asserts route presence only. Verify actual unauthorized/authorized tool calls and public schema exposure before deployment.[^txtai-repo]

## Cluster, concurrency, and lifecycle

`Cluster` fans out shard requests through aiohttp and aggregates query results with SQL helpers. String IDs use Adler-32 for shard selection; other ID shapes can use integer or random routing. Its inspected client does not explicitly forward the inbound bearer token or set application-specific timeout/TLS options. Library defaults and shard URL schemes still apply; **absence of a timeout override does not prove infinite waits**. Authenticated shards and failure/latency behavior require deployment testing.[^txtai-repo]

`execute` uses `run_until_complete`, making a caller's already-running event loop a compatibility concern. `Application` locks several local embeddings reads and writes; cluster, count, agents, and workflow paths are not uniformly covered by the same lock. Agent session history has no inspected per-session lock. `lifespan` yields without an explicit shutdown-finalization block, while application cleanup/scheduler waiting exists separately. No runtime race, throughput, or graceful-shutdown guarantee was verified.[^txtai-repo]

## Relationships and limits

- **Exposes:** [Retrieval](txtai-retrieval.md), [RAG](txtai-rag.md), [pipelines](txtai-pipelines.md), and [agents/workflows](txtai-agents-workflows.md).
- **Depends on:** [Security](txtai-security.md) and [operations](txtai-operations.md) for production policy and lifecycle.
- **Part of:** [txtai](txtai.md); external language-binding repositories and transport dependencies remain outside the [inspected source scope](txtai-source-map.md).

No HTTP request, MCP exchange, shard call, auth test, stream, or concurrency/shutdown test ran.

[^txtai-repo]: Revision `738aac498ccb`: `src/python/txtai/api/application.py::create, lifespan, enabled, createmcp`; `api/authorization.py::Authorization.__call__, digest`; `api/routers/embeddings.py`; `api/routers/openai.py::chat, embeddings, speech, transcribe, translate, StreamingChatResponse`; `api/route.py::EncodingAPIRoute`; `api/responses/factory.py`; `api/cluster.py::Cluster.shard, execute, run, get, post`; `app/base.py::Application.search, count, reindex, __del__, wait`; `agent/base.py::Agent.__call__`; `docs/api/mcp.md`, `docs/api/security.md`, `docs/api/cluster.md`; `test/python/testapi/testmcp.py::TestMCP.testMCP`, `test/python/testapi/testauthorization.py`, `test/python/testapi/testcluster.py`, `test/python/testapi/testopenai.py` (static only). Short module paths are relative to `src/python/txtai/`.
