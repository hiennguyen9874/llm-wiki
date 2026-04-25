---
name: llm-wiki-visualization
description: Create or update Canvases, Bases, and live-vault validation workflows for this knowledge base. Use when the task benefits from visual mapping, dashboards, queues, or validating discoverability in Obsidian.
---

# LLM Wiki Visualization

Use this skill when the task benefits from a visual or operational artifact.
Always activate `llm-wiki-core` first.

This file owns visualization procedure only.
- Use `llm-wiki-ops` when updating naming, placement, `wiki/index.md`, `wiki/log.md`, or discoverability conventions.
- Use `llm-wiki-schema` when visual artifacts need aligned metadata or linked markdown structure.

## Companion Skills
- `json-canvas` for `.canvas` files
- `obsidian-bases` for `.base` files
- `obsidian-cli` when a running Obsidian vault should be inspected or validated
- `obsidian-markdown` when embedding or linking visual artifacts from notes

## Manual Graph-Insights Stance
Use Canvases and Bases as Obsidian-first overlays. They may represent isolated pages, sparse clusters, bridge pages, surprising connections, and review queues, but they are not a separate graph engine. Do not claim Louvain/community detection, 4-signal relevance, or other graph algorithms unless implemented by actual tooling. When maintenance or query finds graph-insights-lite patterns, consider a Canvas or Base to make them reviewable.

## Visual Synthesis Workflow
Use JSON Canvas when a topic is relational, ambiguous, or benefits from spatial organization.

Good use cases:
- concept maps
- source relationship maps
- project strategy maps
- timelines and causal maps
- people/projects/ideas relationship maps

Workflow:
1. Decide the canvas purpose.
2. Create or update a `.canvas` file in `wiki/canvases/`.
3. Use nodes for concepts, source notes, projects, prompts, or lifecycle stages.
4. Connect them with labeled edges where useful.
5. Keep layout readable and validate JSON integrity.
6. Add the canvas to `wiki/index.md`.
7. Log meaningful work as `visualize` or `update`.

## Bases Workflow
Use Obsidian Bases for operational dashboards and review queues.

Good use cases:
- inbox queue
- source inventory
- stale-page review queue
- project tracker
- reading list
- outputs-to-promote queue
- human review queue from `outputs/review-queue/`
- graph-insights-lite findings
- pages with low confidence or low quality

Workflow:
1. Create or update `.base` files in `wiki/bases/`.
2. Use filters over folders, tags, and metadata.
3. Add formulas only when they materially improve review or triage.
4. Validate YAML carefully.
5. Add important bases to `wiki/index.md`.
6. Log meaningful work as `visualize` or `update`.

## Vault Interaction Policy
If Obsidian is open and the task benefits from live vault interaction, use Obsidian CLI to:
- search the vault
- inspect backlinks or properties
- create/open notes
- validate that notes render or exist as expected

Especially useful for:
- checking note discoverability
- validating Bases or Canvas behavior
- supporting plugin/theme/vault workflows
