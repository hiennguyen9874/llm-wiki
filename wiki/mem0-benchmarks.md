---
type: Concept
title: Mem0 reported benchmarks and evaluation limits
description: Vendor-reported managed-platform memory benchmark scores, conflicting published figures, and unavailable evaluation code.
tags: [agent-memory, mem0, benchmarks]
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

**Reported, not reproduced:** the README reports LoCoMo 92.5, LongMemEval 94.4, BEAM 1M 64.1 and BEAM 10M 48.6, using a top-200 retrieval budget and single-pass retrieval. The source explicitly attributes these numbers to the managed platform with proprietary optimizations, not the open-source SDK.[^mem0]

## Contradictions

- **Reported:** the README gives LoCoMo 92.5 and LongMemEval 94.4. The OSS migration guide instead reports 91.6 and 93.4 for the new algorithm. The available sources do not establish why the figures differ; neither is independently verified.[^mem0]

The `evaluation/` benchmark harness is a declared submodule but was uninitialized and unavailable in this checkout. No benchmark or project tests were run, so dataset preparation, judging, statistical uncertainty and results could not be independently checked. See [source map](mem0-source-map.md).[^mem0]

[^mem0]: Revision `d16b8df6`; `README.md::New Memory Algorithm (April 2026)`; `docs/migration/oss-v2-to-v3.mdx::Overview`; `.gitmodules::submodule evaluation`; local `git submodule status` showed evaluation uninitialized.
