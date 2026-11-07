---
type: Concept
title: Headroom interfaces and deployment
description: Library, proxy, agent wrapper, MCP, and packaging entry points and their operating boundaries.
tags: [agent-memory, deployment]
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

**Observed:** the Python package exposes `compress()` and the `headroom` CLI; `headroom proxy`, `headroom wrap`, `headroom install` and `headroom deploy` offer different runtime and persistence choices. The TypeScript package is an SDK that uses the proxy, not the Python CLI. The MCP server offers compression, retrieval and statistics over stdio or HTTP.[^headroom]

The Python proxy registers provider-specific compressed routes and passthrough routes. Bind policy and local control-surface protections apply to that implementation; the separate Rust proxy has a different exposure model. The MCP HTTP transport defaults to loopback and does not itself add authentication, making rebinding a security decision.[^headroom]

**Reported:** `headroom wrap` is session-scoped, whereas `headroom deploy` is intended for persistent deployment. The README warns that third-party OpenAI-compatible providers need an explicitly configured upstream to avoid sending their key to the default upstream.[^headroom]

## Relationships

- Exposes [compression](headroom-compression.md) and [CCR](headroom-cache-and-ccr.md); see [privacy and security](headroom-privacy-and-security.md) before deployment.

[^headroom]: `pyproject.toml` `[project.scripts]`; `README.md` §§ Get started, Agent compatibility; `sdk/typescript/README.md` introduction; `headroom/providers/proxy_routes.py::register_provider_routes`; `headroom/proxy/bind_policy.py::evaluate_bind_policy`; `headroom/cli/mcp.py`; `headroom/ccr/mcp_http.py::create_streamable_http_app`; `crates/headroom-proxy/src/config.rs` proxy listen options; `RUST_DEV.md` proxy security section; revision `2b0315b`.
