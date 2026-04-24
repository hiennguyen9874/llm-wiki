---
name: llm-wiki-query
description: Search, retrieval, answering, briefing, connections, disagreement analysis, gap analysis, and next-research workflows for the second brain. Use when the task is to understand or synthesize what the knowledge base already contains.
---

# LLM Wiki Query

Use skill for questions, analysis over existing knowledge base.
Always activate `llm-wiki-core` first.

## Companion Skills

* `qmd` for primary vault retrieval
* `obsidian-markdown` for markdown artifacts you create or update
* `llm-wiki-visualization` when Canvas or Base would materially help

## Search Policy

Use hybrid retrieval even if QMD remains primary tool.

### Orientation

* Read `purpose.md` and `wiki/overview.md` for broad, strategic, research-planning, gap, or session-orientation questions.
* Read `wiki/index.md` when broad content orientation helps.
* Do not force purpose/overview/index reading for every narrow lookup.

### Retrieval Strategy

1. Use QMD lexical search for exact names, terms, filenames, aliases.
2. Use QMD semantic or expanded search when vocabulary uncertain or question conceptual.
3. Use metadata-aware filtering mentally or via Bases when status, recency, retention class, page type, or visibility matters.
4. Expand outward from first results using typed relationships, `related_entities`, backlinks, supersession links, cited sources.
5. Treat relationship walk as current markdown-first graph traversal layer.
6. Read actual files before synthesizing.
7. Re-index/embed after large updates if search quality becomes stale.

## Query Workflow

When answering question:

1. Use `wiki/index.md` for orientation when helpful, not by reflex.
2. Use QMD to find relevant pages across `wiki/`, `outputs/`, optionally `raw/`.
3. Run both exact-term and concept-level retrieval when first search may miss synonyms or adjacent phrasing.
4. Expand from first results using entities, metadata, typed relationships, supersession chains, cited source pages, and markdown-first graph cues.
5. Read relevant pages before synthesizing.
6. Answer with citations to pages that informed answer.
7. Distinguish clearly between supported facts, inference, unresolved uncertainty.
8. Mention confidence, staleness, dispute, retention concerns, or supersession when they materially affect answer.
9. If raw sources needed to resolve ambiguity, read them directly.
10. If answer creates durable value, save in `outputs/answers/` or promote into `wiki/`.
11. Persist only when reusable, well cited, non-duplicative, likely to meet at least moderate quality bar.
12. If visual map or dashboard would help, create/update Canvas or Base.
13. Append `query` entry when saved artifact produced.

## Query Variants

### Brief

* Produce short, decision-oriented summary grounded only in knowledge base.
* Aim for roughly 150-250 words with one-sentence summary, key points, open questions or next steps.
* Cite supporting pages.
* Save only when explicitly requested or clearly reusable.

### Briefing

* Produce fuller reusable executive summary grounded only in knowledge base.
* Structure around current state, key tensions, open questions, recommended next steps when useful.
* Cite supporting pages for each section.
* Save to `outputs/briefings/` only if durable reuse value exists.

### Connections

* Map shared mechanisms, causal links, analogies, historical relationships, reinforcing patterns between concepts.
* Cite pages supporting each connection.
* If relationship durable and not already captured, create or update canonical page.

### Disagreements

* Identify conflicting claims across sources or canonical pages.
* Quote or paraphrase competing claims and cite each source page.
* Assess which side seems better supported using recency, authority/directness, supporting-source count, specificity.
* Preserve durable tensions in wiki pages when useful instead of flattening uncertainty.

### Gaps / Explore / Next Research

* Read `purpose.md` and `wiki/overview.md` unless scope is very narrow.
* Look for underdeveloped areas, implied but missing concepts, promising adjacent topics.
* Prioritize by impact on existing knowledge and purpose, not novelty alone.
* Recommend future sources, search topics, and next questions that would strengthen wiki.
* For manual-first Deep Research, propose editable search queries and ask user to approve URLs/sources before ingest.
* Save durable artifact only when scan itself will be useful later.

## Citation and Evidence Rules

* Every factual answer should cite wiki pages or raw sources that support it.
* Distinguish clearly between what supported, inferred, still uncertain.
* Mention if relevant page low-confidence, stale, disputed, or superseded.

## When to Persist Output

Persist result when it creates reusable value, such as:

* durable answer likely to be asked again
* cross-topic connection worth retaining
* contradiction map worth revisiting
* research agenda or gap analysis that should guide future work

Before persisting, prefer quick check:

* citations are present
* artifact adds something non-trivial beyond chat reply
* not obviously duplicating existing page
* likely clears rough `quality_score >= 0.75`
* visibility is set appropriately for audience
