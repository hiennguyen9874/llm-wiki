---
title: Monthly Review and Lint Report - 2026-04-26
created: 2026-04-26
last_updated: 2026-04-26
status: reviewed
page_type: review_item
aliases:
  - Monthly Review 2026-04-26
  - Lint Report 2026-04-26
tags:
  - review
  - lint
  - graph-insights-lite
  - maintenance
retention_class: episodic
visibility: private
related_pages:
  - [[overview]]
  - [[index]]
  - [[log]]
  - [[tradingview-mcp]]
  - [[prediction-market-trading]]
  - [[moondev]]
  - [[regime-trading-bot]]
  - [[openclaw-for-tradingview]]
---

# Monthly Review and Lint Report - 2026-04-26

## Scope
Monthly review of the current second-brain vault after the first populated trading / prediction-market ingest cluster.

Checked:
- `purpose.md`, `wiki/overview.md`, `wiki/index.md`, `wiki/log.md`
- all current `wiki/*.md` pages
- `outputs/review-queue/`
- `raw/inbox/` and `raw/captures/`
- Bases / Canvas inventory
- QMD status and retrieval availability

## Executive summary
The vault is small but coherent. The main semantic cluster is now trading automation, with four canonical non-source pages: [[tradingview-mcp]], [[moondev]], [[regime-trading-bot]], and [[prediction-market-trading]], plus the [[openclaw-for-tradingview]] project page.

No destructive cleanup or merge is warranted. The biggest maintenance need is not repair; it is preserving uncertainty around promotional trading-performance claims and deciding when to split broader synthesis pages.

## Monthly workflow results

### Inbox and captures
- `raw/inbox/` contains only `.gitkeep`.
- `raw/captures/` contains only `.gitkeep`.
- No unprocessed inbox/capture items found.

### Recent ingests and crystallizations
- Recent ingests are concentrated on 2026-04-26 trading and prediction-market sources.
- No new crystallization files were present for this review window.
- The source-to-topic promotion pattern is consistent: every raw article currently has a corresponding wiki source page, and major repeated patterns have topic/project pages.

### Review queue checks
Found 9 active review items in `outputs/review-queue/`.

Open items by theme:
- Scope / taxonomy decisions:
  - `2026-04-26-tradingview-mcp-page-scope.md`
  - `2026-04-26-openclaw-for-tradingview-page-scope.md`
  - `2026-04-26-prediction-market-trading-cluster-scope.md`
  - `2026-04-26-polymarket-pnl-tracker-scope-review.md`
  - `2026-04-26-tradingview-master-prompt-framing-review.md`
- Robustness / overfit decisions:
  - `2026-04-26-rbi-0dte-topic-scope-review.md`
  - `2026-04-26-gpt-55-backtest-robustness-review.md`
  - `2026-04-26-polymarket-5min-bot-robustness-review.md`
  - `2026-04-26-tradingview-scalping-backtest-robustness-review.md`

Maintenance action taken:
- Normalized draft review items to `status: open` where they represented active human-review decisions.

Recommended next queue handling:
1. Resolve scope items first; they are low-risk and will clarify future page structure.
2. Keep robustness items open until independent evidence, reproducible tests, or stronger backtest methodology is available.
3. Do not promote extreme performance numbers into durable conclusions without out-of-sample evidence.

### Privacy / visibility scan
- All reviewed wiki and output artifacts are marked or treated as `private`.
- A keyword scan for common secret indicators found no credentials or tokens in downstream wiki pages.
- No privacy remediation was needed.

## Lint findings

### 🔴 Errors
None found.

### 🟡 Warnings
1. **Uncreated concept links in [[tradingview-mcp]].**
   - Missing target pages: `TradingView Desktop`, `Chrome DevTools Protocol`, `Pine Script`.
   - These may be intentional future concept links. If they stay important, create lightweight concept pages; otherwise convert to plain text during a later cleanup.

2. **Several source pages have quality scores below 0.80.**
   - Examples: the Ethereum scalping source, master-prompt TradingView demo, Polymarket consensus source, GPT-5.5 backtest source, and OpenClaw project page.
   - This is acceptable for early source pages, but the lower scores correctly signal promotional claims, source-local evidence, and limited independent verification.

3. **Trading-performance claims remain highly source-local.**
   - Extreme backtest / P&L claims appear in source pages and review items, but should not be upgraded to durable trading knowledge without corroboration.

