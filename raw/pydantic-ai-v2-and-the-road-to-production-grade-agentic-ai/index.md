---
title: "Pydantic AI v2 and the road to production-grade agentic AI"
author: "Nicholas Berryman"
site: "Vstorm"
published: 2026-07-03T10:18:43+00:00
source: "https://vstorm.co/pydanticai/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/"
domain: "vstorm.co"
language: "en"
description: "Pydantic AI v2 bundles instructions, tools, hooks and model settings into composable capabilities, with Vstorm packages linked from the Harness."
word_count: 1148
---

Pydantic AI v2 bundles instructions, tools, hooks and model settings into composable capabilities, with Vstorm packages linked from the Harness.

On June 23, 2026, the Pydantic team shipped Pydantic AI v2, built around a single composable primitive: the capability. It bundles an agent's instructions, tools, lifecycle hooks, and model settings into one unit, paired with a leaner core and the first-party Pydantic AI Harness.

The release matters to anyone moving agents from demo to deployment, because it makes the production layer composable rather than hand-wired. It also names Vstorm directly. Our open-source capabilities are endorsed by the Pydantic AI team and linked from the Harness, drawn from patterns proven across 30+ production deployments. This is what a working partnership looks like in the open.

The hard part of an agent was never the inner loop. Call the model, run a tool, feed the result back: that pattern settled long ago. What breaks in production is everything wrapped around it. Memory that survives between sessions. Context that does not overflow. Guardrails that catch a bad tool call before it reaches your data.

Tool discovery that does not flood the prompt with hundreds of external tool definitions. Steering that lets an operator correct a run in real time. We know this because we have built that layer for AI agents, over and over, across more than 30 production agent systems.

That is exactly the layer Pydantic AI v2 reorganises. Released on [June 23, 2026](https://pydantic.dev/articles/pydantic-ai-v2), v2 turns the whole surrounding layer into one thing you compose: the **capability**.

## What v2 actually changes

A capability is a single, composable unit that carries an agent's instructions, tools, lifecycle hooks, and model settings together, so a memory system or a guardrail can reach every layer of the agent, from the system prompt to toolsets exposed over the Model Context Protocol, through one concept ( [capabilities docs](https://pydantic.dev/docs/ai/core-concepts/capabilities/)). Around it sits a deliberately smaller core and the first-party **Pydantic AI Harness**, described by the team as the batteries for your agent ( [Harness overview](https://pydantic.dev/docs/ai/harness/overview/)).

The split is the interesting part. Core stays small and stable, shipping the loop, the providers, and the capabilities every agent needs. Everything else lives in the Harness, where it can move fast. A capability can then graduate into core once it proves broadly essential. That path, from community building block to endorsed package to upstreamed core feature, is the road Vstorm has been travelling.

### Why this matters for production-grade agentic AI

Anyone who has shipped a generative AI pilot knows the pattern: the proof of concept impresses stakeholders, then reality hits. Real tasks are not single-step, and simple agents lose the thread, cannot recover from errors, and offer no visibility into their reasoning. We wrote about this gap in detail when we released [pydantic-deep](https://pydantic.dev/articles/pydantic-deep-agents) as a guest post on pydantic.dev.

The capability model speaks straight to that gap. **Production-grade agentic AI** depends on composing the unglamorous layer reliably: observability, context limits, guardrails, human-in-the-loop approval, knowledge transfer. Pydantic AI adds structured output validation and type safety on top of large language models, which is what makes agentic AI systems debuggable rather than opaque. v2 gives that whole layer a clean, type-safe shape you assemble from parts instead of re-wiring per project. For teams that value owning their AI system with no lock-in, this is the difference between one you maintain and one you fight.

## Where Vstorm fits: endorsed, linked, and upstreaming

The v2 announcement names us by name. The Pydantic team writes that community capabilities are part of the release, and that Vstorm and others ship capabilities the team endorses and links to from the Harness, and is working to upstream ( [announcement](https://pydantic.dev/articles/pydantic-ai-v2)).

This is not a logo on a partner page. The official Harness wires Vstorm packages into its own reference example, including `pydantic_ai_summarization` for context management and `pydantic_deep` for memory and stuck-loop detection ( [Harness README](https://github.com/pydantic/pydantic-ai-harness/blob/main/README.md)). Our **Pydantic AI capabilities** did not come from a whiteboard. They are roughly 20 open-source packages distilled from real engagements, covering middleware, subagents, summarization, monitoring, and a full-stack agent template, each one a pattern that survived production ( [Vstorm OSS](https://oss.vstorm.co/), [vstorm-co on GitHub](https://github.com/vstorm-co)).

That is the arc we care about: community, to endorsed, to upstreamed, to core. We do not only use the framework. We help build it.

> "Vstorm are exactly the kind of partner we love working with – sharp engineers who actually build with Pydantic AI in production, and who give us the honest feedback that makes the framework better." Samuel Colvin, Founder and CEO, Pydantic ( LinkedIn )

## What it means for teams building agentic AI implementation today

If your team is already in the Pydantic ecosystem, v2 changes the economics of your next build. The capability model plus the Harness means less bespoke plumbing between a prototype and an owned, observable production system. You assemble the production layer from composable parts, keep full control of the code, and stay free to switch models. That is the practical shape of an **agentic AI implementation** that does not trap you.

In practice, composing that layer is a few lines. The same tools and hooks run unchanged when you switch the underlying model:

from pydantic\_ai import Agent, RunContext from pydantic\_ai\_harness import CodeMode agent = Agent( 'anthropic:claude-sonnet-4-6', system\_prompt='Research thoroughly and cite your sources.', capabilities=\[CodeMode()\], ) @agent.tool def lookup(ctx: RunContext, query: str) -> str: """Look up a record the agent can act on."""... # Swap the model; the tools and hooks above run unchanged researcher = Agent('openai:gpt-5.2', capabilities=\[CodeMode()\]) That is how agentic AI works once you stop hand-wiring the layer around the loop.

The contrast is concrete:

| **Concern** | **Before v2 (hand-wired layer)** | **Pydantic AI v2 (composable capabilities)** |
| --- | --- | --- |
| Memory and context | Custom code per project, re-built each time | Attach a capability; context management composes in |
| Tool discovery | Hundreds of definitions loaded upfront | Tool search; tools load on demand |
| Guardrails and observability | Bolted on late, often inconsistent | Capabilities and hooks, consistent across the loop |
| Path to production | Re-wiring glue before touching agent logic | Compose proven building blocks, focus on the problem |
| Ownership | Risk of framework lock-in | Open source, model-agnostic, fully yours |

## One ecosystem, from primitive to production

The loop was always the easy part. v2 makes the hard part composable, and Vstorm is helping build it in the open, contributing the capabilities that turn a model into a system that survives contact with production. For mid-market teams moving from agentic vision to deployment, that is the point: you do not have to choose between a framework you trust and a partner who has shipped this before. Here, they are the same ecosystem.

> "Vstorm haven't just adopted Pydantic AI, they've helped shape it – contributing extensions, pushing on the rough edges, and showing us where real-world agent systems break. That kind of collaboration is gold for an open source project." Samuel Colvin, Founder and CEO, Pydantic ( source )
