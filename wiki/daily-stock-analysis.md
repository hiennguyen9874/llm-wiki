---
title: Daily Stock Analysis
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - daily_stock_analysis
  - Daily Stock Analysis System
  - 股票智能分析系统
  - Stock Analysis System
tags:
  - trading
  - ai
  - stocks
  - automation
  - analysis
  - finance
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-daily-stock-analysis]]
confidence_score: 0.77
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: working
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - ZhuLinsen
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
  - historical reports
  - backtesting
  - portfolio management
---

# Daily Stock Analysis

## Summary
Daily Stock Analysis is a daily stock-analysis platform that turns multi-market data, news, fundamentals, and strategy logic into a decision dashboard and pushes the result through automated notification channels.

It is best understood as an analysis-and-delivery system rather than a live trading engine. The source emphasizes watchlist review, operator workflows, and validation of historical analysis.

> [!note]
> The repo’s durable value is the workflow shape: gather signals, synthesize a decision, push the result, and keep a history for review.

## Key capabilities
### Analysis inputs
- technical analysis
- real-time quotes and market data
- chip distribution
- news sentiment
- announcements and catalysts
- capital flow
- fundamentals

### Markets covered
- A-shares
- Hong Kong stocks
- US stocks
- indices
- common ETFs

### Output and delivery
- one-line core conclusion
- score and buy/sell levels
- risk alerts and action checklist
- multi-channel push to WeCom, Feishu, Telegram, Discord, Slack, and email

### Operator workspace
- manual analysis and configuration management
- task progress monitoring
- historical report browsing
- full Markdown report generation
- backtest validation of prior analyses
- portfolio / holdings management
- image, CSV/Excel, and clipboard import
- code/name/pinyin/alias completion

### Automation and orchestration
- GitHub Actions for scheduled runs
- Docker deployment
- local scheduling
- FastAPI service mode

## Evidence / claims
#### Claim
- Statement: Daily Stock Analysis turns daily market data into a decision dashboard for A/H/US watchlists.
- Status: active
- Confidence: 0.80
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: This is the project’s top-level framing.

#### Claim
- Statement: The platform combines technicals, sentiment, announcements, capital flow, fundamentals, and market data in one analysis workflow.
- Status: active
- Confidence: 0.79
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: This is the durable structural synthesis to keep.

#### Claim
- Statement: The system emphasizes operational delivery through multi-channel notifications and a web workspace for review and configuration.
- Status: active
- Confidence: 0.80
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: This is what makes the project reusable in practice.

#### Claim
- Statement: The README frames the project as learning / research oriented rather than as a live-trading promise.
- Status: active
- Confidence: 0.85
- Evidence: [[source-daily-stock-analysis]]
- Last confirmed: 2026-04-26
- Notes: Keep the non-investment-advice framing visible.

## Relationships
- `Daily Stock Analysis` uses a dashboard-first flow: signal collection → synthesis → notification → historical review.
- `Daily Stock Analysis` depends on LLM providers and market-data vendors.
- `Daily Stock Analysis` is adjacent to [[quantdinger]] because both combine research, workflow, and operational delivery in one platform.
- `Daily Stock Analysis` is adjacent to [[vibe-trading]] because both emphasize multi-surface interfaces and reusable automation primitives.
- `Daily Stock Analysis` is adjacent to [[tradingagents]] because both structure market analysis into repeatable agentic workflows.
- `Daily Stock Analysis` is adjacent to [[regime-trading-bot]] because both are concerned with transforming market interpretation into actionable summaries.

## Open questions
- Which implementation details are stable enough to treat as durable beyond the README snapshot?
- Should this page later feed a broader `stock-analysis-automation` synthesis, or remain a distinct project anchor?
- Would a Canvas or Base help if more daily-dashboard style repos enter the wiki?

## Related pages
- [[source-daily-stock-analysis]]
- [[quantdinger]]
- [[vibe-trading]]
- [[tradingagents]]
- [[regime-trading-bot]]
- [[overview]]
- [[index]]
