---
type: Concept
title: WeKnora configuration precedence and key management
description: YAML/environment layering, explicit overrides, validation, JWT persistence, and the exact AES key-length requirement.
tags: [ml, weknora, configuration, security]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd5855fc4ded5c981a92dcb82a455246
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora configuration combines a required YAML file, environment interpolation, Viper lookup, and hand-written override/default passes. **Observed:** the effective value is not reliably inferred from a single template. Persistent JWT and encryption keys are operational identities: changing or omitting them has consequences beyond ordinary configuration reload.[^weknora]

## Load order and validation

`internal/config/config.go::LoadConfig` searches the current directory, `./config`, `$HOME/.appname`, and `/etc/appname/`. Failure to read a config file is fatal. It enables environment lookup with dot-to-underscore replacement, substitutes `${VAR}` in file text only for **nonempty** environment values, then unmarshals with YAML tags. Empty or absent variables leave the literal placeholder intact.[^weknora]

Prompt templates and built-in agent definitions are loaded separately. Explicit OIDC, agent, KB, network, auth/tenant, and audit overrides run before validation. Comments explain that `WEKNORA_*` does not automatically become a global nested-field prefix; those knobs need explicit handling. **Synthesis:** documentation for an environment name should be reconciled with its actual consumer rather than assuming every YAML field has a prefixed override.[^weknora]

`ValidateConfig` checks authentication mode enums, nonnegative retention, retrieval bounds, overlap smaller than chunk size, and valid server ports, among other constraints. This was read statically, not exercised against example configurations.[^weknora]

## Keys and failure behavior

| Key | Inspected behavior |
| --- | --- |
| `JWT_SECRET` | Uses a nonempty, non-placeholder configured value; empty values or either recognized legacy change-me placeholder trigger a random per-process fallback, so sessions cannot be assumed to survive restart or work across replicas |
| `SYSTEM_AES_KEY` | Must be exactly **32 bytes of environment string data**; invalid length yields no key |
| `SYSTEM_SIGNING_KEY` | Optional independent signing key; signing helpers can fall back to a valid AES key |

**Observed:** `GetAESKey` does not hex-decode its input. `EncryptAESGCM` returns plaintext when given no key. Strict `DecryptStoredSecret` raises a missing-key error for an encrypted stored value instead of treating ciphertext as a credential. Legacy plaintext values are distinguished from encrypted values by a prefix.[^weknora]

The inspected `.env.example` correctly recommends `openssl rand -hex 16` for a 32-ASCII-byte AES string, and `openssl rand -hex 32` for JWT/signing secrets. Those are generation commands, not credential values; **they were not run**. Preserve existing encryption keys during upgrades and back up key material separately from this wiki. Template defaults and secret values are intentionally not copied here.[^weknora]

## Relationships

- Configures [backend composition](weknora-backend-architecture.md) and [deployment](weknora-deployment.md).
- Determines important [authentication and authorization defaults](weknora-security.md).
- Separate [runtime queue settings](weknora-task-queues.md) can also change effective concurrency.

## Coverage limits

Selected loader/default passes, JWT generation, crypto helpers, startup banner, and templates were inspected. Full override coverage, every credential consumer, signing-helper bodies, secret rotation, and multi-replica behavior were not executed or exhaustively audited. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd5855fc4ded5c981a92dcb82a455246`: `internal/config/config.go::LoadConfig`, `ValidateConfig`, `applyOIDCEnvOverrides`, `applyAgentEnvOverrides`, `applyKnowledgeBaseEnvOverrides`, `applyNetworkEnvOverrides`, `applyAuthAndTenantDefaults`, `applyAuditDefaults`; `internal/application/service/user.go::getJwtSecret`; `internal/utils/crypto.go::GetAESKey`, `EncryptAESGCM`, `DecryptStoredSecret`, `ErrEncryptedDataMissingKey`; `internal/utils/presign.go` signing-key symbols (partial inspection); `internal/runtime/startup.go::LogStartupEnv`; `.env.example`, “F1. keys” section, lines 595–608. Package entry: [README](../raw/WeKnora/README.md), “Quick Start” and configuration links.
