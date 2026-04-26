---
title: Source - OpenBB
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: source
aliases:
  - OpenBB README
  - Open Data Platform by OpenBB
  - ODP by OpenBB
  - OpenBB source
tags:
  - source
  - finance
  - data-platform
  - ai
  - workspace
domain: finance
importance: medium
review_status: active
related_sources:
  - [[openbb]]
confidence_score: 0.81
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
  - OpenBB
  - Open Data Platform
  - OpenBB Workspace
  - Python
  - FastAPI
  - Uvicorn
  - MCP
  - Excel
  - REST API
  - AI copilots
  - research dashboards
  - proprietary data
  - licensed data
  - public data
source_file: raw/apps/OpenBB.md
source_type: documentation
author: OpenBB Finance
canonical_url: https://github.com/OpenBB-finance/OpenBB
---

# Source - OpenBB

## What this source is
A README / documentation source for OpenBB’s Open Data Platform (ODP), an open-source financial data integration layer and companion Workspace product.

## Why it matters
This source adds an upstream layer to the wiki’s finance cluster: instead of only trading bots or strategy frameworks, it shows how market and financial data can be normalized once and consumed across many downstream surfaces.

The durable takeaway is the platform shape:
- ingest proprietary, licensed, and public data
- expose it through Python, a CLI, MCP servers, Excel, and REST APIs
- support an analyst-facing Workspace with AI-agent assistance
- provide a local backend bootstrap path for self-hosted use

## Key claims
#### Claim
- Statement: OpenBB’s Open Data Platform is an open-source toolset for integrating proprietary, licensed, and public data sources into downstream applications.
- Status: active
- Confidence: 0.92
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: Core identity claim from the README.

#### Claim
- Statement: The platform operates as a connect-once/consume-everywhere infrastructure layer across Python, OpenBB Workspace, Excel, MCP servers, and REST APIs.
- Status: active
- Confidence: 0.88
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: This is the most reusable structural claim in the source.

#### Claim
- Statement: OpenBB Workspace is an enterprise UI for analysts to visualize datasets and leverage AI agents.
- Status: active
- Confidence: 0.86
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: The README clearly separates the open-source data platform from the Workspace surface.

#### Claim
- Statement: The README documents a local backend flow using `pip install "openbb[all]"` and `openbb-api`, which launches a FastAPI server on `127.0.0.1:6900`.
- Status: active
- Confidence: 0.84
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: Useful operational detail for self-hosted use.

#### Claim
- Statement: The README shows a backend-connect flow for adding the local backend to OpenBB Workspace through the Apps tab.
- Status: active
- Confidence: 0.80
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: This supports the Workspace/backend integration story.

#### Claim
- Statement: The repository is distributed under AGPLv3 and includes a disclaimer that the data is not necessarily accurate and that trading in financial instruments involves risk.
- Status: active
- Confidence: 0.97
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: Keep the caution visible in downstream pages.

## Relationships
- `OpenBB` uses a data-platform architecture that spans Python, CLI, API, MCP, Workspace, and Excel.
- `OpenBB` depends on external data-source aggregation rather than a single trading strategy or model.
- `OpenBB` is adjacent to [[fincept-terminal]], [[daily-stock-analysis]], [[vibe-trading]], [[tradingview-mcp]], [[finrl]], and [[fingpt]] because all sit in the broader finance-tooling ecosystem.

## Notes
> [!info]
> The README mixes open-source platform documentation with an enterprise Workspace surface. That split is part of the source and should stay explicit downstream.

> [!warning]
> Preserve the disclaimer: OpenBB does not claim the contained data is necessarily accurate, and the trading-risk notice should remain visible when this source is reused.

## Related pages
- [[openbb]]
- [[fincept-terminal]]
- [[daily-stock-analysis]]
- [[vibe-trading]]
- [[tradingview-mcp]]
- [[finrl]]
- [[fingpt]]
- [[overview]]
- [[index]]

## Open questions
- Which Workspace and backend claims are code-level reality versus README-level promise?
- Should OpenBB later anchor a broader `financial-data-infrastructure` synthesis if more sources arrive?
- Are the install and backend-connect steps stable enough to treat as durable workflow guidance?
