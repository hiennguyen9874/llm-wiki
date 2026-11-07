---
type: Concept
title: Hindsight overview
description: What Vectorize's Hindsight agent-memory system is, how its monorepo is laid out, and where each subsystem is documented in this wiki.
tags: [agent-memory, hindsight, overview]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: api-pyproject
    resource: ../raw/hindsight/hindsight-api-slim/pyproject.toml
    kind: code
    revision: eb963cb
    title: hindsight-api-slim package manifest
  - id: license
    resource: ../raw/hindsight/LICENSE
    kind: code
    revision: eb963cb
    title: Repository license file
  - id: workspace
    resource: ../raw/hindsight/pyproject.toml
    kind: code
    revision: eb963cb
    title: Root uv workspace manifest
---

Hindsight is an open-source agent memory system from Vectorize.io that aims to make agents *learn* rather than merely recall conversation history. It stores memories in isolated **banks** and exposes three operations — [retain](hindsight-retain-pipeline.md), [recall](hindsight-recall-pipeline.md) and [reflect](hindsight-reflect-agent.md) — over REST, MCP and several SDKs. Background [consolidation](hindsight-consolidation-and-mental-models.md) turns facts into evidence-backed observations, mental models and knowledge pages.[^readme] This page is the entry point to the Hindsight cluster of this wiki; all findings are pinned to repository revision `eb963cb` (submodule `raw/hindsight`, version 1.2.0).[^api-pyproject]

## What the README claims (Reported)

- Four memory kinds: world facts, experiences, observations, mental models; memories live in banks.[^readme]
- Recall runs four strategies in parallel (semantic, BM25 keyword, graph, temporal), fuses with reciprocal rank fusion, reranks with a cross-encoder and trims to a token budget.[^readme]
- Positioned as state of the art on LongMemEval; the README says results were reproduced by Virginia Tech and The Washington Post collaborators while other systems' scores are vendor self-reported. See [benchmarks and testing](hindsight-benchmarks-and-testing.md) for the evidence and its limits.[^readme]
- Deployment options: Docker, Docker + external PostgreSQL, `pip install hindsight-api`, Helm, embedded Python (`hindsight-all`), or managed Hindsight Cloud.[^readme]
- Licence: MIT per the root `LICENSE` file and `hindsight-api-slim/pyproject.toml` (Observed).[^license][^api-pyproject] Some sub-package READMEs and the OpenAPI metadata say "Apache 2.0"; see [documentation vs code discrepancies](hindsight-doc-code-discrepancies.md).

## Repository map (Observed)

| Directory | Role | Wiki page |
| --- | --- | --- |
| `hindsight-api-slim/` | The real engine (`hindsight_api` package, 4 console scripts) | [API surface](hindsight-api-surface.md), [retain](hindsight-retain-pipeline.md), [recall](hindsight-recall-pipeline.md), [reflect](hindsight-reflect-agent.md) |
| `hindsight-api/`, `hindsight-all/`, `hindsight-all-slim/`, `hindsight-all-npm/` | Thin packaging wrappers around the engine | [API surface](hindsight-api-surface.md) |
| `hindsight-clients/{python,typescript,go,rust}`, `hindsight-cli/`, `hindsight-embed/`, `hindsight-dev/` | SDKs, CLI, local daemon, dev tooling | [Clients, CLI and embed](hindsight-clients-cli-embed.md) |
| `hindsight-control-plane/` | Next.js web UI | [Control plane](hindsight-control-plane.md) |
| `hindsight-extensions/` | Out-of-tree server extensions | [Extensions, defense, webhooks](hindsight-extensions-defense-webhooks.md) |
| `hindsight-integrations/`, `skills/` | ~48 framework/agent integrations; 5 agent skills | [Integrations](hindsight-integrations.md), [Coding agents](hindsight-coding-agents.md) |
| `docker/`, `helm/`, `monitoring/`, `.github/` | Deployment, dashboards, CI/release | [Deployment and CI](hindsight-deployment-and-ci.md) |
| `hindsight-system-evals/`, `hindsight-system-tests/`, `hindsight-integration-tests/` | Quality evals and blackbox tests | [Benchmarks and testing](hindsight-benchmarks-and-testing.md) |
| `hindsight-docs/` | Docusaurus site (docs, 179 blog posts, cookbook pages) | this cluster |
| `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `scripts/` | Contributor rules and tooling | [Contributor workflow](hindsight-contributor-workflow.md) |

The root is a uv workspace (members `hindsight-all`, `hindsight-api`, `hindsight-api-slim`, `hindsight-all-slim`, `hindsight-dev`, `hindsight-mcp-server`, `hindsight-clients/python`, `hindsight-embed`) plus an npm workspace; `hindsight-mcp-server` is declared but the directory does not exist in this checkout (Observed).[^workspace]

## Other topic pages

[Memory banks](hindsight-memory-banks.md) · [Decision models](hindsight-decision-models.md) · [Storage and configuration](hindsight-storage-and-configuration.md) · [LLM, embedding and reranker providers](hindsight-llm-embedding-providers.md)

## Coverage and limits

- **Method:** static inspection only, performed by parallel Explore subagents (engine; docs site; clients/CLI/embed/dev; control plane/extensions/contributor files; integrations/skills; deploy/evals/tests/CI), followed by the curator's direct spot checks (license, MMR, versions, embed idle timeout, `opinion` fact type, missing workspace member, file existence). No code, tests, builds or containers were executed. Claims not spot-checked are subagent observations of source files, not independently re-read by the curator.
- **Excluded or only sampled:** `hindsight-docs/versioned_docs` (duplicates of 4 versions: 1.2, 1.1, 1.0, 0.10), the 179 blog posts and ~135 unlisted guides (only benchmark-relevant posts read), the 116 Alembic migrations (summarized), generated client code, `node_modules`, static images and videos, per-integration source (only READMEs and a few deep dives), the cookbook (external repo; `cookbook/README.md` is a pointer).
- **Time sensitivity:** version numbers, model names and benchmark numbers describe the 1.2.0 snapshot; blog dates in the tree run to 2026-11-03.

[^readme]: `README.md` § "What is Hindsight?", "Memory Performance & Accuracy", "Quick Start", "Core Concepts" (Memory Types, The Three Operations).
[^api-pyproject]: `hindsight-api-slim/pyproject.toml` lines 7–9 (`version = "1.2.0"`, `license = "MIT"`) and `[project.scripts]`.
[^license]: `LICENSE` header ("MIT License, Copyright (c) 2025 Vectorize AI, Inc.").
[^workspace]: `pyproject.toml` line 2 (`members = [...]`); `package.json` (npm workspaces); `ls hindsight-mcp-server` fails in this checkout.
