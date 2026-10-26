---
type: Concept
title: "RAGFlow security and disclosure limits"
description: "Redacted committed-key finding, credential-default risks, authentication surfaces, and limits of the static security review."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54
    title: RAGFlow repository snapshot
---

# RAGFlow security and disclosure limits

**Observed:** the source includes a tracked private-key file and a loader with an embedded decryption passphrase. The human authorized continuing the ingest after this finding was disclosed; this does **not** establish that the key is a harmless fixture, unused, or safe for deployment. This wiki records only the minimum useful description and resolvable provenance, never key material or credential values.[^ragflow]

## Committed-key finding

`internal/common/password.go::LoadPrivateKey` reads `conf/private.pem`, decodes PEM, handles an encrypted block with an embedded passphrase, and parses an RSA private key. The adjacent password-decryption code uses RSA PKCS#1 v1.5 and returns the original input on decryption failure. **Synthesis:** the public source's encryption wrapper is not a deployment-specific secret boundary when the key and unlocking material travel together. Whether live systems rely on it remains unknown; remediation/rotation belongs to the human.[^ragflow]

## Configuration and runtime trust surfaces

- Populated infrastructure credential defaults exist in configuration and config constructors. Override and isolate them for deployment; no values are reproduced.
- Router groups distinguish public, beta-token and session-authenticated routes; public agent webhook registration is an intentional unauthenticated surface.
- Agent workflows can invoke code/browser/network tools. Registry presence does not prove sandbox isolation, safe egress, or appropriate tenant authorization.
- The API server sets transport timeouts and proxy trust configuration; these are controls to inspect, not evidence of a complete security audit.[^ragflow]

## Permissions and integration identity

**Observed:** Community Edition policy derives resource decisions from persisted ownership, private/tenant/shared modes and membership. A zero-value QueryScope denies every row; hidden-resource normalization maps forbidden responses to not-found. Connector and chat-channel resources use tenant-scoped credential-use rules, not per-person connector secrets. **Synthesis:** active tenant membership can be inside the stored integration credential-use boundary; inspect service callers before assuming finer isolation.[^ragflow]

## Channel gateway caveat

**Observed:** channel runtime reconciliation restarts configured adapters when credential fingerprints change. Platform verification is adapter-specific. The WhatsApp Node gateway's control API accepts requests when its token environment variable is empty; its default loopback bind limits exposure but does not add authentication. The Go supervisor passes its parent environment to that child. **Synthesis:** configure gateway authentication and network isolation, and minimize child-process secrets; no exploit was attempted.[^ragflow]

## Review limits

Only sampled configuration, auth-routing and tool-registration paths were inspected. No penetration tests, exploit checks, tenant-isolation tests, secret rotation, full secret-scanner validation, sandbox review or production deployment inspection occurred. Enterprise extensions and external services were not audited. Raw evidence remains untouched; distributing the repository also distributes raw source, so redacted wiki prose alone does not remove the underlying key.[^ragflow]

## Relationships

- **Constrains:** [operations](ragflow-operations.md), [server architecture](ragflow-architecture.md) and [agent workflows](ragflow-agent-workflows.md).
- **Recorded by:** [source map](ragflow-source-map.md), whose sensitive entries store names/statuses only.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54`; locators: `internal/common/password.go::LoadPrivateKey / RSA decryption preceding LoadPrivateKey`; `conf/private.pem::tracked file presence only (contents excluded)`; `conf/service_conf.yaml::infrastructure credential keys (values excluded)`; `internal/server/config/database_config.go::parseMySQLConfig (credential values excluded)`; `internal/router/router.go::Setup`; `internal/router/agent_routes.go::RegisterPublicAgentWebhookRoutes`; `internal/server/api/server.go::HTTP timeout / trusted proxy configuration`; `internal/agent/component/registry.go::component registration`; `internal/permission/policy_ce.go::resolveResource`; `internal/permission/policy_ee.go::newPolicyEE`; `internal/permission/query_scope.go::QueryScope`; `internal/permission/response/errors.go::NormalizeHidden`; `internal/permission/database_source.go::connectorResource / chatChannelResource`; `internal/channels/bootstrap.go::Runtime.Reconcile / credentialFromConfig`; `internal/channels/whatsapp-gateway/index.js::isAuthorized / default host`; `internal/channels/whatsapp_gateway.go::cmd.Env`.
