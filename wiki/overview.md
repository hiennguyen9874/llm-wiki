---
title: Overview
created: 2026-04-24
last_updated: 2026-04-26
source_count: 11
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
confidence_score: 0.68
quality_score: 0.77
evidence_count: 11
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

The wiki is in an early structural phase. Core navigation, logging, lifecycle rules, review dashboards, and workflow skills exist. Domain knowledge pages have started to populate with a TradingView-Claude cluster spanning connection/setup sources, an indicator-building walkthrough source, a live-trading / 0DTE research source, a fifth master-prompt / no-terminal demo source, a new Ethereum scalping-strategy demo with BlackCat indicators and backtest claims, a separate MoonDev / liquidation-data trading-research branch centered on model-comparison backtests, a new Claude Code automated-trading-bot branch centered on HMM regime detection, Alpaca execution, and risk management, a new TradingView community-indicator mining / Pine-to-Python backtest branch, and a Polymarket / prediction-market AI-agent branch that now splits into both consensus-scanning and short-interval backtest / tick-data experimentation.

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
- Source pages and canonical topic/entity pages are only just beginning to populate, including a MoonDev / liquidation-data tooling page that sits alongside the TradingView-Claude cluster, a new regime-trading-bot topic for automated trading architecture, and a new prediction-market-trading topic for Polymarket-style AI-agent workflows.
- Review queue exists as a workflow convention and now has active ingest judgment items for scope / robustness decisions in the trading cluster.
- Graph-insights-lite has not yet been run on a populated wiki.

## Recent structural changes

- Added `purpose.md` for directional intent.
- Added this overview as a separate agent-maintained current-state synthesis.
- Added conventions for ingest plans, review queue items, graph-insights-lite, and manual-first Deep Research.
- Adopted selected `LLM-Wiki-v4.md` workflow ideas in manual-first form: `/compile`, stronger `related_sources` traceability, index-as-rebuildable-catalog, conservative lint-as-migration, librarian-style freshness/quality review.
- Added the first source/topic ingest pair for a TradingView-Claude MCP workflow source, then reinforced that cluster with a second source describing more CLI and chart-data detail, then added a third source on prompt-by-prompt TradingView indicator construction and OI/EMA interpretation, then added a fourth source on live trading bot prototyping, RBI, and 0DTE research, then added a fifth source focused on a master-prompt, no-terminal demo of chart reading and custom indicator generation, then added a sixth source on GPT-5.5 vs Claude Opus 4.7 liquidation-data backtests plus a new MoonDev topic page, then added a seventh source plus a new regime-trading-bot topic for a Claude Code automated-trading-bot tutorial, then added an eighth source on Claude-generated Ethereum scalping strategy design with BlackCat indicators and a 30-minute optimization claim, then added a ninth source plus a new OpenClaw project page for TradingView community-indicator mining and Pine-to-Python backtesting, then added a tenth source plus a new prediction-market-trading topic for Polymarket AI-agent consensus workflows, and now added an eleventh source that expands the Polymarket branch into short-interval backtesting, tick data, and CVD.

## Next actions

- Refine `purpose.md` with current top goals and questions.
- Ingest first high-value sources using the two-stage workflow.
- Continue validating the trading-research and automated-trading-bot branches with follow-up robustness checks where results look overfit.
- Compare whether prediction-market workflows deserve their own long-lived synthesis or should later fold into a broader trading-automation cluster.
- Run review/lint once enough pages exist to surface real gaps and connections.
