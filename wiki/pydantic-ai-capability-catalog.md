---
type: Concept
title: Pydantic AI capability catalog
description: The vendor's own inventory of the capabilities Pydantic AI ships — every entry tagged core or Harness, grouped by the job it does, with the deferral, compaction and loop-customization rules that decide which one to attach.
tags: [pydantic-ai, agents, llm-frameworks, catalog]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:37:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-capabilities-overview
    resource: ../raw/capabilities/overview/index.md
    scope: ../raw/capabilities/overview/
    kind: docs
    revision: sha256:6434ebdb6f8a86b177d4659f738e214d9f719260787ae93cd1bcda3811bd15c
    title: "Capabilities"
---

This page is the retrieval map for "what does Pydantic AI already ship for this job, and does it come from core or the Harness": the vendor's capabilities overview page is a single catalog of every capability the project documents, and each entry names the package it ships from[^pydantic-docs-capabilities-overview] The split is not arbitrary. Core (`pydantic-ai`) ships only the capabilities that need model or framework support — provider-native tools, provider APIs, and deep loop integration — while [Pydantic AI Harness](pydantic-ai-harness.md) ships everything else, from a single capability to a complete agent, and both compose with each other and with capabilities you write[^pydantic-docs-capabilities-overview] The page names no Pydantic AI version and no date, so the inventory is a snapshot of the vendor's documentation at capture rather than a manifest tied to a release.

## What the catalog is for, and what it is not

The capability is the primary extension point, so "is there a capability for this" is the first build question[^pydantic-docs-capabilities-overview] The page's own boundary is drawn against plain configuration: `instructions` and `model_settings` stay parameters on `Agent` (or `AgentSpec`), and capabilities are for behaviour that goes beyond them — tools, lifecycle hooks, custom extensions — which is exactly why reuse across several agents and loading from a spec file are argued as their payoff[^pydantic-docs-capabilities-overview] The declarative `Capability` form, subclassing and the `Agent(capabilities=[...])` attachment are compiled in [capability primitive](pydantic-ai-capability-primitive.md).

Two loading rules sit on top of the catalog:

- **Deferred capabilities.** Any capability can be loaded by the model on demand; an on-demand capability keeps its instructions and tools hidden until the model loads the bundle, which gates a workflow's or skill's tools as one unit[^pydantic-docs-capabilities-overview]
- **Tool search.** Where the problem is individual tools inside a large catalog rather than a bundle, tool search is the other lever; the two are separate mechanisms[^pydantic-docs-capabilities-overview]

Capabilities that can be declared in YAML/JSON agent specs are listed on the agent-spec page — the serializable subset, with `from_spec` as the opt-in for custom ones, recorded in [agent specs](pydantic-ai-agent-specs.md) — and ACP, serving any agent to editors such as Zed over the Agent Client Protocol, is marked experimental and Harness-shipped in this catalog[^pydantic-docs-capabilities-overview]

## Harnesses: whole agents that come apart

A harness is a complete agent stack published as one regular, combined capability: one import gives a working agent, and each can be taken apart into the blocks catalogued below[^pydantic-docs-capabilities-overview]

| Harness | Package | What it provides |
| --- | --- | --- |
| Coder | Harness | Coding-agent stack: files, shell, repo context, planning, a read-only explorer sub-agent, context controls |
| Researcher | Harness | Web-research stack: search, page fetching, a delegated sub-researcher, bounded tool output |

`Coder` is the same whole agent that [Pydantic AI AgentEnv evaluation](pydantic-ai-agentenv-evaluation.md) installs and that [Claude Agent SDK versus Pydantic AI](claude-agent-sdk-vs-pydantic-ai.md) contrasts with a bundled external harness.

## Execution environments

Core ships only the local workspace; every sandbox backend is Harness[^pydantic-docs-capabilities-overview]

