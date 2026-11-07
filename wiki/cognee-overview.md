---
type: Concept
title: Cognee overview
description: Cognee's graph-based agent memory model, public operations, local quickstart, and source snapshot.
tags: [agent-memory, cognee]
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

Cognee is an agent-memory platform that builds connected graph and vector representations from content, and offers memory retrieval and session workflows. **Reported:** its README presents `remember`, `recall`, `improve`, and `forget` as its principal operations, with local and hosted configurations. **Observed:** the Python package declares version 1.6.6, Apache-2.0, and Python >=3.10,<3.15; these are snapshot-specific, not guarantees about other releases.[^cognee]

## Starting point

**Reported:** the local quickstart installs `cognee[gliner]`, then calls `await cognee.remember(text, dataset_name=...)` and `await cognee.recall(question, datasets=[...])`. Its local models download on first use; retrieved passages need no LLM-generated answer, whereas generated answers and some media processing need additional configuration. The quickstart was not run.[^cognee]

## Relationships

- **Uses:** [Ingestion and code graphs](cognee-ingestion-and-code-graphs.md) construct memory; [retrieval](cognee-retrieval.md) queries it.
- **Uses:** [Sessions and improvement](cognee-sessions-and-improvement.md) bridge session experience into durable memory.
- **Depends on:** [Storage and security](cognee-storage-and-security.md) and [interfaces and deployment](cognee-interfaces-and-deployment.md) for operational boundaries.
- **Reported evidence:** [Benchmarks](cognee-benchmarks.md); see the [source map](cognee-source-map.md) for inspection limits.

[^cognee]: Revision `525b1d1`, `README.md::Quickstart`, `README.md::How Cognee works`, `pyproject.toml::[project]`.
