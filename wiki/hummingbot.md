---
title: Hummingbot
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - Hummingbot project
  - Hummingbot trading framework
  - Hummingbot crypto trading bot
tags:
  - trading
  - crypto
  - bot
  - automation
  - connectors
  - python
  - finance
domain: trading
importance: medium
review_status: active
related_sources:
  - [[source-hummingbot]]
confidence_score: 0.81
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: durable
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
---

# Hummingbot

## Summary
Hummingbot is an open-source Python trading framework for designing and deploying automated strategies across centralized and decentralized exchanges.

Its durable value is architectural breadth: the project is not just a bot, but a connector ecosystem with clear categories for CLOB CEX, CLOB DEX, and AMM DEX access, plus Gateway middleware and several adjacent repos for control, APIs, notebooks, AI-assistant integration, and documentation.

## Key capabilities
### Trading and connectivity
- exchange connectors across centralized and decentralized venues
- connector taxonomy for CLOB CEX, CLOB DEX, and AMM DEX use cases
- Gateway middleware for DEX / AMM access
- installation and deployment guidance for local setups

### Ecosystem and operations
- Condor Telegram interface repo
- Hummingbot API for running bots
- Hummingbot MCP for AI assistant integration
- Quants Lab notebooks for research and data work
- docs and governance pathways for contributors

### Durable operational posture
- Apache 2.0 open-source codebase
- community contribution model
- documentation-first onboarding and support flow
- explicit help, FAQ, troubleshooting, and proposal paths

## Evidence / claims
#### Claim
- Statement: Hummingbot is a free and open-source Python framework for automated trading across centralized and decentralized exchanges.
- Status: active
- Confidence: 0.94
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: Main identity claim.

#### Claim
- Statement: Hummingbot organizes its connector surface into CLOB CEX, CLOB DEX, and AMM DEX categories, with Gateway handling DEX middleware.
- Status: active
- Confidence: 0.91
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: The project's most distinctive architectural feature.

#### Claim
- Statement: The surrounding ecosystem includes Condor, Hummingbot API, Hummingbot MCP, Quants Lab, and the site documentation repo.
- Status: active
- Confidence: 0.88
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: Useful for understanding the broader platform rather than only the core bot.

#### Claim
- Statement: The README presents Hummingbot as a mature, community-driven trading platform with onboarding, contribution, and governance pathways.
- Status: active
- Confidence: 0.85
- Evidence: [[source-hummingbot]]
- Last confirmed: 2026-04-26
- Notes: Keep this as a high-level synthesis rather than overfitting to any one release.

## Relationships
- `Hummingbot` is adjacent to [[freqtrade]] as a classic open-source trading bot.
- `Hummingbot` is adjacent to [[regime-trading-bot]] because both emphasize operational trading workflows and risk-aware deployment.
- `Hummingbot` is adjacent to [[quantdinger]] because both present integrated trading systems with strategy and execution surfaces.
- `Hummingbot` is adjacent to [[vibe-trading]] because both live in the broader trading-automation cluster.
- `Hummingbot` is adjacent to [[tradingagents]] as another structured trading system, though Hummingbot is connector-centric rather than agent-debate-centric.

## Notes
> [!info]
> Hummingbot reads best as a trading infrastructure platform, not merely a strategy example.

> [!warning]
> Connector lists, repo lists, and adoption claims come from a README snapshot. Revisit upstream docs if any of them become decision-relevant.

## Open questions
- Should Hummingbot stay a standalone project page, or later become part of a broader trading-automation synthesis?
- Which connector or ecosystem claims are stable enough to preserve without future verification?

## Related pages
- [[source-hummingbot]]
- [[freqtrade]]
- [[regime-trading-bot]]
- [[quantdinger]]
- [[vibe-trading]]
- [[tradingagents]]