| Capability | Package | What it does |
| --- | --- | --- |
| Local Workspace | Core | Gives tools `ctx.workspace` to run commands and edit files on this machine; adds no tools; no isolation |
| FileSystem | Harness | Read, write, edit and search files under a root; path-traversal and symlink safe, secrets read-only |
| Smart Search | Harness | Behavioural code search in the run's workspace: plain-English queries, ranked excerpts, judged by a decision model (System One, or TypeSafe's Jev, recommended) |
| Shell | Harness | Command execution with allowlists, denylists, timeouts and credential-stripping |
| Modal, E2B, Kubernetes, Render, Sprites, Daytona, boxd, Smol, BoxLite, OpenSandbox | Harness | Commands and files in that vendor's cloud or local sandbox; `Smol` and `BoxLite` are micro-VMs on your own machine with no cloud account, `OpenSandbox` runs on your own server |
| Docker Container | Harness | Commands and files in a local Docker or Podman container |
| SSH Workspace | Harness | Commands and files on a remote host over your `ssh` client; no isolation |
| Bubblewrapped Workspace | Harness | Wraps another workspace capability so its commands run under Linux bubblewrap on that workspace's host; best-effort, explicitly not a security boundary |

The workspace API and the sandbox list are compiled in [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md); this table adds which package each backend ships from and the two security qualifiers the catalog states — `Local Workspace` and `SSH Workspace` add no isolation, and bubblewrap is a convenience rather than a boundary[^pydantic-docs-capabilities-overview]

## Tools and native abilities

All four are core, because each needs provider or loop support[^pydantic-docs-capabilities-overview]

| Capability | What it does |
| --- | --- |
| MCP | Connect any MCP server's tools; local by default, provider-native connectors opt-in |
| Image Generation | Generate and edit images; provider-native where supported, direct image-model fallback elsewhere |
| File Understanding | Describe images, documents, audio and video the model cannot read, with a model that can |
| Native Tool | Register any provider-native tool with the agent |

The first three are compiled in [MCP integration](pydantic-ai-mcp-integration.md), [image generation](pydantic-ai-image-generation.md) and [file understanding](pydantic-ai-file-understanding.md); the native-versus-local routing they share is in [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md), and the native-tool layer the `Native Tool` row names — its nine tools and their per-provider support — is in [native tools](pydantic-ai-native-tools.md) and [native tool configuration](pydantic-ai-native-tool-configuration.md).

## Integrations

Every integration in the catalog is Harness, and most are a thin capability over that service's own hosted MCP server rather than a bespoke client[^pydantic-docs-capabilities-overview]

| Capability | Connects to |
| --- | --- |
| GitHub, Linear, Google Workspace, Notion, Slack, Day AI, Grain, Pylon, PostHog, Logfire MCP, Ordinal | That service's hosted MCP server |
| LocalStack | An emulated AWS environment with AWS CLI tools |
| Macroscope | A local Macroscope code review, handed to the agent |
| StackOne | Linked SaaS accounts (HRIS, ATS, CRM, …) |

The Logfire one is compiled in [Logfire MCP server](logfire-mcp-server.md). The hosted-MCP shape is the same integration economics the MCP overview argues: a service written once as an MCP server is reachable from every MCP-speaking application[^pydantic-docs-capabilities-overview]

## Web and research

| Capability | Package | What it does |
| --- | --- | --- |
| Web Search | Core | Provider-native search where available, local DuckDuckGo fallback everywhere |
| Web Fetch | Core | Fetch and read URLs, native or local |
| X Search | Core | Search X; native on xAI, subagent fallback elsewhere |
| Citations | Core | Ask providers to cite the documents and pages behind the answer |
| Exa Search, Exa Agent | Harness | Exa web research: excerpted search and full-page reads, or the Exa Agent API for open-ended research |
| You.com Search, You.com Research | Harness | Web search and page reads, or cited answers through the You.com Answer, Research and Finance Research APIs |
| Keenable Search | Harness | Exa-like excerpted search and full-page reads, keyless and with nothing extra to install |
| Browser Use | Harness | Hands a web task to an autonomous browser-use agent driving a real browser |
| Playwright Browser | Harness | Drives a real Chromium page yourself: navigate, click, type, read, inspect |

