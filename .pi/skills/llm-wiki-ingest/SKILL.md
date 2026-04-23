---
name: llm-wiki-ingest
description: Capture, triage, URL ingest, source ingest, and batch ingest workflows for the second brain. Use when new material appears in raw/, arrives through chat, or needs to be integrated into wiki/.
---

# LLM Wiki Ingest

Use for new source material.
Always activate `llm-wiki-core` first. Core owns shared rules for privacy, metadata, citations, naming, supersession, index/log, and governance. This file covers ingest-specific flow only.

## Companion Skills
- `qmd` → find related notes and prior sources
- `obsidian-markdown` → wiki/output markdown edits
- `defuddle` → standard web URLs
- `llm-wiki-visualization` → add/update Base or Canvas when structure gets complex
- `ask-user` → high-level taxonomy or irreversible structural changes

## Ingest-Specific Principles
- Preserve raw source unchanged unless unsafe sensitive material should not remain in repo; if raw file itself is unsafe, stop and ask user.
- Read source fully before synthesis.
- Run privacy/sensitivity screen before promoting content into `wiki/` or `outputs/`.
- Use QMD to find related pages before creating new ones.
- Integrate broadly; avoid isolated summary notes.
- Handle reinforcement, contradiction, uncertainty, supersession explicitly.
- Use lightweight claim/evidence blocks for high-value, disputed, or easily stale claims.

## Capture and Triage Workflow
Use when material lands in `raw/inbox/`, `raw/captures/`, or chat.

1. Review new item.
2. Classify it:
   - article
   - paper
   - book/chapter
   - note/capture
   - transcript
   - documentation
   - reference
   - session artifact
3. Move or save into correct `raw/` subfolder when needed.
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
1. Read full source.
2. Screen for secrets, credentials, tokens, PII, other sensitive content.
3. If sensitive content exists, keep it out of `wiki/` and `outputs/`; if raw file itself is unsafe to retain, stop and ask user.
4. Read `wiki/index.md` only if broad orientation is needed.
5. Use QMD to find relevant existing wiki pages and prior sources.
6. Extract key entities, attributes, typed relationships, candidate claims.
7. Decide what is new, what reinforces old knowledge, what supersedes older claims.
8. Resolve contradictions using recency, authority/directness, supporting-source count, specificity.
9. Create or update dedicated source page in `wiki/`.
10. Update all relevant topic, concept, entity, project, person, timeline pages.
11. Add backlinks from existing pages to new material.
12. For high-value or contested facts, update `Evidence / claims` with lightweight claim records.
13. Mark contradictions explicitly and set supersession state when justified.
14. Refresh lifecycle metadata, retention class, visibility, confidence/quality signals when evidence supports it.
15. Run quick self-check: citations, structure, links, metadata, fact-vs-inference separation.
16. Apply core index/log rules: update `wiki/index.md` when needed; append `wiki/log.md` with what changed and why.
17. If ingest produces durable standalone analysis, save it to `outputs/`.
18. If topic becomes structurally complex, consider Canvas or Base.
19. Goal = broad integration across wiki, not isolated summary.

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
- raw source preserved in right location, or user asked before retaining unsafe sensitive material
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
