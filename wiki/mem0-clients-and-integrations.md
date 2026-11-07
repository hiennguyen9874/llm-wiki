---
type: Concept
title: Mem0 clients, CLI and integrations
description: Hosted and OSS client surfaces, CLI configuration, coding-agent plugins, and integration boundaries.
tags: [agent-memory, mem0]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:08:00Z }
stale_after: 2027-02-06
sources:
  - id: mem0
    resource: ../raw/mem0/README.md
    scope: ../raw/mem0/
    kind: code
    revision: d16b8df
    title: Mem0 repository
---

**Observed:** Python and TypeScript provide hosted-platform clients alongside OSS memory implementations. The hosted Python client uses multiple endpoint generations, with v3 memory add and search and older endpoints for some management operations; constructor identity validation contacts the service. Do not assume self-hosted routes match the managed API.[^mem0]

The repository includes Python and Node CLI implementations, coding-agent plugins, and reference and workflow skills. **Observed:** the CLI spec's endpoint descriptions and some agent-facing documentation lag the implementations. Integrations share agent-plugin core code but host adapters have different lifecycle semantics; capture and remote storage introduce privacy boundaries, and regex redaction is not a guarantee that all secrets are removed.[^mem0]

The CLI's local configuration and synchronization can replicate credentials into pre-existing configuration files; see [server and security](mem0-server-and-security.md). The individual integration adapters were examined selectively, and hosted behavior was not tested.[^mem0]

[^mem0]: Revision `d16b8df6`; `mem0/client/main.py::MemoryClient`, `MemoryClient._validate_api_key`, `MemoryClient.add`, `MemoryClient.search`; `mem0-ts/src/client/mem0.ts::MemoryClient`; `cli/cli-spec.json::api.endpoints`; `cli/python/src/mem0_cli/backend/platform.py`; `cli/python/src/mem0_cli/plugin_sync.py`; `integrations/agent-plugin-core/README.md`; `integrations/claude-code-plugin/core/memory_core.py`; `README.md::Agent Skills`.