The core four are the *provider-adaptive* group — one capability name over a native tool and a local fallback — which is compiled, with its defaults and install extras, in [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md). `Citations` is the fifth core entry in this group but not provider-adaptive: it adds no tool, it asks the provider to attach provenance to results already returned, and its asking surface, `TextPart.citations` shape and structured-output veto are compiled in [Pydantic AI citations](pydantic-ai-citations.md).

## Reasoning, planning and delegation

`Thinking` is the only core entry here; the rest are Harness[^pydantic-docs-capabilities-overview]

| Capability | Package | What it does |
| --- | --- | --- |
| Thinking | Core | Provider-adaptive extended thinking at configurable effort |
| Planning | Harness | Model-owned task plans with a cache-safe live reminder |
| Subagents | Harness | Delegate self-contained tasks to named child agents |
| Dynamic Workflow | Harness | The model orchestrates sub-agents from one Python script — fan-out, chain, vote in a single tool call — with hard `max_agent_calls` budgets |
| [Advisor](pydantic-ai-harness-advisor.md) | Harness | Lets an executor consult a stronger model mid-run |
| [Background Tools](pydantic-ai-harness-background-tools.md) | Harness | Runs selected tools concurrently; results arrive as follow-up messages |

`Thinking` maps onto each provider's native control in [thinking and reasoning control](pydantic-ai-thinking.md); the model-written choreography behind `Dynamic Workflow` is described in [Pydantic AI Harness](pydantic-ai-harness.md) and [code as the agent graph](code-as-agent-graph.md).

## Context management

This is the group where a name can appear twice: **Compaction** exists in core as provider-native summarisation and in Harness as model-agnostic strategies, so the split is by mechanism rather than by package[^pydantic-docs-capabilities-overview]

| Capability | Package | What it does |
| --- | --- | --- |
| Code Mode | Harness | Model writes one Python script calling many tools inside a Monty sandbox: one round-trip instead of N, intermediate results never enter context |
| IPython Code Mode | Harness | Code Mode with a persistent IPython kernel instead of Monty; full CPython and installed packages, state kept between calls; local agents only, not a sandbox |
| Tool Search | Core | Load tool definitions on demand instead of carrying hundreds in every prompt |
| Caching | Core | Provider-adaptive prompt caching of tools, instructions and conversation at a configurable retention |
| Compaction (native) | Core | OpenAI and Anthropic provider-native compaction; the provider summarises history server-side |
| Compaction (model-agnostic) | Harness | Tool-result clearing, sliding-window trimming, LLM summarisation, tiered; all window-relative, with live usage reporting |
| Tool Output Limits | Harness | Truncate, spill to a queryable file, or summarise oversized tool returns at the source |
| Warn On Cache Busts | Harness | Detects prompt-cache prefix collapses between requests from the provider's own numbers |

The catalog's framing of the whole group is the reason it is worth reading: this is "the difference between an agent that degrades over a long run and one that doesn't, and between paying for tokens N times or once"[^pydantic-docs-capabilities-overview] Code Mode and IPython Code Mode are compiled in [code mode](pydantic-ai-code-mode.md) and [IPython Code Mode](pydantic-ai-ipython-code-mode.md); caching in [prompt caching](pydantic-ai-prompt-caching.md) and [Anthropic prompt caching](anthropic-prompt-caching.md).

## Knowledge and memory

Every entry is Harness, and the grouping separates what the agent remembers from the conversation history it is already in — persistence of that history is a separate page[^pydantic-docs-capabilities-overview]

| Capability | What it does |
| --- | --- |
| Memory | A persistent, namespaced notebook: bounded prompt injection, on-demand search; in-memory, file and Postgres stores |
| Pixeltable | Query and search allowed Pixeltable tables; also persists the memory notebook there |
| Conversation Search | BM25 search over stored history, including turns compaction dropped |
| Skills | Load Agent Skill (`SKILL.md`) instructions on demand |
| Repo Context | Start runs oriented: `AGENTS.md`/`CLAUDE.md` plus repository structure |
| Pydantic AI Docs | On-demand Pydantic AI documentation lookup |

