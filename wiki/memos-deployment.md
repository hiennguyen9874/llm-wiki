---
type: Concept
title: Memos deployment and configuration
description: Deployment defaults, declarative configuration and migration requirements for Memos.
tags: [note-taking, memos, deployment]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:10:00Z' }
sources:
  - id: memos
    resource: ../raw/memos/README.md
    scope: ../raw/memos/
    kind: code
    revision: 88a20fe
    title: Memos repository
---

**Reported:** the README's Docker quick start maps port 5230 and a persistent data directory. **Observed:** the bare process defaults to port 8081, while the container sets `MEMOS_PORT=5230`; these are different deployment contexts, not necessarily contradictory. The Dockerfile requires the frontend to be built beforehand and a version build argument.[^memos]

**Observed:** CLI flags are bound to `MEMOS_` environment variables; startup migrates the database before applying declarative configuration. The API changelog reports JSON configuration documents in `/etc/memos/config` by default, replacing older `/etc/secrets` deployment files. `proto/README.md` still describes an older storage-schema configuration model; treat that description as stale rather than current operational guidance.[^memos]

**Reported migration constraint:** the minimum schema baseline is 0.31.8 from v0.31.0. Databases older than v0.22, or without a recorded schema version, must first run v0.25.3 and then v0.31.0. The current tree does not embed historical SemVer migration scripts. Verify upgrade guidance against the target release before use.[^memos]

No container, configuration, backup or upgrade was run. See [overview](memos-overview.md) and [source coverage](memos-source-map.md).

[^memos]: `README.md` §§ Quick start, Upgrading; `scripts/Dockerfile`; `cmd/memos/main.go::init`, `runServer`; `proto/api/CHANGELOG.md` deployment-configuration entry; `proto/README.md` § Deployment settings; `store/migration/README.md` § Database migration baseline.
