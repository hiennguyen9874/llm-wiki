---
name: llm-wiki-visualization
description: Create or update Canvases, Bases, and live-vault validation workflows for this knowledge base. Use when the task benefits from visual mapping, dashboards, queues, or validating discoverability in Obsidian.
---

# LLM Wiki Visualization

Use this skill when the task benefits from a visual or operational artifact.
Always activate `llm-wiki-core` first.

## Companion Skills
- `json-canvas` for `.canvas` files
- `obsidian-bases` for `.base` files
- `obsidian-cli` when a running Obsidian vault should be inspected or validated
- `obsidian-markdown` when embedding or linking visual artifacts from notes

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
