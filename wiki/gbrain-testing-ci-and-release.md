---
type: Concept
title: GBrain testing, CI, release and repository hygiene
description: GBrain's test lanes and commands, CI and guard battery, versioning and release gating, community-PR wave process, TLA+ drain-lease spec, vendored code and notable repo-hygiene findings.
tags: [agent-memory, gbrain, testing, ci, release, tla]
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
  - id: contributing
    resource: ../raw/gbrain/CONTRIBUTING.md
    kind: code
    revision: 27f8b9d
    title: Contributing guide
  - id: testing-doc
    resource: ../raw/gbrain/docs/TESTING.md
    kind: code
    revision: 27f8b9d
    title: Testing guide
  - id: releasing
    resource: ../raw/gbrain/docs/RELEASING.md
    kind: code
    revision: 27f8b9d
    title: Releasing guide
  - id: ci-red-runbook
    resource: ../raw/gbrain/docs/ci-red-runbook.md
    kind: code
    revision: 27f8b9d
    title: CI red runbook
  - id: package-json
    resource: ../raw/gbrain/package.json
    kind: code
    revision: 27f8b9d
    title: Package manifest
  - id: tla-readme
    resource: ../raw/gbrain/spec/tla/README.md
    kind: code
    revision: 27f8b9d
    title: TLA+ spec README
  - id: vendor-readme
    resource: ../raw/gbrain/vendor/README.md
    kind: code
    revision: 27f8b9d
    title: Vendoring README
  - id: native-locks
    resource: ../raw/gbrain/native/locks/README.md
    kind: code
    revision: 27f8b9d
    title: Native locks README
  - id: dbg-tmp
    resource: ../raw/gbrain/dbg-tmp.ts
    kind: code
    revision: 27f8b9d
    title: dbg-tmp.ts stray script
  - id: changelog
    resource: ../raw/gbrain/CHANGELOG.md
    kind: code
    revision: 27f8b9d
    title: GBrain changelog
---

GBrain's engineering process is heavily guard-driven: six test lanes keyed by filename, a 93-check `verify` battery, executed-test receipts, a "discrimination test" rule, generated artifacts with freshness checks, a branch-scoped four-segment version, a release gate that waits for green master, and a community-PR "fix wave" process that never merges contributor PRs as-is. Everything here is static inspection by subagent (nothing was executed) and is **Reported** by project docs unless marked Observed.[^contributing][^testing-doc][^releasing] The eval instruments that run through this machinery are in [evals and benchmarks](gbrain-evals-and-benchmarks.md).

## Test lanes and commands

Lanes by filename (Observed counts): `test/*.test.ts` (5,882), `*.serial.test.ts` (484), `*.slow.test.ts` (60), `test/e2e/*.test.ts` (870, of which 496 are Postgres/parity), `*.live.test.ts` (3, key-gated, excluded from CI) and `tests/heavy/*.sh` (ops-shape shell). `test/` totals 7,244 files / 92 MB.[^testing-doc]

| Command | Purpose | Reported time |
| --- | --- | --- |
| `bun run test` (`scripts/run-unit-parallel.sh`) | weighted parallel shards (4 default, ≤ 8 local, 10 in CI) then a serial pass | ~8 min |
| `bun run verify` (`scripts/run-verify-parallel.sh`) | guard battery: 93 `CHECKS` plus one solo guard self-test, typecheck included | ~65–85 s |
| `bun run test:full` | verify + unit + slow + smart E2E (E2E only when `DATABASE_URL` is set) | ~3–5 min |
| `bun run ci:local` / `ci:ubicloud` | full CI stack in Docker (gitleaks, 4 pgvector DBs, PgBouncer) or ephemeral VMs | ~5 min |

`bunfig.toml` installs nine preload guards (DB-URL refusal, operator-env scrub, provider-key strip, real-home guard, hermetic git, etc.). Isolation rules are formal: lint rules R1–R4 with a shrinking allowlist, a mandatory **discrimination test** (a fix-revert must fail at least one *executed* test), executed-test receipts, and `structural-suites.tsv` separating behavioral from source-shape suites.[^testing-doc][^package-json]

## CI and flake handling

23 workflows (Observed) include `test.yml`, `e2e.yml`, `persistence-validation.yml`, `convergence-nightly.yml`, `native-locks.yml`, security scans (`semgrep.yml`, `osv-scanner.yml`), `stress.yml`, `scale-tier.yml`, `tla-spec.yml`, `release.yml`, `promote-stable.yml` and fix-wave automation. PRs run a cheap tier; merge requires the full suite on the head commit. `ci-event-parity.md` enumerates ~30 event-conditional behaviors as parity or named exceptions. Labels `master-red`, `nightly-red`, `flake`, `known-red` carry response SLAs; a `flake` record expires after 14 days; targets are ≥ 95% master and ≥ 90% PR first-attempt pass.[^ci-red-runbook]

## Versioning and release

