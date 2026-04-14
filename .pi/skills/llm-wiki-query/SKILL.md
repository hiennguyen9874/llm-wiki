---
name: llm-wiki-query
description: Search, retrieval, answering, briefing, connections, disagreement analysis, gap analysis, and next-research workflows for the second brain. Use when the task is to understand or synthesize what the knowledge base already contains.
---

# LLM Wiki Query

Use this skill for questions and analysis over the existing knowledge base.
Always activate `llm-wiki-core` first.

## Companion Skills
- `qmd` for primary vault retrieval
- `obsidian-markdown` for any markdown artifacts you create or update
- `llm-wiki-visualization` when a Canvas or Base would materially help

## Search Policy
Use hybrid retrieval behavior even if QMD remains the primary tool.

### Orientation
- Read `wiki/index.md` when broad orientation is helpful.
- Do not force index-first reading for every narrow lookup.

### Retrieval Strategy
1. Use QMD lexical search for exact names and terms.
2. Use QMD semantic or expanded search when vocabulary is uncertain.
3. Use metadata-aware filtering mentally or via Bases when status, recency, or page type matters.
4. Expand outward from key entities and relationships mentioned in the first results.
5. Read the actual files before synthesizing.
6. Re-index/embed after large updates if search quality becomes stale.

## Query Workflow
When answering a question:
1. Use `wiki/index.md` for orientation when helpful, not by reflex.
2. Use QMD to find relevant pages across `wiki/`, `outputs/`, and optionally `raw/`.
3. Expand from the first results using entities, metadata, and typed relationships.
4. Read the relevant pages before synthesizing.
5. Answer with citations to the pages that informed the answer.
6. Mention confidence, staleness, dispute, or supersession when it materially affects the answer.
7. If raw sources are needed to resolve ambiguity, read them directly.
8. If the answer creates durable value, save it in `outputs/answers/` or promote it into `wiki/`.
9. If a visual map or dashboard would help, create/update a Canvas or Base.
10. Append a `query` entry when a saved artifact is produced.

## Query Variants
### Briefing
- Produce a concise executive summary grounded only in the knowledge base.
- Structure around current state, key tensions, open questions, and recommended next steps when useful.
- Cite the supporting pages for each section.
- Save to `outputs/briefings/` only if it has durable reuse value.

### Connections
- Map shared mechanisms, causal links, analogies, historical relationships, and reinforcing patterns between concepts.
- Cite the pages supporting each connection.
- If the relationship is durable and not already captured, create or update a canonical page.

### Disagreements
- Identify conflicting claims across sources or canonical pages.
- Quote or paraphrase the competing claims and cite each source page.
- Assess which side seems better supported without erasing unresolved uncertainty.
- Preserve durable tensions in wiki pages when useful.

### Gaps / Explore / Next Research
- Look for underdeveloped areas, implied but missing concepts, and promising adjacent topics.
- Prioritize based on impact on existing knowledge, not novelty alone.
- Recommend future sources or next questions that would strengthen the wiki.
- Save a durable artifact only when the scan itself will be useful later.

## Citation and Evidence Rules
- Every factual answer should cite the wiki pages or raw sources that support it.
- Distinguish clearly between what is supported, what is inferred, and what is still uncertain.
- Mention if a relevant page is low-confidence, stale, disputed, or superseded.

## When to Persist Output
Persist the result when it creates reusable value, such as:
- a durable answer likely to be asked again
- a cross-topic connection worth retaining
- a contradiction map worth revisiting
- a research agenda or gap analysis that should guide future work
