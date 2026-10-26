---
type: Concept
title: Claude Agent SDK versus Pydantic AI
description: Why the Claude Agent SDK installs Claude Code's coding-agent harness — a bundled subprocess, an unpublished system prompt, an upgrade surface no code review sees — and how Pydantic AI keeps the loop, the instructions and the workspace in your own process.
tags: [ml, pydantic-ai, agents, llm-frameworks, ecosystem]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T13:10:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-vs-claude-sdk-2026
    resource: ../raw/pydantic-ai-vs-claude-agent-sdk/index.md
    scope: ../raw/pydantic-ai-vs-claude-agent-sdk/
    kind: article
    revision: sha256:e13b086e39460e61065006caca8d0b4b2502621205a283c70cd66ea1da31974b
    title: "Pydantic AI vs Claude Agent SDK: Who owns the agent?"
---

The Claude Agent SDK hands your application a coding agent rather than a library: `pip install claude-agent-sdk` brings a Python client **and** a bundled Claude Code executable, and every session starts Claude Code as a subprocess whose shell, file tools, skills, plugins, permissions, settings, session files and agent loop come with it[^pydantic-vs-claude-sdk-2026] Pydantic AI starts from the application instead — your model string, instructions, tools, output types and capabilities — so the loop runs in your process and a coding agent is something you attach when you need one[^pydantic-vs-claude-sdk-2026] The vendor's framing is that an agent's prompts, tools, permissions, control loop and failure behaviour are part of the contract you depend on even though none of them appear in a type signature, and that adopting another product's choices for them is a decision worth making deliberately[^pydantic-vs-claude-sdk-2026]

## Behaviour is part of the contract

The argument rests on a thought experiment rather than a measurement. Dependencies get pinned, upgrades get reviewed, and breaking changes are expected to be visible — but if Pydantic AI's retry prompt were changed to something absurd, the imports would still work, the types would still check, and no public API would break, while deployed agents behaved differently[^pydantic-vs-claude-sdk-2026] Prompts, tools, permissions, control loops and failure behaviour therefore decide what the model sees, what it can do and what happens next, which makes them contract surface rather than incidental implementation detail[^pydantic-vs-claude-sdk-2026] When those decisions live inside another product, that product owns a meaningful part of your application's behaviour.

## What the SDK installs, and which switches remain

| Brought in by the SDK | Why it makes sense for a coding agent |
| --- | --- |
| A bundled Claude Code executable started per session as a subprocess | It needs a process to inspect repositories and edit files |
| Shell and file tools | Editing and running code is the job |
| Skills, plugins and project settings | Reusable procedures and repository conventions |
| Permissions and session files | Tool gating and resumable sessions |
| Claude Code's own agent loop | Failure recovery and instruction-following for code work |

Most of that has a switch: tools can be denied, hooks added, the system prompt replaced, your own MCP tools supplied, and `setting_sources=[]` together with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` passed so a session stops loading the project's `.claude/` settings and memory[^pydantic-vs-claude-sdk-2026] The author's objection is not that the switches are missing but that using them means configuring Claude Code rather than building the runtime the application needs[^pydantic-vs-claude-sdk-2026] Anthropic's alternative for teams that do not want to run the subprocess is Managed Agents, which hosts the agent loop while tools run in Anthropic's cloud sandbox or one you host — the loop stays Anthropic's[^pydantic-vs-claude-sdk-2026]

## Where the upgrade risk lands

A locked deployment does not change overnight, because the SDK pins a Claude Code version. Upgrading the SDK can still replace the bundled Claude Code binary[^pydantic-vs-claude-sdk-2026] Anthropic states that Claude Code upgrades usually change the system prompt or the tool definitions, and the system prompt is not published as part of the SDK's contract[^pydantic-vs-claude-sdk-2026] The concrete cost named is team-level: your prompt, your model and your code can stay identical while the deployed agent changes, and the reason does not appear in your code review, so the team has to learn Claude Code's assumptions, constrain capabilities the application does not need, and investigate behaviour controlled by a runtime built for a different job[^pydantic-vs-claude-sdk-2026] The article is explicit that being opinionated is correct for a coding agent; the problem is adopting those opinions when shipping a coding agent was not the goal.

## What Pydantic AI keeps in your process

Pydantic AI begins with one model call, from any supported provider, plus the instructions, tools, dependencies, output types and capabilities you declare[^pydantic-vs-claude-sdk-2026] The source's example is an output type doing the constraining:

```python
from pydantic import BaseModel
from pydantic_ai import Agent