- `VERSION` is a single token, now four-segment (`0.60.593.0`); older history is three-segment. `CHANGELOG.md` has 987 `## [` entries newest-first, each with a plain-English summary and `### Itemized changes`; review-process detail and plan IDs are forbidden in entries. Two duplicate version headings (`0.19.0`, `0.38.0.0`) and one out-of-order entry exist (Observed by subagent).[^releasing][^changelog]
- Releases are never hand-rolled: `/ship` and `bun run release:restamp` merge `origin/master`, set the patch, renumber the branch's migrations and regenerate artifacts. `release.yml` publishes on every VERSION bump on master, attaches compiled binaries and force-advances `latest-stable` last; `release-gate.ts` waits (≤ 110 min) for push-to-master Test and E2E to pass. A slower `stable` channel is promoted by `promote-stable.yml` after a production-shaped soak on the exact tree.[^releasing]
- **Community PRs** are never merged as-is: maintainers fold them into a fix-wave branch, re-prove with `audit:contributors` and `wave-security-scan`, and land one PR with `Supersedes #N` and `Co-Authored-By:` trailers; `fix-wave-gate.yml` fails fork-head PRs by design (with a maintainer-override label path). The README repeats that contributors are credited in the changelog.[^releasing][^readme]

## Generated artifacts and guards

`scripts/` holds 436 files: ~94 `check-*` guards (registry `guards-manifest.tsv`, 108 lines, each `selftest=yes` guard proven able to fail via `guard-self-test.sh`), 24 `ci-*`, ~26 build/generate scripts, 13 `bench-*`, release and ops scripts, and loose one-off research scripts. `bun run regen:all` regenerates schema, migration registry, error-code and protocol blocks, tool catalog, skills manifest, CLI flag registry, plugin trees and `llms.txt`; `check:regen-all` runs inside `verify`. Weight manifests for shard balancing are drift-checked.[^testing-doc]

## Formal spec (TLA+)

`spec/tla/drain-lease/` models exactly one protocol: the managed-sync drain lease (`src/core/persistence/sync-lease.ts`), an `acquisition_token` fencing token read `FOR KEY SHARE`. Properties: `FencedTxnsMatchRow`, `OneDrainer`, `CursorMonotone`, `NoSpuriousLapse`. Every modelled guard is a **mutant**: removing it from the model must break a named property and removing it from code must fail a named test. The TLC jar is sha256-pinned; a nightly config at two overlapping lanes reached 6,420,020 states (Reported). See [sync and ingestion](gbrain-sync-and-ingestion.md) for the sync feature.[^tla-readme]

## Vendored and third-party material

- `vendor/postgres/` is upstream `postgres@3.4.9` plus a 109 KB patch (abort-aware reservation, `cancelAndDiscard`, poisoned-connection retirement, pipelining, cache and idle-buffer fixes); licensed **Unlicense**, not MIT. `vendor/update-postgres.sh --check` re-downloads, sha512-verifies, re-applies and byte-compares; it runs in `verify` as `check:vendor-postgres`.[^vendor-readme]
- `native/locks/` is a first-party C Node-API addon with 8 prebuilt `.node` binaries checked in, hash-listed in a manifest (the binaries were not audited).[^native-locks]
- `third-party/company-brain/` is MIT (schema and fictional sample only, no code).

## Repo-hygiene findings (Observed by subagent)

- Size: 260 MB working tree (`.git` 431 MB); biggest single files `CHANGELOG.md` 4.8 MB, `TODOS.md` 880 KB, `llms-full.txt` 780 KB.
- **`dbg-tmp.ts`** at the repository root is tracked, imports a hard-coded absolute path on the author's machine, has no header and no references, so it cannot run elsewhere.[^dbg-tmp]
- `admin/dist` (280 KB) is committed deliberately and guarded by `check:admin-build` and `check:admin-embedded`.
- Secret hygiene is layered (gitleaks with a history-only ignore list of explained fingerprints, privacy guards in `verify`); sealed eval outputs are listed in `.gstack/pregate.json`.
- Archaeology is kept: `docs/test-audit/` (historical, "re-verify before acting"), `docs/incidents/` (a brainstorm cost overrun of $50.71 against a $0.96 estimate; a retrieval max-pool postmortem), `docs/fix-wave-notes/`.

## Relationships

- Runs: [evals and benchmarks](gbrain-evals-and-benchmarks.md).
- Secures: [authorization and security](gbrain-authorization-and-security.md) (scanning, env trust).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Contributing" (`bun run test`, `verify`, `ci:local`; community PR waves; credit in `CHANGELOG.md`).
[^contributing]: `CONTRIBUTING.md` (lanes, discrimination test, change-kind table, "How a contributor PR lands").
[^testing-doc]: `docs/TESTING.md` "File taxonomy" (~lines 1389–1425), "Test command tiers" (~402–455), "Guard registry and self-test" (~832–900), authoring gate (~304–402); `scripts/run-verify-parallel.sh` lines 65–266; `bunfig.toml`; `docs/ci-event-parity.md`.
[^releasing]: `docs/RELEASING.md` "Release restamp", "CHANGELOG voice", release gate, "Stable channel promotion", "Community PR wave process" (~lines 708–800).
[^ci-red-runbook]: `docs/ci-red-runbook.md` (labels, flake records, health targets).
[^package-json]: `package.json` `scripts` (`test`, `verify`, `test:full`, `ci:local`, `regen:all`, `check:*`).
[^tla-readme]: `spec/tla/README.md`; `spec/tla/drain-lease/{DrainLease.tla,mutants.json}`.
[^vendor-readme]: `vendor/README.md`; `vendor/postgres/UNLICENSE`; `patches/postgres@3.4.9.patch`.
[^native-locks]: `native/locks/README.md`, `manifest.json`.
[^dbg-tmp]: `dbg-tmp.ts` (whole file, 1.6 KB).
[^changelog]: `CHANGELOG.md` head (~120 lines) and heading count (987, re-counted by the curator).
