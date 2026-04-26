---
title: Review - Polymarket P&L tracker scope and concept split
created: 2026-04-26
last_updated: 2026-04-26
status: open
page_type: review_item
action_type: skip
priority: medium
source:
  - [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
related_pages:
  - [[prediction-market-trading]]
  - [[overview]]
visibility: private
---

# Review - Polymarket P&L tracker scope and concept split

## Decision needed
Should the keyword-filtered Polymarket P&L tracker become its own canonical concept page, or remain folded into `prediction-market-trading`?

## Context
The source describes:
- a Python P&L tracker for Polymarket exports
- keyword and lookback filtering over the trade history
- bid / ask midpoint handling for open markets
- fee-aware break-even analysis

## Recommendation
Keep it folded into `prediction-market-trading` for now.
Treat the tracker as a useful sub-workflow, not yet a separate durable concept.

## Options
1. Split out a dedicated P&L analysis / trade-review topic now.
2. Keep it embedded under prediction-market trading and revisit if more sources reinforce the pattern.
3. Fold it into a broader trading-analytics topic later if the vault develops that branch.

## Status
Open for later human review.
