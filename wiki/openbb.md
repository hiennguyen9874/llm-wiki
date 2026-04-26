---
title: OpenBB
created: 2026-04-26
last_updated: 2026-04-26
source_count: 1
status: draft
page_type: project
aliases:
  - Open Data Platform
  - ODP
  - OpenBB Workspace
  - openbb
tags:
  - finance
  - data-platform
  - ai
  - workspace
  - mcp
  - api
domain: finance
importance: medium
review_status: active
related_sources:
  - [[source-openbb]]
confidence_score: 0.82
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
  - OpenBB Finance
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
  - data integration
---

# OpenBB

## Summary
OpenBB is a financial data platform built around the idea of connect once, consume everywhere. It integrates proprietary, licensed, and public data sources into multiple downstream surfaces, including Python, an analyst workspace, Excel, MCP servers, and REST APIs.

The strongest durable takeaway is that OpenBB is upstream infrastructure, not a strategy bot: it is the layer that makes data available to research tools, copilots, dashboards, and other applications.

> [!note]
> The README clearly splits the open-source Open Data Platform from the enterprise OpenBB Workspace. Keep that distinction visible when reusing the page.

## Key capabilities
### Platform surfaces
- Python package for programmatic access
- CLI / backend workflow for local use
- OpenBB Workspace for analyst visualization and AI-agent workflows
- MCP server surface for agent integration
- REST API exposure for downstream applications
- Excel integration for analysts

### Data integration
- Aggregates proprietary, licensed, and public data sources
- Designed as a unifying layer rather than a single-source application
- Suitable for downstream research dashboards and copilots

### Local backend workflow
- `pip install openbb` for core package use
- `pip install "openbb[all]"` for full backend setup
- `openbb-api` serves a local FastAPI backend on `127.0.0.1:6900`
- Workspace backend connection flow supports adding the local backend as an app source

### Governance / caution
- AGPLv3 licensing is part of the repo identity
- README disclaimer says data may not be necessarily accurate
- Trading-risk notice should remain visible when the page is reused

## Evidence / claims
#### Claim
- Statement: OpenBB is a financial data platform that integrates proprietary, licensed, and public data sources into downstream applications.
- Status: active
- Confidence: 0.92
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: This is the project’s core framing.

#### Claim
- Statement: OpenBB’s architecture spans Python, Workspace, Excel, MCP servers, and REST APIs.
- Status: active
- Confidence: 0.88
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: This is the most reusable “surface map” for the project.

#### Claim
- Statement: The README presents OpenBB Workspace as an enterprise analyst UI layered on top of the open-source data platform.
- Status: active
- Confidence: 0.86
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: Preserve the platform/workspace split.

#### Claim
- Statement: The local backend workflow uses `openbb-api` to launch a FastAPI server on `127.0.0.1:6900`, which can then be connected to Workspace.
- Status: active
- Confidence: 0.84
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: Operational detail from the README.

#### Claim
- Statement: The repository includes an explicit disclaimer about data accuracy and trading risk.
- Status: active
- Confidence: 0.97
- Evidence: [[source-openbb]]
- Last confirmed: 2026-04-26
- Notes: Keep this caution visible downstream.

## Relationships
- `OpenBB` is adjacent to [[openstock]] because both sit in the market-data / financial-platform layer.
- `OpenBB` is adjacent to [[fincept-terminal]] because both present analyst-facing financial intelligence platforms with multiple data connectors.
- `OpenBB` is adjacent to [[daily-stock-analysis]] because both turn market data into repeatable research outputs.
- `OpenBB` is adjacent to [[vibe-trading]] because both expose multi-surface finance tooling for agentic workflows.
- `OpenBB` is adjacent to [[tradingview-mcp]] because both support agent-assisted market research through local tooling surfaces.
- `OpenBB` is adjacent to [[finrl]] and [[fingpt]] because both sit in the broader AI-finance ecosystem.

## Open questions
- Which parts of the platform are code-level reality versus documentation-level promise?
- Should OpenBB later anchor a broader `financial-data-infrastructure` synthesis if more sources arrive?
- Is the enterprise Workspace surface something this wiki should keep tracking separately, or is the project page enough?

## Related pages
- [[source-openbb]]
- [[openstock]]
- [[fincept-terminal]]
- [[daily-stock-analysis]]
- [[vibe-trading]]
- [[tradingview-mcp]]
- [[finrl]]
- [[fingpt]]
- [[overview]]
- [[index]]
