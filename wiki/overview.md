---
title: Overview
created: 2026-04-24
last_updated: 2026-04-26
source_count: 23
status: draft
page_type: overview
aliases: [Current Overview, Wiki Overview]
tags: [system, synthesis]
domain: general
importance: high
review_status: active
related_sources:
  - [[source-how-to-connect-claude-to-tradingview]]
  - [[source-how-to-connect-claude-to-tradingview-2]]
  - [[source-how-to-use-claude-to-build-tradingview-indicators]]
  - [[source-claude-code-tradingview-live-trading-bot-0dte]]
  - [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]
  - [[source-gpt-55-traded-for-me-and-made-54597-percent]]
  - [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
  - [[source-i-gave-claude-ai-full-access-to-tradingview-the-scalping-strategy-it-built-was-insane]]
  - [[source-openclaw-for-tradingview]]
  - [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
  - [[source-polymarket-5-min-claude-code-bot-are-nuts]]
  - [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
  - [[source-vibe-trading]]
  - [[source-quantdinger]]
  - [[source-tradingagents]]
  - [[source-fincept-terminal]]
  - [[source-daily-stock-analysis]]
  - [[source-openbb]]
  - [[source-finrl]]
  - [[source-fingpt]]
  - [[source-freqtrade]]
  - [[source-hummingbot]]
  - [[source-jesse]]
confidence_score: 0.69
quality_score: 0.78
evidence_count: 23
first_seen: 2026-04-24
last_confirmed: 2026-04-26
claim_status: active
retention_class: working
visibility: private
supersedes: []
superseded_by: []
related_entities: []
---

# Overview

Agent-updated current-state synthesis of the wiki. Keep [[home]] stable for human orientation; keep this page current enough that broad query, review, crystallization, and manual-first research planning can quickly understand the shape of the knowledge base.

## Current state

The wiki is in an early structural phase. Core navigation, logging, lifecycle rules, review dashboards, and workflow skills exist. Domain knowledge pages have started to populate with a TradingView-Claude cluster spanning connection/setup sources, an indicator-building walkthrough source, a live-trading / 0DTE research source, a fifth master-prompt / no-terminal demo source, a new Ethereum scalping-strategy demo with BlackCat indicators and backtest claims, a separate MoonDev / liquidation-data trading-research branch centered on model-comparison backtests, a new Claude Code automated-trading-bot branch centered on HMM regime detection, Alpaca execution, and risk management, a new TradingView community-indicator mining / Pine-to-Python backtest branch, a broad Vibe-Trading agentic finance workspace branch with CLI/TUI, MCP, memory, swarms, and backtests, a QuantDinger self-hosted AI quant OS branch with Flask/Vue/Nginx, Python strategy generation, live execution, and commercialization primitives, a formal TradingAgents multi-agent trading-firm branch with role specialization, debate, and benchmarked backtests, a new Fincept Terminal native financial intelligence terminal branch with C++20/Qt6/Python analytics, data connectors, and broker integrations, a Daily Stock Analysis stock-analysis automation branch with daily dashboards and push delivery, a new OpenBB financial data platform branch with Python, Workspace, Excel, MCP, and REST surfaces, a new FinRL financial reinforcement learning branch with the original train-test-trade pipeline and FinRL-X successor framing, a new FinGPT open-source financial LLM branch with datasets, LoRA fine-tuning, forecasting demos, and benchmarked finance tasks, classic Freqtrade and Hummingbot crypto-bot / trading-framework branches, a new Jesse crypto trading-framework branch with strategy authoring, optimize mode, Monte Carlo, and ML claims, and a Polymarket / prediction-market AI-agent branch that now splits into consensus-scanning, short-interval backtest / tick-data experimentation, and keyword-filtered P&L tracking / post-trade analysis.

## Major knowledge areas

- Projects and work
- Research and learning
- Ideas and writing
- People and relationships
- Health, habits, and personal systems

## Active direction

- Build durable semantic pages from raw sources and crystallized sessions.
- Use two-stage ingest for substantial sources.
- Preserve provenance, uncertainty, contradictions, and supersession.
- Use QMD plus markdown links/metadata for retrieval and graph-like traversal.
- Use Bases and Canvases when they improve review or synthesis.

## Known gaps

- Purpose needs explicit human refinement beyond broad priorities.
- Source pages and canonical topic/entity pages are still early but now form a coherent trading-automation and finance-LLM cluster: TradingView-Claude tooling, MoonDev / liquidation-data tooling, regime trading bots, OpenClaw-style indicator mining, Vibe-Trading’s broader agentic finance workspace, QuantDinger’s self-hosted AI quant OS, FinRL’s original finance-RL stack, FinGPT’s open-source financial LLM stack, Daily Stock Analysis’s stock-analysis automation branch, classic crypto bots like Freqtrade, Hummingbot, and Jesse, and prediction-market trading workflows.
- Review queue has active human-judgment items for page scope, cluster boundaries, and robustness / overfit risk in the trading cluster.
- Graph-insights-lite has now been run once on the populated wiki; the current bridge pages are [[tradingview-mcp]], [[moondev]], and [[prediction-market-trading]].

## Recent structural changes

- Added `purpose.md` for directional intent.
- Added this overview as a separate agent-maintained current-state synthesis.
- Added conventions for ingest plans, review queue items, graph-insights-lite, and manual-first Deep Research.
- Adopted selected `LLM-Wiki-v4.md` workflow ideas in manual-first form: `/compile`, stronger `related_sources` traceability, index-as-rebuildable-catalog, conservative lint-as-migration, librarian-style freshness/quality review.
- Added the first source/topic ingest pair for a TradingView-Claude MCP workflow source, then reinforced that cluster with a second source describing more CLI and chart-data detail, then added a third source on prompt-by-prompt TradingView indicator construction and OI/EMA interpretation, then added a fourth source on live trading bot prototyping, RBI, and 0DTE research, then added a fifth source focused on a master-prompt, no-terminal demo of chart reading and custom indicator generation, then added a sixth source on GPT-5.5 vs Claude Opus 4.7 liquidation-data backtests plus a new MoonDev topic page, then added a seventh source plus a new regime-trading-bot topic for a Claude Code automated-trading-bot tutorial, then added an eighth source on Claude-generated Ethereum scalping strategy design with BlackCat indicators and a 30-minute optimization claim, then added a ninth source plus a new OpenClaw project page for TradingView community-indicator mining and Pine-to-Python backtesting, then added a tenth source plus a new prediction-market-trading topic for Polymarket AI-agent consensus workflows, then added an eleventh source that expands the Polymarket branch into short-interval backtesting, tick data, and CVD, then added a twelfth source that adds keyword-filtered P&L tracking and post-trade analysis to the Polymarket branch, then added a thirteenth source plus a new Vibe-Trading project page for a broad agentic finance workspace with CLI/TUI, MCP, persistent memory, swarm workflows, and backtests, then added a fourteenth source plus a new QuantDinger project page for a self-hosted AI quant operating system with Flask/Vue/Nginx deployment, Python strategy generation, backtesting, live execution, and commercialization primitives, then added a fifteenth source plus a new TradingAgents project page for a multi-agent trading-firm framework with role specialization, debate, and benchmarked backtests, then added a sixteenth source plus a new Fincept Terminal project page for a native desktop financial intelligence terminal with C++20/Qt6/Python analytics, data connectors, broker integrations, and optional alternative-data overlays, then added a seventeenth source plus a new Daily Stock Analysis project page for an AI stock-analysis system with dashboards, imports, notifications, and validation, then added an eighteenth source plus a new OpenBB project page for a financial data platform with Python, Workspace, Excel, MCP, and REST surfaces, then added a nineteenth source plus a new FinGPT project page for an open-source financial LLM stack with datasets, LoRA fine-tuning, benchmarks, and forecasting demos, then added a twentieth source plus a new FinRL project page for the original financial reinforcement learning framework and its FinRL-X successor framing, then added a twenty-first source plus a new Freqtrade project page for the open-source crypto trading bot with dry-run, backtesting, WebUI, Telegram, and exchange support, then added a twenty-second source plus a new Hummingbot project page for the connector-centric trading framework with Gateway middleware and ecosystem repos, and now added a twenty-third source plus a new Jesse project page for the crypto trading framework with strategy authoring, optimize mode, Monte Carlo analysis, and ML claims.
- Ran the first monthly review on the populated wiki, including lint, retention/freshness checks, review queue normalization, privacy scan, and graph-insights-lite; saved the durable report at `outputs/reports/lint-report-2026-04-26.md`.

## Next actions

- Refine `purpose.md` with current top goals and questions.
- Ingest first high-value sources using the two-stage workflow.
- Continue validating the trading-research and automated-trading-bot branches with follow-up robustness checks where results look overfit.
- Compare whether prediction-market workflows deserve their own long-lived synthesis or should later fold into a broader trading-automation cluster.
- Consider whether future finance-RL and finance-LLM sources should accumulate into broader synthesis pages if FinRL- and FinGPT-like material keeps growing.
- Decide whether keyword-filtered P&L analysis should stay embedded in prediction-market-trading or eventually become a standalone trading-analytics concept.
- Consider whether classic bot sources like Freqtrade, Hummingbot, and Jesse should remain standalone project pages or later feed a broader trading-automation synthesis.
- Keep QMD retrieval refreshed after future ingest/review batches.
- Consider a `trading-automation` synthesis page or Canvas only after one more source/review pass confirms it would reduce fragmentation.
- Consider whether the finance-RL branch should eventually anchor a dedicated synthesis page if additional FinRL-X or related sources arrive.
- Consider whether OpenBB-like data infrastructure should later anchor a dedicated `financial-data-infrastructure` synthesis if similar sources accumulate.
