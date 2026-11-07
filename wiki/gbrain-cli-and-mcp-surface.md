---
type: Concept
title: GBrain CLI and MCP surface
description: How GBrain's CLI dispatches commands, how the MCP server exposes tools over stdio and HTTP with surface ceilings, and how gbrain setup wires harnesses and brain-first instructions.
tags: [agent-memory, gbrain, cli, mcp, setup]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: cli-ts
    resource: ../raw/gbrain/src/cli.ts
    kind: code
    revision: 27f8b9d
    title: CLI entry
  - id: command-table
    resource: ../raw/gbrain/src/cli/command-table.ts
    kind: code
    revision: 27f8b9d
    title: CLI-only command table
  - id: main-ts
    resource: ../raw/gbrain/src/cli/main.ts
    kind: code
    revision: 27f8b9d
    title: CLI dispatcher
  - id: top-help
    resource: ../raw/gbrain/src/cli/top-help.ts
    kind: code
    revision: 27f8b9d
    title: Top-level CLI help
  - id: mcp-server
    resource: ../raw/gbrain/src/mcp/server.ts
    kind: code
    revision: 27f8b9d
    title: MCP server
  - id: surface-ts
    resource: ../raw/gbrain/src/mcp/surface.ts
    kind: code
    revision: 27f8b9d
    title: MCP surfaces
  - id: tool-catalog
    resource: ../raw/gbrain/docs/TOOL_CATALOG.md
    kind: code
    revision: 27f8b9d
    title: Generated tool catalog
  - id: setup-ts
    resource: ../raw/gbrain/src/commands/setup.ts
    kind: code
    revision: 27f8b9d
    title: gbrain setup orchestrator
  - id: brain-first-ts
    resource: ../raw/gbrain/src/core/setup/brain-first.ts
    kind: code
    revision: 27f8b9d
    title: Brain-first instruction block
  - id: design-md
    resource: ../raw/gbrain/DESIGN.md
    kind: code
    revision: 27f8b9d
    title: Admin SPA design system
---

GBrain's CLI and MCP server are two front ends over one operation registry. Commands that *are* operations are resolved from a generated manifest; CLI-only commands go through a 129-record command table with connect-phase metadata. The MCP server speaks stdio or HTTP, advertises one of three tool surfaces (`verbs`, `starter`, `full`) and enforces them fail-closed at dispatch. `gbrain setup <harness>` wires MCP, hooks and a "brain-first" instruction block into a coding agent.[^cli-ts][^command-table][^surface-ts] See [architecture](gbrain-architecture-and-engines.md) for the registry and [authorization and security](gbrain-authorization-and-security.md) for who may call what.

## CLI structure (Observed by subagent)

- `src/cli.ts` answers `--version`, bare and `--help` without loading the dispatcher, then imports `src/cli/main.ts::runCli()` for everything else.[^cli-ts]
- **Two lanes:** (1) the operations lane from `operation-manifest.generated.ts` through `src/cli/op-manifest.ts`; (2) the CLI-only lane `CLI_COMMANDS` — 129 `CliCommandRecord`s `{name, phase, thinClient, load}` with phases `pre-connect`, `pre-connect-own-engine`, `post-connect` plus a deferred-persistence route. Derived sets (`CLI_ONLY`, `THIN_CLIENT_REFUSED_COMMANDS`, …) replace hand-synced lists.[^command-table]
- **CLI-only pipeline:** thin-client guard → pre-connect table dispatch → engine-free subcommand and help routes → read-only timeout dispatch → connect engine → post-connect dispatch → teardown. Flags are validated from a generated `CLI_FLAG_REGISTRY` or op-declared params.[^main-ts]
- **Command groups** (from top-level help): setup/ops (`setup`, `init`, `doctor`, `repair`, `migrate`, `upgrade`, `serve`, `connect`, `mcp expose|grant|admin|verify`); memory verbs (`remember`, `recall`, `forget`); pages and search (`get`, `put`, `list`, `find`, `search`, `query`/`ask`, `search --exact`); ingest (`import`, `sync`, `export`, `sources …`, `capture`); jobs (`jobs submit|list|work|supervisor`, `autopilot`, `dream`); admin (`stats`, `health`, `history`, `revert`, `config`, `auth`, `access`, `trust`, `quarantine`); and the escape hatch `gbrain call <tool> '<json>'`, which reuses the MCP `handleToolCall` with `remote: false`.[^top-help]

## MCP server

