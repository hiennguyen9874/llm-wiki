---
title: Source - How to Use Claude to Build TradingView Indicators
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - How to Use Claude to Build TradingView Indicators
  - TradingView indicator guide
  - ZCT Momentum Filter article
  - OI momentum indicator article
tags:
  - source
  - tradingview
  - claude
  - mcp
  - pine-script
  - open-interest
  - technical-analysis
domain: trading
importance: medium
review_status: active
related_sources: []
confidence_score: 0.74
quality_score: 0.80
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - tradingview-mcp
  - TradingView Desktop
  - Claude Code
  - Pine Script
  - open interest
  - exponential moving average
  - ZCT Momentum Filter
source_file: raw/articles/How-to-Use-Claude-to-Build-TradingView-Indicators.md
source_type: article
author: Koroush AK
---

# Source - How to Use Claude to Build TradingView Indicators

## What this source is
An X article by Koroush AK that walks through an incremental workflow for using Claude Code to build and save a TradingView Pine Script indicator inside TradingView Desktop.

## Why it matters
This source expands the existing TradingView-Claude cluster beyond connection/setup into actual indicator authoring and trading interpretation:
- prompt-by-prompt Pine Script editing
- open-interest based plotting and smoothing
- user-adjustable indicator settings
- save-to-account persistence after session-only injection
- heuristic interpretation of indicator behavior for breakouts, breakdowns, and reversals

## Key claims
#### Claim
- Statement: Claude Code can be used in an incremental, one-prompt-one-change loop to build a TradingView indicator through `tradingview-mcp` and TradingView Desktop.
- Status: active
- Confidence: 0.76
- Evidence: [[source-how-to-use-claude-to-build-tradingview-indicators]]
- Last confirmed: 2026-04-26
- Notes: The article emphasizes small, visible steps so each change can be verified before moving on.

#### Claim
- Statement: The example indicator plots dollar-denominated open interest using the `_OI` suffix, adds 60-period and 240-period EMAs, shades the space between them, and exposes the EMA lengths as settings.
- Status: active
- Confidence: 0.74
- Evidence: [[source-how-to-use-claude-to-build-tradingview-indicators]]
- Last confirmed: 2026-04-26
- Notes: This is the article’s core build recipe, presented as a beginner-friendly workflow.

#### Claim
- Statement: The article recommends saving the injected Pine Script in Pine Editor because Claude’s injection is session-only.
- Status: active
- Confidence: 0.80
- Evidence: [[source-how-to-use-claude-to-build-tradingview-indicators]]
- Last confirmed: 2026-04-26
- Notes: The persistence step is framed as required if the user wants the script to live in their TradingView account.

#### Claim
- Statement: The article interprets OI/EMA behavior as breakout, breakdown, and reversal regimes for trading decisions.
- Status: active
- Confidence: 0.70
- Evidence: [[source-how-to-use-claude-to-build-tradingview-indicators]]
- Last confirmed: 2026-04-26
- Notes: Treat as the author’s trading heuristic, not a validated predictive rule.

## Entities and relationships
- `tradingview-mcp` supports Claude Code ↔ TradingView Desktop integration.
- `Claude Code` uses prompt-driven indicator authoring workflows.
- `TradingView Desktop` hosts the Pine Editor and indicator save flow.
- `Pine Script` indicator logic uses open interest and EMA overlays.
- `open interest` is used as a momentum input in the article’s example.
- `ZCT Momentum Filter` is the named example indicator.

## Notes
> [!warning]
> The article says OI data may not exist on every symbol. If the chart returns “no data,” it suggests switching to `BINANCE:BTCUSDT.P`.

> [!info]
> The build process is deliberately incremental: one prompt, one change, one visible verification step. The article argues this makes the script easier to understand and debug.

## Open questions
- How generally useful is the OI/EMA heuristic across different markets and timeframes?
- How much of the indicator-building workflow depends on TradingView Desktop specifics versus the broader MCP bridge?
- Should this remain only a source page, or later be compiled into a broader Pine Script workflow synthesis if more sources arrive?

## Related pages
- [[tradingview-mcp]]
- [[source-how-to-connect-claude-to-tradingview]]
- [[source-how-to-connect-claude-to-tradingview-2]]

## Sources
- Original raw source: `raw/articles/How-to-Use-Claude-to-Build-TradingView-Indicators.md`
