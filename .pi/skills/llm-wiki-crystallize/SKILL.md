---
name: llm-wiki-crystallize
description: Distill research, debugging, and exploration sessions into durable episodic memory, then promote stable lessons into the wiki. Use when a completed session produced insights worth preserving.
---

# LLM Wiki Crystallize

Use this skill when exploration itself has become a source.
Always activate `llm-wiki-core` first.

This file owns crystallization procedure only.
- Use `llm-wiki-schema` when writing crystallization artifacts, frontmatter, or wiki updates.
- Use `llm-wiki-governance` when the session contains sensitive, disputed, stale, or superseding knowledge.
- Use `llm-wiki-ops` when saved artifacts affect naming, index, log, or discoverability.

## Companion Skills
- `qmd` for locating affected pages and related prior work
- `obsidian-markdown` for crystallization artifacts and wiki updates
- `llm-wiki-visualization` if a Canvas or Base would clarify the episode

## Crystallization Workflow
1. Distill the completed session into a structured digest in `outputs/crystallizations/` or `outputs/analyses/`.
2. Capture:
   - original question
   - what was investigated
   - key findings
   - affected files, entities, and pages
   - unresolved questions
   - reusable lessons
   - confidence or uncertainty where it materially matters
   - appropriate visibility for the artifact
3. Promote durable lessons into `wiki/` pages or update existing canonical pages, guided by `purpose.md` when broad direction matters. If several crystallizations/outputs need synthesis, recommend or run `/compile`.
4. Add links from the crystallization artifact back to the relevant canonical pages.
5. If the session reinforces or weakens existing knowledge, update confidence, contradiction, or supersession state where justified.
6. If a repeated process lesson emerged, consider promoting it into procedural memory (`AGENTS.md`, skills, or prompts) and log why.
7. Update `wiki/overview.md` when the session changes current understanding, active themes, gaps, or direction.
8. Update `wiki/index.md` if the artifact or promoted pages are important for browsing; treat index as rebuildable but update it explicitly.
9. Create review queue items for non-blocking human judgments that emerged.
10. Append `crystallize` or `update` entries to `wiki/log.md`.

## Promotion Rules
- Promote stable concepts, not transient debugging noise.
- Preserve provenance back to the session artifact.
- If a lesson changes older knowledge, mark contradiction or supersession explicitly.
- If the session mainly produced process improvements, consider a procedural page instead of a topic page.
- Set visibility deliberately when the artifact contains personal or sensitive details.

## Good Crystallization Outputs
A strong artifact usually makes later reuse easier by preserving:
- the key insight
- the evidence or reasoning that supported it
- where it belongs in the existing knowledge graph
- what remains unresolved
- what should be promoted into semantic or procedural memory
