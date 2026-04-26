---
title: Jesse ingest plan
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
  - python
related_sources:
  - [[source-jesse]]
visibility: private
retention_class: working
---

# Jesse ingest plan

## Source identity
- Source file: `raw/apps/jesse.md`
- Source type: documentation / README snapshot
- Canonical URL: `https://github.com/jesse-ai/jesse`
- Subject: advanced crypto trading framework for researching, defining, backtesting, optimizing, and live trading strategies.

## Why it matters
Jesse adds another classic crypto-trading framework to the wiki's trading-automation cluster. It is especially useful because it covers a broad operational surface:
- strategy authoring in Python
- backtesting and live trading
- multiple timeframes / symbols
- indicators, order types, and risk management
- debug, optimization, Monte Carlo, and ML-assisted workflow claims

## Key entities and relationships
- `Jesse` — crypto trading framework / project
- `Strategy` — user-authored strategy class
- `ta` / indicators — technical analysis helpers
- `backtesting` — validation workflow
- `live trading` / `paper trading` — execution modes implied by the README
- `optimize mode` — parameter tuning / AI-assisted optimization claim
- `JesseGPT` — integrated assistant claim
- `machine learning` pipeline — data gathering, training, and deployment helpers

Typed relationships:
- `Jesse` supports `backtesting`, `optimization`, and `live trading`
- `Jesse` uses `Python` strategy definitions and technical indicators
- `Jesse` combines execution, monitoring, and validation features in one framework
- `Jesse` is adjacent to [[freqtrade]], [[hummingbot]], [[quantdinger]], [[vibe-trading]], and [[tradingagents]] in the trading-automation cluster

## Candidate claims
1. Jesse is an advanced crypto trading framework for researching and defining Python trading strategies.
2. It supports backtesting, live trading, multiple timeframes / symbols, and built-in risk management.
3. It exposes advanced feature surfaces such as debug mode, optimize mode, Monte Carlo analysis, and machine learning helpers.
4. The README claims integrated assistant and tooling support through JesseGPT and a built-in code editor.
5. The README is promotional in tone, so accuracy / simplicity claims should be preserved as source statements rather than independently verified facts.

## What is new / reinforced / uncertain
### New
- Adds a fresh classic crypto bot / framework reference distinct from Freqtrade and Hummingbot.
- Adds a strong example of an all-in-one strategy workflow that includes optimization and ML claims.

### Reinforced
- The existing trading cluster's themes of dry-run / backtesting discipline, structured strategy workflows, and operational tooling.
- The pattern that trading platforms increasingly combine coding, testing, execution, and monitoring in one system.

### Uncertain
- Which README claims are stable implementation facts versus marketing claims.
- Whether Jesse should later remain a standalone project page or be folded into a broader trading-automation synthesis if more classic bot references arrive.

## Proposed edits
### Source page
Create `[[source-jesse]]` with source metadata, durable claims, relationships, and source-specific notes on promotional framing.

### Canonical page
Create `[[jesse]]` as the durable project page summarizing workflow, capabilities, and caveats.

### Related pages to update
- `[[overview]]`
- `[[index]]`
- `[[log]]`
- likely `[[freqtrade]]` and `[[hummingbot]]` to add Jesse as an adjacent classic-bot reference

## Traceability
- Add `related_sources: [[source-jesse]]` to `[[jesse]]`
- Keep the source page as the support anchor for the project page

## Scope recommendation
- Treat this as a single-source ingest for now.
- Do not trigger `/compile` yet.
- Integrate into the existing trading cluster rather than creating a new synthesis page.

## Review items
- `approve_edit`: Decide later whether Jesse should stay as a standalone project page or eventually feed a broader trading-automation synthesis.
- `deep_research`: Optional future verification if feature claims such as optimization, JesseGPT, or ML pipeline behavior become decision-relevant.

## Outputs / visuals
- No Canvas or Base needed now.
- No separate durable analysis artifact beyond this plan and the updated wiki pages.

## Human judgment
No high-stakes taxonomy or destructive change required.
Proceed with normal source integration.
