---
title: "What Is Pydantic AI 2.0? The Capability Primitive That Changes How You Build Agents"
author: "Luis Chavez-Mattos"
site: "MindStudio"
published: 2026-07-11T00:00:00.000Z
source: "https://www.mindstudio.ai/blog/what-is-pydantic-ai-2-0-capability-primitive"
domain: "mindstudio.ai"
language: "en"
description: "Pydantic AI 2.0 introduces a single composable unit called the capability that bundles tools, instructions, hooks, and guardrails. Here's how it works."
word_count: 2594
---

## The Agent Architecture Problem No One Talks About

Building AI agents is getting easier. Keeping them maintainable is not.

Most developers hit the same wall: you start with a single agent, add tools, system prompt fragments, a few validators, maybe some logging hooks. Then the agent grows. You split it into multiple agents. Suddenly you’re copy-pasting tools across agent definitions, duplicating instructions, and manually syncing guardrails across a system that should be cohesive.

Pydantic AI 2.0 addresses this directly with a concept called the **capability primitive** — a single composable unit that bundles tools, instructions, hooks, and guardrails together so you can build agent behavior in reusable blocks rather than sprawling monoliths.

If you’ve been building with the Pydantic AI framework and wondering how to scale beyond a single agent without losing your mind, this is the concept worth understanding.

---

## What Pydantic AI Actually Is (and Why It Matters)

Before unpacking the capability primitive, it’s worth grounding what Pydantic AI is for developers who haven’t used it.

