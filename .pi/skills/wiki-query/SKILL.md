---
name: wiki-query
description: Answer questions from the LLM wiki. Use when the user asks a question, comparison, or report grounded in the knowledge base.
---

# Wiki Query

Retrieve progressively: state first, map second, concepts third, raw evidence only on the triggers in step 4.

## Steps

1. **State and vocabulary.** From the repository root, read `SCOPE.md` (when present) and classify the wiki state. For an uninitialized or valid empty wiki, report that no knowledge is compiled yet and stop. For a damaged wiki, enumerate concept files directly, disclose the integrity limit, and route repair to `wiki-lint`. Otherwise translate the question into concepts, aliases, relationships, constraints, and, when completeness is asked, source coverage. Done when the state, candidate vocabulary, and known retrieval limits are explicit.

2. **Candidate union.** Read `wiki/index.md` and applicable group indexes, selecting by title, description, type, tags, and relationships. Glob for structural scope; exact-search titles, aliases, identifiers, metadata, source identities, and relationship labels. Include `SourceMap` pages for coverage questions. When exact retrieval is too broad or misses the user's vocabulary, follow `qmd-retrieval`. QMD only adds candidates: its absence, staleness, or low scores leave catalog and exact matches in place. Done when paths from every applicable channel are deduplicated and remaining gaps are explicit.

3. **Read and traverse.** Read candidates and follow relationship types that fit the question: `Depends on`/`Uses` for impact, `Caused`/`Fixed by` for diagnosis, `Supersedes`/`Contradicts` for freshness, `Owned by` for responsibility. For large pages, read metadata, synthesis, headings, coverage limits, contradictions, and relationships first, then the relevant sections; prefer linked cohesive concepts over treating a source-shaped overview as exhaustive. Done when every relevant relationship frontier and recorded coverage limit has been checked.

4. **Evaluate trust.** For each consequential claim, check `status`, `stale_after`, `verified`, evidence class, contradictions, the citation join, and the locator. Missing verification means unverified; broken or coarse provenance is a retrieval limit. Open `raw/` only for a disputed citation, a broken or too-coarse provenance edge, inconsistent wiki summaries, or explicit source-level research (exact implementation, equation, benchmark, wording), and cite the file plus locator; every other answer comes from the wiki. Done when every material claim is supported, labeled synthesis, or marked uncertain, with each provenance limit visible.

5. **Answer** directly with Markdown links to concepts, separating documented knowledge, synthesis, related-but-insufficient evidence, no compiled knowledge, and limits from the wiki state. Absence means "not compiled or not retrieved", never "false". State whether raw research ran. Done when the requested scope is answered and every material claim shows its basis.

6. **Crystallize.** File the result as `type: Synthesis` through `wiki-ingest` when it is durable: reusable multi-concept synthesis, a comparison, a decision or lesson, a newly supported relationship, a contradiction resolution, or a verified procedure. Cite the underlying concepts or raw sources (chat is not provenance) and fold extracted insights into affected concepts. Save requested transient deliverables under `outputs/`; a read-only answer leaves wiki and log unchanged. Done when each durable insight is filed or explicitly left transient.
