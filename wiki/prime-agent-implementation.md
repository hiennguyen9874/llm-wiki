---
type: Concept
title: Prime Agent implementation
description: A partial static inspection of Prime Agent's Rust workspace, Python kernel shim, and operational boundaries.
tags: [language-models, agent-harnesses, implementation]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T16:59:27Z }
sources:
  - id: prime-agent-code
    resource: ../raw/prime-agent/README.md
    scope: ../raw/prime-agent/
    kind: code
    revision: 783acb5d72a9b23f97fa4a793a67d421b3ec402d
    title: Prime Agent repository
---

Prime Agent's supplied repository implements a coding and research agent using a Rust workspace and a Python kernel-side runtime. This is a **partial static inspection**, not a runtime verification or a complete audit; its relationship to the paper's experimental implementation has not been established.[^prime-agent-code]

## Architecture and interfaces

**Observed:** Workspace version 0.10.5 uses Rust edition 2021 and has ten member crates, including CLI, daemon, agent, core, AI, models, TUI, types, telemetry and performance crates. The CLI entry point delegates to `pa_cli::main_with_runtime`; core exposes session, kernel, tools, refinement, goals, skills and other modules. The kernel module documents a persistent Python REPL subprocess using JSON lines over stdin and stdout. Its Python runtime package requires Python 3.11 or later and declares MCP and other dependencies.[^prime-agent-code]

**Observed:** The Python shim defines a child handle containing an ID, name, session directory and model; its diagnostic explicitly directs callers to `await rlm.spawn(...)`, rather than calling `rlm` or using the renamed `rlm.run`. **Reported:** The README describes asynchronous child agents, daemon-backed sessions and direct agent communication. These interfaces and behavior are not fully traced end to end here.[^prime-agent-code]

## Refinement and scheduled work

**Reported:** The supplied refine skill describes `await refine.run(instructions=None, global_=False)` as scheduling a focused update after the current turn; global scope is opt-in, and repeated calls during the turn update instructions. The heartbeat skill distinguishes internal session heartbeats from the user's `/heartbeat`: it documents a five-minute default and `steer` versus `follow_up` delivery. Implementation and concurrency guarantees remain unverified.[^prime-agent-code]

## Operation and security

**Reported:** The README recommends starting `prime-agent` in the working directory and using `/login` for a provider. It warns that model-generated Python and project commands run with user permissions, that worker/kernel isolation is not a security sandbox, and recommends trusted inputs or an external restricted environment. Its installation commands fetch and execute remote installers; they were not run. It describes session inspection, attach, status, doctor, update and shutdown commands; repair and shutdown can change state.[^prime-agent-code]

## Source and coverage

Prime Intellect repository, MIT licensed, snapshot commit above; the working tree reported clean when inspected. The README, workspace manifest, runtime manifest, license, security policy, CLI entry point, core and kernel module declarations, initial shim definitions, and refine and heartbeat skill instructions were inspected. Root directories and representative module trees were inventoried; the repository contains 1,668 files. Other source, tests, CI, configurations, scripts, packaging, skills, history fragments and documentation remain **pending**, as do full dependency closure, configuration precedence and source-to-paper reconciliation. Vendored `crossterm` is a workspace patch but its contents were not inspected; binaries and assets were not analyzed. A limited credential-pattern scan excluding vendor found no matches; this is not proof of absence. No package code, installer, build, or tests were executed. These gaps make the concept draft.[^prime-agent-code]

## Relationships

- **Synthesis:** [Prime Agent harness](prime-agent.md) describes the paper's architecture; this page covers a related repository snapshot without asserting experimental revision equivalence.

[^prime-agent-code]: [Repository README](../raw/prime-agent/README.md), §§Why Prime Agent, Getting Started, Built for Long-Running Work; `Cargo.toml` `[workspace]` and `[workspace.package]`; `crates/pa-cli/src/main.rs::main`; `crates/pa-core/src/lib.rs` and `crates/pa-core/src/kernel/mod.rs`; `prime-agent-runtime/pyproject.toml` `[project]`; `prime-agent-runtime/src/rlm/__init__.py::RLMSpawnHandle` and diagnostics; `skills/refine/SKILL.md` §API; `skills/rlm-heartbeat/SKILL.md` §§API, Delivery mode; `LICENSE`; `SECURITY.md`.
