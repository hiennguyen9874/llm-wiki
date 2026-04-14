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
- Check whether any new Canvas or Base should be created

### Monthly review
- Run the lint workflow
- Refresh major topic pages
- Check orphan pages and weakly linked areas
- Review stale or low-confidence knowledge
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
- Bases or Canvases that no longer reflect the current wiki state

### Safe self-heal actions
Automatically repair only when safe:
- obvious broken internal links
- missing backlinks when unambiguous
- marking obviously stale pages as `needs_update`

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

## Update Workflow
When asked to improve the wiki without a new source:
1. Use `wiki/index.md` for orientation if needed.
2. Use QMD to find weakly connected, stale, disputed, or duplicate areas.
3. Merge duplicates, add links, improve summaries, and strengthen citations.
4. Refresh lifecycle metadata and supersession links where justified.
5. Update Bases/Canvases when they are out of sync with the markdown layer.
6. Record meaningful changes in `wiki/log.md` as `update`.

## Automation Direction
Design maintenance work so it can eventually support:
- scheduled lint/review passes
- stale-knowledge scans
- contradiction/supersession checks on wiki writes
- promotion of durable outputs into canonical pages
