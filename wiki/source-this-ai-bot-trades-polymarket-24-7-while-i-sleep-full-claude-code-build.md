---
title: Source - This AI Bot Trades Polymarket 24/7 While I Sleep (Full Claude Code Build)
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - Polymarket P&L tracker demo
  - Keyword-filtered Polymarket tracker
  - Full Claude Code Polymarket build
tags:
  - source
  - trading
  - polymarket
  - p-and-l
  - analysis
  - automation
  - claude-code
domain: trading
importance: medium
review_status: active
related_sources: []
confidence_score: 0.67
quality_score: 0.78
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Polymarket
  - Python
  - P&L tracker
  - CSV export
  - keyword filter
  - lookback window
  - bid / ask midpoint
  - realized P&L
  - fees
  - Claude Code
source_file: 'raw/articles/this-ai-bot-trades-polymarket-24%2f7-while-i-sleep-(full-claude-code-build).md'
source_type: transcript
author: unknown
canonical_url: 
---

# Source - This AI Bot Trades Polymarket 24/7 While I Sleep (Full Claude Code Build)

## What this source is
A YouTube transcript / article-style capture in which the speaker demonstrates a Python P&L tracker for Polymarket trades. The tool filters exported trade history by keyword and lookback window so the speaker can compare profitability across market terms and horizons.

## Why it matters
This source adds a post-trade analysis layer to the Polymarket branch in the vault:
- not just live scanning or signal generation
- not just short-interval backtesting
- but retrospective P&L slicing by keyword, category, and time window

That makes the cluster more reusable because it shows how the speaker evaluates what kinds of markets or phrases perform best.

## Key claims
#### Claim
- Statement: The speaker built a Python P&L tracker that can inspect Polymarket profitability by keyword and hours back.
- Status: active
- Confidence: 0.79
- Evidence: [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
- Last confirmed: 2026-04-26
- Notes: This is the core workflow pattern shown in the transcript.

#### Claim
- Statement: The tracker supports keyword filters such as `Bitcoin`, `market cap`, and exact phrases like `exactly`.
- Status: active
- Confidence: 0.76
- Evidence: [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
- Last confirmed: 2026-04-26
- Notes: Treat the specific examples as source-local filter names.

#### Claim
- Statement: For open markets, the workflow estimates value using bid price or the bid/ask midpoint.
- Status: active
- Confidence: 0.70
- Evidence: [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
- Last confirmed: 2026-04-26
- Notes: This is a practical valuation detail that may change depending on data availability.

#### Claim
- Statement: The speaker says the bot is roughly break-even after a day and that fees materially affect profitability.
- Status: active
- Confidence: 0.69
- Evidence: [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
- Last confirmed: 2026-04-26
- Notes: Keep this low-confidence and source-local; the transcript is demo-like and promotional.

#### Claim
- Statement: The speaker uses the tracker to infer which market categories or keywords perform better or worse.
- Status: active
- Confidence: 0.68
- Evidence: [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
- Last confirmed: 2026-04-26
- Notes: The transcript frames the tool as a learning aid for market selection.

## Entities and relationships
- `Polymarket` is the market venue being analyzed.
- `Python` is used to implement the P&L tracker.
- `CSV export` / portfolio download provides the trade history.
- `keyword filter` narrows the analysis to subsets of trades.
- `lookback window` allows the speaker to compare horizons like 72 hours or 30 days.
- `bid / ask midpoint` is used when a market is still open.
- `fees` are treated as a major drag on profitability.
- `Claude Code` is the build tool used to produce the workflow.

## Notes
> [!warning]
> The transcript is promotional and demo-like. Treat the break-even framing, category advice, and fee comparisons as source-local until reinforced by independent evidence.

> [!info]
> The durable takeaway is the workflow pattern: export trades, filter by keyword and horizon, and use the resulting P&L slices to decide which market types deserve more attention.

## Open questions
- Does keyword-filtered P&L analysis actually improve trading decisions over time?
- Which filters matter most: keyword, category, time horizon, or open-market valuation method?
- Should this eventually become a standalone trading-analytics concept page if more sources arrive?

## Related pages
- [[prediction-market-trading]]
- [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
- [[source-polymarket-5-min-claude-code-bot-are-nuts]]

## Sources
- Original raw source: `raw/articles/this-ai-bot-trades-polymarket-24%2f7-while-i-sleep-(full-claude-code-build).md`
