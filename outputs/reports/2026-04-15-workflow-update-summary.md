---
title: Workflow Update Summary
created: 2026-04-15
last_updated: 2026-04-15
status: reviewed
page_type: synthesis
tags:
  - workflow
  - schema
  - prompts
  - skills
visibility: private
---

# Workflow Update Summary

## Summary

This pass updated the second-brain workflow to make the current system more operational, more explicit, and more internally consistent.

The main result is a stronger **manual-first LLM wiki workflow** with:
- clearer repository-level governance and workflow scope in `AGENTS.md` (`AGENTS.md`)
- more operational lifecycle rules in core skills, including privacy screening, confidence/quality heuristics, retention review, contradiction resolution, visibility handling, and lightweight claim tracking (`.pi/skills/llm-wiki-core/SKILL.md`, `.pi/skills/llm-wiki-ingest/SKILL.md`, `.pi/skills/llm-wiki-query/SKILL.md`, `.pi/skills/llm-wiki-maintenance/SKILL.md`, `.pi/skills/llm-wiki-crystallize/SKILL.md`)
- thinner but more precise prompts for ingest, query, review, lint, crystallization, and disagreement analysis (`.pi/prompts/ingest.md`, `.pi/prompts/ingest-url.md`, `.pi/prompts/ingest-batch.md`, `.pi/prompts/query.md`, `.pi/prompts/review.md`, `.pi/prompts/lint.md`, `.pi/prompts/crystallize.md`, `.pi/prompts/disagreements.md`)
- new prompts for retention review, contradiction resolution, privacy scanning, session start, and session end (`.pi/prompts/retention-pass.md`, `.pi/prompts/resolve-contradictions.md`, `.pi/prompts/privacy-scan.md`, `.pi/prompts/session-start.md`, `.pi/prompts/session-end.md`)
- clearer separation between a short **brief** and a fuller reusable **briefing** (`.pi/prompts/brief.md`, `.pi/prompts/briefing.md`, `.pi/skills/llm-wiki-query/SKILL.md`)

## What changed

## 1. Repository-level policy was clarified

`AGENTS.md` now explicitly states that the repository is **manual-first, human-steered, and prompt-driven**, and should not pretend hidden automation or graph infrastructure already exists (`AGENTS.md`).

It also now:
- distinguishes supported facts from inference/speculation (`AGENTS.md`)
- requires privacy/sensitivity screening before promoting material into `wiki/` or `outputs/` (`AGENTS.md`)
- clarifies that QMD is the primary retrieval layer and `wiki/index.md` is mainly for orientation (`AGENTS.md`)
- expands the prompt taxonomy to include retention, contradiction, privacy, and session-start/session-end workflows (`AGENTS.md`)

## 2. Core skill behavior became more operational

### `llm-wiki-core`

The core skill now carries more concrete policy instead of just vocabulary (`.pi/skills/llm-wiki-core/SKILL.md`):
- implementation stance is explicit
- page-level vs claim-level lifecycle is clarified
- lightweight confidence and quality heuristics are defined
- retention/review expectations are defined by `retention_class`
- visibility semantics are defined for `private | shared | publishable`
- a lightweight `Evidence / claims` pattern is defined for important or disputed claims
- markdown-first graph stance is explicit
- contradiction/supersession resolution behavior is more explicit
- logging expectations now require recording what changed and why for meaningful updates

### `llm-wiki-ingest`

The ingest skill now requires (`.pi/skills/llm-wiki-ingest/SKILL.md`):
- privacy/sensitivity screening before downstream promotion
- contradiction resolution using a shared rubric
- candidate-claim extraction, not just generic summarization
- use of lightweight claim blocks for high-value or disputed facts
- lifecycle, retention, visibility, and confidence/quality refresh when justified
- a quick quality self-check before finishing
- more explicit logging of what changed and why

### `llm-wiki-query`

