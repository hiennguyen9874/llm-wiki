---
type: Concept
title: Pydantic AI v2 release
description: The Pydantic AI v2 release — capability-centric architecture, a leaner core with opt-in providers, manual migration checks, a shortened major-version support window, and the point releases and security advisories through v2.59.0.
tags: [ml, pydantic-ai, agents, release-notes]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:10:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-ai-v2
    resource: ../raw/pydantic-ai-v2/index.md
    scope: ../raw/pydantic-ai-v2/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2: capabilities, a leaner core, and the Harness"
  - id: vstorm-v2-blog
    resource: ../raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md
    scope: ../raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2 and the road to production-grade agentic AI"
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
---

**Pydantic AI v2** ships a capability-centric architecture (see the [capability primitive](pydantic-ai-capability-primitive.md)), a leaner core with opt-in providers, and a shortened window between major versions. The maintainers frame the agent inner loop — call the model, run a tool, feed the result back — as settled, and place v2's leverage in the surrounding layer: instructions and tools, hooks that rewrite what the model sees mid-run, context management, steering, and just-in-time tool loading[^pydantic-ai-v2]

## Release identity

- **Announced:** 2026-06-23 by Douwe Maan on pydantic.dev; the first beta (2.0.0b1, forked from v1.100.0) is dated 2026-05-20, and stable v2.0.0 followed with no breaking changes beyond the betas[^dd-v2-tour-2026]
- **Current at the last source update:** v2.59.0, released 2026-10-20[^dd-v2-tour-2026]
- **Install:** `uv add pydantic-ai` installs v2.
- **Predecessor:** v1 shipped in September 2025 with more than a hundred releases and, per the announcement, no breaking changes to user code; v1.107.7 shipped a security fix on 2026-09-29[^dd-v2-tour-2026]
- **Stability:** press coverage published the same day reports v2 as stable after seven betas[^alphasignal-v2-news]
- **Coverage, not corroboration:** the AlphaSignal column restates the same pydantic.dev announcement, so it adds detail and framing rather than independent verification[^alphasignal-v2-news]

## Migration path

1. Upgrade to the latest v1 and clear every deprecation warning — the article suggests pointing a coding agent at the warnings. It claims this covers most of the migration and that almost nothing else should break.
2. Check the behavior changes a warning could not catch:

| Change | Effect |
| --- | --- |
| `openai:` model names | Now use the Responses API; use `openai-chat:` to stay on Chat Completions |
| `WebSearch` / `WebFetch` | Native by default |
| `MCP(url=...)` | Runs locally by default |
| Instrumentation | Defaults to version 5, with aggregated token-usage attributes |
| Function tools + output tool | Function tools requested alongside a successful output tool now run instead of being skipped (`end_strategy='graceful'`) |
| Generic defaults | `Agent(...)` infers `Agent[object, str]` instead of `Agent[None, str]`; `RunContext[None]` no longer matches a deps-less agent, so annotate `RunContext[object]` |
| `ModelProfile` | Now a `TypedDict` |

Message history serialized under V1 still deserializes in V2, so a stored conversation survives the upgrade[^dd-v2-tour-2026]

The full breaking-change list is the project's Upgrade Guide; the article points to GitHub issues and Slack for breakage reports[^pydantic-ai-v2]

## Additions not driven by deprecations

- **Agent spec files** — an agent can be defined entirely in YAML/JSON with no code, which follows from capabilities being serializable[^alphasignal-v2-news]
- **Pricing boundary** — the framework is open source and free; observability through Pydantic Logfire has its own pricing tier[^alphasignal-v2-news]

## The production gap v2 targets

A partner account of the release names the same thesis from the deployment side: what breaks is not the loop but the layer around it — memory that does not survive between sessions, context that overflows, guardrails that must stop a bad tool call before it reaches the data, tool discovery that floods the prompt with hundreds of definitions, and steering that lets an operator correct a run mid-flight[^vstorm-v2-blog] Its before/after reading of the release:

| Concern | Hand-wired layer (pre-v2) | v2 capabilities |
| --- | --- | --- |
| Memory and context | Custom code per project, rebuilt each time | Context management composes in as a capability |
| Tool discovery | Hundreds of definitions loaded upfront | Tools load on demand |
| Guardrails and observability | Bolted on late, often inconsistently | Capabilities and hooks, consistent across the loop |
| Path to production | Re-wiring glue before touching agent logic | Compose proven building blocks, focus on the problem |
| Ownership | Framework lock-in risk | Open source, model-agnostic, fully owned |

