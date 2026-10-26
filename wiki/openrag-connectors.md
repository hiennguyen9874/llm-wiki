---
type: Concept
title: "OpenRAG connectors and ACL propagation"
description: "Connector registry, OAuth versus login, workspace access policy, indexed ACLs, and the limits of inspected synchronization behavior."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10ee3d0dedc842d244ec2b63fd9791
    title: OpenRAG repository
---

**Observed:** OpenRAG discovers document-source connectors through a registry and routes their content through common ingestion metadata and ACL structures. **Reported:** standard documentation offers Google Drive, OneDrive, SharePoint, and AWS S3; additional source packages can extend the registry. Connector credentials, application login, workspace connector policy, and document access are different concerns.[^openrag-repo]

## Source and identity boundaries

Google OAuth credentials serve both Google Drive authorization and OpenRAG OAuth login; Microsoft credentials authorize OneDrive/SharePoint but do not add Microsoft login, and AWS uses access credentials rather than making S3 an OAuth identity provider. The documentation's general instruction to register an OAuth app for every provider is therefore broader than its own AWS credential instructions.[^openrag-repo]

The optional `enhancements` package adds connector/provider implementations, including Azure Blob and IBM COS. The registry extension points were inspected; all enhancement implementation bodies were not. Do not infer deployed availability from package directories alone.[^openrag-repo]

## Control flow and policy

- `ConnectorService` owns the connection manager; startup loads persisted connections conditionally and schedules subscription renewal, while shutdown attempts subscription cleanup.
- Connector-specific routes register before generic parameterized connector routes, avoiding route shadowing.
- Workspace `connector_access` policy defaults access to true for registry-derived types and applies only when its enforcement flag is active. Checks appear in authorization initiation and webhook handling. This is distinct from RBAC permission checks.
- **Reported:** a configured webhook base URL enables provider callbacks for automatic ingestion; explicit Sync can enqueue many files and time out. No exactly-once or deletion-propagation guarantee was established.[^openrag-repo]

## ACL representation

`DocumentACL` carries owner, allowed users/groups/principals, and labels. Ingestion serializes this metadata into runtime headers and indexed chunks. OpenSearch roles combine ownership with principal lookups; group lookup and DLS-principal caches are process-local and refreshed on request/TTL paths. **Synthesis:** source permissions can only affect retrieval if conversion, indexing, refresh, and query enforcement all agree; checking the source connector UI alone is insufficient.[^openrag-repo]

## Relationships

- Supplies content and ACLs to [document ingestion](openrag-document-ingestion.md).
- Depends on [authentication/security](openrag-auth-security.md) for DLS, gateway identity, and webhook exposure.
- Uses [backend persistence](openrag-backend-architecture.md) for connector policy and legacy connection state.

## Coverage limits

Connector modules were inspected selectively, not end-to-end. Delta/ETag change detection, provider ACL translation, webhook validation/renewal failures, token persistence, concurrent sync, and remote-deletion handling remain pending. No cloud accounts or network calls were used. See [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d3ec10ee3d0dedc842d244ec2b63fd9791`: `src/connectors/{registry,base,service}.py::{get_connector_classes,DocumentACL,ConnectorService}`; `src/connectors/{google_drive,onedrive,sharepoint,aws_s3}/connector.py`; `src/services/connector_access_service.py::{CONNECTOR_ACCESS_SECTION,get_access_map,is_connector_access_policy_enforced}`; `src/services/{group_acl_service,dls_principal_service}.py`; `src/app/{container,lifespan}.py::{_should_load_persisted_connections,cleanup_subscriptions_proper}`; `src/app/routes/internal.py` connector registration order; `src/api/auth.py::auth_init`; `src/api/connectors.py::_connector_access_denied`; `src/services/langflow_file_service.py::run_ingestion_flow`; `securityconfig/roles.yml`; `docs/docs/core-components/knowledge-connectors.mdx`; `docs/docs/_partial-oauth-credentials.mdx`.
