---
title: Ingest Plan - OpenBB
author: OpenBB
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-openbb]]
  - [[openbb]]
  - [[fincept-terminal]]
  - [[daily-stock-analysis]]
  - [[vibe-trading]]
  - [[tradingview-mcp]]
  - [[finrl]]
  - [[fingpt]]
---

# Ingest Plan - OpenBB

## Source identity
- Source file: `raw/apps/OpenBB.md`
- Source type: documentation / project README
- Likely topic domain: financial data infrastructure, market-data aggregation, analyst workspaces, AI-agent data access, research dashboards, and local API/backend integration
- Why it matters to `purpose.md`: this is a reusable example of turning many licensed/public/proprietary data sources into a multi-surface platform for research, copilots, dashboards, and downstream applications.

## Key entities and relationships
- OpenBB / Open Data Platform (ODP) → open-source data integration platform
- OpenBB Workspace → enterprise UI for analysts and AI-agent workflows
- Python package / CLI / API server / REST APIs → primary access surfaces
- MCP servers → agent integration surface
- Excel → analyst surface
- proprietary, licensed, and public data sources → integrated inputs
- `openbb-api` / FastAPI / Uvicorn → local backend surface
- `pip install openbb` / `openbb[all]` → installation and backend bootstrap path
- `support@openbb.co` / `hello@openbb.co` / docs.openbb.co → support and documentation surfaces

## Candidate claims
- OpenBB is an open-source toolset for integrating proprietary, licensed, and public data sources into downstream applications.
- The platform operates as a connect-once/consume-everywhere infrastructure layer across Python, Workspace, Excel, MCP servers, and REST APIs.
- OpenBB Workspace is an enterprise UI for analysts to visualize datasets and leverage AI agents.
- The README documents a local backend workflow using `pip install "openbb[all]"` and `openbb-api`, which serves a FastAPI app on `127.0.0.1:6900`.
- The README shows a backend-connect flow for adding the local backend to OpenBB Workspace.
- The repository is licensed under AGPLv3 and includes a trading-risk / data-accuracy disclaimer.

## Existing pages likely affected
- `[[openbb]]` — should become the canonical project page for the platform.
- `[[fincept-terminal]]` — adjacent because both describe analyst-facing financial intelligence platforms with data connectors and execution / workflow surfaces.
- `[[daily-stock-analysis]]` — adjacent because both turn data feeds into repeatable analysis outputs.
- `[[vibe-trading]]` — adjacent because both expose multi-surface finance tooling for agentic workflows.
- `[[tradingview-mcp]]` — adjacent because both involve local tooling surfaces for agent-assisted market research.
- `[[finrl]]` / `[[fingpt]]` — adjacent as broader AI-finance infrastructure references.
- `[[wiki/overview]]` — should gain a market-data infrastructure / analyst workspace branch.
- `[[wiki/index]]` — should add the new source and project pages for discoverability.

## New vs reinforced vs uncertain
### New
- A public financial data platform / workspace repo is now represented in the wiki as a durable source/project pair.
- The wiki now covers data-infrastructure, not just trading bots and strategy frameworks.

### Reinforced
- The trading / finance cluster already includes research, execution, and dashboard tooling; OpenBB strengthens the upstream data-access layer.
- Analyst-facing surfaces, not only bots, are a recurring pattern in the wiki’s finance cluster.

### Uncertain
- The README is clear on product shape, but the extent of code-level completeness is not independently verified here.
- It is unclear whether this should later anchor a broader `financial-data-infrastructure` synthesis or remain a project-local reference.

## Proposed page actions
### Source page
Create `wiki/source-openbb.md` with:
- source metadata
- concise summary of the OpenBB platform and why it matters
- claim blocks for connect-once/consume-everywhere scope, Workspace, local backend bootstrap, and disclaimer / license context
- open questions about code-level reality versus documentation-level promise
- related pages linking to adjacent finance-tooling pages

### Project page
Create `wiki/openbb.md` with:
- durable summary of OpenBB as a financial data platform / analyst workspace
- key capabilities organized by platform surfaces, data integration, backend workflow, and analyst usage
- explicit note that the source combines open-source platform docs with an enterprise Workspace surface
- relationships to nearby finance and trading pages

## Traceability updates
- Add `related_sources` on the new project page.
- Preserve the raw source unchanged.
- Keep source provenance explicit, especially for the Workspace / enterprise split and the backend endpoint details.

## Review items
1. Should OpenBB remain a standalone project page, or later anchor a broader `financial-data-infrastructure` synthesis if more similar sources arrive?
   - Recommendation: keep it standalone for now; it is coherent and useful on its own.
2. Should the README’s data-accuracy and trading-risk disclaimer be reflected prominently in downstream pages?
   - Recommendation: yes; keep the caution visible.
3. Should future maintenance verify which Workspace and backend claims are code-level reality versus documentation-level promise?
   - Recommendation: yes; treat current claims as source-backed but not independently validated.

## Integration scope
- Single-source ingest is sufficient for the source page, but the project page plus overview/index/log updates make this a broad integration task.
- A later `/compile` pass may be warranted if additional financial-data-platform or market-data-infrastructure sources accumulate.
- No Canvas or Base is required yet.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because the source introduces a durable platform / infrastructure branch with audit value.
- Create the source page and project page in `wiki/`.
- Update `wiki/overview.md`, `wiki/index.md`, and `wiki/log.md` after integration.
- Create one review-queue item for the synthesis question about whether this should later anchor a broader data-infrastructure page.
