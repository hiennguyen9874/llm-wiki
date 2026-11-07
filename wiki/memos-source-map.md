---
type: SourceMap
title: Memos source map and coverage
description: Source identity, inspection coverage, exclusions and outstanding limits for the Memos repository snapshot.
tags: [note-taking, memos, source-map]
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

The source is the MIT-licensed Memos repository snapshot at revision `88a20fe`, with [README](../raw/memos/README.md) as entry point. Four parallel static explorations and curator spot checks informed this initial, **draft** synthesis; no project code, builds, tests, benchmarks, integrations or network requests were executed.[^memos]

## Coverage ledger

- **Inspected or sampled:** README and license; startup and routing (`cmd/memos`, `server`); memo authorization and SQLite predicate (`core/access`, `store/db/sqlite`); memo sharing, attachment storage, session tokens; payload backfill; MCP service and documentation; database migration guidance, Dockerfile, proto changelog, configuration and CI documentation. See the linked concepts for precise locators.[^memos]
- **Inventoried, partially inspected:** Go packages, web SPA, API and store protos, filter and Markdown engines, tests, providers, migration scripts, CI and design documents. Coverage is sampled, not file-by-file exhaustive; MySQL and PostgreSQL driver behavior, frontend behavior, provider implementations, and most tests remain pending.
- **Excluded or limited:** generated `proto/gen/` and `web/src/types/proto/` are not independently validated; generated OpenAPI is an MCP input but its code generation was not run. Frontend build output, binary brand images, translated duplicates, lock files beyond dependency inventory, Git metadata, and test archives were not compiled as independent knowledge. Public documentation and external integrations linked from the README were not fetched. Demo seed content and fixture credentials are not reproduced.
- **Screening:** pattern and filename screening reported no likely live credentials in the inspected working tree; this was not a comprehensive secret or security audit. No source execution occurred.

## Relationships

This ledger covers [overview](memos-overview.md), [data and storage](memos-data-and-storage.md), [security](memos-security.md), [interfaces](memos-interfaces.md), and [deployment](memos-deployment.md). The deployment page records a stale proto README configuration description; the security page records a share-handler comment/code discrepancy.[^memos]

[^memos]: `README.md` §§ About Memos, Quick start, License; `LICENSE`; `cmd/memos/main.go::runServer`; `server/api/api.go::NewHandler`; `server/mcp/service.go::NewMCPService`; `core/access/memo.go::CheckMemoReadContext`; `server/api/memo_share_service.go::CreateMemoShare`; `proto/README.md` § Deployment settings; `proto/api/CHANGELOG.md` deployment-configuration entry.
