---
title: Source - How to Connect Claude to TradingView
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - How to Connect Claude to TradingView
  - TradingView MCP article
  - Trades Dont Lie article on TradingView MCP
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
confidence_score: 0.78
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
  - tradingview-mcp
  - TradingView Desktop
  - Claude
  - Claude Code
  - Chrome DevTools Protocol
  - Pine Script
source_file: raw/articles/How-to-Connect-Claude-to-TradingView-1.md
source_type: article
author: Trades Dont Lie
---

# Source - How to Connect Claude to TradingView

## What this source is
An X article by Trades Dont Lie describing a local MCP-based workflow for connecting Claude Code to TradingView Desktop through the `tradingview-mcp` repository and a `tv` CLI.

## Why it matters
This source captures a concrete example of an LLM-in-the-loop workflow for a live desktop charting app:
- local access to a running Electron app via Chrome DevTools Protocol
- structured chart inspection through MCP tools and CLI commands
- AI-assisted Pine Script authoring, compile, and validation loops
- local-only data flow, with caveats around undocumented internals and TradingView's terms

## Key claims
#### Claim
- Statement: `tradingview-mcp` connects Claude Code to TradingView Desktop through a Node.js MCP server using Chrome DevTools Protocol on localhost.
- Status: active
- Confidence: 0.78
- Evidence: [[source-how-to-connect-claude-to-tradingview]]
- Last confirmed: 2026-04-26
- Notes: Based on the source article; not independently verified in the vault.

#### Claim
- Statement: The tooling exposes TradingView chart data, indicator drawings, tables, strategy tester data, screenshots, and a JSON/streaming CLI named `tv`.
- Status: active
- Confidence: 0.76
- Evidence: [[source-how-to-connect-claude-to-tradingview]]
- Last confirmed: 2026-04-26
- Notes: The article describes broad access to chart state and a pipe-friendly CLI.

#### Claim
- Statement: The setup is local-first, but it depends on undocumented TradingView internals and may break when TradingView updates.
- Status: active
- Confidence: 0.74
- Evidence: [[source-how-to-connect-claude-to-tradingview]]
- Last confirmed: 2026-04-26
- Notes: Treat as an operational caution, not a guarantee of long-term compatibility.

## Entities and relationships
- `tradingview-mcp` uses `Claude Code`.
- `tradingview-mcp` depends_on `TradingView Desktop`.
- `TradingView Desktop` exposes an Electron/Chromium debug surface through `Chrome DevTools Protocol`.
- `tv` CLI supports chart inspection, streaming, and Pine Script workflows.
- Pine Script workflows can use Claude to generate, compile, inspect errors, and revise scripts in a loop.

## Notes
> [!warning]
> The article explicitly warns that this approach touches undocumented internal TradingView APIs through the Electron debug interface. Stability may change with TradingView updates, so pinning versions matters if the workflow is used in practice.

## Open questions
- How stable is the tool across TradingView Desktop releases?
- How far can chart inspection go before it becomes unreliable or brittle?
- Are there important TradingView terms-of-service constraints for downstream use?

## Related pages
- [[tradingview-mcp]]
- [[source-how-to-use-claude-to-build-tradingview-indicators]]

## Sources
- Original raw source: `raw/articles/How-to-Connect-Claude-to-TradingView-1.md`
- Linked repository in the article: `https://github.com/tradesdontlie/tradingview-mcp`
