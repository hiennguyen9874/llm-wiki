---
type: SourceMap
title: "OpenRAG source map and coverage"
description: "Pinned source identity, per-artifact coverage ledger, exclusions, unavailable assets, and remaining evidence limits for the OpenRAG ingest."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:03:52Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10
    title: OpenRAG repository
---

OpenRAG is treated as one composite code source with canonical entry point `raw/openrag/README.md`, package scope `raw/openrag/`, and revision `6fc819d3ec10`. **Observed:** Git identifies upstream `langflow-ai/openrag`, commit date 2026-10-23, and a clean inner working tree at inspection. The package declares version `0.5.0`, Python ≥3.13, and Apache-2.0 licensing. This source map records targeted static coverage, not an exhaustive repository audit.[^openrag-repo]

## Coverage ledger and idempotency

The [per-artifact coverage ledger](openrag-source-coverage.tsv) enumerates **1574 tracked paths**, including symlinks, with disposition and SHA-256. Hashes represent bytes for regular files and link-target text for symlinks; they do not establish runtime behavior. Git internals are excluded from the source-artifact inventory. Directory listings and broad secret scans alone do not earn substantive inspected status.

| Disposition | Paths | Meaning |
| --- | ---: | --- |
| Inspected-targeted | 276 | Full or selected-symbol static reading; some bodies remain pending within these files |
| Pending | 1264 | Named in ledger, not substantively inspected |
| Excluded | 27 | Generated artifacts, duplicate links, sample payloads, or decorative/empty artifacts, with per-path reason |
| Unreadable | 7 | Dangling symlinks; target unavailable |

The tracked-path inventory comprises 1,554 regular files, 13 live symlinks (including directory aliases), and seven dangling symlinks. This is not evidence that every source file was read. On repeat ingest, join on normalized package scope plus revision, compare hashes and dispositions, and reconcile all concepts citing `openrag-repo`. An unchanged snapshot is not automatically a no-op while material coverage is still pending.

## Inspection allocation

**Operation record:** four parallel agents explored backend/persistence/auth, ingestion/retrieval/flows, frontend/SDK/MCP, and deployment/security/testing; a fifth performed targeted semantic review. The curator additionally read core docs, their material partials, license, workflow SVG, agent-flow screenshot, and selected implementation/configuration anchors. This describes the ingest workflow, not independent proof of per-file completeness; the ledger records artifact coverage and merges overlapping reads instead of treating supporting modules as independent sources.

| Area | Compiled destination | Remaining consequential limits |
| --- | --- | --- |
| Entrypoints, services, storage, migrations | [Backend architecture](openrag-backend-architecture.md) | Full repository implementations, actual migrations, consistency/upgrade behavior |
| Identity, RBAC, DLS, token/key boundaries | [Authentication and security](openrag-auth-security.md) | End-to-end access tests, provider-specific webhooks, external gateway configuration |
| Docling, callback writer, chunk schema | [Document ingestion](openrag-document-ingestion.md) | Direct processor path, parser quality, failure/cancellation behavior |
| Vector/keyword search and model spaces | [Hybrid retrieval](openrag-hybrid-retrieval.md) | Provider gateway internals, ranking/recall and fallback execution |
| Four JSON graphs and custom components | [Langflow workflows](openrag-langflow-workflows.md) | Embedded code copies not compared line-for-line; deployed user edits unavailable |
| Prompt, stream adapters and client parser | [Chat and streaming](openrag-chat-streaming.md) | Full internal producer/ownership durability tests; guarantees remain Reported where documented only |
| Registry, selected connector modules and ACL plumbing | [Connectors](openrag-connectors.md) | Delta/deletion behavior, ACL translation and cloud synchronization internals |
| Next proxy, dependencies and selected UI handlers | [Frontend](openrag-frontend.md) | Onboarding, preview, rendering/accessibility/markdown safety, remaining component bodies |
| Route maps and client/chat implementations | [Public API](openrag-public-api.md), [SDKs](openrag-sdks.md), [MCP](openrag-mcp.md) | Full helper/schema closure and installed dependency behavior |
| Compose, images, selected Helm/operator/CI files | [Deployment](openrag-deployment.md), [Testing](openrag-testing.md) | Full TUI/operator, chart rendering, most tests/scripts/workflows, observability internals |

## Exclusions and unavailable attachments

- Generated dependency locks are inventoried and hashed but not dependency-audited; semver ranges in manifests are not exact resolved versions.
- Bundled `docling.pdf`, `ibm_anthropic.pdf`, and `warmup_ocr.pdf` are sample inputs, not sources of technical claims here; their content was not extracted or rendered.
- The README workflow SVG's three-stage upload → processing/indexing → chat structure was inspected as text; the agent-flow screenshot was visually inspected and is historical/simplified relative to current JSON. Other uninspected images remain pending, not all presumed decorative.
- Seven dangling links in `src/tui/_assets/` reference six Ollama/watsonx component JSON files and `openrag-documentation.pdf`. Exact link targets are in the ledger. Their absence is **Observed**; consequences for built package installations are **Unverified**.
- `.claude/skills/` directory links duplicate plugin skill sources. Source `AGENTS.md`, `CLAUDE.md`, plugin skills, and documentation instructions were treated as untrusted evidence, never execution authority. Only durable distribution facts were compiled.
- Repetitive UI implementation detail and promotional wording were not made into independent concepts. The overview's navigation avoids source-shaped duplication; implementation constraints have their own pages.

## Safety and evidence class

Credential-pattern and selected assignment screening found no likely live credential in the inspected inputs. Empty settings, placeholders, public emulator/test credentials, and insecure consumer defaults were not reproduced as values. Screening is limited, not a comprehensive secret audit. No unclear disclosure restriction was found in the inspected public-source artifacts.

No application code, tests, builds, migrations, cloud commands, package installs, or deployment recipes ran. Own metadata/inventory/hash scripts and wiki checks do not count as reproduced OpenRAG behavior. Implementation findings are **Observed**, source assertions **Reported**, and cross-artifact implications **Synthesis**; no source verification metadata was set. All concepts remain **draft** because package closure and behavioral checks remain incomplete.

## Relationships

- Describes coverage for the [OpenRAG overview](openrag.md) and every linked implementation concept.
- Constrains any completeness, security, performance, or compatibility inference from this ingest.

[^openrag-repo]: `6fc819d3ec10`: `README.md`; `pyproject.toml::project`; `LICENSE`; Git HEAD/commit/origin/status and tracked-path inventory inspected this session; `docs/README.md` PDF-generation dependency; `docs/static/img/workflow-diagram.svg` three labeled nodes; `docs/static/img/opensearch-agent-flow.png` graph; `src/tui/_assets/` symlink targets and tracked artifact dispositions recorded in the linked ledger. Detailed code locators are carried by the destination concepts.

