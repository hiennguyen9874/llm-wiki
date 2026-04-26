---
title: Regime Trading Bot
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: topic
aliases:
  - Regime-based trading bot
  - HMM trading bot
  - Automated regime trader
tags:
  - trading
  - automation
  - bot
  - regime
  - hmm
  - risk-management
  - alpaca
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
confidence_score: 0.74
quality_score: 0.83
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Claude Code
  - Hidden Markov Model
  - HMM
  - regime detection
  - allocation strategies
  - circuit breakers
  - risk manager
  - Alpaca
  - IBKR
  - Streamlit
  - paper trading
---

# Regime Trading Bot

## Summary
A regime trading bot is an automated trading system that classifies the current market regime, adjusts portfolio exposure and strategy by regime, and lets a separate risk layer veto trades or shut the system down when conditions deteriorate. The source page for this topic describes a Claude Code-built example that uses HMMs, regime-based allocation, circuit breakers, Alpaca execution, and a monitoring dashboard.

## Key points
- The bot is organized as a layered system, not a single strategy script.
- Regime detection is treated as the decision anchor.
- Allocation changes with volatility / regime instead of staying fixed.
- Risk controls are independent of the strategy model and can hard-stop the bot.
- Brokerage execution and monitoring are separate layers.
- Paper trading is the recommended starting point before live funds.

## Relationships
- `Claude Code` can scaffold and connect the layers of the system.
- `Hidden Markov Models` provide the regime classifier.
- `Regime` states influence allocation, leverage, and strategy selection.
- `Risk manager` overrides strategy output when drawdown or other limits are hit.
- `Alpaca` is used as the execution broker in the source.
- `Streamlit` / dashboard provides visibility into signals, regime state, and risk status.

## Evidence / claims
#### Claim
- Statement: The architecture has five layers: brain, allocation, safety, brokerage, dashboard.
- Status: active
- Confidence: 0.82
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: Useful as a reusable mental model for the system.

#### Claim
- Statement: HMM-based regime detection is used to classify market state rather than forecast price.
- Status: active
- Confidence: 0.80
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: The source presents this as the core bot logic.

#### Claim
- Statement: The system should reduce exposure in more turbulent markets and increase exposure in calmer regimes.
- Status: active
- Confidence: 0.76
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: The exact allocation schedule is source-local and should be customized.

#### Claim
- Statement: Risk rules should have veto power over the strategy model and can stop the bot on drawdown breaches.
- Status: active
- Confidence: 0.81
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: This is the most durable design principle in the source.

#### Claim
- Statement: Paper trading is the safe default before any live deployment.
- Status: active
- Confidence: 0.84
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: Treat this as a strong operational recommendation.

## Open questions
- Does the HMM regime taxonomy remain useful across symbols, horizons, and market conditions?
- What backtest / walk-forward discipline is enough to trust the strategy stack?
- Is Alpaca the right long-term broker, or is IBKR a better default once scale and operational constraints increase?
- Should this evolve into a broader trading-automation synthesis if more sources arrive?

## Related pages
- [[source-how-to-actually-build-a-trading-bot-with-claude-code]]

## Sources
- [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
