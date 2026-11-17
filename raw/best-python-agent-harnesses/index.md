---
title: "Best Python Agent Harnesses in 2026"
author: "Douwe Maan"
site: "Pydantic"
published: 2026-11-09T09:00:00.000Z
source: "https://pydantic.dev/articles/best-python-agent-harnesses"
domain: "pydantic.dev"
language: "en"
description: "Compare Python agent harness SDKs in 2026 by models, sandboxes, durability and support: Pydantic AI Harness, Deep Agents, Claude Agent SDK, OpenHands and more."
word_count: 5339
---

Every agent that does real work ends up with the same parts around the model: a place to read and write files, a shell, a plan it keeps current, sub-agents to hand work to, a way to keep the context window useful in hour three, rules about what it may do without asking, and a way to pick up where it left off after a restart. The field calls that the harness. In 2026 you rarely write one from scratch. You pick a harness SDK and build on it, and that choice decides which models you can run, where your agent's commands execute, and how much of its behavior is yours to change.

**TL;DR.** [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/) is our pick overall: 80+ capabilities across Pydantic AI and the Harness, from file and shell tools, planning, memory, skills and sub-agents to context management, guardrails and twelve sandboxes and remote workspaces, that you add to any [Pydantic AI](https://pydantic.dev/docs/ai/) agent one at a time, on 30+ model providers, with runs that survive a crash on nine durable execution engines. Its complete agents, `Coder` and `Researcher`, are those same capabilities combined, so you can start from a working coding agent and take it apart. Choose **LangChain Deep Agents** if your agents already run on LangGraph and LangSmith. The **Claude Agent SDK** if the agent you want is Claude Code itself, on Claude models. The **OpenAI Agents SDK** if OpenAI is your model provider and tracing platform, and the **Codex SDK** if the agent you want is Codex. The **OpenHands Software Agent SDK** if you are building a software engineering agent and want an agent server, sandboxes and a long benchmark record with it. The **Strands harness** if you build on AWS and Bedrock. **Microsoft Agent Framework's Harness** if you need the same harness in.NET or Go.

*Last updated: November 9, 2026. Capabilities, counts and licenses were read from each project's own docs and repository on October 30, 2026; the Pydantic AI Harness and OpenHands Index figures were re-read on November 9.*

## What to look for in an agent harness

Two kinds of thing get called a harness. A harness product is someone else's agent (its loop, prompts, tools and permissions) that you configure: Claude Code and Codex are prominent examples. A harness SDK gives you the same pieces as a library you build your own agent from. This post compares harness SDKs you use from Python, including the ones that wrap a harness product, and these are our criteria. They are opinionated.

- **Can you change models without rewriting the agent?** Prices, quality and rate limits move every month, and the best model for a coding agent is not always the best one for a research agent. A harness built around one vendor's models makes every other vendor a second-class path, or no path at all.
- **How much can you take apart?** A ready-made agent is the fastest start. The question is what you can change when it does not fit: remove a tool, replace the planning step, swap the context strategy, or rewrite the instructions, without forking the harness or fighting defaults you cannot see.
- **Where do the agent's commands run?** On your machine, in a container, or in a cloud sandbox. Check which sandboxes the harness supports natively and whether the same agent code runs in each.
- **What may it do without asking?** Look for approval on individual tool calls that survives the process going away, and for limits on the shell and file system that you set, not the model.
- **What happens when the process dies mid-run?** Long agent runs meet deploys, crashes and rate limits. Resuming a saved conversation is not the same as durable execution, which records each completed model and tool call and, after a restart, replays its result instead of running it again. Check which one the harness offers, and whether it works with an engine your company already runs or only with its own store.
- **Does it stay coherent on long runs?** Compaction, clearing old tool results, spilling oversized output to files, and loading tools and skills on demand are the difference between an agent that degrades after an hour and one that does not.
- **Do traces go where your other traces go?** OpenTelemetry to any backend, or a vendor's own tracing product.
- **Can you buy support for the harness itself?** Once an agent is in production you want an escalation path beyond a public issue tracker. Check whether a support agreement covers the open-source SDK, or only a hosted platform or cloud you would also have to adopt.

## How we compared

For each harness we read its documentation, opened its license file and checked its latest release on the date above. We recorded which models it runs natively, what its ready-made agent contains and how much of that you can remove or replace, which sandboxes it supports, how a person approves an action, how a run survives a restart, how it manages context on long runs, what tracing it emits, who makes it under which license, and what you have to buy to get commercial support for it. Where we could count something, we did, using the project's own docs. Where a project's docs mark something experimental, preview or beta, we say so. Every entry, ours included, gets a catch.

"Agent harness SDK" here means a library you import from Python that ships the batteries around the loop (file and shell tools, planning, sub-agents, context management and somewhere for the agent to work) plus a ready-made agent assembled from them. They come in several shapes, named in the table's "Kind" column: from libraries of parts with agents built from them, through assembled harnesses on top of a framework, to SDKs that embed a finished agent such as Claude Code or Codex. We include the last because it is how many teams start, and judge it against the same criteria. A plain agent framework, the loop and tools without those batteries, is the subject of our companion post, [The best Python AI agent frameworks in 2026](https://pydantic.dev/articles/best-python-ai-agent-frameworks). Finished agents you run rather than build on are covered briefly [further down](#finished-agents-and-smaller-libraries). After Pydantic AI Harness, the order is not a score. "Native" means built into the harness or an officially maintained package, not reached through a generic adapter such as LiteLLM. "None documented" means we found nothing in the project's own docs on that date, not that it cannot be built.

Harnesses change every month, so this post does too. We re-check it against each project's own docs and releases every month, and the "Last updated" date above changes whenever anything in it does. If you maintain one of these projects and something here is wrong or out of date, email [hello@pydantic.dev](mailto:hello@pydantic.dev) and we will fix it.

## The best Python agent harnesses in 2026

### 1\. Pydantic AI Harness: best Python agent harness overall

Pydantic AI Harness (that's us) is the open-source capability library for Pydantic AI, from the team behind Pydantic. Everything in it is one primitive: a capability, a self-contained unit of agent behavior you add to `capabilities=[...]` on any Pydantic AI agent. The [Harness docs](https://pydantic.dev/docs/ai/harness/#capabilities) list 80+ of them across Pydantic AI and the Harness package, and the complete agents are capabilities too. [`Coder`](https://pydantic.dev/docs/ai/harness/coder/) is file tools, a persistent shell, repository instructions, delegation to a fresh run of itself and context controls, combined; [`Researcher`](https://pydantic.dev/docs/ai/harness/researcher/) is web search, page fetching, a sub-researcher and bounded tool output.

Here is `Coder` fixing a failing test in the current directory, traced with Pydantic [Logfire](https://pydantic.dev/logfire). Install it with `pip install "pydantic-ai-harness[coder,anthropic,logfire]"`, set `ANTHROPIC_API_KEY`, and run `logfire auth` once, or drop the two `logfire` lines:

```python
import logfire
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import Coder

logfire.configure()
logfire.instrument_pydantic_ai()

agent = Agent(
    'anthropic:claude-fable-5-1',
    capabilities=[LocalWorkspace('.'), Coder()],
)
result = agent.run_sync('Find out why tests/test_parser.py fails and fix the bug it caught.')
print(result.output)
```

Change the model string to run the same agent on another provider. To run its commands in a cloud sandbox instead, install the `modal` extra as well (`pip install "pydantic-ai-harness[coder,modal,anthropic,logfire]"`) and swap the workspace. The sandbox starts empty, with `git` but none of your dependencies, so the prompt has to bring the repository in:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Coder
from pydantic_ai_harness.modal_sandbox import ModalSandbox

agent = Agent('anthropic:claude-fable-5-1', capabilities=[ModalSandbox(), Coder()])
result = agent.run_sync(
    'Clone https://github.com/you/your-repo, install it, then find out why tests/test_parser.py fails and fix the bug it caught.'
)
```

When `Coder` stops fitting, rebuild it from [its parts](https://pydantic.dev/docs/ai/harness/coder/) and change the one you need: an allowlist on the shell, a different compaction strategy, no delegation.

Why it is first: measured against the criteria above, it is the only harness here that answers all of them in the open-source library. Each of the others misses at least one, by its own docs. The Claude Agent SDK runs one vendor's models, and the OpenAI Agents SDK treats other vendors' as beta. Deep Agents keeps durability in LangGraph's checkpointers and sells support with LangSmith. OpenHands and Strands document no external durable execution engine, Microsoft's Harness documents only its own Durable Extension, and Strands and Microsoft document no commercial support for their SDKs. What answering all of them looks like in practice:

- **[30+ model providers](https://pydantic.dev/docs/ai/models/overview/), natively**, from OpenAI, Anthropic and Gemini to Bedrock, Vertex AI, Azure, Mistral, Groq, xAI, Ollama and OpenRouter, plus any OpenAI-compatible endpoint, with fallback to another model when a request fails.
- **Parts you can take out one at a time.** Each capability works on its own and composes with the rest and with your own: [file system](https://pydantic.dev/docs/ai/harness/filesystem/) and [shell](https://pydantic.dev/docs/ai/harness/shell/) tools with allowlists and denylists, [planning](https://pydantic.dev/docs/ai/harness/planning/), [sub-agents](https://pydantic.dev/docs/ai/harness/subagents/), [memory](https://pydantic.dev/docs/ai/harness/memory/) across sessions, [skills](https://pydantic.dev/docs/ai/harness/skills/) loaded on demand, web search and browsers, and integrations such as GitHub, Linear and Slack.
- **A local directory plus twelve [sandboxes and remote workspaces](https://pydantic.dev/docs/ai/harness/#execution-environments)**: Modal, E2B, Render, Sprites, Daytona, boxd, smolvm, BoxLite, OpenSandbox, Docker, Bubblewrap and SSH. The same file and shell tools work in whichever one the run has.
- **Context management for long runs**: model-agnostic [compaction strategies](https://pydantic.dev/docs/ai/harness/compaction/) (tool-result clearing, sliding windows, summarization), provider-native compaction on OpenAI and Anthropic, oversized tool output spilled to a file the agent can query, tool search, and [Code Mode](https://pydantic.dev/docs/ai/harness/code-mode/), where the model calls many tools from one script in a sandboxed interpreter.
- **Control over what it does**: [tool approval](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) that ends the run with the pending call so a later run in any process resumes it, an [approval reviewer](https://pydantic.dev/docs/ai/harness/approval-reviewer/) that lets a second model approve low-risk calls and leaves the rest to a person, a [tool call judge](https://pydantic.dev/docs/ai/harness/tool-call-judge/), [guardrails](https://pydantic.dev/docs/ai/harness/guardrails/) with secret masking, and spend limits.
- **Nine [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) engines**: Temporal, DBOS, Prefect, Restate, AWS Lambda, Absurd, pgtask, Azure Durable Task and Apache Airflow, plus [step persistence](https://pydantic.dev/docs/ai/harness/step-persistence/) to resume or fork a run from files, SQLite, MongoDB or PostgreSQL.
- **OpenTelemetry** spans for every model and tool call, following the GenAI semantic conventions, to any backend. [Pydantic Logfire](https://pydantic.dev/logfire) is the easiest way to see them, and optional.

The same agent runs in a terminal chat, a web chat, editors through the Agent Client Protocol (experimental), and frontends through AG-UI and the Vercel AI protocol. Pydantic offers [enterprise support](https://pydantic.dev/docs/ai/overview/enterprise-support/) for Pydantic AI and the Harness, from the team that builds them, with an SLA and no platform to buy. Both are MIT licensed.

The catch: it is Python only, and it is a library, not a product. There is no hosted runtime and no management UI; agents run in your process on your infrastructure, and durability comes from an engine you choose and operate. `Coder` in a `LocalWorkspace` runs shell commands on your machine without an allowlist, so production use belongs in a sandbox or behind the approval and shell controls above. More parts also means more choices: `Coder` 's defaults are ours, but once you rebuild it, testing your combination in your workspace is your job.

Best for Python teams that want a working agent today and expect to change its parts, its model and where it runs as their product grows.

### 2\. LangChain Deep Agents: if your agents already run on LangGraph and LangSmith

[Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) calls itself "the batteries-included agent harness". In LangChain's own layering, LangGraph is the graph runtime, `create_agent` is a minimal harness on top of it, and Deep Agents is a more opinionated harness on top of `create_agent`. It is [MIT licensed](https://github.com/langchain-ai/deepagents), from LangChain, Inc., and also exists for JavaScript.

The default agent has file tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`), a `task` tool for sub-agents, summarization of long threads and offloading of large tool results. Memory, skills and human approval are opt-in, and since version 0.7 so is the `write_todos` planning tool. You change it through middleware: an override replaces the default instance, and any LangGraph graph can be a sub-agent. It runs on any LangChain chat model. Commands run in a [sandbox backend](https://docs.langchain.com/oss/python/deepagents/sandboxes): LangSmith Sandbox, AWS AgentCore, Databricks, Daytona, E2B, Modal, NVIDIA OpenShell, Runloop or Vercel. LangChain also ships Deep Agents Code (`dcode`), a terminal coding agent built on it, and in February [reported](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) a Terminal-Bench 2.0 score of 66.5 for its earlier CLI on `gpt-5.2-codex`.

The catch: it brings the LangChain stack with it. The package depends on `langsmith`, `langchain-anthropic` and `langchain-google-genai`. [Human approval](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop) requires a LangGraph checkpointer, durability is LangGraph's own checkpointers with no external durable execution engine documented, and tracing is LangSmith's, with [OpenTelemetry through the LangSmith SDK](https://docs.langchain.com/langsmith/trace-with-opentelemetry). Its README describes a "trust the LLM" security model, and its local backends give no isolation. The API moves quickly: 0.7.0 removed the default planning tool and default prompts.

Pick it when your agents, checkpoints and traces already live in LangGraph and LangSmith, and you want a harness from the same vendor.

### 3\. Claude Agent SDK: if the agent you want is Claude Code, on Claude

The [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) gives you "the same tools, agent loop, and context management that power Claude Code", in Python or TypeScript. It runs a bundled Claude Code binary as a subprocess, so file editing, shell commands, web search, sub-agents, skills, automatic compaction, permission modes and sessions arrive already wired. The Python package is [MIT licensed](https://github.com/anthropics/claude-agent-sdk-python/blob/main/LICENSE), and use of the SDK is governed by Anthropic's Commercial Terms of Service.

You can [remove built-in tools](https://code.claude.com/docs/en/agent-sdk/permissions) and replace the system prompt. [Permission callbacks](https://code.claude.com/docs/en/agent-sdk/user-input) approve, deny or modify each tool call, and a [hook can defer](https://code.claude.com/docs/en/agent-sdk/hooks) a call so you resume it later. Your own tools arrive as in-process MCP servers.

The catch: Claude models only, through [Anthropic, Bedrock, Vertex AI or Microsoft Foundry](https://code.claude.com/docs/en/agent-sdk/quickstart). Its [hosting docs](https://code.claude.com/docs/en/agent-sdk/hosting) describe every running agent as "a long-lived process tied to local state", suggest 1 GiB of RAM per agent as a floor, and say sessions do not survive a container restart unless you mirror transcripts to a `SessionStore`, which is best-effort. With a custom system prompt, Claude Code's own reminders still reach the model until you [turn each one off](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts). Its built-in sandbox is off by default, and when it is enabled but cannot start, commands run unsandboxed with a warning. OpenTelemetry tracing is opt-in and marked beta, and no durable execution engine integration is documented. Aditya's post [Would you deploy an agent you don't control?](https://pydantic.dev/articles/pydantic-ai-vs-claude-agent-sdk) makes the longer argument.

Pick it when the product you want is Claude Code itself, embedded, and a single model vendor is acceptable.

### 4\. OpenAI Agents SDK: if you are all-in on OpenAI

OpenAI [described](https://openai.com/index/the-next-evolution-of-the-agents-sdk/) its April update to the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) as a "model-native harness". Alongside agents, handoffs and guardrails, [sandbox agents](https://openai.github.io/openai-agents-python/sandbox/guide/) now work in a container with shell and file tools, skills, memory and compaction. [Sandbox clients](https://openai.github.io/openai-agents-python/sandbox/clients/) cover a local Unix sandbox, Docker, Blaxel, Cloudflare, Daytona, E2B, Modal and Vercel. Tools take [`needs_approval`](https://openai.github.io/openai-agents-python/human_in_the_loop/), and the paused run's state serializes to JSON so you can resume it later. Its docs list [four durable execution integrations](https://openai.github.io/openai-agents-python/running_agents/): Temporal, DBOS, Restate and Dapr. It is [MIT licensed](https://github.com/openai/openai-agents-python) and also exists for TypeScript.

The catch: its default path is OpenAI's Responses API, and [other providers](https://openai.github.io/openai-agents-python/models/) go through LiteLLM and Any-LLM adapters its docs call "best-effort, beta", which lose Responses-only features. [Tracing](https://openai.github.io/openai-agents-python/tracing/) is on by default, goes to OpenAI, and is unavailable to organizations under Zero Data Retention. Right for teams whose model provider and tracing platform are both OpenAI.

### 5\. Codex SDK: if the agent you want is Codex

The [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk) has a stable Python package, `openai-codex`, that "controls the local Codex app-server over JSON-RPC", and a TypeScript package that wraps the `codex` CLI. You get Codex's own agent, with its tools, read-only, workspace-write or full-access sandbox presets, base and developer instructions you set, and local threads you can resume and fork. It is [Apache 2.0 licensed](https://github.com/openai/codex/blob/main/LICENSE).

The catch: it wraps a Codex process, so you configure that agent rather than recompose it. Its docs are written around OpenAI's models; other providers are a Codex configuration matter. Its Python approval setting has two values: deny everything, or let an automatic reviewer decide. Commercial support for the SDK: none documented.

Use it when the product you want is Codex itself, embedded.

### 6\. OpenHands Software Agent SDK: if you are building a software engineering agent

The [OpenHands Software Agent SDK](https://docs.openhands.dev/sdk) provides "Python, TypeScript, and REST APIs for building agents that work with code", and is the engine behind the OpenHands CLI and OpenHands Cloud. It needs Python 3.12 or later and is [MIT licensed](https://github.com/OpenHands/software-agent-sdk/blob/main/LICENSE). It is a separate project from the [`OpenHands/OpenHands`](https://github.com/OpenHands/OpenHands) repository, which is now Agent Canvas, a TypeScript control center that runs OpenHands, Claude Code, Codex and other agents over ACP; the [`openhands-ai`](https://pypi.org/project/openhands-ai/) Python package from that repository had its last release, 1.11.0, in July 2026.

An agent is built from [swappable components](https://docs.openhands.dev/sdk/arch/overview): terminal, file editor, task tracker and [browser](https://docs.openhands.dev/sdk/guides/agent-browser-use.md) tools, sub-agents, a [context condenser](https://docs.openhands.dev/sdk/guides/context-condenser.md), skills, MCP and hooks. The same agent code runs in a local workspace or, through its agent server, in Docker, Apptainer, an API-based sandbox or OpenHands Cloud. [Confirmation policies](https://docs.openhands.dev/sdk/guides/security.md) ask before every action, never, or only for actions a security analyzer rates risky. Conversations [persist to disk](https://docs.openhands.dev/sdk/guides/convo-persistence.md) and resume, and [traces](https://docs.openhands.dev/sdk/guides/observability.md) are OpenTelemetry to any OTLP backend.

Its benchmark record is long. OpenHands has submitted to the official [SWE-bench Verified](https://www.swebench.com/) leaderboard since October 2024, and its newest entry there marked as checked by the SWE-bench team is 71.8, with GPT-5, from August 2025. OpenHands also runs its own [OpenHands Index](https://index.openhands.dev/) across five benchmarks, including SWE-bench and GAIA, and posts each run's results and trajectories; its newest entry, from June 11, 2026, averages 81.0 with Claude Fable 5. The Index numbers are OpenHands' own runs.

The catch: it is built for agents that work with code. Models come through [LiteLLM](https://docs.openhands.dev/sdk/guides/llm-registry.md) model strings rather than native provider clients. Isolation means running its separate agent server in a container or remote sandbox; the local workspace acts on the host. Its default security analyzer has the acting model label the risk of its own actions, so the risky-only policy depends on the agent's own judgment. Persistence is a directory of events, with no external durable execution engine documented. The paid offerings are hosting: OpenHands Cloud, and [OpenHands Enterprise](https://openhands.dev/enterprise), which adds self-hosting and guidance from its engineers, as a platform.

Pick it when your product is a coding agent and you want an agent server, its sandboxes and a long benchmark record with it.

### 7\. Strands harness: if you build on AWS and Bedrock

AWS's Strands Agents now ships [Strands harness](https://strandsagents.com/docs/user-guide/harness/), "a fully assembled agent harness", on top of its SDK, in Python and TypeScript. One `create_harness()` call gives you shell, read, write and edit tools, web fetch and search, a built-in sub-agent, a todo list, skills, file-based memory, sessions you resume by id, and context management. It is [Apache 2.0 licensed](https://github.com/strands-agents/harness-sdk).

The [configuration reference](https://strandsagents.com/docs/user-guide/harness/reference/configuration/) documents every default you can override, and [interventions](https://strandsagents.com/docs/user-guide/harness/configure/interventions/index.md) gate tool calls behind human approval, a natural-language rule or a Cedar policy. Models come from Bedrock, Anthropic, OpenAI, Google and Ollama, and the SDK emits OpenTelemetry traces.

The catch: Amazon Bedrock is the default provider, and the harness package is new, first published in September 2026. Its sandboxes are Docker, SSH and Strands Shell, an in-process shell sandbox, and no durable execution engine integration is documented. Commercial support for the SDK: none documented.

Suited to teams whose models, credentials and deployment are already on AWS and want an assembled harness from the same place.

### 8\. Microsoft Agent Framework Harness: if you need the same harness in.NET or Go

Microsoft Agent Framework [provides](https://learn.microsoft.com/en-us/agent-framework/concepts/harness) "an opinionated, batteries-included Harness for research, coding, data analysis, and other long-running work", in.NET, Python and Go. In Python, `create_harness_agent` returns an ordinary Agent Framework agent with todo tracking, plan and execute modes, session file memory, tool approval rules, web search where the model supports it, and OpenTelemetry, all on by default. Compaction, skills, file access, background sub-agents, shell and bounded looping are opt-in. The framework is [MIT licensed](https://github.com/microsoft/agent-framework).

Each default has a switch to disable it, and you can replace the todo and mode providers or add your own context providers. For durability, Microsoft's [Durable Extension](https://learn.microsoft.com/en-us/agent-framework/integrations/durable-extension) runs agents on the Durable Task Scheduler, on Azure Functions or your own compute.

The catch: in Python, background agents, file access and looping are marked experimental, shell tooling comes from a pre-release package, and the Durable Extension installs as a pre-release. Sandboxes for the agent's commands: none documented on the Harness page. Commercial support for the framework: none documented.

The choice for teams that need one harness across Python,.NET and Go.

## Comparison at a glance

Checked October 30, 2026, with the Pydantic AI Harness row re-checked November 9, 2026. Counts are what each project's own docs list natively; "via" means through an adapter or a separate integration; "none documented" means its docs describe none.

| Harness | Kind | Models | Taking it apart | Where commands run | Durability and resume | Tracing | Commercial support | License and maker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pydantic AI Harness | Capability library; `Coder` and `Researcher` built from it | 30+ providers, plus any OpenAI-compatible endpoint | Each of 80+ capabilities works alone, including the parts of `Coder` | Local, plus 12 sandboxes and remote workspaces | Replay on 9 durable engines; step persistence to files, SQLite, MongoDB, PostgreSQL | OpenTelemetry (GenAI conventions) to any backend | For Pydantic AI and the Harness, from Pydantic; no platform plan needed | MIT; Pydantic |
| LangChain Deep Agents | Opinionated harness on LangGraph; Deep Agents Code | Any LangChain chat model | Middleware overrides; any LangGraph graph as a sub-agent | Local backends, plus 9 sandbox integrations | LangGraph checkpointers; no external engine documented | LangSmith; OTel via the LangSmith SDK | With a LangSmith Enterprise plan | MIT; LangChain, Inc. |
| Claude Agent SDK | Embedded finished agent (Claude Code) | Claude only, on 4 platforms | Remove tools, replace the system prompt, hooks | Local subprocess; own sandbox off by default | Sessions on disk, or a best-effort `SessionStore`; no engine documented | OpenTelemetry, opt-in (beta) | None documented | MIT, under Anthropic's Commercial Terms; Anthropic |
| OpenAI Agents SDK | Framework with sandbox agents | OpenAI; others via beta LiteLLM and Any-LLM adapters | Capabilities on sandbox agents | Local Unix, Docker, plus 6 hosted sandboxes | Serialized run state; 4 engines: Temporal, DBOS, Restate, Dapr | OpenAI tracing on by default; third-party processors | None documented for the SDK | MIT; OpenAI |
| Codex SDK | Embedded finished agent (Codex) | OpenAI-oriented; others through Codex configuration | Instructions, sandbox and approval settings | Codex sandbox presets | Local threads you resume and fork; no engine documented | OpenTelemetry log export, opt-in, through Codex configuration | None documented | Apache 2.0; OpenAI |
| OpenHands SDK | Coding agent SDK (Python, TypeScript, REST) with an agent server | Via LiteLLM | Swappable tools, condenser, workspace | Local, or Docker, Apptainer, API sandboxes and Cloud via its agent server | Conversation persistence to disk; no engine documented | OpenTelemetry to any OTLP backend | With OpenHands Enterprise | MIT; OpenHands |
| Strands harness | Assembled harness on the Strands SDK | Bedrock by default; Anthropic, OpenAI, Google, Ollama | Override every default; drop to the SDK | Docker, SSH, Strands Shell | Sessions by id; no engine documented | OpenTelemetry | None documented | Apache 2.0; AWS |
| Microsoft Agent Framework Harness | Assembled harness on Agent Framework | Agent Framework chat clients | Disable or replace each default | None documented on the Harness page | Durable Extension on Durable Task (pre-release) | OpenTelemetry | None documented | MIT; Microsoft |

## Finished agents and smaller libraries

Five projects come up in harness lists and searches that we left out of the ranking, each for a reason.

- **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** from Nous Research is a finished, self-improving agent with a terminal UI, a messaging gateway, memory, skills and six terminal backends, under the MIT license. You can import its `AIAgent` from Python, but only from a git checkout: its docs say it publishes no supported wheel. Use it as an agent, not as a library.
- **[Mistral Vibe](https://docs.mistral.ai/vibe/code/overview)** is Mistral's Python coding agent, a finished CLI under the Apache 2.0 license, with a separate pre-1.0 [SDK](https://pypi.org/project/mistralai-vibe-sdk/) for building agents.
- **[DeepSeek Harness Python SDK](https://github.com/deepseek-ai/deepseek-harness/blob/master/python/sdk/README.md)** is a client, still a developer preview, that drives DeepSeek's TypeScript harness over JSON-RPC, and its shipped profiles [send the session log](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-log-deepseek/README.md) to DeepSeek's official API by default until a profile patch turns that off.
- **[smolagents](https://github.com/huggingface/smolagents)** from Hugging Face is "a barebones library for agents that think in code", with code executors on E2B, Modal, Blaxel and Docker. Its docs describe no file or shell tools, compaction, skills or tool approvals, and its last release was in May.
- **[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)** is a minimal coding agent whose only tool is bash, built for research and benchmarks.

If what you want is a coding agent to use rather than one to build, Claude Code, Codex, OpenCode and Pi are finished harnesses, and several of the SDKs above are how you embed them.

## If you work in TypeScript

This list is Python only, and several widely used harnesses are TypeScript-first.

- **[Pi](https://github.com/earendil-works/pi)**, by Mario Zechner, is "a minimal, extensible agent harness that you can make your own", with an agent core package, a coding agent CLI and an SDK, under the MIT license. It leaves out sub-agents and plan mode by design.
- **[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)** (`dsh`) is itself a TypeScript harness, with a web UI and a desktop app, and its plugins are TypeScript packages; the Python SDK mentioned above drives it.
- **[Deep Agents JS](https://github.com/langchain-ai/deepagentsjs)** is the TypeScript version of Deep Agents, MIT licensed.
- **[Mastra](https://mastra.ai/docs/harness/overview)** uses "harness" for a set of capabilities around its agents (durable agents, background tasks, schedules and `AgentController`) and has a `createCodingAgent()` helper.
- The **Strands harness**, **OpenAI Agents SDK** and **Codex SDK** also ship TypeScript versions. The TypeScript **Claude Agent SDK** is not open source: its license file reserves all rights under Anthropic's Commercial Terms.
- The **[Vercel AI SDK](https://ai-sdk.dev/docs/ai-sdk-harnesses)** has an experimental `HarnessAgent` that runs other harnesses, such as Claude Code, Codex, Pi and Deep Agents, behind one interface.

## How to choose

- You are building a Python agent and want a working one now, on any model, with parts you can replace as it grows: **Pydantic AI Harness**.
- Your agent's runs must survive a crash, on an engine your company already operates: **Pydantic AI Harness** (nine engines), or the **OpenAI Agents SDK** (four) if you are on OpenAI's models.
- Your agents, checkpoints and traces already live in LangGraph and LangSmith: **LangChain Deep Agents**.
- You want Claude Code itself inside your product, on Claude models: the **Claude Agent SDK**.
- OpenAI is your model provider and tracing platform: the **OpenAI Agents SDK**.
- You want Codex itself inside your product: the **Codex SDK**.
- Your product is a coding agent and you want an agent server, sandboxes and a long benchmark record: the **OpenHands Software Agent SDK**.
- Your models and deployment are on AWS: the **Strands harness**.
- You need the same harness across Python,.NET and Go: **Microsoft Agent Framework's Harness**.

## When another harness is the better pick

Three situations favor something else over Pydantic AI Harness.

The first is wanting a specific vendor's agent. If the product you want is Claude Code or Codex, embedded, their own SDKs give you the agent its makers ship and tune. Rebuilding it from parts only pays off if you expect to change it.

The second is a stack you already run. A team with LangGraph agents in production and traces in LangSmith gets Deep Agents on the runtime, checkpointers and tracing it already operates. The same goes for Strands on Bedrock.

The third is a language other than Python. Pi, DeepSeek Harness, Deep Agents JS and Mastra in TypeScript, and Microsoft's Harness in.NET and Go, are where those teams should look.

If your product is not a coding agent, think twice before starting from one. Our earlier posts on [the harness thesis](https://pydantic.dev/articles/the-harness-thesis), [what makes a good harness](https://pydantic.dev/articles/what-makes-a-good-harness) and [Harness Week](https://pydantic.dev/articles/harness-week) go further into why we build the harness as parts.

## Frequently asked questions

**What is the best Python agent harness?** Our answer is Pydantic AI Harness: 80+ capabilities across Pydantic AI and the Harness on any of 30+ model providers, twelve sandboxes and remote workspaces, nine durable execution engines and OpenTelemetry tracing, with ready-made agents built from the same parts. The exceptions are teams that want a specific vendor's agent (the Claude Agent SDK or the Codex SDK), teams already on LangGraph and LangSmith (Deep Agents), and teams standardized on AWS or Azure.

**Which harness should I use to build my own coding agent in Python?** Start from `Coder` in Pydantic AI Harness if you want to choose the model and change the agent's parts; it runs locally or in a sandbox, and you can rebuild it from its capabilities. The OpenHands Software Agent SDK is the pick if you want its agent server and its record of SWE-bench runs, and the Claude Agent SDK if you want Claude Code itself.

**Which agent harnesses work with any model?** Pydantic AI Harness (30+ providers natively), LangChain Deep Agents (any LangChain chat model) and the OpenHands SDK (through LiteLLM). The Strands harness defaults to Bedrock and supports other providers. The Claude Agent SDK runs Claude models only, and the OpenAI Agents SDK reaches other providers through beta adapters.

**Is Pydantic AI Harness the same as Pydantic AI?** No. [Pydantic AI](https://pydantic.dev/docs/ai/) is the agent framework: the typed agent loop, models, tools and structured output. Pydantic AI Harness is a separate package of capabilities you add to a Pydantic AI agent, and it installs Pydantic AI with it.

## Sources

Every source below was checked on October 30, 2026; the Pydantic AI Harness sources and the OpenHands Index were re-checked on November 9, 2026.

- **Pydantic AI Harness**: [overview](https://pydantic.dev/docs/ai/harness/), [Coder](https://pydantic.dev/docs/ai/harness/coder/), [Researcher](https://pydantic.dev/docs/ai/harness/researcher/), [compaction](https://pydantic.dev/docs/ai/harness/compaction/), [step persistence](https://pydantic.dev/docs/ai/harness/step-persistence/), [workspaces](https://pydantic.dev/docs/ai/core-concepts/workspace/), [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) and [Azure Durable Task](https://pydantic.dev/docs/ai/harness/azure-durable-task/), [models](https://pydantic.dev/docs/ai/models/overview/), [enterprise support](https://pydantic.dev/docs/ai/overview/enterprise-support/).
- **LangChain Deep Agents**: [overview](https://docs.langchain.com/oss/python/deepagents/overview), [customization](https://docs.langchain.com/oss/python/deepagents/customization), [sandboxes](https://docs.langchain.com/oss/python/deepagents/sandboxes), [human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop), [repository and changelog](https://github.com/langchain-ai/deepagents), [OpenTelemetry](https://docs.langchain.com/langsmith/trace-with-opentelemetry), [pricing](https://www.langchain.com/pricing).
- **Claude Agent SDK**: [overview](https://code.claude.com/docs/en/agent-sdk/overview), [quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart), [hosting](https://code.claude.com/docs/en/agent-sdk/hosting), [permissions](https://code.claude.com/docs/en/agent-sdk/permissions), [hooks](https://code.claude.com/docs/en/agent-sdk/hooks), [system prompts](https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts), [repository](https://github.com/anthropics/claude-agent-sdk-python).
- **OpenAI Agents SDK and Codex SDK**: [announcement](https://openai.com/index/the-next-evolution-of-the-agents-sdk/), [sandbox agents](https://openai.github.io/openai-agents-python/sandbox/guide/), [sandbox clients](https://openai.github.io/openai-agents-python/sandbox/clients/), [models](https://openai.github.io/openai-agents-python/models/), [human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/), [running agents](https://openai.github.io/openai-agents-python/running_agents/), [tracing](https://openai.github.io/openai-agents-python/tracing/), [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk), [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-advanced), [Codex repository](https://github.com/openai/codex).
- **OpenHands Software Agent SDK**: [docs](https://docs.openhands.dev/sdk), [architecture](https://docs.openhands.dev/sdk/arch/overview), [security](https://docs.openhands.dev/sdk/guides/security.md), [persistence](https://docs.openhands.dev/sdk/guides/convo-persistence.md), [observability](https://docs.openhands.dev/sdk/guides/observability.md), [models](https://docs.openhands.dev/sdk/guides/llm-registry.md), [repository](https://github.com/OpenHands/software-agent-sdk), [Agent Canvas](https://github.com/OpenHands/OpenHands), [`openhands-ai` on PyPI](https://pypi.org/project/openhands-ai/), [OpenHands Index](https://index.openhands.dev/), [SWE-bench leaderboards](https://www.swebench.com/), [enterprise](https://openhands.dev/enterprise).
- **Strands harness**: [harness guide](https://strandsagents.com/docs/user-guide/harness/), [configuration](https://strandsagents.com/docs/user-guide/harness/reference/configuration/), [interventions](https://strandsagents.com/docs/user-guide/harness/configure/interventions/index.md), [repository](https://github.com/strands-agents/harness-sdk).
- **Microsoft Agent Framework Harness**: [Harness](https://learn.microsoft.com/en-us/agent-framework/concepts/harness), [Durable Extension](https://learn.microsoft.com/en-us/agent-framework/integrations/durable-extension), [repository](https://github.com/microsoft/agent-framework).
- **Also covered**: [Hermes Agent](https://github.com/NousResearch/hermes-agent), [Mistral Vibe](https://docs.mistral.ai/vibe/code/overview), [Vibe CLI repository](https://github.com/mistralai/mistral-vibe), [Vibe SDK on PyPI](https://pypi.org/project/mistralai-vibe-sdk/), [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness), [DeepSeek Python SDK reference](https://github.com/deepseek-ai/deepseek-harness/blob/master/python/sdk/README.md), [DeepSeek session-log upload](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/session/session-log-deepseek/README.md), [smolagents](https://github.com/huggingface/smolagents), [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent), [Pi](https://github.com/earendil-works/pi), [Deep Agents JS](https://github.com/langchain-ai/deepagentsjs), [Mastra](https://mastra.ai/docs/harness/overview), [Vercel AI SDK harnesses](https://ai-sdk.dev/docs/ai-sdk-harnesses).

## Try Pydantic AI Harness

`pip install "pydantic-ai-harness[coder,anthropic]"` (or the extra for your model provider), then follow the [Harness docs](https://pydantic.dev/docs/ai/harness/) from `Coder` on your own repository to an agent built from the capabilities you choose. Choosing the framework underneath instead? Our companion post, [The best Python AI agent frameworks in 2026](https://pydantic.dev/articles/best-python-ai-agent-frameworks), compares those.
