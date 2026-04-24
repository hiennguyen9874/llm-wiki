---
title: Lint Report 2026-04-24
created: 2026-04-24
last_updated: 2026-04-24
source_count: 0
status: reviewed
page_type: report
aliases:
  - 2026-04-24 maintenance report
  - 2026-04-24 lint report
tags:
  - maintenance
  - lint
  - review
  - retention
  - qmd
domain: general
importance: medium
review_status: active
confidence_score: 0.80
quality_score: 0.84
evidence_count: 0
first_seen: 2026-04-24
last_confirmed: 2026-04-24
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - text-to-image person retrieval
  - TBPS
  - maintenance
---

# Lint Report 2026-04-24

## Scope and method
Full maintenance lint over `wiki/`, including markdown pages, source pages, `wiki/bases/`, and `wiki/canvases/`.

Checked:
- duplicates and near-duplicates
- orphan pages and weak cross-links
- broken / unresolved wikilinks
- stale pages, low-confidence knowledge, low-quality pages
- source pages not integrated into topic pages
- supersession chains and contradiction markers
- visibility / privacy mismatches
- retention metadata and decay risk
- Bases / Canvases out of sync with markdown
- important pages that need lightweight `Evidence / claims` sections

Tools used:
- QMD status and lexical searches over `wiki` / `outputs` for stale, lifecycle, evidence, source-integration, duplicate-synthesis, benchmark, CARE/IQE, and dataset terms.
- Filesystem/link scans over 36 top-level wiki markdown pages, 17 source pages, 2 Bases, and 1 Canvas.
- Similarity scan for near-duplicate page families.

## Auto-fixes applied
- Added missing required core metadata (`domain`, `importance`, `review_status`, `related_sources`) to [[home]], [[index]], and [[log]].
- Refreshed [[home]] `last_updated` to `2026-04-24` and raised `quality_score` from `0.78` to `0.80` because the missing required metadata was repaired.

No page renames, deletions, merges, or taxonomy/schema changes were performed.

## Findings

### 🔴 Errors

- 🔴 **Unresolved wikilinks to concepts that do not yet have pages.** These were not auto-fixed because each target could mean either a new concept page or plain-text terminology.
  - [[text-to-image-person-retrieval-research-agenda]] links to missing dataset pages: `[[CUHK-PEDES]]`, `[[ICFG-PEDES]]`, `[[RSTPReid]]`.
  - [[source-arxiv-2601-18625-conquer]] links to missing sub-method pages: `[[care]]`, `[[iqe]]`.
  - [[source-github-flame-chasers-tbps-clip]] links to missing `[[clip]]`; this may need either a general CLIP concept page or conversion to plain text / `[[tbps-clip|CLIP]]` depending intended meaning.
- 🔴 **Three source pages point `source_file` at missing `.tar.gz` archives while extracted source directories exist.** Do not delete provenance; decide whether to update `source_file` to the LaTeX entrypoint or restore the archive artifact.
  - [[source-arxiv-2303-12501-irra]] → `raw/papers/arxiv-2303.12501-source.tar.gz` missing; `source_archive_dir` and `entrypoint` exist.
  - [[source-arxiv-2308-09911-rde]] → `raw/papers/arxiv-2308.09911-source.tar.gz` missing; extracted source directory exists.
  - [[source-arxiv-2507-10195-mra]] → `raw/papers/arxiv-2507.10195-source.tar.gz` missing; extracted source directory exists.

### 🟡 Warnings

- 🟡 **Most method/topic concept pages remain `status: draft` despite active review and recent confirmation.** This is conservative rather than broken, but may make the review Base noisy. Candidate pages for later promotion to `reviewed`: [[text-to-image-person-retrieval]], [[irra]], [[tbps-clip]], [[rde]], [[mars]], [[mra]], [[ga-dms]], [[conquer]], [[bi-irra]], [[mvr]], [[webperson]].
- 🟡 **Low-quality / just-below-threshold pages.** These are usable but would benefit from stronger structure, citations, or explicit evidence claims:
  - [[domain-aware-diffusion]] — `quality_score: 0.78`.
  - [[noisy-correspondence]] — `quality_score: 0.77`.
  - [[synthetic-domain-aligned-dataset]] — `quality_score: 0.79`.
