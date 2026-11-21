---
type: Concept
title: rlm.pi implementation
description: A Pi RLM plugin with persistent Python execution, recursive delegation, and important security and documentation limits.
tags: [language-models, inference, agents, security]
status: draft
created: 2026-11-21
generated: { by: llm-wiki-agent/1, at: 2026-11-21T17:01:33Z }
sources:
  - id: rlm-pi
    resource: ../raw/rlm.pi/README.md
    scope: ../raw/rlm.pi/
    kind: code
    revision: cc77fab30d085d1207eeb6ee7a242facb95f6061
    title: rlm.pi
---

rlm.pi is a Pi and oh-my-pi plugin implementing a [recursive language model](recursive-language-models.md) with a persistent Python worker, retrieval helpers, leaf model calls, and depth-limited child runs. Its subprocess is **not a security sandbox**: model-authored code can access the filesystem and network. **Observed** in worker source; deployment requires trusting the code and supplying external isolation appropriate to the risk.[^rlm-pi]

## Use and architecture

**Reported:** install with `pi install npm:@hicaru/pi-rlm` or `omp plugin install @hicaru/pi-rlm`, reload, and toggle `/rlm`; `/rlm-config` changes settings and `/rlm-stop` aborts a run. The package identifies version 0.3.31, requires Node 20 or newer, and registers `src/index.ts` as the Pi extension. Python is needed for the worker; provider calls may leave the machine despite documentation describing the local process architecture. **Observed** in package metadata and sandbox host code.[^rlm-pi]

**Reported:** the root works with context in a Python REPL, using search, regex, outline, document loading, leaf model calls and child RLM calls. **Observed:** the host starts a persistent Python subprocess and communicates by JSONL; subcalls are handled by the host. The worker implements an answer dictionary and asynchronous task scaffolding. Root and child surfaces differ: the worker source says child sandboxes are delegation-only, without retrieval helpers. Treat the README's promise that a child gets the full sandbox as an oversimplification pending further inspection of context inheritance and child execution.[^rlm-pi]

**Observed defaults:** `maxDepth=4`, `maxIterations=1000`, 120-second REPL timeout, unlimited leaf and child concurrency, and token budgeting enabled. The plugin README instead lists 30 iterations and says verification nudge defaults off, whereas the inspected configuration sets it on; consult the code for this revision rather than relying on those README defaults. Effective overrides and enforcement are not fully audited.[^rlm-pi]

## Security and operational limits

**Observed:** the host filters environment variables by a sensitive-name regex, but the Python worker explicitly permits imports and filesystem access, including writes and network-capable modules. This contradicts the root README's blanket statement that the engine does not write to disk and the answer is the only output. Environment filtering is not a complete isolation guarantee; trusted code can still access resources available to its operating-system account. No exploit or runtime security test was performed.[^rlm-pi]

**Reported, historical:** a field audit against an earlier revision describes malformed final answers, budget overshoot, failures and logging gaps. It cannot establish that those defects persist in this later revision; fixes and current behavior are pending inspection.[^rlm-pi]

## Relationships

- **Synthesis:** [Recursive language models](recursive-language-models.md) describes the general scaffold this plugin implements.
- **Uses:** [rlm.pi evaluation](rlm-pi-evaluation.md) describes the project's reported benchmark of this implementation.

## Source and coverage

Repository [entry point](../raw/rlm.pi/README.md), MIT-licensed plugin by hicaru contributors; snapshot revision above. Statically inspected root and plugin READMEs, both package manifests, benchmark README, defaults, Python guards and worker excerpt, host subprocess excerpt, and part of the historical audit. Inventory includes TypeScript plugin modules, Python scaffold, tests, benchmarks and journals, lockfiles, configuration, translations, changelog, images, video and chart script. Remaining source modules, settings precedence, tests, audit remainder, benchmark code and run data are pending; translations and generated/binary media were not inspected. The README's hero plot is not used as evidence. No code, tests, benchmarks, or external dependencies were executed or fetched. Sensitive-pattern screening found test fixtures with fake credentials, not a known live credential; this is not a complete privacy audit. Draft reflects substantial pending coverage and unverified behavior.[^rlm-pi]

[^rlm-pi]: [Repository README](../raw/rlm.pi/README.md), “Install”, “How it works”, “Sandbox API”, and “Security”; `pi-plugin/rlm/README.md`, “Settings” and “Security”; `pi-plugin/rlm/package.json`, `version`, `engines`, `pi.extensions`; `pi-plugin/rlm/src/config/defaults.ts::DEFAULT_CONFIG`; `src/sandbox/sandbox.ts::sanitizedEnv` and `PythonSandbox`; `src/sandbox/py/guards.py` module docstring; `src/sandbox/py/worker.py` module docstring and `Worker`; `pi-plugin/rlm/docs/audit-2026-08-30.md` §§0–2. Paths abbreviated after `pi-plugin/rlm/` where indicated.
