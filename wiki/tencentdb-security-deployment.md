---
type: Concept
title: TencentDB security and deployment boundaries
description: Authentication, authorization, credential handling and deployment caveats across the TencentDB memory services.
tags: [agent-memory, tencentdb, security]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:17:35Z' }
stale_after: 2027-02-06
sources:
  - id: tencentdb
    resource: ../raw/TencentDB-Agent-Memory/README.md
    scope: ../raw/TencentDB-Agent-Memory/
    kind: code
    revision: 2002196
    title: TencentDB Agent Memory repository
---

**Observed:** security depends on the deployed service boundaries, not simply on asset visibility. In MemoryKnowledge an empty service key disables its bearer gate, and even with a key configured a list of read-only paths bypasses that gate. Network exposure and the Panel/Core authorization layers therefore matter.[^tencentdb]

## Boundaries requiring review

- Core has an optional gateway bearer gate and separate identity/permission handling. Some trusted service endpoints delegate user-level authorization to the Panel; do not expose them as though the gateway alone enforces asset ownership.[^tencentdb]
- Knowledge source credentials use base64 encoding rather than encryption; protection depends on database and host access controls. The repository fetcher's private-address check examines host strings, not resolved DNS addresses, so it is not a complete SSRF defense.[^tencentdb]
- The Panel knowledge status callback explicitly omits normal panel-header validation and uses a payload service ID to select instance credentials; assess network controls and callback authentication before exposure. Panel stores user-key sessions in browser local storage, and optional API telemetry includes a user-key field.[^tencentdb]
- Proxy code defaults and example configuration differ in authentication and injection settings; review the effective configuration rather than assuming examples are defaults. Optional diagnostic dumps can include sensitive request contents.[^tencentdb]

## Deployment

**Reported:** the root installation guide starts Core, Hub and Proxy via `deploy/global-images/start-all.sh`. **Observed:** the global-image scripts and combined Hub startup have different key-generation behavior; the Core launcher documents an incompatibility with a nonempty gateway bearer in the referenced proxy setup. Purge removes persistent deployment data; read the script before using it.[^tencentdb]

All security findings are static observations, not penetration tests. The [source map](tencentdb-source-map.md) records pending areas, and [retrieval](tencentdb-retrieval-storage.md) describes an isolation documentation discrepancy.

[^tencentdb]: Revision `2002196`: `MemoryKnowledge/src/middleware/auth.ts::createServiceAuthMiddleware`, `::READONLY_POST_PATHS`; `MemoryCore/src/gateway/server.ts::checkAuth`; `MemoryCore/v3-api-memorycore-doc.md` §3.4; `MemoryKnowledge/src/source-auth/credential-codec.ts::encodeSecret`; `MemoryKnowledge/src/source-fetcher/git-fetcher.ts::isPrivateAddress`; `MemoryPanel/src/panel/http/routes/knowledge/callback-routes.ts::registerKnowledgeCallbackRoutes`; `MemoryPanel/web/src/lib/panelSession.ts::setPanelSession`; `MemoryPanel/src/panel/infra/api-call-telemetry.ts::createPanelApiCallTelemetry`; `MemoryProxy/src/config.ts::DEFAULT_CONFIG`; `MemoryProxy/config.example.yaml`; `MemoryProxy/src/pipeline/stages/parse-body.ts::dumpInbound`; `README.md` §Installation; `deploy/global-images/start-memory-core.sh`; `deploy/global-images/_lib.sh::ensure_knowledge_service_key`; `deploy/panel-knowledge-combined/start-combined.sh`; `deploy/global-images/stop-all.sh`.
