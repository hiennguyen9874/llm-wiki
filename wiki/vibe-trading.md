---
title: Vibe-Trading
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - Vibe Trading
  - vibe-trading-ai
  - Personal Trading Agent
  - AI-powered multi-agent finance workspace
tags:
  - trading
  - agents
  - mcp
  - backtesting
  - automation
  - finance
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-vibe-trading]]
confidence_score: 0.76
quality_score: 0.83
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: working
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - HKUDS
  - FastAPI
  - React
  - MCP
  - FTS5
  - TradingView
  - Claude Desktop
  - OpenClaw
  - cross-session memory
  - swarm workflows
  - backtest engines
---

# Vibe-Trading

## Summary
Vibe-Trading is a broad agentic finance workspace: it combines a CLI/TUI, web UI, MCP server, persistent memory, swarm-based multi-agent workflows, backtesting engines, and multi-platform export tools into one trading-research platform.

The project is best understood as an end-to-end research and analysis environment rather than a simple indicator script or single-purpose bot. The README emphasizes natural-language strategy generation, market research, portfolio analysis, and reusable skills.

> [!note]
> The repo’s branding is stronger than its disclaimer. It presents itself as a personal trading agent, but the README says it is for research, simulation, and backtesting only and does not execute live trades.

## Key capabilities

### Interface surface
- CLI/TUI for interactive runs and slash commands
- FastAPI server for web access and API routes
- React frontend for dashboards and run views
- MCP server for agent-client integration

### Agent harness
- Persistent cross-session memory
- FTS5 session search
- Self-evolving skills with CRUD workflows
- Five-layer context compression
- Read/write tool batching

### Research and execution support
- Natural-language prompts become trading strategies, research summaries, or portfolio analysis
- Swarm presets provide pre-built multi-agent finance workflows
- Backtest engines cover multiple markets and composite portfolios
- Statistical validation and optimizer support are advertised

### Data and export
- Market coverage spans A-shares, HK/US equities, crypto, futures, and forex
- Strategies can be exported to TradingView, TDX, and MetaTrader 5
- Broker-export and document upload workflows support trade journal analysis

## Evidence / claims
#### Claim
- Statement: Vibe-Trading combines CLI/TUI, web UI, MCP, memory, swarms, backtests, and exports into one trading-research workspace.
- Status: active
- Confidence: 0.79
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: This is the broad architectural summary of the project.

#### Claim
- Statement: The platform claims persistent cross-session memory, self-evolving skills, FTS5 search, and five-layer context compression.
- Status: active
- Confidence: 0.78
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: This is the main “agent harness” differentiator.

#### Claim
- Statement: The README claims 71 skills, 29 swarm presets, 5 data sources, 7 backtest engines, and 17 MCP tools.
- Status: active
- Confidence: 0.72
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: Keep the counts as snapshot claims unless code verification later upgrades them.

#### Claim
- Statement: Vibe-Trading can export strategies to TradingView, TDX, and MetaTrader 5.
- Status: active
- Confidence: 0.74
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: This makes the tool useful as a research-to-platform handoff layer.

#### Claim
- Statement: The README’s live-trading branding is softened by a disclaimer that the project is for research, simulation, and backtesting only.
- Status: disputed
- Confidence: 0.86
- Evidence: [[source-vibe-trading]]
- Last confirmed: 2026-04-26
- Notes: Preserve the tension instead of rewriting it away.

## Relationships
- `Vibe-Trading` is adjacent to [[tradingview-mcp]] because both support agentic TradingView workflows.
- `Vibe-Trading` is adjacent to [[regime-trading-bot]] because both present layered automation and risk-aware research patterns.
- `Vibe-Trading` is adjacent to [[openclaw-for-tradingview]] because both sit in the broader agentic trading research ecosystem.
- `Vibe-Trading` is published by HKUDS and appears to be part of the same ecosystem as other agent-oriented finance tooling.

## Open questions
- Is the project primarily a research platform, a bot workspace, or a future live-trading foundation?
- Which feature counts are stable enough to track as durable facts?
- Should this page later anchor a broader `trading-automation` synthesis, or is the current cluster enough?

## Related pages
- [[source-vibe-trading]]
- [[tradingview-mcp]]
- [[regime-trading-bot]]
- [[openclaw-for-tradingview]]
- [[overview]]
- [[index]]