[Pydantic AI](https://ai.pydantic.dev/) is a Python framework built by the same team behind Pydantic — the library that underpins data validation in FastAPI, SQLModel, and countless other Python projects. The framework extends that same philosophy of type safety and validation into AI agent construction.

REMY IS NOT

- ✕a coding agent
- ✕no-code
- ✕vibe coding
- ✕a faster Cursor

IT IS

✓a general contractor for software

The one that tells the coding agents what to build.

Where most agent frameworks treat tools and outputs loosely, Pydantic AI enforces structure. Agents declare their expected outputs as Pydantic models. Tools are typed functions. The entire agent system is built to catch problems at definition time, not at runtime when a production workflow breaks.

The framework supports multiple model providers — OpenAI, Anthropic, Google Gemini, Mistral, Groq, and others — through a consistent interface. That means you can swap the underlying model without rewriting your tool definitions or agent logic.

Pydantic AI 2.0 takes this further by introducing capabilities as the primary unit of agent composition.

---

## What Is a Capability in Pydantic AI 2.0?

A capability is a self-contained bundle of agent behavior. Think of it as a module — not in the Python sense, but in the agent design sense.

Each capability packages four things together:

- **Tools** — the functions the agent can call to interact with external systems or perform computation
- **Instructions** — system prompt fragments that tell the agent how and when to use those tools
- **Hooks** — lifecycle callbacks that fire at specific moments (before a tool runs, after a response is generated, when a retry happens)
- **Guardrails** — validation logic that constrains what the agent can do or return

Before capabilities, these four things lived separately. You’d define tools in one place, write system prompt instructions in another, wire up hooks manually, and add validators wherever you remembered to. Connecting them required discipline and luck.

With the capability primitive, they travel together. If you give an agent a “web search” capability, it gets the search tool, the instructions for when to use it, the hooks for logging search calls, and the guardrails for filtering results — all at once.

### What a Capability Looks Like in Practice

In Pydantic AI 2.0, a capability is defined as a class or structured object that the agent consumes at initialization. A simplified example:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Capability

web_search_capability = Capability(
    tools=[search_web, fetch_page],
    instructions="Use web search when the user asks about current events or real-time data.",
    hooks=[log_search_call, track_token_usage],
    guardrails=[filter_unsafe_urls, limit_results_to_10]
)

agent = Agent(
    model="openai:gpt-4o",
    capabilities=[web_search_capability, code_execution_capability]
)
```

The agent doesn’t need to know how the capability was assembled. It just receives the bundle and treats it as a coherent piece of behavior.

---

## The Four Components, Explained

### Tools

Tools are the agent’s hands. They’re typed Python functions that the agent can call during a conversation turn to retrieve information, trigger actions, or compute results.

In Pydantic AI, tools use Python type annotations to define their inputs and outputs. The framework automatically generates the schema that the language model uses to decide when and how to call each tool.

Within a capability, tools are scoped. A “calendar” capability owns calendar-related tools. A “CRM” capability owns CRM-related tools. This scoping prevents bloat — agents don’t get access to tools they shouldn’t use for a given context.

### Instructions

Instructions are system prompt fragments. They’re the text that tells the agent what it’s supposed to do with the tools in the capability.

### Everyone else built a construction worker.We built the contractor.

🦺

CODING AGENT

Types the code you tell it to.  
One file at a time.

🧠

CONTRACTOR · REMY

Runs the entire build.  
UI, API, database, deploy.

Keeping instructions inside the capability is the key architectural move. When instructions live separately from tools, they drift. A developer adds a new tool but forgets to update the system prompt. The agent now has a capability it doesn’t know how to use.

When instructions are part of the capability, the tool and the instruction for using that tool are always in sync.

### Hooks

Hooks are lifecycle callbacks. They attach to specific events in the agent’s execution cycle:

- **Pre-tool hooks** — run before a tool is called (useful for logging, auth checks, input validation)
- **Post-tool hooks** — run after a tool returns (useful for result transformation, caching)
- **Response hooks** — fire when the agent generates a response
- **Retry hooks** — trigger when the agent retries a failed tool call

In a traditional setup, hooks get bolted on at the agent level, applying globally to everything. With capabilities, hooks are scoped to the tools and behavior they’re meant to govern. A payment capability can have strict logging hooks without those hooks polluting a simple FAQ capability.

### Guardrails

Guardrails are validation and safety constraints. They can operate at multiple levels:

- **Input guardrails** — validate what the agent receives before it starts reasoning
- **Tool-level guardrails** — constrain what a specific tool can do or return
- **Output guardrails** — validate the agent’s final response before it’s sent

Pydantic AI’s approach to guardrails is notably practical. Rather than building a parallel “safety system,” guardrails are just Python functions with access to the agent’s context. They can be tested like any other code. They can be composed. They can raise exceptions, return fallback values, or trigger retries.

By packaging guardrails inside capabilities, you ensure that a tool’s constraints travel with the tool. If you share a database-query capability between two agents, both agents get the same query-depth limits and injection-prevention logic automatically.

---

## Why Composition Changes Everything

The capability primitive’s real value shows up at scale.

### Reuse Without Copy-Paste

A team building multiple agents — a customer support agent, an internal ops agent, a sales assistant — often needs the same underlying capabilities across all three.

With capabilities as first-class objects, you define a CRM-lookup capability once. You add it to each agent. When the CRM API changes, you update the capability once. All three agents get the fix.

Without this, you’re maintaining parallel copies of the same tools, instructions, and guardrails across multiple agent files. That’s how production systems accumulate silent inconsistencies.

### Safer Multi-Agent Systems

Multi-agent architectures introduce a specific problem: an orchestrating agent needs to delegate to sub-agents, but the sub-agents need to behave consistently. Capabilities help here because they’re portable contracts.

When a sub-agent is given a capability, you know exactly what it can do, what it will log, and what constraints it operates under. The orchestrator doesn’t need to trust that the sub-agent was configured correctly — the capability is the configuration.

This aligns with how Pydantic AI models [multi-agent workflows](https://mindstudio.ai/blog/multi-agent-systems-explained), where each agent in the system has a defined scope and well-understood behavior.

### Testability

Individual capabilities can be unit tested. You don’t need a full agent to verify that a capability’s guardrails reject malformed inputs — you test the capability directly.

Cursor

ChatGPT

Figma

Linear

GitHub

Vercel

Supabase

goremy.ai

## Seven tools to build an app. Or just Remy.

Editor, preview, AI agents, deploy — all in one tab. Nothing to install.

This is a significant improvement over monolithic agent definitions where testing any single behavior requires standing up the entire agent context.

---

## Capabilities and the Broader Shift in Agent Design

Pydantic AI 2.0’s capability primitive reflects a broader shift in how developers are thinking about agent architecture.

Early agent frameworks treated agents as self-contained entities. You configured one agent, ran it, and that was the system. As use cases matured, the need for agent collaboration became clear — but the mental models and tooling hadn’t caught up.

The capability primitive is part of closing that gap. It treats agent behavior as something compositional and transferable, not monolithic.

This connects to what researchers and practitioners call the “capability boundary” problem: in a multi-agent system, each agent should have a well-defined set of capabilities it’s responsible for, and the handoffs between agents should be explicit. Pydantic AI’s approach encodes that idea directly into the framework’s type system.

Compare this to approaches like [LangChain’s tool definitions](https://python.langchain.com/docs/concepts/tools/) or OpenAI’s Assistants API. Both handle tools well, but neither packages tools with their associated instructions, hooks, and guardrails as a single transferable unit. You assemble those pieces yourself, outside the framework.

The capability primitive makes the “right” thing the easy thing — and that’s what good framework design does.

---

## How MindStudio Handles Composable Agent Behavior

Pydantic AI’s capability primitive is a compelling design pattern for Python developers building agents in code. But not every team wants or needs to operate at that abstraction layer.

MindStudio takes a different approach to the same underlying problem: making agent behavior composable, testable, and shareable — without requiring code.

Through MindStudio’s visual workflow builder, you construct agents as connected blocks of behavior. Each block can include AI reasoning steps, tool integrations (from 1,000+ pre-built connectors), conditional logic, and validation steps. These blocks compose into full [AI workflows](https://mindstudio.ai/blog/what-is-an-ai-workflow) that behave consistently across agent runs.

The Agent Skills Plugin goes further for developer teams. It exposes MindStudio’s 120+ typed capabilities — things like `agent.searchGoogle()`, `agent.sendEmail()`, `agent.generateImage()`, `agent.runWorkflow()` — as simple typed method calls that any AI agent (Claude Code, LangChain, CrewAI) can consume directly.

This mirrors the capability primitive pattern: instead of defining the tool, instructions, and guardrails yourself, you call a pre-assembled, production-tested capability that handles the infrastructure layer — rate limiting, retries, authentication — so your agent can focus on reasoning.

If you’re building multi-agent systems and want a practical way to package reusable agent behaviors without standing up your own capability library from scratch, MindStudio’s approach is worth a look. You can try it free at [mindstudio.ai](https://mindstudio.ai/).

---

## Common Patterns for Using Capabilities Effectively

### Layered Capabilities

Not every agent needs every capability. A good pattern is to define capabilities in layers:

1. **Base capabilities** — logging, error handling, context injection (every agent gets these)
2. **Domain capabilities** — CRM, calendar, search (added based on the agent’s role)
3. **Specialized capabilities** — payment processing, medical data access (restricted to specific agents)

This layering maps cleanly to the principle that agents should only have access to the tools they need for their job.

### Capability Versioning

Since capabilities bundle behavior, they can be versioned independently of the agent. You might run `crm_capability_v1` in a stable customer support agent while testing `crm_capability_v2` — with updated instructions and additional guardrails — in a sandbox agent.

This makes capability evolution safer. Changes to a capability don’t automatically propagate to every agent using it.

### Shared Guardrail Libraries

One of the most useful patterns is building a shared guardrail library that multiple capabilities import. Rate limiting, PII detection, output length constraints — these can be written once and applied consistently across every capability in your system.

This is the equivalent of a shared middleware layer, but scoped to agent behavior.

---

## FAQ

### What is Pydantic AI 2.0?

Pydantic AI 2.0 is a version of the Pydantic AI Python framework — built by the team behind the Pydantic data validation library — that introduces the capability primitive as its central unit of agent composition. The framework is designed for building type-safe, production-ready AI agents that can work across multiple model providers.

### What is a capability primitive in Pydantic AI?

A capability primitive is a composable object that bundles four things: tools (functions the agent can call), instructions (system prompt fragments), hooks (lifecycle callbacks), and guardrails (validation and safety constraints). Instead of defining these separately across your agent codebase, you package them together into a reusable capability and attach it to any agent that needs it.

### How does Pydantic AI handle multi-agent systems?

Pydantic AI supports multi-agent systems by treating agents as first-class callable objects. One agent can call another, passing context and receiving structured outputs. The capability primitive makes this safer by ensuring that each agent’s behavior is clearly defined and portable — sub-agents receive capabilities with known constraints, so orchestrating agents don’t need to make assumptions about sub-agent configuration.

### Is Pydantic AI 2.0 better than LangChain for building agents?

Pydantic AI and LangChain serve overlapping but distinct use cases. Pydantic AI is opinionated about type safety and structured outputs — it’s a better fit if you want strict validation and prefer a lighter, more focused framework. LangChain has a broader ecosystem and more pre-built integrations. For teams that already use Pydantic heavily, Pydantic AI’s conventions feel natural and reduce friction. For teams that need maximum tool coverage immediately, LangChain’s ecosystem is hard to beat.

### What are hooks in Pydantic AI agents?

Hooks are callback functions that fire at specific points in an agent’s execution lifecycle. They can run before or after a tool call, when a response is generated, or when the agent retries a failed operation. Hooks are used for logging, monitoring, input validation, result transformation, and other cross-cutting concerns. In Pydantic AI 2.0, hooks are scoped inside capabilities, so they apply only to the behavior they’re meant to govern.

### Can I use Pydantic AI with OpenAI, Anthropic, and other models?

Yes. Pydantic AI uses a model-agnostic interface. You can configure agents to use OpenAI (GPT-4o, o1, o3), Anthropic (Claude), Google Gemini, Mistral, Groq, and other providers. The tool definitions, capability structure, and output validation work consistently across models, so switching models is largely a configuration change rather than a code rewrite.

---

## Key Takeaways

- The capability primitive is Pydantic AI 2.0’s core contribution: a composable unit that bundles tools, instructions, hooks, and guardrails so agent behavior travels as a coherent package.
- Keeping instructions co-located with tools prevents drift — one of the most common sources of agent misbehavior in production systems.
- Capabilities make multi-agent systems more predictable because each agent’s behavior is a known, portable contract.
- Guardrails inside capabilities ensure that safety constraints follow the tools they govern, regardless of which agent uses them.
- For teams building [AI workflows](https://mindstudio.ai/blog/what-is-an-ai-workflow) without deep Python expertise, tools like MindStudio apply the same composability principles through a visual builder with 1,000+ pre-built integrations — giving you the same structural benefits without the framework overhead.

## Remy is new. The platform isn't.

Remy

Product Manager Agent

THE PLATFORM

200+ models 1,000+ integrations Managed DB Auth Payments Deploy

▮

BUILT BY MINDSTUDIO

Shipping agent infrastructure since 2021

Remy is the latest expression of years of platform work. Not a hastily wrapped LLM.

If you’re building agents at any meaningful scale, the capability primitive is the right mental model. Whether you implement it in Pydantic AI 2.0 directly or adopt its principles through another platform, the underlying insight holds: agent behavior should be modular, portable, and testable — not woven into a single definition that no one wants to touch.

[Editorial standards](https://www.mindstudio.ai/editorial-standards)
