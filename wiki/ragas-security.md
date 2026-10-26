---
type: Concept
title: Ragas telemetry and evaluation trust boundaries
description: Default analytics, enabled data sinks, asymmetric image access, local paths, plugins and credential-handling patterns define Ragas trust boundaries.
tags: [security, rag, operations, telemetry]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:20:38Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b682
    title: Ragas repository
---

**Observed:** Ragas can send evaluation data to explicitly configured judge/embedding/integration services and also emits opt-out usage analytics by default. Evaluation inputs can select image URLs/files, persistence paths and executable extension surfaces. **Synthesis:** treat the library as trusted application code handling potentially untrusted datasets, not as a sandbox or privacy boundary.[^ragas-298b682]

## Default analytics versus enabled data sinks

`_analytics.py` posts to `https://t.explodinggradients.com` with a one-second timeout. Set `RAGAS_DO_NOT_TRACK=true` before use to disable it; lookup is cached, so changing it late may not affect the process. A random install identifier is persisted in appdirs' ragas/uuid.json and included with version and event fields. The shipped batcher uses ten events/ten seconds, a daemon thread and exit flush. Debug tracking logs payloads rather than sending after the opt-out check. The opt-out is enforced in `track`, not at global batcher creation or event-model construction, so it is not a guarantee of no background thread or identifier-file activity.[^ragas-298b682]

| Channel | Inspected data boundary |
| --- | --- |
| Built-in analytics | Metric/provider/model identifiers, counts, language/type and usage/completion flags, persistent pseudonymous ID; event schemas have no prompt/context/response/API-key fields |
| Judge / embedding providers | Input texts, contexts and optionally image payloads needed by scoring/generation |
| Drive backend | Dataset/experiment rows in Sheets; broad Drive and spreadsheet scopes; OAuth cache defaults token.json in CWD |
| LangSmith / tracing SDKs | Enabled uploads/trace capture according to adapter and caller instrumentation; not governed by the analytics opt-out |

The README's “anonymized” wording should not be interpreted as unlinkable runs: the identifier persists across runs. User-chosen metric/model names can themselves contain confidential identifiers even when no raw prompt field exists. Disabling analytics is not disabling configured provider or integration networking.[^ragas-298b682]

## Image/file/network policy is path-specific

The older multimodal prompt checks initial resolved IPs, defaults to disallow internal/local targets, and validates image size/content, but allows redirects; its source explicitly notes redirect bypass risk. The collections multimodal-faithfulness helper has HTTP(S), ten-second/ten-MiB and PIL validation without equivalent private-IP or allowed-root checks. It tries local paths and sends valid image bytes as base64 in model messages.[^ragas-298b682]

**Synthesis:** an untrusted context can trigger internal HTTP requests or disclose accessible valid local images to a configured provider. This does **not** establish arbitrary non-image file exfiltration: invalid image processing falls back to text. No attack or payload was executed. Restrict egress and readable files at the application/process boundary; sibling helper protections do not automatically cover collections scoring.

## Other trust surfaces

- Local CSV/JSONL backend names are composed into paths without a demonstrated containment check; do not accept untrusted names as storage authority.
- Backend entry points load installed Python extension code. CLI eval modules execute caller-selected Python; quickstart may download an unpinned archive. `version_experiment` can stage, commit and branch the caller's repository.
- Cache files contain persisted provider results; the cache-key builder does not automatically isolate model configuration. Dependency serialization internals were not inspected, so no reproduced pickle/code-execution claim is made.
- Benchmark Docker build passes OPENAI_API_KEY as build arg and stores it in ENV. AI-doc CI configuration combines fork content with write-scoped permissions/secret-bearing actions; deployed workflow protections and exploitability remain unverified.

## Review status and disclosure limits

Pattern screens across tracked UTF-8 content found no selected live-key/private-key shapes; inspected assignments were placeholders/fixtures. This is not an exhaustive secret, PII, notebook-output, dependency or security audit. No credential value is compiled here. SECURITY.md reports a private disclosure policy and 0.3.x support table; applicability to this commit was not independently established.[^ragas-298b682]

## Relationships

- Constrains [model adapters](ragas-model-adapters.md), [specialized metrics](ragas-specialized-metrics.md), [persistence](ragas-backends.md), [integrations](ragas-integrations.md) and [operations](ragas-operations.md).

[^ragas-298b682]: Ragas `298b682`, `src/ragas/_analytics.py::do_not_track/get_userid/BaseEvent/AnalyticsBatcher/track`; `README.md::Open Analytics`; `src/ragas/prompt/multi_modal_prompt.py::_download_validate_and_encode/_is_safe_url_target`; `src/ragas/metrics/collections/multi_modal_faithfulness/util.py::_try_process_url/_try_process_local_file/build_multimodal_message_content`; `src/ragas/backends/gdrive_backend.py::GDriveBackend._setup_auth`; `src/ragas/backends/local_csv.py::LocalCSVBackend._get_file_path`; `src/ragas/backends/local_jsonl.py::LocalJSONLBackend._get_file_path`; `src/ragas/backends/registry.py::BackendRegistry.discover_backends`; `src/ragas/cli.py::load_eval_module/quickstart`; `src/ragas/experiment.py::version_experiment`; `Makefile::benchmarks-docker`; `tests/benchmarks/Dockerfile`; `.github/workflows/claude-docs-check.yml::check-docs`; `SECURITY.md::Reporting Security Issues/Supported Versions`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
