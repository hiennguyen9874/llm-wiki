---
type: Concept
title: Hindsight extensions, memory defense and webhooks
description: Hindsight's server extension slots, bundled extensions, the opt-in memory defense secret/PII filter, and signed webhook delivery.
tags: [agent-memory, hindsight, extensions, security, webhooks]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: extensions-readme
    resource: ../raw/hindsight/hindsight-extensions/README.md
    kind: documentation
    revision: eb963cb
    title: hindsight-extensions README
  - id: extensions-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/extensions.md
    kind: documentation
    revision: eb963cb
    title: Extensions developer doc
  - id: defense-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/memory-defense/index.md
    kind: documentation
    revision: eb963cb
    title: Memory defense developer doc
  - id: webhooks-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/api/webhooks.mdx
    kind: documentation
    revision: eb963cb
    title: Webhooks API doc
  - id: ext-code
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/extensions/loader.py
    kind: code
    revision: eb963cb
    title: Extension loader
---

Hindsight is customized without forking through **extensions** — Python classes loaded by import path from `HINDSIGHT_API_<KIND>_EXTENSION=module:Class`; remaining env vars with the same prefix become that extension's config. It also ships an opt-in **memory defense** filter and signed **webhooks**.[^extensions-readme][^ext-code]

## Extension slots

- `EXTENSION_KINDS` in code: TENANT, MEMORIES, OPERATION_VALIDATOR, MEMORY_DEFENSE, LLM_REQUEST, MODEL_CALL, HTTP, MCP. Docs list six main points (Tenant, Http mounted under an extension path, OperationValidator, MCP, LLMRequest, ModelCall). One extension per slot. Extensions can ship their own Alembic migrations.[^ext-code][^extensions-doc]
- **Built in:** `ApiKeyTenantExtension`, `MemoryDefenseRegexExtension`.[^ext-code]
- **Out-of-tree examples** (`hindsight-extensions/`, not on PyPI, distributed via a derived Docker image): `supabase-tenant` (validates Supabase JWTs, schema `user_<uid>`), `static-keys-tenant` (`HINDSIGHT_API_TENANT_USERS=user:key,…`, one schema per user), `bank-llm-routing` (glob-routed per-bank LLM overrides; `UNMATCHED=deny|server`) (Observed).[^extensions-readme]
- Breaking change noted in docs: `SupabaseTenantExtension` moved to an external registry in 0.9.3.[^extensions-doc]

## Memory defense

Opt-in per bank via `memory_defense` config. Scans every retain against 45 bundled regex patterns (AI/LLM keys, cloud, SCM/CI, payments, comms, DB URLs, PEM/JWT, US PII) and either **redacts** (`[REDACTED:type]` before storage) or **blocks** (422 if every item is blocked; partial blocks return 200). Not retroactive. Emits a `memory_defense.triggered` webhook and `memory_defense` audit entries.[^defense-doc][^readme] Code counts about 50 detectors, including Luhn-checked cards (Observed; minor count difference with docs).[^ext-code]

## Webhooks

Per-bank (and global) endpoints; at-least-once delivery (dedupe on `X-Hindsight-Event-Id`); 30 s timeout; 6 attempts with backoff 5 s, 5 min, 30 min, 2 h, 5 h; HMAC-SHA256 `X-Hindsight-Signature` (equal to `X-Hub-Signature-256`) plus timestamped `X-Hindsight-Signature-V2`. Events: `consolidation.completed`, `retain.completed`, `memory_defense.triggered`. Deliveries are queued as `async_operations` type `webhook_delivery`.[^webhooks-doc][^ext-code]

## Relationships

Guards [Retain](hindsight-retain-pipeline.md); defaults in [Storage and configuration](hindsight-storage-and-configuration.md); queue in [API surface](hindsight-api-surface.md); tenant extensions enable multi-tenant deployments ([Deployment](hindsight-deployment-and-ci.md)).

## Limits

`DEFAULT_WEBHOOK_EVENT_TYPES = "consolidation.completed"` carries a comment saying "default = all supported events" (Observed; see [discrepancies](hindsight-doc-code-discrepancies.md)). Pattern lists are regex heuristics and not verified to catch every secret format.

[^readme]: `README.md` § "Memory Banks" (Memory Defense), "Running in Production" (Events, Extensibility).
[^extensions-readme]: `hindsight-extensions/README.md`; `supabase-tenant/`, `static-keys-tenant/`, `bank-llm-routing/` extension modules.
[^extensions-doc]: `hindsight-docs/docs/developer/extensions.md`.
[^defense-doc]: `hindsight-docs/docs/developer/memory-defense/index.md`.
[^webhooks-doc]: `hindsight-docs/docs/developer/api/webhooks.mdx`.
[^ext-code]: `hindsight-api-slim/hindsight_api/extensions/{loader,base,memory_defense,tenant}.py`, `extensions/builtin/memory_defense_regex.py`, `webhooks/manager.py`, `webhooks/models.py::WebhookEventType`, `config.py:DEFAULT_WEBHOOK_EVENT_TYPES`.
