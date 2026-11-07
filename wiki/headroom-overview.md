---
type: Concept
title: Headroom overview
description: Headroom's context-compression product, interfaces, packaging, and snapshot boundaries.
tags: [agent-memory, context-compression]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:19:57Z }
stale_after: 2027-05-06
sources:
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
---

Headroom is an agent-context compression system with a Python library, proxy, agent wrappers and MCP tools; the project also provides memory and failure-learning features. **Reported:** compression is local, but this does not mean the installation has no network egress: the beacon is on by default. See [privacy and security](headroom-privacy-and-security.md).[^headroom]

**Observed:** the Python distribution is `headroom-ai` 0.43.1, requires Python 3.11+, and builds a Rust extension with maturin. The separate TypeScript SDK uses the proxy. The Rust workspace also includes a separate proxy implementation; Python proxy conclusions should not be generalized to it without verification.[^headroom]

## Relationships

- Uses [content compression](headroom-compression.md), [prefix caching and CCR](headroom-cache-and-ccr.md), and optional [memory](headroom-memory.md).
- Exposes [interfaces and deployment](headroom-interfaces.md); [source coverage](headroom-source-map.md) records inspection limits.
- Compared in [Agent memory landscape survey](agent-memory-landscape-survey.md) (cross-system synthesis).

[^headroom]: `README.md` §§ What it does, How it works, Telemetry; `pyproject.toml` `[project]`, `[build-system]`, `[tool.maturin]`; `sdk/typescript/README.md` introduction; `Cargo.toml` workspace members; `RUST_DEV.md` proxy section, revision `2b0315b`.
