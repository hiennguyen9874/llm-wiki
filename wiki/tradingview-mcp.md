---
title: tradingview-mcp
created: 2026-04-26
last_updated: 2026-04-26
source_count: 6
status: draft
page_type: topic
aliases:
  - TradingView MCP
  - Claude to TradingView
tags:
  - tradingview
  - claude
  - mcp
  - pine-script
  - automation
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-how-to-connect-claude-to-tradingview]]
  - [[source-how-to-connect-claude-to-tradingview-2]]
  - [[source-how-to-use-claude-to-build-tradingview-indicators]]
  - [[source-claude-code-tradingview-live-trading-bot-0dte]]
  - [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]
  - [[source-i-gave-claude-ai-full-access-to-tradingview-the-scalping-strategy-it-built-was-insane]]
confidence_score: 0.84
quality_score: 0.88
evidence_count: 6
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
  - Chrome DevTools Protocol
  - Pine Script
  - Research Backtest Incubate
  - 0DTE options
  - Interactive Brokers
  - Robinhood
  - BlackCat indicators
  - ADX
  - ATR bands
  - Ethereum
---

# tradingview-mcp

## Summary
`tradingview-mcp` is a local bridge between Claude Code and TradingView Desktop. The source articles describe it as a Node.js MCP server plus CLI that lets an LLM inspect chart state, read indicator outputs, stream market data, and participate in Pine Script development workflows.

The second source adds more operational detail about the `tv` CLI surface, streaming JSONL output, and the breadth of chart data the agent can read back.

The third source shows the same bridge can also support prompt-by-prompt Pine Script indicator construction, including open-interest plotting, EMA overlays, fills, and save-to-account persistence.

The fourth source broadens the cluster into live trading bot prototyping and 0DTE research, showing the same TradingView bridge being used as a live system-design surface rather than only as an indicator authoring tool.

The fifth source presents the workflow as a master-prompt, no-terminal demo that can live-read charts, switch assets and timeframes, inspect indicators, and generate custom indicators from plain English. The sixth source shows the bridge can also support multi-indicator strategy construction and backtesting on Ethereum, including timeframe iteration, signal stacking, and optimization around a 30-minute chart.

## Key points
- Uses TradingView Desktop as the live data source.
- Connects locally through Chrome DevTools Protocol on the Electron app.
- Exposes a `tv` CLI with JSON output, status checks, streaming commands, and Pine Script helpers.
- Makes chart data, indicator drawings, tables, strategy results, and screenshots readable to an LLM.
- Supports an AI-in-the-loop Pine Script edit / compile / fix loop.
- Can be used for incremental, prompt-by-prompt indicator construction in TradingView Desktop.
- Can also support multi-indicator strategy construction and backtesting, not just single-indicator editing.
- Can also serve as a live research surface for bot prototyping, broker comparison, and options-trading hypothesis testing.
- A later source presents the workflow as a master-prompt, low-friction setup demo with live chart reading, symbol switching, and plain-English indicator generation.
- The newest source extends the cluster into Ethereum scalping strategy design with BlackCat indicators, ADX, and ATR bands.
- The articles frame the workflow as local-first, but dependent on undocumented TradingView internals.

## Relationships
- `tradingview-mcp` uses Claude Code as the agent-side interface.
- `tradingview-mcp` depends on [[TradingView Desktop]].
- `tradingview-mcp` uses [[Chrome DevTools Protocol]] semantics through the Electron debug surface.
- `tradingview-mcp` supports [[Pine Script]] authoring and validation workflows.

## Evidence / claims
#### Claim
- Statement: The tool surfaces chart metadata, OHLC data, indicator drawings, table contents, strategy tester results, and screenshots to the agent.
- Status: active
- Confidence: 0.80
- Evidence: [[source-how-to-connect-claude-to-tradingview]], [[source-how-to-connect-claude-to-tradingview-2]]
- Last confirmed: 2026-04-26
- Notes: This is the most consistently reinforced capability across both sources.

#### Claim
- Statement: The workflow is local-first, but depends on undocumented internals of TradingView Desktop.
- Status: active
- Confidence: 0.78
- Evidence: [[source-how-to-connect-claude-to-tradingview]], [[source-how-to-connect-claude-to-tradingview-2]]
- Last confirmed: 2026-04-26
- Notes: Keep this caution visible because compatibility may change with TradingView updates.

#### Claim
- Statement: The `tv` CLI supports chart inspection, symbol/timeframe changes, Pine Script compile/analyze/check/save flows, and streaming JSONL output.
- Status: active
- Confidence: 0.79
- Evidence: [[source-how-to-connect-claude-to-tradingview-2]]
- Last confirmed: 2026-04-26
- Notes: The second source gives the clearest command-level description.

#### Claim
- Statement: The `tradingview-mcp` workflow can support incremental, prompt-by-prompt Pine Script indicator construction inside TradingView Desktop, including plotting open interest, adding EMA overlays, and saving the script to the user’s account.
- Status: active
- Confidence: 0.72
- Evidence: [[source-how-to-use-claude-to-build-tradingview-indicators]]
- Last confirmed: 2026-04-26
- Notes: This is demonstrated in one source article; keep it as a usage pattern rather than a universal capability claim.

#### Claim
- Statement: The same TradingView bridge can also support live trading research tasks, including bot prototyping, 0DTE thesis exploration, and broker/platform comparison.
- Status: active
- Confidence: 0.67
- Evidence: [[source-claude-code-tradingview-live-trading-bot-0dte]]
- Last confirmed: 2026-04-26
- Notes: This is a broader operational framing supported by the new livestream summary, but it remains source-local and should not be overgeneralized.

#### Claim
- Statement: A later source presents the workflow as a one-prompt, low-friction setup demo that can read live TradingView chart state and execute chart-control / indicator-generation commands without terminal work.
- Status: active
- Confidence: 0.70
- Evidence: [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]
- Last confirmed: 2026-04-26
- Notes: Treat the speed and “no terminal” framing as a promotional UX claim rather than a universal guarantee.

#### Claim
- Statement: The same bridge can support multi-indicator strategy construction and backtesting on Ethereum, including timeframe iteration and signal stacking around a 30-minute chart.
- Status: active
- Confidence: 0.69
- Evidence: [[source-i-gave-claude-ai-full-access-to-tradingview-the-scalping-strategy-it-built-was-insane]]
- Last confirmed: 2026-04-26
- Notes: Treat this as a demonstrated usage pattern from a source-local demo rather than a validated trading edge.

## Open questions
- Should this stay a general topic page, or become part of a broader trading automation cluster if more sources arrive?
- How much of the behavior described in the sources has been independently verified?
- Which parts of the workflow are stable enough to rely on versus merely demonstrated in the articles?

## Related pages
- [[vibe-trading]]
- [[openclaw-for-tradingview]]
- [[regime-trading-bot]]

## Sources
- [[source-how-to-connect-claude-to-tradingview]]
- [[source-how-to-connect-claude-to-tradingview-2]]
- [[source-how-to-use-claude-to-build-tradingview-indicators]]
- [[source-claude-code-tradingview-live-trading-bot-0dte]]
- [[source-claude-code-tradingview-insane-trading-setup-stocks-crypto]]
