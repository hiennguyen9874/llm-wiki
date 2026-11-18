---
type: Concept
title: Pydantic AI Harness documentation lookup
description: The Harness PydanticAIDocs capability — one read_pyai_docs(topic) tool that resolves a docs page from a workspace checkout first and GitHub at the installed release tag second, replaces model aliases, caches per run, and fails loudly when neither source has the page.
tags: [pydantic-ai, agents, harness, context]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:59:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-ai-docs-docs
    resource: ../raw/harness/pydantic-ai-docs/index.md
    scope: ../raw/harness/pydantic-ai-docs/
    kind: documentation
    revision: sha256:4016fb73b2ad2ac93a38a0c078b619c3788a79b236d6336138fff82bbf537f0c
    title: "Pydantic AI Docs"
---

`PydanticAIDocs` is the [Harness](pydantic-ai-harness.md) capability that gives an agent **one tool, `read_pyai_docs(topic)`, and no preloaded documentation**[^pydantic-ai-docs-docs] It exists for the agent that writes Pydantic AI code: preloading the docs spends context the agent rarely needs in full and pins a snapshot that drifts from the installed version, so the page is fetched at the moment it is needed instead. The same on-demand shape, with a different corpus and loader, is [on-demand capabilities](pydantic-ai-on-demand-capabilities.md) and [coding-agent skills](pydantic-ai-coding-agent-skills.md). The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## The six topics

The tool's whole vocabulary is a fixed topic list — `capabilities`, `hooks`, `tools`, `tools-advanced`, `toolsets`, `agent` — and a call returns one page in full[^pydantic-ai-docs-docs] That list is the retrieval surface: an agent asking about a topic outside it gets the resolution failure described below rather than a search.

A static, cache-stable instruction tells the model the tool exists and that it should read the relevant topic **before authoring or modifying** a capability, hook, tool or toolset rather than relying on memory[^pydantic-ai-docs-docs] Being cache-stable is the design constraint, not a detail: instructions that changed per run would rewrite the cached prefix every turn, the same problem [Harness planning](pydantic-ai-harness-planning.md) solves by keeping its plan out of the system prompt.

## Resolution order

Each call resolves in three steps[^pydantic-ai-docs-docs]:

| Step | Source | Detail |
| --- | --- | --- |
| 1 | Workspace checkout | `local_docs_path`, or the `PYDANTIC_AI_HARNESS_DOCS_PATH` environment variable when that is unset; the page must exist at `{path}/{topic}.md`, or `{path}/capabilities/overview.md` for `capabilities` |
| 2 | GitHub | The same path under `https://raw.githubusercontent.com/pydantic/pydantic-ai/{remote_ref}/docs/`, where `remote_ref` defaults to the installed `pydantic_ai` release tag such as `v2.69.0`, or `main` for a dev build; needs network access |
| 3 | Neither | A descriptive error naming the local path tried and the URL |

Defaults to the installed release tag are what keep the answer honest: the page describes the APIs the agent actually has, and `remote_ref='main'` is the explicit opt-in to the latest docs instead[^pydantic-ai-docs-docs]

Because the checkout is read **through the run's workspace**, configuring `local_docs_path` without a workspace fails the run at its start; with no local path, no workspace is needed[^pydantic-ai-docs-docs] The capability never runs git, so keeping the checkout current is the application's job, and `~` is not expanded — the path must be absolute or relative to the workspace working directory. `local_docs_path` wins over the environment variable.

## Model aliases

Docs pages name models through aliases that the docs site substitutes at render time, so a returned page would otherwise carry placeholders[^pydantic-ai-docs-docs] Before returning a page that uses one, the tool reads `model_aliases/aliases.json` in the same workspace-then-GitHub order and replaces each alias with the model it names; an alias the file does not define stays as written, and so does every alias when neither source provides the file. A page with no aliases reads nothing extra, so a checkout predating the alias file keeps working.

## Configuration and identity

