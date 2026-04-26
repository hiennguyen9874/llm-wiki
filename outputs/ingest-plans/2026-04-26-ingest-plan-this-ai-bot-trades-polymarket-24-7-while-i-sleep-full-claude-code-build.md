---
title: Ingest Plan - This AI Bot Trades Polymarket 24/7 While I Sleep (Full Claude Code Build)
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
  - [[prediction-market-trading]]
---

# Ingest Plan - This AI Bot Trades Polymarket 24/7 While I Sleep (Full Claude Code Build)

## Source identity
- Source file: `raw/articles/this-ai-bot-trades-polymarket-24%2f7-while-i-sleep-(full-claude-code-build).md`
- Source type: transcript / YouTube-style demo
- Likely topic domain: prediction-market trading, post-trade P&L analysis, keyword-filtered trade review, bot performance inspection
- Why it matters to `purpose.md`: it extends the Polymarket branch beyond consensus scanning and short-interval backtesting into post-trade analysis tooling that helps compare profitability by market keyword and lookback window.

## Key entities and relationships
- Polymarket → market venue whose trades are being exported and analyzed
- Python P&L tracker → script that filters trades by keyword and lookback window
- CSV / portfolio export → input data for the tracker
- keyword filter → selects trades or markets for focused analysis
- lookback window → last 72 hours / last 30 days style horizon used to slice results
- bid / ask midpoint or bid price → valuation logic for open markets
- realized P&L → performance metric the speaker inspects
- fees → important drag on profitability
- Claude Code → the build tool used for the analysis workflow

## Candidate claims
- The speaker built a Python P&L tracker that can inspect Polymarket profitability by keyword and hours back.
- The tracker supports keyword filters such as `Bitcoin`, `market cap`, and exact phrases like `exactly`.
- For markets that are still open, the workflow estimates value using bid price or the bid/ask midpoint.
- The speaker says the bot is roughly break-even after a day and emphasizes that fees materially affect profitability.
- The speaker uses the tool to identify which market categories or keywords perform better or worse.

## Existing pages likely affected
- `[[prediction-market-trading]]` — should add a post-trade analysis / P&L tracker branch alongside consensus scanning and short-interval backtesting.
- `[[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]` — sibling source in the same prediction-market cluster.
- `[[source-polymarket-5-min-claude-code-bot-are-nuts]]` — sibling source that already covers short-interval backtesting.
- `[[wiki/overview]]` — should mention the new Polymarket post-trade analysis branch.
- `[[wiki/index]]` — add the new source page for discoverability.

## New vs reinforced vs uncertain
### New
- A post-trade P&L inspection workflow for Polymarket CSV exports.
- Keyword- and time-window-based slicing as an analysis tool for deciding which market types to trade.
- Bid / ask midpoint handling for open markets inside a P&L review process.

### Reinforced
- The Polymarket cluster is now more than a single demo: it includes scanning, backtesting, and analysis tooling.
- Fees and market selection matter when judging profitability.
- Source-local demo workflows often expose more useful process patterns than headline returns.

### Uncertain
- The profitability and break-even framing are promotional and likely source-local until validated.
- It is unclear whether the tracker should become its own durable concept page or remain embedded in `prediction-market-trading`.
- The exact valuation logic for open markets may need follow-up if we want to reuse it precisely.

## Proposed page actions
### Source page
Create a dedicated source page in `wiki/` with:
- source metadata
- concise summary of the tracker and P&L workflow
- claim blocks for keyword filtering, open-market valuation, and fee-aware break-even framing
- open questions around robustness and whether the tracker should become a standalone concept later
- related pages linking to `prediction-market-trading` and the earlier Polymarket sources

### Canonical page updates
Update `prediction-market-trading` to add:
- a third branch: post-trade analysis / P&L tracker / keyword-based market comparison
- explicit separation between live scanning, short-interval backtesting, and retrospective P&L inspection
- a new evidence block grounded in this source

## Traceability updates
- Add `related_sources` on `[[prediction-market-trading]]` to include the new source.
- Add `related_sources` on the new source page to point back to the Polymarket topic pages and sibling sources as appropriate.
- Preserve the raw source unchanged.

## Review items
1. Should the keyword-filtered P&L tracker become its own canonical concept page?
   - Recommendation: not yet; keep it folded into `prediction-market-trading` unless more sources reinforce the pattern.
2. Should the fee / break-even claims be treated as durable knowledge?
   - Recommendation: no; keep them source-local and low-confidence.

## Integration scope
- Single-source ingest is sufficient.
- No `/compile` pass is required yet unless more Polymarket analysis tools arrive.
- No Canvas/Base is needed right now.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because it documents a non-trivial expansion of the Polymarket cluster.
- Create a review-queue item for the page-scope / concept-split question.
- Update `wiki/log.md` after integration.
- Update `wiki/index.md` for the new source page.
- Refresh `wiki/overview.md` to reflect the broader Polymarket analysis branch.
