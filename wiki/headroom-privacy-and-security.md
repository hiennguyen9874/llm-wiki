---
type: Concept
title: Headroom privacy and security boundaries
description: Telemetry defaults, local plaintext storage, control-surface trust, and documentation discrepancies.
tags: [agent-memory, privacy, security]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:19:57Z }
stale_after: 2027-02-06
sources:
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
---

**Observed:** the upload beacon defaults on, independently of local telemetry collection, which defaults off. `HEADROOM_BEACON=off`, `DO_NOT_TRACK=1`, or `HEADROOM_OFFLINE=1` disables the beacon; explicit precedence is implemented in `beacon_off_reason`. The beacon payload includes structural aggregates and allow-listed configuration values, not simply token counts.[^headroom]

**Reported:** the security model says local data is not encrypted at rest. **Observed:** the Python proxy's CCR SQLite store can contain original tool content, and full-message logging is opt-in; TTL is not a secure deletion guarantee. Settings and persistent-install mechanisms can also store configured secret-bearing values. Treat project memory, agent files and local stores as sensitive.[^headroom]

The Python proxy's sensitive local control surfaces use loopback and other checks, not an identity boundary between mutually untrusted local processes. The Rust proxy is separate and has different defaults; do not assume Python's bind policy applies to it.[^headroom]

## Contradictions

- `docs/content/docs/proxy.mdx` says beacon data excludes environment variables and anything derived from bodies; `headroom/telemetry/session.py` constructs allow-listed configuration and structural shape fields. The broader wording is not supported by the inspected implementation.[^headroom]
- `docs/content/docs/security-model.mdx` describes the runtime log as inheriting umask, but `headroom/proxy/helpers.py::_OwnerOnlyRotatingFileHandler` implements owner-only creation; platform behavior was not tested.[^headroom]

## Relationships

- Qualifies [interfaces](headroom-interfaces.md), [CCR](headroom-cache-and-ccr.md), and [memory](headroom-memory.md).

[^headroom]: `headroom/telemetry/beacon.py::beacon_off_reason`, `BEACON_DEFAULT_ON`; `headroom/telemetry/session.py::_payload_v2`, `_CONFIG_ENV_KEYS`; `docs/content/docs/proxy.mdx` telemetry section; `docs/content/docs/security-model.mdx` §§ Data at rest, Local control surface; `headroom/cache/compression_store.py::_create_default_ccr_backend`; `headroom/proxy/models.py` logging configuration; `headroom/settings_store.py` secret settings; `headroom/install/supervisors.py::_render_unix_runner`; `headroom/proxy/loopback_guard.py::require_loopback`; `headroom/proxy/helpers.py::_OwnerOnlyRotatingFileHandler`; `crates/headroom-proxy/src/config.rs` listen options; revision `2b0315b`.
