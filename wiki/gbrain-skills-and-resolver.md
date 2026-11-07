---
type: Concept
title: GBrain skills, resolver and conventions
description: How GBrain teaches agents through 75 Markdown skills, the RESOLVER routing map, filing, output and friction conventions, and the tooling that creates, optimizes and distributes skills.
tags: [agent-memory, gbrain, skills, resolver, agent-instructions]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: skills-agent-readme
    resource: ../raw/gbrain/skills/_AGENT_README.md
    kind: code
    revision: 27f8b9d
    title: Skills agent README
  - id: resolver
    resource: ../raw/gbrain/skills/RESOLVER.md
    kind: code
    revision: 27f8b9d
    title: Skills resolver
  - id: filing-rules
    resource: ../raw/gbrain/skills/_brain-filing-rules.md
    kind: code
    revision: 27f8b9d
    title: Brain filing rules
  - id: output-rules
    resource: ../raw/gbrain/skills/_output-rules.md
    kind: code
    revision: 27f8b9d
    title: Output rules
  - id: friction-protocol
    resource: ../raw/gbrain/skills/_friction-protocol.md
    kind: code
    revision: 27f8b9d
    title: Friction protocol
  - id: manifest
    resource: ../raw/gbrain/skills/manifest.json
    kind: code
    revision: 27f8b9d
    title: Skills manifest
  - id: skillify
    resource: ../raw/gbrain/skills/skillify/SKILL.md
    kind: code
    revision: 27f8b9d
    title: skillify skill
  - id: skill-optimizer
    resource: ../raw/gbrain/skills/skill-optimizer/SKILL.md
    kind: code
    revision: 27f8b9d
    title: skill-optimizer skill
  - id: scaling-skills
    resource: ../raw/gbrain/docs/guides/scaling-skills.md
    kind: code
    revision: 27f8b9d
    title: Scaling skills guide
  - id: shared-skills
    resource: ../raw/gbrain/docs/guides/shared-brain-skills.md
    kind: code
    revision: 27f8b9d
    title: Shared brain skills guide
  - id: ethos-thin
    resource: ../raw/gbrain/docs/ethos/THIN_HARNESS_FAT_SKILLS.md
    kind: code
    revision: 27f8b9d
    title: Thin harness, fat skills
---

GBrain keeps the harness thin and puts behavior in Markdown "fat skills". A skill is a directory `skills/<slug>/` with a `SKILL.md` (frontmatter plus Contract, Phases, Output Format and Anti-Patterns), optionally with routing-eval fixtures and a paired script. The bundle has **75 skills** (the curator counted 75 `skills/*/SKILL.md` and the manifest parse agrees).[^skills-agent-readme][^manifest] The README describes shared skills that live beside knowledge.[^readme] The philosophy essay frames a skill file as "a method call", the harness as the secret (about 200 lines), and a resolver as a table saying what to load when.[^ethos-thin] How skills reach an agent is covered in [CLI and MCP surface](gbrain-cli-and-mcp-surface.md) (brain-first block) and [recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md).

## Routing

- **Runtime:** the harness matches each message against every skill's frontmatter `triggers:` (substring baseline; embeddings allowed on top). `priority:` is explicitly not routing.[^skills-agent-readme]
- **`RESOLVER.md`** is the human-readable dispatch map of the same routing, with a "which gbrain call for which lookup" table, ten numbered disambiguation rules and conventions; **frontmatter wins on disagreement**. It ships with the install but not through `skillpack scaffold` or the plugin lanes. A generated lookup-table block inside it contradicts the README claim that no machine-managed block exists.[^resolver][^skills-agent-readme]
- Frontmatter fields: `name`, `description`, `triggers[]`, `tools[]`, `mutating`, `writes_pages`/`writes_to`, `sources[]`, optional `upstream: <donor>@<sha>`, and `brain_first` (Observed across ~18 skill heads by subagent).

## Skill categories (Observed from the manifest and resolver sections)

| Group | Skills |
| --- | --- |
| Core brain loop | `brain-ops`, `query`, `enrich`, `capture`, `citation-fixer`, `correction-pipeline` |
| Ingestion and routing (13) | `ingest`, `idea-ingest`, `media-ingest`, `meeting-ingestion`, `voice-note-ingest`, `blog-ingest`, `bulk-ingestion`, `conversation-archive`, `chat-connectors`, `archive-crawler`, `citation-graph-ingest`, `two-tier-extraction`, `webhook-transforms` |
| Research and synthesis | `data-research`, `perplexity-research`, `academic-verify`, `fact-check`, `research-compendium`, `strategic-reading`, `book-mirror`, `concept-synthesis`, `idea-lineage`, `article-enrichment`, `draft-in-voice` |
| Gates and discipline | `brain-ingest-gate`, `brain-taxonomist`, `data-loss-gate`, `resolve-before-asking`, `cross-modal-review`, `measure-before-you-fix`, `frontmatter-guard`, `brain-link-discipline`, `eiirp` |
| Operations | `maintain`, `briefing`, `daily-task-manager`, `daily-task-prep`, `google-loops`, `cron-scheduler`, `reports`, `gbrain-advisor`, `smoke-test`, `db-repair`, `gbrain-upgrade`, `minion-orchestrator` |
| Setup, access, engine | `setup`, `cold-start`, `migrate`, `mcp-access`, `remote-mcp`, `postgres-adopt`, `company-brainify` |
| Schema, filing, output | `schema-author`, `schema-unify`, `repo-architecture`, `functional-area-resolver`, `publish`, `brain-pdf` |
| Meta / skill lifecycle | `skill-creator`, `skillify`, `skill-optimizer`, `skill-autobench`, `skillpack-check`, `skillpack-harvest`, `testing`, `context-audit`, `soul-audit` |
| Interaction | `ask-user`, `signal-detector` (opt-in ambient capture) |

