---
title: Ingest Plan - How to Connect Claude to TradingView
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
source_count: 1
status: draft
retention_class: episodic
visibility: private
source_file: raw/articles/How-to-Connect-Claude-to-TradingView-1.md
source_type: article
related_sources: []
---

# Ingest Plan - How to Connect Claude to TradingView

## Source identity
- Source: X article by Trades Dont Lie about connecting Claude to TradingView via the `tradingview-mcp` GitHub repo and a `tv` CLI.
- Why it matters to `purpose.md`: it is a concrete example of an LLM-in-the-loop workflow that connects a coding agent to a live external application, useful as durable knowledge about agentic tooling, MCP usage, and local-app integration patterns.

## Key entities
- `tradingview-mcp` repository / tool
- TradingView Desktop app
- Claude / Claude Code
- Node.js MCP server
- Chrome DevTools Protocol (CDP)
- `tv` CLI
- Pine Script
- TradingView chart data, drawings, screenshots, strategy tester data

## Candidate claims
- TradingView Desktop can be accessed locally through CDP on port 9222 when launched with debugging enabled.
- The MCP server mediates between Claude Code and TradingView Desktop locally.
- The tooling exposes a `tv` CLI with JSON output and streaming commands.
- Claude can read chart metadata, OHLC data, indicator drawings, tables, strategy tester results, and screenshots.
- The workflow supports Pine Script authoring/compile loops and local validation of indicators.
- The article emphasizes the tool is a research project, uses undocumented internal APIs, and may break when TradingView updates.

## Related existing pages
- No relevant wiki pages found yet via QMD for TradingView, Claude, MCP, Pine Script, Electron, or CDP.
- No existing source pages appear to be present yet.

## Proposed page updates
### New source page
- Create a dedicated source page in `wiki/` for the article with source metadata and a concise claim inventory.

### New canonical topic pages likely warranted
- `tradingview-mcp` or similar topic page for the tool/repository itself.
- `chrome-devtools-protocol` or `electron-debugging` concept page if the vault later accumulates more sources on local-app automation.
- `pine-script-ai-workflow` or similar topic page if this becomes a recurring workflow concept.

## New / reinforced / uncertain
- New: a concrete local MCP-based pattern for connecting an LLM agent to a desktop charting app.
- New: specific `tv` CLI behaviors and the breadth of chart data exposed.
- Reinforced: local-first toolchains and agent-assisted code/test loops.
- Uncertain: long-term stability, exact tool behavior over time, and TradingView ToS implications; keep these as cautions rather than hard claims.

## Traceability
- `related_sources` should be added on any new canonical pages created from this ingest.
- The source page should point back to the article and preserve the GitHub repository link / canonical URL where available.

## Integration strategy
- Treat as a single-source ingest for now, with a lightweight source page plus a small number of topic pages if they add clear reuse value.
- A later `/compile` pass is only warranted if more TradingView / MCP / Pine Script sources accumulate.

## Review items
- Should the repo/tool be treated as a `project`, `tool`, or `topic` page in the wiki? Recommendation: `topic` unless a broader project collection emerges.
- Should the tool page name center `tradingview-mcp` or the broader workflow name? Recommendation: center `tradingview-mcp` because it is the concrete artifact named in the source.
- Should TradingView API / ToS caveats be represented as a caution callout or as a claim block note? Recommendation: caution callout in the source page, with a weaker confidence level on any claims that depend on undocumented internals.

## Downstream artifacts
- No Base or Canvas warranted yet.
- No deep-research prompt warranted yet.
- Update `wiki/index.md` and `wiki/log.md` after page creation if discoverability changes.