The same account illustrates model-agnostic assembly: an agent built with `capabilities=[CodeMode()]` plus its tools runs unchanged when the model string changes from `anthropic:claude-sonnet-4-6` to `openai:gpt-5.2`[^vstorm-v2-blog] This is a vendor's illustration, not a measured comparison, and the production-gap list is its framing rather than a surveyed finding.

## Leaner core and opt-in providers

`uv add pydantic-ai` installs `pydantic-ai-slim[openai,anthropic,google,cli,mcp,evals,web,retries,logfire]`, so OpenAI, Anthropic and Google ship by default while Bedrock, Groq, Mistral, Cohere, xAI, Hugging Face, Temporal, AG-UI, UI and spec extras must be added explicitly — only what is used gets installed[^dd-v2-tour-2026] The announcement itself named only a few examples ("bedrock, groq, mistral, and friends"), so the exact default set was unknown until this second source[^pydantic-ai-v2] Capabilities beyond the core live in the [Pydantic AI Harness](pydantic-ai-harness.md)

## Version policy change

The no-breaking-changes window between major versions moves from **six months to three**. The stated reason is not reduced commitment to stability but that the field moves fast enough that promising further out means committing to decisions that fit today and not the world three months from now. Everything else stands: no breaking changes within a major version, and deprecations always land before removals[^pydantic-ai-v2]

The published policy confirms the shape from the consumer side: minor releases avoid intentional breaking changes, deprecated APIs stay until the next major, and the next major will not ship sooner than three months after v2.0. V1 keeps receiving security fixes for at least six months after v2.0's stable release, which is why the upgrade is not urgent[^dd-v2-tour-2026] The Python floor is a separate constraint: since v2.55.0 every package requires Python 3.11 or newer — on 3.10, installs resolve to 2.54.0 or earlier — and v2.56.0 added Python 3.15 support[^dd-v2-tour-2026]

## Point releases since v2.0

The release cadence is fast enough that the version number is part of the operational picture. From the timeline in the tour[^dd-v2-tour-2026]:

| Date (2026) | Version | Headline |
| --- | --- | --- |
| Jun 23 | v2.0.0 | Stable V2; no new breaking changes since the betas |
| Sep 24 | v2.50.0 | `RunContext.in_durable_context` |
| Sep 29 | v2.52.0 | Workspaces and the first sandboxes, a higher Anthropic `max_tokens` default, Claude Sonnet 5.5 support (v1.107.7 also shipped a security fix that day) |
| Oct 1 | v2.53.0 | Harness `AbsurdDurability`, `repair_messages`, Harness `ToolCallJudge`, and the fix for GHSA-6fqq-452j-qhrp |
| Oct 2 | v2.54.0 | `wrap_*` hooks enclose full stage lifecycles; a second durable engine is refused |
| Oct 9 | v2.55.0 | `Conversation`, unified `Caching`, Python 3.11 minimum, faster import, Claude Haiku 5.5 support |
| Oct 13 | v2.56.0 | Harness pgtask durability, Render Workflows, `SmolSandbox`, Python 3.15 support |
| Oct 15 | v2.57.0 | Harness `ApprovalReviewer`, MCP Apps relay, `MetaProvider`, pricing at the provider's reported service tier |
| Oct 19 | v2.58.0 | Run `timeout=` and `RunContext.deadline`, `request_timeout` and `max_retries`, `DelegationTasks.steer`, the `openai-chatgpt` provider, two medium advisories |
| Oct 20 | v2.59.0 | Provider-neutral model error categories, `non_retryable_model_errors`, `on_change='append'` instructions, `DaytonaSandbox`, `ElevenLabsRealtimeModel` |

The two October releases are covered feature by feature in [Pydantic AI run controls](pydantic-ai-run-controls.md) (error categories, time budgets, append-only instructions), [durable execution](pydantic-ai-durable-execution.md) (retry classification), and [workspaces](pydantic-ai-workspaces-and-sandboxes.md) (Daytona).

## Security advisories

Three advisories are part of the upgrade calculus, and the source warns that the list is not exhaustive[^dd-v2-tour-2026]:

| Advisory | Fixed in | Rated | Affects |
| --- | --- | --- | --- |
| GHSA-6fqq-452j-qhrp | v2.53.0 | High | `ConcurrencyLimitedModel` / `limit_model_concurrency` with streaming: a streamed request kept its concurrency slot. V1 is not affected; sharing a limiter with its agent now raises `UserError` |
| GHSA-xv4x-g8mx-ch56 | v2.58.0 | Medium | Provider-native MCP configuration could expose server URLs and authorization tokens in telemetry |
| GHSA-5pfm-2g3g-gh85 | v2.58.0 | Medium | UI adapters used with server-side `message_history` |
| Unnamed | v2.59.0 | High | Not described beyond the severity and the instruction to read the release notes and upgrade from 2.58 too |

