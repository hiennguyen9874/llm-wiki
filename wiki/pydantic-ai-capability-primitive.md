---
type: Concept
title: Pydantic AI capability primitive
description: Pydantic AI v2's single composable unit that bundles instructions, tools, lifecycle hooks, and model settings — with its hook ordering, typing constraints, and deferred on-demand loading.
tags: [ml, pydantic-ai, agents, llm-frameworks]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T10:58:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: pydantic-ai-v2
    resource: ../raw/pydantic-ai-v2/index.md
    scope: ../raw/pydantic-ai-v2/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2: capabilities, a leaner core, and the Harness"
  - id: alphasignal-v2-news
    resource: ../raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/index.md
    scope: ../raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work"
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: mindstudio-capability-primitive
    resource: ../raw/what-is-pydantic-ai-2-0-capability-primitive/index.md
    scope: ../raw/what-is-pydantic-ai-2-0-capability-primitive/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "What Is Pydantic AI 2.0? The Capability Primitive That Changes How You Build Agents"
  - id: pydantic-image-gen-2026
    resource: ../raw/image-generation/index.md
    scope: ../raw/image-generation/
    kind: article
    revision: sha256:2563fee14c8dd9209912c64e26cb10d888eb54d1e0d027343f546fe21ceaf69e
    title: "Generate images with Pydantic AI"
  - id: pydantic-image-gen-capability-docs
    resource: ../raw/capabilities/image-generation/index.md
    scope: ../raw/capabilities/image-generation/
    kind: documentation
    revision: sha256:9a2451a4bea14f49a395b66f9464f2c43f01aea4c52aba6dbb65694390deead9
    title: "ImageGeneration Capability"
  - id: pydantic-docs-capabilities-overview
    resource: ../raw/capabilities/overview/index.md
    scope: ../raw/capabilities/overview/
    kind: docs
    revision: sha256:6434ebdb6f8a86b177d4659f738e214d9f719260787ae93cd1bcda3811bd15c
    title: "Capabilities"
---

The **capability** is the single unit of agent behavior that Pydantic AI v2 composes. It bundles an agent's instructions, tools, lifecycle hooks, and model settings into one object, so an extension such as a memory system, a guardrail, or a coding toolkit reaches every layer of the agent through one concept and is attached the same way as anything else: `Agent(..., capabilities=[...])`[^pydantic-ai-v2]

## What a capability bundles

- **Instructions** — prompt text the capability contributes to the agent.
- **Tools / toolsets** — callable tools, native tools, or MCP toolsets.
- **Lifecycle hooks** — callbacks that read and rewrite what the model sees on every step: its tools, its instructions, and its message history.
- **Model settings** — provider-level request settings.
- **Models** — static or adaptive model selection and application-specific model ID resolution.

The fifth line is what the vendor's capabilities catalog adds: it lists model selection beside the other four, while `instructions` and `model_settings` remain parameters on `Agent` (or `AgentSpec`) and capabilities are reserved for behaviour beyond that simple configuration[^pydantic-docs-capabilities-overview] The capabilities that fill those slots are listed in the [capability catalog](pydantic-ai-capability-catalog.md).

The article's example uses the shape `Capability(id='github', description='Look up GitHub issues, pull requests, and code.', instructions=..., toolset=MCPToolset('https://mcp.example.com/github'), defer_loading=True)`, which shows a capability built inline from an ID, a description, instructions, and a toolset rather than subclassed[^pydantic-ai-v2]

Capability shapes vary in depth. `Thinking` (extended thinking unified across providers) is essentially a model setting; `WebSearch` wraps a native tool that runs natively where the provider supports it and falls back to a local implementation otherwise; the more powerful capabilities use hooks to rewrite the model's per-step view[^pydantic-ai-v2] Image generation shows the same native-or-local split at a finer grain: `ImageGeneration()` is native only, `ImageGeneration(local=generator)` prefers native generation where the model supports it and falls back to the supplied generator otherwise, and `ImageGeneration(native=False, local=generator)` forces the local path — a capability-level fallback, not automatic failover between image providers[^pydantic-image-gen-2026] The fallback itself has three shapes, so the "local" half is not one mechanism: `local=` takes a direct generator or your own tool, `fallback_image_model='provider:model'` names a direct image model, and `fallback_subagent_model='provider:model'` runs a second agent whose native image tool draws the picture[^pydantic-image-gen-capability-docs]

