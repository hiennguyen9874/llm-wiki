---
title: Ingest Plan - TradingAgents
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-tradingagents]]
  - [[tradingagents]]
---

# Ingest Plan - TradingAgents

## Source identity
- Source files: `raw/apps/TradingAgents.pdf`, `raw/apps/TradingAgents.md`
- Source type: paper + documentation / repository README
- Likely topic domain: multi-agent financial trading, agentic debate, risk-aware trading bots, backtesting, trading-firm simulation
- Why it matters to `purpose.md`: this source adds a canonical multi-agent trading framework with a trading-firm role model, structured outputs, debate, and a benchmarked backtest story.

## Key entities and relationships
- TradingAgents → multi-agent LLM financial trading framework
- Fundamentals Analyst / Sentiment Analyst / News Analyst / Technical Analyst → analyst team roles
- Bullish Researcher / Bearish Researcher → debate team roles
- Trader → decision-making / execution role
- Risk Manager → exposure and risk-control role
- ReAct → shared reasoning/acting protocol
- Structured outputs / shared environment state → communication and coordination layer
- Evaluation universe → AAPL, GOOGL, AMZN and broader tech-stock backtests
- Baselines → Buy & Hold, MACD, KDJ+RSI, ZMR, SMA

## Candidate claims
- TradingAgents mirrors the organization of a real trading firm using seven specialized roles.
- The framework combines structured outputs with natural-language debate and ReAct-style interaction.
- The paper’s simulation uses multimodal market data, including historical prices, news, social sentiment, insider information, financial statements, and 60 technical indicators.
- The reported experiment window is Jan 1, 2024 to Mar 29, 2024.
- The paper claims TradingAgents outperforms rule-based baselines on cumulative return, annualized return, Sharpe ratio, and maximum drawdown for the sampled stocks.
- The README companion documents release/usage details, including v0.2.4 structured-output agents, checkpoint resume, decision logs, and multi-provider support.

## Existing pages likely affected
- `[[tradingagents]]` — should become the canonical project/topic page for the framework.
- `[[overview]]` — should record TradingAgents as a new formal multi-agent trading branch.
- `[[index]]` — should add both the source and project pages.
- `[[regime-trading-bot]]`, `[[vibe-trading]]`, `[[quantdinger]]`, and `[[openclaw-for-tradingview]]` — adjacent trading-automation pages that should link to this source family.

## New vs reinforced vs uncertain
### New
- A formal, paper-backed multi-agent trading-firm architecture exists in the wiki’s trading cluster.
- Role specialization and debate are central design patterns, not just incidental features.
- The README adds a later release snapshot with structured-output agents and checkpoint/resume support.

### Reinforced
- The wiki’s broader trading cluster already includes agentic finance workspaces, trading bots, and execution-oriented tooling.
- Risk controls, staged reasoning, and backtesting remain recurring design motifs.

### Uncertain
- The performance claims come from a short historical window and a limited stock set; they should stay low-confidence until corroborated.
- The README’s feature list is useful but should be treated as a snapshot claim unless later verified in code.
- There is no contradiction with existing pages, but the benchmark numbers likely deserve a review note.

## Proposed page actions
### Source page
Create `wiki/source-tradingagents.md` with:
- source metadata for the paper + README family
- concise summary of the framework and the README companion
- claim blocks separating architecture, benchmark setup, and release-note snapshot claims
- a caution that the benchmark window is narrow
- links to the project page and nearby trading-automation pages

### Project page
Create `wiki/tradingagents.md` with:
- durable synthesis of the framework as a trading-firm simulator
- key capabilities organized by roles, coordination, data, and evaluation
- explicit note that the strongest durable takeaway is the architectural pattern, not the headline backtest numbers
- relationships to `[[regime-trading-bot]]`, `[[vibe-trading]]`, and `[[quantdinger]]`

## Traceability updates
- Update `related_sources` on the project page to point to `[[source-tradingagents]]`.
- Preserve raw source files unchanged.
- Keep the source page explicit about what comes from the paper versus what comes from the README companion.

## Review items
1. Should the benchmark numbers be treated as durable knowledge or kept as source-local evidence?
   - Recommendation: keep them source-local / low-confidence for now.
2. Should the README’s v0.2.4 feature snapshot be promoted into the project page, or only referenced in the source page?
   - Recommendation: mention it briefly on the project page, but keep the detailed release-note claims in the source page.

## Integration scope
- Single-source ingest is sufficient, but the source family should update the broader trading cluster and catalog.
- A later `/compile` pass may be useful only if more paper-backed trading-firm sources accumulate.
- No Canvas/Base is required yet.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because it introduces a durable framework-level branch with audit value.
- Create the source page and project page in `wiki/`.
- Update `wiki/overview.md`, `wiki/index.md`, and `wiki/log.md` after integration.
- Create one review-queue item for the benchmark-robustness question.
