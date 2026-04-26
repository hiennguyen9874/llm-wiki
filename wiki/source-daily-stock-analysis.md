---
title: Source - Daily Stock Analysis
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - Daily Stock Analysis README
  - daily_stock_analysis
  - 股票智能分析系统
  - Stock Analysis System source
tags:
  - source
  - trading
  - ai
  - stocks
  - automation
  - analysis
  - dashboard
domain: trading
importance: medium
review_status: active
related_sources: []
confidence_score: 0.76
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
  - ZhuLinsen
  - Daily Stock Analysis
  - 股票智能分析系统
  - GitHub Actions
  - Docker
  - FastAPI
  - AIHubMix
  - Gemini
  - OpenAI-compatible models
  - Claude
  - Ollama
  - WeCom
  - Feishu
  - Telegram
  - Discord
  - Slack
  - Email
  - A-shares
  - Hong Kong stocks
  - US stocks
source_file: raw/apps/daily_stock_analysis.md
source_type: documentation
author: ZhuLinsen
canonical_url: https://github.com/ZhuLinsen/daily_stock_analysis
---

# Source - Daily Stock Analysis

## What this source is
A README / documentation source for `daily_stock_analysis`, presented as an AI-powered stock-analysis system that builds a daily decision dashboard and pushes it to messaging and email channels.

## Why it matters
This source adds a clean, analysis-first branch to the trading cluster. It is less about live execution and more about turning market data, sentiment, fundamentals, and strategy logic into a repeatable daily decision workflow.

The durable value is in the pipeline shape:
- ingest multiple market and news signals
- synthesize a decision dashboard
- validate history with backtests
- deliver results through automated notifications
- support manual review through a web workspace

## Key claims
#### Claim
- Statement: Daily Stock Analysis is an AI-driven stock-analysis system for A-share, Hong Kong, and US self-selected stocks that produces a daily decision dashboard.
- Status: active
- Confidence: 0.80
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: This is the README’s top-level product framing.

#### Claim
- Statement: The analysis stack combines technical analysis, real-time market data, chip distribution, news sentiment, announcements, capital flow, and fundamentals.
- Status: active
- Confidence: 0.79
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: This is the most durable structural claim in the source.

#### Claim
- Statement: The project supports multiple output channels, including WeCom, Feishu, Telegram, Discord, Slack, and email.
- Status: active
- Confidence: 0.82
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: This makes the system operationally useful rather than purely analytical.

#### Claim
- Statement: The repo includes a web workspace for manual analysis, configuration management, task progress, historical reports, backtesting, and portfolio management.
- Status: active
- Confidence: 0.78
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: This is the core operator surface around the analysis pipeline.

#### Claim
- Statement: The system supports smart import from images, CSV/Excel, and clipboard, plus code/name/pinyin/alias completion for watchlists.
- Status: active
- Confidence: 0.76
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: Useful because it lowers the friction of daily watchlist maintenance.

#### Claim
- Statement: The automation story centers on GitHub Actions, Docker, local scheduling, and FastAPI service mode.
- Status: active
- Confidence: 0.77
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: Treat this as the project’s deployment / orchestration layer.

#### Claim
- Statement: The README includes a learning / research disclaimer rather than an explicit live-trading promise.
- Status: active
- Confidence: 0.85
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: Keep the non-investment-advice framing visible downstream.

## Relationships
- `Daily Stock Analysis` uses a dashboard-first workflow: analysis inputs → decision summary → notifications → history / validation.
- `Daily Stock Analysis` depends on multi-market data sources and LLM providers.
- `Daily Stock Analysis` is adjacent to [[quantdinger]], [[vibe-trading]], [[tradingagents]], and [[regime-trading-bot]] because all sit in the broader AI-finance automation space.

## Notes
> [!info]
> The source is useful because it shows how a public repo can operationalize daily stock analysis without needing to promise live execution.

> [!warning]
> Preserve the distinction between documented capability and independently verified implementation. The README is credible as a product description, but feature completeness is not yet code-verified here.

## Related pages
- [[daily-stock-analysis]]
- [[quantdinger]]
- [[vibe-trading]]
- [[tradingagents]]
- [[regime-trading-bot]]
- [[overview]]
- [[index]]

## Open questions
- Which of the deployment and model claims are code-level reality versus README-level promise?
- Should this source later anchor a broader `stock-analysis-automation` synthesis, or remain a project-local reference?
- Are the import and alias-completion features stable enough to keep as durable capabilities in future maintenance passes?
