---
type: Concept
title: "RAGFlow answer citation mechanisms"
description: "Similarity-based citation insertion and agentic evidence-ID tracking have distinct provenance and correctness limits."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
---

# RAGFlow answer citation mechanisms

**Observed:** RAGFlow has two materially different citation paths: sentence-to-chunk similarity insertion in conventional chat, and evidence-registry IDs plus explicit chunk references in agentic retrieval. Both produce `[ID:n]`-style markers, but matching marker syntax does not imply identical evidence semantics.[^ragflow]

## Conventional chat: inferred citation placement

`InsertCitations` and `InsertCitationsWithVectors` split an answer and compare sentence/chunk embeddings. Citation selection lowers its threshold from 0.63 toward 0.3 with multiplicative steps and caps references at four per sentence. Repair/extraction helpers and a streaming citation filter handle marker forms. Chat/ask services call this citation machinery.[^ragflow]

**Synthesis:** similarity-based attachment indicates related retrieved text, not independent entailment verification or a guarantee that the generator relied on that chunk. Citation evaluation must separate retrieval quality, sentence faithfulness, and reference formatting.[^ragflow]

## Agentic retrieval: explicit evidence identity

`EvidenceRegistry` assigns stable first-seen IDs to served evidence text. Agentic citation helpers parse explicit chunk references and append citation markers outside code spans; insertion is intended to be idempotent. The service resolves selected references into response payloads. This provenance mechanism differs from post-hoc embedding matching.[^ragflow]

**Synthesis:** deterministic evidence identity improves traceability but does not establish that every cited claim is supported. Neither citation algorithm was executed or audited against annotated answers during this ingest.[^ragflow]

## Relationships

- **Uses:** [retrieval](ragflow-retrieval.md) for source chunks.
- **Used by:** [agent workflows](ragflow-agent-workflows.md) and [streaming UI](ragflow-frontend.md).

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa0`; locators: `internal/service/citation.go::InsertCitations / InsertCitationsWithVectors / splitAnswer / findCitations / applyCitations / RepairBadCitationFormats / citationStreamFilter`; `internal/service/chat_pipeline.go::InsertCitations call`; `internal/service/ask_service.go::InsertCitations call`; `internal/agentic_rag/citations.go::ExtractCitedChunkIDs / InsertCitationMarkers`; `internal/agentic_rag/evidence_registry.go::EvidenceRegistry.ServeText / Stamp`; `internal/service/agentic_reference.go::reference resolution`.
