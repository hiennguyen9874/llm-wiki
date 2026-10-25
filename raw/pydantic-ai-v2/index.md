---
title: "Pydantic AI v2: capabilities, a leaner core, and the Harness"
author: "Douwe Maan"
site: "Pydantic"
published: 2026-06-23T09:00:00.000Z
source: "https://pydantic.dev/articles/pydantic-ai-v2"
domain: "pydantic.dev"
language: "en"
description: "Pydantic AI v2 is here: one capability primitive for instructions, tools, hooks, and settings, a slimmer core, and the Pydantic AI Harness."
word_count: 1158
---

**Pydantic AI v2 is here, and your agents have never been more capable.** We shipped [Pydantic AI v1](https://pydantic.dev/articles/pydantic-ai-v1) last September and have put out [more than a hundred releases](https://github.com/pydantic/pydantic-ai/releases) since, without once breaking your code. The inner loop of an agent is settled by now: call the model, run a tool, feed the result back. The real leverage is in the layer around it: not just the instructions and tools you give an agent, but the hooks that rewrite what the model sees mid-run, context management, steering, and loading the right tools just in time. v2 turns that whole layer into one thing you compose: the [capability](https://pydantic.dev/docs/ai/core-concepts/capabilities/).

> [!note] Note
> - `uv add pydantic-ai` gets you v2.
> - Coming from v1? Upgrade to the latest v1 first and clear every deprecation warning (point a coding agent at them). That covers most of the migration, and if you do it, almost nothing else should break. The behavior changes a warning couldn't catch are short:
> 	- `openai:` model names now use the Responses API; use `openai-chat:` to stay on Chat Completions.
> 		- `WebSearch` and `WebFetch` are native by default, and `MCP(url=...)` runs locally by default.
> 		- Instrumentation defaults to version 5, with aggregated token-usage attributes.
> 		- Function tools requested alongside a successful output tool now run, instead of being skipped (`end_strategy='graceful'`).
> - Full list in the [Upgrade Guide](https://pydantic.dev/docs/ai/project/changelog/#breaking-changes). Questions or breakage? [GitHub](https://github.com/pydantic/pydantic-ai/issues) or [Slack](https://pydantic.dev/docs/logfire/join-slack/).

## One primitive: the capability

A [capability](https://pydantic.dev/docs/ai/core-concepts/capabilities/) bundles an agent's instructions, tools, lifecycle hooks, and model settings into a single, composable unit, so a whole extension (a memory system, a guardrail, a coding toolkit) can reach every layer of the agent through one concept. It is the unit of agent behavior that lives in the loop, and you attach one the same way you attach any other:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Capability, Thinking, ToolSearch, WebSearch
from pydantic_ai.mcp import MCPToolset
from pydantic_ai_harness import CodeMode

agent = Agent(
    'anthropic:claude-opus-4-7',
    instructions='Research thoroughly and cite your sources.',
    capabilities=[
        Thinking(effort='high'),  # extended thinking, unified across providers
        CodeMode(),               # one run_code call replaces N tool calls, sandboxed by Monty
        WebSearch(),              # native where the provider supports it, local fallback otherwise
        ToolSearch(),             # discover tools on demand instead of listing hundreds upfront
        Capability(
            id='github',
            description='Look up GitHub issues, pull requests, and code.',
            instructions='Use the GitHub tools when a question is about a repository.',
            toolset=MCPToolset('https://mcp.example.com/github'),
            defer_loading=True,  # stays out of the prompt until the model loads it on demand
        ),
    ],
)
```

Some of these are just model settings, like [`Thinking`](https://pydantic.dev/docs/ai/advanced-features/thinking/). Some wrap a [native tool](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/), like `WebSearch`, which runs natively where the provider supports it and falls back to a local implementation otherwise. The powerful ones use [hooks](https://pydantic.dev/docs/ai/core-concepts/hooks/) to read and rewrite what the model sees on every step, including its tools, its instructions, and its message history. [Code mode](https://github.com/pydantic/pydantic-ai-harness/tree/main/pydantic_ai_harness/code_mode) and [tool search](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-search) are built on exactly the same public hooks your own capabilities would use, so the batteries we ship double as worked examples.

The GitHub entry shows a richer shape: a [`Capability`](https://pydantic.dev/docs/ai/core-concepts/capabilities/) you build inline from an id, a description, some instructions, and a toolset (here an MCP server). Marked `defer_loading=True`, it stays out of the prompt until the model needs it: the model sees only the one-line description in a compact catalog, then loads the whole bundle, instructions and tools together, in a single step when it decides to.

The capability is also why so much has landed lately. In recent releases we have turned more and more of the framework into capabilities: [instrumentation](https://pydantic.dev/docs/ai/integrations/logfire/), [deferred tool calls resolved in the loop](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/), [server-side compaction for OpenAI and Anthropic](https://pydantic.dev/docs/ai/core-concepts/capabilities/#compaction), [capabilities built dynamically per run](https://pydantic.dev/docs/ai/core-concepts/capabilities/#dynamically-building-a-capability), [on-demand loading](https://pydantic.dev/docs/ai/core-concepts/capabilities/#on-demand-capabilities) so a deferred capability stays out of the prompt until the model needs it, a [pending message queue](https://pydantic.dev/docs/ai/core-concepts/message-history/#injecting-messages-mid-run) for steering a run mid-flight, and even durable execution, which is [moving onto the same capability layer](https://github.com/pydantic/pydantic-ai/pull/4977) (in progress, with a runtime extension point [tracked for after v2](https://github.com/pydantic/pydantic-ai/issues/5477)).

Because capabilities are serializable, an agent can be loaded from a [spec file](https://pydantic.dev/docs/ai/core-concepts/agent-spec/), and the surface is small enough that an LLM can write one: point a coding agent at the [capabilities docs](https://pydantic.dev/docs/ai/core-concepts/capabilities/) and it builds most of what you need. It points at something we are excited about, though not a promise yet: with [Monty](https://pydantic.dev/articles/pydantic-monty), our safe Python subset, an agent could propose its own declarative tweaks, like adding a hook that trims an oversized tool result before it fills the context window. And because [instrumentation](https://pydantic.dev/docs/ai/integrations/logfire/) is now a capability too, the traces you already send to [Logfire](https://pydantic.dev/logfire) close the loop: an agent that reads its own runs could spot the clearly-wrong things, a pair of contradictory instructions or a tool whose description doesn't match what it does, and suggest the fix. We have already started turning that loop into something real in [Logfire](https://pydantic.dev/logfire).

## The Harness and a leaner core

Some capabilities ship with Pydantic AI itself; more come from the first-party [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/overview/), the batteries for your agent (memory, guardrails, context management, file system access, code mode, and more); and others are third-party or your own. Plenty already come from the community: [VStorm](https://github.com/vstorm-co) and others ship capabilities that [we endorse and link to from the Harness](https://github.com/pydantic/pydantic-ai-harness#capability-matrix), and are working to upstream. The Harness is where we are spending June: a wave of new capabilities, plus a headless coding agent built on Pydantic AI that we are dogfooding across Pydantic's own repositories.

The split is deliberate. Core stays small and stable, shipping the loop, the providers, the capability and hooks API, and only the capabilities that need deep provider support or are fundamental to every agent. Everything else lives in the Harness, where it can move fast, and a capability can graduate into core once it proves broadly essential. v2 leans into that: `uv add pydantic-ai` still includes OpenAI, Anthropic, and Google by default, but the long tail of providers (`bedrock`, `groq`, `mistral`, and friends) is now opt-in, so you install only what you use. The full [Upgrade Guide](https://pydantic.dev/docs/ai/project/changelog/#breaking-changes) covers every behavior change, split into what a deprecation warning already caught and what to check by hand.

## A word on the version policy

One deliberate change comes with v2: the no-breaking-changes window between major versions moves from six months to three. This is not us caring less about stability. The field moves fast enough that committing further out means committing to decisions that fit today and not the world three months from now. Everything else stands. No breaking changes within a major version, and deprecations always land before removals, exactly as you saw in the run-up to this release: the latest v1 already warns about most of what v2 changes.

## Try it

```bash
uv add pydantic-ai
```

Try it on something real, keep the [Upgrade Guide](https://pydantic.dev/docs/ai/project/changelog/) handy if you are coming from v1, and tell us what you build (or what breaks) on [GitHub](https://github.com/pydantic/pydantic-ai/issues) or in [Slack](https://pydantic.dev/docs/logfire/join-slack/). We can't wait to see it.
