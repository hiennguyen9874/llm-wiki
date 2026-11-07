---
type: Concept
title: ai-memory auto-improvement loop, eval gates and rules promotion
description: The scheduled auto-improvement loop that stages and applies page proposals, its optional eval gate, and the not-yet-implemented rules-promotion design.
tags: [agent-memory, ai-memory, auto-improve, evals, rules]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: auto-improve
    resource: ../raw/ai-memory/docs/auto-improvement-loop.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Auto-improvement loop
  - id: eval-gates
    resource: ../raw/ai-memory/docs/auto-improve-eval-gates.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Auto-improve eval gates
  - id: rules-promotion
    resource: ../raw/ai-memory/docs/design-rules-promotion.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Rules promotion design (proposed)
---

# ai-memory auto-improvement loop, eval gates and rules promotion

The auto-improvement loop reviews recent sessions with an LLM and proposes edits to memory pages (rules, procedures); proposals are staged, optionally gated by an eval, then applied.[^auto-improve] It is inspired by the Hermes Agent self-improvement loop named in the README.[^readme]

Evidence class: **Observed** (docs and `auto_improve.rs`, delegated static reading); nothing executed; effectiveness **Unverified**. `stale_after` set because defaults are shipping-version specific.

## Loop behaviour (defaults)

- The scheduler is **on by default when an LLM provider exists**: `interval_secs=3600`, `max_sessions_per_tick=1` per project, `min_session_age_secs=600`.[^auto-improve]
- `require_approval=false` means proposals are staged in `_pending/auto-improve/` and auto-applied through `Wiki::apply_batch` as actor `auto_improve`; caps include `max_proposals_per_run=5` and `min_confidence=0.75`; a rejection buffer keeps 50 entries for 180 days.[^auto-improve]
- `patchable_page_prefixes=["_rules/","procedures/"]` constrain reviewer bodies (a documented blind spot). A cross-session `experience` pass is opt-in (`experience_every_sessions=0`).[^auto-improve]
- `memory_auto_improve` rejects removed `dry_run`/`stage`/`mode` parameters with `invalid_params`.[^auto-improve]

## Eval gate (off by default)

`[auto_improve.eval] enabled=false`. Choose either `builtin="structure"` (in-process; pass at `score_after ≥ 0.70` and ≥ `score_before`) or an external `command` speaking a JSON stdin/stdout contract. Any command, timeout, parse, `passed=false` or delta failure rejects only that proposal; results are recorded with eval id, body SHA-256s and an invocation digest. The server owns policy; hooks never run it, and clients sending `eval` get 422.[^eval-gates]

## Rules promotion — proposed, not implemented

`design-rules-promotion.md` proposes a budget of ≤15 rules (~40 lines) with `recommend/approve/edit/remove/list` and never auto-editing `AGENTS.md`. Delegated inspection found no `ai-memory rules` subcommand and no `[rules_promotion]` keys; only the lint `rule_suggestion` finding exists. Its 2.1/2.2 roadmap is stale (those releases shipped without it).[^rules-promotion] Treat as **proposed**.

## Relationships

- Builds on consolidation outputs: [Consolidation and aging](ai-memory-consolidation-and-aging.md); uses LLM task profiles from [Providers](ai-memory-llm-and-embedding-providers.md).
- Eval tooling for the harness itself: [Evals and benchmarks](ai-memory-evals-and-benchmarks.md).
- Egress implications: [Data handling](ai-memory-data-handling-and-lifecycle-ops.md).

[^readme]: `../raw/ai-memory/README.md` — "Built on the shoulders of" (Hermes Agent).
[^auto-improve]: `../raw/ai-memory/docs/auto-improvement-loop.md`; code `crates/ai-memory-consolidate/src/auto_improve.rs`, `auto_improve_schedule.rs` (symbol-level locators not recorded).
[^eval-gates]: `../raw/ai-memory/docs/auto-improve-eval-gates.md` — config, built-in checker, JSON contract, failure modes.
[^rules-promotion]: `../raw/ai-memory/docs/design-rules-promotion.md` — status banner and proposal; absence of subcommand checked via `crates/ai-memory-cli/src/cli.rs::Command` and `lint.rs:416` by a delegated agent.
