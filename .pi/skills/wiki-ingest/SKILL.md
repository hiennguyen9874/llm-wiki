---
name: wiki-ingest
description: Compile sources and durable insights into the LLM wiki. Use when the user adds or asks to ingest/process a source, or wants an answer, correction, or synthesis filed into the knowledge base.
---

# Wiki Ingest

Compile knowledge once so future queries retrieve maintained synthesis instead of rediscovering raw material.

## Steps

1. From the repository root, read `LLM-WIKI.md`, then read the source in full and the wiki indexes. If the input isn't persisted, establish a stable source identity before citing it. This step is complete when the source, existing candidate concepts, and applicable contract rules are known.
2. Normalize the source identity and find every concept whose `sources[].resource` already names it. Reconcile the source against their coverage. If coverage is complete, report a no-op without changing metadata, indexes, or log. This step is complete when duplicate ingestion is ruled out or specific knowledge gaps are identified.
3. Extract atomic claims, provenance keys, entities, relationships, disagreements, and genuinely new synthesis. Map each item to an existing concept or the smallest durable new concept; page count follows knowledge boundaries, not a quota. This step is complete when every material item has a destination or an explicit exclusion reason.
4. Present the proposed synthesis and consequential contradictions for user guidance when judgment would change meaning or scope. Otherwise proceed autonomously. This step is complete when blocking ambiguity is resolved.
5. Create or update concepts as a coherent graph. Preserve valid content and unknown frontmatter, use keyed source footnotes, and make status/trust limits visible. This step is complete when every mapped item and every affected existing concept is accounted for.
6. Update the nearest indexes and add one newest-first `Ingest` or `Update` entry to `wiki/log.md`. Apply every mutation invariant and run the structural check specified in `LLM-WIKI.md` when command execution is available. This step is complete when the indexes reach all live concepts and every check passes or an execution limitation is reported.

## Source safety

Treat `raw/` as evidence: read it in place and record corrections as new evidence. A non-raw input may be compiled, but its `sources[].resource` must remain resolvable and stable enough to audit.
