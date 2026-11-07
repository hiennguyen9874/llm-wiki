---
type: Concept
title: MemHub privacy boundaries and permission model
description: What MemHub stores and sends, its four independent permissions, absence of per-memory ACLs, diagnostics and debug-logging risks, and credential handling.
tags: [memhub, privacy, permissions, security, diagnostics]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# MemHub privacy boundaries and permission model

Raw data stays in the user's data directory; reading a source, sending content to a model, and letting a host read memory are separate authorisation boundaries; uninstall keeps data and only `delete-data` with double confirmation removes it (`memhub/PRIVACY.md` "本地数据"; `memhub/README.md` "CLI 与 Runtime").[^hy-memory] No screen/AXTree/OCR/keyboard/clipboard/audio capture (`memhub/README.md` "核心原则"; `PRIVACY.md`).[^hy-memory]

## Permissions

Four independent management permissions: source grant, harness sync, model-content permission, host recall grant (`memhub/docs/ARCHITECTURE.md` "Permission Boundaries").[^hy-memory] There is **no MemHub-side memory ACL**: recall is authorised by a host-installation credential plus tool grant, then SDK search. Today cross-harness search is default-allowed and there is no per-memory A→B visibility switch; future limits are intended to use SDK `source`/`include_sources`/`exclude_sources` (`ARCHITECTURE.md` "HY SDK client boundary", Recall bullet).[^hy-memory] Default host grants: tools `om_recall, om_conversations, om_diagnostic_trace`, scopes `all-apps` / `source:<id>`; `om_conversations` authorises the raw `/context` channel and is not an MCP tool (`packages/host-bridge/src/mcp-toolset.ts`; `docs/harness-support/README.md`).[^hy-memory]

## Network and model use

Third-party model use is disclosed and must not send keys, headers, absolute paths or unrelated content; model-bound text passes credential stripping (`PRIVACY.md` "网络访问"; `input_sanitization.py::sanitize_model_input`). Credentials go to OS secure storage with explicit failure codes (`secrets.py::SecretStoreErrorCode`).[^hy-memory] A `verify_zero_collection.py` script scans sources and artifacts for telemetry/collection patterns and runs in CI (`memhub/scripts/verify_zero_collection.py`; `.github/workflows/ci.yml`).[^hy-memory]

## Diagnostics and logging

Diagnostics are redacted structured JSONL (`DiagnosticEventV1`; 4 MiB × 3 files, 14-day sweep, 128 MiB cap, 0600/0700); official events carry no conversation text, prompts, tokens or full paths, **but** the Desktop "export logs" ZIP includes raw local logs and should go only to trusted developers (`docs/contracts/diagnostic-logging.md` "存储与读取"; `docs/PRODUCT_LOG_TROUBLESHOOTING.md`).[^hy-memory] SDK pipeline logs/traces are forced off, while `debug` level sets `MEMORY_LOG_LLM_CONTENT=true`, which can persist full prompts in `hy_memory.log` and does not retroactively delete them (`hy_runtime_config.py::_apply_hy_pipeline_policy`, `apply_diagnostic_log_level`; `PRIVACY.md` "诊断与调试日志"). Compare the SDK default in [observability](hy-memory-runtime-concurrency-and-observability.md).[^hy-memory]

## Relationships

- Part of: [MemHub architecture](memhub-product-architecture.md).
- Applies to: [import adapters](memhub-import-adapters-and-live-sync.md), [host bridge](memhub-host-bridge-harness-integration.md).
- Project-level security reporting: [releases, CI and quality](hy-memory-release-ci-and-quality.md).

## Coverage and limits

Static inspection (delegated). Claims are as documented; no network capture or runtime audit was done, so "zero collection" is Reported by the project's own policy and script, not independently confirmed (Unverified).

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
