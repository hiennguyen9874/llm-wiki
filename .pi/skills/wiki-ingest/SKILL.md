---
name: wiki-ingest
description: Compile sources into the LLM wiki. Use when the user adds or asks to process a source, or asks to file an answer, correction, or synthesis into the knowledge base.
---

# Wiki Ingest

Compile knowledge once so future queries retrieve maintained synthesis instead of rediscovering raw material. Each gate applies a section of `AGENTS.md`.

## Gates

1. **State, scope, and safety.** From the repository root, read `SCOPE.md` (when present), inventory concept and reserved files, and classify the wiki state. Valid empty or populated: continue. Uninitialized: continue; the scaffold appears only at gate 7, with the first durable concepts. Damaged: repair through `wiki-lint` first. Apply the `SCOPE.md` inclusion test, exclusions, and domain rules; name the source's primary domain and register a new one per `SCOPE.md` Governance in this same mutation. Screen for sensitive values, disclosure restrictions, and executable content, pausing as the contract requires. Done when the state is classified, applicable policy is loaded, and the source is safe and in scope.

2. **Coverage ledger.** Identify the source's entry point, scope, revision, and material dependency closure: includes, imports, configurations, launchers, manifests, tests, attachments, supplements, and linked local evidence. Separate project-owned evidence from generated, cached, duplicated, vendored, binary, decorative, and unavailable artifacts. Inspect statically; execute code or compile documents only in an authorized safe environment. A non-raw input is compilable only when its `resource` stays stable and resolvable. Done when the coverage ledger names every discovered material artifact.

3. **Idempotency.** Apply the contract's idempotency rule, including any relevant `SourceMap`. A supporting file inside a known scope reconciles against its package. Complete prior coverage ends the run as a no-op. Done when duplicate ingestion is ruled out or each missing item is explicit.

4. **Extraction.** Read [`references/source-profiles.md`](references/source-profiles.md) and apply the common profile plus every matching source-type profile. Capture claims, assumptions, qualifiers, entities, terminology, procedures, evidence, negative findings, contradictions, supersessions, and typed relationships, each consequential finding tagged with its evidence class and locator. Done when every applicable profile field is extracted or has an explicit exclusion or unknown reason.

5. **Durable mapping.** Keep only durable items. Map each to an existing concept or the smallest cohesive new boundary, following the contract's split rule. Account for the source's contribution, mechanism, constraints, evidence, limitations, relationships, and material attachments; leave decorative, repetitive, transient, and merely narrative detail behind. A zero-yield source is reported as a no-op with no concept or log entry. Done when every extracted item has a destination or a recorded exclusion reason and every proposed page has one retrieval purpose.

6. **Plan.** List concepts created or updated, source identities and locators, relationships, contradictions or supersessions, persisted coverage, exclusions, status choices, and open ambiguity. Apply the interaction mode: `guided` presents the plan and waits; `autonomous` proceeds unless ambiguity would change meaning, scope, privacy, or governance. Done when required guidance is received and no blocking ambiguity remains.

7. **Mutation.** Write the concepts as one graph. On a first ingest, create the reserved files, concepts, and index entries together, with no placeholders. Preserve valid content and unknown frontmatter, cite the canonical entry point, choose `draft` or `stable` by the metadata rules, persist consequential coverage and trust limits, and write supersession per the concept contract. Done when every planned item, affected edge, privacy boundary, and index change is in the working tree.

8. **Validate and log.** Confirm every mutation invariant in `AGENTS.md`, then add exactly one newest-first log entry (`Ingest` for sources, `Query` for filed query results, `Update` for corrections) and run the structural check plus the direct checks it lists. Repair or roll back this operation's edits when a check fails. Done when every invariant passes and the single log entry describes the completed state.
