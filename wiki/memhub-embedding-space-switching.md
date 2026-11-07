---
type: Concept
title: MemHub embedding-space switching
description: How MemHub safely changes embedding models — space identity, 409 refusal with plan, full re-embed with rollback, retention, and the built-in local ONNX embedder.
tags: [memhub, embedding, reembed, migration]
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

# MemHub embedding-space switching

An embedding space is identified by **model + width only**; changing endpoint, provider or key never re-embeds. Activating a different identity on a non-empty home returns `409 embedding_switch_required` with a plan (`memhub/docs/contracts/embedding-switch-v1.md` §1).[^hy-memory]

## Switch semantics

A switch re-embeds every vector of every user, verifies, then commits in one transaction (new space live, old retired, profile active). Reads keep serving the old space; model writes pause while intake keeps queueing; failure or cancel rolls back, and the old space is never modified. Most mutating endpoints answer `409 embedding_switch_in_progress` during a switch. Retired spaces are kept 14 days; stray spaces from older naming are scanned and folded in (`embedding-switch-v1.md` §§1, 2, 5.1; `apps/core/src/one_memory/embedding_spaces.py`, `VECTOR_ROLES`).[^hy-memory]

## Engine and embedder

Re-embedding is delegated to the SDK through `ReembedBackend` (unavailable before SDK 2.0.10) — see [storage and re-embedding](hy-memory-storage-and-reembed.md) (`embedding_backend.py` docstring).[^hy-memory] The built-in embedder is local ONNX `bge-small-zh-v1.5`, 512 dims, hash-pinned download, no torch (`embedding_assets.py`; `local_embedding.py`).[^hy-memory]

## Relationships

- Uses: [SDK re-embedding](hy-memory-storage-and-reembed.md).
- Pauses: [model writes in the queue](memhub-memory-modes-and-write-queue.md).
- Part of: [MemHub architecture](memhub-product-architecture.md).

## Coverage and limits

Static inspection (delegated); the switch was not executed, and the 14-day retention is reported from the contract only.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
