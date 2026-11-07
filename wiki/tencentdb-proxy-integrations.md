---
type: Concept
title: TencentDB proxy, capture, and agent integrations
description: Proxy turn processing, on-demand memory tools, capture, bridges, and SDK version boundaries.
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

**Observed:** MemoryProxy routes agent protocol requests through a staged pipeline that resolves identity and session, injects context, forwards requests, and records eligible completed turns. The README describes a proxy-based integration without requiring an agent plugin; actual behavior depends on configuration and the client adapter.[^tencentdb]

The configured injection assembly includes skills, knowledge tools, and memory profile/tool blocks. Its wiring leaves the L1 auto-recall injector unregistered: L1 and conversation search are made available on demand through tools, while profile and scene navigation may be injected. On completed turns the proxy can send conversation data to Core and submit eligible rounds for skill extraction; extraction is configurable.[^tencentdb]

The memory bridge restricts paths to reads and overwrites caller-provided identity with session-derived identity. The skill bridge has a separate allowlist and gates LLM writes. A session header remains a sensitive capability; avoid assuming the bridge provides independent end-user authentication. See [security](tencentdb-security-deployment.md).[^tencentdb]

**Observed:** the TypeScript SDK top-level exports v3, while the Python package top-level retains v2 and exposes v3 separately. Check import paths and client versions before implementing integrations.[^tencentdb]

[^tencentdb]: Revision `2002196`: `README.md` §All Agents Share the Same Memory Server; `MemoryProxy/src/pipeline/runners/openai-chat.ts::runOpenaiChatPipeline`; `MemoryProxy/src/injection/index.ts::buildPipelineBundle`; `MemoryProxy/src/tdai/recorder.ts::recordTdaiTurn`; `MemoryProxy/src/extraction-gate.ts::isExtractionAllowed`; `MemoryProxy/src/memory/memory-bridge.ts::createMemoryBridgeHandler`; `MemoryProxy/src/skill/skill-bridge.ts::createSkillBridgeHandler`; `sdk/memory-core/typescript/src/index.ts`; `sdk/memory-core/python/tencentdb_agent_memory/__init__.py`.
