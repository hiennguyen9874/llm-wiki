---
type: Concept
title: LightRAG authentication and security boundaries
description: Open-by-default deployment, shared API/JWT authorization, Ollama whitelist exposure, redacted credential findings, and static-review limits.
tags: [security, operations, authentication]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:15:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
---

**Observed:** LightRAG supports open/guest, API-key and account/JWT modes through shared route dependencies, but ships a network bind and unauthenticated configuration by default. The default whitelist leaves Ollama-compatible routes open even when other authentication is enabled. **Synthesis:** this snapshot is not a per-user document-permission system; network, whitelist and deployment isolation choices define consequential trust boundaries.[^lightrag-aaebfe1]

## Redacted source finding and human decision

**Observed by the operations reviewer:** tracked `env.docker-compose-full` contains non-placeholder-shaped LLM/provider and embedding/rerank service keys, alongside database/object-store credential defaults. **Unverified:** whether the provider/service keys remain valid or were live at commit time. An associated deployment endpoint also made the disclosure boundary unclear; neither endpoint nor secret values are reproduced. The initial narrow prefix-based screen missed this class of credential.[^lightrag-aaebfe1]

Compilation paused, unfinished canonical drafts were removed, and the human authorized continuing with redacted code-grounded findings. The source remains unchanged. **Limit:** permission to compile is not evidence of rotation, revocation, public-disclosure clearance for values, or deployment safety. Remediation remains the human's decision. The coverage ledger records the file as sensitive/redacted rather than an ordinary sample ready to reuse.[^lightrag-aaebfe1]

## Authentication and authorization

**Observed:** combined auth resolves whitelist first, then bearer, then API key. API keys use `X-API-Key`; accounts can use bcrypt-marked passwords or plaintext comparisons with defensive timing work. Account mode requires an explicit non-default token secret: `validate_auth_configuration`, called by argument parsing/config initialization, rejects an empty secret or the exact built-in default. JWT validation rejects none-algorithm, invalid/missing expiry and oversized subject; issuer/audience/revocation are not checked in the inspected handler. Logout is client-side.[^lightrag-aaebfe1]

**Observed:** configured accounts receive user role, and protected document/graph routes share credential acceptance rather than per-object ownership checks. The inspected API does not implement per-user/per-document workspace authorization. Workspace selection is primarily deployment-level storage configuration, not a request tenant switch. Guest tokens do not substitute for an API key in API-key-only mode; old documentation describing that access conflicts with current code/assertions.[^lightrag-aaebfe1]

**Observed:** login limiting defaults to five failures over 300 seconds in process-local state keyed by IP and username. Bcrypt runs off-loop; forwarded client-IP headers are not blindly trusted. **Observed from the limiter's module contract:** direct uvicorn runs use one worker, while independent Gunicorn worker counters can multiply the effective limit by worker count; the source advises shared state for stronger coordination. **Limit:** that documented multi-worker behavior and deployment-proxy effects were not execution-verified.[^lightrag-aaebfe1]

## Exposure defaults

| Setting/surface | Observed boundary |
| --- | --- |
| Host / auth | `0.0.0.0`, auth unconfigured; warning rather than unconditional startup refusal |
| Whitelist | `/health,/api/*`; explicitly removing `/api/*` is necessary to protect Ollama routes |
| Health | Anonymous payload reduced to liveness when whitelisted; removing health from whitelist changes reachability |
| `/auth/verify` | Enforced credential check ignoring whitelist; preferable to health as an API-key probe |
| UI / docs / customization | Public mounts/routes; docs configurable; UI visibility is not API authorization |
| CORS | Wildcard default; explicit origins enable credentialed CORS behavior |

**Observed:** token renewal can attach `X-New-Token`; browser localStorage holds JWT/API-key state. Client expiry checks are not signature verification. Chat/customization sanitizers reduce selected rendering risks, not a complete XSS or credential-theft audit.[^lightrag-aaebfe1]

## Operational security limits

- **Observed:** `setup.sh::security_check_env_file` compares a shortened default token-secret spelling, while `lib/validation.sh` and the configured constant use the full spelling; the sample-secret case can evade that specific audit check. This does not establish failure of the separate startup configuration validator.
- **Observed:** runtime dependency installers can contact package services at startup/import; Docker build context exclusions do not exclude the flagged compose environment sample. No secret-bearing values were copied into compiled artifacts.
- **Observed:** image entrypoint drops privileges, but inspected Helm defaults do not assert a pod security context. The chart is not a general read-only-replica enforcement mechanism.
- **Reported:** `SECURITY.md` directs reports to GitHub advisories but lists support for 1.3.x, not an up-to-date verified support statement for every current package release.[^lightrag-aaebfe1]

## Relationships

- **Constrains:** [API/UI](lightrag-api-ui.md), [storage workspace isolation](lightrag-storage.md), and [deployment](lightrag-deployment.md).
- **Related:** [Multimodal image containment](lightrag-parsing-multimodal.md) is a specific sink control, not full parser-service security.
- **Related:** [Deletion/recovery](lightrag-deletion.md) performs destructive operations reachable through the shared auth plane.

## Evidence limits

Static review, not penetration testing, secret-validity checking, complete PII scanning, token revocation testing or proof of safe deployment. Secret defaults, hypotheses and reviewer findings are redacted. See [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`: `env.docker-compose-full::{LLM_BINDING_API_KEY, EMBEDDING_BINDING_API_KEY, RERANK_BINDING_API_KEY, VLLM_EMBED_API_KEY, VLLM_RERANK_API_KEY}` (values withheld); `env.example` auth/OpenSearch default settings (values withheld); `api/config.py::DEFAULT_TOKEN_SECRET, validate_auth_configuration, parse_args, initialize_config`; `api/auth.py::AuthHandler`; `api/utils_api.py::get_combined_auth_dependency, credentials_accepted, path_is_whitelisted, _renew_token_if_needed`; `api/login_rate_limit.py::LoginRateLimiter`; `api/passwords.py::verify_password`; `api/lightrag_server.py::create_app` login/health/auth/verify handlers; document/graph route auth dependencies; `scripts/setup/setup.sh::security_check_env_file`; `scripts/setup/lib/validation.sh` default-secret check (506); `.dockerignore` environment exclusions; `Dockerfile`, `docker-entrypoint.sh`; Helm `templates/_helpers.tpl`; `SECURITY.md`; `tests/api/auth/test_shared_credential_check.py` and `tests/api/config/test_whitelist_exposes_api_routes.py` selected assertions. Session approval/rotation limits are operational history, not an upstream claim.