class SupportReply(BaseModel):
    answer: str
    needs_human: bool

agent = Agent("anthropic:claude-sonnet-4-6", output_type=SupportReply)
```

The growth path is additive rather than a replacement: typed tools, then dependency injection, structured outputs, human approval, [durable execution](pydantic-ai-durable-execution.md), multiple agents, or an explicit [graph](pydantic-ai-graph-builder.md)[^pydantic-vs-claude-sdk-2026] Filesystem access, a shell, planning, memory and subagents arrive one [capability](pydantic-ai-capability-primitive.md) at a time from the [Harness](pydantic-ai-harness.md)[^pydantic-vs-claude-sdk-2026]

The Harness also ships whole agents to start from: `Coder` is a complete coding agent — file tools, a shell, repository instructions, delegation and context management — and `Researcher` answers questions from the web with cited sources. Both are built from the same capabilities, so they come apart the way they went together: start from one and remove what you do not need, or skip both[^pydantic-vs-claude-sdk-2026] Attaching `Coder` is a single capability entry:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import Coder

agent = Agent("anthropic:claude-sonnet-4-6", capabilities=[LocalWorkspace("."), Coder()])
```

The same agent can then run in CI as a GitHub Agentic Workflow triggered by issues, pull requests or a schedule — your agent, your instructions, your tools and your model, doing the job a vendor's GitHub Action does for the vendor's own agent[^pydantic-vs-claude-sdk-2026]

## Where the commands run

`LocalWorkspace(".")` runs the agent's commands on your machine, as you — fine for your own repository, not for code a user handed you. Swapping the workspace moves the work without touching the agent[^pydantic-vs-claude-sdk-2026]:

```python
from pydantic_ai_harness.modal_sandbox import ModalSandbox

agent = Agent("anthropic:claude-sonnet-4-6", capabilities=[ModalSandbox(), Coder()])
```

`Coder`'s file and shell tools then run in a Modal sandbox, and `E2BSandbox()` or `SpritesSandbox()` drop into the same slot; tools you write yourself reach the environment through `ctx.workspace`, so a tool tested on a laptop runs in the sandbox unchanged[^pydantic-vs-claude-sdk-2026] The architectural difference the author draws is placement: with Pydantic AI the agent stays in your application and only its commands and file edits move, whereas Anthropic's advice for the Claude Agent SDK is to run the whole SDK inside a sandboxed container, which puts the agent in there with them[^pydantic-vs-claude-sdk-2026] A sandbox keeps running after the run ends and must be deleted when you are done[^pydantic-vs-claude-sdk-2026] See [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md).

## Seeing the run, and gating an upgrade

Owning the agent only helps if its behaviour is visible: `logfire.configure()` plus `logfire.instrument_pydantic_ai()` records every model request, tool call and retry, including the exact prompt the model received[^pydantic-vs-claude-sdk-2026] The same tooling answers the upgrade question from earlier — keep a set of cases in [Pydantic Evals](pydantic-evals.md), run it before and after bumping a dependency or changing a prompt, and a behaviour change shows up in a report read during review[^pydantic-vs-claude-sdk-2026] That is a claim about a workflow, not a demonstrated catch of a Claude Code upgrade.

## The comparison, as the source states it

|  | Claude Agent SDK | Pydantic AI |
| --- | --- | --- |
| What you install | A Python client and a bundled Claude Code executable | A Python library |
| Agent loop | Claude Code's, in a subprocess | Pydantic AI's, in your process |
| System prompt | Yours or Claude Code's, plus reminders Claude Code adds | The instructions you write |
| Default tools | Shell, file tools, skills and plugins | None until you add them |
| Where tools run | Wherever you run the SDK process | Your machine, or a Modal, E2B or Sprites sandbox |
| Models | Claude | Any supported provider |
| Coding agent | Claude Code | `Coder` from the Harness |
| Fits best | A coding product built on Claude Code's behaviour | An application that defines its own agent |

The stated conclusion is conditional rather than universal: for a product that wants Claude Code's shell, filesystem, project instructions, skills, permissions and coding loop, the SDK is the direct choice; for anything else, a coding-agent harness packaged as an SDK is the wrong starting point[^pydantic-vs-claude-sdk-2026]

