---
name: wiki-lint
description: Lint and repair LLM wiki health. Use when the user requests maintenance, a health check, stale or unsupported claims, contradictions, broken links, orphan pages, source coverage, maturity, or index integrity.
---

# Wiki Lint

Audit the corpus against its contract, repair deterministic defects, and surface judgment calls.

## Steps

1. **Inventory and state.** From the repository root, read `LLM-WIKI.md`, independently enumerate reserved files, indexes, and concepts, and classify the wiki state under the contract. Run `python3 tools/wiki_check.py` when command execution is available, but directly inspect root-state requirements the checker may not enforce. Treat valid empty as healthy. Report an uninitialized bundle without creating a scaffold unless initialization was explicitly requested. Treat concepts with a missing, malformed, or incomplete index or log as damaged and retain the independent inventory for repair. This step is complete when every Markdown file is accounted for and the state, audit scope, structural findings, and visibility limits are explicit.

2. **Exhaustive audit.** Check every in-scope concept against every applicable contract rule: parseable required metadata; deliberate `draft`, `stable`, or `deprecated` maturity; staleness and verification; logical source identity, canonical entry point, revision, and package scope; resolvable local source resources/scopes; source-ID, body-citation, and footnote-definition joins; useful claim locators; reported, observed, reproduced, and synthesis distinctions where consequential; coverage ledgers and material attachment limits; unsupported claims; contradictions; typed relationship support; reciprocal supersession context; deprecated-page replacements; link targets; complete and unique index coverage; metadata/index agreement; concept cohesion; and privacy or disclosure leakage. Assess central missing concepts, consequential unanswered questions, single weak-source dependencies, and source coverage that is pending, unreadable, or stale. Suggest research questions or source needs without performing external research unless requested. This step is complete when every concept and root/index/log file has a recorded pass or finding for every applicable rule and durable knowledge gaps have been assessed.

3. **Disposition and repair.** Classify each finding as `error` (contract, privacy, or retrieval failure), `warning` (trust, maturity, coverage, or freshness risk), or `suggestion` (useful enrichment). Repair deterministic errors in place, including reconstructing complete indexes from the independent inventory without deleting concepts. Preserve disputed meaning, ambiguous source identity, and semantic status changes for human review. Report likely live secrets only by file and location category with values redacted, and pause affected mutation work. This step is complete when every finding is repaired or has an owner-facing disposition and no deterministic repair remains unattempted.

4. **Validate and report.** Write `outputs/wiki-lint-YYYY-MM-DD.md` with state, scope, visibility limits, counts, repairs, and unresolved findings. When the wiki changed, validate source/provenance joins, links, metadata/index agreement, complete index reachability, privacy, and all other mutation invariants; then add exactly one newest-first `Lint` entry to `wiki/log.md` and rerun the structural check. Repair or roll back this lint operation's incomplete edits if validation fails. This step is complete when the report accounts for every finding and changed state passes every contract check with one operation log entry.

## Audit thresholds

- A missing reserved file, invalid root `okf_version`, unindexed concept, duplicate index entry, broken local link, unresolved local source path/scope, or mismatched source/citation/footnote join is an error.
- A page is orphaned when neither an index nor useful concept context reaches it. A valid empty wiki has no orphan finding.
- A deprecated page without a current replacement is a warning unless retirement is explicitly terminal. A typed relationship without supporting context is a warning.
- A `stable` page with material coverage, provenance, interpretation, or attachment work outstanding is a maturity warning; missing independent verification alone means unverified, not false and not automatically a warning.
- A coarse locator is a warning when it makes a consequential claim impractical to audit. An unavailable locator is recorded as a limit rather than invented.
- A likely live secret is an error reported with its value redacted.
- New-concept recommendations require repeated or central mentions, not every noun. Knowledge gaps and source recommendations are suggestions unless they expose a concrete trust, coverage, or freshness risk.
