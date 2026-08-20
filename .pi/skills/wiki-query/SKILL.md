---
name: wiki-query
description: Retrieve and synthesize answers from the LLM wiki. Use when the user asks a knowledge question, comparison, analysis, report, or search grounded in the knowledge base.
---

# Wiki Query

Retrieve progressively: map first, concepts second, raw evidence only on demand.

## Steps

1. From the repository root, read the retrieval policy in `LLM-WIKI.md` and `wiki/index.md`. Translate the question into concepts, aliases, relationships, and constraints. This step is complete when candidate pages and known retrieval gaps are explicit.
2. Build a candidate union progressively. Use glob for structural scope and exact text search for titles, aliases, tags, identifiers, metadata, and relationship labels. When exact retrieval is too broad or misses the user's vocabulary, follow `qmd-retrieval`: use BM25 `search` for lexical ranking and hybrid `query` only for semantic, ambiguous, or cross-concept gaps. QMD is optional; an unavailable or stale cache falls back to repository search, and its scores cannot discard catalog or exact matches. This step is complete when candidate paths from every applicable retrieval channel are deduplicated and remaining gaps are explicit.
3. Read candidate concepts and traverse relationship types suited to the question: `Depends on` and `Uses` for impact, `Caused` and `Fixed by` for diagnosis, `Supersedes` and `Contradicts` for freshness, and `Owned by` for responsibility. This step is complete when each relevant relationship frontier has been checked and remaining gaps are explicit.
4. Evaluate provenance, lifecycle, freshness, verification, and contradictions before synthesis. Open raw sources only under the contract's retrieval policy. This step is complete when each material answer claim is supported, identified as synthesis, or marked uncertain.
5. Answer directly with Markdown links to wiki concepts. Separate documented knowledge from inference and state consequential gaps or stale evidence. This step is complete when the question is answered to its requested scope and every material claim has a visible basis.
6. Crystallize through `wiki-ingest` when the result creates reusable multi-concept synthesis, a durable comparison, a decision or lesson, a supported new relationship, a contradiction resolution, or a verified procedure. Cite underlying concepts or raw sources rather than transient chat, and integrate extracted insights into affected concepts. Save requested transient deliverables under `outputs/`; read-only answers leave the wiki and log unchanged. This step is complete when every durable insight is filed or explicitly left transient.
