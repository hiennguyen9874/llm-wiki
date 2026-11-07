---
type: Concept
title: Memos overview and architecture
description: Product purpose and layered architecture of the self-hosted Memos note-taking application.
tags: [note-taking, memos]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:10:00Z' }
sources:
  - id: memos
    resource: ../raw/memos/README.md
    scope: ../raw/memos/
    kind: code
    revision: 88a20fe
    title: Memos repository
---

Memos is a self-hosted note-taking application. The project **reports** a Markdown-based personal timeline with tags and user-controlled sharing; its README also points to external deployment and integration documentation.[^memos]

**Observed:** the Go process selects a database driver, constructs the store, runs migrations, applies configuration and starts the server. The server exposes API, file, frontend and MCP services; the structured API includes Connect and gRPC-Gateway transports. SQLite, MySQL and PostgreSQL are selectable drivers. The repository also contains a React web client.[^memos]

## Relationships

- Uses [memo storage and processing](memos-data-and-storage.md) to maintain content and derived metadata.
- Uses [access and privacy controls](memos-security.md) across its interfaces.
- Exposes [API and MCP interfaces](memos-interfaces.md); see [deployment and configuration](memos-deployment.md).
- The [source map](memos-source-map.md) records inspection limits.

[^memos]: `README.md` §§ About Memos, Quick start; `cmd/memos/main.go::runServer`; `store/db/db.go::NewDBDriver`; `server/server.go::NewServer`; `server/api/api.go::NewHandler`; `web/package.json`.