- 🟡 **Important page lacking explicit lightweight `Evidence / claims` section.** [[text-to-image-person-retrieval-research-agenda]] is high-importance and synthesis-like; add claim blocks for priority gaps and rationale so future reviews can distinguish evidence-backed gaps from inference.
- 🟡 **Unresolved or implicit supersession chains are understandable but not fully queryable.** Several pages narrate benchmark leadership shifts across IRRA → RDE/MRA/GA-DMS → Bi-IRRA/MVR, but page-level `supersedes` / `superseded_by` fields do not capture all dataset-specific relationships. Keep the current dataset-dependent nuance; add claim-level supersession blocks rather than forcing one global winner.
- 🟡 **Canvas layer is stale relative to the markdown layer.** `wiki/canvases/home.canvas` is still a starter workflow map and does not reflect the now-dominant TBPS method/source cluster or the canonical [[synthesis-tbps-hybrid-design-space]].
- 🟡 **Review Base is narrow.** `wiki/bases/review.base` catches `draft`, `needs_update`, stale, and disputed pages, but does not directly surface `quality_score < 0.80`, low `confidence_score`, missing `Evidence / claims`, or broken-link review targets.
- 🟡 **Inbox Base may not surface non-markdown captures.** `wiki/bases/inbox.base` filters `raw/inbox` for `file.ext == "md"`, which is fine for markdown-first triage but will miss PDFs, images, archives, and code drops if they land in the inbox.
- 🟡 **High similarity pairs are mostly expected source↔topic pairs, but a few deserve consolidation policy.** QMD and similarity scans show the hybrid recommendation outputs, [[synthesis-tbps-hybrid-design-space]], and [[text-to-image-person-retrieval]] overlap heavily. Treat the synthesis page as canonical and keep outputs as provenance.
- 🟡 **Visibility is consistently private, but publishability is not assessed.** No private→shared mismatch found; if any TBPS synthesis is intended for external reuse, run a dedicated sanitization/pass before changing `visibility`.

### 🔵 Info

- 🔵 **No true orphan wiki pages found.** Every wiki markdown page has at least one inbound wikilink from another wiki page. [[home]] is the weakest normal page with one inbound link from [[index]], which is acceptable for a landing page.
- 🔵 **Source pages are broadly integrated.** All 17 source pages are linked from [[index]] and at least one topic/method page; source integration is strongest around [[text-to-image-person-retrieval]].
- 🔵 **QMD retrieval confirmed the main clusters.** Searches for lifecycle metadata, source integration, evidence/claims, hybrid synthesis, benchmark datasets, and CARE/IQE returned the expected TBPS cluster pages.
- 🔵 **No low-confidence pages found by frontmatter threshold.** All pages with `confidence_score` are at or above `0.77`; low-confidence issues are mainly claim-level ambiguity around benchmark generalization, not page-level confidence.
- 🔵 **No current `needs_update`, `stale`, or `disputed` page-level markers found.** The main unresolved tension is dataset-dependent benchmark leadership, which is intentionally preserved in prose.
- 🔵 **Retention check: no age-based decay needed.** The active TBPS cluster was created or confirmed on 2026-04-23/2026-04-24. Foundational system pages are now metadata-complete after auto-fix.
- 🔵 **Raw inbox is clear.** `raw/inbox/` has no pending files beyond `.gitkeep`.

## Duplicate / consolidation review

Not recommended for automatic merge:
- Method pages and source pages are intentionally similar because each source has a canonical method/topic page. Keep both layers.
- [[synthesis-tbps-hybrid-design-space]] overlaps with `outputs/answers/tbps-method-synthesis-and-hybrid-recommendation.md`, `outputs/answers/tbps-hybrid-architecture-spec.md`, and `outputs/analyses/text-to-image-person-retrieval-unexplored-connections.md`; this is expected promotion. The wiki synthesis should remain canonical.
- [[irra]] and [[bi-irra]] are semantically close but distinct; do not merge.

## Retention checks

- `transient`: none found in wiki frontmatter.
- `working`: none found in wiki frontmatter.
- `episodic`: report/output layer only; no wiki downgrade needed.
- `durable`: most TBPS topic/source pages are recent and still active.
- `foundational`: [[home]], [[index]], and [[log]] now have complete required metadata; no archival action.

