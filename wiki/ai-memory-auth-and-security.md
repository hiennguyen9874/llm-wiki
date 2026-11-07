---
type: Concept
title: ai-memory authentication, authorization and security model
description: Loopback-by-default deployment, the bearer-token ladder, user API keys, per-project grants, admission webhooks, HTTPS posture and known security caveats of ai-memory.
tags: [agent-memory, ai-memory, security, auth, authz]
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
  - id: security
    resource: ../raw/ai-memory/SECURITY.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: SECURITY.md
  - id: users
    resource: ../raw/ai-memory/docs/users.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Multi-user attribution
  - id: security-boundaries
    resource: ../raw/ai-memory/docs/security-boundaries.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Security boundaries matrix
  - id: authz-design
    resource: ../raw/ai-memory/docs/design-per-project-authz.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Per-project authz design
  - id: admission
    resource: ../raw/ai-memory/docs/admission-webhooks.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Admission webhooks
  - id: https-proxy
    resource: ../raw/ai-memory/docs/https-via-proxy.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: HTTPS via a reverse proxy
---

# ai-memory authentication, authorization and security model

ai-memory is framed as a **single-tenant workstation/homelab service with optional multi-user attribution**, not as something to expose to the hostile internet.[^security][^users] It binds to loopback by default, mints a root bearer token into the data directory on `init`, and hardens incrementally: LAN bearer, per-user accounts, OIDC device auth for hooks, TLS via a reverse proxy.[^readme]

Evidence class: **Reported** by the project's own security docs; the doc claims were read statically by a delegated agent (**Observed** as document content, not verified behaviour). One security-boundary row is explicitly marked "not independently verified" by the project. No tests or exploits were run. `stale_after` is set because security posture changes between releases.

## Network posture

Default bind `127.0.0.1:49374`; the server fails closed before serving unauthenticated non-loopback HTTP unless `--allow-insecure-no-auth` is passed (in containers the check downgrades to a warning). `AI_MEMORY_ALLOWED_HOSTS` is a DNS-rebinding allowlist (403 on mismatch). Installs created before token-by-default, and the Docker quick-start, run without auth until `ai-memory auth enable`.[^security][^readme]

## The bearer ladder (sticky, no escalation)

1. Anonymous (no root bearer configured).
2. Static root bearer (`AI_MEMORY_AUTH_TOKEN`) — machine root.
3. Proxy-asserted user (a distinct `actor_proxy_bearer_token` plus trusted actor headers; root only for the exact configured root issuer/subject).
4. DB user `aim_` API keys (SHA-256 + `token_pepper`) — attribution, never admin.
5. Otherwise 401.[^users][^security-boundaries]

Once a deployment distinguishes operators (user rows or a proxy bearer), every `/admin/*` route — including read-only status/search/recent and `/web/pending`/`/web/health` — becomes root-only. The server never validates OIDC tokens itself; `auth login oidc-device` stores a token for an external gateway.[^security-boundaries][^security]

## Browser sessions

Dual auth on protected routes: `ai_memory_session` cookie with `X-CSRF-Token`, or `Authorization: Bearer`; bearer beats cookies and an invalid bearer fails closed. Human login beyond loopback requires an HTTPS posture; `serve --allow-insecure-human-auth` is the explicit LAN escape hatch. TLS is delegated to a reverse proxy (Caddy/nginx/Cloudflare Tunnel templates), with `AI_MEMORY_AUTH__SECURE_COOKIE=true` as the operator signal.[^users][^https-proxy][^security]

## Per-project authorization

Project `access_mode` is `open` or `restricted`; `project_grants` hold `read`/`write` grants; entry is granted to root, the creator and grantees through one choke point (`authorize_project`). Unscoped reads filter in SQL before `LIMIT`; captures into unwritable projects are dropped and counted; grant management is root-only and audited. Slices 2–3 of the design landed; the design doc retains superseded "not implemented" text below its banner.[^authz-design][^security]
**Caveat (documented):** proxy-asserted users have no `UserId` to key a grant on, so they bypass `restricted` grants.[^security][^users]

## Admission webhooks

Operators can configure an HTTP chain consulted in `Wiki::write_page` before the atomic write; webhooks may mutate frontmatter/body (re-sanitized) or reject, for ops including `write_page`, `consolidate`, `delete`, `purge_*` and `move_project`, plus non-blocking observers after durability. Webhook payloads (path, frontmatter, full body) leave the process and are not sanitized by ai-memory.[^admission]

## Other hardening notes

Body size caps; symlink/reparse-point refusal in wiki roots; DB triggers that reject cross-project links; login endpoints reject preflight-free bodies; every attributed write lands in an `audit_log`. A fixed advisory (GHSA-w734-2f7h-6qcp) concerned `restore` bringing back wiki-git hooks/config.[^security][^security-boundaries]

## Relationships

- Data flow, retention and egress: [Data handling and lifecycle ops](ai-memory-data-handling-and-lifecycle-ops.md).
- Sanitizer: [Capture and hooks](ai-memory-capture-and-hooks.md). Surfaces protected: [MCP tools and HTTP surfaces](ai-memory-mcp-tools-and-http-surfaces.md).
- Stale wording in `docs/users.md` ("does not implement RBAC") vs per-project grants: [Source map and discrepancies](ai-memory-source-map-and-doc-discrepancies.md).

[^readme]: `../raw/ai-memory/README.md` — "Security" section; Docker quick-start no-auth note.
[^security]: `../raw/ai-memory/SECURITY.md` — "Threat model", "Network exposure…", "Authentication…", per-project restricted modes, assistant-capture notes.
[^users]: `../raw/ai-memory/docs/users.md` — "The four resolution rungs", human login, trusted proxy, ownership; "Multi-user attribution".
[^security-boundaries]: `../raw/ai-memory/docs/security-boundaries.md` — rows 0a–3j (admin gating, `aim_` keys); row 3a states its regression test is "not independently verified here".
[^authz-design]: `../raw/ai-memory/docs/design-per-project-authz.md` — landed-slices banner; code: `crates/ai-memory-store/src/project_authz.rs::authorize_project`, migrations V68/V69.
[^admission]: `../raw/ai-memory/docs/admission-webhooks.md` — operations list, chain semantics; code `crates/ai-memory-wiki/src/admission.rs`.
[^https-proxy]: `../raw/ai-memory/docs/https-via-proxy.md` — TLS templates and failure modes.
