---
title: Hummingbot ingest plan
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
tags:
  - ingest
  - trading
  - crypto
  - bot
  - automation
related_sources:
  - [[source-hummingbot]]
visibility: private
retention_class: working
---

# Hummingbot ingest plan

## Source identity
- Source file: `raw/apps/hummingbot.md`
- Source type: documentation / README
- Canonical URL: `https://github.com/hummingbot/hummingbot`
- Subject: open-source Python framework for designing and deploying automated trading bots across centralized and decentralized exchanges.

## Why it matters
Hummingbot adds a broader, connector-centric trading-bot reference to the wiki's trading-automation cluster. It complements the existing classic bot pages by emphasizing:
- multi-venue exchange connectors
- CLOB CEX / CLOB DEX / AMM DEX categorization
- Gateway middleware for DEX access
- community governance and ecosystem repos
- documentation-level claims about scale and adoption

## Key entities and relationships
- `Hummingbot` — open-source automated trading framework
- `Gateway` — middleware for standardized DEX connectivity
- `Condor` — Telegram bot interface repo
- `Hummingbot API` — central hub for running bots
- `Hummingbot MCP` — AI-assistant integration repo
- `Quants Lab` — notebooks for research and data fetches
- `exchange connectors` — the main operational surface
- `CLOB CEX`, `CLOB DEX`, `AMM DEX` — connector classes

Typed relationships:
- `Hummingbot` uses exchange connectors to run strategies across venues
- `Hummingbot` depends on `Gateway` for AMM / DEX middleware use cases
- `Condor`, `Hummingbot API`, `Hummingbot MCP`, and `Quants Lab` extend the ecosystem around the core project
- `Hummingbot` is adjacent to [[freqtrade]], [[regime-trading-bot]], [[quantdinger]], [[vibe-trading]], and [[tradingagents]] in the broader trading-automation cluster

## Candidate claims
1. Hummingbot is an open-source framework for designing and deploying automated trading strategies on centralized and decentralized exchanges.
2. The project is Apache 2.0 licensed and emphasizes a public, community-driven codebase.
3. Hummingbot groups connectors into CLOB CEX, CLOB DEX, and AMM DEX categories, with Gateway for DEX middleware.
4. The README highlights a large ecosystem of related repos: Condor, Hummingbot API, Hummingbot MCP, Quants Lab, Gateway, and the site docs repo.
5. The docs present Hummingbot as a mature bot platform with installation, help, contribution, and governance pathways.

## What is new / reinforced / uncertain
### New
- Adds a broad connector and middleware perspective to the trading cluster.
- Adds an ecosystem view: not only the bot core, but the surrounding repos and support surfaces.

### Reinforced
- Safe-first, documentation-first trading automation patterns.
- The value of separating strategy, execution, control, and infrastructure layers.

### Uncertain
- The market-volume / venue-count marketing claim is source-backed but still a README snapshot, so it should remain high-level.
- Whether Hummingbot should remain a standalone project page or later anchor a broader `trading-automation` synthesis if more classic bot sources arrive.

## Proposed edits
### Source page
Create `[[source-hummingbot]]` with source metadata, claims, relationships, and open questions.

### Canonical page
Create `[[hummingbot]]` as the durable project page summarizing the framework, connector taxonomy, ecosystem repos, and operational posture.

### Related pages to update
- `[[overview]]`
- `[[index]]`
- `[[log]]`
- likely `[[freqtrade]]` for adjacency, since both are classic bot references

## Traceability
- Add `related_sources: [[source-hummingbot]]` to `[[hummingbot]]`
- Keep `related_sources: []` or source-local support on `[[source-hummingbot]]`

## Scope recommendation
- Treat this as a single-source ingest for now.
- Do not trigger `/compile` yet; the source fits the existing trading cluster without requiring a broader synthesis merge.

## Review items
- `approve_edit`: Decide later whether Hummingbot should remain a standalone project page or eventually fold into a broader `trading-automation` synthesis.
- `deep_research`: Optional future follow-up if the ecosystem repos or connector lists need verification against current upstream docs.

## Outputs / visuals
- No Canvas or Base needed now.
- No durable standalone analysis needed beyond this plan and the source/project pages.

## Human judgment
No high-stakes taxonomy or destructive change required.
Proceed with normal source integration.
