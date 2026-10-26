---
type: Concept
title: "OpenRAG authentication and security boundaries"
description: "Identity planes, opt-in RBAC, OpenSearch document access, delegated tokens, and configuration-dependent security risks."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:03:52Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10ee3d0dedc842d244ec2b63fd9791
    title: OpenRAG repository
---

**Observed:** OpenRAG separates authentication, optional RBAC, document-level OpenSearch access, and service-to-service delegation. Authentication alone does not imply fine-grained authorization: `OPENRAG_RBAC_ENFORCE` defaults false, and the permission gate returns an authenticated user without checking permissions when disabled.[^openrag-repo]

## Identity and document access

- Browser routes use sessions; public routes accept API keys or gateway-forwarded identity. External `user_id` is distinct from SQL `db_user_id`, which ownership checks use.
- **Reported by documentation:** without Google OAuth, users share anonymous document access; Google credentials enable per-user OAuth mode. Microsoft/AWS connector credentials do not enable OpenRAG login.
- **Observed:** security roles combine ownership/email/owner-less-document access with ACL-based access using `allowed_users` and principal lookup records. Both roles map to the `openrag_user` backend role. SQL permissions and OpenSearch DLS are different layers.
- DLS principal refresh failures are warned about rather than always failing the request. **Unverified:** effective access under upstream/group-refresh failures was not exercised.[^openrag-repo]

## Delegation and credentials

API keys have an `orag_` prefix and cryptographically random material; the active service stores an HMAC-SHA256 digest keyed by `SESSION_SECRET`, accepting legacy SHA256 hashes during lookup. Do not copy keys or shipped credential defaults into wiki notes.[^openrag-repo]

The standard OpenRAG LLM/embedding components use backend OpenAI-compatible endpoints with short-lived hop tokens. Provider headers alias the hop token into compatibility variables rather than forwarding vendor keys on that normal path. **Important exceptions:** Docling VLM options contain real provider credentials or an exchanged IAM token, so Docling Serve is inside that credential trust boundary; IBM OpenSearch header construction also has a username/password compatibility path. Decrypted provider keys may be copied to backend process environment variables. “Vendor keys never leave the backend” is therefore not a valid system-wide claim.[^openrag-repo]

Ingestion callbacks use a separate per-run token and run-ID validation; a narrow router listener is not a replacement for those checks. See [ingestion](openrag-document-ingestion.md).[^openrag-repo]

## Deployment-sensitive risks

| Observed mechanism | Consequence / operational interpretation |
| --- | --- |
| Gateway JWT claims decode without signature verification by default | Edge must authenticate and strip client-supplied trusted identity headers; direct backend exposure changes the trust model |
| Optional issuer verification has no issuer allowlist and defaults issuer TLS verification off | Enabling the flag alone is not evidence of a fully hardened verifier |
| Predictable session-secret fallback; shipped OpenSearch admin placeholder/default artifacts | Supply deployment-specific secrets; do not infer secure credentials from successful startup |
| `encrypt_secret` returns unchanged plaintext without `OPENRAG_ENCRYPTION_KEY` | Encryption is conditional; startup enforcement is separately controlled by `OPENRAG_ENFORCE_PREREQUISITES` |
| OSS OpenSearch client uses TLS with certificate verification disabled | Encryption-in-transit is not authenticated server identity |
| Webhook routes are registered without session authentication; inspected handlers show no generic signature gate | Treat webhook exposure as a separate boundary; provider-specific validation is not exhaustively audited |

These are static findings and **Synthesis** implications, not demonstrated exploits. No penetration tests, live keys, or deployed configuration were inspected.[^openrag-repo]

## Relationships

- Governs [public API](openrag-public-api.md), [MCP](openrag-mcp.md), and [connector ACL propagation](openrag-connectors.md).
- Depends on [backend architecture](openrag-backend-architecture.md) for SQL ownership and single-process caching.
- Constrains [deployment](openrag-deployment.md); UI permission visibility in the [frontend](openrag-frontend.md) is not enforcement.

## Coverage limits

Static checks did not establish end-to-end DLS behavior, every webhook provider's validation, JWT issuer safety, key rotation, or all RBAC route coverage. Limited credential-pattern screening found no likely live credentials; that is not a comprehensive secret audit. See [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d3ec10ee3d0dedc842d244ec2b63fd9791`: `src/services/rbac_service.py::is_rbac_enforced`; `src/auth/permission_dependencies.py::enforce_permission`; `src/auth/request_identity.py::{_attach_db_user_id,_attach_opensearch_jwt}`; `src/services/api_key_service.py::{_hash_key,_candidate_hashes}`; `src/config/settings.py::{get_api_jwt_header,get_jwt_verify_signature,AppClients.initialize}`; `src/config/utils.py::{resolve_jwt_claims,verify_jwt_from_issuer}`; `src/utils/{encryption,langflow_headers}.py::{encrypt_secret,add_provider_credentials_to_headers,build_ibm_opensearch_vars}`; `src/services/docling_service.py::picture_description_api` construction; `src/services/langflow_llm_token_service.py`; `securityconfig/{roles,roles_mapping,internal_users}.yml`; `src/api/{connectors,knowledge_filter}.py` webhook handlers; `docs/docs/_partial-opensearch-auth-modes.mdx`; `docker-compose.yml::SESSION_SECRET`.
