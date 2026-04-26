---
title: Review - Polymarket 5-minute bot robustness and overfit risk
created: 2026-04-26
last_updated: 2026-04-26
status: open
page_type: review_item
action_type: deep_research
priority: medium
source:
  - [[source-polymarket-5-min-claude-code-bot-are-nuts]]
related_pages:
  - [[prediction-market-trading]]
  - [[moondev]]
  - [[overview]]
visibility: private
---

# Review - Polymarket 5-minute bot robustness and overfit risk

## Decision needed
Should the 60% win-rate / 287-of-288-trades idea and the surrounding CVD / tick-data workflow be treated as durable trading knowledge, or kept explicitly source-local until robustness checks pass?

## Context
The source describes:
- backtesting Polymarket 5-minute markets using 1-minute data
- a CVD-based approach built from tick data
- MoonDev / Mundev as the data/docs/API source
- a reported MACD 3/15/3 result with very high trade frequency
- an explicit overfit warning from the speaker

## Recommendation
Keep the result low-confidence and source-local for now.
Treat the main durable takeaway as the workflow pattern, not the headline performance number.

## Options
1. Promote the result into a broader prediction-market topic now.
2. Keep it source-local and add robustness testing as follow-up research.
3. Create a dedicated CVD / order-flow topic only after more sources reinforce it.

## Status
Open for later human review.
