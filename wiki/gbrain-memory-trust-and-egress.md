---
type: Concept
title: GBrain memory trust, egress and contradictions
description: GBrain's six trust tiers, write-gate defaults, what text leaves the machine (including the Memorable relay consent model), and its contradiction-detection and calibration mechanisms.
tags: [agent-memory, gbrain, trust, privacy, contradictions]
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
  - id: memory-trust
    resource: ../raw/gbrain/docs/guides/memory-trust.md
    kind: code
    revision: 27f8b9d
    title: Memory trust guide
  - id: memory-boundaries
    resource: ../raw/gbrain/docs/guides/memory-boundaries.md
    kind: code
    revision: 27f8b9d
    title: Memory boundaries
  - id: memorable
    resource: ../raw/gbrain/docs/memorable-agents.md
    kind: code
    revision: 27f8b9d
    title: Memorable integration guide
  - id: tier-ts
    resource: ../raw/gbrain/src/core/trust/tier.ts
    kind: code
    revision: 27f8b9d
    title: Trust tiers
  - id: guardrails
    resource: ../raw/gbrain/docs/guardrails.md
    kind: code
    revision: 27f8b9d
    title: Guardrail seams
  - id: contradictions-doc
    resource: ../raw/gbrain/docs/contradictions.md
    kind: code
    revision: 27f8b9d
    title: Contradictions probe
  - id: decide-doc
    resource: ../raw/gbrain/docs/architecture/decide.md
    kind: code
    revision: 27f8b9d
    title: decide architecture
  - id: calibration-spec
    resource: ../raw/gbrain/docs/architecture/calibration-quality-gate-spec.md
    kind: code
    revision: 27f8b9d
    title: Calibration quality gate spec
  - id: belief-ledger-design
    resource: ../raw/gbrain/docs/designs/BELIEF_LEDGER.md
    kind: code
    revision: 27f8b9d
    title: Belief ledger design
---

GBrain labels every stored memory with a trust tier, by default *flags and labels* suspicious writes instead of blocking them, can send memory text to configured providers, while keyless keyword retrieval needs no model API, and offers three independent contradiction mechanisms that propose but never auto-apply changes. The README is explicit that configured cloud embedding, reranking, extraction and synthesis providers can receive text, and that the harness's own model sees recalled memory even in keyless mode.[^readme] Fact and take semantics are in the [memory model](gbrain-memory-model.md); caller isolation is in [authorization and security](gbrain-authorization-and-security.md).

## Trust tiers (Observed)

Six ordered tiers with fixed user-facing labels: `user_confirmed` ("confirmed by you") > `operator_curated` ("your notes") > `tool_observed` > `agent_written` > `unknown` ("unverified origin") > `external_untrusted`. `user_said` stays `agent_written` with a `:user_said` origin marker; nothing becomes confirmed without a typed confirmation at a terminal (`--yes` never confirms).[^tier-ts]

Defaults (Reported): `trust.read_policy=label`, `write_gate.external_mode=flag`, `write_gate.agent_mode=flag`, `trust.agent_activation=allow` — instruction-like writes are saved, flagged, still pushed and labeled. Opt-in hardening: quarantine, reject, suppress, `recall.confidence_weighting` (age and tier; at most halves a score, never hides) and `min_trust` floors. `trust claim-sources` lifts pre-tier rows to "your notes" in a bounded, resumable pass; connector sources can never be claimed.[^memory-trust]

## What leaves the machine

