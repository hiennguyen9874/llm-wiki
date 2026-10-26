---
type: Concept
title: Graphiti security boundaries and telemetry
description: Unauthenticated reference MCP/REST servers declared out of security scope, the production paths the README offers, and opt-out anonymous telemetry.
tags: [security, rag, telemetry, operations]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:45:00Z }
stale_after: 2027-01-24
sources:
  - id: graphiti-readme
    resource: ../raw/graphiti.md
    kind: documentation
    title: Graphiti README — A Framework for Building Temporal Knowledge Graphs (getzep/graphiti)
---

**Reported:** Graphiti's repository ships two reference servers — an MCP server and a FastAPI REST service — that intentionally implement no authentication, no authorization, and no prompt-injection filtering, and the README states explicitly that security reports about those omissions, and pull requests adding them, are out of scope.[^graphiti-readme] **Synthesis:** this is an unusually explicit trust declaration: the servers are protocol demonstrations, so an exposed Graphiti endpoint without an authorisation layer in front of it is an architecture defect introduced by the deployer, not a framework bug.[^graphiti-readme]

## Reference server trust boundaries

| Documented limit | Consequence stated in the README |
| --- | --- |
| No caller authentication | Any caller can read, change, or delete data in any `group_id` |
| No authorization or tenant isolation | Group boundaries are organisation only, not an access-control boundary |
| No prompt-injection detection | Episode content and tool input go to the configured LLM unfiltered |
| Example Compose default credentials | Database trust is whatever the sample stack ships with |

Upstream also states these servers "are not production deployments", and that security reports and hardening PRs against them are out of scope.[^graphiti-readme]

## Documented production paths

Two options are offered: embed the `graphiti-core` library in your own service, which must then supply authentication, authorization, tenant isolation, and input controls; or use Zep, the vendor's managed or BYOC context platform built on Graphiti ([positioning](graphiti-positioning.md)).[^graphiti-readme]

**Synthesis:** neither path is a substitute for a threat model here — the first delegates every control to the integrator without specifying any, and the second was not inspected at all.[^graphiti-readme]

## Telemetry

Telemetry is described as anonymous, on by default, and opt-out.[^graphiti-readme]

- **Collected on instance initialisation:** a randomly generated UUID stored at `~/.cache/graphiti/telemetry_anon_id`; operating system, Python version, and system architecture; Graphiti version; and configuration choices — LLM provider type, database backend, and embedder provider.[^graphiti-readme]
- **Stated as not collected:** personal information, API keys or credentials, actual data, queries or graph content, IP addresses or hostnames, file paths, and any episode/node/edge content.[^graphiti-readme]
- **Disabling:** set `GRAPHITI_TELEMETRY_ENABLED=false` in the environment or via `os.environ` before importing/initialising Graphiti; telemetry is also disabled automatically when `pytest` is detected.[^graphiti-readme]
- **Mechanism:** PostHog analytics, with operations designed to fail silently so they never interrupt the application; the implementation is linked at `graphiti_core/telemetry/telemetry.py`.[^graphiti-readme]

## Disclosure and credential handling

**Observed:** the captured README contains only placeholder credentials — literal `password`, `your-api-key`, `ollama` placeholder keys, and `<NEPTUNE_ENDPOINT>`/`<AMAZON_OPENSEARCH_SERVERLESS_HOST>` angle-bracket hosts — so no sensitive values were compiled or redacted here. The Jev section does note that dedupe prompt content is sent to TypeSafe, which is a data-flow disclosure rather than a secret ([model configuration](graphiti-model-providers.md)).[^graphiti-readme]

## Relationships

- **Part of:** [Graphiti](graphiti.md).
- **Constrains:** [deployment and graph backends](graphiti-deployment-backends.md) (default credentials, exposure) and [episode ingestion](graphiti-episode-ingestion.md) (unfiltered prompt-injection surface, external provider egress).
- **Alternative path:** the managed platform discussed in [positioning](graphiti-positioning.md) claims governance and SLAs that the self-managed framework does not provide.

## Evidence limits

**Reported only.** No server code, `SECURITY.md`, Compose file, or telemetry module was inspected, so the "what we don't collect" list is an unverified vendor statement; the `group_id`-based access behaviour was not tested. Tenancy and access-control designs for production Graphiti deployments are absent from the source and from this wiki.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): “Reference MCP and REST servers” (WARNING box, limits list, out-of-scope note, production options), “MCP Server” and “REST Service”, “Zep vs Graphiti”, “Telemetry” (What We Collect / What We Don't Collect / How to Disable / Technical Details), “Jev dedupe” (TypeSafe data flow), and credential placeholders in “Optional Environment Variables” and provider examples.
