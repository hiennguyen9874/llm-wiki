---
title: Ingest Plan - Simple 4-Step AI Trading Assistant With Claude
created: 2026-04-26
last_updated: 2026-04-26
page_type: ingest_plan
status: draft
visibility: private
retention_class: working
related_sources:
  - [[source-how-to-actually-build-a-trading-bot-with-claude-code]]
---

# Ingest Plan - Simple 4-Step AI Trading Assistant With Claude

## Source identity
- Source file: `raw/articles/the-simple-4-step-process-to-build-your-own-ai-trading-assistant-with-claude-(for-beginners).md`
- Source type: article / video summary
- Likely topic domain: Claude Code workflows, personal trading dashboards, journaling, playbooks, routine automation
- Why it matters to `purpose.md`: this source adds a durable workflow pattern for using Claude Code to build a bespoke trading assistant. The key takeaway is not the specific dashboard, but the repeatable plan/build/personalize/routine loop that could generalize to other personal tools.

## Key entities and relationships
- Claude Code → planning/building interface for the assistant
- AI trading assistant → personal tool / dashboard
- trading dashboard → local HTML-style workspace for trades, best opportunities, and journals
- playbook → stored trade setup logic and rules
- tendencies → recurring mistakes / behavior patterns discovered from journals
- coach notes → AI-generated feedback layer based on historical review
- routines → scheduled daily review prompts or popups
- plan mode / build mode / personalization / routines → the four-step workflow described by the source

## Candidate claims
- The source presents a four-step workflow: plan mode, build mode, personalization, and routines.
- Plan mode is used to brainstorm requirements and build an implementation plan before coding.
- The assistant focuses on a local trading dashboard that tracks trades, opportunities, journals, playbooks, tendencies, and coach notes.
- Personalization is where the dashboard is adapted to the trader’s actual workflow and metrics.
- Routines make the tool part of a repeatable daily review loop.
- The durable lesson is the workflow pattern, not the exact dashboard UI.

## Existing pages likely affected
- `[[source-how-to-actually-build-a-trading-bot-with-claude-code]]` — sibling source page with adjacent Claude Code + trading workflow content.
- `[[regime-trading-bot]]` — adjacent Claude Code trading-automation page, but the source should remain distinct because this one centers on journaling / assistant workflows rather than execution automation.
- `[[vibe-trading]]` — adjacent broader agentic-finance workspace page, useful if future sources reinforce the assistant / dashboard theme.
- `[[wiki/overview]]` — may merit a small cluster-level note because this source broadens the Claude Code trading branch from bot-building into personal assistant workflows.
- `[[wiki/index]]` — should gain a new source entry for discoverability.

## New vs reinforced vs uncertain
### New
- Claude Code can be used to structure a trading-assistant build process around explicit planning, question-driven requirements gathering, and scheduled routine integration.
- The source foregrounds journaling, tendencies, and coach notes as the main value of the assistant.

### Reinforced
- The vault’s trading branch already favors explicit workflows, structured review, and local tools over vague “AI magic.”
- Durable finance tools in this repo tend to couple AI with evidence capture, logs, dashboards, or backtests.

### Uncertain
- The source is a video summary rather than a first-hand transcript, so the exact UI and feature behavior should stay slightly lower-confidence.
- It is unclear whether Claude Code’s routine capability is native, external, or a workflow pattern demonstrated in the video.
- No separate `ai-trading-assistant` topic page is warranted yet unless another source reinforces the concept.

## Proposed page actions
### Source page
Create `wiki/source-simple-4-step-ai-trading-assistant-with-claude.md` with:
- source metadata
- concise summary of the workflow and why it matters
- claim blocks for the four-step process, plan-mode behavior, assistant contents, personalization, and routines
- open questions about generalization and routine implementation
- related pages linking to the sibling Claude Code trading bot source and adjacent finance-workspace pages

### Canonical updates
- Add a small related-page backlink from `wiki/source-how-to-actually-build-a-trading-bot-with-claude-code.md`.
- Update `wiki/overview.md` to mention the new assistant-workflow branch in the trading cluster.
- Update `wiki/index.md` and `wiki/log.md`.

## Traceability updates
- Preserve the raw source unchanged.
- Keep source traceability explicit in the new source page.
- Use `related_sources` on the new source page only if it materially helps cluster navigation; otherwise keep it minimal to avoid noisy adjacency.

## Review items
1. Should this remain source-only, or later become a dedicated `ai-trading-assistant` topic page if more sources reinforce the workflow?
   - Recommendation: keep source-only for now; one source is enough to document the workflow without creating a premature concept page.

## Integration scope
- Single-source ingest is sufficient.
- No Base or Canvas is warranted yet.
- A later `/compile` pass may be useful if additional Claude Code workflow sources arrive.

## Artifact plan
- Save this ingest plan in `outputs/ingest-plans/` because it captures a durable workflow pattern and a non-trivial scope decision.
- Create the source page in `wiki/`.
- Update `wiki/source-how-to-actually-build-a-trading-bot-with-claude-code.md`, `wiki/overview.md`, `wiki/index.md`, and `wiki/log.md`.
- Add one review-queue item about whether this should later anchor a dedicated `ai-trading-assistant` topic page.
