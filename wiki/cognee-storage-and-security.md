---
type: Concept
title: Cognee storage, authorization, and deletion
description: Store families, authentication posture, local file boundaries, and deletion limitations in Cognee.
tags: [agent-memory, cognee, security, storage]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:06:51Z' }
stale_after: 2027-02-06
sources:
  - id: cognee
    resource: ../raw/cognee/README.md
    scope: ../raw/cognee/
    kind: code
    revision: 525b1d1
    title: Cognee repository
---

**Observed:** Cognee separates relational metadata, graph, vector, file storage and session cache. Snapshot defaults include SQLite metadata/cache, Ladybug graph and LanceDB vectors; provider and deployment configuration can change these defaults. File-storage encryption configuration does not imply encryption of the graph, vector or relational stores.[^cognee]

## Access and deletion

- **Observed:** `_resolve_auth_posture` defaults backend access control on and makes authentication inherit that setting. An explicit attempt to disable authentication while access control remains on is overridden to require authentication.[^cognee]
- **Observed:** local file-root restriction is opt-in; evaluate exposure and permissions before permitting untrusted requests to ingest local paths.[^cognee]
- **Reported:** `forget(memory_only=True)` preserves raw files and data records while removing memory and resetting pipeline status. Logical deletion is not a byte-level erasure guarantee: the implementation documents residual LanceDB fragments and a lack of user-facing embedded-graph compaction.[^cognee]
- **Reported:** the system-wide prune implementation has no permission checks; it is a destructive administrative operation, not a safe substitute for authorized dataset deletion.[^cognee]

## Relationships

- **Constrains:** [Sessions and improvement](cognee-sessions-and-improvement.md), [interfaces and deployment](cognee-interfaces-and-deployment.md).
- **Part of:** [Cognee overview](cognee-overview.md). Security behavior was statically inspected, not penetration tested.

[^cognee]: Revision `525b1d1`, `cognee/infrastructure/databases/relational/config.py::RelationalConfig`, `cognee/infrastructure/databases/graph/config.py::GraphConfig`, `cognee/infrastructure/databases/vector/config.py::VectorConfig`, `cognee/infrastructure/databases/cache/config.py::CacheConfig`, `cognee/infrastructure/files/encryption/config.py::FileEncryptionConfig`, `cognee/infrastructure/files/utils/local_path_safety.py::get_allowed_local_file_roots`, `cognee/modules/users/methods/get_authenticated_user.py::_resolve_auth_posture`, `cognee/api/v1/forget/forget.py::forget`, `cognee/modules/data/deletion/prune_system.py::prune_system`.
