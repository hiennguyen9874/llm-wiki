---
type: Concept
title: Hindsight integrations and agent skills
description: The ~48 Hindsight integration packages grouped by integration mechanic, the LiteLLM wrapper, and the five agent skills shipped in the repo.
tags: [agent-memory, hindsight, integrations, skills]
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
  - id: integrations-readme
    resource: ../raw/hindsight/hindsight-integrations/README.md
    kind: documentation
    revision: eb963cb
    title: hindsight-integrations hub README
  - id: litellm-readme
    resource: ../raw/hindsight/hindsight-integrations/litellm/README.md
    kind: documentation
    revision: eb963cb
    title: hindsight-litellm README
  - id: skills
    resource: ../raw/hindsight/skills/hindsight-docs/SKILL.md
    kind: documentation
    revision: eb963cb
    title: hindsight-docs skill
---

Hindsight claims 60+ integrations; the repo's `hindsight-integrations/` holds 48 independently versioned packages, each with its own README, manifest, tests and lockfile, released with `scripts/release-integration.sh` under tags `integrations/<name>/v<version>`.[^readme][^integrations-readme] Every integration needs a Hindsight URL, a token and a `bank_id`; the server can be cloud, self-hosted or the embedded daemon.[^integrations-readme]

## Integration mechanics (Observed)

1. **Library adapter** — expose retain/recall/reflect as the framework's native primitive: `FunctionTool` (openai-agents, autogen), `@tool` (strands, langgraph), Toolkit (agno), `BaseToolSpec`/`BaseMemory` (llamaindex), `BaseMemoryService` (google-adk), context provider (agent-framework), `FrameProcessor` (pipecat), webhook handler (vapi).[^integrations-readme]
2. **MCP + rules** — an `init` command writes the Hindsight MCP server into the host config and appends an always-on recall/retain rule (github-copilot, openhands, zed, devin-desktop, gemini-spark, meta-muse, agent-plugin).[^integrations-readme]
3. **Hooks/lifecycle** — `SessionStart` + `UserPromptSubmit` (recall) + `Stop` (retain): coding-agents, cursor, omo, roo-code, continue.[^integrations-readme]

Naming: Python `hindsight-<name>`, TypeScript `@vectorize-io/hindsight-<name>`; exceptions include `hermes-plugin-hindsight` and `hindsight-copilot`.[^integrations-readme]

## Groups

- **Coding agents/IDEs:** coding-agents (umbrella, see [Coding agents](hindsight-coding-agents.md)), cursor, continue, github-copilot, devin-desktop, roo-code, openhands, aider, claude-agent-sdk, zed, omo, agent-plugin, grok-bot, meta-muse, gemini-spark.
- **Frameworks:** litellm, langgraph, llamaindex, crewai, pydantic-ai, google-adk, agent-framework, openai-agents, autogen, ag2, agno, strands, smolagents, haystack, composio, superagent (prompt-injection and PII guard), ai-sdk, eliza, eve, chat, agentcore, pipecat, vapi.
- **No-code:** n8n, zapier, dify, flowise, cloudflare-oauth-proxy (OAuth 2.1 proxy for MCP clients).
- **Apps/bots:** obsidian (one-way vault→bank sync with a reflect-based chat panel), openclaw (gateway plugin with setup wizard), nemoclaw, paperclip, hermes.[^integrations-readme]

## LiteLLM wrapper

`hindsight-litellm` recalls (or reflects) before an LLM call, injects memory into the system message, and retains the exchange asynchronously afterward. `wrap_openai(client, bank_id=…, hindsight_api_url=…)` and `wrap_anthropic(...)` return wrapped SDK clients; the README presents this as the two-line way to add memory, covering 100+ models via LiteLLM.[^litellm-readme][^readme]

## Skills (`skills/`)

Five single-file skills: `hindsight-docs` (docs for agents, auto-generated from `hindsight-docs/docs` via `scripts/generate-docs-skill.sh`), `hindsight-architect` (memory-architect persona that outputs a plan), and three usage skills for Cloud, self-hosted and local daemon (`hindsight-cloud`, `hindsight-self-hosted`, `hindsight-local`).[^skills]

## Limits and discrepancies

No `claude-code` or `codex` directory exists — they were superseded by `coding-agents`; the hub README's "Claude Code Skills" row links to `chat/`, which documents the Vercel Chat SDK (Observed by subagent; see [discrepancies](hindsight-doc-code-discrepancies.md)). Integration source was not read beyond READMEs and manifests.

## Relationships

Wraps the [SDKs](hindsight-clients-cli-embed.md) and the [MCP endpoint](hindsight-api-surface.md); release and CI rules in [Contributor workflow](hindsight-contributor-workflow.md).

[^readme]: `README.md` § "Adding Hindsight to Your Agent" (LLM Wrapper, Integrations).
[^integrations-readme]: `hindsight-integrations/README.md` (tables and install commands); per-integration `README.md` and manifests.
[^litellm-readme]: `hindsight-integrations/litellm/README.md` § "Native Client Wrappers"; `hindsight_litellm/{wrappers,callbacks,config}.py`.
[^skills]: `skills/hindsight-docs/SKILL.md`; `skills/hindsight-architect/SKILL.md`; `skills/hindsight-{cloud,self-hosted,local}/SKILL.md`.
