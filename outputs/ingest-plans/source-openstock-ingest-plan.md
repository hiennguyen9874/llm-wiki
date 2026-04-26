---
title: Ingest Plan - OpenStock
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: episodic
related_sources:
  - [[source-openstock]]
  - [[openstock]]
---

# Ingest Plan - OpenStock

## Source identity
- **Source file:** `raw/apps/OpenStock.md`
- **Source type:** documentation / README
- **Canonical URL:** https://github.com/Open-Dev-Society/OpenStock
- **Author / org:** Open Dev Society
- **Why it matters:** adds a stock-market app/project branch to the finance tooling cluster, centered on market data, dashboards, alerts, authentication, automation, and TradingView embeds.

## Key entities and relationships
- **OpenStock** — open-source stock market app / project.
- **Open Dev Society** — project org / framing layer.
- **Next.js / React / TypeScript / Tailwind / shadcn/ui / Radix** — UI and app stack.
- **Better Auth / MongoDB / Mongoose** — auth and persistence layer.
- **Finnhub / TradingView** — market data and chart surfaces.
- **Inngest / Nodemailer / Gemini** — automation and notification layer.
- **Users / watchlists / stock detail pages / alerts / daily summaries** — core product flow.
- **AGPL-3.0** — license boundary to preserve.

Typed relationships to capture:
- OpenStock **uses** Finnhub for symbols, profiles, news.
- OpenStock **uses** TradingView widgets for charts, heatmaps, quotes.
- OpenStock **depends_on** Better Auth and MongoDB for user accounts and watchlists.
- OpenStock **uses** Inngest for welcome-email and daily-summary workflows.
- OpenStock **supports** a dashboard-first stock research workflow rather than live brokerage execution.
- OpenStock **is_adjacent_to** OpenBB / Daily Stock Analysis / Fincept Terminal / TradingView MCP / Vibe-Trading.

## Candidate claims
- OpenStock is an open-source alternative to expensive market platforms.
- It provides real-time price tracking, personalized alerts, and company-insight pages.
- The README frames it as community-built and not a brokerage.
- Market data may be delayed depending on provider rules and configuration.
- The stack includes Next.js 15, React 19, TypeScript, Tailwind v4, shadcn/ui, Radix, Better Auth, MongoDB, Finnhub, TradingView, Inngest, Nodemailer, and optional Gemini.
- The app supports watchlists, stock detail pages, onboarding, email automation, and keyboard search.
- The repository is licensed under AGPL-3.0 and requires source release if modified / redistributed / deployed as a service.

## Related existing pages
Likely affected or adjacent:
- `[[openbb]]` / `[[source-openbb]]`
- `[[daily-stock-analysis]]` / `[[source-daily-stock-analysis]]`
- `[[fincept-terminal]]`
- `[[tradingview-mcp]]`
- `[[vibe-trading]]`
- `[[overview]]`
- `[[index]]`

## New vs reinforced vs uncertain
### New
- A distinct stock-market application project page is warranted.
- The source adds a clean finance app pattern: watchlist + alerts + market data + charts + daily email automation.

### Reinforced
- Finance tooling cluster already emphasizes data surfaces, dashboards, and agentic workflows.
- OpenStock reinforces the role of TradingView and market-data providers in the existing finance stack.

### Uncertain / to preserve
- Feature completeness is README-level only; code-level verification is not established here.
- “Real-time” may be provider-dependent and should remain qualified.
- No live brokerage claim should be inferred.

## Proposed edits
### Source page
Create `wiki/source-openstock.md` with:
- required frontmatter + source metadata
- what the source is
- why it matters
- key claims in lightweight evidence blocks
- relationships
- notes on license / not-a-brokerage / data-delay caveats
- related pages and open questions

### Canonical project page
Create `wiki/openstock.md` with:
- summary
- key capabilities (market data, alerts, watchlists, dashboard, email automation)
- evidence / claims blocks
- relationships to adjacent finance-tooling pages
- open questions about code-level verification and whether a broader synthesis is later warranted

### Traceability updates
- `related_sources` on `[[openstock]]` should point to `[[source-openstock]]`.
- `related_sources` on `[[source-openstock]]` should point to `[[openstock]]`.
- Update adjacent pages’ `related_pages` / relationships if helpful, especially `[[openbb]]` and `[[daily-stock-analysis]]`.

## Compile decision
- **Mode:** single-source ingest is sufficient for now.
- **Later compile?** Not required immediately. Revisit only if more stock-platform sources accumulate into a broader synthesis.

## Review items
- No high-stakes taxonomy or schema change is required.
- Keep README claims clearly labeled as source-derived, not code-verified.
- Preserve AGPL and not-a-brokerage disclaimers in downstream pages.

## Outputs / visuals
- No output report, Base, or Canvas is warranted yet.
- If similar stock-platform sources keep accumulating, consider a later synthesis page or Canvas for the finance-app cluster.