- **stdio:** `gbrain serve` with a 64 MiB message cap; `initialize`/`tools/list` read only the manifest and dispatch boots lazily. Surface precedence: `GBRAIN_SURFACE` env > `--surface` > config `mcp_surface` > `full`. `--advertise <surface>` narrows only `tools/list`; `--access read-only` is stdio-only.[^mcp-server]
- **HTTP:** `serve --http` mounts MCP SDK OAuth 2.1 routes, a `client_credentials` handler, legacy bearer verification, `POST /mcp`, the owner dashboard `/admin`, `/health`, `/metrics` and `/webhooks/github`.
- **Surfaces:** `verbs` = exactly the seven frozen memory verbs; `starter` = 41 operations (counted by the subagent; the source header comment still says "~20-op"); `full` = default. Enforcement is two-layer: `ListTools` is filtered and dispatch receives the same allow-list. On HTTP the server surface is a ceiling, `min(ceiling, client surface)`.[^surface-ts]
- **One dispatcher** (`src/mcp/dispatch.ts`) serves both transports. The generated manifest has 194 operations; 23 are `localOnly`, so the generated catalog's "171 tools across 26 areas" matches (curator re-counted the 23).[^tool-catalog]

## `gbrain setup <harness>` (Observed by subagent unless noted)

The orchestrator is engine-free and never a new installer. It resolves the target first (existing local brain, hosted brain, or a new keyless PGLite) and refuses with coded errors before writing. It records three consent decisions — wiring scope, automatic capture (declined by default) and provider use (declined). It registers an MCP stdio entry through a hook launcher, installs `SessionStart` and `UserPromptSubmit` read-context hooks (capture hooks only if opted in), and splices a marked brain-first block (`BRAIN_FIRST_VERSION = 2`) into the harness's instruction file (`~/.claude/CLAUDE.md`, `$CODEX_HOME/AGENTS.md`, opencode, workspace `AGENTS.md`, Hermes `SOUL.md`, Cursor rules). Ownership is tracked by a hash ledger; text outside the markers is never touched; `--instructions-only`, `--no-instructions` and `GBRAIN_AGENT_INSTRUCTIONS=0` control it. A `harness_wiring` smoke spawns the registered argv and runs initialize, `tools/list` and recall. A versioned capability table marks Claude Code `connection-verified`, Codex `native-verified`, and OpenClaw/Hermes `unsupported` for this path. The README gives the rationale: agents seldom call an MCP server nobody told them about; the source header cites a "1/100 → 92/100 tool-use lift" (Reported).[^setup-ts][^brain-first-ts][^readme]

## Admin dashboard note

`admin/` is a React/Vite SPA served at `/admin` (pages: Dashboard, Agents, Request Log, Calibration, Jobs Watch, Login, OAuth Consent), embedded into the binary through three assets. Root `DESIGN.md` documents *its design system* (color tokens, voice rules, SVG charts), not product architecture.[^design-md]

## Relationships

- Depends on: [architecture and engines](gbrain-architecture-and-engines.md) (registry, engine).
- Guarded by: [authorization and security](gbrain-authorization-and-security.md).
- Teaches agents via: [skills and resolver](gbrain-skills-and-resolver.md) and [recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Connect GBrain to your AI client (MCP)", "Install" (`gbrain setup … --instructions-only`).
[^cli-ts]: `src/cli.ts` lines 1–21, 83–104 (fast path, dispatcher import).
[^command-table]: `src/cli/command-table.ts` lines 1–33, 148, 446–484.
[^main-ts]: `src/cli/main.ts` lines 1957–1996 (`handleCliOnly` pipeline).
[^top-help]: `src/cli/top-help.ts` lines 1–260; `src/commands/call.ts:4`.
[^mcp-server]: `src/mcp/server.ts` lines 34–48; `src/commands/serve.ts:290–295`; `docs/operations/mcp-surface-runbook.md`.
[^surface-ts]: `src/mcp/surface.ts` lines 1–40, 85–120, 461 (`STARTER_OPS`, `effectiveSurfaceForClient`); `src/core/verbs.ts:41`.
[^tool-catalog]: `docs/TOOL_CATALOG.md` line 7; `src/core/operation-manifest.generated.ts` header.
[^setup-ts]: `src/commands/setup.ts` lines 1–33, 116–205; `src/core/setup/capabilities.ts` lines 1–60.
[^brain-first-ts]: `src/core/setup/brain-first.ts` lines 1–58.
[^design-md]: `DESIGN.md` headings "Color tokens", "Charts"; `admin/src/App.tsx`; `src/admin-embedded.ts` (`ADMIN_ASSET_COUNT = 3`).
