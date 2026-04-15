---
name: llm-wiki-maintenance
description: Review, lint, and improve the existing second brain without requiring a new source. Use for weekly/monthly reviews, wiki cleanups, contradiction checks, stale-page repair, and structural maintenance.
---

# LLM Wiki Maintenance

Use this skill for ongoing health and quality work.
Always activate `llm-wiki-core` first.

## Companion Skills
- `qmd` for finding duplicates, stale areas, and weakly connected pages
- `obsidian-markdown` for note repair and metadata updates
- `llm-wiki-visualization` when Bases or Canvases need refresh
- `ask-user` before irreversible or high-level structural changes

## Review Workflow
### Weekly review
- Process `raw/inbox/` and `raw/captures/`
- Review recent ingests and crystallizations
- Promote durable outputs into `wiki/`
- Review stale drafts and pages marked `needs_update`
- Refresh lifecycle metadata when evidence changed
- Run a light privacy/sensitivity scan over recently added downstream artifacts
- Check whether any new Canvas or Base should be created

### Monthly review
- Run the lint workflow
- Run the retention workflow
- Refresh major topic pages
- Check orphan pages and weakly linked areas
- Review stale or low-confidence knowledge
- Review low-quality pages and rewrite/repair the worst offenders
- Update at least one major synthesis page or Canvas
- Identify top knowledge gaps and next-source targets
- Record review activity in `wiki/log.md` as `review`

## Lint Workflow
Run monthly or on request.
Check for:
- contradictions between pages
- stale claims superseded by newer sources
- orphan pages with no inbound links
- concepts mentioned but never explained
- duplicate pages that should be merged
- missing cross-references
- claims without source attribution
- source pages not integrated into broader topic pages
- missing lifecycle metadata on important pages
- low-confidence or low-quality pages that need review
- unresolved supersession chains
- visibility mismatches or pages that should not be broadly scoped
- important pages that need lightweight `Evidence / claims` structure but lack it
- Bases or Canvases that no longer reflect the current wiki state

## Retention Workflow
Use retention class plus `last_confirmed` to decide what needs decay review.

### Suggested cadence
- `transient` → check quickly; can go stale within days or weeks
- `working` → check within weeks
- `episodic` → revisit during crystallization or monthly review
- `durable` → revisit during broader maintenance or when contradicted
- `foundational` → revisit slowly but keep well sourced

### Retention actions
When evidence has gone cold:
- lower `confidence_score` modestly when justified
- mark `claim_status` or page status as `stale` / `needs_update` when warranted
- preserve provenance instead of deleting content
- suggest consolidation or archival only with clear reasoning
- ask the user before destructive cleanup or major consolidation

## Contradiction Resolution Workflow
When resolving conflicting claims:
1. Identify the competing claims and cite the relevant pages.
2. Compare recency.
3. Compare authority/directness of the evidence.
4. Compare supporting-source count.
5. Compare specificity.
6. If one side is clearly stronger, mark the weaker claim/page as `superseded` or `stale`.
7. If evidence remains mixed, keep both visible and mark the issue `disputed`.
8. Briefly record the reasoning in the updated page or report.

## Quality Review Rules
Treat quality as operational, not decorative.

Pages usually need attention when they:
- lack source citations
- blur fact and inference
- have weak structure or missing frontmatter
- are poorly linked to related pages
- no longer match the current known state

Default behavior:
- safely improve structure, citations, and links when the fix is obvious
- mark weaker pages for review when the right rewrite is not obvious
- avoid silently inventing missing evidence

### Safe self-heal actions
Automatically repair only when safe:
- obvious broken internal links
- missing backlinks when unambiguous
- marking obviously stale pages as `needs_update`
- modest confidence/quality refreshes when the reason is explicit and provenance is preserved

For risky merges, taxonomy changes, or deletions, ask the user first.

### Lint output
- Save to `outputs/reports/lint-report-[date].md`
- Use severity levels:
  - 🔴 errors
  - 🟡 warnings
  - 🔵 info
- Also propose:
  - 3 important knowledge gaps
  - 3 possible next sources to ingest
  - 3 pages or artifacts needing consolidation

## Privacy Scan Workflow
When asked to scan for sensitive content:
- inspect recent or specified scope for secrets, credentials, tokens, PII, or private material
- verify that such material has not been copied into `wiki/` or broadly reusable outputs
- redact downstream summaries where safe and unambiguous
- ask the user before destructive cleanup or altering raw source storage policy
- record meaningful remediation in `wiki/log.md`

## Update Workflow
When asked to improve the wiki without a new source:
1. Use `wiki/index.md` for orientation if needed.
2. Use QMD to find weakly connected, stale, disputed, or duplicate areas.
3. Merge duplicates, add links, improve summaries, and strengthen citations.
4. Refresh lifecycle metadata, visibility, and supersession links where justified.
5. Update Bases/Canvases when they are out of sync with the markdown layer.
6. Record meaningful changes in `wiki/log.md` as `update`, including what changed and why.

## Automation Direction
Keep maintenance manual-first for now, but shape the workflows so they can later support:
- scheduled lint/review passes
- stale-knowledge scans
- contradiction/supersession checks on wiki writes
- promotion of durable outputs into canonical pages
- periodic privacy and retention passes
