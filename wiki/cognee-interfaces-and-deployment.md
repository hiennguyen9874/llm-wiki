---
type: Concept
title: Cognee interfaces and deployment
description: Python, HTTP, CLI, MCP, and container deployment surfaces with configuration caveats.
tags: [agent-memory, cognee, deployment]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:06:51Z' }
stale_after: 2027-02-06
sources:
  - id: cognee
    resource: ../raw/cognee/README.md
    scope: ../raw/cognee/
    kind: code
    revision: 525b1d1
    title: Cognee repository
---

**Observed:** Cognee includes a Python SDK, FastAPI application, command-line interface and separate MCP server. The MCP server supports tool-advertisement modes that change discovery, not whether registered tools can be called by name.[^cognee]

## Operation and deployment

**Reported:** the README documents Docker-based API deployment and a source-checkout Compose stack with optional UI and MCP profiles. It describes disabling backend access control as a single-user/local posture; persistent storage and authentication require deliberate configuration for other deployments. Neither the container stack nor service health was tested here.[^cognee]

**Observed:** MCP code labels `code_search` as a default tool, while its README describes a smaller default pinned set. Treat the source version's registration as the implementation, not the README count.[^cognee]

## Relationships

- **Exposes:** [Cognee ingestion](cognee-ingestion-and-code-graphs.md) and [retrieval](cognee-retrieval.md).
- **Depends on:** [Storage and authorization](cognee-storage-and-security.md) for deployment boundaries.

[^cognee]: Revision `525b1d1`, `README.md::Connect your agent`, `README.md::Deploy Cognee`, `cognee/api/client.py::app`, `cognee/cli/_cognee.py::main`, `cognee-mcp/src/server.py::apply_tool_mode`, `::code_search`, `cognee-mcp/README.md::Tool modes`.
