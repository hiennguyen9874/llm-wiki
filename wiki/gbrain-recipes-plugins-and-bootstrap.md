---
type: Concept
title: GBrain recipes, plugins and personal-agent bootstrap
description: GBrain's integration recipes, the Claude Code and Codex plugin lanes and variants, and the bootstrap flow that turns a coding-agent session into a persistent personal agent.
tags: [agent-memory, gbrain, recipes, plugins, bootstrap]
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
  - id: recipes-dir
    resource: ../raw/gbrain/recipes/agent-voice.md
    kind: code
    revision: 27f8b9d
    title: agent-voice recipe (representative of recipes/)
  - id: plugin-readme
    resource: ../raw/gbrain/plugin/README.md
    kind: code
    revision: 27f8b9d
    title: Plugin README
  - id: plugin-lanes
    resource: ../raw/gbrain/skills/plugin-lanes.json
    kind: code
    revision: 27f8b9d
    title: Plugin lanes
  - id: openclaw-plugin
    resource: ../raw/gbrain/openclaw.plugin.json
    kind: code
    revision: 27f8b9d
    title: OpenClaw plugin manifest
  - id: bootstrap-for-agents
    resource: ../raw/gbrain/BOOTSTRAP_FOR_AGENTS.md
    kind: code
    revision: 27f8b9d
    title: Bootstrap for agents
  - id: bootstrap-guide
    resource: ../raw/gbrain/docs/guides/bootstrap.md
    kind: code
    revision: 27f8b9d
    title: Bootstrap guide
  - id: install-for-agents
    resource: ../raw/gbrain/INSTALL_FOR_AGENTS.md
    kind: code
    revision: 27f8b9d
    title: Install for agents
  - id: origin
    resource: ../raw/gbrain/docs/ethos/ORIGIN.md
    kind: code
    revision: 27f8b9d
    title: GBrain origin story
---

Beyond the core, GBrain ships three kinds of onboarding assets: **recipes** (self-installing Markdown integration specs), **plugins** for Claude Code and Codex (generated trees of skills plus an MCP registration), and a **bootstrap** flow that makes a coding agent into a persistent personal agent with identity files and a private repo. Each is a way of delivering the [skills](gbrain-skills-and-resolver.md) and the [CLI/MCP surface](gbrain-cli-and-mcp-surface.md) to a harness.[^readme][^install-for-agents]

## Recipes (Observed: 10 files in `recipes/`)

Recipes carry frontmatter (`id`, `category`, `requires`, `secrets` as redacted pointers, `health_checks`, `output_paths`, `setup_time`, `cost_estimate`) and install with `gbrain integrations install <name>`.[^recipes-dir]

| Recipe | Category | What it does |
| --- | --- | --- |
| `credential-gateway` | infra | Gmail/Calendar/Contacts access via native `gbrain google connect` or a hosted gateway |
| `ngrok-tunnel` | infra | fixed public URL for MCP or voice (~$8/month tier) |
| `calendar-to-brain`, `email-to-brain` | sense | Google Calendar and Gmail into brain pages; email feeds the open-loop engine |
| `x-to-brain` | sense | X timeline, mentions and keyword monitoring (API ~$200/month per the recipe) |
| `meeting-sync` | sense | Circleback transcripts with attendee detection |
| `twilio-voice-brain` | sense | **deprecated** frozen redirect to `agent-voice` |
| `agent-voice` | voice | WebRTC-first reference with personas and optional Twilio; code is *copied into the host repo* and becomes user-owned |
| `retrieval-reflex` | reflex | teaches when/what to retrieve; a deterministic pointer layer on by default plus a policy skill |
| `restart-sweep` | reflex | detects Telegram messages dropped during gateway restarts |

The README's integration list also names embedding providers, rerankers, the credential vault and MCP clients.[^readme] Source ingestion behavior is in [sync and ingestion](gbrain-sync-and-ingestion.md).

## Plugin distribution (Reported, files Observed)

