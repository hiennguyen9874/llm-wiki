---
title: Ingest Plan - QuantDinger
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-quantdinger]]
  - [[quantdinger]]
  - [[tradingview-mcp]]
  - [[regime-trading-bot]]
  - [[openclaw-for-tradingview]]
---

# Ingest Plan - QuantDinger

## Source identity
- Source file: `raw/apps/QuantDinger.md`
- Source type: documentation / project README
- Likely topic domain: self-hosted quant trading platform, AI research workspace, strategy generation, backtesting, live execution, billing and operations
- Why it matters to `purpose.md`: this is a broad, reusable trading-platform reference that expands the agentic finance cluster with a complete quant OS / research-to-execution stack.

## Key entities and relationships
- QuantDinger → project / product / platform
- brokermr810 → repository owner / publisher identity
- Flask backend → application layer
- Vue frontend / Nginx → delivery layer
- PostgreSQL / Redis → state and worker infrastructure
- Docker Compose → deployment surface
- LLM providers → AI analysis layer
- strategies / indicators → Python-native research artifacts
- exchanges / IBKR / MT5 / Polymarket → market and execution integrations
- memberships / credits / USDT payments → commercialization and admin primitives

## Candidate claims
- QuantDinger presents itself as a private, local-first AI quant operating system for research, Python strategy generation, backtesting, and live execution.
- The stack is self-hosted and deploys via Docker Compose with PostgreSQL, Redis, and Nginx.
- The product combines market research, strategy development, quick trade, live trading, portfolio monitoring, and alerts in one system.
- The README advertises multi-user operations, memberships, credits, admin management, and USDT payment flows.
- The repository claims backend Apache 2.0 licensing, plus a separately licensed frontend source distribution with commercial-use constraints.
- The README includes several snapshot-style feature claims that should be treated carefully unless later verified in code.

## Existing pages likely affected
- `[[tradingview-mcp]]` — adjacent because both support AI-assisted trading workflows and local tool surfaces.
- `[[regime-trading-bot]]` — adjacent because both describe structured trading automation / risk management.
- `[[openclaw-for-tradingview]]` — adjacent because both sit in the agentic trading research ecosystem.
- `[[wiki/overview]]` — should gain QuantDinger as a new durable branch in the trading cluster.
- `[[wiki/index]]` — should add the new source and project pages for discoverability.

## New vs reinforced vs uncertain
### New
- A self-hosted quant OS / research workspace is represented in the wiki as a durable platform reference.
- The source combines research, strategy generation, execution, and commercialization primitives in one README.

### Reinforced
- The trading cluster already includes research-to-execution workflows, but QuantDinger broadens the scope to a more complete operating stack.
- Self-hosting, local control, and operator-ready deployment remain recurring themes.

### Uncertain
- The practical completeness of the advertised feature set is not independently verified.
- The README is strongly promotional; downstream pages should preserve the distinction between documented claims and confirmed implementation.
- It is unclear whether QuantDinger should later anchor a broader `trading-automation` synthesis page or remain a separate project anchor.

## Proposed page actions
### Source page
Create `wiki/source-quantdinger.md` with:
- source metadata
- concise summary of the platform and why it matters
- claim blocks for product shape, infrastructure, AI/research flow, commercialization, and license framing
- open questions about code-level reality versus README claims
- related pages linking to nearby trading-workflow pages

### Project page
Create `wiki/quantdinger.md` with:
- durable summary of the platform as a self-hosted quant OS
- key capabilities organized by interface, infrastructure, AI/research, trading, and commercialization
- explicit note that the source is documentation-level and partly promotional
- relationships to nearby trading pages

## Traceability updates
- Add `related_sources` on the new project page and source page.
- Preserve the raw source unchanged.
- Keep the source page explicit about which claims are directly from the README versus what is inferred as the durable platform shape.

## Review items
1. Should QuantDinger remain a standalone project page, or later anchor a broader `trading-automation` synthesis?
   - Recommendation: keep it standalone for now; it is already a cohesive platform reference.
2. Should README marketing claims be softened in downstream pages because the source is promotional and some features are snapshot claims?
   - Recommendation: yes; preserve the claims but label them carefully.
3. Should the license and commercialization statements be treated as durable facts or as README-level claims pending code/license verification?
   - Recommendation: treat them as source-backed claims for now, with explicit note that they are documentation-level.

## Integration scope
- Single-source ingest is sufficient for the source page, but the project page and overview/index/log updates make this a broad integration task.
- A later `/compile` pass may be warranted if more platform-level sources arrive.
- No Canvas or Base is required yet.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because the source introduces a broad trading-platform branch with durable audit value.
- Create the source page and project page in `wiki/`.
- Update `wiki/overview.md`, `wiki/index.md`, and `wiki/log.md` after integration.
- Create one review-queue item for the synthesis question about whether this should later anchor a broader `trading-automation` page.
