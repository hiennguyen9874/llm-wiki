---
title: Source - QuantDinger
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - QuantDinger README
  - QuantDinger source
  - QuantDinger documentation
tags:
  - source
  - trading
  - ai
  - quant
  - backtesting
  - automation
domain: trading
importance: medium
review_status: active
related_sources:
  - [[quantdinger]]
confidence_score: 0.75
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
  - brokermr810
  - QuantDinger
  - Flask
  - Vue
  - Nginx
  - PostgreSQL
  - Redis
  - Docker Compose
  - LLM providers
  - IBKR
  - MT5
  - Polymarket
  - USDT
source_file: raw/apps/QuantDinger.md
source_type: documentation
author: brokermr810
canonical_url: https://github.com/brokermr810/QuantDinger
---

# Source - QuantDinger

## What this source is
A repository README / documentation source for QuantDinger, presented as a self-hosted AI quant operating system for research, strategy generation, backtesting, live execution, and trading operations.

## Why it matters
This source broadens the wiki’s trading cluster with a complete quant-platform reference rather than a narrow tool or one-off bot. It combines:
- AI market research
- Python strategy generation
- backtesting and strategy persistence
- live trading workflows
- portfolio monitoring and alerts
- multi-user / billing / commercialization primitives
- deployment and operator infrastructure

## Key claims
#### Claim
- Statement: QuantDinger is a self-hosted, local-first quantitative trading and algorithmic trading platform for AI research, Python strategy generation, backtesting, and live execution.
- Status: active
- Confidence: 0.82
- Evidence: [[source-quantdinger]]
- Last confirmed: 2026-04-26
- Notes: This is the README’s main framing.

#### Claim
- Statement: The platform runs as a Docker Compose stack with a Flask backend, prebuilt Vue frontend, PostgreSQL, Redis, and Nginx.
- Status: active
- Confidence: 0.84
- Evidence: [[source-quantdinger]]
- Last confirmed: 2026-04-26
- Notes: This is the core infrastructure claim set.

#### Claim
- Statement: QuantDinger integrates AI analysis, Python indicator and strategy development, backtests, quick trade, live operations, portfolio monitoring, and alerts in one product.
- Status: active
- Confidence: 0.79
- Evidence: [[source-quantdinger]]
- Last confirmed: 2026-04-26
- Notes: The source presents this as the main product value proposition.

#### Claim
- Statement: QuantDinger advertises multi-market coverage across crypto exchanges, IBKR for US stocks, MT5 for forex, and Polymarket research workflows.
- Status: active
- Confidence: 0.74
- Evidence: [[source-quantdinger]]
- Last confirmed: 2026-04-26
- Notes: Capture this as a documentation-level platform claim.

#### Claim
- Statement: The README advertises multi-user operations, memberships, credits, admin management, and USDT payment flows.
- Status: active
- Confidence: 0.74
- Evidence: [[source-quantdinger]]
- Last confirmed: 2026-04-26
- Notes: Treat as documentation-level claim unless later code verification strengthens it.

#### Claim
- Statement: The repository says the backend is Apache 2.0 licensed, while the frontend source is separately licensed and commercial use requires a separate commercial license.
- Status: active
- Confidence: 0.77
- Evidence: [[source-quantdinger]]
- Last confirmed: 2026-04-26
- Notes: Preserve the license split explicitly.

## Relationships
- `QuantDinger` uses a research-to-execution stack that spans AI analysis, strategy code, backtesting, and trading operations.
- `QuantDinger` depends on operator infrastructure such as Docker Compose, PostgreSQL, Redis, and Nginx.
- `QuantDinger` is adjacent to [[tradingview-mcp]], [[regime-trading-bot]], and [[openclaw-for-tradingview]].

## Notes
> [!info]
> The README is useful because it defines a cohesive platform shape. The durable takeaway is the architecture and workflow stack, not any implied trading edge.

> [!warning]
> The source is promotional and includes snapshot-style feature counts and licensing statements. Keep those claims visible, but do not overstate them as independently verified facts.

## Related pages
- [[quantdinger]]
- [[tradingview-mcp]]
- [[regime-trading-bot]]
- [[openclaw-for-tradingview]]

## Open questions
- Which parts of the platform are code-level reality versus README-level aspiration?
- Are the license and commercialization statements stable enough to treat as durable facts?
- Should this later anchor a broader `trading-automation` synthesis?
