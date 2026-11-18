---
type: Concept
title: Pydantic AI Harness researcher
description: The Harness Researcher combined capability — default research instructions over core web search, page fetching, a default research delegate and tool-output limits, the workspace its spills require, and the three levers that change it.
tags: [pydantic-ai, agents, harness, research]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:58:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-researcher-docs
    resource: ../raw/harness/researcher/index.md
    scope: ../raw/harness/researcher/
    kind: documentation
    revision: sha256:cc32139fcfcd38790d1526ed17894465cd7f261fd8ba553e34ba09599a16414c
    title: "Researcher"
---

`Researcher` is a [Harness](pydantic-ai-harness.md) **combined capability**: one import that gives an agent a source-backed web-research stack, built from parts you can also assemble yourself[^pydantic-researcher-docs] Its shape is small — four capabilities and a short instruction block — so it is better read as a reference composition of the [native-or-local](pydantic-ai-native-or-local-capabilities.md) pattern, [subagents](pydantic-ai-subagents.md) and tool-output bounding than as a framework of its own. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## What it composes

`Researcher()` is the ordered combination of[^pydantic-researcher-docs]:

| Part | Configured as | Job |
| --- | --- | --- |
| Default instructions | `DEFAULT_RESEARCHER_INSTRUCTIONS` | Search broadly, read the sources behind each claim, prefer primary sources, cite with a direct link, and separate sourced fact from inference |
| Core web search | `WebSearch(local=True)` | Provider-native search where the model supports it, DuckDuckGo fallback where it does not |
| Core web fetch | `WebFetch(local=True)` | Reads the pages behind the results, native or local, so claims can be checked against their source |
| Subagents | `SubAgents(agents=[...], agent_folders=None)` | A focused `researcher` delegate for a sub-question, with its own search, fetch and output limits |
| Tool output limits | `ToolOutputLimits()` | Bounds any single tool result and spills the oversized ones to a file the model can read |

The delegate's description — "Research a focused sub-question on the web and report back with findings and source links" — and its instruction text are the ones the source documents in its blown-out equivalent, which is the whole composition as ordinary Python rather than a constructor call[^pydantic-researcher-docs] That equivalent is the practical answer to "I want this but with one part changed": it is the same agent with the pieces visible.

## The workspace requirement

`ToolOutputLimits` spills oversized results into the run's **workspace**, under `.pydantic-ai-harness/tool-output/`, which is git-ignored, so a run without a workspace fails at its start[^pydantic-researcher-docs] Attach `LocalWorkspace('.')` to keep spills in the current directory or a sandbox capability to keep them in the sandbox; `LocalWorkspace` is not a sandbox, so a command running in it can reach anything the process user can.

Two ways out of the requirement, and one trap[^pydantic-researcher-docs]:

- `Researcher(store=LocalFileOverflowStore())` keeps spills on the machine running the agent, even when the agent itself works in a sandbox;
- pointing memory-like paths at a local backend is the same pattern [Harness memory](pydantic-ai-harness-memory.md) documents for `FileMemoryStore`;
- a **custom** delegate does not inherit the `Researcher`'s store, so it needs its own configured, while the default delegate does inherit it.

## Three levers

The constructor takes three parameters, each a whole-package decision[^pydantic-researcher-docs]:

| Parameter | Default | Effect |
| --- | --- | --- |
| `instructions` | `DEFAULT_RESEARCHER_INSTRUCTIONS` | Replace the text; `None` keeps the abilities and drops the instructions entirely |
| `subagents` | `None` (a focused web `researcher`) | Your own `SubAgent` entries; `[]` removes delegation |
| `store` | `None` (the run's workspace) | An `OverflowStore` or `WorkspaceOverflowStore` for oversized results, shared with the default delegate |

Beyond the constructor, the source names three extensions rather than options[^pydantic-researcher-docs]: a typed [`output_type`](pydantic-ai-structured-output.md) model of findings so the agent returns structured data with a source link per finding instead of prose; Exa search as a replacement backend; and [dynamic workflows](pydantic-ai-dynamic-workflow.md) beside it, so the model can fan out typed researcher sub-agents in parallel and combine their structured results — the composition that turns this stack into a multi-query research run.

## Interfaces and durability

The same agent works through every Pydantic AI interface the source names — `to_cli_sync()` for terminal chat and `to_web()` for a browser UI — and the package exports a model-less `researcher_agent` for the `clai` CLI's `module:variable` targets, so `uvx --with 'pydantic-ai-harness[researcher]' clai -a pydantic_ai_harness.researcher:researcher_agent -m …` runs this stack without a source file[^pydantic-researcher-docs]

Under durable execution it is composed the same way as anything else: `Researcher()` next to `TemporalDurability()`, `DBOSDurability()` or `PrefectDurability()` when the agent is constructed, with the workspace still attached for its spills[^pydantic-researcher-docs] The source does not say how a spill file behaves across a replay, which is the limit worth remembering: see [durable execution](pydantic-ai-durable-execution.md) for what replay does and does not re-run.

## Coverage and limits

The package is the single `index.md` capture: no attachments, includes, imports or supporting files, and the diagram is described in its text form[^pydantic-researcher-docs] Every external link — the capabilities overview, web search, web fetch, subagents, tool output limits, workspace, Exa Search, dynamic workflow and the CLI and web interfaces — was read as a link and not followed. The page states no version, date, author or licence, so the capability is `draft` under the `pydantic-ai` domain rule and its examples pin `openai:gpt-6.1-sol`, an alias no release pin corroborates.

Nothing was installed, no agent run, no search issued, no page fetched, no delegate spawned and no result spilled, so every claim is **Reported** and none **Observed** or **Reproduced**. The source also does not state what the default instructions cost in tokens, what the default delegate's model is (it inherits the parent agent's), or how `ToolOutputLimits` behaves when the overflow write fails — that last one belongs to the capability's own page.

## Relationships

- **Depends on** the [workspace](pydantic-ai-workspaces-and-sandboxes.md) for its oversized tool results, or on a non-workspace overflow store.
- **Uses** core web search and web fetch through [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md), and delegation through [Harness subagents](pydantic-ai-subagents.md).
- **Extended by** [Harness dynamic workflows](pydantic-ai-dynamic-workflow.md) for parallel sub-question fan-out.
- **Compared with** using the same parts by hand in [Coder](pydantic-ai-harness-coder.md): `Coder` composes files and shell where `Researcher` composes search and fetch.

[^pydantic-researcher-docs]: Pydantic Docs, "Researcher", <https://pydantic.dev/docs/ai/harness/researcher/>; local capture `raw/harness/researcher/index.md`, content digest sha256:cc32139f, 870 words as declared (913 by `wc -w`), 164 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the combined-capability framing; 13–36 for the flow diagram (instructions, `WebSearch`/`WebFetch`, `delegate_task` to the `researcher` sub-agent, `ToolOutputLimits` reads against the run workspace); 38–51 for the install extra and the usage example; 53–72 for the `researcher_agent` CLI route and the durability composition; 74–86 for the ordered parts, `subagents=[]`, the `.pydantic-ai-harness/tool-output/` spill path, the workspace or `store=LocalFileOverflowStore()` requirement and the custom-delegate store rule; 88–96 for `instructions`/`None` and the three extensions; 98–134 for the blown-out equivalent, including the default instruction text and the delegate's name and description; 136–163 for the constructor parameters and `researcher_agent`. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
