---
type: Concept
title: WeKnora authentication and security boundaries
description: Workspace RBAC, scoped machine principals, tenant selection, outbound filtering, and deployment-dependent trust limits.
tags: [ml, weknora, security, authorization]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T16:19:21Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora combines workspace membership/RBAC for human users with a separate route-policy authority for API-key principals. **Observed:** authentication, tenant resolution, resource ownership, outbound networking, and separately authenticated integration routes are distinct boundaries. Their presence is not proof of complete route coverage or a penetration-test result.[^weknora]

## Identity, workspace, and authorization

The global auth middleware supports Bearer JWT and `X-API-Key`, with designated public and tenant-optional routes. Tenant selection considers an explicit tenant header, token context, and active membership; a tenant-scoped key cannot widen itself to another workspace by changing the header. Platform keys need an explicit target workspace.[^weknora]

**Observed:** RBAC uses Owner, Admin, Contributor, and Viewer roles, plus resource ownership checks. Missing roles fall back to Viewer. Cross-tenant superuser behavior requires both a user attribute and the cluster configuration flag. System-admin checks are always enforced, while ordinary role/ownership enforcement has an explicit rollout switch: disabling it logs warnings and permits paths that would otherwise be denied. The code default in `TenantConfig.IsRBACEnforced` enables enforcement when the tenant setting is unspecified. A different edge exists in the middleware helper: an entirely nil `*Config` disables ordinary RBAC enforcement. This distinction was inspected statically; normal bootstrap and every test wiring path were not exercised.[^weknora]

The machine-principal policy registry keys rules by method and router path; absent policies deny API-key access. Capability checks do not widen a key's KB scope. **Coverage limit:** engine-level and independently mounted routes need their own explicit guards; this pass did not audit every route registration.[^weknora]

## Defaults and outbound access

**Observed:** default registration mode is self-serve, default post-registration behavior creates a personal workspace, and self-service workspace creation is enabled. Login authentication therefore does not imply invitation-only access. Production posture must be chosen deliberately; the README recommends private networks and controlled exposure.[^weknora]

Outbound utilities support restricted-IP classification, host allowlisting, and optional whitelist-only mode; an invalid nonboolean whitelist-only value fails closed by enabling lockdown. Lockdown requires configuring legitimate dependency hosts or external models/connectors can stop working. Full DNS-rebinding, redirect, storage URL, and provider-specific validation coverage remains pending.[^weknora]

Docker socket access is host-root-equivalent and the Docker sandbox backend is opt-in. Lite auto-setup checks both edition and a desktop token; “registration-free Lite” should not be interpreted as unrestricted remote anonymous access. Persistent secrets and encryption failure modes are detailed in [configuration](weknora-configuration.md).[^weknora]

## Relationships

- Applies to [domain persistence](weknora-persistence.md) and [agent/sandbox execution](weknora-skills-sandboxes.md).
- [MCP servers](weknora-mcp-servers.md) and [embed/IM channels](weknora-publishing-channels.md) have additional authentication surfaces before the global middleware.
- Depends on deliberate [deployment topology](weknora-deployment.md).
- Complements the [model-facing citation/source boundary](weknora-citations-source-boundary.md): existing untrusted-data instructions do not replace tool authorization.
- Informs the [fork roadmap](weknora-fork-roadmap.md), including proposed source-ACL checks for derived wiki, graph, cache and conversation surfaces.

## Coverage and trust limits

Selected middleware, policy, config, outbound-classification, and Lite setup sections were inspected. OIDC end-to-end, all route guards, adapter callbacks, storage access, sandbox enforcement, rate limits, credential logging, and full tenant isolation remain pending. No exploit, auth request, or integration test ran. No likely live credentials were identified in inspected inputs; this is not a whole-repository secret audit. `SECURITY.md` asks for private vulnerability reporting.[^weknora]

[^weknora]: Snapshot `fd7a2586fd58`: `internal/middleware/auth.go::Auth`, `resolveTargetTenant`, `authenticateAPIKeyRequest`, `resolveTenantRole`; `middleware/access.go::IsCrossTenantSuperuser`, `IsTenantAccessible`; `middleware/rbac.go::RequireRole`, `RequireSystemAdmin`, `RequireOwnershipOrRole`, `rbacEnforcementEnabled`; `middleware/api_key_gate.go::APIKeyRouteAuthorizer`, `authorize`, `DenyAPIKeyPrincipal`; `internal/config/config.go::applyAuthAndTenantDefaults`, `TenantConfig.IsRBACEnforced`; `internal/utils/security.go::SSRFWhitelistOnlyEnabled`, `CheckSSRFWhitelistOnly`, `CheckDialWhitelistOnly`; `internal/ipclass/ipclass.go` class declarations; `internal/sandbox/docker_enabled.go`; `internal/handler/auth.go::AutoSetup`; `docker-compose.yml` app socket warning; `SECURITY.md`, “Reporting a Vulnerability.” Package entry: [README](../raw/WeKnora/README.md), deployment warning and “Access and security.”
