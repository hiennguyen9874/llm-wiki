---
type: Concept
title: Hindsight coding-agents integration
description: How the @vectorize-io/hindsight-coding-agents package gives CLI coding agents per-repo memory from git history, session transcripts and seeded knowledge pages.
tags: [agent-memory, hindsight, coding-agents, knowledge-pages]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: coding-agents-readme
    resource: ../raw/hindsight/hindsight-integrations/coding-agents/README.md
    kind: documentation
    revision: eb963cb
    title: coding-agents README
  - id: coding-agents-pkg
    resource: ../raw/hindsight/hindsight-integrations/coding-agents/package.json
    kind: code
    revision: eb963cb
    title: coding-agents package manifest
---

One npm package (`@vectorize-io/hindsight-coding-agents`, v0.8.6, TypeScript/ESM) wires long-term project memory into 20+ CLI coding agents: a per-repo bank built automatically from git history and past sessions, injected as an agent starts, plus curated knowledge pages.[^readme][^coding-agents-pkg] Install with `npx @vectorize-io/hindsight-coding-agents install <agent|all>`; there is no ingestion command.[^coding-agents-readme]

## Installation (Reported + Observed)

- Targets include claude-code, codex, opencode, kilo, cursor-cli, copilot-cli, grok-build, qwen-code, kimi-code, factory-droid, antigravity, devin, cline, pi, prime-agent, deepseek-harness and others. It writes 3–4 hooks into each host's config, registers the `hindsight` MCP server and copies a companion skill; `uninstall` removes exactly what was added.[^coding-agents-readme]
- One bank per repo (`coding-agent::{gitProject}`) shared across agents; server mode cloud, self-hosted or a local `hindsight-embed` daemon (documented port 9077). Config in `~/.hindsight/coding-agent.json` with env fallbacks.[^coding-agents-readme]
- It supersedes older per-agent plugins (`hindsight-claude-code`, `hindsight-codex`).[^coding-agents-readme]

## Ingestion flow

A "deepen" engine spawned at each session start does only missing work: bank config → conversation import (dedup by document id) → one-time gitlog seed → next per-commit diff batch (newest first) → knowledge pages once extraction drains.[^coding-agents-readme]

- `gitIngest`: `"message"` (default; one aggregated `gitlog:<repo>` document, `seedLimit` 300), `"full"` (per-commit messages and diffs) or `"none"`.
- A detached read-only headless **survey** by the host agent (for example `claude -p`, `codex exec --sandbox read-only`) explores the repo and is re-run every `surveyRefreshCommits` (20).
- Session write-back (`retainSessions`, default true) retains transcripts on Stop.[^coding-agents-readme]

## Knowledge pages

Five seeded pages — Component map, Core concepts, Conventions and patterns, Key decisions and rationale, Initiatives and enhancements — each synthesized server-side from tier tags (`knowledge:component|concept|convention|decision|feature-work`). Agent tools include `hindsight_search_knowledge_pages`, `hindsight_read_knowledge_page`, `hindsight_reflect`, `hindsight_ingest_document`, `hindsight_capture_initiative`. `autoInject` (default reflect) injects one retrieval on the first prompt.[^coding-agents-readme] Page mechanics are in [Consolidation and mental models](hindsight-consolidation-and-mental-models.md).

## Relationships

Part of [Integrations](hindsight-integrations.md); uses the embedded daemon from [hindsight-embed](hindsight-clients-cli-embed.md). The `skill/SKILL.md` is generated from README regions (`npm run skill:build`) — a contributor rule in [Contributor workflow](hindsight-contributor-workflow.md).

## Limits

Behaviour reported from the README and manifest by subagent; hooks and the deepen engine were not executed. Hosted-service port and flag names may drift between package releases.

[^readme]: `README.md` § "Coding Agents".
[^coding-agents-readme]: `hindsight-integrations/coding-agents/README.md` (install, ingestion, knowledge pages, migration sections); `src/core/{git,survey,deepen,missions,knowledge-tools}.ts`.
[^coding-agents-pkg]: `hindsight-integrations/coding-agents/package.json` (name, version, `bin`); `plugin.json`.
