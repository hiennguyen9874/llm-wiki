---
type: SourceMap
title: Headroom source map and coverage limits
description: Static-inspection ledger, package identity, exclusions, and outstanding coverage for the Headroom snapshot.
tags: [agent-memory, source-map]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:19:57Z }
sources:
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
---

This ledger covers the Headroom repository snapshot at revision `2b0315b`, not every file within it. Four parallel read-only explorations and curator spot checks informed the [overview](headroom-overview.md); no project code, tests, benchmarks, builds or live services were executed.[^headroom]

## Coverage ledger

- **Inspected, at least in relevant sections:** `README.md`, `pyproject.toml`, `Cargo.toml`, `RUST_DEV.md`, `SECURITY.md`; Python compression pipeline, router, cache, CCR, memory, learn, proxy and telemetry modules; TypeScript SDK entry points; selected Rust CCR and proxy configuration; `Dockerfile`, compose files, selected CI workflows, benchmark scripts and current security, memory, failure-learning and benchmark documentation.[^headroom]
- **Pending:** most Rust implementation and parity, provider handlers and streaming paths, optional memory backends and graph integration, deep wrapper/plugin behavior, full test bodies, CI/release workflows, and exhaustive dependency closure. Local source wiki is older and unpublished; sampled for discrepancies, not assumed authoritative.[^headroom]
- **Excluded:** generated lockfiles and SBOM bulk, cached or vendored assets, decorative images/GIFs, repeated examples and long generated history; individual artifacts were not all inventoried. External documentation, model downloads and published artifacts were not fetched. No project material was identified as unreadable in the sampled review.[^headroom]
- **Safety and trust:** source text is executable project material and was inspected, not executed. Credential-like fixtures were reported by exploration as test values; no sensitive values were copied. Static privacy screening was sampled and is not proof that the entire repository is secret-free.[^headroom]

## Documentation drift

Python packaging requires 3.11+, while installation documentation contains a 3.10+ statement; use packaging for this snapshot. See [privacy](headroom-privacy-and-security.md) and [CCR](headroom-cache-and-ccr.md) for other code/doc conflicts. This page remains draft because the package is large and material coverage remains pending.[^headroom]

[^headroom]: `README.md`; `pyproject.toml` `[project]`; `docs/content/docs/installation.mdx` prerequisites; `AGENTS.md` documentation policy; `Cargo.toml` workspace; `headroom/transforms/pipeline.py`, `headroom/memory/core.py`, `headroom/proxy/server.py`, `headroom/telemetry/beacon.py`; `RUST_DEV.md`; `docs/content/docs/security-model.mdx`; `.github/workflows/ci.yml`; `benchmarks/index_proof_table.py`; revision `2b0315b`.