## Limits

- This is a Pydantic engineer's argument for his employer's framework, published on the employer's site with no independence, no benchmark and no measurement of behaviour drift[^pydantic-vs-claude-sdk-2026] It is the wiki's only source on the Claude Agent SDK, so every Claude Code claim here is **Reported**.
- The vendor grounding is specific but one-sided: `claude-agent-sdk==0.2.152` with bundled Claude Code `2.1.259` was reviewed on 2026-09-04, and the Pydantic AI examples were checked against commit `06ba88fd` on 2026-10-01 — **no Pydantic AI release version is named**, which is why this page is `draft` under the [`pydantic-ai`](../SCOPE.md) domain rule[^pydantic-vs-claude-sdk-2026]
- Every Claude Code documentation link, the SDK repository's release workflow, the `Coder`/`Researcher`/workspace documentation and the GitHub Agentic Workflow page were read as links, not followed; `Researcher` appears in no other capture here and neither agent's package, prompt or tool list was inspected.
- "The system prompt is not published as part of the SDK's contract" is the article's reading of Anthropic's settings docs, not a statement Anthropic makes in those words.
- The models row says Claude for the SDK because that is what the bundled harness calls; the article offers no figure for cost, latency, or output quality against the same application built in Pydantic AI, and no upgrade of either stack was performed.
- Nothing was installed, no session started, no sandbox created or billed, no trace opened and no eval run, so no claim here is **Reproduced**.
- The `Coder` snippet puts `LocalWorkspace` in core (`pydantic_ai.capabilities`) and `ModalSandbox` in the Harness (`pydantic_ai_harness.modal_sandbox`), which matches the core-versus-Harness placement recorded in [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md); the split is recorded from two vendor sources, not verified against packages.

## Relationships

- **Sharpens** the look-elsewhere row in [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md), which lists "the model vendor's own agent loop" as a reason to choose the OpenAI Agents SDK or the Claude Agent SDK.
- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md) to add filesystem, shell, planning, memory and subagents one at a time, and the [Harness](pydantic-ai-harness.md) for `Coder` and `Researcher`.
- **Depends on** [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) to run model-written commands off the host while the agent stays in process.
- **Gates upgrades with** [Pydantic Evals](pydantic-evals.md), and reads runs through [Pydantic AI observability](pydantic-ai-observability.md).
- **Contrasts with** a hosted loop: Managed Agents moves the loop to Anthropic rather than into your process[^pydantic-vs-claude-sdk-2026]

[^pydantic-vs-claude-sdk-2026]: Aditya Vardhan, "Pydantic AI vs Claude Agent SDK: Who owns the agent?", Pydantic, published 2026-10-05, 1,453 words as declared. §"The contract is bigger than the API" (raw lines 29–42) for the behaviour-surface argument and the retry-prompt thought experiment; §"A coding-agent harness dressed up as an SDK" (lines 43–56) for the bundled executable, the subprocess session, the switch list including `setting_sources=[]` and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, and Managed Agents; §"The impact on your application" (lines 57–68) for the pinned version, the replaceable binary, and the "system prompt is not published" claim; §"Pydantic AI grows with your application" (lines 69–101) for the growth path, `Coder`, `Researcher`, the two code samples and GitHub Agentic Workflows; §"Give it somewhere to work" (lines 102–119) for `LocalWorkspace`, `ModalSandbox`, `E2BSandbox`, `SpritesSandbox`, `ctx.workspace`, the container-sandboxing contrast and sandbox cleanup; §"See what your agent actually did" (lines 120–125) for `logfire.configure()`/`instrument_pydantic_ai()` and the evals-before-upgrade practice; §"Choose the thing you intend to ship" (lines 126–146) for the eight-row table and the closing recommendation; the closing reviewer note (line 147) for the reviewed versions. The attached `assets/claude-code-python-sdk.jpg` was not inspected — it is a decorative meme, not evidence. Local capture: `raw/pydantic-ai-vs-claude-agent-sdk/index.md`, content digest sha256:e13b086e. Evidence class: **Reported** — a vendor comparison of its own product against a competitor it names by version; no SDK was installed, no Claude Code session run, no sandbox created, and no benchmark performed.
