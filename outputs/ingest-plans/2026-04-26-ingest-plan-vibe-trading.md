---
title: Ingest Plan - Vibe-Trading
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-vibe-trading]]
  - [[tradingview-mcp]]
  - [[regime-trading-bot]]
  - [[openclaw-for-tradingview]]
---

# Ingest Plan - Vibe-Trading

## Source identity
- Source file: `raw/apps/Vibe-Trading.md`
- Source type: documentation / project README
- Likely topic domain: trading automation, agentic finance workspace, MCP tooling, multi-agent swarms, backtesting, market-data routing
- Why it matters to `purpose.md`: this source is a broad, durable trading-workspace reference. It adds a self-contained agentic trading platform with CLI/TUI, web UI, MCP server, persistent memory, swarm workflows, and multi-market backtesting.

## Key entities and relationships
- Vibe-Trading → named project / app / platform
- HKUDS → publisher / ecosystem parent
- CLI / TUI → user-facing interactive interface
- FastAPI web server / React frontend → web UI surface
- MCP server → integration layer for Claude Desktop / OpenClaw / Cursor / other clients
- Persistent cross-session memory → reusable memory layer
- Self-evolving skills → skill CRUD / workflow evolution layer
- Swarm presets → multi-agent finance workflows
- Backtest engines → strategy research and validation layer
- Data sources → A-shares, HK/US, crypto, futures, forex
- Multi-platform export → TradingView / TDX / MetaTrader 5 outputs
- Document upload / analyzer → broker exports and report ingestion

## Candidate claims
- The project presents itself as an AI-powered multi-agent finance workspace and personal trading agent.
- It offers a CLI/TUI, FastAPI web server, React frontend, and MCP server.
- It claims persistent cross-session memory, self-evolving skills, FTS5 session search, 5-layer compression, and read/write batching.
- It claims 71 skills across 7 categories and 29 swarm team presets.
- It claims 5 data sources and 7 backtest engines, with cross-market composite testing and statistical validation.
- It can export strategies to TradingView, TDX, and MetaTrader 5.
- It exposes 17 MCP tools, with 16 working without API keys.
- It supports document upload and broker-export analysis.
- The README markets the app as a trading agent, but the disclaimer says it is for research/simulation/backtesting only and does not execute live trades.

## Existing pages likely affected
- `[[tradingview-mcp]]` — the source overlaps with MCP-enabled trading workflows and TradingView export, but should remain a separate topic.
- `[[regime-trading-bot]]` — the source reinforces layered trading-bot architecture, risk gating, and paper-trading-first posture.
- `[[openclaw-for-tradingview]]` — the source sits in the same broader agentic trading research ecosystem.
- `[[wiki/overview]]` — should record Vibe-Trading as a new app/platform branch in the trading cluster.
- `[[wiki/index]]` — should add the new source and project pages for discoverability.

## New vs reinforced vs uncertain
### New
- A broad end-to-end trading workspace exists in the repo: CLI, web UI, MCP, memory, skills, swarms, backtests, and exports.
- The platform integrates document analysis and trading-journal workflows, not just strategy generation.
- The repo explicitly combines research tooling with a non-live-trading disclaimer.

### Reinforced
- The vault already has a trading automation / TradingView / bot cluster; this source strengthens the idea that the cluster should stay broad.
- Risk management and staged validation remain key themes across the trading pages.

### Uncertain
- The practical reliability of the feature counts and marketing claims is not independently validated.
- The README’s “personal trading agent” framing conflicts somewhat with the disclaimer; preserve the tension rather than flattening it.
- It is unclear whether a broader `trading-automation` synthesis page should now be created, or whether the current branch structure is sufficient.

## Proposed page actions
### Source page
Create `wiki/source-vibe-trading.md` with:
- source metadata
- concise summary of the platform
- claim blocks for the app surfaces, memory/skill system, swarm/backtest stack, MCP surface, and disclaimer tension
- open questions about live trading vs research-only framing
- related pages linking to `tradingview-mcp`, `regime-trading-bot`, and `openclaw-for-tradingview`

### Project page
Create `wiki/vibe-trading.md` with:
- durable summary of the platform as an agentic trading workspace
- key capabilities organized by interface, memory, execution, research, and export
- explicit note that the repo positions itself as research/simulation/backtesting rather than live execution
- relationships to nearby trading pages

### Optional future expansion
- If more sources reinforce this ecosystem, consider a broader `trading-automation` synthesis page or Canvas.
- If the repo’s feature counts become a recurring reference point, consider a lighter operational dashboard/Base later.

## Traceability updates
- Add `related_sources` on the new project page and the source page.
- Preserve the raw README unchanged.
- Keep the source page explicit about what comes from the README versus what is inferred as the durable project shape.

## Review items
1. Should Vibe-Trading remain a standalone project page, or should it later be merged into a broader trading-automation synthesis?
   - Recommendation: keep it standalone for now; it is already a cohesive platform and useful anchor page.
2. Should the README’s live-trading marketing language be softened in downstream pages because the disclaimer says research/simulation/backtesting only?
   - Recommendation: yes; preserve both claims and mark the tension explicitly.
3. Should the feature counts (71 skills / 29 swarm presets / 17 MCP tools / 7 engines) be treated as stable facts or as snapshot claims from the README?
   - Recommendation: treat them as snapshot claims unless reinforced by code or another source.

## Integration scope
- Single-source ingest is sufficient for the source page, but the project page and overview/index/log updates make this a broad integration task.
- A later `/compile` pass may be warranted if more platform-repo sources arrive.
- No Canvas/Base is required yet.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because the source introduces a broad trading-platform branch with durable audit value.
- Create the source page and project page in `wiki/`.
- Update `wiki/overview.md`, `wiki/index.md`, and `wiki/log.md` after integration.
- Create one review-queue item for the synthesis-question about whether this should later anchor a broader `trading-automation` page.
