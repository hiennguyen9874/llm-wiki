---
name: wiki-query
description: Retrieve and synthesize answers from the LLM wiki. Use when the user asks a knowledge question, comparison, analysis, report, or search grounded in the knowledge base.
---

# Wiki Query

Retrieve progressively: map first, concepts second, raw evidence only on demand.

## Steps

1. From the repository root, read the retrieval policy in `LLM-WIKI.md` and `wiki/index.md`. Translate the question into concepts, aliases, relationships, and constraints. This step is complete when candidate pages and known retrieval gaps are explicit.
2. Read candidate concepts and follow relevant links. Expand with text search only when index metadata and links don't cover the question. This step is complete when additional pages stop changing the answer or a named gap prevents completion.
3. Evaluate provenance, lifecycle, freshness, verification, and contradictions before synthesis. Open raw sources only under the contract's retrieval policy. This step is complete when each material answer claim is supported, identified as synthesis, or marked uncertain.
4. Answer directly with Markdown links to wiki concepts. Separate documented knowledge from inference and state consequential gaps or stale evidence. This step is complete when the question is answered to its requested scope and every material claim has a visible basis.
5. When the result adds reusable knowledge, offer to file it with `wiki-ingest`; save requested deliverables under `outputs/`. Read-only answers leave the wiki and log unchanged. This step is complete when durable output has a clear destination.
