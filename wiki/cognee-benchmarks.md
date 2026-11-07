---
type: Concept
title: Cognee reported benchmarks
description: Reported BEAM conversational-memory scores and methodological limits at the inspected Cognee snapshot.
tags: [agent-memory, benchmarks, cognee]
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

**Reported:** Cognee's preliminary BEAM report gives a mean score of 0.79 for a fixed hybrid retrieval setup at 100K context and 0.67 for question-type routed retrieval at 10M. BEAM uses synthetic conversational data and rubric-based LLM judging; these are vendor-reported results, not an independent reproduction.[^cognee]

## Interpretation

- **Reported:** the 100K result averages four QA-and-scoring rounds across 20 questions on one held-out conversation, with reported run standard deviation 0.005.[^cognee]
- **Reported:** the 10M result uses one conversation, one ingestion, five evaluation rounds and routing selected on the same questions as the reported score; it is exploratory. The public code omits that run's BEAM-specific distributed orchestration.[^cognee]
- **Reported:** scales are not a controlled comparison because conversations, ingestion models, and retrieval-selection methods differ. Repeated rounds do not add independent questions.[^cognee]

## Relationships

- **Evaluates:** [Cognee overview](cognee-overview.md) using benchmark-specific formatting and retrieval configuration. See [source map](cognee-source-map.md) for coverage limits.

[^cognee]: Revision `525b1d1`, `cognee/eval_framework/beam/REPORT.md::3.1 Experimental Design`, `::3.2 Data Ingestion`, `::3.4 Evaluation Protocol`, `::4 Results`.