## Conventions (Reported by the convention files; read by subagent)

- **Brain-first:** ask gbrain (CLI or same-named MCP tool) before `grep`/`cat`/SQL; parse `--json`, check exit codes.
- **Filing:** the primary subject decides the directory, not format or source; `sources/` is only for bulk raw imports; mandatory back-links ("Iron Law"); a notability gate ("when in doubt, DON'T create"); mandatory `[Source: …]` citations; raw sources under 100 MB in git and larger ones through `gbrain files upload-raw`; takes attribution (holder ≠ subject, 0.05 weight grid); a dream-cycle write allow-list in `_brain-filing-rules.json`.[^filing-rules]
- **Output:** links built deterministically from data; no slop, hedging, preamble or placeholder dates; verbatim phrasing preserved; titles under 60 characters.[^output-rules]
- **Friction:** log confusing, missing or wrong tool experiences with `gbrain friction log --severity … --phase … --message …` (and `--kind delight`); `render` redacts `$HOME` and `$CWD` by default.[^friction-protocol]

## Skill lifecycle tooling

- **Authoring:** `skill-creator`, and `skillify` — a 15-item checklist, a per-skill `eval_contract`, cross-modal eval before tests and a NO-REGRESSION LAW (any edit must score ≥ prior).[^skillify]
- **Optimization:** `skill-optimizer` wraps `gbrain skillopt` — the SKILL.md body is the trainable parameter and frontmatter mutation is forbidden; the validation gate is median-of-3 per task with a +0.05 epsilon; bundled skills need `--allow-mutate-bundled` plus a held-out set of ≥ 5 disjoint tasks or exit 2. One-shot rewrite is default; `--loop` is deprecated with removal on/after 2026-12-03 (time-sensitive).[^skill-optimizer]
- **Benchmark mining:** `skill-autobench` mines real invocations and stages benchmarks as pending human approval; it never rewrites a SKILL.md.
- **Health and distribution:** `skillpack-check` emits JSON `{healthy, summary, actions[], doctor, migrations}` (actions are proposals); `skillpack-harvest` is the inverse of scaffold. Skillpacks are *scaffolding, not packages*: `scaffold` copies additively, `reference` diffs, `--apply-clean-hunks` can overwrite intentional local edits, and there is no uninstall. `skills.lock.json` hashes and `bun run gate:skills` provide tamper evidence and a commit gate.[^scaling-skills]
- **Shared catalog:** canonical skills live beside knowledge in a brain source; child agents use `list_skills` → `get_skill` → `get_skill_asset` at a pinned revision, and membership grants cover following only (no tools, scripts, spend or capture).[^shared-skills]

## Staleness and gaps (Observed by subagent)

`skills/manifest.json#version` is `0.32.3.0` while `VERSION` is `0.60.593.0`; `GBRAIN_SKILLPACK.md` says "50+ skills" and still links the deprecated Twilio recipe; six skills carry bare `brain_first: exempt` without the justification the README requires. See [discrepancies](gbrain-doc-code-discrepancies.md).[^manifest]

## Relationships

- Delivered by: [recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md).
- Uses: [CLI and MCP surface](gbrain-cli-and-mcp-surface.md) (`gbrain` commands inside skills).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Keep skills beside knowledge"; "Auto-improve a skill with `gbrain skillopt`" tutorial entry.
[^skills-agent-readme]: `skills/_AGENT_README.md` "What lives in this directory", "Routing — your first job", "Frontmatter contract notes", "Updates", "Removing".
[^resolver]: `skills/RESOLVER.md` ("Disambiguation rules", "Conventions", generated lookup-table block).
[^filing-rules]: `skills/_brain-filing-rules.md`; `skills/_brain-filing-rules.json` (`dream_synthesize_paths.globs`).
[^output-rules]: `skills/_output-rules.md`.
[^friction-protocol]: `skills/_friction-protocol.md`.
[^manifest]: `skills/manifest.json` (`version`, 75 entries); `docs/GBRAIN_SKILLPACK.md` (stale counts) via subagent.
[^skillify]: `skills/skillify/SKILL.md` (checklist, `eval_contract`, NO-REGRESSION LAW).
[^skill-optimizer]: `skills/skill-optimizer/SKILL.md`; `docs/guides/skillopt.md` (deprecation banner); `docs/tutorials/improving-skills-with-skillopt.md`.
[^scaling-skills]: `docs/guides/scaling-skills.md` (gating, plugin bundling); `docs/guides/skillpacks-as-scaffolding.md`; `skills/skillpack-check/SKILL.md`.
[^shared-skills]: `docs/guides/shared-brain-skills.md`.
[^ethos-thin]: `docs/ethos/THIN_HARNESS_FAT_SKILLS.md` (`draft-v4`; five definitions).
