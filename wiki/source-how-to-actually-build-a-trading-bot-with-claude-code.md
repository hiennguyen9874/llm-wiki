---
title: Source - How to Actually Build a Trading Bot With Claude Code
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - Fully Automated Trading Bot With Claude Code
  - Regime Trader tutorial
  - Claude Code trading bot transcript
  - HMM Alpaca bot source
tags:
  - source
  - trading
  - claude
  - claude-code
  - bot
  - automation
  - hmm
  - alpaca
  - risk-management
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-simple-4-step-ai-trading-assistant-with-claude]]
confidence_score: 0.74
quality_score: 0.81
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Claude Code
  - Hidden Markov Model
  - HMM
  - Alpaca
  - IBKR
  - Streamlit
  - risk management
  - circuit breakers
  - paper trading
  - regime detection
  - walk-forward backtesting
source_file: raw/articles/how-to-actually-build-a-trading-bot-with-claude-code-fully-automated.md
source_type: transcript
author: unknown
canonical_url: 
---

# Source - How to Actually Build a Trading Bot With Claude Code

## What this source is
A YouTube transcript / article-style capture that walks through building a fully automated trading bot with Claude Code. The architecture centers on regime detection with HMMs, regime-based allocation, safety circuit breakers, broker execution via Alpaca, and a monitoring dashboard.

## Why it matters
This source adds a distinct trading-automation branch to the vault. It is not just about indicators or chart tooling; it describes a reusable system architecture for:
- market regime classification
- allocation by volatility / regime
- hard risk vetoes and shutdown rules
- brokerage integration
- backtesting and paper-trading discipline
- operational monitoring in a dashboard

## Key claims
#### Claim
- Statement: The bot architecture is organized into five parts: brain, allocation, safety, brokerage, and dashboard.
- Status: active
- Confidence: 0.82
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: This is the source’s high-level framing and is stable enough to reuse as the page structure.

#### Claim
- Statement: Hidden Markov Models are used as the bot’s “brain” to classify market regime rather than to predict price direction.
- Status: active
- Confidence: 0.80
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: The regime labels are example outputs from the transcript, not a validated universal taxonomy.

#### Claim
- Statement: The source recommends avoiding look-ahead bias by using forward-style inference instead of naïve full-sequence prediction.
- Status: active
- Confidence: 0.78
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: This is an implementation caution with direct practical value.

#### Claim
- Statement: Allocation should change by regime, with lower exposure in more turbulent markets and higher exposure in calmer markets.
- Status: active
- Confidence: 0.76
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: The exact thresholds are source-local examples and should not be generalized without testing.

#### Claim
- Statement: Risk management should be independent of the strategy model and can hard-stop the bot on drawdown, leverage, or correlation violations.
- Status: active
- Confidence: 0.81
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: The source treats this as the most important layer of the system.

#### Claim
- Statement: Alpaca is presented as the initial brokerage choice, with IBKR mentioned as a possible later-scale alternative.
- Status: active
- Confidence: 0.74
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: This is a practical recommendation from the tutorial, not an independent brokerage comparison.

#### Claim
- Statement: The source recommends paper trading for at least a month before live deployment.
- Status: active
- Confidence: 0.84
- Evidence: [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- Last confirmed: 2026-04-26
- Notes: This is the strongest operational guidance in the transcript.

## Entities and relationships
- `Claude Code` builds the project scaffolding and orchestrates the code-generation loop.
- `Hidden Markov Model` / `HMM` supports regime detection.
- `Regime` labels drive `allocation` decisions.
- `Risk manager` has veto power over strategy outputs.
- `Alpaca` receives paper / live orders from the bot.
- `Streamlit` / dashboard displays portfolio, regime state, signals, and risk controls.
- `Walk-forward backtesting` supports validation before paper/live use.

## Notes
> [!warning]
> This transcript is heavily tutorial / promotional in tone. Treat the strategy thresholds, regime labels, and backtest claims as source-local until reinforced by additional evidence.

> [!info]
> The transcript repeatedly stresses paper trading, validation, and manual review before live deployment. That caution is more durable than the exact example settings.

## Open questions
- Do the regime labels and thresholds generalize beyond the tutorial’s example setup?
- Is the Alpaca-first recommendation still the best default once slippage, fees, and latency are measured?
- Does the HMM + allocation + risk stack produce a durable edge in live conditions?
- Should this later be folded into a broader `trading-automation` or `claude-code-trading-automation` synthesis if more sources arrive?

## Related pages
- [[regime-trading-bot]]
- [[source-simple-4-step-ai-trading-assistant-with-claude]]

## Sources
- Original raw source: `raw/articles/how-to-actually-build-a-trading-bot-with-claude-code-fully-automated.md`
