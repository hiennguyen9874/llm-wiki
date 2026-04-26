---
title: Freqtrade ingest plan
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
tags:
  - ingest
  - trading
  - crypto
  - bot
  - automation
related_sources:
  - [[source-freqtrade]]
visibility: private
retention_class: working
---

# Freqtrade ingest plan

## Source identity
- Source file: `raw/apps/freqtrade.md`
- Source type: documentation / README
- Canonical URL: `https://github.com/freqtrade/freqtrade`
- Subject: open-source Python crypto trading bot with exchange support, backtesting, dry-run, WebUI, Telegram control, and strategy optimization / FreqAI features.

## Why it matters
Freqtrade is a concrete, widely used crypto-trading automation reference. It strengthens the trading-automation cluster with a more classic bot architecture than the existing Claude/LLM-heavy sources:
- operational trading bot workflow
- exchange connectivity and leverage support
- backtesting and hyperopt tooling
- safety-first dry-run guidance
- web and Telegram control surfaces

## Key entities and relationships
- `Freqtrade` — Python crypto trading bot project
- `FreqAI` — adaptive prediction / ML-oriented strategy tooling
- `WebUI` — browser control surface
- `Telegram` — remote control surface
- `Backtesting`, `Hyperopt`, `Plotting`, `Money management` — core operational features
- `dry-run` — recommended safe start mode
- `supported exchanges` — spot and futures venues listed in docs

Typed relationships:
- `Freqtrade` uses `WebUI` and `Telegram` for control
- `Freqtrade` depends on exchange integrations for execution
- `Freqtrade` supports backtesting and hyperparameter optimization
- `Freqtrade` recommends dry-run before live funds
- `Freqtrade` is adjacent to [[regime-trading-bot]], [[quantdinger]], [[vibe-trading]], and [[tradingagents]] in the trading-automation cluster

## Candidate claims
1. Freqtrade is a free and open-source crypto trading bot written in Python.
2. It supports major exchanges and can be controlled via Telegram or a web UI.
3. It includes backtesting, plotting, money management, and machine-learning strategy optimization.
4. The docs explicitly recommend dry-run first and warn users to understand the software before risking money.
5. The README lists extensive CLI commands for trading, data management, backtesting, hyperopt, plotting, webserver, and analysis workflows.

## What is new / reinforced / uncertain
### New
- Adds a durable classic crypto-bot reference to the trading cluster.
- Adds a source that is about operational botting rather than only LLM-assisted workflows.

### Reinforced
- Safe-first paper-trading / dry-run guidance already present in the trading pages.
- The value of separating strategy, execution, and risk control.

### Uncertain
- Which exchange support claims are stable versus documentation snapshots.
- Whether Freqtrade should remain a standalone project page or later feed a broader `trading-automation` synthesis.

## Proposed edits
### Source page
Create `[[source-freqtrade]]` with source metadata, claims, relationships, and open questions.

### Canonical page
Create `[[freqtrade]]` as the durable project page summarizing capabilities, workflow, and safety posture.

### Related pages to update
- `[[overview]]`
- `[[index]]`
- `[[log]]`
- possibly `[[regime-trading-bot]]` / `[[quantdinger]]` / `[[vibe-trading]]` if cross-link density is worth expanding later

## Traceability
- Add `related_sources: [[source-freqtrade]]` to `[[freqtrade]]`
- Keep `related_sources: []` or source-local support on `[[source-freqtrade]]`

## Scope recommendation
- Treat this as a single-source ingest for now.
- Do not trigger `/compile` yet; the source fits the existing trading cluster without requiring a broader synthesis merge.

## Review items
- `approve_edit`: Decide later whether Freqtrade should remain a standalone project page or fold into a broader `trading-automation` synthesis if more classic bot sources arrive.
- `deep_research`: Optional future follow-up if exchange-support or feature claims need verification against current upstream docs.

## Outputs / visuals
- No Canvas or Base needed now.
- No durable standalone analysis needed beyond this plan and the source/project pages.

## Human judgment
No high-stakes taxonomy or destructive change required.
Proceed with normal source integration.