That last row is the operational gap: a high-severity fix is recorded only as a cross-reference, so anyone on 2.58.0 is told to upgrade without being told what is at risk[^dd-v2-tour-2026]

## Limits

- Version, packaging, and migration claims now come from two sources — the vendor announcement and a third-party hands-on tour — but neither was cross-checked against the changelog, PyPI, release tags, or the library itself[^dd-v2-tour-2026]
- The point-release table and the advisory summaries are the tour's restatement of GitHub release notes; the advisory pages themselves were not read, and one v2.59.0 advisory is unnamed[^dd-v2-tour-2026]
- The "no breaking changes in v1" claim is the maintainers' characterization.
- The AlphaSignal capture is a newsroom summary of the same announcement, so agreement between it and the vendor post does not raise confidence; the third source is independent in vantage but is still read, not executed, here.

## Relationships

- **Introduces** the [capability primitive](pydantic-ai-capability-primitive.md) as its central abstraction.
- **Splits** capability delivery between core and the [Pydantic AI Harness](pydantic-ai-harness.md).
- **Supersedes** Pydantic AI v1; the upgrade to latest v1 plus deprecation warnings is the migration path.
- **Part of** the framework comparison recorded in [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md): the release is where the type-safety posture becomes a composable capability system.
- **Corroborated by** the partner account in [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md), which describes the same core-to-Harness split and the endorsed third-party ecosystem from a vendor's vantage point.
- **Continues into** [Pydantic AI run controls](pydantic-ai-run-controls.md): v2.58 and v2.59 move failure classification and time budgets into the framework.
- **Documented feature by feature** in [Conversation state](pydantic-ai-conversation-state.md), [prompt caching](pydantic-ai-prompt-caching.md), [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md), [durable execution](pydantic-ai-durable-execution.md), [graph builder](pydantic-ai-graph-builder.md), [Pydantic Evals](pydantic-evals.md), [MCP integration](pydantic-ai-mcp-integration.md), and [observability](pydantic-ai-observability.md).

[^pydantic-ai-v2]: Douwe Maan, "Pydantic AI v2: capabilities, a leaner core, and the Harness", Pydantic, published 2026-06-23. Sections: opening thesis and the release note block (install, migration, behavior-change list); §"The Harness and a leaner core" (provider defaults and opt-ins); §"A word on the version policy" (six-to-three-month window); §"Try it" (install command). Local capture: `raw/pydantic-ai-v2/index.md` (revision 836bd3b1). Evidence class: **Reported** — a maintainer announcement; no Pydantic AI installation, release notes page, or code was inspected or executed in this ingest.
[^vstorm-v2-blog]: Nicholas Berryman, "Pydantic AI v2 and the road to production-grade agentic AI", Vstorm, published 2026-07-03, §"Why this matters for production-grade agentic AI" (production-gap list) and §"What it means for teams building agentic AI implementation today" (before/after table and the model-swap code sample). Local capture: `raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md` (revision 836bd3b1). Evidence class: **Reported** — partner marketing; no code was run to confirm the model-swap claim.
[^alphasignal-v2-news]: AlphaSignal Newsroom, "Pydantic AI v2 Ships a Single Primitive That Rebuilds How Agents Work", AlphaSignal, published 2026-06-23, §"One primitive to rule the loop" (stable after seven betas), §"What's actually new vs. what just got formalized" (agent spec files), §"Getting started and migrating from v1" (install, Logfire pricing, Harness 0.x policy). Local capture: `raw/pydantic-ai-v2-ships-a-single-primitive-that-rebuilds-how-agents-work/index.md` (revision 836bd3b1). Evidence class: **Reported** — a newsroom summary of the pydantic.dev announcement; no Pydantic AI installation, changelog, package, or third-party repository was inspected. Assets (`assets/favicons.png`, `assets/favicons-2.png`, `assets/twitter.3.ico`) are decorative site furniture and were excluded.
[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"What changed in V2, in one table" (raw lines 77–97) for the beta and stable dates, the default install extras, the generic-default and `ModelProfile` changes, and V1 history deserialization; the V1-upgrade paragraphs after the "What changed in V2, in one table" section and the FAQ answer "Do I have to upgrade from V1 now?" for the V1 security window, minor-release policy, and Python floor; §"Release timeline since V2.0" (raw lines 614–628) for the point-release table, v1.107.7, and the advisory summary. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — a third-party hands-on tour that type-checked and ran some examples; no Pydantic AI package, changelog page, PyPI listing, release tag, or advisory page was inspected in this ingest.