- Three generated lanes (never hand-edit): `plugin/` (full, 72 skill directories), `plugin-variants/gbrain-coding` (21 skills) and `plugin-variants/gbrain-daily` (20 skills). Claude Code's marketplace declares three plugins; install with `/plugin marketplace add garrytan/gbrain` then `/plugin install gbrain@gbrain`; Codex uses `codex plugin marketplace add garrytan/gbrain@codex-plugin`.[^plugin-readme][^readme]
- Both harnesses register `gbrain serve --surface full --source-guard` over stdio plus a `UserPromptSubmit` hook; Codex additionally needs a trust entry or hooks are silently inert. Variants are personas, not forks; install exactly one per machine since they share the MCP server name.[^plugin-readme]
- **Curation math:** `openclaw.plugin.json` (64 skill paths) minus 11 host-only exclusions plus 11 lane additions equals the 72-directory plugin tree; a test pins membership both ways. `plugin/README.md` asserts a 194-operation full surface (Reported; it matches the manifest count noted in [CLI and MCP surface](gbrain-cli-and-mcp-surface.md)).[^plugin-lanes][^openclaw-plugin]

## Bootstrap a persistent personal agent (Reported)

`gbrain bootstrap` (subcommands `status`, `interview`, `render`, `contract`, `repo`, `hooks`, `verify`, `attach`, `uninstall`, `harness`, `cloud-setup-script`; the set is confirmed in `src/commands/bootstrap.ts`) proceeds through: preflight (git, Bun ≥ 1.4.4, `gh`; the human's one manual step is `gh auth login`) → engine (`gbrain init --pglite`, or a Postgres ladder) → **interview** (max 12 questions, 6 required, three batches; read-back then `--confirm <hash>`) → **render** identity files (never overwrites) → `gbrain skillpack scaffold --all` → **hooks** → private GitHub **repo** (privacy verified through the API) → **verify**.[^bootstrap-for-agents]

- **Identity files** (from `templates/bootstrap/`): SOUL, USER, MEMORY, AGENTS, CLAUDE, HEARTBEAT (cadence, quiet hours, staggered), ACCESS_POLICY (four tiers: full/work/family/none), GITHUB, plus `agent.json` and directories for brain, memory, skills and state.
- **Verification:** `gbrain bootstrap verify` runs a brain round trip through the real write path, a graph floor, token sweep, secret scan, repo privacy check, hooks smoke and capability report; it must exit 0 or the agent "is not done", and it cleans its own probe pages.[^bootstrap-guide]
- **Hard rules:** never invent interview answers, never work around a refusal, never fabricate binaries. A second machine uses `bootstrap attach`. The README notes the resulting repo is not a complete backup.[^bootstrap-for-agents][^readme]
- Two identity-template sets (`templates/*.template` and `templates/bootstrap/*.template`) describe the same files differently and no doc reconciles them (Observed by subagent).

## Origin and framing

The origin essay says GBrain grew out of OpenClaw's flat-Markdown pain (forgetting between sessions, duplicate entities); its quoted production figures (17,888 pages, 723 companies, 21 crons) differ from the README's (155,795 pages, 5,340 companies, 66 crons) — undated, self-reported snapshots.[^origin][^readme]

## Relationships

- Delivers: [skills and resolver](gbrain-skills-and-resolver.md).
- Relies on: [CLI and MCP surface](gbrain-cli-and-mcp-surface.md) (`gbrain setup`), [authorization and security](gbrain-authorization-and-security.md) (hook launcher).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Choose your setup", "Optional: a new personal agent", "Connect GBrain to your AI client (MCP)", "Integrations", "Production brain" paragraph.
[^recipes-dir]: `recipes/*.md` (10 files; frontmatter and intros read by subagent), representative `recipes/agent-voice.md` (`install_kind: copy-into-host-repo`); `docs/integrations/README.md`.
[^plugin-readme]: `plugin/README.md`; `plugin-variants/*/README.md`; `.claude-plugin/marketplace.json`; `.codex-plugin/{plugin,mcp}.json`; `docs/guides/bootstrap.md` (Codex hook trust).
[^plugin-lanes]: `skills/plugin-lanes.json`; `skills/plugin-exclusions.json`; `test/openclaw-plugin-manifest.test.ts`.
[^openclaw-plugin]: `openclaw.plugin.json` (64 skill paths).
[^bootstrap-for-agents]: `BOOTSTRAP_FOR_AGENTS.md` (phases, hard rules, failure-mode table); `src/commands/bootstrap.ts:2020` (known subcommand set); `templates/bootstrap/questions.json`.
[^bootstrap-guide]: `docs/guides/bootstrap.md` (contract tables, verify).
[^install-for-agents]: `INSTALL_FOR_AGENTS.md` intro, Step 0, Step 1 (memory-only path, plugin wire-up, npm trap).
[^origin]: `docs/ethos/ORIGIN.md`; compare `docs/GBRAIN_SKILLPACK.md` figures ("14,700+ brain files").
