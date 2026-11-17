---
type: Concept
title: Pydantic AI AgentEnv evaluation
description: How AgentEnv runs a Pydantic AI Coder agent against seeded MCP environments, verifies outcomes, and routes model calls through Logfire Gateway.
tags: [pydantic-ai, agents, evaluation, mcp]
status: draft
created: 2026-11-17
generated: { by: llm-wiki-agent/1, at: 2026-11-17T06:46:43Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-agentenv-2026
    resource: ../raw/agentenv-pydantic-ai/index.md
    scope: ../raw/agentenv-pydantic-ai/
    kind: article
    revision: sha256:5d786679bdd474040198f8ac22c6246bb5e98ba7e9f75bf46d511e233f39721e
    title: "Pydantic AI is now a supported agent in AgentEnv Framework"
---

AgentEnv Framework offers a way to evaluate a Pydantic AI agent on a seeded application environment and verify the resulting task outcome, rather than only grading a response to a fixed prompt. **Reported:** Pydantic's 2026-11-06 announcement describes a first-party integration but names no Pydantic AI, Harness, or AgentEnv version; the behavior below is version-unknown and not independently tested.[^pydantic-agentenv-2026]

## Architecture and comparison

**Reported, versions unknown:** An environment provides applications and seed data; a version-pinned task graph deploys the environment and agent, prompts the agent, and verifies the outcome. Environment tools are exposed over MCP; agents connect over A2A. The author claims pinned versions reproduce the original on rerun; model nondeterminism and the conditions necessary for reproducibility are not discussed. The same task, environment and verifier can be used to compare agent implementations, but equivalent settings and repeated runs are still important to a meaningful comparison (**Synthesis**).[^pydantic-agentenv-2026]

The `pydantic-ai` integration runs an `Agent` in process with the [Harness](pydantic-ai-harness.md) `Coder` capability, exposing `shell`, `read_file`, `write_file`, `edit_file`, `list_files`, `grep`, and `delegate_task`. The article reports that shell commands receive `PATH`, `HOME`, and locale, not the model key; this is not a general security audit or proof that other secrets cannot be exposed. MCP servers, skills, peer agents and live trajectories use A2A extensions.[^pydantic-agentenv-2026]

A context maps to a conversation on the agent's own disk; follow-up tasks continue it while that agent is up. To move to a new instance, the reported snapshot flow saves and restores the conversation and optionally the workspace. The source does not specify persistence guarantees or snapshot storage and isolation.[^pydantic-agentenv-2026]

## Configuration and smoke task

**Reported, versions unknown; commands not executed:** install with `uv tool install agentenv-framework`, then check with `agent-env run hello`. The article says nothing is configured by default. Its `.agentenv/config.toml` example sets `model.base_url` to `https://gateway-us.pydantic.dev/proxy/openai`, `model.api_key` to `env:PYDANTIC_AI_GATEWAY_API_KEY`, `model.roles.agent` to `gpt-5.5`, and `agents.default_a2a_agent_id` to `pydantic-ai`. Export the named environment variable before running; the key value is not stored in the configuration. For this integration, use the organization's Gateway Connect URL without `/v1`: the agent appends `/chat/completions`. The EU region has a different host. The article reports support for OpenAI-compatible endpoints and a `vllm:` model prefix selecting Pydantic AI's vLLM provider.[^pydantic-agentenv-2026]

For the example, copy the externally linked `mail-mcp` bundle and add to `tasks/smoke.json` a `deploy_agent` step depending on `deploy_env`, then a `prompt_agent` step asking who sent the invoice, followed by `env_outcome_verifier` depending on the prompt. Run the copy with `agent-env run ./my-mail`. The source reports a three-email seed, an MCP `search_emails` tool, trajectory and reply in the output, and an invoice-finding verifier; the original sample task deploys the environment and verifier but does not include the agent steps. The first run also builds an environment gateway and reportedly takes a few minutes. Changing `a2a_agent_id` to `claude-code` is the article's comparison example, not a measured benchmark.[^pydantic-agentenv-2026]

For [Logfire Gateway](pydantic-ai-gateway.md), the article says to enable Gateway telemetry and choose a project; model calls using the Gateway API key then appear as Logfire spans without modifying the agent. This is model-call tracing, not evidence that every environment action or verifier result is traced.[^pydantic-agentenv-2026]

## Limits and coverage

The source is a Pydantic vendor announcement about its own integration, not independent corroboration. The local capture and its attachment inventory were inspected; `assets/agentenv-pydantic.webp` is a decorative logo image, excluded from evidence. The AgentEnv repository, sample bundle, provider docs, A2A extension details and other external links were not fetched. License, exact revisions, verifier implementation and nondeterminism controls are unspecified. No packages were installed, commands run, keys supplied, sandbox deployed, outcomes scored or traces checked. All runtime claims are **Reported**, not reproduced.[^pydantic-agentenv-2026]

## Relationships

- **Uses** [Pydantic AI Harness](pydantic-ai-harness.md) `Coder` for the in-process agent, according to the article.[^pydantic-agentenv-2026]
- **Complements** [Pydantic Evals](pydantic-evals.md): **Synthesis**, environment-outcome verification is a distinct evaluation route; the article does not claim it invokes Pydantic Evals.[^pydantic-agentenv-2026]
- **Uses** [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md) as the tool-protocol context and [Pydantic AI Gateway](pydantic-ai-gateway.md) as an optional model route; the exact MCP client configuration is not specified.[^pydantic-agentenv-2026]

[^pydantic-agentenv-2026]: Laís Carvalho, “Pydantic AI is now a supported agent in AgentEnv Framework,” Pydantic, published 2026-11-06, local capture `raw/agentenv-pydantic-ai/index.md`, sha256:5d786679bdd474040198f8ac22c6246bb5e98ba7e9f75bf46d511e233f39721e, original https://pydantic.dev/articles/agentenv-pydantic-ai. Sections “What AgentEnv Framework is”, “Pydantic AI inside AgentEnv”, “Try it”, and “Why this matters”. Evidence class: **Reported**, vendor announcement; external links and implementation not inspected.
