---
name: llm-wiki-ingest
description: Capture, triage, URL ingest, source ingest, and batch ingest workflows for the second brain. Use when new material appears in raw/, arrives through chat, or needs to be integrated into wiki/.
---

# LLM Wiki Ingest

Use for new source material.
Always activate `llm-wiki-core` first.

This file owns ingest procedure only.
- Use `llm-wiki-schema` when creating or updating structured markdown, frontmatter, claim blocks, or source metadata.
- Use `llm-wiki-governance` for privacy, contradiction, supersession, review-queue, or other risky judgment calls.
- Use `llm-wiki-ops` when naming, folder placement, `wiki/index.md`, or `wiki/log.md` updates matter.

## Companion Skills
- `qmd` → find related notes and prior sources
- `obsidian-markdown` → wiki/output markdown edits
- `defuddle` → standard web URLs
- `llm-wiki-visualization` → add or update a Base or Canvas when structure gets complex
- `ask-user` or review queue → handle high-stakes taxonomy or irreversible structural decisions

## Ingest-Specific Principles
- Use a two-stage ingest for substantial sources: first an explicit ingest plan, then page generation/integration.
- The stage-1 plan is not hidden chain-of-thought; it is a concise, auditable artifact with entities, claims, affected pages, contradictions, review items, and proposed edits.
- Save stage-1 plans selectively in `outputs/ingest-plans/` when they contain non-trivial decisions, contradictions, review items, or broad integration plans.
- For trivial captures, use a fast path but still apply core safety, traceability, retrieval, citation, and logging expectations.
- Preserve raw source unchanged unless unsafe sensitive material should not remain in repo; if raw retention itself is unsafe, stop and ask user.
- Maintain source traceability with `related_sources: []` on wiki pages and source metadata on source pages.
- Read source fully before synthesis.
- Use QMD to find related pages before creating new ones.
- Integrate broadly; avoid isolated summary notes.
- Handle reinforcement, contradiction, uncertainty, and supersession explicitly.

## Capture and Triage Workflow
Use when material lands in `raw/inbox/`, `raw/captures/`, or chat.

1. Review new item.
2. Classify it: article, paper, book/chapter, note/capture, transcript, documentation, reference, or session artifact.
3. Move or save into the correct `raw/` subfolder when needed.
4. Preserve raw source unchanged.
5. Append `wiki/log.md` as `capture` when intake is meaningful.
6. Then run ingest workflow.

## URL Ingest Workflow
When user gives standard web URL:
1. Use Defuddle to extract clean markdown.
2. Save result into `raw/web-clips/` with stable kebab-case filename.
3. Preserve original URL in source metadata as `canonical_url`.
4. If URL ends in `.md`, skip Defuddle; fetch/read markdown directly.
5. Then run normal ingest workflow.

## Ingest Workflow
When processing one new source:

### Stage 0 — orientation and safety
1. Read full source.
2. Screen for secrets, credentials, tokens, PII, or other sensitive content.
3. If sensitive content exists, keep it out of `wiki/` and `outputs/`; if raw retention itself is unsafe, stop and ask user.
4. Read `purpose.md`, `wiki/overview.md`, and `wiki/index.md` when broad orientation helps; skip for narrow or trivial items.
5. Use QMD to find relevant existing wiki pages and prior sources.

### Stage 1 — ingest plan
6. Produce a structured ingest plan before editing pages for substantial sources. Include:
   - source identity and why it matters to `purpose.md`
   - key entities, attributes, typed relationships, and candidate claims
   - related existing pages and likely affected pages
   - what is new, reinforced, contradicted, superseded, or uncertain
   - proposed source page and canonical page updates
   - `related_sources` updates needed for affected wiki pages
   - whether this should remain single-source ingest or trigger a later `/compile` pass
   - review items for human judgment with recommended action
   - whether an output, Base, Canvas, overview update, or deep-research prompt is warranted
7. Save the plan to `outputs/ingest-plans/` only when it has durable audit value; otherwise keep it in chat and summarize in log.
8. If the plan exposes high-stakes taxonomy/schema/destructive decisions, ask user before proceeding. If non-blocking, create review queue items in `outputs/review-queue/`.

### Stage 2 — generation and integration
9. Create or update dedicated source page in `wiki/`.
10. Update all relevant topic, concept, entity, project, person, timeline, synthesis, and overview pages.
11. Add or refresh `related_sources` on affected wiki pages so source support is traceable.
12. Add backlinks from existing pages to new material.
13. For high-value or contested facts, add lightweight `Evidence / claims` records.
14. Mark contradictions explicitly and set supersession state when justified.
15. Refresh lifecycle metadata, retention class, visibility, confidence/quality signals, and source metadata when evidence supports it.
16. Run quick self-check: citations, structure, links, metadata, fact-vs-inference separation, and plan-to-edit consistency.
17. Update `wiki/index.md` when discoverability changes and append `wiki/log.md` with what changed and why.
18. If ingest produces durable standalone analysis, save it to `outputs/`.
19. If topic becomes structurally complex, consider Canvas or Base.
20. Goal = broad integration across wiki, not isolated summary.

## Compile Workflow
Use when several raw sources, saved answers, analyses, or crystallizations should become one coherent semantic update instead of isolated summaries.

1. Classify mode as `incremental` unless the user requests `full`.
2. Read `purpose.md`, `wiki/overview.md`, and `wiki/index.md` when scope is broad or strategic.
3. Use QMD for exact and conceptual retrieval across `wiki/`, `outputs/`, and relevant `raw/` paths.
4. Read selected files before synthesis; do not compile from snippets or index summaries alone.
5. Produce a concise compile plan in chat before editing. Include affected sources/outputs, canonical pages to create/update, traceability updates, contradictions/supersession, overview/index/log updates, and human review items.
6. Ask before high-stakes taxonomy/schema/bulk move/delete/merge changes. Queue non-blocking judgments in `outputs/review-queue/`.
7. Update or create canonical wiki pages. Prefer integration into existing pages over isolated summaries.
8. Refresh traceability, claim/evidence blocks, confidence/quality, retention, visibility, contradictions, and supersession where justified.
9. Update `wiki/overview.md`, `wiki/index.md`, and `wiki/log.md` when required by core + ops rules.
10. Save the compile plan under `outputs/analyses/` or `outputs/ingest-plans/` only when it has durable audit value.

## Batch Ingest Workflow
When processing multiple unprocessed files:
1. Determine target folder or queue in `raw/`.
2. Process sequentially unless parallelism is clearly safe.
3. Apply full single-source ingest workflow to each item.
4. Update shared canonical pages incrementally instead of creating duplicate one-off notes.
5. Reassess after several ingests whether Base or Canvas should be updated.
6. Ask user before high-level reorganization beyond normal integration.

## Ingest Done Checklist
Before finishing, confirm:
- raw source preserved in the right location, or user asked before retaining unsafe sensitive material
- stage-1 ingest plan produced for substantial source, and saved selectively if audit-worthy
- review queue items created for non-blocking human judgments
- source page created/updated
- related canonical pages updated
- backlinks added where useful
- contradictions/supersession resolved or preserved as disputed
- important sensitive details kept out of downstream wiki/output artifacts
- metadata refreshed where justified
- visibility set appropriately
- `wiki/index.md` updated if needed
- `wiki/log.md` appended with what changed and why
- outputs or visual artifacts created if they add durable value
- quality self-check passed
