---
title: Source - Polymarket 5 Min Claude Code Bot are NUTS
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - Polymarket 5-minute Claude Code bot transcript
  - CVD Polymarket bot demo
  - Polymarket short-interval backtest transcript
tags:
  - source
  - trading
  - polymarket
  - prediction-markets
  - backtesting
  - tick-data
  - cvd
  - automation
domain: trading
importance: medium
review_status: active
related_sources: []
confidence_score: 0.66
quality_score: 0.79
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
  - Claude Code
  - CVD
  - tick data
  - 1-minute data
  - 5-minute markets
  - MACD
  - MoonDev
  - Mundev
source_file: raw/articles/polymarket-5-min-claude-code-bot-are-nuts.md
source_type: transcript
author: unknown
canonical_url: 
---

# Source - Polymarket 5 Min Claude Code Bot are NUTS

## What this source is
A YouTube transcript in which the speaker describes building and testing Polymarket trading bots for 5-minute markets using Claude Code, then pivots to a tick-data / CVD approach for a new bot.

## Why it matters
This source adds a second Polymarket branch to the vault:
- the earlier source focused on multi-model consensus scanning
- this one focuses on short-interval backtesting, tick-level order flow, and bot automation

It is useful as a pattern for how people try to extract faster signal from prediction markets using more granular data than ordinary OHLC bars.

## Key claims
#### Claim
- Statement: The speaker says Polymarket 5-minute markets can be backtested with 1-minute data by treating the start-of-window price as the price to beat.
- Status: active
- Confidence: 0.74
- Evidence: [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- Last confirmed: 2026-04-26
- Notes: This is the core backtesting idea in the transcript.

#### Claim
- Statement: The speaker says tick data is where the important edge lives and uses it to build a CVD-based bot.
- Status: active
- Confidence: 0.72
- Evidence: [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- Last confirmed: 2026-04-26
- Notes: The transcript frames tick data as higher resolution than standard OHLC data.

#### Claim
- Statement: The source reports that a MACD 3/15/3 idea wins about 60% of trades and takes 287 of 288 trades per day.
- Status: active
- Confidence: 0.58
- Evidence: [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- Last confirmed: 2026-04-26
- Notes: Treat this as source-local and likely overfit until independently verified.

#### Claim
- Statement: The speaker says MoonDev / Mundev provides data, docs, and API access used to obtain the 1-minute and tick data for the workflow.
- Status: active
- Confidence: 0.69
- Evidence: [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- Last confirmed: 2026-04-26
- Notes: This reinforces MoonDev as recurring trading-infrastructure context.

#### Claim
- Statement: The speaker explicitly warns that the backtest results may be overfit even while presenting them as promising.
- Status: active
- Confidence: 0.77
- Evidence: [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- Last confirmed: 2026-04-26
- Notes: This warning should stay attached to any reuse of the results.

## Entities and relationships
- `Polymarket` is the prediction-market venue being traded.
- `Claude Code` is used to build or automate the bot.
- `1-minute data` is used to estimate the price-to-beat in each 5-minute window.
- `tick data` feeds the CVD calculation and reveals intrabar order-flow pressure.
- `MoonDev` / `Mundev` is referenced as the data / docs / API layer.
- `MACD` is one of the reported strategy ideas from the backtest set.

## Notes
> [!warning]
> The transcript is promotional and demo-like. The win-rate and trade-frequency claims should be treated as source-local until reinforced by independent evidence.

> [!info]
> The durable takeaway is the workflow pattern: narrow prediction-market interval + higher-resolution data + explicit backtest framing + caution about overfit.

## Open questions
- Does tick-level CVD actually improve prediction-market trading results in practice?
- What is the exact data-access path for the 1-minute and tick data?
- Are the reported results robust out of sample, or mostly a backtest artifact?
- Should CVD become its own topic page later if more sources reinforce it?

## Related pages
- [[prediction-market-trading]]
- [[moondev]]
- [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]

## Sources
- Original raw source: `raw/articles/polymarket-5-min-claude-code-bot-are-nuts.md`
