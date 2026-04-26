---
title: Ingest Plan - Claude Code + TradingView Insane Trading Setup (Stocks & Crypto)
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
source_count: 1
status: draft
retention_class: episodic
visibility: private
source_file: raw/articles/claude-code-tradingview-insane-trading-setup-stocks-crypto.md
source_type: transcript
related_sources: []
---

# Ingest Plan - Claude Code + TradingView Insane Trading Setup (Stocks & Crypto)

## Source identity
- Source: YouTube transcript / article-style marketing demo about using Claude Code with TradingView through the `tradingview-mcp` bridge.
- Why it matters to `purpose.md`: it reinforces the existing TradingView-Claude cluster with a more polished, no-code / one-prompt framing that demonstrates live chart control, multi-timeframe analysis, and custom indicator generation.

## Key entities
- Claude Code / Claude
- TradingView Desktop
- `tradingview-mcp`
- Master prompt / setup prompt
- Chrome DevTools Protocol / live debug port
- `tv` CLI / chart-control surface
- Pine Script
- Indicators: RSI, Bollinger Bands, MACD, EMA
- Asset/timeframe switching, screenshots, indicator analysis, custom indicator generation

## Candidate claims
- A single master prompt can clone the repo, configure the MCP bridge, create the rules JSON, enable a 12-hour update flow, and launch TradingView with debug access.
- The workflow is presented as requiring only a small number of confirmations and roughly a few minutes to set up.
- Claude reads the live TradingView chart at the code/data level rather than from a screenshot, so the chart data is current instead of stale pixels.
- The setup exposes commands for switching symbols/timeframes, adding/removing indicators, taking screenshots, reading current indicator values, comparing multiple timeframes, comparing multiple assets, and generating a custom indicator from plain English.
- The source is highly promotional and should be treated as a capability demo plus marketing rather than as independently verified documentation.

## Related existing pages
- [[tradingview-mcp]] — canonical topic page for the bridge/workflow.
- [[source-how-to-connect-claude-to-tradingview]] — first setup/connection source.
- [[source-how-to-connect-claude-to-tradingview-2]] — second setup/connection source with more CLI detail.
- [[source-how-to-use-claude-to-build-tradingview-indicators]] — indicator-building source in the same cluster.
- [[source-claude-code-tradingview-live-trading-bot-0dte]] — live-trading / research branch of the same cluster.

## What is new, reinforced, uncertain
### New
- A more polished, promotional setup demo centered on a master prompt.
- Strong no-terminal / no-coding / under-4-minutes positioning.
- Specific live command examples: chart switching, screenshots, indicator queries, multi-timeframe comparison, multi-asset ranking, and custom indicator generation.

### Reinforced
- `tradingview-mcp` as a local bridge between Claude Code and TradingView Desktop.
- AI-assisted Pine Script and chart-analysis workflows.
- The cluster’s move from simple connection setup toward practical trading work surfaces.

### Uncertain
- How much of the “one prompt, no terminal” framing is truly zero-setup versus hidden operational complexity.
- Whether the 12-hour update feature and the more advanced command set are stable across versions.
- Whether the video’s speed claims should be generalized beyond the demo environment.

## Proposed page actions
### Source page
Create a dedicated source page in `wiki/` with:
- source metadata
- concise summary of the demo
- claim blocks for the master-prompt setup, live chart reading, and action surface
- a caution callout on promotional framing / unverified speed claims
- related pages pointing to the existing TradingView-Claude cluster

### Canonical topic update
Update `[[tradingview-mcp]]` to reflect the new source and the no-terminal / master-prompt framing.

### Overview / catalog updates
- Update `[[wiki/overview.md]]` if needed to note the fifth TradingView-Claude source.
- Update `wiki/index.md` to include the new source page.
- Append `wiki/log.md` with a short ingest note.

## Traceability
- Preserve `source_file: raw/articles/claude-code-tradingview-insane-trading-setup-stocks-crypto.md` on the new source page.
- Update `related_sources` on `[[tradingview-mcp]]` to include the new source page.
- Keep the source’s promotional nature explicit so later compilation does not overstate certainty.

## Integration strategy
- Treat as a single-source incremental ingest, not a full `/compile` pass.
- This source reinforces an existing topic cluster rather than forcing a taxonomy change.
- A later `/compile` pass becomes interesting only if more setup/demo sources accumulate.

## Review items
- Should the “master prompt / under-4-minutes” framing remain source-local or get a small topic-level note? Recommendation: keep it topic-level only as a low-confidence UX demo claim.
- Should future sources about setup prompts become a separate prompt-setup synthesis page? Recommendation: defer until there is more than one durable example.
- No high-stakes taxonomy, privacy, or deletion decisions identified.

## Downstream artifacts
- No Base or Canvas warranted yet.
- No deep-research prompt warranted yet.
- Update `wiki/index.md` and `wiki/log.md` after page creation if discoverability changes.
