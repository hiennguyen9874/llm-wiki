---
title: Ingest Plan - Fincept Terminal
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-fincept-terminal]]
  - [[fincept-terminal]]
  - [[tradingview-mcp]]
  - [[quantdinger]]
  - [[vibe-trading]]
  - [[tradingagents]]
---

# Ingest Plan - Fincept Terminal

## Source identity
- Source file: `raw/apps/FinceptTerminal.md`
- Source type: documentation / project README
- Likely topic domain: financial intelligence platform, desktop trading terminal, AI-assisted analytics, data connectors, broker integrations, quantitative analysis
- Why it matters to `purpose.md`: this source adds a cohesive, production-style financial terminal reference that broadens the trading cluster beyond bot tutorials into a native desktop analytics platform with data connectivity, AI agents, and execution tooling.

## Key entities and relationships
- Fincept Terminal / Fincept Terminal v4 → named desktop app / platform
- Fincept Corporation → publisher / commercial owner
- C++20 + Qt6 + embedded Python → implementation stack
- Data connectors → market, macro, and alternative-data integrations
- Broker integrations → trading execution and brokerage routing
- AI agents → model / persona framework for analysis
- QuantLib suite → quantitative finance modules
- Node editor → visual workflow / automation surface
- Adanos market sentiment → optional alternative-data overlay
- Commercial license / university licensing / community token → commercial and ecosystem context

## Candidate claims
- Fincept Terminal is a pure native C++20 desktop application using Qt6 for UI and embedded Python for analytics.
- The README presents it as a state-of-the-art financial intelligence platform with CFA-level analytics, AI automation, and unlimited data connectivity.
- The project claims 37 AI agents, 100+ data connectors, 16 broker integrations, 18 QuantLib modules, and a node editor for automation pipelines.
- The platform includes real-time crypto / equity / algo / paper trading workflows and a multi-provider LLM setup.
- Recent builds support optional Adanos market sentiment connectivity for alternative-data overlays in equity research.
- The README includes commercial licensing, university licensing, and a community token section; these are source-backed but partly promotional / ecosystem context.
- The project ships as AGPL-3.0 open source with a commercial license option.

## Existing pages likely affected
- `[[fincept-terminal]]` — new project page should capture the durable platform shape.
- `[[source-fincept-terminal]]` — new source page should preserve source traceability and README-level claims.
- `[[tradingview-mcp]]` — adjacent because both connect AI-assisted analysis to trading workflows and terminal-style tooling.
- `[[quantdinger]]` — adjacent because both are broad platform-style quant / trading systems with execution and ops layers.
- `[[vibe-trading]]` — adjacent because both describe integrated agentic trading workspaces.
- `[[tradingagents]]` — adjacent because both broaden the agentic-finance cluster.
- `[[wiki/overview]]` — should note Fincept Terminal as another platform branch in the trading cluster.
- `[[wiki/index]]` — should add the new source and project pages for discoverability.

## New vs reinforced vs uncertain
### New
- A native desktop financial terminal with extensive data connectivity and broker routing joins the wiki as a durable project reference.
- The cluster now includes not only research bots and agent frameworks, but also a Bloomberg-like desktop platform shape.

### Reinforced
- The trading cluster already favors broad platform views; Fincept Terminal strengthens the case for keeping the cluster architecture-level rather than bot-only.
- Native / local-first / non-Electron tooling remains a recurring theme across the trading-related pages.

### Uncertain
- The practical reality of snapshot claims like 37 agents, 100+ connectors, and 16 broker integrations is not independently verified.
- The commercial-license and university-license wording should be preserved as documentation-level claims, not treated as fully validated legal analysis.
- The community token section is notable but secondary; it should stay source-local unless future sources make it more relevant.

## Proposed page actions
### Source page
Create `wiki/source-fincept-terminal.md` with:
- source metadata
- concise summary of the platform and why it matters
- claim blocks for desktop architecture, analytics, data/connectors, broker integrations, AI agents, QuantLib suite, and licensing / community context
- open questions about documentation-level claims versus code-level reality
- related pages linking to the closest trading / platform pages

### Project page
Create `wiki/fincept-terminal.md` with:
- durable summary of the platform as a native financial intelligence terminal
- key capabilities organized by architecture, analytics, data, execution, and visual workflows
- explicit note that the README is promotional and contains snapshot-style counts
- relationships to nearby trading pages

## Traceability updates
- Add `related_sources` on the new project page and source page.
- Preserve the raw README unchanged.
- Keep the source page explicit about which claims are directly from the README versus what is inferred as the durable platform shape.

## Review items
1. Should Fincept Terminal remain a standalone project page, or later anchor a broader `trading-automation` / `financial-terminal` synthesis?
   - Recommendation: keep it standalone for now; it is already a cohesive platform reference.
2. Should the README’s marketing language and snapshot feature counts be softened in downstream pages because they are not independently verified?
   - Recommendation: yes; preserve the claims but label them carefully as source-backed claims.
3. Should the commercial-license and university-license statements be revisited later if code, docs, or external evidence add more detail?
   - Recommendation: yes; treat them as documentation-level claims pending further verification.

## Integration scope
- Single-source ingest is sufficient for the source page, but the project page and overview/index/log updates make this a broad integration task.
- A later `/compile` pass may be warranted if more platform-level financial terminal sources arrive.
- No Canvas or Base is required yet.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because the source introduces a broad, durable trading-platform reference with audit value.
- Create the source page and project page in `wiki/`.
- Update `wiki/overview.md`, `wiki/index.md`, and `wiki/log.md` after integration.
- Create one review-queue item for the synthesis question about whether this should later anchor a broader `trading-automation` or `financial-terminal` page.