The query skill now defines a more concrete retrieval pattern (`.pi/skills/llm-wiki-query/SKILL.md`):
- exact-term plus concept-level retrieval
- relationship expansion via typed relationships, backlinks, supersession links, and cited sources
- markdown-first graph traversal stance
- explicit distinction between supported facts, inference, and uncertainty
- a clearer persistence threshold for saved outputs
- explicit separation of `Brief` vs `Briefing`

### `llm-wiki-maintenance`

The maintenance skill now includes dedicated workflow guidance for (`.pi/skills/llm-wiki-maintenance/SKILL.md`):
- retention review / decay review
- contradiction resolution
- quality review
- privacy scanning
- visibility mismatch detection
- identifying pages that need lightweight `Evidence / claims` structure

### `llm-wiki-crystallize`

The crystallization skill now better supports episodic-to-semantic/procedural promotion (`.pi/skills/llm-wiki-crystallize/SKILL.md`):
- capture confidence/uncertainty when material matters
- set visibility deliberately
- update confidence / contradiction / supersession state when session outcomes change existing knowledge
- promote repeated process lessons into procedural memory when justified

## 3. Prompt layer was expanded and aligned

The thin prompt layer was updated to reflect the stronger workflow skills.

### Updated prompts

The following prompts were tightened to explicitly invoke privacy screening, contradiction handling, quality review, retention-aware review, or stronger persistence rules:
- `ingest.md` (`.pi/prompts/ingest.md`)
- `ingest-url.md` (`.pi/prompts/ingest-url.md`)
- `ingest-batch.md` (`.pi/prompts/ingest-batch.md`)
- `query.md` (`.pi/prompts/query.md`)
- `review.md` (`.pi/prompts/review.md`)
- `lint.md` (`.pi/prompts/lint.md`)
- `crystallize.md` (`.pi/prompts/crystallize.md`)
- `disagreements.md` (`.pi/prompts/disagreements.md`)

### New prompts

New prompt entry points were added for missing but now-supported workflows:
- `retention-pass.md` for decay / stale-knowledge review (`.pi/prompts/retention-pass.md`)
- `resolve-contradictions.md` for targeted contradiction resolution (`.pi/prompts/resolve-contradictions.md`)
- `privacy-scan.md` for downstream sensitive-content review (`.pi/prompts/privacy-scan.md`)
- `session-start.md` for context loading and orientation (`.pi/prompts/session-start.md`)
- `session-end.md` for end-of-session episodic distillation (`.pi/prompts/session-end.md`)

## 4. Brief vs briefing overlap was resolved

The prior overlap between `brief.md` and `briefing.md` was reduced.

### `brief.md`
Now means a **short, decision-oriented brief**:
- roughly 150-250 words
- one-sentence summary
- 3-5 key points
- 1-3 open questions or next steps
- save only when explicitly requested or clearly reusable (`.pi/prompts/brief.md`, `.pi/skills/llm-wiki-query/SKILL.md`)

### `briefing.md`
Now means a **fuller reusable briefing**:
- roughly 500 words
- one-sentence summary
- current state
- key tensions
- open questions
- recommended next steps
- save in `outputs/briefings/` when it has durable reuse value (`.pi/prompts/briefing.md`, `.pi/skills/llm-wiki-query/SKILL.md`)

## Why these changes matter

These changes move the workflow from “good concepts scattered across schema and prompts” toward “repeatable daily operating behavior.”

In practice, the updated workflow is better because it now:
- makes privacy handling part of normal ingest and maintenance rather than an easy-to-forget principle (`AGENTS.md`, `.pi/skills/llm-wiki-ingest/SKILL.md`, `.pi/skills/llm-wiki-maintenance/SKILL.md`)
- treats contradiction handling as a default workflow with a shared rubric rather than ad hoc judgment (`.pi/skills/llm-wiki-core/SKILL.md`, `.pi/skills/llm-wiki-ingest/SKILL.md`, `.pi/skills/llm-wiki-query/SKILL.md`, `.pi/skills/llm-wiki-maintenance/SKILL.md`)
- introduces retention review without over-claiming full automation (`AGENTS.md`, `.pi/skills/llm-wiki-core/SKILL.md`, `.pi/skills/llm-wiki-maintenance/SKILL.md`, `.pi/prompts/retention-pass.md`)
- provides an actionable, markdown-first path for claim-aware and graph-aware work without requiring a separate graph database (`.pi/skills/llm-wiki-core/SKILL.md`, `.pi/skills/llm-wiki-query/SKILL.md`)
- gives session context loading and session distillation first-class entry points (`.pi/prompts/session-start.md`, `.pi/prompts/session-end.md`)

