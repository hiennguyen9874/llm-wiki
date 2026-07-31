---
name: wiki-lint
description: Audit and repair LLM wiki health. Use when the user requests linting, maintenance, a health check, stale or unsupported claims, contradictions, broken links, orphan pages, or index integrity.
---

# Wiki Lint

Audit the corpus against its contract, then repair mechanical defects and surface judgment calls.

## Steps

1. From the repository root, read `LLM-WIKI.md` and run `python3 tools/wiki_check.py` when command execution is available. Then read all indexes and the independently enumerated concept inventory. When execution is unavailable, use the indexes and state that unindexed-file detection is incomplete. This step is complete when the audit scope, structural findings, and any visibility limits are explicit.
2. Check every in-scope concept for parseable required metadata, lifecycle and staleness, provenance/footnote joins, unsupported claims, unresolved contradictions, typed relationship support, reciprocal supersession context, deprecated-page replacements, link targets, index agreement, useful inbound context, and likely leakage of credentials, tokens, private keys, PII, or confidential content. Keep sensitive values out of reports. This step is complete when every concept has been checked against every applicable rule.
3. Classify findings as `error` (contract or retrieval failure), `warning` (trust or freshness risk), or `suggestion` (useful enrichment). Repair deterministic errors in place; preserve disputed meaning for user review. This step is complete when each finding is repaired or has an owner-facing disposition.
4. Write `outputs/wiki-lint-YYYY-MM-DD.md` with scope, visibility limits, counts, repairs, and unresolved findings. If the wiki changed, update affected indexes, rerun the structural check when available, and add exactly one newest-first `Lint` entry to `wiki/log.md`; apply every mutation invariant. This step is complete when the report accounts for every finding and all changed state is indexed, checked, and logged.

## Audit thresholds

A page is orphaned when no concept or index reaches it. A broken link is a retrieval defect even though OKF consumers tolerate it. A deprecated page without a current replacement is a warning unless retirement is explicitly terminal. A typed relationship without supporting context is a warning. A likely live secret is an error reported only by file and location category, with its value redacted. A missing verification event means unverified; it becomes a warning only when the page presents high-impact claims as settled. Recommendations for new concepts require repeated or central mentions, not every noun.
