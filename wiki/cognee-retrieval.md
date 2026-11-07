---
type: Concept
title: Cognee retrieval and query routing
description: Recall versus search, routing rules, retrieval lanes, and dataset-scoped fallback behavior.
tags: [agent-memory, cognee, retrieval]
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

**Reported:** `recall` adds source selection, result labels, and automatic routing over lower-level `search`; a bare session ID can cause a session hit to short-circuit graph lookup. In contrast, `search` uses a session as history rather than as a searchable source. Explicit `query_type` bypasses the recall router.[^cognee]

## Routing and retrieval

**Observed:** the ordered regex rules route quoted phrases to lexical chunks, coding-rule requests to coding rules, code questions to code search, count questions to broad search, and date-scoped questions to temporal retrieval; the fallback is hybrid completion. With no LLM, routing constraints can force context-only behavior or fallback. Cypher is not automatically routed: the source identifies the risk of running arbitrary query text with only read authorization.[^cognee]

**Reported:** unscoped authorized searches can route among readable datasets using global-context-index vectors, always include unindexed datasets, and widen a routed search when retrieval yields nothing. Explicit dataset scope is not routed. Runtime behavior was not tested.[^cognee]

## Relationships

- **Uses:** [Ingestion](cognee-ingestion-and-code-graphs.md) supplies graph and chunk indexes; [sessions](cognee-sessions-and-improvement.md) supply cached context.
- **Part of:** [Cognee overview](cognee-overview.md).

[^cognee]: Revision `525b1d1`, `docs/recall-vs-search.md::What recall() adds on top of search()`, `::Same argument, different meaning`, `cognee/api/v1/recall/query_router.py::_RULES`, `::constrain`, `cognee/modules/search/methods/search.py::authorized_search`.