Retention recommendations:
1. Add claim-level `last_confirmed` / `supersedes` blocks for benchmark-leadership claims rather than changing whole-page status.
2. Keep source pages durable, even when historical benchmark claims are superseded.
3. Keep outputs as episodic/provenance artifacts once promoted into wiki syntheses.

## Bases / Canvases sync check

- `wiki/bases/inbox.base`: operationally valid but markdown-only. Consider an additional non-md inbox view if raw captures diversify.
- `wiki/bases/review.base`: valid but incomplete for quality maintenance. Add filters/formulas later for low quality, low confidence, missing review metadata, and next-review dates.
- `wiki/canvases/home.canvas`: valid JSON Canvas but conceptually stale. It maps the generic second-brain workflow, not the active TBPS knowledge graph or recent synthesis layer.

## Important pages needing `Evidence / claims`

Highest priority:
1. [[text-to-image-person-retrieval-research-agenda]] — high-importance recommendations need claim-level evidence/rationale.
2. [[synthesis-tbps-hybrid-design-space]] — already separates supported facts and hypotheses, but would benefit from lightweight claim blocks for the modular hybrid recommendation.
3. [[text-to-image-person-retrieval]] — central topic page with many benchmark/generalization claims; add claim blocks for dataset-dependent benchmark leadership and robustness tradeoffs.

Secondary candidates:
- [[bi-irra]], [[mvr]], [[ga-dms]], [[mra]] for benchmark and supersession claims.

## Suggested fixes not auto-applied

1. Create dataset concept pages for `CUHK-PEDES`, `ICFG-PEDES`, and `RSTPReid`, or convert those links to plain text if the vault should not track datasets as pages.
2. Create concept pages for `CARE`, `IQE`, and possibly `CLIP`, or disambiguate links to existing method pages.
3. Resolve missing `.tar.gz` source references by either restoring archives or changing `source_file` to existing entrypoint files while keeping `source_archive_dir` for extracted source trees.
4. Update `wiki/bases/review.base` to include quality/confidence/claim-structure maintenance targets.
5. Create a TBPS method/source Canvas or update `home.canvas` to point at the active cluster and [[synthesis-tbps-hybrid-design-space]].

## 3 important gaps

1. **Dataset-level diagnostics gap:** the vault has benchmark numbers and leadership claims, but lacks a durable page explaining CUHK-PEDES vs ICFG-PEDES vs RSTPReid differences and why methods win on different datasets.
2. **Training-time denoising vs inference-time compensation gap:** RDE/GA-DMS and CONQUER/MVR are connected conceptually, but the vault lacks evidence from a controlled comparison that isolates when each route helps.
3. **Hybrid-validation gap:** [[synthesis-tbps-hybrid-design-space]] proposes a modular hybrid stack, but no source validates the complete combined architecture or gives ablation guidance for choosing modules under compute/data constraints.

## 3 next sources to ingest

1. A recent text-based person search / text-to-image person retrieval survey or benchmark-diagnostics paper that compares datasets, query ambiguity, language, and attribute density.
2. A paper or codebase combining training-time noisy-correspondence handling with inference-time query reformulation / multi-view compensation.
3. Dataset documentation or benchmark papers for CUHK-PEDES, ICFG-PEDES, and RSTPReid to support dedicated dataset pages and explain benchmark-regime differences.

## 3 pages or artifacts needing consolidation

1. `outputs/answers/tbps-method-synthesis-and-hybrid-recommendation.md`, `outputs/answers/tbps-hybrid-architecture-spec.md`, `outputs/analyses/text-to-image-person-retrieval-unexplored-connections.md`, and [[synthesis-tbps-hybrid-design-space]] — keep outputs as provenance, but maintain the wiki synthesis as canonical.
2. [[text-to-image-person-retrieval]], [[text-to-image-person-retrieval-research-agenda]], and [[synthesis-tbps-hybrid-design-space]] — clarify boundaries: topic overview vs research agenda vs design-space recommendation.
3. `wiki/canvases/home.canvas` and [[home]] / [[index]] — decide whether home remains a generic second-brain map or gains a current-domain navigation branch for the TBPS cluster.
