---
title: tradingview-mcp
created: 2026-04-26
last_updated: 2026-04-26
source_count: 2
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
confidence_score: 0.80
quality_score: 0.85
evidence_count: 2
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
---

# tradingview-mcp

## Summary
`tradingview-mcp` is a local bridge between Claude Code and TradingView Desktop. The source articles describe it as a Node.js MCP server plus CLI that lets an LLM inspect chart state, read indicator outputs, stream market data, and participate in Pine Script development workflows.

The second source adds more operational detail about the `tv` CLI surface, streaming JSONL output, and the breadth of chart data the agent can read back.

## Key points
- Uses TradingView Desktop as the live data source.
- Connects locally through Chrome DevTools Protocol on the Electron app.
- Exposes a `tv` CLI with JSON output, status checks, streaming commands, and Pine Script helpers.
- Makes chart data, indicator drawings, tables, strategy results, and screenshots readable to an LLM.
- Supports an AI-in-the-loop Pine Script edit / compile / fix loop.
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

## Open questions
- Should this stay a general topic page, or become part of a broader trading automation cluster if more sources arrive?
- How much of the behavior described in the sources has been independently verified?
- Which parts of the workflow are stable enough to rely on versus merely demonstrated in the articles?

## Sources
- [[source-how-to-connect-claude-to-tradingview]]
- [[source-how-to-connect-claude-to-tradingview-2]]
