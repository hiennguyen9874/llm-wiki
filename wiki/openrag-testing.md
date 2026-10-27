---
type: Concept
title: "OpenRAG testing and validation limits"
description: "Configured backend, frontend, SDK and CI checks, known exclusions, non-gating scans, and what this ingest did not execute."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10
    title: OpenRAG repository
---

**Observed:** OpenRAG includes Python unit/integration tests, frontend Vitest/Playwright configuration, SDK tests, lint/typecheck workflows, and several security scanning workflows. Their presence establishes intended validation mechanisms, not passing results, full feature coverage, or release safety.[^openrag-repo]

## Configured validation surfaces

| Area | Static evidence | What is not established |
| --- | --- | --- |
| Backend | pytest/asyncio/mock/cov dev dependencies, RuntimeWarning promoted to error, unit/integration fixtures | No tests executed; integration fixtures require infrastructure |
| Auth | Unit permission fixture uses in-memory SQLite with seeded roles/catalog | Does not establish every production RBAC/DLS path |
| Frontend | Vitest, Testing Library/jsdom/MSW; Playwright E2E configuration; Biome and separate typecheck script | No browser, rendering, typecheck, or lint run |
| SDKs | Repository test trees and integration-oriented examples | No installed/published-package parity or live API validation |
| CI | Backend test/lint, integrated stack, CodeQL, dependency/security scan workflows | No workflow run results or coverage reports inspected |

Ruff and mypy configuration comments explicitly scope checks to changed files in PR workflows. `make lint` covers frontend rather than constituting a whole-repository lint guarantee. Next build ignores TypeScript errors; use the separate configured typecheck rather than equating build with type safety.[^openrag-repo]

## Negative findings and check semantics

`tests/unit/known_failures.txt` lists agent-response and source test modules among import-time exclusions. This is an **Observed exclusion record**, not a reproduced import failure in this session. A flow-component synchronization test exists, but its body and result were not examined, so serialized/Python code equivalence is not verified.[^openrag-repo]

Security workflow scans are configured with non-failing exit behavior, and the advertised `fail_on_critical` input is not connected to enforcement in the inspected workflow. **Synthesis:** a green workflow alone would not prove absence of critical vulnerabilities. No scan findings report or dependency advisory set was retrieved.[^openrag-repo]

The documentation's ingestion benchmark has inconsistent rate/timing/count statements; [ingestion](openrag-document-ingestion.md) preserves the reported figures and arithmetic qualification rather than treating them as a regression baseline.[^openrag-repo]

## This ingest's checks

The ingest executed only repository metadata/inventory parsing and wiki-maintenance checks, not OpenRAG source code, tests, builds, migrations, or cloud operations. Evidence classes on implementation pages are therefore Observed, Reported, or Synthesis—not Reproduced application behavior. Any structural wiki validation result belongs to the operation report and log, not to an assertion that OpenRAG itself passes tests.

## Relationships

- Constrains confidence in [deployment](openrag-deployment.md), [security](openrag-auth-security.md), and [workflow synchronization](openrag-langflow-workflows.md).
- Coverage and remaining work are recorded in the [source map](openrag-source-map.md).

## Coverage limits

Most test bodies, all execution results, provider/live validation scripts, and generated lockfile dependency audits remain pending. No source-level verification metadata is set on the compiled concepts.

[^openrag-repo]: `6fc819d3ec10`: `pyproject.toml::{dependency-groups.dev,tool.pytest.ini_options,tool.ruff,tool.mypy}`; `tests/conftest.py`; `tests/unit/dependencies/test_require_api_key_permission.py`; `tests/integration/core/test_api_endpoints.py`; `tests/unit/known_failures.txt`; inventory entry `tests/unit/test_flow_component_sync.py` (existence only); `frontend/{package.json,next.config.ts,vitest.config.mts,playwright.config.ts}`; `Makefile::lint`; `.github/workflows/{test-backend,lint-backend,test-ci,security-scan,dependency-audit,codeql}.yml`; `docs/docs/core-components/ingestion.mdx` § Ingestion performance expectations.
