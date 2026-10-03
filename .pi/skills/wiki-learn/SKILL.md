---
name: wiki-learn
description: Write a beginner-first course page into the wiki from compiled concepts.
disable-model-invocation: true
---

# Wiki Learn

Build one durable beginner-first **course**: a wiki page a newcomer can read, practice, and verify without re-walking the source graph.

## Steps

1. **Retrieve: run `wiki-query` steps 1–4** for the topic in `$ARGUMENTS`. Done when every claim the course will make is backed by a wiki concept or raw source, or labeled synthesis or uncertain, and every retrieval gap is explicit.

2. **Plan.** Take the course's primary domain from its concepts' tags and group paths, and pick the course profile `SCOPE.md` maps to it (else the `SCOPE.md` default). Read `references/profiles/<profile>.md` and [`references/TEMPLATE.md`](references/TEMPLATE.md). Choose the slot from Placement and the file name from the template. When `wiki/index.md` already lists a course on the topic, update that page. Done when profile, path, `sources[]`, and a heading outline giving every template block a destination or an omission reason are fixed.

3. **Draft** at the slot, following the template, the profile, and `obsidian-markdown`. Hold the **beginner bar**: every term, step, and formula is explained at first use for a reader with only foundational knowledge. Done when every template block is present or omitted with a reason, every source-dependent claim carries its `[^id]`, and a reread finds no step that skips the beginner bar.

4. **File: run `wiki-ingest` gate 8** with a `Query` log entry, updating the nearest index (and the root summary link when grouped). Done when the index reaches the course and every mutation invariant passes.

## Placement

A course is queryable knowledge, so a durable course lives in `wiki/`, where it is indexed, its `sources[].resource` links resolve, and its relationships traverse.

| Slot | When | Index |
|---|---|---|
| `wiki/<file>` | Default while `wiki/` is flat | `wiki/index.md` |
| `wiki/learn/<file>` | Once courses make flat scanning hard (around 15–20) | `wiki/learn/index.md`, linked from the root |
| `outputs/learn-<slug>-preview.md` | Explicit preview request, or verification fails | Not indexed or logged |

A new profile is `references/profiles/<name>.md` with Practice, Verification, Trade-offs, and Vocabulary sections, mapped to a domain in `SCOPE.md`.
