---
type: Concept
title: "RAGFlow inbound and outbound MCP boundaries"
description: "MCP caller binding, per-caller tool discovery, delegated authorization, outbound SSRF controls, and protocol-review limits."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54
    title: RAGFlow repository snapshot
---

# RAGFlow inbound and outbound MCP boundaries

**Observed:** RAGFlow both serves MCP tools and calls external MCP servers. Inbound credentials bind requests/sessions to a user identity; service adapters supply dataset/chat/retrieval access. Outbound clients validate and pin endpoints, including same-origin validation for SSE-advertised request URLs. These are separate trust directions and should not be conflated.[^ragflow]

## Inbound tools and identity

`NewHandler` applies local-host/origin checks and parses accepted bearer/API-key credentials; resolution must yield a user or the request is unauthorized. Legacy SSE sessions are random-ID and owner bound, with a body cap and handler-lifetime/request cancellation. The server exposes retrieval, list-datasets and list-chats tools; discovery descriptions are rebuilt per caller with private cache scope because they include caller-specific resources.[^ragflow]

`ServiceConnector` captures a user identity and delegates operations to injected functions. **Synthesis:** actual object-level authorization must remain correct in the service layer; a credential accepted by the transport does not establish access to arbitrary dataset IDs. Handler wiring also includes a self-host identity path; review it before sharing a host endpoint across users.[^ragflow]

## Outbound validation

`AssertMCPURLSafe` checks scheme, DNS and public routability unless configured to allow private hosts; pinning remains in place. `AssertMCPURLSafeSameOrigin` requires matching scheme, host and effective port for an SSE-advertised POST endpoint. FetchTools/CallTool use pinned HTTP clients. Operator-configured outbound headers are templated and may carry credentials: this package is not a redaction boundary.[^ragflow]

## Limits

Full protocol lifecycle, reconnect/cleanup behavior, tool schema bodies, downstream authorization and all escape-hatch configurations were not exhaustively reviewed or tested. Do not infer interoperability or complete security from the static handlers alone.[^ragflow]

## Relationships

- **Exposes:** [retrieval](ragflow-retrieval.md) through a distinct integration protocol.
- **Used by:** [agent workflows](ragflow-agent-workflows.md) for configured external tools.
- **Depends on:** [security/permissions](ragflow-security.md) and [server deployment](ragflow-operations.md).

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54`; locators: `internal/mcp/http.go::NewHandler / Credential / SSE session ownership`; `internal/mcp/server.go::newServer / tools/list / tools/call`; `internal/mcp/connector.go::ServiceConnector`; `internal/handler/mcp_server.go::handler wiring`; `internal/mcp/client/mcp_ssrf.go::AssertMCPURLSafe / AssertMCPURLSafeSameOrigin`; `internal/mcp/client/mcp_call.go::FetchTools / CallTool`; `internal/mcp/client/mcp_client.go::requestSSE / renderHeaders / substituteTemplate`.
