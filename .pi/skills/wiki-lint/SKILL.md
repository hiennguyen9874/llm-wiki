---
name: wiki-lint
description: Lint and repair LLM wiki health. Use when the user asks to audit, lint, or repair the wiki, or a workflow finds it damaged.
---

# Wiki Lint

Audit the corpus against its contract, repair deterministic defects, and surface judgment calls.

## Steps

1. **Inventory and state.** From the repository root, read `SCOPE.md` (when present), enumerate reserved files, indexes, and concepts directly, and classify the wiki state. Run the structural check and its listed direct checks. Valid empty is healthy. Report an uninitialized wiki as-is, scaffolding only on explicit request. A damaged wiki keeps the direct inventory for repair. Done when every Markdown file is accounted for and the state, audit scope, structural findings, and visibility limits are explicit.

2. **Exhaustive audit.** Check every concept and every root, index, and log file against every rule in the contract's Concept, Index, and Log sections, every mutation invariant, and `SCOPE.md` exclusions and domain rules (including recurring domains left unregistered). Then assess durable gaps: central missing concepts, consequential unanswered questions, single weak-source dependencies, and pending, unreadable, or stale coverage. Suggest research questions or source needs; run external research only on request. Done when every file has a recorded pass or finding for every applicable rule and gaps are assessed.

3. **Disposition and repair.** Classify each finding by the thresholds below as `error` (contract, privacy, or retrieval failure), `warning` (trust, maturity, coverage, or freshness risk), or `suggestion` (useful enrichment). Repair deterministic errors in place, including rebuilding complete indexes from the direct inventory while keeping every concept. Leave disputed meaning, ambiguous source identity, and semantic status changes for human review. Report a likely live secret by file and location category only, and pause affected mutation work. Done when every finding is repaired or has an owner-facing disposition.

4. **Report and log.** Write `outputs/wiki-lint-YYYY-MM-DD.md` with state, scope, visibility limits, counts, repairs, and unresolved findings. When the wiki changed, confirm every mutation invariant, add one `Lint` log entry, and rerun the structural check; repair or roll back this operation's edits on failure. Done when the report accounts for every finding and any changed state passes every check.

## Audit thresholds

- **Error:** missing reserved file, invalid root `okf_version`, unindexed or duplicate-indexed concept, broken local link, unresolved source path or scope, broken citation join, or a likely live secret (value redacted).
- **Orphan:** a page that neither an index nor useful concept context reaches. A valid empty wiki has none.
- **Warning:** a deprecated page without a replacement (unless retirement is explicitly terminal); a typed relationship without supporting context; a `stable` page with coverage, provenance, interpretation, or attachment work outstanding; a locator too coarse to audit a consequential claim. Missing verification alone is unverified, not a warning.
- An unavailable locator is recorded as a limit.
- **Suggestion:** new concepts (only for repeated or central mentions), knowledge gaps, and source recommendations, unless they expose a concrete trust, coverage, or freshness risk.
