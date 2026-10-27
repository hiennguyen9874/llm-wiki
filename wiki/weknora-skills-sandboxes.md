---
type: Concept
title: WeKnora skills and session sandboxes
description: Progressive skill disclosure, installed-image source selection, session-bound workspaces, and execution trust boundaries.
tags: [ml, weknora, skills, sandbox]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora exposes skills progressively and executes them against a session workspace rather than placing every skill file into the initial model prompt. **Observed:** the skill manager separates metadata, instructions, and supporting files; sandbox orchestration distinguishes durable session bindings from throwaway calls. These boundaries describe intended execution structure, not a completed isolation audit.[^weknora]

## Skill discovery and loading

`internal/agent/skills/manager.go` implements three levels: `GetAllMetadata` for prompt discovery, `LoadSkill` for full instructions, and `ReadSkillFile` for individual supporting artifacts. An empty skill allowlist means all discovered skills are allowed; a nonempty allowlist filters metadata and is checked again at load time.[^weknora]

**Observed:** when a tenant-installed source is present it owns discovery and loading; the manager does not fall back to a host directory that the installed sandbox image cannot execute. `WithSkillsRoot` can override the installed execution root. Artifact output defaults to `/workspace/output`; overrides are validated. Reserved injected environment names cannot be reassigned through skill environment declarations.[^weknora]

**Reported:** the README advertises installs from ClawHub, SkillHub, Git, and ZIP, plus an interactive terminal and graphical desktop. Those install pipelines and UI paths were not fully audited.[^weknora]

## Session persistence

**Observed contract and constants:** `internal/sandbox/session_manager.go` describes one remote sandbox per tenant session, with the authoritative binding outside the process and lifecycle operations serialized through a distributed coordinator. An empty session ID instead selects throwaway execution. The header documents Redis-backed production bindings, Cube/E2B provider TTLs, and a separate Docker idle sweeper. Full lifecycle enforcement was not reviewed end to end.[^weknora]

Input attachments and generated outputs occupy separate workspace trees. Per-turn checkpoint Git metadata is kept outside the writable workspace root so cleaning that root need not delete rewind/fork history. **Synthesis:** workspace persistence improves continuity but also means a later turn inherits prior filesystem state; it should not be described as a fresh isolated machine on every tool call.[^weknora]

## Trust boundary and version scope

Docker backend activation is opt-in; mounting its daemon socket grants host-root-equivalent control. The README's v0.8.2 note states that sandbox commands run as root. Tenant network-policy resolution exists, but provider-specific enforcement remains pending.[^weknora]

The README's historical v0.8.0 “local host-process backend removed” statement must not be generalized to all editions: later notes describe a macOS Lite host sandbox, and a separate `internal/localsandbox/` implementation exists. **Synthesis:** distinguish the remote skill backend history from Lite/desktop host execution; platform safety was not verified.[^weknora]

## Relationships

- Used by the [agent runtime](weknora-agent-runtime.md).
- Depends on deployment-specific [access and outbound controls](weknora-security.md).
- Runs in the edition-specific [deployment topology](weknora-deployment.md).

## Coverage limits

Skill-manager sections and the sandbox's declared session/workspace contract were inspected. Remote adapters, installation supply chain, local host sandbox, lifecycle races, network enforcement, and provider TTL behavior remain pending. No sandbox was launched. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd58`: `internal/agent/skills/manager.go::GetAllMetadata`, `LoadSkill`, `ReadSkillFile`, `filterAllowedSkills`, `isSkillAllowed`, `resolveSource`, `discoverAllSkills`, `ArtifactOutputDir`, `InjectedSandboxEnvVars`, `WithSkillsRoot`; `internal/sandbox/session_manager.go` package contract and `SessionInputRoot`, `SessionOutputRoot`, `SessionWorkspaceRoot`, `SessionGitDir`; `internal/sandbox/tenant_config.go` symbol inventory; `internal/sandbox/docker_enabled.go` opt-in guard; `docker-compose.yml` app Docker-socket warning; `internal/localsandbox/` directory inventory. Package entry: [README](../raw/WeKnora/README.md), “Skills and sandbox” and v0.8.0–v0.8.3 notes.
