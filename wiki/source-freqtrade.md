---
title: Source - Freqtrade
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - Freqtrade README
  - Freqtrade documentation
  - Freqtrade repo README
tags:
  - source
  - trading
  - crypto
  - bot
  - automation
  - backtesting
  - python
domain: trading
importance: medium
review_status: active
related_sources: []
confidence_score: 0.84
quality_score: 0.83
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
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
source_file: raw/apps/freqtrade.md
source_type: documentation
author: Freqtrade contributors
canonical_url: https://github.com/freqtrade/freqtrade
---

# Source - Freqtrade

## What this source is
A project README / documentation snapshot for Freqtrade, a free and open-source crypto trading bot written in Python.

## Why it matters
This source adds a concrete classic trading-bot reference to the wiki's trading cluster. It is useful because it covers the practical operating model of an automated trading bot rather than only agent-assisted research workflows:
- exchange integration
- dry-run safety
- backtesting and plotting
- hyperopt / ML-assisted strategy tuning
- WebUI and Telegram control
- CLI-first operations

## Key claims
#### Claim
- Statement: Freqtrade is a free and open-source crypto trading bot written in Python.
- Status: active
- Confidence: 0.94
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: This is the source's opening claim and the main identity statement.

#### Claim
- Statement: Freqtrade supports control through Telegram and a built-in web UI.
- Status: active
- Confidence: 0.90
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: This is one of the source's main practical features.

#### Claim
- Statement: Freqtrade includes dry-run, backtesting, plotting, money management, and strategy optimization features, including FreqAI.
- Status: active
- Confidence: 0.88
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: These are the durable features worth keeping in the wiki.

#### Claim
- Statement: The documentation recommends starting in dry-run mode and warns users not to risk money before understanding the bot.
- Status: active
- Confidence: 0.96
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: The safety posture is explicit and important.

#### Claim
- Statement: The README lists a broad CLI surface covering trading, configuration, data conversion, backtesting, hyperopt, plotting, webserver, and analysis commands.
- Status: active
- Confidence: 0.86
- Evidence: [[source-freqtrade]]
- Last confirmed: 2026-04-26
- Notes: This shows the project is operationally complete rather than a toy demo.

## Relationships
- `Freqtrade` uses `WebUI` and `Telegram` for control.
- `Freqtrade` depends on exchange integrations and documentation-specific exchange notes.
- `Freqtrade` supports the safe workflow pattern of dry-run first, then live use.
- `Freqtrade` is adjacent to [[regime-trading-bot]], [[quantdinger]], [[vibe-trading]], and [[tradingagents]] in the broader trading-automation cluster.

## Notes
> [!info]
> The most durable lesson is operational: a trading bot should expose control, testing, and risk-management surfaces clearly before live capital is involved.

> [!warning]
> Exchange-support lists and feature lists are documentation snapshots. Treat them as current until contradicted by newer evidence.

## Related pages
- [[freqtrade]]
- [[regime-trading-bot]]
- [[quantdinger]]
- [[vibe-trading]]
- [[tradingagents]]

## Open questions
- Does Freqtrade deserve a broader synthesis page if more classic bot references arrive?
- Which exchange and feature claims need future verification against upstream docs?
