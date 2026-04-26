---
title: Ingest Plan - How to Connect Claude to TradingView 2
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
source_count: 1
status: draft
retention_class: episodic
visibility: private
source_file: raw/articles/How-to-Connect-Claude-to-TradingView-2.md
source_type: article
related_sources: []
---

# Ingest Plan - How to Connect Claude to TradingView 2

## Source identity
- Source: X article by Miles Deutscher describing a TradingView + Claude workflow built around the `tradingview-mcp` repo, the `tv` CLI, and TradingView Desktop.
- Why it matters to `purpose.md`: it reinforces a concrete LLM-in-the-loop workflow for live charting and agent-assisted trading research, adding a second source to the existing TradingView-Claude cluster.

## Key entities
- Miles Deutscher (author / curator of the article)
- `tradingview-mcp` repository / tool
- TradingView Desktop app
- Claude / Claude Code
- Node.js MCP server
- Chrome DevTools Protocol / Electron debug surface
- `tv` CLI
- Pine Script
- TradingView chart data, drawings, screenshots, strategy tester data, alerts, watchlists

## Candidate claims
- Claude Code can be connected locally to TradingView Desktop through a Node.js MCP server plus the `tv` CLI.
- The article claims the setup exposes live chart data, indicator values, drawings, tables, strategy tester outputs, screenshots, and streaming JSONL data.
- The article claims the workflow is local-first and does not send data to TradingView servers, but depends on undocumented internals and TradingView Desktop debug access.
- The article claims the tooling supports AI-assisted Pine Script development, indicator validation, replay logging, and multi-pane streaming workflows.
- The article recommends using the setup for high-leverage tasks rather than low-value UI automation, because permission prompts and token usage can make simple tasks inefficient.

## Related existing pages
- [[source-how-to-connect-claude-to-tradingview]] — first source page for the same TradingView-Claude workflow cluster.
- [[tradingview-mcp]] — canonical topic page for the tool/workflow.
- [[wiki/overview.md]] — current overview already references the first source/topic pair.

## What is new, reinforced, uncertain
- New:
  - A second source on the same workflow cluster.
  - More detailed `tv` CLI command coverage and a claim of 78 MCP tools.
  - Stronger framing around local-only operation, protected indicators, and replay/streaming workflows.
- Reinforced:
  - Local MCP-based LLM integration with TradingView Desktop.
  - AI-assisted Pine Script and chart analysis loops.
  - Stability caveats around undocumented TradingView internals.
- Uncertain:
  - The exact breadth of the toolset in practice.
  - How much of the article’s capability list is verified versus aspirational.
  - TradingView ToS implications for downstream use.

## Proposed page updates
### New source page
- Create a dedicated source page in `wiki/` for this article with source metadata, a concise claim inventory, and traceable references back to the raw file.

### Canonical topic page updates
- Update [[tradingview-mcp]] to reflect that the topic now has a second source.
- Refresh `source_count`, `related_sources`, and evidence/confidence metadata.
- Add or refine claim blocks for CLI breadth, local-first operation, and AI-assisted Pine Script / streaming workflows.

### Overview / catalog updates
- Update [[wiki/overview.md]] if needed to reflect the second source in the TradingView-Claude cluster.
- Update `wiki/index.md` to include the new source page.
- Append `wiki/log.md` with a short ingest note.

## Traceability
- `related_sources` should be updated on the canonical topic page to include both source pages.
- The new source page should preserve the raw file path in `source_file` and keep the article content attributable to the original source.

## Integration strategy
- Treat this as an incremental ingest, not a full `/compile` pass.
- The source adds reinforcement to an existing topic cluster rather than forcing a new taxonomy.
- A later `/compile` pass would only be warranted if more TradingView / MCP / Pine Script sources accumulate.

## Review items
- No high-stakes taxonomy or deletion decisions identified.
- Keep the standalone `tradingview-mcp` topic page for now. Recommendation: approve.
- Keep ToS / undocumented-internals caveats visible, but do not overstate them beyond the article’s own wording.

## Downstream artifacts
- No Base or Canvas warranted yet.
- No deep-research prompt warranted yet.
- A review-queue item already exists for the topic scope question; it can remain as the decision record.
