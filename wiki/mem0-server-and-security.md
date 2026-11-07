---
type: Concept
title: Mem0 self-hosted server and security
description: Self-hosted deployment topology, authentication, authorization boundaries, configuration, and important operational risks.
tags: [agent-memory, mem0, security]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:08:00Z }
stale_after: 2027-02-06
sources:
  - id: mem0
    resource: ../raw/mem0/README.md
    scope: ../raw/mem0/
    kind: code
    revision: d16b8df
    title: Mem0 repository
---

**Observed:** The development Compose stack exposes the API, PostgreSQL/pgvector, and a dashboard. Its API startup reinstalls an unpinned `mem0ai` package before migrations and server start, so the deployed library need not match this source snapshot. The Compose file requires a database password.[^mem0]

## Authentication versus isolation

**Observed:** `verify_auth` accepts bearer credentials, an API key or an explicitly disabled-auth mode. Administrative checks protect unscoped listing and certain destructive/configuration operations. However, memory routes accept caller-supplied identifiers or memory IDs without binding those values to the authenticated principal; authenticated entity listing scans shared payloads. **Synthesis:** authentication alone should not be treated as tenant isolation; an authenticated caller with identifiers may access other scopes. This is static analysis, not an exploit test.[^mem0]

Disabling authentication is intended for local development; in that mode the admin dependency also accepts the bypass. **Observed:** the Python CLI may synchronize a stored API key into already-existing shell or Claude configuration entries, expanding the locations where credentials reside. Treat these files and memory contents as sensitive.[^mem0]

See [clients and integrations](mem0-clients-and-integrations.md) and [source coverage](mem0-source-map.md). No server, network, authentication or deployment tests were run.

[^mem0]: Revision `d16b8df6`; `server/docker-compose.yaml::services`, `server/auth.py::verify_auth`, `server/auth.py::require_admin`, `server/main.py::get_all_memories`, `server/main.py::get_memory`, `server/main.py::search_memories`, `server/routers/entities.py::list_entities`, `cli/python/src/mem0_cli/plugin_sync.py::_update_shell_rc` and `_update_claude_settings`.
