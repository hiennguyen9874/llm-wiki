---
name: llm-wiki-maintenance
description: Review, lint, and improve the existing second brain without requiring a new source. Use for weekly/monthly reviews, wiki cleanups, contradiction checks, stale-page repair, and structural maintenance.
---
# LLM Wiki Maintenance

Use skill for ongoing health, quality work.
Always activate `llm-wiki-core` first.

## Companion Skills

* `qmd` for finding duplicates, stale areas, weakly connected pages
* `obsidian-markdown` for note repair, metadata updates
* `llm-wiki-visualization` when Bases or Canvases need refresh
* `ask-user` before irreversible or high-level structural changes
* `llm-wiki-ingest` when maintenance turns into compile/promotion from raw or outputs

## Review Workflow

### Weekly review

* Process `raw/inbox/` and `raw/captures/`
* Review recent ingests, crystallizations
* Promote durable outputs into `wiki/`
* Review stale drafts and pages marked `needs_update`
* Refresh lifecycle metadata when evidence changed
* Run light privacy/sensitivity scan over recently added downstream artifacts
* Check whether new Canvas or Base should be created
* Review open items in `outputs/review-queue/`
* Refresh `wiki/overview.md` when recent changes affect the global state

### Monthly review

* Run lint workflow
* Run retention workflow
* Refresh major topic pages
* Check orphan pages and weakly linked areas
* Review stale or low-confidence knowledge
* Review low-quality pages and rewrite/repair worst offenders
* Update at least one major synthesis page or Canvas
* Identify top knowledge gaps and next-source targets
* Run graph-insights-lite: isolated pages, sparse clusters, bridge pages, surprising cross-topic links
* Record review activity in `wiki/log.md` as `review`


## Librarian-Style Freshness and Quality Review
Use this during monthly review, lint, or explicit freshness/quality audits. Keep repo metadata on the existing 0-1 scale. Reports may show equivalent percentages for readability.

Check:
- source traceability through `related_sources` and source pages
- `last_confirmed`, `retention_class`, `claim_status`, confidence, and quality
- whether source support is missing, stale, contradicted, or low quality
- page depth, coherence, utility, citations, and link structure

Output:
- save durable reports to `outputs/reports/`
- include worst stale pages, worst low-quality pages, likely fixes, and review items
- do not automatically refresh factual claims without evidence

## Lint Workflow

Run monthly or on request.
Check for:

* contradictions between pages
* stale claims superseded by newer sources
* orphan pages with no inbound links
* concepts mentioned but never explained
* duplicate pages that should be merged
* missing cross-references
* claims without source attribution
* source pages not integrated into broader topic pages
* missing lifecycle metadata on important pages
* low-confidence or low-quality pages needing review
* unresolved supersession chains
* visibility mismatches or pages that should not be broadly scoped
* important pages needing lightweight `Evidence / claims` structure but lacking it
* Bases or Canvases no longer reflecting current wiki state
* stale or unresolved review queue items
* `wiki/overview.md` no longer matching current wiki state


## Lint-as-Migration Rules
Use lint as the normal place to repair safe schema drift. Auto-fix only mechanical, low-risk defects: missing obvious frontmatter defaults, stale index rows, clear broken links, unambiguous backlinks, and explicitly documented legacy aliases.

Do not auto-fix decisions requiring judgment: taxonomy changes, bulk renames/moves/deletes, page merges, source deletion, privacy cleanup that removes provenance, or new metadata schema. Ask user or create review queue items.

## Retention Workflow

Use retention class plus `last_confirmed` to decide decay review.

### Suggested cadence

* `transient` → check quickly; stale within days or weeks
* `working` → check within weeks
* `episodic` → revisit during crystallization or monthly review
* `durable` → revisit during broader maintenance or when contradicted
* `foundational` → revisit slowly but keep well sourced

### Retention actions

When evidence gone cold:

* lower `confidence_score` modestly when justified
* mark `claim_status` or page status as `stale` / `needs_update` when warranted
* preserve provenance instead of deleting content
* suggest consolidation or archival only with clear reasoning
* ask user before destructive cleanup or major consolidation

## Contradiction Resolution Workflow

When resolving conflicting claims:

1. Identify competing claims and cite relevant pages.
2. Compare recency.
3. Compare authority/directness of evidence.
4. Compare supporting-source count.
5. Compare specificity.
6. If one side clearly stronger, mark weaker claim/page as `superseded` or `stale`.
7. If evidence remains mixed, keep both visible and mark issue `disputed`.
8. Briefly record reasoning in updated page or report.

## Quality Review Rules

Treat quality as operational, not decorative.

Pages usually need attention when they:

* lack source citations
* blur fact and inference
* have weak structure or missing frontmatter
* are poorly linked to related pages
* no longer match current known state

Default behavior:

* safely improve structure, citations, links when fix obvious
* mark weaker pages for review when right rewrite not obvious
* avoid silently inventing missing evidence

### Safe self-heal actions

Automatically repair only when safe:

* obvious broken internal links
* missing backlinks when unambiguous
* marking obviously stale pages as `needs_update`
* modest confidence/quality refreshes when reason explicit and provenance preserved

For risky merges, taxonomy changes, or deletions, ask user first.

### Lint output

* Save to `outputs/reports/lint-report-[date].md`
* Use severity levels:

  * 🔴 errors
  * 🟡 warnings
  * 🔵 info
* Also propose:

  * 3 important knowledge gaps
  * 3 possible next sources to ingest
  * 3 pages or artifacts needing consolidation

## Privacy Scan Workflow

When asked to scan for sensitive content:

* inspect recent or specified scope for secrets, credentials, tokens, PII, or private material
* verify such material has not been copied into `wiki/` or broadly reusable outputs
* redact downstream summaries when safe and unambiguous
* ask user before destructive cleanup or altering raw source storage policy
* record meaningful remediation in `wiki/log.md`

## Graph-Insights-Lite Workflow

Use during monthly review, lint, gaps, or when the wiki feels fragmented. This is markdown-first and does not imply a real graph database exists.

Look for:

* isolated pages with few links or no obvious inbound/outbound context
* sparse clusters where related pages lack cross-links or synthesis
* bridge pages that connect several topics and may deserve a synthesis page or Canvas
* surprising cross-topic links worth preserving as connections
* purpose-relevant gaps that deserve manual-first Deep Research

Actions:

* add obvious links/backlinks when supported
* create review items for uncertain links or page creation decisions
* recommend or create Canvas/Base artifacts when they clarify structure
* save durable gap/connection findings to `outputs/reports/` or `outputs/analyses/` when useful

## Compile / Promotion Maintenance
When several raw sources, saved answers, analyses, or crystallizations should become canonical wiki knowledge, run the `/compile` prompt or follow the compile workflow from `llm-wiki-core`. Prefer incremental compile unless the user asks for a full rewrite.

## Update Workflow

When asked to improve wiki without new source:

1. Use `purpose.md`, `wiki/overview.md`, and `wiki/index.md` for orientation if needed.
2. Use QMD to find weakly connected, stale, disputed, or duplicate areas.
3. Merge duplicates, add links, improve summaries, strengthen citations.
4. Refresh lifecycle metadata, visibility, supersession links where justified.
5. Update Bases/Canvases when out of sync with markdown layer.
6. Record meaningful changes in `wiki/log.md` as `update`, including what changed and why.

## Automation Direction

Keep maintenance manual-first for now, but shape workflows so later support:

* scheduled lint/review passes
* stale-knowledge scans
* contradiction/supersession checks on wiki writes
* promotion of durable outputs into canonical pages
* periodic privacy and retention passes