4. **QMD index is available and was refreshed after the review.**
   - `qmd status` confirmed the local index is available.
   - `qmd embed` completed successfully and reported all current content hashes already had embeddings.

### 🔵 Info
1. Required wiki frontmatter fields are present across current wiki pages.
2. No orphan wiki pages were found when counting links from index/overview/source/topic pages.
3. The catalog in [[index]] matches the current populated wiki pages.
4. `wiki/bases/inbox.base`, `wiki/bases/review.base`, and `wiki/canvases/home.canvas` exist; no urgent visualization repair was needed.

## Retention and freshness review
- Most semantic pages have `last_confirmed: 2026-04-26`, so no age-based staleness downgrade is needed.
- The main retention risk is evidential, not temporal: many claims are based on promotional demos or single-source transcripts.
- Keep `claim_status: active` for workflow/tooling claims that are directly sourced.
- Keep performance claims bounded in source-local claim blocks and review items until stronger evidence arrives.

## Graph-insights-lite

### Isolated pages
- No true isolated wiki pages found.
- [[regime-trading-bot]] is structurally sparse: it has one direct source and limited outward links. It is still discoverable via [[index]] and [[prediction-market-trading]], but would benefit from future links to a broader trading-automation synthesis if that page is created.

### Sparse clusters
- **TradingView-Claude cluster:** dense and currently centered on [[tradingview-mcp]].
- **MoonDev / backtesting cluster:** emerging around [[moondev]], [[openclaw-for-tradingview]], and source-local backtest demos.
- **Prediction-market cluster:** coherent around [[prediction-market-trading]], but robustness evidence is weak and review items should stay open.

### Bridge pages
- [[tradingview-mcp]] bridges LLM tool use, TradingView, Pine Script, and strategy/backtest demos.
- [[moondev]] bridges liquidation-data backtests, OpenClaw-style indicator mining, and Polymarket tick-data experimentation.
- [[prediction-market-trading]] bridges market scanning, multi-model consensus, short-interval backtesting, and P&L analysis.

### Surprising / useful cross-topic links
- The prediction-market and TradingView clusters share an underlying pattern: agent-assisted strategy ideation plus weak backtest claims that require robustness gates.
- [[moondev]] may become the bridge between market-data tooling and automated trading research rather than remaining a narrow source-derived page.

### Canvas / Base recommendation
- No new Canvas is necessary yet.
- If the trading cluster grows by another 3-5 sources, create a `wiki/canvases/trading-automation.canvas` map showing: sources → tooling pages → strategy/backtest claims → review items.

## Major pages to refresh later
1. [[overview]] — keep updated as the trading cluster branches into synthesis pages.
2. [[tradingview-mcp]] — consider splitting setup/tooling claims from trading-strategy demos if more sources arrive.
3. [[prediction-market-trading]] — revisit once robustness or P&L-tracking evidence accumulates.

## Top knowledge gaps
1. Current purpose is still broad; the human’s top projects and highest-leverage research questions are not explicit.
2. Trading automation pages lack independent verification or reproducible robustness checks for performance claims.
3. No broad `trading-automation` synthesis page exists yet to connect TradingView, MoonDev, regime bots, and prediction-market agents.

## Possible next sources to ingest
1. Primary documentation or repository for `tradingview-mcp` / `tv` CLI, if available.
2. Reproducible backtesting methodology source covering out-of-sample tests, walk-forward validation, fees, slippage, and multiple-hypothesis bias.
3. Polymarket API / data documentation for tick data, open-market valuation, fee modeling, and historical exports.

## Consolidation candidates
1. A future `trading-automation` synthesis page could connect [[tradingview-mcp]], [[regime-trading-bot]], [[moondev]], [[openclaw-for-tradingview]], and [[prediction-market-trading]]. Do not create it until one more pass confirms it would reduce fragmentation.
2. `TradingView Desktop`, `Chrome DevTools Protocol`, and `Pine Script` could become lightweight concept pages if they recur.
3. Performance-robustness review items could eventually consolidate into a single `trading-backtest-robustness` topic if repeated evidence accumulates.

## Actions completed in this review
- Ran monthly lint, retention, review-queue, privacy, and graph-insights-lite checks.
- Normalized active review queue items from `draft` to `open` where appropriate.
- Refreshed/validated QMD embeddings with `qmd embed`.
- Saved this durable report.
- Updated [[overview]], [[index]], and [[log]] to reflect the review.
