---
type: SourceMap
title: TencentDB Agent Memory source coverage map
description: Revision, inspection ledger, exclusions, and outstanding coverage for the TencentDB Agent Memory repository.
tags: [agent-memory, tencentdb]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:17:35Z' }
sources:
  - id: tencentdb
    resource: ../raw/TencentDB-Agent-Memory/README.md
    scope: ../raw/TencentDB-Agent-Memory/
    kind: code
    revision: 2002196
    title: TencentDB Agent Memory repository
---

This ledger tracks a **partial static review** of the TencentDB Agent Memory source package at revision `2002196`. Four parallel exploratory reviews covered Core, Knowledge, Proxy/integrations, and Panel/deployment, followed by curator spot checks. The [overview](tencentdb-agent-memory-overview.md) links the resulting concepts. No source code, containers, tests, benchmarks or installation commands were run.[^tencentdb]

## Coverage ledger

- **Inspected:** root README; selected Core capture, recall, store, isolation, gateway and metadata implementation; Knowledge wiki ingest, search, tool routes, code graph and auth; Proxy request pipeline, injection, bridges and clients; Panel auth, routes, telemetry and deployment startup scripts. Entry points and specific locators appear on the linked concepts.[^tencentdb]
- **Inspected selectively:** manifests, API docs, SDK entry points, agent adapters, deployment documentation and CI. The large codebase was not read exhaustively; individual branches and operational claims remain unverified.
- **Pending:** Core offload, full extraction and skill internals, migration scripts and benchmark harnesses; Knowledge converters and full service internals; most Panel frontend; Proxy alternative protocol branches; integration and authorization end-to-end behavior. Documentation references to absent design/test trees cannot be verified from this snapshot.
- **Excluded:** generated dependency lockfiles as exhaustive dependency analysis, generated/build/cache artifacts, duplicate translations, and decorative images. Architecture diagrams were not separately interpreted; the README's adjacent prose was used. The README-linked video is remote and was not inspected. No network access, independent performance validation, or secret-history audit was performed.
- **Trust:** upstream README benchmark and product claims are vendor-reported; code observations describe only this revision. The package contains executable scripts and network-enabled services; they were inspected statically, not executed.

## Known discrepancies

The Core isolation helper's documented throw conflicts with its fallback implementation; see [retrieval and storage](tencentdb-retrieval-storage.md). Knowledge's API documents omit some routes visible in the implementation; see [knowledge service](tencentdb-knowledge-service.md). Deployment and security assumptions vary by launch configuration; see [security and deployment](tencentdb-security-deployment.md).[^tencentdb]

[^tencentdb]: Revision `2002196`: `README.md` §Installation, §Technical Implementation and §Benchmark; `MemoryCore/src/core/store/isolation.ts::assertIsolation`; `MemoryKnowledge/src/routes/wiki.ts::createWikiRoutes`; `MemoryKnowledge/openapi.yaml`; `MemoryProxy/src/server.ts::createApp`; `MemoryPanel/src/panel/http/app.ts::buildPanelApp`; `deploy/global-images/start-all.sh`.
