---
title: Workflow Review Report
created: 2026-04-15
review_scope:
  - AGENTS.md
  - .pi/prompts/*
  - .pi/skills/llm-wiki-*
comparison_sources:
  - LLM-WIKI.md
  - LLM-WIKI-v2.md
status: updated
last_updated: 2026-04-15
---

# Workflow Review Report

## Executive summary

Current workflow design is **well aligned with the original `LLM-WIKI.md` pattern** and **partially aligned with the extended `LLM-WIKI-v2.md` pattern**.

In short:
- **Original pattern coverage:** strong
- **v2 lifecycle / scale / automation coverage:** mixed
- **Main gap:** the repo has the right concepts in several places, but many v2 ideas are still **metadata-level or aspirational**, not yet turned into explicit operational workflow rules

The current system is already a strong **manual, disciplined, persistent wiki workflow**. It clearly implements the core LLM-wiki model: raw sources → compiled wiki → schema/procedures; ingest/query/review/crystallize; index/log; broad integration; contradiction handling; durable outputs; and human-in-the-loop governance.

What is **not yet fully implemented** is the stronger v2 machinery: a fully materialized graph layer, event-driven automation, full auditability, and multi-agent coordination. Several previously missing areas were implemented in a later update pass, especially around claim-aware structure, retention workflows, contradiction resolution, privacy filtering, quality heuristics, session prompts, and manual-first governance.

---

## Update after implementation pass

After this report was first written, the workflow was updated across `AGENTS.md`, core skills, and prompt entry points. The following recommendations from this report are now **implemented or partially implemented**:

### Implemented since review
- explicit **manual-first** repository stance in `AGENTS.md`
- explicit **privacy/sensitivity screening** in ingest workflows and prompts
- stronger **contradiction-resolution rubric** using recency, authority/directness, support count, and specificity
- lightweight **claim/evidence structure** via `Evidence / claims` guidance in `llm-wiki-core`
- more concrete **hybrid retrieval procedure** in `llm-wiki-query`
- explicit **quality heuristics** and persistence thresholds
- explicit **retention review workflow** in maintenance plus `retention-pass.md`
- explicit **visibility semantics** for `private | shared | publishable`
- new **session-start** and **session-end** prompts
- clearer distinction between **brief** and **briefing**

### Still not implemented or only lightly implemented
- no true event-driven automation layer yet; the system remains prompt-driven
- no separate graph artifact or fully machine-usable graph layer yet
- auditability is improved, but still not a full per-operation audit trail
- multi-agent coordination remains out of scope / unimplemented

This means the report below should be read as the **initial review plus the implementation delta above**.

---

## Files reviewed

### Reference design
- `LLM-WIKI.md`
- `LLM-WIKI-v2.md`

### Current workflow files
- `AGENTS.md`
- `.pi/prompts/brief.md`
- `.pi/prompts/briefing.md`
- `.pi/prompts/connections.md`
- `.pi/prompts/crystallize.md`
- `.pi/prompts/disagreements.md`
- `.pi/prompts/explore.md`
- `.pi/prompts/gaps.md`
- `.pi/prompts/ingest-batch.md`
- `.pi/prompts/ingest.md`
- `.pi/prompts/ingest-url.md`
- `.pi/prompts/lint.md`
- `.pi/prompts/next-research.md`
- `.pi/prompts/query.md`
- `.pi/prompts/review.md`
- `.pi/skills/llm-wiki-core/SKILL.md`
- `.pi/skills/llm-wiki-crystallize/SKILL.md`
- `.pi/skills/llm-wiki-ingest/SKILL.md`
- `.pi/skills/llm-wiki-maintenance/SKILL.md`
- `.pi/skills/llm-wiki-query/SKILL.md`
- `.pi/skills/llm-wiki-visualization/SKILL.md`

---

## 1. What already matches the original `LLM-WIKI.md`

## 1.1 Core architecture: implemented

The original pattern defines three main layers: raw sources, wiki, and schema. Current workflow matches this strongly:
- `AGENTS.md` defines `raw/`, `wiki/`, `wiki/bases/`, `wiki/canvases/`, and `outputs/`
- `llm-wiki-core` formalizes memory architecture and lifecycle
- `AGENTS.md` + `.pi/prompts/` + `.pi/skills/` together act as the schema / operating instructions

This is a good extension of the original rather than a deviation.

## 1.2 Persistent compiled wiki, not scratchpad: implemented

This is one of the strongest matches.

Current workflow explicitly says:
- treat the wiki as a persistent compiled artifact
- prefer updating existing pages over making duplicates
- keep durable insights in markdown artifacts, not only in chat
- broadly integrate new information instead of leaving isolated summaries

That is fully consistent with the central idea in `LLM-WIKI.md`.

## 1.3 Ingest / query / lint operations: implemented

The original names ingest, query, and lint as the core operations. Current workflow covers all of them clearly:
- ingest: `.pi/skills/llm-wiki-ingest`, prompts `ingest.md`, `ingest-url.md`, `ingest-batch.md`
- query: `.pi/skills/llm-wiki-query`, prompts `query.md`, `briefing.md`, `brief.md`, `connections.md`, `disagreements.md`, `gaps.md`, `next-research.md`, `explore.md`
- maintenance / lint / review: `.pi/skills/llm-wiki-maintenance`, prompts `review.md`, `lint.md`
- crystallization: extra layer beyond original, but compatible with it

## 1.4 Index and log discipline: implemented

The original strongly emphasizes `index.md` and `log.md`. Current workflow has good support for both:
- `AGENTS.md` requires updating `wiki/index.md` when important pages/artifacts change
- `AGENTS.md` requires append-only behavior for `wiki/log.md`
- `llm-wiki-core` defines a concrete log entry format and action taxonomy
- ingest / review / crystallize / visualization skills all include logging expectations

This is one of the most complete parts of the current design.

## 1.5 Durable outputs filed back into the system: implemented

The original says good answers should sometimes be filed back into the wiki. Current workflow does this well:
- query skill says durable answers can be saved into `outputs/answers/` or promoted into `wiki/`
- crystallization skill turns completed exploration into reusable artifacts
- maintenance skill explicitly promotes durable outputs into canonical pages

This is actually stronger than the original.

## 1.6 Search beyond index-only: good and intentional divergence

The original still leans on `index.md` as a query-time orientation tool. Current workflow deliberately shifts toward QMD and uses `wiki/index.md` only when helpful.

This is a **good divergence**, because it aligns with `LLM-WIKI-v2.md` scaling advice:
- QMD is made primary in `llm-wiki-core`
- query skill says use hybrid retrieval behavior and expand from entities/relationships
- prompts consistently say index first only when orientation is useful

So this is not a mismatch; it is an improvement.

## 1.7 Human-in-the-loop governance: implemented

The original describes the human as curator and director. Current workflow preserves that:
- user approval is required for high-stakes structural decisions
- `ask-user` is mandated for risky taxonomy / merge / deletion decisions
- prompts remain thin and allow human steering

This is aligned and healthy.

---

## 2. What already matches `LLM-WIKI-v2.md`

## 2.1 Memory lifecycle exists conceptually: implemented at the repository/workflow level

`LLM-WIKI-v2.md` introduces working / episodic / semantic / procedural memory. Current workflow already reflects this surprisingly well:
- `llm-wiki-core` defines all four tiers explicitly
- `raw/` = working memory
- `outputs/crystallizations/` and `outputs/analyses/` = episodic memory
- `wiki/` = semantic memory
- `AGENTS.md`, prompts, and skills = procedural memory

This is a strong conceptual match.

## 2.2 Supersession and contradiction handling: implemented and strengthened

Current workflow includes:
- `supersedes` / `superseded_by`
- `claim_status`
- explicit contradiction handling during ingest
- contradiction checks in maintenance
- disagreement analysis in prompts

This is now solid alignment with v2 for a manual-first system: the workflow does not just flag issues, it also defines a default comparison rubric and resolution behavior. It is still lighter than a full claim engine, but no longer merely metadata-level.

## 2.3 Confidence / quality metadata: partially operationalized

Current workflow includes fields such as:
- `confidence_score`
- `quality_score`
- `evidence_count`
- `last_confirmed`
- `retention_class`
- `visibility`

This is good and clearly inspired by v2.

However, these are mostly **schema fields**, not yet a full working policy. The workflow does not define:
- how confidence is calculated
- how confidence decays over time
- how contradictions affect scores
- what quality thresholds trigger rewrite or review
- whether scoring applies at page level only or claim level

So: **present in schema and now partially operationalized in workflow**, though still not a full claim-by-claim scoring engine.

## 2.4 Typed entities and relationships: implemented at workflow level

Current workflow clearly requires:
- entity extraction
- entity types
- attributes
- typed relationships
- preferred relationship verbs

This is strong alignment with the v2 knowledge-graph direction.

The limitation is that the structure lives mainly as markdown conventions and mental workflow, not as a separate graph artifact or graph-aware query system.

## 2.5 Visualization as graph support: partially implemented

The v2 document wants the graph to augment pages. Current workflow provides:
- `wiki/canvases/`
- `llm-wiki-visualization`
- relationship maps, timelines, concept maps, operational bases

This is useful, but it is still closer to **human-facing visual mapping** than to a machine-usable typed graph layer.

## 2.6 Crystallization: strongly implemented

This is one of the best v2-aligned parts of the current workflow.

Current design explicitly treats exploration and sessions as sources of memory:
- `llm-wiki-crystallize` is a dedicated skill
- prompts support converting completed work into `outputs/crystallizations/` or `outputs/analyses/`
- durable lessons are promoted into the canonical wiki

This is directly aligned with the v2 crystallization section.

## 2.7 Privacy and governance: stronger and more operationalized

Current workflow includes:
- do not commit secrets / credentials / private data
- sanitize sensitive source material before adding it
- prefer reversible bulk changes
- ask user before major structural changes
- use `wiki/log.md` and saved outputs for auditability

This is now meaningfully closer to v2 because privacy screening is part of ingest and maintenance workflows, though full audit-trail coverage is still not complete.

---

## 3. Main mismatches and missing implementation vs `LLM-WIKI-v2.md`

## 3.1 Claim-level lifecycle is now lightly implemented

### Current state
Current workflow has page metadata for confidence, evidence, quality, retention, and claim status.

### Gap
`LLM-WIKI-v2.md` frames lifecycle as something attached to **facts/claims**, not just pages. The current workflow now defines a lightweight `Evidence / claims` pattern, but it still does not provide a fully systematic claim engine for every page/claim. Remaining gaps include:
- universal use of individual claim records
- consistently maintained per-claim confidence
- consistently maintained per-claim recency
- comprehensive per-claim contradiction tracking

### Impact
The system can now represent high-value or disputed claims more explicitly, but it still cannot reliably guarantee full claim-by-claim lifecycle coverage everywhere.

### Update status
Implemented in lightweight form via `llm-wiki-core` guidance for `Evidence / claims` sections. Future improvement would be broader and more consistent adoption.

---

## 3.2 Retention / forgetting curve is partially implemented

### Current state
There is a `retention_class` field and mention of stale knowledge.

### Gap
There is now an explicit retention workflow and decay guidance, but it is still light/manual rather than fully automated. Remaining gaps include:
- automatic decay over time
- fully scheduled retention enforcement
- consistent application to all claims/pages

### Impact
The workflow now recognizes and operationalizes staleness better, but it still does not model forgetting as deeply or automatically as v2 recommends.

### Update status
Implemented in manual-first form via retention guidance in `llm-wiki-core`, retention workflow in `llm-wiki-maintenance`, and `retention-pass.md`.

---

## 3.3 Event-driven automation is still mostly missing

### Current state
Current workflow is mainly manual and prompt-driven.

`llm-wiki-maintenance` has an “automation direction” section, but it is aspirational.

### Gap
The following v2 hooks are still not event-driven/automatic:
- on new source
- on query persistence threshold
- on memory write contradiction check
- on schedule retention decay / consolidation

However, manual prompt entry points now exist for:
- session start
- session end
- retention review
- contradiction resolution

### Impact
The design is still strong for active manual use, but not yet a self-running memory system.

### Update status
Partially implemented: `AGENTS.md` now explicitly states a manual-first stance, and new prompts exist for `session-start.md`, `session-end.md`, `retention-pass.md`, and `resolve-contradictions.md`. True automation remains out of scope for now.

---

## 3.4 Hybrid retrieval is now specified more concretely

### Current state
`llm-wiki-query` says to use hybrid retrieval behavior and QMD as primary search.

### Gap
The workflow now specifies a repeatable manual-first retrieval pattern, though it still lacks a separate graph engine or hardcoded fusion pipeline.

### Impact
Operator behavior should now be more consistent across sessions, especially for exact-term search, concept-level search, and relationship expansion.

### Update status
Implemented in `llm-wiki-query` as a concrete retrieval strategy using lexical search, concept-level retrieval, metadata-aware filtering, and markdown-first relationship traversal.

---

## 3.5 Knowledge graph is implied, not materialized

### Current state
The workflow supports entity extraction, typed relationships, canvases, and cross-linking.

### Gap
There is no explicit durable graph layer such as:
- structured relation blocks
- graph-oriented files
- a canonical entity schema beyond prose pages
- graph traversal procedures for queries

### Impact
The repo benefits from graph-like thinking, but it does not yet have a true graph-backed workflow.

### Recommended update
Choose one lightweight path:
- **Option A:** keep graph-in-markdown but standardize a `Relationships` section format
- **Option B:** maintain companion graph data artifacts for entities/edges
- **Option C:** treat canvases as visual overlays only, but say clearly that no machine graph layer exists yet

---

## 3.6 Quality control is now partially operationalized

### Current state
`quality_score` exists in `llm-wiki-core`. Maintenance mentions low-quality pages. Lint supports safe self-heal.

### Gap
The workflow now defines basic heuristics, thresholds, and persistence checks, but it still does not run a separate quality-evaluation pass or full rewrite loop everywhere.

### Impact
The system now has a usable quality mechanism for everyday work, though not a full self-evaluating quality pipeline.

### Update status
Implemented in lightweight form via scoring heuristics in `llm-wiki-core`, quality checks in ingest/maintenance, and persistence thresholds in query workflows.

---

## 3.7 Contradiction resolution is now substantially specified

### Current state
Current workflow says to flag contradictions, preserve uncertainty, and sometimes assess which claim is better supported.

### Gap
The workflow now includes a stronger default rubric, but it still does not enforce claim-by-claim contradiction resolution everywhere automatically.

### Impact
Contradictions should now be handled more consistently during ingest, disagreement analysis, and maintenance.

### Update status
Implemented across ingest, maintenance, query/disagreement workflows using the recency + authority/directness + support-count + specificity rubric.

---

## 3.8 Privacy filtering is now made mandatory in ingest

### Current state
`llm-wiki-core` says not to commit secrets and to sanitize sensitive material.

### Gap
The remaining gap is not whether privacy screening exists, but whether legacy content and raw-source retention policies are fully audited and enforced everywhere.

### Impact
Privacy handling is now far less likely to be forgotten during normal ingest.

### Update status
Implemented in `AGENTS.md`, `llm-wiki-core`, `llm-wiki-ingest`, ingest prompts, and `privacy-scan.md`.

---

## 3.9 Audit trail is partial, not full

### Current state
`wiki/log.md` is append-only and well defined.

### Gap
v2 asks for logging every operation on the wiki with timestamp, what changed, and why. Current design logs important actions, but not clearly:
- delete operations
- bulk operations
- major edits with rationale
- query artifacts that were not persisted
- exact “why” for each change

### Impact
Good accountability exists, but it is not yet a full audit trail.

### Recommended update
Strengthen `wiki/log.md` rules or define a second audit convention for:
- bulk updates
- schema changes
- deletions
- merges
- automated maintenance passes

---

## 3.10 Shared/private scoping is now partially operationalized

### Current state
`visibility: private | shared | publishable` exists in `llm-wiki-core`.

### Gap
Skills now explain visibility semantics and promotion concerns, but there is still no separate queueing, storage, or workflow partition by visibility.

### Impact
Visibility is now more than metadata-only, but it is still lighter than a full scoped-memory system.

### Update status
Implemented in `llm-wiki-core` and reflected in ingest, query persistence, crystallization, and review flows.

---

## 3.11 Multi-agent coordination is not implemented

### Current state
No meaningful workflow support found for:
- multiple agents writing in parallel
- conflict merge policy
- work claiming / task ownership
- “who is working on what” notes

### Gap
This is a clear v2 omission.

### Impact
Probably acceptable for a personal single-agent workflow, but it is still a missing v2 capability.

### Recommended update
If multi-agent collaboration matters, add a lightweight coordination pattern, e.g.:
- a work queue page / base
- temporary claim markers for active tasks
- merge notes for parallel sessions

If not needed, explicitly mark this as intentionally out of scope.

---

## 4. File-by-file assessment

## 4.1 `AGENTS.md`

### Strong
- Clear mission and layer model
- Strong skill activation policy
- Good non-negotiables
- Good governance and prompt policy

### Needs update
- Add explicit statement of whether this repo targets **minimal/original** mode or **v2/advanced** mode
- Add automation policy or explicitly say “manual-first, automation later”
- Add retention/decay expectations
- Add privacy filtering as a mandatory ingest gate, not only a general rule
- Add stronger audit expectations for bulk operations and deletions
- Possibly add shared/private workflow semantics if you plan to use `visibility`

## 4.2 `.pi/skills/llm-wiki-core/SKILL.md`

### Strong
- Best file in the system for v2 alignment
- Memory tiers are explicit
- Lifecycle metadata exists
- Supersession, privacy, naming, frontmatter, outputs, index/log are all well defined

### Needs update
- Define operational scoring rules for `confidence_score` and `quality_score`
- Define retention/forgetting behavior
- Clarify claim-level vs page-level lifecycle
- Clarify whether graph data stays prose-only or has a structured representation
- Add explicit contradiction-resolution rubric
- Operationalize `visibility`

## 4.3 `.pi/skills/llm-wiki-ingest/SKILL.md`

### Strong
- Good broad integration mindset
- Good entity/relationship extraction
- Good reinforcement / contradiction / supersession framing
- Good update discipline across canonical pages

### Needs update
- Add mandatory sensitive-data sanitization step
- Add contradiction-resolution step, not only contradiction-flagging
- Add optional quality self-check before final write
- Add explicit claim extraction/provenance pattern if moving toward stronger v2 lifecycle
- Add graph update expectations if a graph layer is introduced

## 4.4 `.pi/skills/llm-wiki-query/SKILL.md`

### Strong
- Good shift from index-first to search-first
- Good mention of hybrid retrieval behavior
- Good treatment of uncertainty / staleness / dispute / supersession
- Good “persist durable value” rule

### Needs update
- Make hybrid retrieval more concrete
- Add graph traversal procedure if graph layer exists
- Add persistence threshold / quality gate for filing answers back
- Possibly add “session start context load” prompt or companion workflow outside this skill

## 4.5 `.pi/skills/llm-wiki-maintenance/SKILL.md`

### Strong
- Good lint checklist
- Good monthly review direction
- Good safe self-heal boundary
- Good future-looking automation direction

### Needs update
- Turn automation direction into concrete periodic workflows
- Add retention decay checks
- Add explicit quality threshold handling
- Add stronger audit and contradiction-resolution procedures
- Add optional privacy-scan pass for legacy content

## 4.6 `.pi/skills/llm-wiki-crystallize/SKILL.md`

### Strong
- Strong v2-aligned episodic-memory workflow
- Good promotion rules
- Good provenance expectations

### Needs update
- Add explicit procedural-memory promotion trigger for repeated lessons
- Add quality / confidence adjustment instructions when crystallized lessons reinforce or weaken canonical knowledge
- Add visibility handling if some session outputs are private

## 4.7 `.pi/skills/llm-wiki-visualization/SKILL.md`

### Strong
- Good support for canvases and bases
- Good human-facing graph support
- Good discoverability / Obsidian validation emphasis

### Needs update
- Clarify that this is visualization, not the canonical graph layer
- If desired, add a workflow for keeping visual artifacts in sync with entity/relationship data

## 4.8 `.pi/prompts/*`

### Strong
- They are intentionally thin, which matches `AGENTS.md`
- They consistently activate the right skills
- They preserve delegation to workflow skills rather than duplicating logic

### Needs update
Across prompts, the same missing v2 ideas remain:
- no explicit privacy/sensitivity gate in ingest prompts
- no claim-level lifecycle language
- no quality threshold for persisting outputs
- no automation/session-start/session-end prompts
- no dedicated retention / contradiction-resolution / graph-refresh prompts

### Specific prompt observations
- `brief.md` and `briefing.md` are very similar; decide whether both are needed
- `lint.md` is good, but could explicitly include retention decay and audit checks
- `review.md` is good, but could include promotion of repeated procedural lessons
- query-family prompts could require a standard retrieval pattern if you want more consistency

---

## 5. Priority update list

## Priority 1 — high value, low complexity

1. **Operationalize confidence and quality scoring**
   - Add simple scoring heuristics in `llm-wiki-core`
   - Reuse them in ingest, query persistence, and maintenance

2. **Make privacy filtering mandatory in ingest**
   - Add a required sanitization step and checklist item

3. **Strengthen contradiction resolution**
   - Add a default comparison rubric: recency, authority, support count

4. **Define retention decay behavior**
   - Even a light monthly rule is enough to start

5. **Clarify whether current system is manual-first or automation-targeted**
   - This should be explicit in `AGENTS.md`

## Priority 2 — medium complexity, strong v2 alignment

6. **Add claim-level evidence structure**
   - Lightweight claim blocks in wiki pages

7. **Standardize hybrid retrieval procedure**
   - Lexical + semantic + relationship expansion

8. **Add persistence thresholds for filing outputs back into memory**
   - Example: citation completeness + quality score + durable reuse value

9. **Improve audit trail for bulk / destructive operations**
   - Add explicit log schema for merges, deletions, schema changes

## Priority 3 — advanced / optional

10. **Introduce a true graph layer or clearly defer it**
11. **Add event-driven workflows or automation hooks**
12. **Add shared/private operational workflow**
13. **Add multi-agent coordination if parallel agents will matter**

---

## 6. Suggested new prompts or workflow modules

If you want stronger v2 coverage, the most useful additions would be:
- `.pi/prompts/session-start.md`
- `.pi/prompts/session-end.md`
- `.pi/prompts/retention-pass.md`
- `.pi/prompts/resolve-contradictions.md`
- `.pi/prompts/privacy-scan.md`
- `.pi/prompts/promote-outputs.md`
- `.pi/prompts/graph-refresh.md`

Potential new or expanded skills:
- stronger lifecycle policy inside `llm-wiki-core`
- stronger audit/governance procedure
- optional graph-management skill if you want structured entities/edges beyond prose

---

## 7. Bottom line

## Best overall judgment

Your current workflow is:
- **very aligned with `LLM-WIKI.md`**
- **already incorporates several major `LLM-WIKI-v2.md` ideas**
- **not yet a full v2 implementation**

The system today is best described as:

> a strong manual-first LLM wiki with clear memory tiers, good ingest/query/maintenance discipline, explicit supersession metadata, crystallization support, and strong Obsidian/QMD integration — but without full claim-level lifecycle management, retention decay, structured graph operations, event-driven automation, formal quality enforcement, or multi-agent coordination.

That means the foundation is good. The biggest work now is not inventing a new design, but **turning existing concepts into stronger operational rules**.

---

## Short answer: what needs update vs what is not implemented

## Needs update
- `llm-wiki-core`: strengthen audit/governance guidance further if full auditability becomes important
- `llm-wiki-maintenance`: decide how aggressive retention/quality enforcement should become in practice
- visualization / graph layer: decide whether to stay markdown-first or introduce a separate graph artifact
- prompts/skills: continue refining real-world usage after several maintenance and ingestion cycles

## Not implemented yet
- universal claim-by-claim lifecycle coverage across all important pages
- fully automated forgetting / retention decay
- event-driven automation hooks
- separate structured graph layer beyond markdown-first traversal
- full audit trail for all operations
- queue-based or storage-level shared/private separation
- multi-agent mesh sync / work coordination

---

## Recommended next step

If you want, I can do the next pass and produce a **concrete patch plan** for:
1. `AGENTS.md`
2. `llm-wiki-core`
3. `llm-wiki-ingest`
4. `llm-wiki-query`
5. `llm-wiki-maintenance`
6. the missing `.pi/prompts/*`

in priority order, with exact proposed text changes.
