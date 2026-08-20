---
name: qmd-retrieval
description: Rank LLM Wiki candidate concepts with project-local QMD. Use when wiki-query needs lexical ranking or semantic fallback beyond the catalog, glob, and exact text search.
compatibility: Optional qmd CLI; retrieval must fall back to the repository tools when unavailable.
---

# QMD Retrieval

Use QMD as a candidate-ranking cache, never as knowledge authority. Catalog entries, exact matches, and QMD results form a union; a low QMD score cannot discard an explicit candidate.

## Steps

1. From the repository root, confirm `.qmd/index.yml` exists and `qmd status` succeeds. If QMD is absent, unhealthy, or cannot read the project index, return to catalog, glob, and exact text search without failing the parent query. This step is complete when the retrieval path is explicit.
2. When QMD is available, run incremental `qmd update` before searching so the local cache reflects synchronized files. If update fails, report that the cache is unavailable and use the deterministic fallback. This step is complete when the index is current or excluded from this query.
3. Select the cheapest adequate mode:
   - Use `qmd search` by default for titles, aliases, tags, identifiers, quoted phrases, and relationship vocabulary.
   - Use `qmd query` only after an observed lexical miss, or immediately for a clearly semantic, vocabulary-mismatched, ambiguous, or cross-concept question.
   - Add `--intent` when disambiguation matters.
   This step is complete when the mode follows a stated retrieval need rather than a fixed preference.
4. Scope every command with `-c wiki`, request structured output with `--json`, and start with a bounded result set such as `-n 10`. Do not impose one shared `--min-score`: BM25 and hybrid scores are not interchangeable. This step is complete when ranked result paths and snippets are available.
5. Union and deduplicate QMD paths with candidates from `wiki/index.md`, glob, and exact search. Read the selected files with repository tools and let `wiki-query` traverse relationships and evaluate lifecycle, provenance, verification, freshness, and contradictions. This step is complete when every retained candidate has been inspected or explicitly rejected with a reason.

## Command Patterns

```bash
qmd search -c wiki --json -n 10 '"retrieval policy" stale_after'
qmd query -c wiki --json -n 10 --intent "Trust and freshness controls" \
  "How does the system avoid presenting stale or disputed knowledge as fact?"
```

QMD snippets are discovery evidence only. Material answer claims must come from inspected wiki concepts or raw sources allowed by `LLM-WIKI.md`.
