---
title: Source - OpenStock
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - OpenStock README
  - Open Dev Society OpenStock
  - OpenStock source
  - OpenStock repo source
tags:
  - source
  - finance
  - stocks
  - dashboard
  - automation
  - open-source
domain: finance
importance: medium
review_status: active
related_sources:
  - [[openstock]]
confidence_score: 0.82
quality_score: 0.84
evidence_count: 1
first_seen: 2026-04-26
last_confirmed: 2026-04-26
claim_status: active
retention_class: episodic
visibility: private
supersedes: []
superseded_by: []
related_entities:
  - OpenStock
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
source_file: raw/apps/OpenStock.md
source_type: documentation
author: Open Dev Society
canonical_url: https://github.com/Open-Dev-Society/OpenStock
---

# Source - OpenStock

## What this source is
A README / documentation source for OpenStock, an open-source stock market app that combines market data, charts, alerts, watchlists, and automated email workflows.

## Why it matters
This source adds a distinct stock-platform branch to the wiki’s finance cluster. It is more app- and workflow-oriented than a strategy bot:
- surfaces stock data and company pages
- supports personalized alerts and watchlists
- adds daily news summaries through automation
- uses TradingView widgets for charts and market views
- frames the project as open-source infrastructure rather than brokerage access

## Key claims
#### Claim
- Statement: OpenStock is an open-source alternative to expensive market platforms.
- Status: active
- Confidence: 0.92
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: Core identity claim from the README.

#### Claim
- Statement: OpenStock is community-built and explicitly not a brokerage.
- Status: active
- Confidence: 0.97
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: Preserve the non-brokerage framing downstream.

#### Claim
- Statement: Market data may be delayed depending on provider rules and configuration.
- Status: active
- Confidence: 0.90
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: Important caution to keep visible.

#### Claim
- Statement: The platform is built with Next.js 15, React 19, TypeScript, Tailwind CSS v4, shadcn/ui, Radix UI, Better Auth, MongoDB, Mongoose, Finnhub, TradingView, Inngest, Nodemailer, and optional Gemini.
- Status: active
- Confidence: 0.89
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: A durable stack map, though still README-level.

#### Claim
- Statement: OpenStock supports authentication, watchlists, stock detail pages, onboarding, email automation, and keyboard search.
- Status: active
- Confidence: 0.87
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: The most reusable product-flow summary.

#### Claim
- Statement: The repository is licensed under AGPL-3.0 and states that modified, redistributed, or deployed versions must release source code under the same license and credit the authors.
- Status: active
- Confidence: 0.96
- Evidence: [[source-openstock]]
- Last confirmed: 2026-04-26
- Notes: Keep the copyleft boundary visible.

## Relationships
- `OpenStock` uses Finnhub for symbols, profiles, and market news.
- `OpenStock` uses TradingView widgets for charts, heatmaps, quotes, and market views.
- `OpenStock` depends on Better Auth + MongoDB for accounts, sessions, and watchlists.
- `OpenStock` uses Inngest and Nodemailer for welcome emails and daily news summaries.
- `OpenStock` is adjacent to [[openbb]], [[daily-stock-analysis]], [[fincept-terminal]], [[tradingview-mcp]], and [[vibe-trading]] because all sit in the broader finance-tooling ecosystem.

## Notes
> [!info]
> The README mixes product promises with implementation details. Treat the stack and feature list as source claims, not independently verified behavior.

> [!warning]
> Keep the “not a brokerage” and delayed-market-data cautions visible when reusing this page.

## Related pages
- [[openstock]]
- [[openbb]]
- [[daily-stock-analysis]]
- [[fincept-terminal]]
- [[tradingview-mcp]]
- [[vibe-trading]]
- [[overview]]
- [[index]]

## Open questions
- Which features are code-level reality versus README-level promise?
- Are the automation and data-delivery workflows stable enough to treat as durable guidance?
- Should OpenStock later anchor a broader stock-platform synthesis if similar sources accumulate?
