---
title: Source - Vibe-Trading
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - Vibe-Trading README
  - Vibe Trading documentation
  - Vibe-Trading source
tags:
  - source
  - trading
  - agents
  - mcp
  - backtesting
  - automation
domain: trading
importance: medium
review_status: active
related_sources:
  - [[vibe-trading]]
confidence_score: 0.74
quality_score: 0.82
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - HKUDS
  - Vibe-Trading
  - FastAPI
  - React
  - MCP
  - FTS5
  - Claude Desktop
  - OpenClaw
  - TradingView
source_file: raw/apps/Vibe-Trading.md
source_type: documentation
author: HKUDS
canonical_url: https://github.com/HKUDS/Vibe-Trading
---

# Source - Vibe-Trading

## What this source is
A README / documentation source for the `Vibe-Trading` repository, presented as an AI-powered multi-agent finance workspace and personal trading agent.

## Why it matters
This source broadens the trading cluster from narrow TradingView bridges and bot tutorials into a more complete agentic trading platform:
- interactive CLI / TUI
- FastAPI web server and React frontend
- MCP server for external agents
- persistent cross-session memory
- swarm workflows and reusable skills
- multi-market backtesting and export tooling
- broker-export / document analysis

## Key claims
#### Claim
- Statement: Vibe-Trading is an AI-powered multi-agent finance workspace that turns natural-language requests into executable trading strategies, research insights, and portfolio analysis across global markets.
- Status: active
- Confidence: 0.77
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: This is the top-level framing of the README.

#### Claim
- Statement: The project exposes a CLI/TUI, FastAPI server, React frontend, and MCP server as its main interaction surfaces.
- Status: active
- Confidence: 0.80
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: The source presents these as first-class product surfaces.

#### Claim
- Statement: The agent harness includes persistent cross-session memory, FTS5 session search, self-evolving skills, five-layer context compression, and read/write batching.
- Status: active
- Confidence: 0.78
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: These are core architectural claims in the README.

#### Claim
- Statement: The README claims 71 skills, 29 swarm presets, 5 data sources, and 7 backtest engines.
- Status: active
- Confidence: 0.73
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: Treat the counts as snapshot claims unless later verified in code.

#### Claim
- Statement: The MCP surface exposes 17 tools, and 16 of them work without API keys.
- Status: active
- Confidence: 0.76
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: This matters for how portable the platform is across local agents.

#### Claim
- Statement: The project can export strategies to TradingView, TDX, and MetaTrader 5, and it supports document upload / broker-export analysis.
- Status: active
- Confidence: 0.75
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: This extends the source beyond pure strategy generation into analysis and handoff.

#### Claim
- Statement: The README markets the app as a personal trading agent, but the disclaimer says it is for research, simulation, and backtesting only and does not execute live trades.
- Status: disputed
- Confidence: 0.86
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: Preserve this tension explicitly in downstream pages.

## Relationships
- `Vibe-Trading` uses a multi-surface product layout: CLI/TUI, web UI, and MCP integration.
- `Vibe-Trading` uses persistent memory and self-evolving skills to support long-running agent sessions.
- `Vibe-Trading` depends on trading data routing and backtest engines for research workflows.
- `Vibe-Trading` is adjacent to [[tradingview-mcp]], [[regime-trading-bot]], and [[openclaw-for-tradingview]].

## Notes
> [!info]
> This source is dense and promotional, but it is still useful because it defines a coherent platform shape. The durable takeaway is the platform architecture, not any implied trading edge.

> [!warning]
> The README’s branding and disclaimer point in slightly different directions: it sounds like a live trading agent, but the disclaimer narrows it to research / simulation / backtesting. Keep both visible.

## Related pages
- [[vibe-trading]]
- [[tradingview-mcp]]
- [[regime-trading-bot]]
- [[openclaw-for-tradingview]]

## Open questions
- Which parts of the platform are code-level reality versus documentation-level aspiration?
- Are the claimed feature counts stable enough to treat as durable, or should they be revisited on future maintenance passes?
- Should this become the anchor for a broader trading-automation synthesis later?
