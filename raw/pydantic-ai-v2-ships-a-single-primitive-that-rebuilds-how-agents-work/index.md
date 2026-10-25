---
title: "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work"
author: "AlphaSignal Newsroom"
site: "AlphaSignal"
published: 2026-06-23T17:46:42.000Z
source: "https://alphasignal.ai/news/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work"
domain: "alphasignal.ai"
language: "en"
description: "PydanticAI v2 is stable after seven betas, introducing the capability as the core primitive for composing agent behavior."
word_count: 1376
---

[Pydantic AI v2](https://pydantic.dev/articles/pydantic-ai-v2?utm_source=alphasignal) is out, and it ships with a single new idea that reshapes how you build agents: the **capability**. The inner loop of an agent is settled by now -- call the model, run a tool, feed the result back. The real leverage is in the layer around it: the hooks that rewrite what the model sees mid-run, context management, steering, and loading the right tools just in time. v2 turns that whole layer into one thing you compose: the capability.

After seven betas, Pydantic AI v2 is now stable. The team shipped Pydantic AI v1 last September and put out more than a hundred releases since, without once breaking user code. v2 is the first major version bump, and it comes with a deliberate architectural shift.

## One primitive to rule the loop

The capability lets you build agents from composable units that bundle tools, hooks, instructions, and model settings into reusable pieces. Think of it as the plugin format for agent behavior. Instead of scattering your memory system, guardrails, or coding toolkit across separate config objects and decorators, you package them as a single capability and attach it to an agent.

Here is what that looks like in practice:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Capability, Thinking, ToolSearch, WebSearch
from pydantic_ai.mcp import MCPToolset
from pydantic_ai_harness import CodeMode
agent = Agent(
    'anthropic:claude-opus-4-7',
    instructions='Research thoroughly and cite your sources.',
    capabilities=[
        Thinking(effort='high'),   # extended thinking, unified across providers
        CodeMode(),                # replaces N tool calls with one sandboxed run_code call
        WebSearch(),               # native where the provider supports it, local fallback otherwise
        ToolSearch(),              # discover tools on demand instead of listing hundreds upfront
        Capability(
            id='github',
            description='Look up GitHub issues, pull requests, and code.',
            instructions='Use the GitHub tools when a question is about a repository.',
            toolset=MCPToolset('https://mcp.example.com/github'),
            defer_loading=True,    # stays out of the prompt until the model loads it on demand
        ),
    ],
)
```

The `defer_loading=True` flag is worth calling out specifically. The capability is why so much has landed lately -- on-demand loading so a deferred capability stays out of the prompt until the model needs it, a pending message queue for steering a run mid-flight, and even durable execution. Because capabilities are serializable, an agent can be loaded from a spec file, and the surface is small enough that an LLM can write one.

## Why on-demand loading matters for your token bill

Before this, adding a capability meant loading everything onto the model immediately -- instructions, tools, all of it, every request, whether it was needed or not. You can use built-in capabilities for web search, thinking, and MCP, pick from the Pydantic AI Harness capability library, build your own, or install third-party capability packages. With deferred capabilities, the model starts with a compact catalog of what's available. When it decides it needs a capability, it calls `load_capability`, and the full bundle -- instructions, tools, hooks, model settings -- is injected in one shot.

This directly addresses one of the most common complaints about production agents: bloated context windows. Agents with dozens of tools have to stuff every tool description into every prompt. With `defer_loading=True`, the model sees only a one-line description until it actually needs the capability.

## The Harness: batteries for your agent

Pydantic AI Harness is the official capability library for Pydantic AI. Pydantic AI core ships the agent loop, model providers, the capabilities/hooks abstraction, and only the capabilities that need deep provider support or are fundamental to every agent. The Harness is where everything else lives: standalone capabilities that make specific categories of agents powerful, or that are still finding their final shape. It ships as a separate package so capabilities can iterate faster without the strict backward-compatibility requirements of core.

The split is deliberate. Running `uv add pydantic-ai` still includes OpenAI, Anthropic, and Google by default, but the long tail of providers like Bedrock, Groq, and Mistral is now opt-in, so you install only what you use. The Harness, meanwhile, ships capabilities like memory, guardrails, context management, file system access, and code mode -- things that are powerful but not universally needed.

What's currently available or in progress in the Harness ecosystem:

- **CodeMode** -- replaces multiple tool calls with a single sandboxed code execution, powered by Monty (Pydantic's safe Python subset)
- **ContextManagerCapability** -- real-time token tracking with auto-compression at a configurable threshold
- **MemoryCapability** -- persistent `MEMORY.md` per agent name
- **SubAgentCapability** -- spawn, check, and cancel subagents as tools
- **TodoCapability** -- task planning with subtasks, dependencies, and PostgreSQL persistence
- **ConsoleCapability** -- filesystem and shell access

As a capability stabilizes and proves itself broadly essential, it can graduate into core -- code mode is an early candidate. Many capabilities benefit from a "fall up" pattern: they typically start as a local implementation that works with every model, then gain provider-native support that uses the provider's built-in API when available, auto-switching between the two.

## What's actually new vs. what just got formalized

The capability concept is both a new API and a reframing of things that already existed. The capability is why so much has landed lately -- in recent releases the team turned more and more of the framework into capabilities: instrumentation, deferred tool calls resolved in the loop, server-side compaction for OpenAI and Anthropic, capabilities built dynamically per run. v2 makes this the official, first-class way to extend an agent.

The other key changes in v2:

- **OpenAI model names** now use the Responses API by default; use the `openai-chat:` prefix to stay on Chat Completions
- **WebSearch and WebFetch** are native by default, with local fallbacks
- **MCP servers** run locally by default when given a URL
- **Instrumentation** defaults to version 5, with aggregated token-usage attributes
- **Function tools** requested alongside a successful output tool now run instead of being skipped (`end_strategy='graceful'`)
- **Agent spec files** -- define agents entirely in YAML/JSON, no code required

## Where PydanticAI fits in a crowded field

The agent framework space is noisy. LangChain has the ecosystem breadth advantage, with hundreds of integrations. If you prioritize type safety and debuggability over integration coverage, PydanticAI and the OpenAI Agents SDK are sharper tools for the job. The trade-off is real though: the PydanticAI ecosystem is roughly 15 times smaller than LangChain's, and third-party integrations and community resources are thin.

Where PydanticAI has consistently won is production reliability. In Pydantic AI, your output models are Python dataclasses or Pydantic models -- the framework literally won't return a response that fails validation. The v2 capability system extends this philosophy: instead of just validating outputs, you now have a structured, typed way to compose the entire behavior of an agent.

## The version policy shift

One deliberate change comes with v2: the no-breaking-changes window between major versions moves from six months to three. This is not the team caring less about stability. The field moves fast enough that committing further out means committing to decisions that fit today and not the world three months from now. No breaking changes within a major version, and deprecations always land before removals -- the latest v1 already warns about most of what v2 changes.

## Getting started and migrating from v1

Install or upgrade with:

```
uv add pydantic-ai
```

Coming from v1? Upgrade to the latest v1 first and clear every deprecation warning -- point a coding agent at them. That covers most of the migration, and if you do it, almost nothing else should break. The [full Upgrade Guide](https://pydantic.dev/docs/ai/project/changelog/?utm_source=alphasignal#breaking-changes) covers every behavior change. The Harness is a separate install:

```
uv add pydantic-ai-harness
```

PydanticAI is open source and free to use. Observability through [Pydantic Logfire](https://pydantic.dev/logfire?utm_source=alphasignal) has its own pricing tier, but the core framework carries no cost. The Harness uses 0.x versioning, signaling that its APIs are still stabilizing -- minor releases may include breaking changes, but patch releases will not.

The capability primitive is a meaningful step toward agents that can reason about and modify their own behavior. Because capabilities are serializable and the surface is small enough that an LLM can write one, it points at something the team is excited about: with Monty, their safe Python subset, an agent could propose its own declarative tweaks -- like adding a hook that trims an oversized tool result before it fills the context window. That loop is not fully closed yet, but v2 lays the groundwork.

Trending

![](assets/twitter.3.ico) ![](assets/favicons.png) ![](assets/favicons-2.png)
