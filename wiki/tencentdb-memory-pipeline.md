---
type: Concept
title: TencentDB memory layers and write pipeline
description: L0 conversation capture and asynchronous L1, L2 and L3 memory synthesis in TencentDB MemoryCore.
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

**Reported:** MemoryCore organizes memory as L0 conversations, L1 atomic facts, L2 scenario blocks and L3 core/persona; the latter layers provide context at different levels of abstraction.[^tencentdb]

## Capture and synthesis

**Observed:** `performAutoCapture` coordinates checkpointed L0 recording and pipeline notification. The L0 recorder sanitizes and writes conversation records; the scheduler drives L1 extraction, L2 scene construction and L3 persona generation. L1 extraction includes candidate deduplication. These are asynchronous stages rather than proof that every captured turn has already reached every layer.[^tencentdb]

**Reported limitation:** the seed runtime documents that it waits for L1 idle but L2/L3 can still be in flight. The code and pipeline have not been run in this review.[^tencentdb] Related: [retrieval and storage](tencentdb-retrieval-storage.md), [proxy capture](tencentdb-proxy-integrations.md), and [coverage](tencentdb-source-map.md).

[^tencentdb]: Revision `2002196`: `README.md` §Technical Implementation; `MemoryCore/src/core/hooks/auto-capture.ts::performAutoCapture`; `MemoryCore/src/core/conversation/l0-recorder.ts::recordConversation`; `MemoryCore/src/utils/pipeline-manager.ts::MemoryPipelineManager`; `MemoryCore/src/core/record/l1-extractor.ts::extractL1Memories`; `MemoryCore/src/core/record/l1-dedup.ts::batchDedup`; `MemoryCore/src/core/seed/seed-runtime.ts::executeSeed`.
