---
type: Concept
title: Foreman Responsibilities and Routing
description: Foreman routes jobs to additive responsibilities whose checks propose directives that policy arbitrates.
tags: [foreman, routing, supervision]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:50:51Z }
sources:
  - id: foreman
    resource: ../raw/foreman/README.md
    scope: ../raw/foreman/
    kind: code
    revision: c3142ef636617f32f772140125aa310d81ceece9
    title: Foreman
---

**Reported:** [Foreman](foreman-overview.md) organizes supervision into responsibilities that own decision-model checks and propose directives. Routing is additive: global responsibilities activate and every conditional responsibility meeting its own threshold can also activate. Checks with the same evidence selection are batched; responsibilities themselves do not have aggregate scores.[^foreman]

## Configuration and lifecycle

Packaged per-responsibility TOML files provide defaults. Managed runs can apply a central override directory using `--responsibilities-dir` or `FOREMAN_RESPONSIBILITIES_DIR`; configuration is not discovered in the supervised repository. Global completion and verification are required for managed runs, whereas attached hooks can disable them centrally. Declarative responsibilities use a generic implementation; other executable directive logic belongs to installed Python implementations.[^foreman]

For managed runs, routing happens once before the first worker; invalid configuration or routing output fails before worker startup. Attached sessions route each submitted work item. The source reports built-in completion, verification, worker health, repository-instruction and human-escalation checks, plus conditional documentation quality. The decision model supplies probabilities, while policy arbitrates proposed actions.[^foreman]

**Coverage limit:** Based on README and `docs/routing.md` and `docs/runtime.md`; responsibility definitions, policy, extensions, tests and other implementation remain uninspected. Values and behavior are reported rather than independently verified.[^foreman]

[^foreman]: `README.md` § Responsibilities and checks; `docs/routing.md` §§ Configuration locations, File format, Runtime flow; `docs/runtime.md` §§ Components, One assessment cycle.
