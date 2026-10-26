---
type: Concept
title: "OpenRAG backend architecture and persistence"
description: "Backend entrypoints, dependency composition, configuration precedence, and the split between SQL, OpenSearch, and legacy file storage."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:03:52Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d
    title: OpenRAG repository
---

**Observed:** OpenRAG's backend is a service-composed FastAPI application with separate browser, public API, Langflow-proxy, ingest-callback, and MCP surfaces. Its persistence is deliberately split: OpenSearch holds searchable content and API-key authentication records, while SQL holds identity/authorization and newer workspace/chat state; legacy YAML and JSON paths remain mode-dependent.[^openrag-repo]

## Startup and composition

1. `bootstrap` loads dotenv with `override=False` and initializes logging before configuration imports.
2. The `python src/main.py` entry path runs Alembic upgrade to `head` before entering the application event loop. **Synthesis:** alternate launchers must account for this migration step rather than assuming all ASGI imports run it.
3. `app.factory::create_app` attaches the service container, request logging/CORS/metrics, and route registrars. The container constructs services and uses lazy DB session factories to avoid capturing a stale event loop.
4. Startup initializes the DB, performs one-shot legacy-data migrations, hydrates workspace configuration, enters mounted MCP lifespan, and schedules background flow backups, subscription renewal, and task cleanup.
5. Startup rejects `UVICORN_WORKERS > 1` and `CACHE_BACKEND != memory`: current permission/identity caches are process-local, not distributed.[^openrag-repo]

An optional second listener exposes an allowlisted router for ingestion and model-proxy traffic. Its router is network-surface isolation, not an independent JWT validator; authentication remains at the main backend.[^openrag-repo]

## Stores and ownership

| Store | Responsibility |
| --- | --- |
| SQL, async SQLite by default or configured `DATABASE_URL` | Users, roles/permissions, audit/preferences, workspace config, conversation/session ownership, migration status; schema also declares an API-key table |
| OpenSearch | Document chunks and embeddings, knowledge filters, API-key authentication records, DLS principal lookups |
| YAML | Legacy `config/config.yaml`, used by file-based configuration |
| JSON | Legacy connections plus file-mode conversation/session ownership; migrations import legacy user identities and chat history, not the connection records themselves |

The declared SQL API-key model does not establish that SQL is the active key-authentication store; the inspected API-key service uses OpenSearch. Conversation and session-ownership models lack user foreign keys in the inspected schema; broader user-table deletion constraints must not be assumed to cover those rows.[^openrag-repo]

## Configuration precedence

**Observed, legacy file path:** defaults → YAML → environment, except that `edited: true` in the file suppresses normal environment overrides. `OPENSEARCH_INDEX_NAME` and the legacy embedding-provider map are deliberate exceptions applied before that gate. The index name must satisfy security-role patterns, so changing it is not arbitrary.[^openrag-repo]

**Observed, modern path:** `OPENRAG_STORAGE_MODE` accepts `db|hybrid|files`, default `db`; workspace config becomes DB-first in `db`/`hybrid`, with interception of legacy save call sites. `OPENRAG_DISABLE_DB_WORKSPACE_CONFIG=true` forces file mode. Consequently, the legacy YAML precedence alone is not the whole runtime configuration model.[^openrag-repo]

## Contradictions

- `ConfigManager.load_config` documentation calls environment highest-priority, while the `edited` gate prevents ordinary overrides. Both the documented rule and implementation behavior are preserved here; inspect the selected storage mode before changing configuration.
- Its constructor describes a project-root config file, while the implementation resolves `$OPENRAG_CONFIG_PATH/config.yaml`.[^openrag-repo]

## Relationships

- Depends on [authentication and security](openrag-auth-security.md) for external-subject versus SQL-owner identity and cache boundaries.
- Uses [document ingestion](openrag-document-ingestion.md) and [hybrid retrieval](openrag-hybrid-retrieval.md) for the OpenSearch data plane.
- Used by the [frontend](openrag-frontend.md), [public API](openrag-public-api.md), and [MCP server](openrag-mcp.md).

## Coverage limits

Targeted entrypoint, config, model, and migration inspection is not execution of migrations or proof of cross-store consistency. Repository methods other than the workspace-config repository, legacy runtime bodies, and gateway internals remain partly pending; see [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d`: `src/main.py::__main__`; `src/bootstrap.py::load_env`; `src/app/{factory,container,lifespan,router_app}.py::{create_app,initialize_services,run_startup}`; `src/config/config_manager.py::{load_config,_load_env_overrides,apply_index_name_env_override}`; `src/config/{paths,storage_mode}.py`; `src/services/{workspace_config_service,api_key_service}.py`; `src/db/engine.py`; `src/db/models/{conversation,session_ownership,api_key}.py`; `src/db/migrations_runtime.py`; `alembic/versions/0001_initial.py` through `0008_session_conversation_id.py`.
