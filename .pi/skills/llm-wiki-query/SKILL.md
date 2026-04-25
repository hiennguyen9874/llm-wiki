---
name: llm-wiki-query
description: Search, retrieval, answering, briefing, connections, disagreement analysis, gap analysis, and next-research workflows for the second brain. Use when the task is to understand or synthesize what the knowledge base already contains.
---

# LLM Wiki Query

Use for questions and analysis over the existing knowledge base.
Always activate `llm-wiki-core` first.

This file owns query procedure only.
- Use `llm-wiki-schema` when persisting structured outputs or updating canonical pages.
- Use `llm-wiki-governance` when handling disputed, superseded, stale, or sensitive material.
- Use `llm-wiki-ops` when saved artifacts require naming, index, log, or discoverability updates.

## Companion Skills
- `qmd` for primary vault retrieval
- `obsidian-markdown` for markdown artifacts you create or update
- `llm-wiki-visualization` when a Canvas or Base would materially help

## Search Policy
Use hybrid retrieval even if QMD remains the primary tool.

### Orientation
- Read `purpose.md` and `wiki/overview.md` for broad, strategic, research-planning, gap, or session-orientation questions.
- Read `wiki/index.md` when broad content orientation helps.
- Do not force purpose/overview/index reading for every narrow lookup.

### Retrieval Strategy
1. Use QMD lexical search for exact names, terms, filenames, and aliases.
2. Use QMD semantic or expanded search when vocabulary is uncertain or the question is conceptual.
3. Use metadata-aware filtering mentally or via Bases when status, recency, retention class, page type, or visibility matters.
4. Expand outward from first results using wikilinks, backlinks, typed relationships, `related_entities`, `related_sources`, claims, supersession links, and cited sources.
5. Budget context by priority: canonical wiki pages first, then relevant outputs, then raw sources needed to resolve ambiguity.
6. Read selected files before synthesizing; do not answer from snippets alone when facts matter.
7. Refresh the QMD search index after large updates if search quality becomes stale.
8. Do not claim vector DB, graph engine, or automatic reranking unless those tools are actually available in the session.

## Query Workflow
When answering a question:
1. Use `wiki/index.md` for orientation when helpful, not by reflex.
2. Use QMD to find relevant pages across `wiki/`, `outputs/`, and optionally `raw/`.
3. Run both exact-term and concept-level retrieval when first search may miss synonyms or adjacent phrasing.
4. Expand from first results using entities, metadata, typed relationships, supersession chains, cited source pages, and markdown-first graph cues.
5. Read relevant pages before synthesizing.
6. Answer with citations to pages that informed the answer.
7. Distinguish clearly between supported facts, inference, and unresolved uncertainty.
8. Mention confidence, staleness, dispute, retention concerns, or supersession when they materially affect the answer.
9. If raw sources are needed to resolve ambiguity, read them directly.
10. If the answer creates durable value, save it in `outputs/answers/` or promote it into `wiki/`.
11. Persist only when reusable, well cited, non-duplicative, and likely to meet at least a moderate quality bar.
12. If the answer reveals material worth canonical synthesis, suggest or run `/compile` over the affected outputs/pages.
13. If a visual map or dashboard would help, create or update a Canvas or Base.
14. Append a `query` entry when a saved artifact is produced.

## Query Variants

### Brief
- Produce a short, decision-oriented summary grounded only in the knowledge base.
- Aim for roughly 150-250 words with one-sentence summary, key points, and open questions or next steps.
- Cite supporting pages.
- Save only when explicitly requested or clearly reusable.

### Briefing
- Produce a fuller reusable executive summary grounded only in the knowledge base.
- Structure around current state, key tensions, open questions, and recommended next steps when useful.
- Cite supporting pages for each section.
- Save to `outputs/briefings/` only if durable reuse value exists.

### Connections
- Map shared mechanisms, causal links, analogies, historical relationships, and reinforcing patterns between concepts.
- Cite pages supporting each connection.
- If a relationship is durable and not already captured, create or update a canonical page.

### Disagreements
- Identify conflicting claims across sources or canonical pages.
- Quote or paraphrase competing claims and cite each source page.
- Assess which side seems better supported using recency, authority/directness, supporting-source count, and specificity.
- Preserve durable tensions in wiki pages when useful instead of flattening uncertainty.

### Gaps / Explore / Next Research
- Read `purpose.md` and `wiki/overview.md` unless scope is very narrow.
- Look for underdeveloped areas, implied but missing concepts, and promising adjacent topics.
- Prioritize by impact on existing knowledge and purpose, not novelty alone.
- Recommend future sources, search topics, and next questions that would strengthen the wiki.
- For manual-first deep research, propose editable search queries and ask user to approve URLs/sources before ingest.
- Save durable artifacts only when the scan itself will be useful later.

## Citation and Evidence Rules
- Every factual answer should cite wiki pages or raw sources that support it.
- Distinguish clearly between what is supported, inferred, and still uncertain.
- Mention if a relevant page is low-confidence, stale, disputed, or superseded.

## When to Persist Output
Persist when the result creates reusable value, such as:
- a durable answer likely to be asked again
- a cross-topic connection worth retaining
- a contradiction map worth revisiting
- a research agenda or gap analysis that should guide future work

Before persisting, prefer a quick check:
- citations are present
- artifact adds something non-trivial beyond the chat reply
- it does not obviously duplicate an existing page
- it likely clears rough `quality_score >= 0.75`
- visibility is set appropriately for the intended audience
