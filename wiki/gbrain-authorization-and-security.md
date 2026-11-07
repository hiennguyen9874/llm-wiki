---
type: Concept
title: GBrain authorization and security model
description: GBrain's OAuth and token model, scopes and grants, the checks run per request, what does and does not confine callers, and its install, environment and hook trust boundaries.
tags: [agent-memory, gbrain, security, authorization, oauth]
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
  - id: security-md
    resource: ../raw/gbrain/SECURITY.md
    kind: code
    revision: 27f8b9d
    title: GBrain security policy and trust model
  - id: scope-ts
    resource: ../raw/gbrain/src/core/scope.ts
    kind: code
    revision: 27f8b9d
    title: Auth scopes
  - id: grants-model
    resource: ../raw/gbrain/src/core/grants/model.ts
    kind: code
    revision: 27f8b9d
    title: Grant model
  - id: dispatch-ts
    resource: ../raw/gbrain/src/mcp/dispatch.ts
    kind: code
    revision: 27f8b9d
    title: MCP dispatch
  - id: private-visibility
    resource: ../raw/gbrain/src/core/search/private-visibility.ts
    kind: code
    revision: 27f8b9d
    title: Private-page visibility policy
  - id: mcp-admin
    resource: ../raw/gbrain/docs/mcp/ADMIN.md
    kind: code
    revision: 27f8b9d
    title: MCP administration guide
  - id: rls-guide
    resource: ../raw/gbrain/docs/guides/rls-and-you.md
    kind: code
    revision: 27f8b9d
    title: RLS and you
  - id: brains-and-sources
    resource: ../raw/gbrain/docs/architecture/brains-and-sources.md
    kind: code
    revision: 27f8b9d
    title: Brains and sources
---

GBrain authorizes remote callers with OAuth 2.1 clients and hashed bearer tokens, narrowed by ten scopes and a per-credential **grant** (source set, operation snapshot, private-page and takes-holder rules, budgets). The project is unusually candid that this confines *authenticated remote clients* only: direct database reachability, local files, token-less stdio and some opt-in escape hatches are different trust boundaries. The README says the authorization tests "exercise specific access paths, not a universal no-leak guarantee".[^readme][^security-md] Transport and surface details are in [CLI and MCP surface](gbrain-cli-and-mcp-surface.md); data-level privacy is in [memory trust and egress](gbrain-memory-trust-and-egress.md).

## Credentials and scopes

- **Scopes (Observed, 10):** `read`, `write`, `admin`, `sources_admin`, `users_admin`, `agent`, `skill_editor`, `skill_publisher`, `skills_member_self`, `memory_confirm` (the last is local-CLI-only). `admin` ⊃ `sources_admin|users_admin|write|read`; `write` and `read` are sibling axes. Dynamic client registration is capped at `read write`; insecure DCR machine clients at `read`.[^scope-ts]
- **Tokens and clients (Observed by subagent):** legacy bearer tokens are stored as SHA-256 hashes with plaintext shown once; OAuth clients live in `oauth_clients`. `/authorize` never mints a code itself: it records a pending request, sends the browser to the owner dashboard and only owner approval mints a code bound to client, redirect URI and S256 PKCE. Access-token lifetime is capped at 90 days.[^grants-model]
- **Owner credential:** a separate secret (`GBRAIN_ADMIN_BOOTSTRAP_TOKEN` or a 0600 token file) logs into `/admin` (24 h cookie, single-use five-minute login links). An OAuth token, client secret or MCP `admin` scope **cannot** administer the server.[^mcp-admin]
- **Grants:** one shape for tokens and clients — `scopes`, `source_grant` ∈ default/scalar/federated/none, write source, federated read set, `takes_holders`, `private_pages`, `bound_slug_prefixes`, `allowed_operations` (NULL = all, including future), bound tool/source/brain, daily USD budget, concurrency, `surface`, TTL, plus delegation (`may_act_for`) and attestation fields. Named profiles: `memory-reader`, `memory-writer`, `coding-agent`, `operator`, `delegating-agent`, `full`. Edits are optimistic (`--if-version`) and audited; `gbrain access check` prints the resolved view.[^grants-model][^mcp-admin]

## Per-request authorization order (Observed)

1. `localOnly` transport backstop (locality axis, not trust axis); 2. `operationScopesAllowed`; 3. `enforceBoundClientOpAllowList` (slug-bound clients get only a fenced write allow-list); 4. `enforceReadTrustFloor`; 5. `remoteCallerAccess` (member readers, folder rules, audience); 6. the handler's own source-scope ladder.[^dispatch-ts]

## Visibility rules

