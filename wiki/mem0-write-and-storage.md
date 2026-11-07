---
type: Concept
title: Mem0 OSS write and storage
description: Additive extraction, deduplication, session history, vector payloads, entity indexing, and write-path limitations in Mem0 OSS.
tags: [agent-memory, mem0]
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

**Observed:** The inferred OSS write path retrieves up to ten existing memories and ten recent session messages, calls an LLM once for additive facts, embeds them, and writes accepted records to the vector store. `infer=False` instead writes each non-system message directly.[^mem0]

## Deduplication and failure

**Observed:** Deduplication compares exact text hashes only against the retrieved ten memories and the current batch; it is not general semantic deduplication. Provider errors raise an LLM error, while malformed extraction JSON is logged and treated as an empty extraction. Batch insertion has per-record fallback; results represent records actually persisted.[^mem0]

## Storage and limits

**Observed:** Memory text and metadata are vector-store payloads; SQLite keeps history and a bounded recent-message buffer. Entity vectors in a separate collection link memory IDs for retrieval boosts. The prompt requests memory links, but the inspected OSS write path does not persist the model's requested `linked_memory_ids` as memory-to-memory links. Explicit updates and deletes are separate operations; additive extraction does not imply that users cannot update or delete memories.[^mem0]

See [retrieval](mem0-retrieval.md) and [security](mem0-server-and-security.md). Static inspection only; provider-specific persistence and runtime behavior were not tested.

[^mem0]: Revision `d16b8df6`; `mem0/memory/main.py::Memory.add`, `Memory._add_to_vector_store`, `Memory.entity_store`, `Memory._create_memory`; `mem0/memory/storage.py::SQLiteManager.save_messages`; `mem0/configs/prompts.py::ADDITIVE_EXTRACTION_PROMPT`.