## Remaining gaps

This update improves the workflow substantially, but several v2 ideas are still intentionally lightweight or still deferred:
- no true event-driven automation layer yet; workflows remain prompt-driven (`AGENTS.md`, `.pi/skills/llm-wiki-core/SKILL.md`)
- no separate machine-usable graph artifact yet; graph behavior remains markdown-first (`.pi/skills/llm-wiki-core/SKILL.md`)
- confidence and quality are now heuristic and operational, but still not fully claim-by-claim everywhere (`.pi/skills/llm-wiki-core/SKILL.md`)
- multi-agent coordination remains out of scope for now (`AGENTS.md` by omission; no dedicated coordination workflow added)

## Recommended next steps

1. Use the new prompts in real sessions and refine them based on actual friction:
   - `session-start.md`
   - `session-end.md`
   - `retention-pass.md`
   - `resolve-contradictions.md`
   - `privacy-scan.md`

2. Decide whether any high-value wiki pages should adopt the lightweight `Evidence / claims` structure first, especially pages with disputes, supersession chains, or mixed-confidence content (`.pi/skills/llm-wiki-core/SKILL.md`).

3. After several real uses, evaluate whether any of the new review flows should become semi-automated or scheduled, while keeping the manual-first stance honest (`AGENTS.md`, `.pi/skills/llm-wiki-maintenance/SKILL.md`).

## Affected files

### Repository policy
- `AGENTS.md`

### Updated skills
- `.pi/skills/llm-wiki-core/SKILL.md`
- `.pi/skills/llm-wiki-ingest/SKILL.md`
- `.pi/skills/llm-wiki-query/SKILL.md`
- `.pi/skills/llm-wiki-maintenance/SKILL.md`
- `.pi/skills/llm-wiki-crystallize/SKILL.md`

### Updated prompts
- `.pi/prompts/brief.md`
- `.pi/prompts/briefing.md`
- `.pi/prompts/crystallize.md`
- `.pi/prompts/disagreements.md`
- `.pi/prompts/ingest-batch.md`
- `.pi/prompts/ingest-url.md`
- `.pi/prompts/ingest.md`
- `.pi/prompts/lint.md`
- `.pi/prompts/query.md`
- `.pi/prompts/review.md`

### New prompts
- `.pi/prompts/privacy-scan.md`
- `.pi/prompts/resolve-contradictions.md`
- `.pi/prompts/retention-pass.md`
- `.pi/prompts/session-end.md`
- `.pi/prompts/session-start.md`

## Sources
- `AGENTS.md`
- `.pi/skills/llm-wiki-core/SKILL.md`
- `.pi/skills/llm-wiki-ingest/SKILL.md`
- `.pi/skills/llm-wiki-query/SKILL.md`
- `.pi/skills/llm-wiki-maintenance/SKILL.md`
- `.pi/skills/llm-wiki-crystallize/SKILL.md`
- `.pi/prompts/brief.md`
- `.pi/prompts/briefing.md`
- `.pi/prompts/crystallize.md`
- `.pi/prompts/disagreements.md`
- `.pi/prompts/ingest-batch.md`
- `.pi/prompts/ingest-url.md`
- `.pi/prompts/ingest.md`
- `.pi/prompts/lint.md`
- `.pi/prompts/privacy-scan.md`
- `.pi/prompts/query.md`
- `.pi/prompts/resolve-contradictions.md`
- `.pi/prompts/retention-pass.md`
- `.pi/prompts/review.md`
- `.pi/prompts/session-end.md`
- `.pi/prompts/session-start.md`