The persistence split — a capability's store versus the conversation history itself — is the distinction [conversation state](pydantic-ai-conversation-state.md) documents; the recall pair is analysed in [self-improving agent loops](self-improving-agent-loops.md).

## Control and safety

Two entries are core, both about the loop stopping for a human; the rest are Harness[^pydantic-docs-capabilities-overview]

| Capability | Package | What it does |
| --- | --- | --- |
| Guardrails | Harness | Validate, block or redact user input, tool calls, tool results and output, including secret masking and parallel async guards |
| Prompt Injection Defender | Harness | Classifies local tool results for indirect prompt injection and can withhold high-risk results |
| Artifact Scanning | Harness | Scans memory files and skills for prompt injection, credential exfiltration and hidden content before they are stored or loaded |
| Spend Limits | Harness | Cross-window USD and token budgets plus per-response cost tracking, per model and per tenant |
| Ask User | Harness | The model asks the user multiple-choice questions mid-run; you supply the answerer (terminal, web, test) |
| System Reminders | Harness | Cache-safe re-injection of guidance mid-run to counter instruction fade |
| Detect Loops | Harness | Notices repeated tool calls, results, alternations, responses, or a response repeating itself as it streams, then nudges, stops, or calls your handler |
| Trajectory Judge | Harness | A second model reviews the live run every N requests over a sliding token window and steers it mid-run |
| Refine Output | Harness | Sends the agent back to review and revise its output before the run ends |
| Tool approval | Core | Flags tool calls that need human approval before they run |
| Handle Deferred Tool Calls | Core | Resolves approvals, answers and external results on deferred calls inside the run, in place or by waiting, durably on AWS Lambda |

Approval is compiled in [deferred tool approval](pydantic-ai-deferred-approvals.md). The grouping is itself the selection advice: the harness-side entries are the ones that police content and cost, and the core pair is the one that pauses the loop for a decision.

## Self-extension

| Capability | Package | What it does |
| --- | --- | --- |
| Capability Creation | Harness | The agent writes, validates and persists *new capabilities* during a run; the host loads them into a later run via `load_active(workspace)` and `capabilities=` |

## Execution runtime

Everything outside the loop that makes a run survive, be observed, or be configured in production[^pydantic-docs-capabilities-overview]

| Capability | Package | What it does |
| --- | --- | --- |
| Durable execution | Core | Runs that survive restarts and failures on Temporal, DBOS or Prefect, with Restate and Airflow integrations |
| Instrumentation | Core | OpenTelemetry GenAI spans for every model and tool call; the raw material for Logfire traces |
| Thread Executor | Core | Run sync tools on a shared thread pool |
| Batch Model Requests | Core | Send model requests through provider batch APIs at batch prices — [batch processing](pydantic-ai-batch-processing.md) |
| AWS Lambda durability | Harness | Checkpoints model requests and tool calls into AWS Lambda durable function steps |
| Absurd durability | Harness | Checkpoints model requests, MCP calls and tool calls into Absurd steps on PostgreSQL |
| pgtask durability | Harness | The same checkpointing into pgtask steps on PostgreSQL |
| Render Workflows | Harness | Model requests and tool calls as chained task runs with separate retries, timeouts and compute settings; retrying the task that runs the agent can repeat completed work |
| Step Persistence | Harness | Save, restore, resume (`continue_run`) and fork (`fork_run`) runs; file, SQLite and MongoDB backends |
| Managed Prompt | Harness | Back instructions with a Logfire-managed prompt so it can be versioned and rolled out without redeploying |
| Repair Tool Arguments | Harness | Repairs malformed JSON tool arguments before schema validation |

Durability is compiled in [durable execution](pydantic-ai-durable-execution.md), observability in [Pydantic AI observability](pydantic-ai-observability.md). The catalog's "Execution runtime" grouping is the useful part: it is the vendor's own statement that durability, tracing, prompt management and argument repair are capabilities rather than framework hooks.

