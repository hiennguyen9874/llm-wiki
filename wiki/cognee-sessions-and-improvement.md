---
type: Concept
title: Cognee sessions and improvement
description: Session cache, ordered improvement stages, distillation, and deletion-invalidation limits.
tags: [agent-memory, cognee, sessions]
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

**Observed:** session configuration defaults to a SQLite cache, with Redis, Tapes, Turso and Postgres options. Cognee's improvement registry orders feedback weighting, session-QA persistence, agent-trace persistence, context extraction, session distillation, preference updating, truth-subspace building, conflict review, and global-context indexing; individual stages have gates.[^cognee]

## Failure and lifecycle boundaries

- **Observed:** the registry validates that `persist_session_qa` is the sole fatal stage and cannot be disabled through the stage-disable list. Its comments describe the rest as fail-open.[^cognee]
- **Reported:** session distillation loads uncovered session entries, curates candidates, checks novelty, and persists accepted lessons as documents. Model calls and exact results were not reproduced.[^cognee]
- **Reported by deletion implementation:** document deletion invalidates matching session turns via recorded graph element IDs and follows their provenance chain. Limits include un-attributed older sessions, traces without element IDs, and the append-only Tapes backend; cleanup on deletion is best-effort.[^cognee]

## Relationships

- **Feeds:** [Cognee retrieval](cognee-retrieval.md) with session context and [ingestion](cognee-ingestion-and-code-graphs.md) with accepted lessons.
- **Constrained by:** [Storage and security](cognee-storage-and-security.md), including deletion semantics.

[^cognee]: Revision `525b1d1`, `cognee/infrastructure/databases/cache/config.py::CacheConfig`, `cognee/modules/improve/registry.py::DEFAULT_STAGES`, `::validate_fatal_stage_policy`, `::validate_stages_disabled`, `cognee/modules/session_distillation/distill.py::distill_session`, `cognee/modules/session_lifecycle/invalidate_sessions.py::invalidate_sessions_for_deleted_data`.
