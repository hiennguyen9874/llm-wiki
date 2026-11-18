---
title: "Pydantic AI Harness"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/harness/"
domain: "pydantic.dev"
language: "en"
description: "Pydantic AI Harness is the official capability library for Pydantic AI: a coding agent, file and shell tools, memory, subagents, and context management."
word_count: 4157
---

*Your agent’s favorite harness, built on Pydantic AI*

[![Join Slack](assets/Slack-Join-Slack-4A154B.svg)](https://logfire.pydantic.dev/docs/join-slack/)

**Pydantic AI Harness** is the official [capability](https://pydantic.dev/docs/ai/capabilities/overview/) and harness library for [Pydantic AI](https://pydantic.dev/docs/ai/overview/). Every Pydantic AI agent already has a light harness: the typed agent loop, [any model](https://pydantic.dev/docs/ai/models/overview/), your own tools, structured output. For simple agents that’s enough. But set an agent loose on complex, long-running work (fix a codebase, research a question, run for hours unattended) and what it needs around the model grows: a [workspace](https://pydantic.dev/docs/ai/harness/filesystem/) to act in, a [plan](https://pydantic.dev/docs/ai/harness/planning/) it keeps current, [memory](https://pydantic.dev/docs/ai/harness/memory/) that carries across sessions, [sub-agents](https://pydantic.dev/docs/ai/harness/subagents/) to hand work to, [context management](https://pydantic.dev/docs/ai/harness/compaction/) for long runs, and [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) that survives a restart. **Pydantic AI Harness** ships that harness.

Everything here is one primitive: a [capability](https://pydantic.dev/docs/ai/capabilities/overview/), a self-contained unit of agent behavior you add to `capabilities=[...]` on any agent. There are [90+ of them](#capabilities), and complete agents like [Coder](https://pydantic.dev/docs/ai/harness/coder/) and [Researcher](https://pydantic.dev/docs/ai/harness/researcher/) are themselves combinations of capabilities. Use a single capability, compose your own set, or start from the whole coding agent and swap parts out.

## Pydantic AI, the Harness, and CLAI

Three packages, each built on the one before it. Start with the one that matches what you are doing:

| Package | What it is | Start here when |
| --- | --- | --- |
| [Pydantic AI](https://pydantic.dev/docs/ai/overview/) (`pydantic-ai`) | The agent framework: the agent loop, models from every major provider, tools, structured output, and the capability system | You are building an agent, or an LLM feature in your own application |
| [Pydantic AI Harness](#capabilities) (`pydantic-ai-harness`) | Capabilities for a Pydantic AI agent: workspaces, file and shell tools, memory, sub-agents, context management, and complete agents like `Coder` | Your agent needs to edit files, run commands, remember, delegate, or keep working through long runs |
| [CLAI](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_clai2) (`pydantic-clai2`) | A coding agent for your terminal, run as `clai2`, built on the Harness’s `Coder` and extended with plugins | You want to use a coding agent rather than build one, or chat with your own agent in a terminal |

Each package installs the one it is built on: `pydantic-ai-harness` installs `pydantic-ai-slim`, and `pydantic-clai2` installs `pydantic-ai-harness`. CLAI is not the [`clai` chat CLI](https://pydantic.dev/docs/ai/integrations/cli/) that ships with Pydantic AI.

## Quick start

- [pip](#tab-panel-0-0)
- [uv](#tab-panel-0-1)

Terminal

```bash
pip install "pydantic-ai-harness[coder,anthropic]"
```

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness.coder import Coder

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[LocalWorkspace('.'), Coder()],
)
result = agent.run_sync('Find out why tests/test_parser.py fails and fix the bug it caught.')
print(result.output)
```

`LocalWorkspace('.')` is where the agent works: its file tools and commands run on your machine, in this directory. It is not a sandbox, so commands can reach anything you can. To run the same agent in an isolated cloud machine, swap it for a sandbox capability (Modal, E2B, Render, Sprites, Daytona, or boxd); see [Workspaces](#workspaces).

With [Modal](https://pydantic.dev/docs/ai/harness/modal-sandbox/), for example:

```python
from pydantic_ai_harness.modal_sandbox import ModalSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[ModalSandbox(), Coder()])
```

Coder provides six tools: `read_file`, `write_file`, `edit_file`, `list_files`, `grep`, and `shell`, plus `delegate_task` to hand a sub-task to a fresh run of the same agent, repository context, and context controls. Shell commands are unrestricted and can persist beyond individual runs. Default instructions guide autonomous investigation, editing, and verification; pass `instructions=` to add your own guidance.

Terminal

```bash
uvx --with "pydantic-ai-harness[coder]" clai -a pydantic_ai_harness.coder:coder_agent -m anthropic:claude-opus-5-5
```

The bundled `coder_agent` is the example above without a model.

Every model works: swap the string for [any provider’s](https://pydantic.dev/docs/ai/models/overview/). Need more? Add capabilities to the list; here’s the same coder on `gpt-6.1-sol`, with web search and cross-session memory:

- [pip](#tab-panel-1-0)
- [uv](#tab-panel-1-1)

Terminal

```bash
pip install "pydantic-ai-slim[openai]"
```

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace, WebSearch
from pydantic_ai_harness import Coder, Memory
from pydantic_ai_harness.memory import FileMemoryStore

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[
        LocalWorkspace('.'),
        Coder(),
        WebSearch(),  # look up docs and error messages on the web
        Memory(FileMemoryStore('.agent-memory')),  # remembers across sessions
    ],
)
```

[Skills](https://pydantic.dev/docs/ai/harness/skills/) (your `SKILL.md` procedures, loaded on demand; point it at a `skills/` directory and add the `skills` extra), [Web Fetch](https://pydantic.dev/docs/ai/capabilities/web-fetch/), [Guardrails](https://pydantic.dev/docs/ai/harness/guardrails/), and [Dynamic Workflow](https://pydantic.dev/docs/ai/harness/dynamic-workflow/) slot in the same way.

## Built from capabilities

`Coder` is a regular combined capability: [`FileSystem`](https://pydantic.dev/docs/ai/harness/filesystem/) with five of its tools and content hashes off, [`Shell`](https://pydantic.dev/docs/ai/harness/shell/) with its persistent `shell` tool and no allowlist, [`RepoContext`](https://pydantic.dev/docs/ai/harness/repo-context/), [`SubAgents`](https://pydantic.dev/docs/ai/harness/subagents/) delegating to the agent itself, [`ClearToolResults`](https://pydantic.dev/docs/ai/harness/compaction/), and a bounded [`ToolOutputLimits`](https://pydantic.dev/docs/ai/harness/tool-output-limits/), plus its default instructions and JSON argument repair. Use it whole, or build the same agent from those capabilities to change any setting; the [Coder page](https://pydantic.dev/docs/ai/harness/coder/) lists the exact configuration, tool signatures, delegation, and the persistent shell lifecycle.

On a remote sandbox, `Coder` loads repo instructions at run start and may create the sandbox before the first model tool call. Use `Coder(repo_context=False)` for lazy creation.

## Workspaces

A [workspace](https://pydantic.dev/docs/ai/core-concepts/workspace/) is where the agent’s files and commands live: your machine with `LocalWorkspace`, or an isolated sandbox. Harness capabilities never pick one for you. Attach one, or the run fails at its start and tells you what to attach.

[Coder](https://pydantic.dev/docs/ai/harness/coder/), [FileSystem](https://pydantic.dev/docs/ai/harness/filesystem/), [Shell](https://pydantic.dev/docs/ai/harness/shell/), [Repo Context](https://pydantic.dev/docs/ai/harness/repo-context/), and [Macroscope](https://pydantic.dev/docs/ai/harness/macroscope/) work in the run’s workspace, starting in its working directory. To work in a subdirectory, set it on the workspace: `LocalWorkspace('./repo')`. To continue in the same files from a later run or another agent, see [Sharing a workspace](https://pydantic.dev/docs/ai/harness/coder/#sharing-a-workspace).

Skills, SubAgents, ToolOutputLimits, and Memory’s `FileMemoryStore` use the run’s workspace for their own files too. To keep those files on your machine while the agent works in a sandbox, point them at a local location:

```python
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai_harness import Memory, ToolOutputLimits
from pydantic_ai_harness.memory import FileMemoryStore
from pydantic_ai_harness.tool_output_limits import LocalFileOverflowStore

memory = Memory(FileMemoryStore('.', workspace=LocalWorkspaceBackend('/var/lib/myapp/memory')))  # notes on this machine
limits = ToolOutputLimits(store=LocalFileOverflowStore())  # spills in this machine's temp directory
```

By default, harness files (Shell’s background job logs, tool-output spills) go in `.pydantic-ai-harness/` in the workspace’s working directory, which is git-ignored. When the workspace user cannot write to the working directory, Shell keeps its job files in a directory private to that user under the workspace’s temp directory (`$TMPDIR` in its environment, or `/tmp`) instead.

Step Persistence’s file and SQLite stores, Media’s disk and SQLite stores, and Code Mode mounts use paths on the machine running the agent, not the run’s workspace.

`FileSystem`’s `root_dir` limits only the file tools, not `Shell` commands.

Upgrading from an earlier release? The [Coder page](https://pydantic.dev/docs/ai/harness/coder/#upgrading) lists what changed.

## From problem to capability

Look up a capability by the problem it solves. The Capabilities section below lists all of them by what they give your agent.

| If your problem is… | Capability | How it works |
| --- | --- | --- |
| The model’s output must pass a check, and bad output should be retried or blocked | [`OutputGuardrail`](https://pydantic.dev/docs/ai/harness/guardrails/) | Its `guard` returns `GuardrailResult.retry(...)` to send the output back to the model, or `False` to raise `OutputBlocked`. `retry` needs `run()`: under `run_stream()` it raises `UnexpectedModelBehavior`. |
| One tool result is flooding the context window | [`ToolOutputLimits`](https://pydantic.dev/docs/ai/harness/tool-output-limits/) | By default, a result of 10,000 characters or more spills to a file in the run’s workspace, and the model gets a preview plus a handle to read the rest. If the write fails, the result is truncated to 4,000 characters. Without a workspace, pass `store=LocalFileOverflowStore()`. |
| The agent’s files and commands must start in a specific directory | Core [`LocalWorkspace`](https://pydantic.dev/docs/ai/core-concepts/workspace/), or a sandbox | Set the directory on the workspace: `LocalWorkspace('./repo')`, or `working_dir=` on a sandbox. Every capability that works in the workspace starts there; `Shell(cwd=)` and `FileSystem(cwd=)` warn and are ignored. In your own tool, `ctx.workspace.run(..., cwd='subdir')` starts one command elsewhere. |
| A run, a day, or a tenant needs a spend ceiling | Core [`UsageLimits`](https://pydantic.dev/docs/ai/core-concepts/agent/#usage-limits), or [`SpendLimits`](https://pydantic.dev/docs/ai/harness/spend/) | For one run, pass `usage_limits=UsageLimits(cost_limit=Decimal('5'))`: the run raises `UsageLimitExceeded` after the response that crosses the limit. For a day or month, per tenant, or across worker processes, `SpendLimits(budgets=[Budget(usd=Decimal('100'), window='day')])` refuses the next request once a window is spent. |
| The model should get only a few calls to an expensive tool per run | [`ToolBudgets`](https://pydantic.dev/docs/ai/harness/tool-budgets/) | `ToolBudgets(per_tool={'web_search': 3}, refuse_repeats={'web_search'})` answers the fourth call, or an exact repeat, with a tool result saying the budget is used, and the run continues. `UsageLimits.tool_calls_limit` stays the hard ceiling. |
| The model repeats the same tool call without making progress | [`DetectLoops`](https://pydantic.dev/docs/ai/harness/detect-loops/) | The default `action='nudge'` adds a system prompt asking the model to change approach; `action='error'` stops the run with `LoopDetectedError`. |
| The model sends malformed JSON in a tool call | [`RepairToolArguments`](https://pydantic.dev/docs/ai/harness/repair-tool-arguments/) | Runs `json-repair` on the arguments before validation, fixing trailing commas, single-quoted keys and truncated JSON; valid arguments pass through unchanged. Import it from `pydantic_ai_harness.repair_tool_arguments` and install the `repair-tool-arguments` extra. `Coder` includes `RepairToolArguments`, so its `coder` extra installs `json-repair` too. |

## Capabilities

Every capability is a self-contained unit you drop into `capabilities=[...]`, and they all compose, with each other and with your own. Some come with [`pydantic-ai`](https://pydantic.dev/docs/ai/overview/) itself, the rest with this package; the **Package** column says which. 90+ in all, grouped by what they give your agent:

### Harnesses

Complete agent stacks as regular combined capabilities: one import gives you a working agent, and you can take either apart into the blocks below.

| Harness | Package | What it provides |
| --- | --- | --- |
| [Coder](https://pydantic.dev/docs/ai/harness/coder/) | Harness | Six coding tools, persistent shell commands, delegation to itself, autonomous guidance, and context controls |
| [Researcher](https://pydantic.dev/docs/ai/harness/researcher/) | Harness | A complete web-research stack: search, page fetching, a delegated sub-researcher, and bounded tool output |

### Execution environments

The workspace the agent acts in: the files it edits and the commands it runs, local or isolated.

| Capability | Package | What it does |
| --- | --- | --- |
| [FileSystem](https://pydantic.dev/docs/ai/harness/filesystem/) | Harness | Read, write, edit, list, and search files under a root in the run’s workspace, with opt-in ripgrep tools; path-traversal checked, secrets read-only |
| [Smart Search](https://pydantic.dev/docs/ai/harness/smart-search/) | Harness | Code search by behavior in the run’s workspace: plain-English queries, ranked excerpts, judged by any model (a decision model over System One, or TypeSafe’s Jev, recommended) |
| [Shell](https://pydantic.dev/docs/ai/harness/shell/) | Harness | Command execution in the run’s workspace with allowlists, denylists, timeouts, credential-stripping, and opt-in commands that outlive the run |
| [Modal Sandbox](https://pydantic.dev/docs/ai/harness/modal-sandbox/) | Harness | Commands and files in an isolated [Modal](https://modal.com/) cloud sandbox |
| [E2B Sandbox](https://pydantic.dev/docs/ai/harness/e2b-sandbox/) | Harness | Commands and files in an isolated [E2B](https://e2b.dev/) cloud sandbox |
| [Kubernetes Sandbox](https://pydantic.dev/docs/ai/harness/kubernetes-sandbox/) | Harness | Commands and files in a sandbox pod from a Kubernetes [agent-sandbox](https://agent-sandbox.sigs.k8s.io/) warm pool |
| [Render Sandbox](https://pydantic.dev/docs/ai/harness/render-sandbox/) | Harness | Commands and files in an isolated [Render](https://render.com/docs/sandboxes) sandbox |
| [Sprites Sandbox](https://pydantic.dev/docs/ai/harness/sprites-sandbox/) | Harness | Commands and files in a persistent [Fly.io Sprite](https://sprites.dev/) |
| [Daytona Sandbox](https://pydantic.dev/docs/ai/harness/daytona-sandbox/) | Harness | Commands and files in an isolated [Daytona](https://www.daytona.io/) cloud sandbox |
| [boxd Sandbox](https://pydantic.dev/docs/ai/harness/boxd-sandbox/) | Harness | Commands and files in an isolated [boxd](https://boxd.sh/) cloud machine |
| [Smol Sandbox](https://pydantic.dev/docs/ai/harness/smol-sandbox/) | Harness | Commands and files in a [smolvm](https://github.com/smol-machines/smolvm) microVM on your own machine; no cloud account |
| [BoxLite Sandbox](https://pydantic.dev/docs/ai/harness/boxlite-sandbox/) | Harness | Commands and files in a [BoxLite](https://github.com/boxlite-ai/boxlite) micro-VM on your own machine, with an optional egress allow-list; no cloud account |
| [OpenSandbox](https://pydantic.dev/docs/ai/harness/opensandbox-sandbox/) | Harness | Commands and files in a sandbox on your own [OpenSandbox](https://open-sandbox.ai/) server, on Docker or Kubernetes |
| [Docker Container](https://pydantic.dev/docs/ai/harness/docker-container/) | Harness | Commands and files in a local [Docker](https://www.docker.com/) or Podman container |
| [SSH Workspace](https://pydantic.dev/docs/ai/harness/ssh-workspace/) | Harness | Commands and files on a remote host over your `ssh` client; no isolation |
| [Bubblewrapped Workspace](https://pydantic.dev/docs/ai/harness/bubblewrap-sandbox/) | Harness | Wraps another workspace capability so its commands run in a Linux [bubblewrap](https://github.com/containers/bubblewrap) wrapper on that workspace’s host (best-effort convenience, not a security boundary) |

### Tools & native abilities

Abilities the provider executes natively, and connections to any MCP server.

| Capability | Package | What it does |
| --- | --- | --- |
| [MCP](https://pydantic.dev/docs/ai/capabilities/mcp/) | Core | Connect any MCP server’s tools; local by default, provider-native connectors opt-in |
| [Image Generation](https://pydantic.dev/docs/ai/capabilities/image-generation/) | Core | Generate and edit images; provider-native where supported, sub-agent fallback elsewhere |

### Integrations

Tools from third-party services, most through the service’s own hosted MCP server. The [Integrations](https://pydantic.dev/docs/ai/harness/integrations/) page groups them by what they connect to.

| Capability | Package | What it does |
| --- | --- | --- |
| [GitHub](https://pydantic.dev/docs/ai/harness/github/) | Harness | Read and change GitHub repositories, issues, pull requests, and other accessible resources. |
| [Linear](https://pydantic.dev/docs/ai/harness/linear/) | Harness | Read and change Linear issues, projects, teams, and comments. |
| [Macroscope](https://pydantic.dev/docs/ai/harness/macroscope/) | Harness | Run a local [Macroscope](https://docs.macroscope.com/cli) code review and hand the findings to the agent |
| [LocalStack](https://pydantic.dev/docs/ai/harness/localstack/) | Harness | An emulated AWS environment with AWS CLI tools |
| [Google Workspace](https://pydantic.dev/docs/ai/harness/google-workspace/) | Harness | Use Gmail, Calendar, Drive, and other Google Workspace tools. |
| [Notion](https://pydantic.dev/docs/ai/harness/notion/) | Harness | Search and change Notion workspace content. |
| [Slack](https://pydantic.dev/docs/ai/harness/slack/) | Harness | Give an agent Slack messages, channels, and canvas tools. |
| [Day AI](https://pydantic.dev/docs/ai/harness/day-ai/) | Harness | Search and update CRM records and meeting context through [Day AI](https://day.ai/)’s hosted MCP server |
| [Grain](https://pydantic.dev/docs/ai/harness/grain/) | Harness | Search and read meetings, transcripts, and notes, and create clips and tag meetings, through [Grain](https://grain.com/)’s hosted MCP server |
| [Pylon](https://pydantic.dev/docs/ai/harness/pylon/) | Harness | Work with support issues, accounts, and contacts through [Pylon](https://www.usepylon.com/)’s hosted MCP server |
| [StackOne](https://pydantic.dev/docs/ai/harness/stackone/) | Harness | Act on linked SaaS accounts (HRIS, ATS, CRM, …) via [StackOne](https://www.stackone.com/) |
| [PostHog](https://pydantic.dev/docs/ai/harness/posthog/) | Harness | Query product analytics and manage feature flags, experiments, and dashboards through [PostHog](https://posthog.com/)’s hosted MCP server |
| [Logfire MCP](https://pydantic.dev/docs/ai/harness/logfire-mcp/) | Harness | Query Logfire telemetry and manage observability resources. |
| [Ordinal](https://pydantic.dev/docs/ai/harness/ordinal/) | Harness | Draft, schedule, and analyze social posts through [Ordinal](https://www.tryordinal.com/)’s hosted MCP server |

### Web & research

Finding and reading things on the open web.

| Capability | Package | What it does |
| --- | --- | --- |
| [Web Search](https://pydantic.dev/docs/ai/capabilities/web-search/) | Core | Provider-native search where available, local DuckDuckGo fallback everywhere |
| [Web Fetch](https://pydantic.dev/docs/ai/capabilities/web-fetch/) | Core | Fetch and read URLs, native or local |
| [X Search](https://pydantic.dev/docs/ai/capabilities/x-search/) | Core | Search X; native on xAI, subagent fallback elsewhere |
| [Exa Search](https://pydantic.dev/docs/ai/harness/exa-search/) | Harness | Web research via [Exa](https://exa.ai/): excerpted search, full-page reads, opt-in cited deep search |
| [Exa Agent](https://pydantic.dev/docs/ai/harness/exa-search/) | Harness | Delegate open-ended research to the Exa Agent API |
| [You.com Search](https://pydantic.dev/docs/ai/harness/youdotcom/) | Harness | Web search and page reads via [You.com](https://you.com/): query-relevant excerpts or full-page markdown |
| [You.com Research](https://pydantic.dev/docs/ai/harness/youdotcom/) | Harness | Cited answers and multi-step research via the You.com Answer, Research, and Finance Research APIs |
| [Keenable Search](https://pydantic.dev/docs/ai/harness/keenable-search/) | Harness | Web research via [Keenable](https://keenable.ai/): excerpted search and full-page reads, keyless and with no extra to install |
| [Browser Use](https://pydantic.dev/docs/ai/harness/browser-use/) | Harness | Hand web tasks to an autonomous [browser-use](https://github.com/browser-use/browser-use) agent driving a real browser |
| [Playwright Browser](https://pydantic.dev/docs/ai/harness/playwright/) | Harness | Drive a real Chromium page yourself: navigate, click, type, read, and inspect what the page did |

### Reasoning, planning & delegation

How the agent thinks and divides the work.

| Capability | Package | What it does |
| --- | --- | --- |
| [Thinking](https://pydantic.dev/docs/ai/capabilities/thinking/) | Core | Provider-adaptive extended thinking at configurable effort |
| [Planning](https://pydantic.dev/docs/ai/harness/planning/) | Harness | Model-owned task plans with a cache-safe live reminder |
| [Subagents](https://pydantic.dev/docs/ai/harness/subagents/) | Harness | Delegate self-contained tasks to named child agents |
| [Peers](https://pydantic.dev/docs/ai/harness/peers/) | Harness | Discover and message other agent sessions without controlling their runs |
| [Dynamic Workflow](https://pydantic.dev/docs/ai/harness/dynamic-workflow/) | Harness | The model orchestrates sub-agents from one Python script: fan-out, chain, vote in a single tool call, with hard `max_agent_calls` budgets |
| [Advisor](https://pydantic.dev/docs/ai/harness/advisor/) | Harness | Let an executor consult a stronger model mid-run |
| [Background Tools](https://pydantic.dev/docs/ai/harness/background-tools/) | Harness | Run selected tools concurrently; results arrive as follow-up messages |

### Context management

How the agent spends its context window over a long run, and how often it pays for the same tokens.

| Capability | Package | What it does |
| --- | --- | --- |
| [Code Mode](https://pydantic.dev/docs/ai/harness/code-mode/) | Harness | The model writes one Python script that calls many tools inside a [Monty](https://github.com/pydantic/monty) sandbox: one round-trip instead of N, and intermediate results never enter the context window |
| [IPython Code Mode](https://pydantic.dev/docs/ai/harness/ipython-code-mode/) | Harness | Code Mode with a persistent [IPython](https://ipython.org/) kernel in place of the Monty sandbox: full CPython and any installed package, with state kept between calls. For local agents only; not a sandbox |
| [Tool Search](https://pydantic.dev/docs/ai/capabilities/tool-search/) | Core | Load tool definitions on demand instead of carrying hundreds in every prompt |
| [Compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) | Core | Provider-native compaction on OpenAI and Anthropic; the provider summarizes history server-side |
| [Compaction](https://pydantic.dev/docs/ai/harness/compaction/) | Harness | Model-agnostic strategies: tool-result clearing, sliding-window trimming, LLM summarization, tiered; all window-relative, with live usage reporting |
| [Tool Output Limits](https://pydantic.dev/docs/ai/harness/tool-output-limits/) | Harness | Truncate, spill to a queryable file, or summarize oversized tool returns at the source |
| [Warn On Cache Busts](https://pydantic.dev/docs/ai/harness/warn-on-cache-busts/) | Harness | Detect prompt-cache prefix collapses between requests, from the provider’s own numbers |

### Knowledge & memory

What the agent knows and remembers, loaded when relevant instead of carried in every prompt.

| Capability | Package | What it does |
| --- | --- | --- |
| [Memory](https://pydantic.dev/docs/ai/harness/memory/) | Harness | A persistent, namespaced notebook: bounded prompt injection, on-demand search; in-memory/file/Postgres stores |
| [Pixeltable](https://pydantic.dev/docs/ai/harness/pixeltable/) | Harness | Read-only, allowlisted tools over Pixeltable tables and embedding indexes, plus a Pixeltable `MemoryStore` |
| [Conversation Search](https://pydantic.dev/docs/ai/harness/conversation-search/) | Harness | BM25 search over stored history, including turns compaction dropped |
| [Skills](https://pydantic.dev/docs/ai/harness/skills/) | Harness | Load [Agent Skill](https://pydantic.dev/docs/ai/capabilities/on-demand/) (`SKILL.md`) instructions on demand |
| [Repo Context](https://pydantic.dev/docs/ai/harness/repo-context/) | Harness | Start runs oriented: `AGENTS.md`/`CLAUDE.md` + repository structure |
| [Pydantic AI Docs](https://pydantic.dev/docs/ai/harness/pydantic-ai-docs/) | Harness | On-demand Pydantic AI documentation lookup |

### Control & safety

Bounding what the agent may do, and keeping it on-instructions.

| Capability | Package | What it does |
| --- | --- | --- |
| [Repair Tool Arguments](https://pydantic.dev/docs/ai/harness/repair-tool-arguments/) | Harness | Repair malformed JSON tool arguments before schema validation. |
| [Guardrails](https://pydantic.dev/docs/ai/harness/guardrails/) | Harness | Validate/block/redact user input, tool calls, tool results, and output, including secret masking and parallel async guards |
| [Prompt Injection Defender](https://pydantic.dev/docs/ai/harness/prompt-injection-defender/) | Harness | Classify local tool results for indirect prompt injection and optionally withhold high-risk results |
| [Artifact Scanning](https://pydantic.dev/docs/ai/harness/artifact-scanning/) | Harness | Scan memory files and skills for prompt injection, credential exfiltration, and hidden content before they are stored or loaded |
| [Spend Limits](https://pydantic.dev/docs/ai/harness/spend/) | Harness | Cross-window USD/token budgets and per-response cost tracking, per model and per tenant |
| [Ask User](https://pydantic.dev/docs/ai/harness/ask-user/) | Harness | Let the model ask the user multiple-choice questions mid-run; you supply the answerer (terminal, web, test) |
| [Tool approval](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval) | Core | Flag tool calls that need human approval before they run |
| [Tool Call Judge](https://pydantic.dev/docs/ai/harness/tool-call-judge/) | Harness | A second model answers one risk question per tool call and blocks the call before the tool function runs |
| [Approval Reviewer](https://pydantic.dev/docs/ai/harness/approval-reviewer/) | Harness | A second model answers one risk question per call waiting for approval, approves the low-risk ones, and leaves the rest to a person |
| [Permissions](https://pydantic.dev/docs/ai/harness/permissions/) | Harness | Ask a person before file writes and commands, by permission mode: full access, auto (asks before risky commands), or read-only |
| [Handle Deferred Tool Calls](https://pydantic.dev/docs/ai/capabilities/handle-deferred-tool-calls/) | Core | Resolve approvals, answers and external results on deferred tool calls inside the run, in place or by waiting for them, durably on AWS Lambda |
| [System Reminders](https://pydantic.dev/docs/ai/harness/system-reminders/) | Harness | Cache-safe re-injection of guidance mid-run to counter instruction fade |
| [Detect Loops](https://pydantic.dev/docs/ai/harness/detect-loops/) | Harness | Notice repeated tool calls, results, alternations, or responses, or a response repeating itself as it streams, and nudge the model, stop the run, or call your handler |
| [Tool Budgets](https://pydantic.dev/docs/ai/harness/tool-budgets/) | Harness | Cap calls per tool and per run, and refuse exact repeats, with a tool result the model can act on instead of an exception |
| [Trajectory Judge](https://pydantic.dev/docs/ai/harness/trajectory-judge/) | Harness | A second model reviews the live run every N requests over a sliding token window and steers it mid-run |
| [Refine Output](https://pydantic.dev/docs/ai/harness/refine-output/) | Harness | Send the agent back to review and revise its output before the run ends |

### Self-extension

| Capability | Package | What it does |
| --- | --- | --- |
| [Capability Creation](https://pydantic.dev/docs/ai/harness/capability-creation/) | Harness | The agent writes, validates, and persists *new capabilities* during a run; the host loads them into a later run via `load_active(workspace)` and `capabilities=` |

### Execution runtime

Outside the loop: how runs persist, survive failures, and get observed and configured in production.

| Capability | Package | What it does |
| --- | --- | --- |
| [Durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) | Core | Runs that survive restarts and failures, on nine engines: [Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/), [DBOS](https://pydantic.dev/docs/ai/capabilities/durable_execution/dbos/), [Prefect](https://pydantic.dev/docs/ai/capabilities/durable_execution/prefect/), [Restate](https://pydantic.dev/docs/ai/capabilities/durable_execution/restate/), [Airflow](https://pydantic.dev/docs/ai/capabilities/durable_execution/airflow/), and the Harness engines AWS Lambda, Absurd, pgtask, and Azure Durable Task below. See the [workspace guide](https://pydantic.dev/docs/ai/core-concepts/workspace/#durable-execution) for Coder, Shell, and FileSystem |
| [AWS Lambda durability](https://pydantic.dev/docs/ai/harness/aws-lambda/) | Harness | Checkpoint model requests and tool calls into AWS Lambda durable function steps |
| [Absurd durability](https://pydantic.dev/docs/ai/harness/absurd/) | Harness | Checkpoint model requests, MCP calls, and tool calls into Absurd steps on PostgreSQL |
| [pgtask durability](https://pydantic.dev/docs/ai/harness/pgtask/) | Harness | Checkpoint model requests, MCP calls, and tool calls into pgtask steps on PostgreSQL |
| [Azure Durable Task durability](https://pydantic.dev/docs/ai/harness/azure-durable-task/) | Harness | Run model requests, tool calls and durable operations as activities in Durable Task Scheduler orchestrations |
| [Render Workflows](https://pydantic.dev/docs/ai/harness/render-workflows/) | Harness | Run model requests and tool calls as chained task runs with separate retries, timeouts, and compute settings; retrying the task that runs the agent can repeat completed work |
| [Step Persistence](https://pydantic.dev/docs/ai/harness/step-persistence/) | Harness | Save, restore, resume (`continue_run`), and fork (`fork_run`) runs; file/SQLite/Mongo backends |
| [Model Fallback](https://pydantic.dev/docs/ai/capabilities/model-fallback/) | Core | Fall back to other models when a model request fails or its response is rejected, within the run’s own request step |
| [Instrumentation](https://pydantic.dev/docs/ai/capabilities/instrumentation/) | Core | OpenTelemetry GenAI spans for every model and tool call; the raw material for [Logfire](https://pydantic.dev/logfire) traces |
| [Managed Prompt](https://pydantic.dev/docs/ai/harness/managed-prompt/) | Harness | Back instructions with a [Logfire](https://pydantic.dev/logfire) -managed prompt; version and roll out without redeploying |
| [Thread Executor](https://pydantic.dev/docs/ai/capabilities/thread-executor/) | Core | Run sync tools on a shared thread pool |

Core also ships loop-customization capabilities for production servers: [Select Model](https://pydantic.dev/docs/ai/capabilities/select-model/), [Resolve Model ID](https://pydantic.dev/docs/ai/capabilities/resolve-model-id/), [Prepare Tools / Prepare Output Tools](https://pydantic.dev/docs/ai/capabilities/prepare-tools/), [Prefix Tools](https://pydantic.dev/docs/ai/capabilities/prefix-tools/), [Set Tool Metadata](https://pydantic.dev/docs/ai/capabilities/set-tool-metadata/), [Include Tool Return Schemas](https://pydantic.dev/docs/ai/capabilities/include-tool-return-schemas/), [Process History](https://pydantic.dev/docs/ai/capabilities/process-history/), [Process Event Stream](https://pydantic.dev/docs/ai/capabilities/process-event-stream/), [Reinject System Prompt](https://pydantic.dev/docs/ai/capabilities/reinject-system-prompt/), and [Raise Content Filter Error](https://pydantic.dev/docs/ai/capabilities/raise-content-filter-error/).

And the agent plugs into any interface: [ACP](https://pydantic.dev/docs/ai/harness/acp/) *(experimental, Harness)* serves it to editors like Zed over the [Agent Client Protocol](https://agentclientprotocol.com/), and core ships the [web chat UI](https://pydantic.dev/docs/ai/guides/web/), [CLI](https://pydantic.dev/docs/ai/integrations/cli/), [frontend adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/) (AG-UI, Vercel AI), and [realtime voice](https://pydantic.dev/docs/ai/realtime/overview/).

Community packages extend the same capability system further; see [third-party capabilities](https://pydantic.dev/docs/ai/capabilities/third-party/).

## When do you need the Harness?

“Harness” is the field’s term for everything around the model that turns it into an agent: the loop, the tools, the context management. Reach for this package when your agent should *do* more than core’s lean harness covers: touch files, run code, browse, remember, delegate, or stay coherent through hours-long runs. The boundary between the packages is mechanical, not a maturity tier: core ships the capabilities that require model or framework support (provider-native tools like [image generation](https://pydantic.dev/docs/ai/capabilities/image-generation/), provider APIs like [compaction](https://pydantic.dev/docs/ai/capabilities/compaction/), deep loop integration like [tool search](https://pydantic.dev/docs/ai/capabilities/tool-search/), and fundamentals like [thinking](https://pydantic.dev/docs/ai/capabilities/thinking/), [MCP](https://pydantic.dev/docs/ai/capabilities/mcp/), and [web search](https://pydantic.dev/docs/ai/capabilities/web-search/)) and the Harness ships everything else, as a separate package so capabilities can iterate at the speed the field moves while Pydantic AI itself stays lean.

## Installation

- [pip](#tab-panel-2-0)
- [uv](#tab-panel-2-1)

Terminal

```bash
pip install pydantic-ai-harness
```

This installs [`pydantic-ai-slim`](https://pydantic.dev/docs/ai/overview/install/) with it, so it works on its own; you don’t need to install Pydantic AI separately. Model providers and the CLI come via extras that pass through to Pydantic AI: `pydantic-ai-harness[anthropic]`, `[cli]`. Some capabilities need their own extra for optional dependencies; each capability’s page gives its exact install line. Requires Python 3.11+.

New to Pydantic AI itself? Start with [its docs](https://pydantic.dev/docs/ai/overview/): the agent you mount these capabilities on is defined there.

## Observability

Core’s [Instrumentation](https://pydantic.dev/docs/ai/capabilities/instrumentation/) capability (or `logfire.instrument_pydantic_ai()`) emits a full trace of every run: every model call and tool call, with token and cost tracking. It’s standard OpenTelemetry, so any OTLP backend works; run `uvx logfire-cli wizard --task pydantic-ai` once to [set up Logfire](https://pydantic.dev/docs/ai/integrations/logfire/#using-logfire).

## Build your own

[Capabilities](https://pydantic.dev/docs/ai/capabilities/custom/) are the primary extension point for Pydantic AI, and every capability in this library doubles as a worked example. Publishing a standalone package? Use the `pydantic-ai-<name>` naming convention; see [Publishing capability packages](https://pydantic.dev/docs/ai/guides/extensibility/#publishing-capability-packages).

## Version policy

Pydantic AI Harness uses **0.x versioning** to signal API stability, not maturity: the capabilities are tested end-to-end and meant for production use, but their APIs may change between minor releases (0.1 -> 0.2) through renamed parameters, changed defaults, or restructured APIs, with deprecation warnings where practical. Patch releases will not intentionally break existing behavior, and every breaking change is documented in release notes with migration guidance your agent can follow. Keeping the Harness a separate package from [Pydantic AI](https://github.com/pydantic/pydantic-ai), which has a [stricter version policy](https://pydantic.dev/docs/ai/project/version-policy/), lets capabilities change faster than core.

On 0.x, each Harness release ships alongside the Pydantic AI release with the same minor and patch number (Harness 0.51.0 ships with Pydantic AI 2.51.0) and pins that exact `pydantic-ai-slim` version, so upgrading the Harness upgrades Pydantic AI with it and every installable pair has been tested together.

### After 1.0

From 1.0, the Harness follows the rules of Pydantic AI’s [version policy](https://pydantic.dev/docs/ai/project/version-policy/): no intentional breaking changes in minor releases, and deprecated functionality is not removed until the next major version. The changes that policy does not consider breaking, such as bug fixes for code that relied on undocumented behavior, OpenTelemetry span attributes, and `__repr__` output, are not breaking for the Harness either. Neither is a change that follows a third-party service or SDK a capability integrates with, when that service removes or changes what the capability relied on. Capabilities marked experimental on their page (currently [ACP](https://pydantic.dev/docs/ai/harness/acp/)) are excluded until they graduate.

A capability’s behavior includes what it sends to the model, so stability covers more than signatures:

- **Defaults**: a minor release does not change a default parameter value in a way that changes what an existing agent does, such as enabling a tool, lowering a limit, or switching a fallback. New behavior arrives behind a new parameter, and a default changes only in a major release.
- **Stored history**: tool names, argument schemas, and the other records a capability writes into message history and reads back on later runs, such as metadata keys and framing tags, persist in histories that you may store and resume. A minor release can add optional tool arguments but does not rename or remove a tool, an argument, or a record a capability relies on.
- **Prompt text**: the wording of instructions, tool descriptions, and other text a capability sends to the model can change in a minor release, since improving how models use a capability is part of maintaining it. Release notes list these changes. Where a capability accepts its own instructions or descriptions as parameters, passing them keeps your wording fixed.

From 1.0, Harness version numbers no longer mirror Pydantic AI’s, and a Harness major release does not require a Pydantic AI major release. Every Harness release still pins the exact `pydantic-ai-slim` release it was tested with, and moving that pin to a new Pydantic AI major version is itself a Harness major release, so upgrading the Harness within a major version does not cross a Pydantic AI major. The pin is listed in the package metadata on PyPI, and the release notes name the Pydantic AI release each Harness release ships with.