## Loop customization

Core also ships capabilities for customising the agent loop itself, "mostly for production servers"[^pydantic-docs-capabilities-overview] All thirteen are core:

| Capability | What it does |
| --- | --- |
| Hooks | Decorator-based lifecycle hook registration |
| Select Model | Select a static or per-step model with a callable |
| Model Fallback | Attempt other models when a request fails or its response is rejected |
| Retry On Model Errors | Attempt the same model again when a request fails with a transient error |
| Resolve Model ID | Resolve custom, application-specific model IDs with a callable |
| Prepare Tools / Prepare Output Tools | Filter or modify function and output tool definitions per step |
| Prefix Tools | Wrap a capability and prefix its tool names |
| Include Tool Return Schemas | Include return type schemas in tool definitions sent to the model |
| Set Tool Metadata | Merge metadata key-value pairs onto selected tools |
| Raise Content Filter Error | Raise `ContentFilterError` whenever a model response has `finish_reason='content_filter'` |
| Reinject System Prompt | Reinject the configured system prompt when the incoming history is missing one |
| Process History | Wrap a history processor |
| Process Event Stream | Forward agent stream events to a handler function |

This table is the strongest evidence in the catalog that the loop itself is now configured by attaching capabilities: model selection, retries, fallback, tool-shape rewriting and content-filter escalation are all capabilities rather than constructor flags[^pydantic-docs-capabilities-overview] Hooks are compiled in [lifecycle hooks](pydantic-ai-lifecycle-hooks.md), fallback in [model fallback](pydantic-ai-model-fallback.md), tool preparation in [structured output](pydantic-ai-structured-output.md), and history and stream processing in [streamed output](pydantic-ai-streamed-output.md) and [conversation state](pydantic-ai-conversation-state.md).

## Authoring primitives named beside the catalog

The page closes the inventory with the two primitives a custom capability is built from: `Capability` for bundling behaviour without subclassing, and `Toolset` for wrapping an `AbstractToolset`[^pydantic-docs-capabilities-overview] Both are compiled in [capability primitive](pydantic-ai-capability-primitive.md).

## Reconciling the earlier lists

Earlier pages in this wiki recorded the capability set from press coverage and a third-party tour, not from the vendor's own catalog. The catalog corroborates most of the later v2.59-era list — `Coder`, `Researcher`, `Memory`, `Guardrails`, `Spend Limits`, `Subagents`, `Planning`, `Code Mode`, `Step Persistence`, `Compaction` and the AWS Lambda, Absurd and pgtask durability integrations all appear here with the same package attribution — and adds roughly eighty entries the press lists never mentioned, chiefly the sandbox and integration families[^pydantic-docs-capabilities-overview]

Two earlier names are absent from the catalog and are left standing as unresolved in [Pydantic AI Harness](pydantic-ai-harness.md): the newsroom's `ContextManagerCapability` and `ConsoleCapability`, which match nothing here by name (the closest entries are `Compaction` and `Local Workspace`/`Shell`/`FileSystem`)[^pydantic-docs-capabilities-overview] `TodoCapability` likewise has no entry; [Pydantic AI Harness planning](pydantic-ai-harness-planning.md) resolves that one separately — the first-party `Planning` capability supersedes Vstorm's community `pydantic-ai-todo`, so the newsroom name and the catalog name describe the same job. Because the catalog itself names no version and no date, this page cannot date the rename or the removal, and neither reading is chosen.

## Limits

