---
title: OpenStock
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - Open Dev Society OpenStock
  - OpenStock app
  - openstock
tags:
  - finance
  - stocks
  - dashboard
  - automation
  - open-source
  - market-data
domain: finance
importance: medium
review_status: active
related_sources:
  - [[source-openstock]]
confidence_score: 0.84
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: working
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - Open Dev Society
  - Next.js 15
  - React 19
  - TypeScript
  - Tailwind CSS v4
  - shadcn/ui
  - Radix UI
  - Better Auth
  - MongoDB
  - Mongoose
  - Finnhub
  - TradingView
  - Inngest
  - Nodemailer
  - Gemini
  - AGPL-3.0
  - watchlists
  - alerts
  - company insights
  - daily summary emails
  - market data
---

# OpenStock

## Summary
OpenStock is an open-source stock market app that aims to replace expensive market platforms with a more open, community-built experience.

The page is best understood as a stock-research and market-monitoring product: it combines price tracking, alerts, watchlists, company insight pages, charts, onboarding, and automated email delivery.

> [!note]
> The project is explicitly not a brokerage. Treat it as a market-information and workflow layer, not an execution venue.

## Key capabilities
### Market surfaces
- real-time or provider-dependent price tracking
- stock detail pages with company insights
- TradingView-based charts and market widgets
- market overview / exploration surfaces

### Personalization and workflow
- user watchlists
- personalized alerts
- onboarding for country, goals, risk tolerance, and industry preferences
- global search and Cmd/Ctrl + K palette

### Automation and delivery
- AI-personalized welcome email
- daily news summary email workflows
- Inngest event / cron orchestration
- Nodemailer-based delivery

### Platform stack
- Next.js 15 + React 19
- TypeScript + Tailwind CSS v4
- shadcn/ui + Radix UI
- Better Auth + MongoDB + Mongoose
- Finnhub for symbols, profiles, and news
- optional Gemini support

## Evidence / claims
#### Claim
- Statement: OpenStock is an open-source alternative to expensive market platforms.
- Status: active
- Confidence: 0.92
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: Core identity claim.

#### Claim
- Statement: OpenStock is community-built and not a brokerage.
- Status: active
- Confidence: 0.97
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: Preserve this boundary.

#### Claim
- Statement: OpenStock combines watchlists, alerts, charts, and company insights into one market-monitoring workflow.
- Status: active
- Confidence: 0.88
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: This is the durable product synthesis.

#### Claim
- Statement: The platform uses Inngest and Nodemailer to automate welcome emails and daily summaries.
- Status: active
- Confidence: 0.86
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: The automation layer is part of the project’s identity.

#### Claim
- Statement: The repository is licensed under AGPL-3.0 and expects source sharing for modified or deployed derivatives.
- Status: active
- Confidence: 0.96
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: Important for downstream reuse.

## Relationships
- `OpenStock` uses Finnhub for market data and TradingView for charting.
- `OpenStock` depends on Better Auth, MongoDB, and Mongoose for user state and persistence.
- `OpenStock` is adjacent to [[openbb]] because both sit in the market-data / financial-platform layer.
- `OpenStock` is adjacent to [[daily-stock-analysis]] because both turn market data into repeatable analysis workflows.
- `OpenStock` is adjacent to [[fincept-terminal]] because both present analyst-facing market surfaces.
- `OpenStock` is adjacent to [[tradingview-mcp]] because both rely on TradingView as part of the market-research stack.
- `OpenStock` is adjacent to [[vibe-trading]] because both expose finance workflows across multiple surfaces.

## Open questions
- Which parts of the project are verified implementation versus README-level promise?
- Is the market-data delay caveat significant enough to shape how this page gets reused?
- Should OpenStock later contribute to a broader stock-platform synthesis if more similar sources appear?

## Related pages
- [[source-openstock]]
- [[openbb]]
- [[daily-stock-analysis]]
- [[fincept-terminal]]
- [[tradingview-mcp]]
- [[vibe-trading]]
- [[overview]]
- [[index]]
