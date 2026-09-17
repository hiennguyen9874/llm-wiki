---
name: wiki-ingest
description: Ingest sources and durable insights into the LLM wiki. Use when the user adds or asks to process a source, or wants an answer, correction, or synthesis filed into the knowledge base.
---

# Wiki Ingest

Compile knowledge once so future queries retrieve maintained synthesis instead of rediscovering raw material.

## Gates

1. **State, scope, and safety.** From the repository root, read `LLM-WIKI.md` and independently inventory concept and reserved files. Classify the wiki under the contract. Continue from a valid empty or populated state; defer scaffolding for an uninitialized wiki until durable knowledge is ready; route a damaged state through `wiki-lint` before ingestion. Load the scope and screen the source for credentials, private keys, tokens, PII, disclosure restrictions, and executable content. Pause on consequential scope ambiguity, a likely live credential, or an unclear disclosure boundary. This gate is complete when the state is classified, applicable policy is loaded, and the source is safe and in scope.

2. **Logical source bundle.** Classify the source and identify its canonical entry point, logical scope, immutable version or revision, and material dependency closure. Inventory includes, imports, configurations, launchers, manifests, tests, attachments, supplements, and linked local evidence. Distinguish project-owned evidence from generated, cached, duplicated, vendored, binary, decorative, unavailable, and potentially material uninspected artifacts. Use static inspection by default; execute code or compile documents only in an authorized safe environment. This gate is complete when a coverage ledger names every discovered material artifact as inspected, executed, excluded with reason, unreadable, or pending.

3. **Identity reconciliation.** Normalize package identity according to `LLM-WIKI.md`. Find every concept citing its scope, canonical resource, revision, or a supporting resource inside the scope; include any relevant `SourceMap`. Reconcile prior coverage rather than treating an internal file as a new source. Complete prior coverage is a no-op that leaves concepts, metadata, indexes, and log unchanged. This gate is complete when duplicate ingestion is ruled out or each missing coverage or knowledge item is explicit.

4. **Source-profile extraction.** Read [`references/source-profiles.md`](references/source-profiles.md), then apply the common profile and every matching source-type profile. Capture atomic claims, assumptions, qualifiers, entities, terminology, procedures, evidence, negative findings, contradictions, supersessions, and typed relationships. Classify consequential findings as reported, observed, reproduced, or synthesis, and capture the best available section, table, figure, symbol, key, region, query, or timestamp locator. This gate is complete when every applicable profile field is extracted or has an explicit exclusion or unknown reason.

5. **Durable mapping.** Apply a durable-value filter: each item must improve future retrieval, verification, reuse, comparison, or a decision. Map retained items to existing concepts or the smallest cohesive new boundaries; split independently retrievable questions and preserve an overview only when it aids navigation. Account for the source's contribution, mechanism, constraints, evidence, limitations, relationships, and material attachments without reproducing decorative, repetitive, transient, or merely narrative detail. A zero-yield source is reported as a no-op and creates no concept or log entry. This gate is complete when every extracted item has a concept destination or a recorded exclusion reason and every proposed page has one coherent retrieval purpose.

6. **Plan and interaction.** Prepare the concepts created or updated, source identities and locators, relationships, contradictions or supersessions, coverage persisted, exclusions, status choices, and unresolved ambiguity. In guided mode, present this plan before mutation. In autonomous mode, proceed unless consequential ambiguity would change meaning, scope, privacy, or governance. This gate is complete when required guidance is received and no blocking ambiguity remains.

7. **Coherent mutation.** Create or update concepts as one graph. On a first successful ingest, create the reserved files, initial concepts, and index entries in the same operation; create no placeholders. Preserve valid content and unknown frontmatter, cite the canonical source entry point, use claim-level locators, assign `draft` or `stable` by the maturity contract, and persist consequential coverage and trust limits. Use a `SourceMap` only when a multipart collection needs a durable package-level ledger. For resolved replacement, deprecate the old concept and write reciprocal supersession context with date and evidence. This gate is complete when every planned item, affected edge, privacy boundary, and root/index change is represented in the staged wiki state.

8. **Validation and commit.** Validate source-ID/citation/footnote joins, source paths and scopes, evidence labels, concept cohesion, coverage limits, status, links, metadata/index agreement, complete index reachability, and privacy. Add exactly one newest-first `Ingest`, `Query`, or `Update` entry only after that semantic preflight, then run `python3 tools/wiki_check.py` and directly check any contract invariant the tool does not enforce. Repair or roll back this operation's incomplete edits when a check fails. This gate is complete only when every mutation invariant passes and the single log entry describes the completed state.

## Source safety

Treat `raw/` as immutable evidence and record corrections as new artifacts or revisions. A non-raw input may be compiled only when its `sources[].resource` remains stable and resolvable. Keep sensitive values inside their governed source boundary; wiki prose, outputs, and logs contain only the minimum useful redacted description.
