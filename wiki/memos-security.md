---
type: Concept
title: Memos access and privacy model
description: Memo audiences, sharing, authentication and security boundaries in Memos.
tags: [note-taking, memos, security]
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

**Observed:** Memos combines a shared transport authorizer with memo-specific audience checks and database access predicates; this is a static description, not a security audit.[^memos]

## Audience and sharing

For structurally valid memos, PUBLIC allows anonymous reads only when instance policy permits, PROTECTED allows active users, PRIVATE allows the active author, and SPACE requires active membership. Instance administrators can read a valid memo by name regardless of audience; collection feeds retain audience filtering. Archived memos are otherwise author-only. A share applies only to its exact memo and not to SPACE memos.[^memos]

The SQLite listing predicate implements audience and lifecycle constraints in SQL. Share creation rejects SPACE or non-active memos and accepts an active author or administrator. **Documentation discrepancy:** its handler comment says creator only, while `CanManageMemo` also allows an administrator.[^memos]

## Sessions and data boundaries

Access tokens have a 15-minute lifetime and refresh tokens 30 days at this revision; access tokens are bound to the password hash. Managed attachment metadata avoids exposing presigned S3 URLs that might outlive a visibility change. Share URLs are bearer capabilities and must be treated as secrets. Webhook and AI integrations can send data outside the instance; provider behavior was not exercised.[^memos]

See [Memos interfaces](memos-interfaces.md), [storage](memos-data-and-storage.md), and [source coverage](memos-source-map.md).

[^memos]: `core/access/memo.go::CheckMemoReadContext`, `IsInstanceAdmin`, `CanManageMemo`; `store/db/sqlite/memo_access.go::sqliteMemoAccessPredicate`; `server/api/memo_share_service.go::CreateMemoShare`; `server/api/api.go::NewHandler`; `server/auth/token.go::AccessTokenDuration`, `RefreshTokenDuration`, `GenerateAccessTokenV2`; `server/api/attachment_service_storage.go::convertAttachmentFromStore`; `server/api/memo_service_webhooks.go`; `server/api/ai_service.go::Transcribe`.
