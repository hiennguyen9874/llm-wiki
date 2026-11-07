---
type: Concept
title: Memos data and storage
description: Memo content, derived Markdown payloads and attachment persistence in Memos.
tags: [note-taking, memos, storage]
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

**Observed:** Memos stores memo content with derived Markdown metadata, and provides SQLite, MySQL and PostgreSQL database drivers. Content-derived tags and property flags are versioned; a background backfill records the payload version after a successful pass and guards writes against concurrent edits. Parse failures are logged and skipped, whereas write failures fail the pass.[^memos]

Attachments may be stored in the database, local files, or S3. Local writes stage to a temporary file before rename; S3 object keys receive a UID suffix when the template has no random component. Managed files are served through the file route rather than stable presigned URLs.[^memos]

**Coverage limit:** SQLite received the closest inspection; MySQL and PostgreSQL behavior, database migrations, and external storage were not executed. See [security](memos-security.md), [deployment](memos-deployment.md), and the [source map](memos-source-map.md).[^memos]

[^memos]: `store/db/db.go::NewDBDriver`; `core/memopayload/runner.go::Backfill`, `RunOnce`; `server/api/attachment_service_storage.go::saveAttachmentContent`, `convertAttachmentFromStore`.
