---
name: llm-wiki-ingest
description: Capture, triage, URL ingest, source ingest, and batch ingest workflows for the second brain. Use when new material appears in raw/, arrives through chat, or needs to be integrated into wiki/.
---

# LLM Wiki Ingest

Use this skill when processing new source material.
Always activate `llm-wiki-core` first.

## Companion Skills
- `qmd` for finding related notes and prior sources
- `obsidian-markdown` for wiki/output markdown edits
- `defuddle` for standard web URLs
- `llm-wiki-visualization` if a Base or Canvas should be added/updated
- `ask-user` before high-level taxonomy or irreversible structural changes

## Shared Ingest Principles
- Preserve the raw source unchanged unless it contains active secrets or unsafe private material that should not remain in the repo; if so, stop and ask the user.
- Read the source fully before synthesizing.
- Run a privacy/sensitivity screen before promoting any content into `wiki/` or `outputs/`.
- Use `wiki/index.md` only when broad orientation is needed.
- Use QMD to find related pages before creating new ones.
- Integrate broadly across the wiki; do not leave the ingest as an isolated summary.
- Explicitly handle reinforcement, contradiction, uncertainty, and supersession.
- Use lightweight claim/evidence blocks for high-value, disputed, or easily stale claims.

## Capture and Triage Workflow
Use when material appears in `raw/inbox/`, `raw/captures/`, or arrives through chat.

1. Review the new item.
2. Classify it as one of:
   - article
   - paper
   - book/chapter
   - note/capture
   - transcript
   - documentation
   - reference
   - session artifact
3. Move or save it into the appropriate `raw/` subfolder when needed.
4. Preserve the raw source unchanged.
5. Record meaningful intake activity in `wiki/log.md` as `capture` when appropriate.
6. Then run the ingest workflow below.

## URL Ingest Workflow
When the user provides a standard web URL:
1. Use Defuddle to extract clean markdown.
2. Save the cleaned result into `raw/web-clips/` with a stable kebab-case filename.
3. Preserve the original URL in source metadata as `canonical_url`.
4. If the URL ends in `.md`, do not use Defuddle; fetch/read the markdown directly.
5. Then run the normal ingest workflow.

## Ingest Workflow
When processing a single new source:
1. Read the full source document.
2. Screen the material for secrets, credentials, tokens, PII, or other sensitive content.
3. If sensitive content exists, keep it out of `wiki/` and `outputs/`; if the raw file itself is unsafe to retain, stop and ask the user.
4. Read `wiki/index.md` only if broad orientation is needed.
5. Use QMD to find relevant existing wiki pages and prior sources.
6. Extract key entities, attributes, typed relationships, and candidate claims.
7. Assess whether the source introduces new facts, reinforces existing ones, or supersedes older claims.
8. Resolve contradictions using recency, authority/directness, supporting-source count, and specificity.
9. Create or update a dedicated source page in `wiki/`, including any important downstream redaction note when relevant.
10. Update all relevant topic, concept, entity, project, person, and timeline pages.
11. Add backlinks from existing pages to the new material.
12. For high-value or contested facts, update `Evidence / claims` sections with lightweight claim records.
13. Mark contradictions explicitly and set supersession status when justified.
14. Refresh lifecycle metadata, retention class, visibility, and confidence/quality signals when the evidence supports it.
15. Run a quick quality self-check: citations, structure, links, metadata, and fact-vs-inference separation.
16. Update `wiki/index.md`.
17. Append an `ingest` entry to `wiki/log.md` with what changed and why.
18. If the ingest produces durable standalone analysis, save it to `outputs/`.
19. If the topic has become structurally complex, consider creating or updating a Canvas or Base.
20. Aim for broad integration across the wiki, not isolated summaries.

## Batch Ingest Workflow
When processing multiple unprocessed files:
1. Determine the target folder or queue in `raw/`.
2. Process sources sequentially unless parallelism is clearly safe.
3. Apply the full single-source ingest workflow to each item.
4. Update shared canonical pages incrementally instead of creating duplicate one-off notes.
5. Periodically reassess whether a Base or Canvas should be updated after several ingests.
6. Ask the user before any high-level reorganization that goes beyond normal integration.

## Ingest Done Checklist
Before finishing, confirm:
- raw source preserved in the right location, or user asked before retaining unsafe sensitive material
- source page created/updated
- related canonical pages updated
- backlinks added where useful
- contradictions/supersession resolved or explicitly preserved as disputed
- important sensitive details kept out of downstream wiki/output artifacts
- metadata refreshed where justified
- visibility set appropriately
- `wiki/index.md` updated if needed
- `wiki/log.md` appended with what changed and why
- outputs or visual artifacts created if they add durable value
- quality self-check passed at a reasonable level