| Option | Default | Meaning |
| --- | --- | --- |
| `local_docs_path` | `None` | Checkout inside the run workspace, falling back to `PYDANTIC_AI_HARNESS_DOCS_PATH`, then to the remote |
| `cache` | `True` | Memoizes each returned page for **one agent run**, so repeated reads in a run do not repeat I/O |
| `remote_ref` | `None` | Git ref for the remote fetch; `None` means the installed release tag or `main` |
| `id` | `'pydantic_ai_docs'` | Keys the capability's instructions, makes them addressable, and lets `defer_loading=True` work without one |

Caching is isolated per run through `for_run`, so content read from one workspace is never reused in another; `cache=False` re-reads or re-fetches on every call[^pydantic-ai-docs-docs]

The `id` carries a merge rule worth knowing: because an agent has only one `read_pyai_docs` tool, two `PydanticAIDocs` sharing the default `id` are one docs source stated twice — they become one when they agree, and the agent raises a `UserError` at construction when they differ — while keeping two requires distinct `id`s wrapped in `PrefixTools`[^pydantic-ai-docs-docs] Earlier releases declared no default `id` and failed on the duplicate tool name at run start instead.

## Agent specs and the rename

`PydanticAIDocs` serializes into [agent specs](pydantic-ai-agent-specs.md) under the name `PydanticAIDocs`, so `capabilities: [{PydanticAIDocs: {}}]` loads with `custom_capability_types=[PydanticAIDocs]`[^pydantic-ai-docs-docs] Specs written before the rename from `PyaiDocs` still use the old block name: loading them means passing the deprecated `PyaiDocs` class from `pydantic_ai_harness.docs`, which keeps that serialization name and warns; re-saving with `PydanticAIDocs` migrates them.

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files, and the flow diagram is read in its text form[^pydantic-ai-docs-docs] Every external link — the capabilities overview, prefix tools, the agent-spec and workspace pages, the GitHub source tree — was read as a link and not followed. The page states no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-sonnet-5-5` and `anthropic:claude-sonnet-4-6`, aliases no release pin corroborates.

Nothing was installed, no topic read, no page fetched and no alias substituted, so every claim is **Reported** and none **Observed** or **Reproduced**. The source does not state the size of the returned pages, what the tool does when a topic page exists but is empty, or whether the remote fetch is retried — the practical limits on how much context one call can cost.

## Relationships

- **Depends on** the [workspace](pydantic-ai-workspaces-and-sandboxes.md) only when a local checkout is configured.
- **Uses** the same on-demand loading idea as [on-demand capabilities](pydantic-ai-on-demand-capabilities.md) and [Harness skills](pydantic-ai-harness-skills.md), which load `SKILL.md` procedures rather than reference pages.
- **Configurable through** [Pydantic AI agent specs](pydantic-ai-agent-specs.md), with a back-compatible `PyaiDocs` alias.
- **Related to** [Code Mode](pydantic-ai-code-mode.md): an agent writing Pydantic AI capabilities is the same audience that reads these six topics.

[^pydantic-ai-docs-docs]: Pydantic Docs, "Pydantic AI Docs", <https://pydantic.dev/docs/ai/harness/pydantic-ai-docs/>; local capture `raw/harness/pydantic-ai-docs/index.md`, content digest sha256:4016fb73, 1,439 words as declared (1,512 by `wc -w`), 252 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the one-tool contract and the local-then-remote resolution; 13–33 for the flow diagram including the error branch; 35–37 for the problem the capability solves; 39–63 for the topic list, the usage example, the workspace requirement and the static instruction; 65–77 for the three-step resolution order and the alias replacement, plus the environment-variable precedence and `~` rule; 79–87 for the `local_docs_path`/`cache`/`remote_ref` table and the per-run cache isolation; 89–93 for the default `id` and its merge/`UserError` rule under `PrefixTools`; 95–114 for the agent-spec name and the `PyaiDocs` rename path; 116–251 for the API reference (`local_docs_path`, `cache`, `remote_ref`, `id`, `combine`, `for_run`, `before_run`, `get_instructions`, `get_toolset`, `get_serialization_name`). Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
