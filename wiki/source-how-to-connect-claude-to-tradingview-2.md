---
title: Source - How to Connect Claude to TradingView 2
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - How to Connect Claude to TradingView (Miles Deutscher)
  - TradingView MCP article 2
  - Miles Deutscher article on TradingView MCP
  - How to Connect Claude to TradingView FULL GUIDE
tags:
  - source
  - tradingview
  - claude
  - mcp
  - pine-script
domain: trading
importance: medium
review_status: active
related_sources: []
confidence_score: 0.76
quality_score: 0.81
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - tradingview-mcp
  - TradingView Desktop
  - Claude Code
  - Chrome DevTools Protocol
  - Pine Script
source_file: raw/articles/How-to-Connect-Claude-to-TradingView-2.md
source_type: article
author: Miles Deutscher
---

# Source - How to Connect Claude to TradingView 2

## What this source is
An X article by Miles Deutscher describing a local MCP-based workflow for connecting Claude Code to TradingView Desktop through the `tradingview-mcp` repository and the `tv` CLI.

## Why it matters
This source reinforces the idea that a coding agent can work against a live desktop charting app as a local data source rather than a screenshot-only interface.
It adds more specific operational detail than the first source, especially around:
- the breadth of chart data exposed to the agent
- the `tv` CLI surface
- AI-assisted Pine Script / indicator validation loops
- multi-pane streaming and replay-style workflows

## Key claims
#### Claim
- Statement: `tradingview-mcp` connects Claude Code to TradingView Desktop through a Node.js MCP server using Chrome DevTools Protocol on localhost.
- Status: active
- Confidence: 0.78
- Evidence: [[source-how-to-connect-claude-to-tradingview-2]]
- Last confirmed: 2026-04-26
- Notes: This is the article’s core technical claim and aligns with the earlier source in the same cluster.

#### Claim
- Statement: The tooling exposes a `tv` CLI with commands for status checks, quotes, OHLCV, symbol/timeframe changes, Pine Script workflows, and streaming JSONL output.
- Status: active
- Confidence: 0.80
- Evidence: [[source-how-to-connect-claude-to-tradingview-2]]
- Last confirmed: 2026-04-26
- Notes: The article gives a concrete CLI command list, making this one of the more actionable claims in the source.

#### Claim
- Statement: The setup can expose chart metadata, live OHLC/volume, indicator drawings, tables, strategy tester data, screenshots, and streaming bar/quote data to the agent.
- Status: active
- Confidence: 0.78
- Evidence: [[source-how-to-connect-claude-to-tradingview-2]]
- Last confirmed: 2026-04-26
- Notes: Treat as article-backed capability reporting rather than independently verified repo behavior.

#### Claim
- Statement: The workflow is local-first, but depends on undocumented TradingView internals and may break when TradingView Desktop updates.
- Status: active
- Confidence: 0.75
- Evidence: [[source-how-to-connect-claude-to-tradingview-2]]
- Last confirmed: 2026-04-26
- Notes: Keep this caution visible because the article explicitly warns about version fragility.

## Entities and relationships
- `tradingview-mcp` uses Claude Code as the agent-side interface.
- `tradingview-mcp` depends on TradingView Desktop.
- TradingView Desktop exposes an Electron/Chromium debug surface through Chrome DevTools Protocol.
- The `tv` CLI supports chart inspection, streaming, and Pine Script workflows.
- Pine Script workflows can use Claude to generate, compile, inspect errors, and revise scripts in a loop.

## Notes
> [!warning]
> The article explicitly warns that the workflow relies on undocumented TradingView internals exposed through the Electron debug interface. Treat stability as version-sensitive, and keep TradingView Desktop updates on a short leash if this workflow is used in practice.

> [!info]
> The article frames this as a research project and says users should reason carefully about TradingView terms of service and their own use of the tooling.

## Open questions
- How stable is the tool across TradingView Desktop releases?
- How much of the CLI/tool breadth has been independently verified in the vault?
- Are there important TradingView terms-of-service constraints for downstream use?

## Related pages
- [[tradingview-mcp]]
- [[source-how-to-connect-claude-to-tradingview]]

## Sources
- Original raw source: `raw/articles/How-to-Connect-Claude-to-TradingView-2.md`
- Linked repository in the article: `https://github.com/tradesdontlie/tradingview-mcp`