One vendor explainer lists guardrails as the fourth part of the bundle instead of model settings; see [Contradictions](#contradictions).

## Why the parts travel together

A vendor explainer gives the design argument for bundling, though no measurement of it[^mindstudio-capability-primitive]:

- **Drift.** When instructions live separately from tools they diverge: a developer adds a tool but not the prompt text, and the agent ends up holding a capability it does not know how to use. Co-locating the two keeps the tool and the rule for using it in sync.
- **Scoped hooks.** Hooks bolted on at the agent level apply globally; hooks owned by a capability let a payment capability carry strict logging without that machinery reaching a simple FAQ capability.
- **Guardrails that follow their tools.** Constraints travel with the tool they govern, so sharing a database-query capability between two agents gives both the same query-depth limits and injection prevention without re-declaration.
- **Portable contracts for multi-agent systems.** An orchestrator delegating to a sub-agent knows what it can do, what it will log, and what constrains it — the explainer's phrasing is that "the capability is the configuration," so the orchestrator need not assume the sub-agent was wired correctly.
- **Testability.** A capability can be unit-tested on its own instead of standing up a whole agent to check one guardrail.

The explainer ties this to a "capability boundary" idea from multi-agent practice — each agent owns a well-defined set of capabilities and the handoffs between them are explicit — and argues the primitive encodes that boundary in the type system[^mindstudio-capability-primitive] These are the argument's own claims about design; no production incident, measurement, or library inspection backs them.

## Hook lifecycle and ordering

Hooks follow a fixed lifecycle at every stage — run, node, model request, tool call, output: `wrap_*` enters, then `before_*`, then the operation (`on_*_error` if it fails), then `after_*`, then `wrap_*` exits. Within one `Hooks` instance, `before_*`, `after_*` and `on_*_error` fire in registration order; `wrap_*` hooks nest as middleware with the first registered outermost; across capabilities, `after_*` and error hooks run in reverse order[^dd-v2-tour-2026] Since v2.54.0 a `wrap_*` hook encloses the stage's complete lifecycle, which changes what a wrapper observes compared with earlier releases.

A `Hooks` object is itself attached as a capability, so the same declaration carries the callbacks[^dd-v2-tour-2026]:

```python
hooks = Hooks[SupportDeps]()

@hooks.on.before_model_request
async def log_request(
    ctx: RunContext[SupportDeps], request_context: ModelRequestContext
) -> ModelRequestContext:
    print(f'model request #{ctx.run_step} for {ctx.deps.customer_id}')
    return request_context

agent = Agent('anthropic:claude-sonnet-5-5', deps_type=SupportDeps, capabilities=[Caching(), hooks])
```

Two further details from the same example: `result.output` is statically typed by the agent's output type, and `result.usage` is a property in V2 rather than a method[^dd-v2-tour-2026]

## Authoring constraints

| Constraint | Detail |
| --- | --- |
| Strict typing on inline capabilities | `Capability(...)` is inferred as `Capability[Unknown]` under strict Pyright; annotate `Capability[object]` or the deps type |
| Deferral needs an identity | `defer_loading=True` requires an `id`, since the catalog entry is keyed by it |
| Capability vs. subclass | No subclassing is required: instructions, tools and a description can be passed declaratively, and a tool's docstring becomes its description |

The typing constraint is a direct consequence of V2's generic default moving from `None` to `object`, the same change that makes `RunContext[None]` invalid for a deps-less agent[^dd-v2-tour-2026] The same `deps_type` declaration and `RunContext.deps` access that this page's sample relies on are compiled in [dependencies](pydantic-ai-dependencies.md).

The vendor documentation describes the declarative form as "defining a skill": `Capability(id='refunds', description='Use for refund eligibility and refund status.', instructions=...)` followed by decorating a function on that object with `@refunds.tool_plain`, after which the bundle attaches as `Agent('openai:gpt-6.1-sol', capabilities=[refunds])`[^pydantic-docs-capabilities-overview] Adding `defer_loading=True` turns the same bundle into an on-demand capability, which is also how an Agent Skill file is wrapped into a capability; behaviour beyond instructions, tools and toolsets — lifecycle hooks, model settings, native tools — is where subclassing `AbstractCapability` is still required[^pydantic-docs-capabilities-overview]

## Where capabilities ship

The split is concrete, and it decides which version policy covers a capability[^dd-v2-tour-2026]:

| Tier | Capabilities |
| --- | --- |
| Core `pydantic-ai` | `Caching`, `Hooks`, `MCP`, `LocalWorkspace`, `Thinking`, `ToolSearch`, and others needing model or framework support, plus Temporal, DBOS and Prefect durability under `pydantic_ai.durable_exec` |
| [Harness](pydantic-ai-harness.md) | `Coder`, `Memory`, `Guardrails`, `Spend Limits`, `Subagents`, `Planning`, `Code Mode` (Monty sandbox), `Step Persistence`, `Compaction`, and AWS Lambda, Absurd and pgtask durability |
| Third-party | Community packages such as [Vstorm's](vstorm-pydantic-ai-capabilities.md) |

## Deferred, on-demand loading

Marking a capability `defer_loading=True` keeps it out of the prompt until the model needs it. The model sees only the capability's one-line description in a compact catalog, and when it decides to load the capability it receives the whole bundle — instructions and tools together — in a single step. `ToolSearch` applies the same idea to tool discovery instead of listing hundreds of tools upfront[^pydantic-ai-v2] The documented contract behind the flag — the catalog element, the parts that activate together, the per-provider cache bill, loading from code and the durable-execution limits — is compiled in [on-demand capabilities](pydantic-ai-on-demand-capabilities.md).

Press coverage names the loading call `load_capability` and frames the motive as token cost: an agent with dozens of tools otherwise stuffs every tool description into every request, so deferral leaves a one-line description in the prompt until the capability is actually needed[^alphasignal-v2-news] This is the release's answer to bloated context windows, not a change to the loop itself. The same idea reaches skill files: v2.57.0 made the `Skills` capability honour the `disable-model-invocation` and `user-invocable` frontmatter fields[^dd-v2-tour-2026]

## Fall-up: local first, native where available

Capabilities often follow a "fall up" pattern: an implementation starts locally, working with every model, and later gains provider-native support that auto-switches to the provider's own API when one exists[^alphasignal-v2-news] `WebSearch` is the visible instance — native where the provider supports it, local fallback otherwise[^pydantic-ai-v2]

## Hooks are the public extension mechanism

`CodeMode` and `ToolSearch` are reported to be built on exactly the same public hooks that user-defined capabilities would use, so the shipped batteries also serve as worked examples of the API[^pydantic-ai-v2] This matters for trust: the extension mechanism is not a private layer that only first-party code can reach.

## Framework features expressed as capabilities

The maintainers state they have progressively moved framework features onto this primitive: instrumentation, deferred tool calls resolved in the loop, server-side compaction for OpenAI and Anthropic, capabilities built dynamically per run, on-demand loading, a pending message queue for steering a run mid-flight, and durable execution, which is moving onto the same layer and was still in progress at publication[^pydantic-ai-v2]

## Composing capabilities at scale

A vendor explainer recommends three patterns for a growing capability library[^mindstudio-capability-primitive] They are practitioner advice about how to use the primitive, not documented framework features:

| Pattern | Shape |
| --- | --- |
| Layered capabilities | Base capabilities every agent gets (logging, error handling, context injection), domain capabilities added by role (CRM, calendar, search), and specialized capabilities restricted to specific agents (payments, regulated data) |
| Capability versioning | A capability versions independently of the agents using it: run `crm_capability_v1` in a stable support agent while testing `crm_capability_v2` with changed instructions and extra guardrails in a sandbox agent, so a change does not land in every consumer at once |
| Shared guardrail library | Rate limiting, PII detection, and output-length limits written once and imported by many capabilities — described as a middleware layer, but scoped to agent behaviour |

## Serialization, authoring, and self-improvement

- **Spec files:** because capabilities are serializable, an agent can be loaded from a spec file.
- **LLM authoring:** the surface is described as small enough that a coding agent pointed at the capabilities documentation can build most of what is needed.
- **Self-proposed tweaks (aspirational):** with Monty, Pydantic's safe Python subset, an agent could propose its own declarative tweaks, such as a hook that trims an oversized tool result before it fills the context window. The article explicitly frames this as not a promise yet.
- **Trace-driven improvement (early):** because instrumentation is now a capability, an agent reading its own runs and their Logfire traces could spot clearly wrong things — contradictory instructions, or a tool description that does not match what the tool does — and suggest a fix. The article says work on that loop has started in Logfire.

## Contradictions

The sources disagree about what a capability bundles, and no account inspects the package to settle it:

- **Maintainer account:** instructions, tools, lifecycle hooks, and model settings[^pydantic-ai-v2]; the type-checked tour shows the declarative form carrying `id`, `description`, `instructions`, `toolset`, and `defer_loading`[^dd-v2-tour-2026]
- **Vendor explainer:** tools, instructions, hooks, and guardrails, with a sample `Capability(tools=..., instructions=..., hooks=..., guardrails=...)` imported from `pydantic_ai.capabilities`[^mindstudio-capability-primitive]
- **Vendor documentation:** tools, lifecycle hooks, instructions, model settings, and models — model selection being the part absent from both other lists[^pydantic-docs-capabilities-overview]

Neither list is chosen here. The partial reconciliation available in this wiki is that guardrails are documented to ship as a [Harness](pydantic-ai-harness.md) capability, which makes a `guardrails=` keyword on `Capability(...)` the less likely reading, while model settings are named by the maintainers and omitted by the explainer. Both enumerations therefore stand as partial, and the explainer's import path, keyword arguments, and `model="openai:gpt-4o"` string are unverified.

## Limits

- The vendor explainer is a marketing post: its publisher sells a competing no-code agent platform, promoted through advertisement blocks between sections and a closing pitch, so its account of Pydantic AI's API carries a commercial interest and the promotional material itself adds nothing about the primitive[^mindstudio-capability-primitive]
- It names no version beyond "2.0", links no repository, changelog, or documentation page, and reports no execution of its own sample.
- It was published 2026-07-11, before the v2.53–v2.59 releases recorded on the [v2 release](pydantic-ai-v2-release.md) page, so any API detail in it may already be stale.

## Relationships

- **Part of** [Pydantic AI v2 release](pydantic-ai-v2-release.md): the capability is v2's central architectural primitive and the reason for several release-level changes.
- **Composes** capabilities shipped by the [Pydantic AI Harness](pydantic-ai-harness.md): core capabilities, Harness capabilities, and third-party capabilities share the same attach-and-compose interface.
- **Uses** hooks as its extension substrate; `CodeMode` and `ToolSearch` are reported to be built on the public hook API. The hook families themselves — the `before_`/`after_`/`wrap_`/`on_*_error` sets per stage, their `AbstractCapability` method names, message-persistence and retry semantics — are compiled in [lifecycle hooks](pydantic-ai-lifecycle-hooks.md), which also carries the `Hooks`-versus-subclass selection table.
- **Is subclassed through** [custom capabilities](pydantic-ai-custom-capabilities.md), which records the configuration-method contract, the `id`/`combine` and run-layer overrides, `for_agent` binding, `for_run` isolation, `CapabilityOrdering`, `@durable_operation` and the spec-publishing route — the authoring half of what this page names.
- **Inserts content through** [capability parts and authority](pydantic-ai-capability-parts-and-authority.md), the typed part kinds and the source-to-authority ceiling that decide how added content is framed.
- **Controls the model through** [capability model control](pydantic-ai-capability-model-control.md): `get_model()`, `resolve_model_id()` and the per-attempt `get_wrapper_model()` are the fifth bundled part, below a run's own model argument and above the constructor.
- **Attaches as** the production features documented in [Conversation state](pydantic-ai-conversation-state.md), [prompt caching](pydantic-ai-prompt-caching.md), [deferred tool approval](pydantic-ai-deferred-approvals.md), [file understanding](pydantic-ai-file-understanding.md), [workspaces](pydantic-ai-workspaces-and-sandboxes.md), [durable execution](pydantic-ai-durable-execution.md), [MCP integration](pydantic-ai-mcp-integration.md), and [Pydantic Evals](pydantic-evals.md).
- **Is extended by** the `get_workspace` hook on a capability that supplies its own environments — including that such a capability cannot defer its loading — as [workspace selection](pydantic-ai-workspace-selection.md) records.
- **Includes** `Thinking`, the thinnest capability in the core set — essentially a model setting with a typed surface — compiled in [thinking and reasoning control](pydantic-ai-thinking.md), with the native controls it delegates to in [reasoning settings per provider](pydantic-ai-reasoning-settings-per-provider.md).
- **Depends on** the two-package split described in [Pydantic AI Harness](pydantic-ai-harness.md): a capability's tier decides its stability guarantee.
- **Reaches** [realtime voice sessions](pydantic-ai-realtime-voice.md), where the same capabilities resolve once at connect time with their instructions re-read before each turn, run-graph features such as output validators are excluded, and a `defer_loading` capability is rejected because the session's tools are fixed at connect; [realtime provider support and settings](pydantic-ai-realtime-provider-support.md) records that capability-contributed model settings do not configure a session at all.
- **Is catalogued in** the [capability catalog](pydantic-ai-capability-catalog.md), which lists the shipped instances tier by tier, and **coordinates through** [capability events](pydantic-ai-capability-events.md), the typed signals a capability publishes at run time.
- **Is serialized by** [agent specs](pydantic-ai-agent-specs.md): only the capabilities whose arguments can be written as YAML or JSON appear in a spec, each lowered through `from_spec()`, so publishing a capability for spec use is a separate step from shipping it in Python.
- **Bundles** [Pydantic AI function tools](pydantic-ai-function-tools.md) as its tools half: a capability's tools are ordinary function tools, so the signature-derived schema and docstring rules are the same contract, attached to the capability instead of the agent.
- **Expresses framework features as** capabilities that rewrite the request rather than add a bundle member: `PrepareTools` for an agent-wide `prepare_tools` hook, `UseThreadExecutor` for a bounded thread pool behind sync tools, and `ToolSearch` for deferred-tool discovery — see [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md), [tool execution, retries and failures](pydantic-ai-tool-execution.md) and [tool search](pydantic-ai-tool-search.md)[^pydantic-docs-tools-advanced].
- **Generalises the routing of** [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md), where one capability name covers a provider-native tool and a local fallback.

[^pydantic-ai-v2]: Douwe Maan, "Pydantic AI v2: capabilities, a leaner core, and the Harness", Pydantic, published 2026-06-23, §"One primitive: the capability" (including the `capabilities=[...]` code sample and the `defer_loading=True` GitHub capability); §"The Harness and a leaner core" for endorsements. Local capture: `raw/pydantic-ai-v2/index.md` (revision 836bd3b1). Evidence class: **Reported** — maintainer announcement, no independent inspection of the library or its hooks was performed in this ingest.
[^alphasignal-v2-news]: AlphaSignal Newsroom, "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work", AlphaSignal, published 2026-06-23, §"One primitive to rule the loop" (the `capabilities=[...]` sample and `defer_loading`) and §"Why on-demand loading matters for your token bill" (`load_capability`, compact catalog, the fall-up pattern). Local capture: `raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/index.md` (revision 836bd3b1). Evidence class: **Reported** — its code sample was read, not executed.
[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Example 1: a typed agent with deps, structured output, hooks and caching" (raw lines 121–184) for the hook lifecycle and ordering rules, the `Hooks` snippet, `result.output` typing and `result.usage` as a property; §"Example 2: bundle behavior as a Capability" (raw lines 185–213) for the declarative `Capability[object]` form and the `defer_loading`/`id` requirement; §"The mental model: an agent loop plus capabilities" (raw lines 98–120) for the core and Harness capability inventories; §"Release timeline since V2.0" for v2.54.0 wrapper semantics and v2.57.0 `Skills` frontmatter support. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — a third-party tour that type-checked and ran some samples against `TestModel`; no package source was inspected here.
[^pydantic-image-gen-2026]: David Sanchez, "Generate images with Pydantic AI", Pydantic, published 2026-09-14, §"Let an agent generate the image" (raw lines 47–86) for the three `ImageGeneration` declaration shapes and the capability-based rather than provider-based fallback. Local capture: `raw/image-generation/index.md`, content digest sha256:2563fee1. Evidence class: **Reported** — vendor announcement; no capability was instantiated.
[^pydantic-image-gen-capability-docs]: Pydantic Docs, "ImageGeneration Capability", https://pydantic.dev/docs/ai/capabilities/image-generation/, §"Fallback Options" (raw lines 131–143) for the direct-model, subagent and own-tool alternatives and their mutual exclusivity. Local capture: `raw/capabilities/image-generation/index.md`, content digest sha256:9a2451a4. Evidence class: **Reported** — vendor documentation naming no framework version; no capability was instantiated.
[^mindstudio-capability-primitive]: Luis Chavez-Mattos, "What Is Pydantic AI 2.0? The Capability Primitive That Changes How You Build Agents", MindStudio, published 2026-07-11. Sections: §"What Is a Capability in Pydantic AI 2.0?" (the four-part bundle) and §"What a Capability Looks Like in Practice" (the `Capability(tools=..., instructions=..., hooks=..., guardrails=...)` sample); §"The Four Components, Explained" (instruction drift, scoped hooks, guardrail levels, "guardrails are just Python functions"); §"Why Composition Changes Everything" (reuse, portable multi-agent contracts, unit testability); §"Common Patterns for Using Capabilities Effectively" ("Layered Capabilities", "Capability Versioning", "Shared Guardrail Libraries"); §"Capabilities and the Broader Shift in Agent Design" (the "capability boundary" framing). Local capture: `raw/what-is-pydantic-ai-2-0-capability-primitive/index.md` (revision 836bd3b1). Evidence class: **Reported**, and **opinion** wherever it argues design — a vendor blog post; no Pydantic AI package source, signature, or documentation was inspected and its sample was not executed. Disclosure: the publisher sells a competing no-code agent platform promoted in the same article.
[^pydantic-docs-capabilities-overview]: Pydantic Docs, "Capabilities" (https://pydantic.dev/docs/ai/capabilities/overview/; 4,642 words as declared, 5,228 by local `wc -w`; no publication date and no Pydantic AI version). §intro for the five kinds of thing a capability can provide (including models — static or adaptive selection and model-ID resolution), the `instructions`/`model_settings`-stay-on-`Agent` boundary, and the extension-point framing; §"Bundling behavior with Capability" for the `refunds` shorthand sample, `@refunds.tool_plain`, the skill analogy, `defer_loading=True` and the wrapping of an Agent Skill, and the list of behaviour that still needs `AbstractCapability`. Local capture: `raw/capabilities/overview/index.md`, content digest sha256:6434ebdb. Evidence class: **Reported** — vendor documentation naming no release version; nothing was constructed or executed.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Agent-wide Dynamic Tools" (raw lines 330–418) for `PrepareTools` attaching an agent-wide `prepare_tools` hook as a capability; §"Thread executor for long-running servers" (804–829) for `UseThreadExecutor(executor)` and `Agent.using_thread_executor`; §"Tool Search" (836–885) for `ToolSearch` as the capability that configures deferred-tool discovery. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
