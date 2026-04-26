---
title: Ingest Plan - How to Use Claude to Build TradingView Indicators
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
source_count: 1
status: draft
retention_class: episodic
visibility: private
source_file: raw/articles/How-to-Use-Claude-to-Build-TradingView-Indicators.md
source_type: article
related_sources: []
---

# Ingest Plan - How to Use Claude to Build TradingView Indicators

## Source identity
- Source: X article by Koroush AK describing how to use Claude Code and TradingView Desktop to build a TradingView indicator incrementally, using `tradingview-mcp` as the bridge.
- Why it matters to `purpose.md`: it adds a concrete, reusable example of prompt-by-prompt agentic indicator authoring, expanding the existing TradingView-Claude cluster from connection/setup into actual scripted output and trading interpretation.

## Key entities
- Koroush AK (author / curator of the article)
- `tradingview-mcp` repository / tool
- TradingView Desktop app
- Claude / Claude Code
- Pine Script v6
- Open Interest (`_OI` symbol suffix)
- EMA overlays, fill regions, chart panes, and indicator settings
- `BINANCE:BTCUSDT.P` as a fallback symbol for OI availability
- The `ZCT Momentum Filter` example indicator

## Candidate claims
- Claude Code can be used in an incremental, one-prompt-one-change loop to build a TradingView indicator.
- The example indicator plots dollar-denominated open interest, adds 60- and 240-period EMAs, shades the gap between them, and exposes the EMA lengths as settings.
- The article recommends saving injected scripts in Pine Editor because the Claude injection itself is session-only.
- The article interprets OI/EMA behavior as breakout, breakdown, and reversal regimes.
- The workflow depends on TradingView Desktop, permissions prompts, and a live debug/injection bridge; it is not instant or frictionless.

## Related existing pages
- [[source-how-to-connect-claude-to-tradingview]] — first TradingView-Claude source page.
- [[source-how-to-connect-claude-to-tradingview-2]] — second TradingView-Claude source page.
- [[tradingview-mcp]] — canonical topic page for the bridge/workflow.
- [[wiki/overview.md]] — current overview already tracks the TradingView-Claude cluster.

## What is new, reinforced, uncertain
- New:
  - A concrete indicator-building walkthrough rather than only connection/setup.
  - Prompt-by-prompt incremental Pine Script editing with visible verification steps.
  - A specific open-interest momentum indicator example and usage heuristics.
- Reinforced:
  - The `tradingview-mcp` local bridge and Claude Code interaction pattern.
  - Pine Script authoring / compile / revise loops.
  - The need to keep TradingView Desktop debug/injection caveats visible.
- Uncertain:
  - Whether the indicator logic generalizes cleanly to other market symbols.
  - How much of the article’s workflow has been independently verified in-vault.
  - TradingView ToS / stability implications for real-world use.

## Proposed page updates
### New source page
- Create a dedicated source page in `wiki/` for the article with source metadata, a concise claim inventory, and traceable references back to the raw file.

### Canonical topic page updates
- Update [[tradingview-mcp]] to reflect that the TradingView-Claude cluster now has a third source.
- Refresh `source_count`, `related_sources`, and evidence/confidence metadata.
- Add or refine a claim about prompt-by-prompt Pine Script indicator construction.

### Overview / catalog updates
- Update [[wiki/overview.md]] if needed to reflect the expanded TradingView-Claude cluster.
- Update `wiki/index.md` to include the new source page.
- Append `wiki/log.md` with a short ingest note.

## Traceability
- Preserve `source_file: raw/articles/How-to-Use-Claude-to-Build-TradingView-Indicators.md` on the new source page.
- Update `related_sources` on `[[tradingview-mcp]]` to include the new source page.
- Keep claims about undocumented internals and session-only injection explicitly caveated rather than flattened into certainty.

## Integration strategy
- Treat this as an incremental ingest, not a full `/compile` pass.
- The source adds reinforcement to an existing TradingView-Claude cluster rather than forcing a new taxonomy.
- A later `/compile` pass is only warranted if more indicator-building or Pine Script workflow sources accumulate.

## Review items
- No high-stakes taxonomy or deletion decisions identified.
- No ask-user gate needed.
- If more sources appear, consider whether a dedicated Pine Script workflow synthesis page becomes worthwhile.

## Downstream artifacts
- No Base or Canvas warranted yet.
- No deep-research prompt warranted yet.
- Update `wiki/index.md` and `wiki/log.md` after page creation if discoverability changes.
