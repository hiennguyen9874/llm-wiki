---
name: wiki-learn
description: Create beginner-first wiki course pages from wiki sources.
disable-model-invocation: true
---

# Wiki Learn

Build one durable beginner-first `course` in `wiki/` that turns scattered wiki concepts into a teachable, verifiable page with theory and runnable code.

Lead word is `course` — every decision serves a single `course` that a newcomer can read, run, and test without re-discovering the source graph.

## Steps

1. **Map the request to concepts — follow `wiki-query`.**
   Read `wiki-query` skill and follow its steps 1-2: read `LLM-WIKI.md` and `wiki/index.md`, then translate `$ARGUMENTS` into required concepts, aliases, and constraints. Search progressively: glob for scope, exact text for tags/titles/relationships, then `qmd-retrieval` only on a lexical miss. This step is complete when every needed concept has a candidate path and every retrieval gap is explicit.

2. **Retrieve and verify evidence — follow `wiki-query`.**
   Read `wiki-query` skill and follow its steps 3-4: read every candidate concept, follow its typed relationships (`Depends on`, `Uses`, `Supersedes`, `Contradicts`), and open `raw/` only to verify a disputed citation or fill a provenance gap per the contract's retrieval policy. Check `status`, `stale_after`, verification, and contradictions. This step is complete when each material claim for the `course` is backed by a wiki concept or raw source, or is explicitly marked as synthesis/uncertain — no uncited durable claim remains.

3. **Plan the course slot and outline.**
   Derive a kebab-case slug from the topic and pick the suffix that matches the form: `-beginners-guide.md` for an explanation, `-beginners-course.md` for a sequenced lesson, `-beginners-project.md` for a build-and-verify lab. Resolve the output slot per Placement rule below and draft the heading outline that will satisfy the Course Template (every template block has a destination or an explicit omission reason). This step is complete when slug, slot, frontmatter `sources[]`, and section plan are fixed and duplicate ingestion is ruled out.

4. **Draft the course file.**
   Write the file at the planned slot following `references/TEMPLATE.md` and `obsidian-markdown`. Keep prose Vietnamese, keep technical keywords in English, add English glosses on first use only. Include theory with LaTeX, one inspectable PyTorch example, executable verification tests, and a benchmark or trade-off table when performance is claimed. Attribute every source-dependent claim with a keyed footnote matching `sources[].id`. This step is complete when the file parses as OKF v0.2, renders in Obsidian preview, and every template block is present or explicitly omitted.

5. **Validate, index, and log — follow `wiki-ingest`.**
   Read `wiki-ingest` skill and follow its step 6 and `LLM-WIKI.md` mutation invariants: run `python3 tools/wiki_check.py` when available, fix deterministic errors (missing frontmatter, broken relative links, duplicate index entries), update the nearest `index.md` (and `wiki/learn/index.md` if the `wiki/learn/` group exists), and append exactly one newest-first entry to `wiki/log.md`. This step is complete when `wiki/index.md` reaches the new concept (including via a `wiki/learn/` group entry when grouped), all mutation invariants hold, and the structural check passes or its execution limit is recorded.

## Placement

Durable `course` pages are queryable knowledge — they belong in `wiki/`, not in `outputs/` or a top-level `learn/` outside the OKF bundle.

| Slot | When | Indexed | Logged |
|---|---|---|---|
| `wiki/<slug>-beginners-guide.md` | Default — durable, reviewed `course` (177 concepts flat today) | `wiki/index.md` | `Query` or `Ingest` entry |
| `wiki/learn/<slug>.md` with `wiki/learn/index.md` | Graduate here only when `wiki/` flat scanning degrades or `course` count > ~15–20 and a group makes retrieval materially easier | `wiki/learn/index.md` + root summary link in `wiki/index.md` | same as above |
| `outputs/learn-<slug>-preview.md` | Explicit draft/preview request, or verification fails — not yet durable | not indexed | no log |

Do not write a durable `course` to `outputs/` or to a top-level `learn/`; `outputs/` is disposable and a top-level `learn/` breaks the contract's "wiki/ is the query surface" and makes `sources[].resource` links and graph traversal inconsistent.

## Course Template

Full block order and field rules are in `references/TEMPLATE.md`. Summary:

Frontmatter: `type: Synthesis` (or `type: Course` if adopted), `title`, `description` (one index-ready sentence), `tags`, `status`, `created`, `generated`, `sources[]`. Body: H1 title → one-paragraph synthesis → `> [!success]` outcome box → Prerequisites/Trước khi đọc → Theory (formulas, tables, `text` diagrams) → Implementation (minimal PyTorch, `interleaved` RoPE convention and absolute `position_ids` documented when attention is involved) → Verification (numbered tests, `torch.testing.assert_close` with `rtol/atol`) → Benchmark/Trade-offs if applicable → Debug checklist → Limitations & Next steps → `## Relationships` with typed bullets → `## Evidence limits` → keyed footnotes. Keep `outputs/` code toy-explicit: `torch.cat` caching is teaching, not serving.

## References

- Template blocks, frontmatter example, and heading skeleton: `references/TEMPLATE.md`
- Retrieval legwork (steps 1-2 above): `wiki-query` skill — external reference, read on demand; not activated via prompt
- Ingest and mutation invariants (step 5 above): `wiki-ingest` + `LLM-WIKI.md`, `wiki/index.md`, `wiki/log.md` — external reference, read on demand; not activated via prompt
- Obsidian rendering (frontmatter, callouts, math, mermaid): `obsidian-markdown` skill (model-invoked, reached via pointer; not listed in prompt)
