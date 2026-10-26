---
type: Concept
title: Pydantic AI observability
description: Pydantic AI instruments with plain OpenTelemetry, defaults to instrumentation v5 with aggregated usage attributes, and prints a first-run banner until a backend is configured.
tags: [ml, pydantic-ai, agents, observability]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:06:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

Pydantic AI's instrumentation is plain OpenTelemetry, so any OTel backend works; Logfire is Pydantic's commercial hosted platform, with a free Personal plan and an Enterprise self-hosted option on your own Kubernetes cluster[^dd-v2-tour-2026] Local development needs two lines:

```python
import logfire
logfire.configure(send_to_logfire='if-token-present')  # plain OTel; any backend works
logfire.instrument_pydantic_ai()
```

## What v2 changed on the wire

Instrumentation v5 is the default in V2, and run spans now report usage under `gen_ai.aggregated_usage.*`. Any dashboard query that read token totals from run spans has to change[^dd-v2-tour-2026]

Model-request spans also carry prompt-cache health attributes from v2.55 — `pydantic_ai.cache.*` hit ratio, cached-prefix size, a `pydantic_ai.cache.collapse` event when a prefix is lost unexpectedly, and a `pydantic_ai.cache.not_enabled` flag[^dd-v2-tour-2026] See [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md).

## The first-run banner

Until instrumentation is configured, the first run prints a banner to stderr when a person or a coding agent is reading it. It is suppressed under pytest, when `CI` is set, or with `PYDANTIC_AI_NO_BANNER=1`[^dd-v2-tour-2026] The banner is the only in-band nudge that a run is uninstrumented, which is why it appears in scripts that never configured Logfire.

## OpenTelemetry is also the eval substrate

The agentic evaluators in [Pydantic Evals](pydantic-evals.md) read the local span tree, so they need the `logfire` SDK configured even when nothing is sent anywhere. Online evaluation emits `gen_ai.evaluation.result` events into the same pipeline, keyed by the agent's `name`[^dd-v2-tour-2026] Observability is therefore not optional instrumentation for teams that grade trajectories; it is the input.

## Limits

- No backend, collector, or Logfire account was exercised; attribute names and the v5 default are reported from the release and docs summary[^dd-v2-tour-2026]
- Logfire's plan limits, retention, and self-hosted requirements are not described beyond the existence of the tiers.
- The banner behaviour was observed by the author on every uninstrumented run, not in this ingest.
- Evidence class: **Reported**.

## Relationships

- **Carries** the attributes exposed by [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md).
- **Feeds** [Pydantic Evals](pydantic-evals.md), offline and online.
- **Surfaces** the warnings and failure modes described in [Pydantic AI run controls](pydantic-ai-run-controls.md).

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Observability: Logfire or any OpenTelemetry backend" (raw lines 594–613) for the OTel-versus-Logfire boundary, the two-line setup, instrumentation v5 and `gen_ai.aggregated_usage.*`, cache attributes, and the banner; §"Pydantic Evals" for the shared span tree and `gen_ai.evaluation.result` events. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — docs summary; nothing was instrumented or exported.
