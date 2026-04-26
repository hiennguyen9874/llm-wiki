---
title: LLM and Agent Ideas in the Current Wiki for Finance and Stocks
created: 2026-04-26
last_updated: 2026-04-26
status: draft
page_type: synthesis
aliases:
  - Wiki survey of LLMs and agents in finance and stock
  - Finance and stock agent ideas report
  - Trading automation wiki survey
tags:
  - llm
  - agents
  - finance
  - stocks
  - trading
  - backtesting
  - automation
domain: trading
importance: medium
review_status: active
related_sources:
  - [[tradingview-mcp]]
  - [[regime-trading-bot]]
  - [[moondev]]
  - [[openclaw-for-tradingview]]
  - [[prediction-market-trading]]
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
confidence_score: 0.80
quality_score: 0.84
evidence_count: 12
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: durable
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Claude Code
  - TradingView Desktop
  - Pine Script
  - Polymarket
  - MoonDev
  - HMM
  - Alpaca
  - Interactive Brokers
  - OpenRouter
---

# LLM and Agent Ideas in the Current Wiki for Finance and Stocks

## Scope
This report surveys the current wiki only. It does **not** add outside research.

The current corpus is heavily concentrated in **trading, market data, backtesting, and automation**. It has relatively little on broader finance topics such as valuation, accounting, portfolio construction, or corporate finance.

## Executive summary
The wiki’s finance/stock ideas cluster around one core pattern:

> use LLMs and agents as **research copilots, UI operators, code generators, and strategy triage tools**, while keeping risk controls, validation, and final judgment outside the model.

The strongest recurring themes are:
- LLM-to-TradingView workflows for live chart inspection and Pine Script iteration ([[tradingview-mcp]], [[source-how-to-connect-claude-to-tradingview]], [[source-how-to-connect-claude-to-tradingview-2]], [[source-how-to-use-claude-to-build-tradingview-indicators]])
- live trading-bot prototyping and regime-based automation ([[source-claude-code-tradingview-live-trading-bot-0dte]], [[regime-trading-bot]], [[source-how-to-actually-build-a-trading-bot-with-claude-code]])
- backtest-heavy idea generation and robustness filtering ([[source-gpt-55-traded-for-me-and-made-54597-percent]], [[openclaw-for-tradingview]], [[moondev]])
- prediction-market scanning, consensus, and post-trade analysis ([[prediction-market-trading]], [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]], [[source-polymarket-5-min-claude-code-bot-are-nuts]], [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]])

## Main idea clusters

### 1) LLM as a live chart copilot
**Facts:** `tradingview-mcp` connects Claude Code to TradingView Desktop through a local MCP / CDP bridge and exposes chart metadata, OHLCV, indicator drawings, tables, strategy tester data, screenshots, and streaming commands. The source pages also show prompt-by-prompt indicator creation and master-prompt chart control ([[tradingview-mcp]], [[source-how-to-connect-claude-to-tradingview]], [[source-how-to-connect-claude-to-tradingview-2]], [[source-how-to-use-claude-to-build-tradingview-indicators]], [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]).

**Inference:** In this wiki, the LLM is being used less as a chatbot and more as an **operator** for a live charting environment. The model is asked to inspect, change, compare, and iterate on chart state.

**Practical use pattern:**
- inspect live chart context
- switch symbols/timeframes
- add/remove indicators
- generate or revise Pine Script
- save the final script back to TradingView

### 2) LLM as indicator author and Pine Script assistant
**Facts:** The TradingView sources show Claude generating indicators from natural language, including open-interest plotting, EMA overlays, and save-to-account persistence ([[source-how-to-use-claude-to-build-tradingview-indicators]]). The master-prompt demo extends this to more polished setup and chart control for stocks and crypto ([[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]).

**Inference:** The reusable pattern is **incremental coauthoring**: one prompt, one change, one verification step. That is much more robust than asking an LLM to produce a full strategy in one shot.

**Practical use pattern:**
- start from a narrow indicator idea
- ask the model for a small code change
- verify it visually on the chart
- repeat until the indicator is usable

### 3) LLM as a trading-bot architecture scaffold
**Facts:** The wiki’s automated-bot branch describes a five-part bot architecture: brain, allocation, safety, brokerage, dashboard. The `brain` is HMM-based regime detection; the `safety` layer can veto or stop trading; Alpaca is the initial broker; paper trading is recommended before live deployment ([[regime-trading-bot]], [[source-how-to-actually-build-a-trading-bot-with-claude-code]]).

The livestream summary also adds a bot-first trading philosophy, the RBI loop (`Research → Backtest → Incubate`), and a 0DTE thesis explored through TradingView and adjacent data sources ([[source-claude-code-tradingview-live-trading-bot-0dte]]).

**Inference:** The model is being used to **scaffold the system**, not to own the whole system. The durable design rule is to keep risk controls, validation, and deployment gates separate from the model’s output.

**Practical use pattern:**
- let the LLM draft the system structure
- use a regime classifier or other signal layer
- enforce independent risk rules
- paper trade before live capital

### 4) LLM as a backtest amplifier and idea generator
**Facts:** The liquidation-data comparison source pits GPT-5.5 High against Claude Opus 4.7, with five-agent expansion and heavy attention to overfit risk. The OpenClaw workflow turns TradingView community indicators into Python backtests and logs metrics like ROI, drawdown, Sharpe, Sortino, EV, and trade count. MoonDev appears as the recurring data/tooling layer behind several of these experiments ([[source-gpt-55-traded-for-me-and-made-54597-percent]], [[openclaw-for-tradingview]], [[moondev]]).

**Inference:** The LLM is useful here as a **candidate generator and triage layer**. It helps create many hypotheses quickly, but the wiki consistently treats headline backtest results as suspicious until robustness checks pass.

**Practical use pattern:**
- generate several candidate strategies
- backtest quickly on available data
- reject obvious overfit results
- only promote candidates that survive robustness review

### 5) LLM as a prediction-market scanner and analyst
**Facts:** The prediction-market branch uses multiple models to scan Polymarket, vote `yes` / `no` / `no trade`, and aggregate consensus. A second source adds short-interval backtesting with 1-minute data and tick-level CVD work. A third source adds keyword-filtered P&L analysis for trade history review ([[prediction-market-trading]], [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]], [[source-polymarket-5-min-claude-code-bot-are-nuts]], [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]).

