---
title: Source - TradingAgents
created: 2026-04-26
last_updated: 2026-04-26
source_count: 2
status: draft
page_type: source
aliases:
  - TradingAgents paper
  - TradingAgents README
  - TradingAgents framework source
  - Multi-Agents LLM Financial Trading Framework
  - TradingAgents: Multi-Agents LLM Financial Trading Framework
tags:
  - source
  - trading
  - ai
  - agents
  - backtesting
  - research
  - framework
domain: trading
importance: medium
review_status: active
related_sources: []
confidence_score: 0.81
quality_score: 0.84
evidence_count: 2
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - TradingAgents
  - Yijia Xiao
  - Edward Sun
  - Di Luo
  - Wei Wang
  - Fundamentals Analyst
  - Sentiment Analyst
  - News Analyst
  - Technical Analyst
  - Researcher
  - Trader
  - Risk Manager
  - Bullish Researcher
  - Bearish Researcher
  - ReAct
  - AAPL
  - GOOGL
  - AMZN
source_file: raw/apps/TradingAgents.pdf
source_type: paper
author: Yijia Xiao, Edward Sun, Di Luo, Wei Wang
published: 2025-06-03
canonical_url: https://arxiv.org/abs/2412.20138
---

# Source - TradingAgents

## What this source is
A paired source family consisting of:
- the arXiv paper `TradingAgents: Multi-Agents LLM Financial Trading Framework`
- the repository README at `raw/apps/TradingAgents.md`

The paper presents the main research framing; the README adds release-note and usage context for the public project.

## Why it matters
This source is one of the clearest formal references in the trading-automation cluster. It gives the wiki a concrete multi-agent trading-firm model with:
- explicit role specialization
- bullish/bearish debate
- trader and risk-manager separation
- structured outputs and ReAct-style interaction
- benchmarked backtests against standard rule-based strategies

It is useful as both a concept source and a project reference for broader agentic trading work.

## Key claims
#### Claim
- Statement: TradingAgents is a multi-agent LLM financial trading framework inspired by real-world trading firms.
- Status: active
- Confidence: 0.88
- Evidence: [[source-tradingagents]]
- Last confirmed: 2026-04-26
- Notes: This is the paper’s main framing.

#### Claim
- Statement: The framework defines seven specialized roles: Fundamentals Analyst, Sentiment Analyst, News Analyst, Technical Analyst, Researcher, Trader, and Risk Manager.
- Status: active
- Confidence: 0.90
- Evidence: [[source-tradingagents]]
- Last confirmed: 2026-04-26
- Notes: The researcher role is debated from bullish and bearish perspectives; the paper and README both reinforce the role-specialization pattern.

#### Claim
- Statement: TradingAgents combines structured outputs, natural-language debate, and ReAct-style reasoning/acting on shared environment state.
- Status: active
- Confidence: 0.84
- Evidence: [[source-tradingagents]]
- Last confirmed: 2026-04-26
- Notes: This is the durable communication / coordination pattern worth preserving.

#### Claim
- Statement: The paper evaluates the framework on a Jan 1 to Mar 29, 2024 backtest using multimodal market data and compares it against Buy & Hold, MACD, KDJ+RSI, ZMR, and SMA.
- Status: active
- Confidence: 0.82
- Evidence: [[source-tradingagents]]
- Last confirmed: 2026-04-26
- Notes: The experiment is real and concrete, but the window is short.

#### Claim
- Statement: The paper reports at least 23.21% cumulative return and 24.90% annualized return on the sampled stocks, with better Sharpe ratio and lower maximum drawdown than the best baselines.
- Status: active
- Confidence: 0.70
- Evidence: [[source-tradingagents]]
- Last confirmed: 2026-04-26
- Notes: Useful, but keep the confidence modest because the evaluation set is narrow and the result could be overfit.

#### Claim
- Statement: The README’s release-note snapshot says v0.2.4 added structured-output agents, LangGraph checkpoint resume, a persistent decision log, multi-provider support, Docker, and a Windows UTF-8 fix.
- Status: active
- Confidence: 0.76
- Evidence: [[source-tradingagents]]
- Last confirmed: 2026-04-26
- Notes: Treat as a documentation snapshot rather than independently verified code behavior.

## Relationships
- `TradingAgents` uses a trading-firm role model with analyst, debate, trader, and risk-management functions.
- `TradingAgents` depends on debate and shared-state coordination to translate analysis into trades.
- `TradingAgents` is adjacent to [[regime-trading-bot]], [[vibe-trading]], and [[quantdinger]] because all three sit in the broader trading-automation / agentic-finance space.
- `TradingAgents` is conceptually related to [[tradingview-mcp]] and [[openclaw-for-tradingview]] as another attempt to structure AI assistance around trading workflows.

## Notes
> [!info]
> The strongest durable lesson here is architectural: split analysis, debate, execution, and risk control into separate roles.

> [!warning]
> The benchmark claims are interesting but narrow. The source itself points toward future live-trading work, so the safe interpretation is “promising framework, not proven edge.”

## Related pages
- [[tradingagents]]
- [[regime-trading-bot]]
- [[vibe-trading]]
- [[quantdinger]]
- [[tradingview-mcp]]
- [[openclaw-for-tradingview]]

## Open questions
- Are the benchmark results stable enough to justify broader synthesis, or should they stay source-local?
- Would a future `trading-automation` synthesis page reduce fragmentation, or would it become too broad?
- How much of the README’s v0.2.4 snapshot is durable versus quickly changing?
