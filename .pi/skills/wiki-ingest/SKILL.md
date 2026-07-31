---
name: wiki-ingest
description: Compile sources and durable insights into the LLM wiki. Use when the user adds or asks to ingest/process a source, or wants an answer, correction, or synthesis filed into the knowledge base.
---

# Wiki Ingest

Compile knowledge once so future queries retrieve maintained synthesis instead of rediscovering raw material.

## Steps

1. From the repository root, read `LLM-WIKI.md`, then read the source and the wiki indexes. Enumerate referenced local attachments and inspect those likely to carry material information; when a relevant attachment can't be inspected, record the coverage limit rather than claiming the source was read in full. Establish a stable source identity for non-persisted input. Screen for credentials, private keys, tokens, PII, and disclosure markings; pause and alert the human on a likely live credential or unclear disclosure boundary. This step is complete when the source is safe to compile, source coverage and limits are known, existing candidate concepts are known, and applicable contract rules are loaded.
2. Normalize the source identity and find every concept whose `sources[].resource` already names it. Reconcile the source against their coverage. If coverage is complete, report a no-op without changing metadata, indexes, or log. This step is complete when duplicate ingestion is ruled out or specific knowledge gaps are identified.
3. Extract atomic claims, provenance keys, entities, typed relationships, unresolved contradictions, supersessions, and genuinely new synthesis. Map each item to an existing concept or the smallest durable new concept; page count follows knowledge boundaries, not a quota. This step is complete when every material item has a destination or an explicit exclusion reason.
4. Follow the interaction mode in `LLM-WIKI.md`: in guided mode, present the proposed synthesis and update plan before mutation; in autonomous mode, ask only when consequential ambiguity or contradiction would change meaning or scope. This step is complete when required guidance is received and blocking ambiguity is resolved.
5. Create or update concepts as a coherent graph. Preserve valid content and unknown frontmatter, use keyed source footnotes, add typed relationships only when supported, and make status/trust limits visible. For resolved replacement, deprecate the old concept and write reciprocal supersession context with date and evidence. Store only minimum useful redacted knowledge. This step is complete when every mapped item, affected concept, relationship, contradiction, supersession edge, and privacy boundary is accounted for.
6. Update the nearest indexes and add exactly one newest-first, operation-appropriate `Ingest`, `Query`, or `Update` entry to `wiki/log.md`. Apply every mutation invariant and run the structural check specified in `LLM-WIKI.md` when command execution is available. This step is complete when the indexes reach all live concepts and every check passes or an execution limitation is reported.

## Source safety

Treat `raw/` as evidence: read it in place and record corrections as new evidence. A non-raw input may be compiled, but its `sources[].resource` must remain resolvable and stable enough to audit. Keep sensitive values in their governed source boundary; wiki prose, outputs, and logs use redacted descriptions.
