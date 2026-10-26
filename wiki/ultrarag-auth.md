---
type: Concept
title: UltraRAG authentication and access control
description: Route-level UI authorization, anonymous default tenancy, SQLite ownership, and knowledge-base visibility.
tags: [ml, ultrarag, authentication, authorization]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e2032d9f134099405b8b483edbbad95274080
    title: UltraRAG repository
---

**Observed:** UltraRAG UI uses Flask cookie sessions and SQLite users, with authorization implemented per route rather than by a global login gate. Anonymous callers become the `default` user for many operations. Having an account system therefore does not imply that the application requires login for resource use or administration-adjacent actions.[^ultrarag]

## Identity and session model

Usernames follow `^[A-Za-z][A-Za-z0-9_]{2,31}$`; `default` is reserved, and minimum password length is six. Werkzeug hashes/verifies passwords. Registration is open and logs in the new user. The session stores `auth_user_id`; admin checks use the reserved admin username, not merely the `ADMIN_MODE` configuration flag.[^ultrarag]

Cookies are HttpOnly and SameSite=Lax; Secure is opt-in through `ULTRARAG_SESSION_COOKIE_SECURE`. The signing secret comes from `ULTRARAG_SESSION_SECRET` with a fixed development fallback. Initialization creates a built-in administrator using a fixed default password. These are source-code defaults, not credentials discovered in a deployed instance; their literal values are intentionally not copied here.[^ultrarag]

## Access matrix

| Gate | Representative operations |
| --- | --- |
| Admin | Pipeline creation/save, raw YAML save/parse, delete, rename, parameter save, build |
| Login | Password/nickname/model-settings changes; saved-chat mutations; knowledge-base visibility management |
| No global login requirement; often `default` identity | Pipeline chat/demo start-stop, prompt CRUD, memory read/write, KB config/upload/build-task paths, AI-helper calls, system shutdown |

This matrix summarizes gates observed in `app.py`, not an assertion that every operation is unrestricted internally: collection access, names, filesystem paths, and other conditions can impose further checks. In particular, listing saved chats anonymously returns an empty list, while saved-chat ownership is enforced within the SQLite store.[^ultrarag]

## Knowledge-base visibility versus retrieval isolation

The visibility store records owner, public/private state, and optional allowed users. View permission is public-or-owner-or-listed; management is owner-only. Collection deletion checks management/admin permissions. Legacy mappings are initialized private to admin despite the helper name `bootstrap_legacy_public`; newly indexed collections are private to their owner. Unmapped collections are filtered from visibility listings.[^ultrarag]

**Synthesis:** UI metadata ACLs and backend index isolation are distinct. A protected saved-chat row or visibility mapping does not prove that every runtime session, shared pipeline file, or underlying FAISS index has a matching tenant boundary. Project-memory retrieval is particularly backend-dependent; FAISS ignores the collection argument.[^ultrarag]

## Evidence and limits

These are **observed static checks**, not reproduced authorization tests. No login, cookie forgery, cross-user request, or exploit was attempted. The supplied CI/tests do not cover these UI auth paths. See [security](ultrarag-security.md) for deployment consequences and [coverage](ultrarag-source-map.md) for the inspection boundary.[^ultrarag]

## Relationships

- **Part of:** [UI architecture](ultrarag-ui.md), not a general authorization layer for every MCP tool.
- **Constrained by:** [deployment security defaults](ultrarag-security.md).
- **Depends on:** [retrieval backend semantics](ultrarag-retrieval.md) for data isolation beyond UI metadata.

[^ultrarag]: Revision `185e2032d9f134099405b8b483edbbad95274080`: `ui/backend/auth.py` username/password constants, `SQLiteUserStore.init_db`, `_ensure_default_admin_user`, password hashing and model-setting methods; `ui/backend/app.py::create_app`, `_get_authenticated_user_id`, `get_current_user_id`, `require_admin_user`, auth/chat/pipeline/KB/prompt/memory/AI/shutdown routes; `ui/backend/chat_store.py::_ensure_owner`; `ui/backend/kb_visibility_store.py::bootstrap_legacy_public`, `can_view`, `can_manage`, `filter_viewable_collections`; `servers/retriever/src/index_backends/faiss_backend.py::search`; `.github/workflows/ci-smoke.yml` test commands and `tests/` inventory. No runtime security verification.