- Keyless keyword memory does not itself require a model API; text can leave via configured providers (embeddings, rerank, expansion, synthesis, LLM extraction) and via the connected agent's own model (Reported).[^memory-boundaries]
- **Memorable** (optional procedural memory, off by default) needs three independent switches: Memorable's own `memorable enable` (fail-closed), `integrations.memorable.enabled`, and a gbrain-private disclosure stamp written only when a human accepts (non-interactive needs `--yes`). The env-only kill switch `GBRAIN_MEMORABLE=0` cannot be overridden by any env value. Per command: `record` sends a session id, a redacted ≤ 200-char task line and redacted allowlisted tool calls; `ingest <trace>` can send conversation text; `recall` sends nothing unless there is no local embedder and a lexical miss (then ≤ 8 KB to `/v1/embed`). Redaction is best effort; the CLI is closed-source and its server-side statelessness is Memorable's claim, which GBrain cannot verify (Reported). Receipts are kept locally (mode 0600).[^memorable]
- **Guardrail seams** are observe-only and fail-open with five hooks (`file_storage.markdown|code`, `ai_gateway.chat|expand|tool_input`); they exclude system prompts, history, tool output and LLM output (Observed in docs and `guardrails.ts`).[^guardrails]
- Soft deletes are restorable for 72 h (remote) while purge removes text; see [data model](gbrain-data-model-and-system-of-record.md).

## Contradiction detection (three mechanisms)

1. **Keyless typed-claim conflicts:** same entity + metric + unit + period in the same as-of bucket; `dream.claim_conflicts.mode propose` or `gbrain decide sweep --claims` produces one `dp<id>` proposal per pair; facts read `contested`; nothing auto-applies (Reported; `claim-conflicts.ts` Observed).[^memory-trust]
2. **`decide` conflict slot (S9):** outcomes `duplicate|proposal|independent`; accept/undo is the only automated fact write. Decide calibration is code-owned: thresholds follow operator > adopted calibration > newest local row > shipped reference; harmful slots need `action_precision_lb ≥ 0.90`; receipts store HMAC-SHA256 hashes only (Reported).[^decide-doc]
3. **Eval probe:** an LLM judge with a six-member verdict enum (including `temporal_supersession`, `temporal_regression`, `temporal_evolution`, `negation_artifact`), a date pre-filter, Wilson 95% CIs and a small-sample note under n < 30; read-only (Reported). Contradictions are not yet pushed into agent context.[^contradictions-doc]

## Calibration and belief ledger

`takes scorecard|calibration|journal|horizon|grades` score resolved predictions. The richer falsifiability gate in `calibration-quality-gate-spec.md` is self-labeled "largely unshipped", and a subagent found no `falsifiability` identifier anywhere in `src/` (Observed).[^calibration-spec] `BELIEF_LEDGER.md` still says "design, not built", yet `src/core/belief/` (20 modules), migration v249 and the `gbrain beliefs` command exist (Observed by subagent); treat the design doc's status line as stale.[^belief-ledger-design]

## Relationships

- Depends on: [memory model](gbrain-memory-model.md), [embeddings and providers](gbrain-embeddings-and-providers.md) (what providers receive).
- Related: [authorization and security](gbrain-authorization-and-security.md), [dream cycle](gbrain-dream-cycle-and-autopilot.md) (`edge_contradictions`, `claim_conflicts` phases).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` paragraph "Durable preferences and facts can be shared across agents…" and "Memorable" section.
[^memory-trust]: `docs/guides/memory-trust.md` (defaults; "Old and conflicting facts"); `src/core/facts/claim-conflicts.ts`, `src/commands/decide/claims-sweep.ts` via subagent.
[^memory-boundaries]: `docs/guides/memory-boundaries.md` "Where text goes", "Expire vs purge".
[^memorable]: `docs/memorable-agents.md` "Trust", per-command egress table.
[^tier-ts]: `src/core/trust/tier.ts` lines 19–46.
[^guardrails]: `docs/guardrails.md` lines 1–60; `src/core/guardrails.ts`.
[^decide-doc]: `docs/architecture/decide.md` §S9, "Policy", "Receipts".
[^contradictions-doc]: `docs/contradictions.md`; `docs/guides/push-context.md` ("Contradictions are not pushed yet").
[^calibration-spec]: `docs/architecture/calibration-quality-gate-spec.md` (self-label); grep of `src/` for `falsifiability` by subagent.
[^belief-ledger-design]: `docs/designs/BELIEF_LEDGER.md` line 3; `docs/architecture/key-files/belief-ledger.md`.
