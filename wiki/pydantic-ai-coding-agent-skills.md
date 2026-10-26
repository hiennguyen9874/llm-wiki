---
type: Concept
title: Pydantic AI coding-agent skills
description: Pydantic's first-party agent skills for Pydantic AI, Pydantic Validation and Logfire — the three distribution channels, what each skill covers, and the install commands, with the staleness argument behind maintaining them in-repo.
tags: [pydantic-ai, logfire, tooling, skills]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:56:00Z }
sources:
  - id: pydantic-skills-2026
    resource: ../raw/pydantic-ai-logfire-claude-code-skills/index.md
    scope: ../raw/pydantic-ai-logfire-claude-code-skills/
    kind: article
    revision: sha256:3da1d0df08ca1a0182dd259a7d1c9553b26eebe4bd2499b960f76f21064ac9b3
    title: "Official Pydantic skills for coding agents"
---

Pydantic maintains official agent skills for three of its libraries — Pydantic Validation, Pydantic AI and Logfire — and ships them three ways: from Claude's plugin marketplace, from the `pydantic/skills` repository for any agent that follows the agentskills.io spec, and, for Python projects, straight out of the installed packages via library-skills.io[^pydantic-skills-2026] The stated reason is staleness rather than absence: community skills already existed, but the libraries move fast and a skill maintained outside the repository drifts into calling APIs that no longer exist, which the author rates as worse than having no skill at all[^pydantic-skills-2026] This page records the distribution surface and the install paths; no skill was installed, read or exercised here, and the article names no Pydantic AI or Logfire version.

## Three channels, three audiences

| Channel | Reaches | Entry |
| --- | --- | --- |
| Claude plugin marketplace | Claude Code, one plugin each for Pydantic AI and Logfire | `claude.com/plugins/pydantic-ai`, `claude.com/plugins/logfire` |
| `pydantic/skills` repository | Cursor, Codex, Gemini CLI and any agent following the agentskills.io spec | `npx skills add pydantic/skills --skill <name>` |
| library-skills.io | Python projects only, reading the installed dependencies | `uvx library-skills` |

The Claude marketplace route is official for two of the three: Pydantic Validation is not listed there, so it is installed by adding the Pydantic marketplace and installing the `pydantic` plugin[^pydantic-skills-2026]:

```bash
claude plugin marketplace add pydantic/skills
claude plugin install pydantic@pydantic-skills
```

For every other agent the three skills are named individually in the `pydantic/skills` repository — `pydantic`, `building-pydantic-ai-agents` and `logfire-instrumentation`[^pydantic-skills-2026]:

```bash
npx skills add pydantic/skills --skill pydantic
npx skills add pydantic/skills --skill building-pydantic-ai-agents
npx skills add pydantic/skills --skill logfire-instrumentation
```

## What each skill covers

The article gives a scope list per skill rather than a file inventory[^pydantic-skills-2026]:

| Skill | Covers |
| --- | --- |
| Pydantic Validation (`pydantic`) | Data modelling — constraints and field metadata, validators, type coercion, unions, forward annotations, model hierarchies |
| Pydantic AI (`building-pydantic-ai-agents`) | Building an agent — dependencies and output types, tools and run context, structured output, streaming, stepping through the agent graph |
| Logfire (`logfire-instrumentation`) | Instrumentation in Python, JavaScript/TypeScript and Rust — spans and structured logging, framework and library integrations, metrics, querying telemetry |

`logfire-instrumentation` is deliberately polyglot: it instructs the agent to inspect `pyproject.toml` or `requirements.txt`, `package.json`, or `Cargo.toml` and then follow the matching SDK guidance, so one skill covers all three runtimes[^pydantic-skills-2026]

## The installed-dependency route

For Python, the skills also ship inside the packages, so they can be extracted from what the project already depends on instead of fetched[^pydantic-skills-2026]:

```bash
uvx library-skills --all
```

The `--all` flag scans transitive dependencies, and the article says Pydantic AI needs it because its skill ships inside `pydantic-ai-slim` rather than in a top-level dependency. A project that only uses Logfire can drop the flag. This route is exclusive to the Python packages; JavaScript/TypeScript and Rust projects use the `logfire-instrumentation` skill command instead[^pydantic-skills-2026]

## Limits

- No version is named anywhere — not for the three libraries, the skills, the `pydantic/skills` repository, or the library-skills tool — so the install commands and the skill names are as of publication (2026-07-29) and carry no compatibility statement[^pydantic-skills-2026]
- The scope lists are the article's summary; no `SKILL.md`, manifest or repository file was fetched, so neither the actual triggering conditions nor the contents of a skill are recorded here[^pydantic-skills-2026]
- Nothing installed or executed: no marketplace added, no skill run, no `library-skills` extraction performed, so every command is **Reported** and untested[^pydantic-skills-2026]
- The article does not say how the in-package copies stay in step with the repository ones, nor which version of a library ships which skill version[^pydantic-skills-2026]
- Reporting a wrong or missing skill is directed at the `pydantic`, `pydantic-ai` or `logfire` issue trackers rather than a single skills tracker[^pydantic-skills-2026]

## Relationships

- **Complements** [Logfire MCP server](logfire-mcp-server.md): the Claude Code `logfire` plugin bundles that server with these skills, so the same install delivers a SQL query surface and the instrumentation guidance that tells the agent which attributes to query.
- **Documents the guidance layer for** [Pydantic AI v2 release](pydantic-ai-v2-release.md) and [capability primitive](pydantic-ai-capability-primitive.md) — the stale-API risk the article opens with is the concrete cost of the release pace those pages record.
- **Part of** the first-party surface counted in [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md): skills are distribution, not a runtime dependency, and nothing in the runtime changes when they are installed.

[^pydantic-skills-2026]: Aditya Vardhan, "Official Pydantic skills for coding agents", Pydantic, published 2026-07-29, 415 words as declared (458 by local `wc -w`), §"Why official skills" (community skills exist, libraries move fast, a stale skill is worse than none), §"What's in them" (the per-skill scope lists), §"Install" (raw lines 31–57) for the Claude marketplace, `pydantic/skills` and library-skills routes and the three skill names, §"Python" (lines 59–69) for `--all`, transitive scanning and the `pydantic-ai-slim` packaging reason, §"JavaScript/TypeScript" and §"Rust" for the polyglot skill and the `Cargo.toml` guidance, §"Logfire" runtime detection via `pyproject.toml`/`requirements.txt`/`package.json`/`Cargo.toml`, and the closing paragraph for the issue trackers. Local capture: `raw/pydantic-ai-logfire-claude-code-skills/index.md`, content digest sha256:3da1d0df. Evidence class: **Reported** — a vendor announcement of the vendor's own distribution; no skill installed, no repository or `SKILL.md` inspected, no command executed.