Local callers (`ctx.remote === false`) see everything. Remote callers do not see private pages unless `GBRAIN_REMOTE_PRIVATE_PAGES=1`, `search.remote_private_pages=visible`, or the credential holds `--private-pages granted-sources` (only inside its named sources). Derived atoms/concepts and `type: question` pages default private. Frontmatter `readable_by` and folder rules are enforced additionally and are not relaxed by those hatches. Remote facts are `world`-only; takes are filtered by `takes_holders`; third-party and transcript text is returned quoted over MCP.[^private-visibility][^brains-and-sources]

## What does and does not confine callers

| Confines (Observed/Reported) | Does **not** confine |
| --- | --- |
| Source isolation (federated > scalar > none, fail-closed); facts visibility; takes holders; private-page filter; `readable_by` and folder rules; audience header intersection; scopes; operation snapshots; surface ceiling; slug/brain/source bindings; rate limits and body cap; DCR off plus owner approval plus PKCE; audit log with redacted params | Direct Postgres reachability (a co-located container on Docker's default bridge can read every source with no token); stdio (token-less, bound only by config); the private-page escape hatches; `granted-sources` opt-in; legacy tokens with NULL scopes (full access; `doctor` warns `legacy_token_null_scope`); tunnel-fronted deployments where per-IP limiting collapses to one IP; trust in Tailscale ACLs for tailnet-only publishing |

Remote soft-delete is restorable for 72 h; only the local CLI can purge.[^security-md][^brains-and-sources]

## RLS

Row-level security is not GBrain's authorization boundary: the service role holds `BYPASSRLS`, so RLS exists to deny a Supabase anon key. An event trigger enables RLS on new tables, and `gbrain doctor` fails when the schema is anon-reachable (warns otherwise). The doctor check body was not read, so severity details are Reported.[^rls-guide]

## Install, environment and hook trust (Reported in `SECURITY.md`)

- **Install path:** release binaries carry GitHub artifact attestations; `gbrain upgrade` (darwin-arm64, linux-x64) verifies the download's SHA-256 against an attestation fetched from a different origin and checks the builder id, fail-closed with a downgrade-replay guard. It does **not** verify Sigstore (Fulcio/Rekor). From-source and force-moved-tag installs are trust-on-first-use.
- **Env boundary:** a cwd `.env` is untrusted; code-loading, exec-target, DB-URL, posture-widening and `LD_*`/`GIT_*`/`BUN_*`/`NODE_OPTIONS`/proxy key families are denied and gbrain re-execs from an empty temp directory.
- **Hooks:** every hook and the stdio registration start via a pinned hook launcher; hooks are fail-open (exit 0) with a counters-only heartbeat and a `GBRAIN_HOOKS=0` kill switch.
- **Defaults:** loopback bind; CORS default-deny; 30 req/60 s pre-auth per IP and 60 req/60 s per token; 1 MiB body cap; audit params redacted unless `--log-full-params`; Gitleaks, OSV-Scanner, Semgrep CE and actionlint in CI.[^security-md]

## Relationships

- Depends on: [CLI and MCP surface](gbrain-cli-and-mcp-surface.md) (dispatch), [data model](gbrain-data-model-and-system-of-record.md) (sources, visibility).
- Related: [memory trust and egress](gbrain-memory-trust-and-egress.md), [testing, CI and release](gbrain-testing-ci-and-release.md) (security scanning).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` paragraph "It works as a company brain too."
[^security-md]: `SECURITY.md` "Install-path trust model", "Environment variables and cwd `.env` files", "Docker network isolation", "CORS", "Rate limiting", "Body size cap", "Audit log", "Remote MCP Security".
[^scope-ts]: `src/core/scope.ts` lines 18–90 (`Scope` type at line 25, `DCR_REGISTRABLE_SCOPES` at line 65; curator read lines 25–72).
[^grants-model]: `src/core/grants/model.ts` lines 6–47, 155–160 (profiles, TTL cap).
[^dispatch-ts]: `src/mcp/dispatch.ts` lines 973–1000, 1098–1110, 1225–1244.
[^private-visibility]: `src/core/search/private-visibility.ts` lines 1–22, 759.
[^mcp-admin]: `docs/mcp/ADMIN.md` "Identify your authority", "Legacy token grants", "Access-token lifetime"; `src/commands/serve-http-admin-api.ts:184–213`.
[^rls-guide]: `docs/guides/rls-and-you.md`.
[^brains-and-sources]: `docs/architecture/brains-and-sources.md` section "What confines remote callers, and what does not" (lines ~345–376); `docs/tutorials/company-brain.md` line ~133.
