---
type: Concept
title: TencentDB Agent Memory overview
description: Product architecture, memory asset model, and reported benchmark of TencentDB Agent Memory.
tags: [agent-memory, tencentdb]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:17:35Z' }
stale_after: 2027-05-06
sources:
  - id: tencentdb
    resource: ../raw/TencentDB-Agent-Memory/README.md
    scope: ../raw/TencentDB-Agent-Memory/
    kind: code
    revision: 2002196
    title: TencentDB Agent Memory repository
---

TencentDB Agent Memory combines layered chat memory with skills, document wiki, and code-graph assets. **Reported:** its README positions a shared proxy and Memory Hub as a way for agent teams to retain and selectively reuse experience across sessions and frameworks.[^tencentdb]

## Architecture and evidence

**Observed:** the source contains MemoryCore, MemoryKnowledge, MemoryPanel and MemoryProxy, plus SDKs, agent integrations, adapters and deployment scripts. Core provides memory and metadata; Knowledge processes wiki and code-graph assets; Panel coordinates management; Proxy mediates agent requests. See [memory pipeline](tencentdb-memory-pipeline.md), [knowledge service](tencentdb-knowledge-service.md), [proxy](tencentdb-proxy-integrations.md), and [security and deployment](tencentdb-security-deployment.md).[^tencentdb]

**Reported:** the README gives PersonaMem results of 48% without and 76% with the product, calling this a 59% relative improvement. The benchmark protocol, dataset and harness were not independently inspected or reproduced; the numbers are vendor claims, not an independent comparison.[^tencentdb]

The [source map](tencentdb-source-map.md) records inspection limits. This snapshot was reviewed statically; behavior, performance and security were not tested.

[^tencentdb]: Revision `2002196`: `README.md` sections “What is TencentDB Agent Memory?”, “Technical Implementation”, and “Benchmark”; `MemoryCore/src/core/tdai-core.ts::TdaiCore`; `MemoryKnowledge/src/module.ts::createKnowledgeModule`; `MemoryPanel/src/panel/panel-deps.ts::buildPanelDeps`; `MemoryProxy/src/server.ts::createApp`.