- The source is a single vendor catalog page: no Pydantic AI or Harness version, no publication or update date, no author and no licence stated, so this inventory is a snapshot of the documentation at capture and every per-item maturity is unstated[^pydantic-docs-capabilities-overview]
- Every entry is one line of marketing copy. No capability's API, configuration keys, dependency footprint, prompt cost or failure mode is documented here; the pages that do own those details are linked per group.
- Package attribution is the vendor's claim, not a check: no package was installed and no import was attempted, so whether a given capability is importable from `pydantic_ai.capabilities` or `pydantic_ai_harness` is **Reported** only.
- The catalog is one page and will drift: capability names, groupings and package placement change between releases, which is why this page carries a `stale_after` date.
- Sandbox and integration vendors are named without any comparison, price, region or isolation guarantee; the deeper entries (`FileSystem`'s read-only secrets, `Smart Search`'s recommended judge, `Render Workflows`' repeat hazard) are the vendor's own qualifiers, not measured.
- Evidence class: **Reported** throughout. Nothing was installed, constructed, imported or run.

## Relationships

- **Indexes** the [Pydantic AI Harness](pydantic-ai-harness.md) tier: every Harness entry above is one row of the tier that page argues for, and the two-package split is the catalog's own organising rule.
- **Catalogs instances of** the [capability primitive](pydantic-ai-capability-primitive.md): the catalog is what the primitive is used to build, including the declarative `Capability` form and the `defer_loading` catalog entry.
- **Depends on** [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md) for the routing rules behind the web, image and MCP rows.
- **Points to** [capability events](pydantic-ai-capability-events.md) for how the catalog's reusable capabilities coordinate with each other at run time.
- **Supplies lowering targets for** [code mode](pydantic-ai-code-mode.md), [IPython Code Mode](pydantic-ai-ipython-code-mode.md), [thinking](pydantic-ai-thinking.md), [prompt caching](pydantic-ai-prompt-caching.md), [deferred tool approval](pydantic-ai-deferred-approvals.md), [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md), [durable execution](pydantic-ai-durable-execution.md), [observability](pydantic-ai-observability.md) and [model fallback](pydantic-ai-model-fallback.md).
- **Corroborates** the v2.59-era Harness inventory recorded from a third-party tour and leaves two press-only names unresolved.
- **Has its Harness rows compiled in** [Coder](pydantic-ai-harness-coder.md), [researcher](pydantic-ai-harness-researcher.md), [file system](pydantic-ai-harness-filesystem.md), [shell](pydantic-ai-harness-shell.md), [smart search](pydantic-ai-harness-smart-search.md), [memory](pydantic-ai-harness-memory.md), [skills](pydantic-ai-harness-skills.md), [documentation lookup](pydantic-ai-harness-docs.md), [ask user](pydantic-ai-harness-ask-user.md), [prompt injection defender](pydantic-ai-harness-prompt-injection-defender.md), and the two sandbox workspaces [Modal](pydantic-ai-harness-modal-sandbox.md) and [E2B](pydantic-ai-harness-e2b-sandbox.md) — every one naming no Harness version.

[^pydantic-docs-capabilities-overview]: Pydantic Docs, "Capabilities" (https://pydantic.dev/docs/ai/capabilities/overview/; 4,642 words as declared, 5,228 by local `wc -w`; language `en`; no publication date and no Pydantic AI or Harness version). Sections used: §intro (capability definition, the bundled parts, always-on versus on-demand, tool search, the Harness and third-party pointers, durable-execution pointer); §"Available capabilities" (the core-versus-Harness rule and package column); §"Harnesses" (Coder, Researcher); §"Execution environments" (Local Workspace plus the sixteen Harness backends, the no-isolation and best-effort-bubblewrap qualifiers); §"Tools & native abilities" (the four core entries); §"Integrations" (the fourteen Harness entries and the grouped Integrations page); §"Web & research" (four core, seven Harness); §"Reasoning, planning & delegation"; §"Context management" (both Compaction rows, Tool Search, Caching, Tool Output Limits, Warn On Cache Busts); §"Knowledge & memory"; §"Control & safety" (nine Harness, two core); §"Self-extension"; §"Execution runtime"; §"Loop customization" plus the ACP note; and the closing paragraph naming the `Capability` and `Toolset` primitives. Local capture: `raw/capabilities/overview/index.md`, content digest sha256:6434ebdb. Evidence class: **Reported** — vendor documentation naming no release version; nothing was installed, imported, constructed or executed.
