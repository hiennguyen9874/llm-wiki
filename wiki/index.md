---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../AGENTS.md) for storage and maintenance rules.

## Concepts

- [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md) — Pydantic AI v2's single composable unit that bundles instructions, tools, lifecycle hooks, and model settings — with its hook ordering, typing constraints, and deferred on-demand loading.
- [Pydantic AI Conversation state](pydantic-ai-conversation-state.md) — Pydantic AI v2.55's Conversation object — serializable thread state that carries messages, running usage, a conversation id, and pending deferred tool requests across runs.
- [Pydantic AI deferred tool approval](pydantic-ai-deferred-approvals.md) — How Pydantic AI pauses a run for human approval without holding a process open, and how ApprovalReviewer and ToolCallJudge automate opposite halves of the decision.
- [Pydantic AI durable execution](pydantic-ai-durable-execution.md) — The nine durability engines Pydantic AI supports, where each integration ships, and the naming and step rules a deployment must not break.
- [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md) — How Pydantic AI trades integration breadth for type-safe, production-first agent building against LangChain and the OpenAI Agents SDK.
- [Pydantic AI graph builder](pydantic-ai-graph-builder.md) — pydantic-graph's typed GraphBuilder for fan-out, joins and decisions, and its deliberate lack of persistence compared with checkpointing frameworks.
- [Pydantic AI Harness](pydantic-ai-harness.md) — First-party Pydantic AI package of agent batteries — Coder, memory, guardrails, context management, approvals, code mode, and durability integrations — kept outside a deliberately small core.
- [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md) — Pydantic AI's MCP client defaults — local connections, opt-in provider-native connectors, Streamable HTTP transport, and MCP Apps relayed to AG-UI and Vercel AI frontends.
- [Pydantic AI observability](pydantic-ai-observability.md) — Pydantic AI instruments with plain OpenTelemetry, defaults to instrumentation v5 with aggregated usage attributes, and prints a first-run banner until a backend is configured.
- [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md) — Pydantic AI v2.55's unified cache setting and Caching capability, the provider-by-provider effect, and the cache-write cost that keeps caching opt-in.
- [Pydantic AI run controls](pydantic-ai-run-controls.md) — Provider-neutral model error categories, run and request time budgets, append-only instructions, and the warnings Pydantic AI raises when a model ignores a setting.
- [Pydantic AI v2 release](pydantic-ai-v2-release.md) — The Pydantic AI v2 release — capability-centric architecture, a leaner core with opt-in providers, manual migration checks, a shortened major-version support window, and the point releases and security advisories through v2.59.0.
- [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) — ctx.workspace gives Pydantic AI tools one file-and-command API that runs locally or in a sandbox, including the sandbox list, the Daytona addition, and the execution constraints.
- [Pydantic Evals](pydantic-evals.md) — Pydantic's code-first evaluation library — deterministic agentic evaluators over local OpenTelemetry spans, offline datasets, and background online grading.
- [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md) — Vstorm's roughly 20 open-source Pydantic AI capability packages — endorsed by the Pydantic team and wired into the Harness reference example — as the worked example of the community-to-core path.
