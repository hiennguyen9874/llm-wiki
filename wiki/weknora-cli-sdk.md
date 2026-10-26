---
type: Concept
title: WeKnora CLI and Go SDK
description: Agent-first CLI envelopes, streaming/replay contracts, credential resolution, project binding, and the Go client API.
tags: [ml, weknora, cli, sdk]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd5855fc4ded5c981a92dcb82a455246
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora's official CLI is an agent-oriented API consumer with a structured output contract; the Go SDK supplies reusable HTTP and streaming access. **Observed:** the CLI, SDK event format, server release, and MCP tool surfaces are distinct compatibility boundaries. The CLI and web frontend are parallel consumers, not layers of one another.[^weknora]

## CLI wire and streaming contracts

The documented contract uses a success envelope on stdout and typed errors on stderr, with error type, exit code, and optional recovery hints. Root command setup pre-scans formatting so parsing failures can also use structured output. Exit-code rows include explicit confirmation-required, timeout, and signal-cancellation outcomes; destructive-command confirmation is not interchangeable with a generic failure.[^weknora]

**Observed:** NDJSON emits an initial CLI event and passes SDK events without renaming; JSON mode accumulates a bounded projection. The SSE accumulator keeps reasoning/reflection separate from final answer content and captures references independently. Session resume replays stored events from the beginning before tailing, so consumers need identity-based deduplication. The inspected stream factory uses a one-hour Redis buffer TTL; memory-mode buffers do not survive process restart.[^weknora]

## Credentials and project context

`KeyringStore` uses profile-specific keyring entries with a best-effort private-file fallback. XDG helpers manage atomic configuration writes; project binding under `.weknora/project.yaml` can supply a default KB through bounded parent-directory discovery. **Reported:** headless access can use `WEKNORA_API_KEY` plus `WEKNORA_HOST` without persisting credentials. Credential values are excluded from this wiki.[^weknora]

Bundled skills and an install command support agent workflows; installation writes outside the repository by default and requires explicit force to overwrite. Skill-parity checks aim to prevent documentation from referring to dropped commands. No installer or CLI binary was executed.[^weknora]

## SDK and MCP distinction

The Go `client.Client` supports API-key or Bearer authentication, timeout and transport customization, and tenant context. `KnowledgeQAStream` and `AgentQAStream` expose response types, content, references, tool data, session/message identity, and terminal errors. A timeout setting also affects SSE lifetime.[^weknora]

The CLI's `weknora mcp serve` is a curated stdio surface, distinct from the app's built-in endpoint server and deprecated Python package. Its tool catalog includes KB/document inspection, chunk search, chat, agent listing, session asking, and chunk listing; do not apply another server's tool count/version to it.[^weknora]

## Relationships

- Uses the [backend API](weknora-backend-architecture.md).
- Shares event concepts with [frontend streaming](weknora-frontend-streaming.md).
- Exposes an alternative to the app's [MCP server](weknora-mcp-servers.md).

## Coverage limits

Selected root/output/credential/project/streaming files and SDK interfaces were inspected. Most CLI commands, nonstreaming SDK CRUD, acceptance tests, and credential precedence combinations remain pending. Documentation contracts are not reproduced check results. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd5855fc4ded5c981a92dcb82a455246`: `cli/README.md`, “Wire contract”; `cli/AGENTS.md`, output/credentials/stream-recovery sections (source data, not wiki governance); `cli/main.go`; `cli/cmd/root.go::Execute`, `resolveFormatEarly`; `cli/cmd/exitcodes.go::exitCodeRows`; `cli/internal/output/ndjson_stream.go`; `cli/internal/sse/accumulator.go::Accumulator.Append`, `projector.go::Projector`; `cli/internal/secrets/keyring.go::KeyringStore`, `NewBestEffortStore`; `cli/internal/projectlink/` inspected discovery interface; `cli/internal/xdg/` inspected path/write interface; `cli/internal/mcp/server.go::RunStdio`, `tools.go`; `client/client.go::Client`, options; `client/session.go::KnowledgeQAStream`, `StreamResponse`; `client/agent.go::AgentQAStream`; `client/sse.go`; `client/stream_errors.go`; `internal/stream/factory.go`. Package entry: [README](../raw/WeKnora/README.md), “Command-Line Interface.”
