---
title: Source - Hummingbot
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - Hummingbot README
  - Hummingbot documentation
  - Hummingbot repo README
tags:
  - source
  - trading
  - crypto
  - bot
  - automation
  - python
  - connectors
domain: trading
importance: medium
review_status: active
related_sources:
  - [[hummingbot]]
confidence_score: 0.86
quality_score: 0.83
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Hummingbot
  - Gateway
  - Condor
  - Hummingbot API
  - Hummingbot MCP
  - Quants Lab
  - exchange connectors
  - CLOB CEX
  - CLOB DEX
  - AMM DEX
  - Docker
  - Apache 2.0
  - community governance
source_file: raw/apps/hummingbot.md
source_type: documentation
author: Hummingbot contributors
canonical_url: https://github.com/hummingbot/hummingbot
---

# Source - Hummingbot

## What this source is
A project README / documentation snapshot for Hummingbot, an open-source framework for designing and deploying automated trading strategies across centralized and decentralized exchanges.

## Why it matters
This source adds a more connector-centric trading-bot reference to the wiki's trading cluster. It is useful because it covers:
- exchange connector taxonomy
- DEX middleware via Gateway
- community ecosystem repos around the core project
- installation, help, and contribution pathways
- a documentation-level scale / adoption claim

## Key claims
#### Claim
- Statement: Hummingbot is an open-source framework that helps design and deploy automated trading strategies on centralized and decentralized exchanges.
- Status: active
- Confidence: 0.95
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: This is the source's opening identity statement.

#### Claim
- Statement: The project groups connectors into CLOB CEX, CLOB DEX, and AMM DEX categories.
- Status: active
- Confidence: 0.92
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: This connector taxonomy is one of the source's main durable takeaways.

#### Claim
- Statement: Gateway provides standardized middleware for AMM / DEX connectivity.
- Status: active
- Confidence: 0.90
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: Keep this as the core architectural idea around decentralized exchange access.

#### Claim
- Statement: The README presents a broader ecosystem of related repos, including Condor, Hummingbot API, Hummingbot MCP, Quants Lab, Gateway, and the site docs repo.
- Status: active
- Confidence: 0.89
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: This ecosystem view is useful when connecting the project to adjacent tools.

#### Claim
- Statement: The README says users have generated over $34 billion in trading volume across 140+ unique venues.
- Status: active
- Confidence: 0.78
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: This is a source-side adoption/scale claim and should be treated as documentation/marketing material unless independently verified.

## Relationships
- `Hummingbot` uses exchange connectors to run strategies across venues.
- `Hummingbot` depends on `Gateway` for DEX / AMM middleware use cases.
- `Condor`, `Hummingbot API`, `Hummingbot MCP`, and `Quants Lab` extend the ecosystem around the core project.
- `Hummingbot` is adjacent to [[freqtrade]], [[regime-trading-bot]], [[quantdinger]], [[vibe-trading]], and [[tradingagents]] in the broader trading-automation cluster.

## Notes
> [!info]
> The durable lesson here is architectural: a trading framework becomes more reusable when execution, control, and middleware are separated cleanly.

> [!warning]
> Exchange lists, venue counts, and ecosystem details are documentation snapshots. Treat them as current until contradicted by newer upstream evidence.

## Related pages
- [[hummingbot]]
- [[freqtrade]]
- [[regime-trading-bot]]
- [[quantdinger]]
- [[vibe-trading]]
- [[tradingagents]]

## Open questions
- Does Hummingbot deserve a broader synthesis page if more classic bot sources arrive?
- Which connector or ecosystem claims need future verification against upstream docs?