**Inference:** The same LLM/agent pattern extends beyond stock charts into event markets, but the task shifts from technical-analysis signals to **signal ranking, filtering, and retrospective analysis**.

**Practical use pattern:**
- scan markets
- filter noise by category, trade size, or price band
- aggregate multiple model opinions
- backtest with higher-resolution data when possible
- review P&L by keyword or time window

## Cross-cutting patterns
These are the most reusable patterns I see across the current wiki:

1. **LLM as interface layer** — the model talks to charting or market tooling ([[tradingview-mcp]], [[prediction-market-trading]]).
2. **LLM as code generator** — the model writes Pine Script, Python backtests, or bot scaffolding ([[source-how-to-use-claude-to-build-tradingview-indicators]], [[openclaw-for-tradingview]], [[source-how-to-actually-build-a-trading-bot-with-claude-code]]).
3. **LLM as hypothesis expander** — multiple agents/models generate candidate strategies or votes ([[source-gpt-55-traded-for-me-and-made-54597-percent]], [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]).
4. **Human or hard-rule risk gate** — the model does not get final authority over deployment, exposure, or stopping conditions ([[regime-trading-bot]], [[source-how-to-actually-build-a-trading-bot-with-claude-code]]).
5. **Validation loop matters more than the model name** — the wiki repeatedly warns that strong-looking results may be overfit, promotional, or source-local ([[source-gpt-55-traded-for-me-and-made-54597-percent]], [[source-i-gave-claude-ai-full-access-to-tradingview-the-scalping-strategy-it-built-was-insane]], [[source-polymarket-5-min-claude-code-bot-are-nuts]]).

## Fact vs inference
### Supported facts
- There is a real TradingView-Claude bridge page and multiple source pages describing it ([[tradingview-mcp]], [[source-how-to-connect-claude-to-tradingview]], [[source-how-to-connect-claude-to-tradingview-2]], [[source-how-to-use-claude-to-build-tradingview-indicators]], [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]).
- There is a regime-based bot architecture with explicit risk controls and paper-trading guidance ([[regime-trading-bot]], [[source-how-to-actually-build-a-trading-bot-with-claude-code]]).
- There are backtest and robustness-oriented workflows using liquidation data and TradingView community indicators ([[source-gpt-55-traded-for-me-and-made-54597-percent]], [[openclaw-for-tradingview]], [[moondev]]).
- There is a separate Polymarket / prediction-market branch with consensus scanning, short-interval backtests, and P&L tracking ([[prediction-market-trading]], [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]], [[source-polymarket-5-min-claude-code-bot-are-nuts]], [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]).

### Inferences
- The wiki is converging on a broader **trading automation** cluster rather than separate one-off demos.
- The most durable use of LLMs here is **research acceleration plus orchestration**, not autonomous trading without human oversight.
- Stock/finance coverage is still narrow: it is mostly technical trading and prediction markets, not broader investing or financial analysis.

## Gaps and next likely syntheses
- The corpus would benefit from a broader **trading-automation** synthesis page if more sources arrive.
- The tradingview branch may deserve a canonical page hierarchy for setup, indicator authoring, and live research.
- The Polymarket branch may eventually need a split between scanning, backtesting, and P&L analytics if it keeps growing.
- There is very little on non-trading finance topics, so if that area matters, it needs new sources.

## Bottom line
The current wiki suggests one clear operating model:

> Use LLMs and agents to **see the market, generate code, compare strategies, and organize experiments**; keep **risk, validation, and deployment judgment** outside the model.

That is the strongest durable idea in the current corpus.

## Pages used
- [[wiki/overview]] and [[wiki/index]] for orientation
- [[tradingview-mcp]]
- [[regime-trading-bot]]
- [[moondev]]
- [[openclaw-for-tradingview]]
- [[prediction-market-trading]]
- [[source-how-to-connect-claude-to-tradingview]]
- [[source-how-to-connect-claude-to-tradingview-2]]
- [[source-how-to-use-claude-to-build-tradingview-indicators]]
- [[source-claude-code-tradingview-live-trading-bot-0dte]]
- [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]
- [[source-gpt-55-traded-for-me-and-made-54597-percent]]
- [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
- [[source-i-gave-claude-ai-full-access-to-tradingview-the-scalping-strategy-it-built-was-insane]]
- [[source-i-let-ai-agents-trade-polymarket-for-24-hours-the-results-are-insane]]
- [[source-polymarket-5-min-claude-code-bot-are-nuts]]
- [[source-this-ai-bot-trades-polymarket-24-7-while-i-sleep-full-claude-code-build]]
