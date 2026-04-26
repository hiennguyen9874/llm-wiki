---
title: Ingest Plan - I Gave Claude AI Full Access to TradingView The Scalping Strategy It Built Was Insane
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
source_count: 1
status: draft
retention_class: episodic
visibility: private
source_file: raw/articles/i-gave-claude-ai-full-access-to-tradingview-the-scalping-strategy-it-built-was-insane.md
source_type: transcript
related_sources: []
---

# Ingest Plan - I Gave Claude AI Full Access to TradingView The Scalping Strategy It Built Was Insane

## Source identity
- Source: YouTube transcript on Claude Code given full TradingView access to build and optimize an Ethereum scalping strategy.
- Why it matters to `purpose.md`: it captures another durable example of AI-assisted trading-strategy design, especially signal stacking, timeframe selection, and backtest interpretation. That is useful as reusable knowledge about the limits and shape of agent-assisted market-research workflows.

## Key entities
- Claude Code
- TradingView / TradingView account access
- Ethereum
- BlackCat indicators
  - L3 3in1 CCI Trader
  - God Hunter scalping
  - L1 C DJX Super Short Line
- ADX
- ATR bands
- Pine Script
- strategy backtesting and optimization

## Candidate claims
- Claude Code can be used with unrestricted TradingView access to build, backtest, and iterate on a multi-indicator scalping strategy.
- The workflow stacks BlackCat indicators plus ADX and ATR bands to form entry and risk rules.
- The transcript reports that 5m and 15m charts were noisy / weak, while 30m was the better fit for the setup.
- The source reports unusually strong backtest results on Ethereum, including a 4,242% return, ~18% max drawdown, 471 closed trades, ~63-64% win rate, and ~1.97 profit factor.
- The narrator frames the workflow as a route to autonomous strategy generation and live trading deployment.

## Related existing pages
- [[tradingview-mcp]] — the core bridge/topic page for Claude ↔ TradingView workflows.
- [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]] — nearby demo source in the same cluster, useful for comparing framing and capability claims.
- [[source-how-to-use-claude-to-build-tradingview-indicators]] — earlier indicator-building source that shows the same bridge in a smaller incremental workflow.
- [[source-claude-code-tradingview-live-trading-bot-0dte]] — broader live-trading research branch, if the strategy source later gets compiled into a larger automation narrative.

## Proposed page updates
### New source page
- Create a dedicated source page in `wiki/` for the transcript with source metadata, a compact claim inventory, and a clear caution about promotional backtest claims.

### Likely canonical updates
- Update `tradingview-mcp` to mention this source as evidence that the bridge can support multi-indicator strategy construction and timeframe optimization, not just indicator editing.
- Update `wiki/overview.md` to keep the TradingView-Claude cluster current and reflect the new source count.
- Update `wiki/index.md` so the new source is discoverable.

## New / reinforced / uncertain
- New: explicit use of a stacked indicator set for scalping strategy design on Ethereum.
- Reinforced: the bridge can support iterative Pine Script / strategy work, including backtesting and optimization.
- Uncertain: the reported performance numbers are not independently verified and may reflect overfit or promotional framing; keep them source-local and low-assurance.

## Traceability
- Add `related_sources` on any updated canonical pages, especially `tradingview-mcp`.
- Preserve the raw transcript path in the new source page metadata.

## Integration strategy
- Treat this as a single-source ingest for now.
- A later `/compile` pass only becomes worthwhile if more strategy/backtest sources accumulate and the wiki needs a broader trading-edge synthesis.

## Review items
- Add a review note for backtest robustness / overfit follow-up. Recommendation: keep the performance claims visible in the source page, but do not elevate them into canonical “edge” knowledge without independent corroboration.
- No taxonomy change seems needed.

## Downstream artifacts
- Save the source page.
- Add one review-queue item for robustness follow-up.
- Update `wiki/log.md` and `wiki/index.md`.
- No Base or Canvas warranted yet.
