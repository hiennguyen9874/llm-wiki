---
type: Concept
title: Headroom failure and traffic learning
description: Offline session analysis, loop detection, managed-file writing, and the distinct online traffic learner.
tags: [agent-memory, learning]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:19:57Z }
stale_after: 2027-05-06
sources:
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
---

**Observed:** `headroom learn` uses agent-specific scanners, detects repeated error and re-fetch loops, and passes session evidence to an analyzer that produces recommendations. The writer merges a marked block into agent instruction or memory files. Claude's project default is `CLAUDE.local.md`; an explicit shared target or other agent writer may write to files intended for version control.[^headroom]

Loop waste is estimated from repeated output sizes, while other recommendations depend on model analysis. A separate `TrafficLearner` uses rule-based extraction from proxy traffic and evidence thresholds; it should not be conflated with the session-analysis command. The project's failure-learning documentation says earlier concrete figures lacked traceable committed evidence; recommendation accuracy was not verified here.[^headroom]

## Relationships

- Complements [Headroom memory](headroom-memory.md); session-derived file content is a [privacy consideration](headroom-privacy-and-security.md).

[^headroom]: `headroom/learn/registry.py::_discover`; `headroom/learn/loops.py::detect_loops`, `LoopPattern`; `headroom/learn/analyzer.py::SessionAnalyzer.analyze`; `headroom/learn/writer.py::ClaudeCodeWriter`, `_merge_into_file`; `headroom/memory/traffic_learner.py::TrafficLearner`; `docs/content/docs/failure-learning.mdx` callout “Figures removed”; revision `2b0315b`.
