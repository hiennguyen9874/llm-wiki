---
title: tradingview-mcp
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
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
confidence_score: 0.74
quality_score: 0.78
evidence_count: 1
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
`tradingview-mcp` is a local bridge between Claude Code and TradingView Desktop. The source article describes it as a Node.js MCP server plus CLI that lets an LLM inspect chart state, read indicator outputs, and participate in Pine Script development workflows.

## Key points
- Uses TradingView Desktop as the live data source.
- Connects locally through Chrome DevTools Protocol on the Electron app.
- Exposes a `tv` CLI with JSON output and streaming commands.
- Makes chart data, indicator drawings, and strategy results readable to an LLM.
- Supports an AI-in-the-loop Pine Script edit/compile/fix loop.

## Relationships
- `tradingview-mcp` uses [[Claude]] / Claude Code as the agent-side interface.
- `tradingview-mcp` depends on [[TradingView Desktop]].
- `tradingview-mcp` uses [[Chrome DevTools Protocol]] semantics through the Electron debug surface.
- `tradingview-mcp` supports [[Pine Script]] authoring and validation workflows.

## Evidence / claims
#### Claim
- Statement: The tool surfaces chart metadata, OHLC data, indicator drawings, table contents, strategy tester results, and screenshots to the agent.
- Status: active
- Confidence: 0.76
- Evidence: [[source-how-to-connect-claude-to-tradingview]]
- Last confirmed: 2026-04-26
- Notes: Derived from the source article; good candidate for future verification if the repo is used directly.

#### Claim
- Statement: The workflow is local-first, but depends on undocumented internals of TradingView Desktop.
- Status: active
- Confidence: 0.74
- Evidence: [[source-how-to-connect-claude-to-tradingview]]
- Last confirmed: 2026-04-26
- Notes: Keep this caution visible because compatibility may change.

## Open questions
- Should this stay a general topic page, or become part of a broader trading automation cluster if more sources arrive?
- How much of the behavior described in the article has been independently verified?

## Sources
- [[source-how-to-connect-claude-to-tradingview]]
