---
title: Prediction Market Trading
created: 2026-04-26
last_updated: 2026-04-26
source_count: 2
status: draft
page_type: topic
aliases:
  - Polymarket trading
  - Polymarket AI trading
  - Prediction market AI agents
  - Prediction market consensus trading
tags:
  - trading
  - prediction-markets
  - polymarket
  - ai-agents
  - consensus
  - automation
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
  - [[source-polymarket-5-min-claude-code-bot-are-nuts]]
confidence_score: 0.68
quality_score: 0.81
evidence_count: 2
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Polymarket
  - prediction markets
  - AI swarm
  - OpenRouter
  - model consensus
  - market filters
  - whale trades
  - websocket
  - 1-minute data
  - tick data
  - CVD
---

# Prediction Market Trading

## Summary
Prediction market trading is the use of systematic or AI-assisted workflows to scan markets such as Polymarket, filter for higher-signal opportunities, and decide whether to enter `yes`, `no`, or no-trade positions.

The current vault now has two strong source examples:
- one on multi-model consensus scanning and market filtering
- one on short-interval backtesting, tick-data / CVD experimentation, and bot automation

## Key points
- The pattern is closer to **signal ranking and market selection** than to classic indicator trading.
- Multiple models can be used as a loose ensemble or debate layer.
- Noise reduction matters: trade-size filters, category exclusions, and refresh logic are all part of the workflow.
- Some prediction-market workflows move from consensus scanning into higher-resolution backtesting with 1-minute and tick data.
- The source claims around CVD and MACD should be treated as source-local until independently validated.
- The cluster is related to broader AI trading automation, but the venue and signal type are still distinct.

## Relationships
- `Polymarket` provides the market venue.
- `AI swarm` / model ensembles can generate per-market recommendations.
- `OpenRouter` can serve as a model access layer.
- `Consensus` is used to combine multiple model opinions into one action.
- `Market filters` reduce low-quality or emotionally noisy opportunities.
- `1-minute data` and `tick data` can support short-interval backtesting and order-flow style experiments.
- `MoonDev` / `Mundev` appears as a recurring data/tooling source in the bot workflow.

## Evidence / claims
#### Claim
- Statement: A prediction-market workflow can ask multiple models in parallel for `yes`, `no`, or `no trade` recommendations and aggregate them into one consensus action.
- Status: active
- Confidence: 0.74
- Evidence: [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
- Last confirmed: 2026-04-26
- Notes: This is the central reusable idea from the source.

#### Claim
- Statement: The transcript’s workflow filters for larger trades and suppresses certain markets to cut noise.
- Status: active
- Confidence: 0.69
- Evidence: [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
- Last confirmed: 2026-04-26
- Notes: The exact thresholds are source-local and should be validated before reuse.

#### Claim
- Statement: A second Polymarket workflow can backtest 5-minute markets using 1-minute data and then derive a CVD-style signal from tick data.
- Status: active
- Confidence: 0.72
- Evidence: [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- Last confirmed: 2026-04-26
- Notes: This expands the cluster from consensus scanning into higher-resolution bot research.

#### Claim
- Statement: The short-interval transcript reports a 60% win-rate idea and very high trade frequency, but warns that the result may be overfit.
- Status: active
- Confidence: 0.60
- Evidence: [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- Last confirmed: 2026-04-26
- Notes: Keep this explicitly low-confidence until validated out of sample.

#### Claim
- Statement: The source frames the workflow as a repeatable scanner that can run continuously and update as new trades appear.
- Status: active
- Confidence: 0.67
- Evidence: [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
- Last confirmed: 2026-04-26
- Notes: Useful operationally, but not yet proven as a durable edge.

## Open questions
- Does consensus across several models outperform a single model or a simple heuristic on prediction markets?
- What market categories, trade-size filters, and refresh cadences are actually useful?
- Does tick-level CVD improve prediction-market trading results in practice?
- Should CVD remain embedded in this page or become its own canonical concept page later?
- Should the best use of LLMs in prediction markets be signal generation, triage, or explanation?
- Should this remain a distinct topic or merge later into a broader trading-automation synthesis?

## Related pages
- [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
- [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- [[regime-trading-bot]]
- [[tradingview-mcp]]
- [[moondev]]

## Sources
- [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
- [[source-polymarket-5-min-claude-code-bot-are-nuts]]
