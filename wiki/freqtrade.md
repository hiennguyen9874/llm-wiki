---
title: Freqtrade
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - Freqtrade project
  - Freqtrade crypto trading bot
  - Freqtrade trading bot
tags:
  - trading
  - crypto
  - bot
  - automation
  - backtesting
  - python
  - finance
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-freqtrade]]
confidence_score: 0.82
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Freqtrade
  - FreqAI
  - WebUI
  - Telegram
  - dry-run
  - backtesting
  - hyperopt
  - money management
  - Binance
  - Bybit
  - OKX
  - Kraken
---

# Freqtrade

## Summary
Freqtrade is a Python-based open-source crypto trading bot built for operational use: configure an exchange, test strategies, dry-run first, and then optionally move to live trading. The project emphasizes practical controls such as a built-in WebUI, Telegram management, backtesting, plotting, and strategy optimization.

The durable takeaway is not just that it is a bot, but that it exposes a fairly complete trading workflow: data, strategy, testing, execution, and monitoring all sit in one documented toolchain.

## Key capabilities
### Trading workflow
- create-userdir / new-config / show-config / new-strategy
- download, convert, and list market data
- backtesting and backtest analysis
- hyperopt and hyperopt result inspection
- lookahead and recursive analysis

### Operations and control
- built-in WebUI
- Telegram RPC commands for status, balance, profit, and emergency exits
- webserver module for remote access
- SQLite-backed persistence

### Strategy and research support
- plotting and profit visualization
- strategy optimization with machine-learning-oriented tooling via FreqAI
- support for whitelist / blacklist pair selection
- dry-run mode before live capital

### Exchange coverage
- documented support for many major spot and futures exchanges
- leverage docs called out separately
- community-tested exchanges also listed in the source

## Evidence / claims
#### Claim
- Statement: Freqtrade is a free and open-source Python crypto trading bot with a documented operational workflow.
- Status: active
- Confidence: 0.93
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: This is the stable identity of the project.

#### Claim
- Statement: Freqtrade supports backtesting, hyperopt, plotting, and dry-run workflows as first-class features.
- Status: active
- Confidence: 0.90
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: These are central to the project's value.

#### Claim
- Statement: Freqtrade can be managed through both a built-in WebUI and Telegram RPC commands.
- Status: active
- Confidence: 0.88
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: This makes the bot operationally accessible.

#### Claim
- Statement: The docs explicitly recommend starting with dry-run before risking live money.
- Status: active
- Confidence: 0.96
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: Strong safety guidance.

#### Claim
- Statement: The project supports a broad set of exchanges, including major spot and futures venues.
- Status: active
- Confidence: 0.80
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: Keep this as a high-level claim unless a future source needs precise exchange-by-exchange tracking.

## Relationships
- `Freqtrade` is adjacent to [[hummingbot]] because both are classic open-source trading bots, though Hummingbot is more connector-centric.
- `Freqtrade` is adjacent to [[regime-trading-bot]] because both emphasize automated trading with safety controls.
- `Freqtrade` is adjacent to [[quantdinger]] because both are practical trading systems with strategy, execution, and operations surfaces.
- `Freqtrade` is adjacent to [[vibe-trading]] because both sit in the broader trading-automation space.
- `Freqtrade` is adjacent to [[tradingagents]] as another structured trading system, though it is less agent-centric.

## Notes
> [!info]
> Freqtrade is best read as a classic production-minded trading bot rather than an LLM research artifact.

> [!warning]
> The upstream docs change over time. Exchange lists, CLI commands, and feature details should be revisited if they become decision-relevant.

## Open questions
- Should Freqtrade stay as a standalone project page, or later anchor a broader trading-automation synthesis?
- Which features are stable enough to treat as durable knowledge versus docs snapshot material?

## Related pages
- [[source-freqtrade]]
- [[hummingbot]]
- [[regime-trading-bot]]
- [[quantdinger]]
- [[vibe-trading]]
- [[tradingagents]]
