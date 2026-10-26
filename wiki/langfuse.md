---
type: Concept
title: Langfuse
description: Langfuse's acceptance boundary — an MIT core beside nine enterprise-key features, trace-only OTLP ingest, and a billable unit that counts evaluations — plus the three cases where leaving it is not worth it.
tags: [ml, agents, observability, langfuse, licensing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:24:36Z }
stale_after: 2027-02-26
sources:
  - id: pydantic-langfuse-alts-2026
    resource: ../raw/best-langfuse-alternatives/index.md
    scope: ../raw/best-langfuse-alternatives/
    kind: article
    revision: sha256:ca8ebbf2906627e3d5b930e13b62421d77cefb001be9758f3487f2a344b13ace
    title: "Best Langfuse Alternatives in 2026"
  - id: pydantic-eval-tools-2026
    resource: ../raw/best-llm-evaluation-tools/index.md
    scope: ../raw/best-llm-evaluation-tools/
    kind: article
    revision: sha256:6a9f009216a57d12fd893e17a7388b01e6bfa5ed482e0d3443a5003ac5eab103
    title: "Best LLM Evaluation Tools 2026"
  - id: pydantic-prompt-tools-2026
    resource: ../raw/best-prompt-management-tools/index.md
    scope: ../raw/best-prompt-management-tools/
    kind: article
    revision: sha256:db5ee87b64a4ccf3e2a1d78f6743164874926a11cf645eb18cf81ace43333372
    title: "Best Prompt Management Tools 2026"
---

Langfuse is an MIT-licensed LLM observability platform that self-hosts with no usage limits and ships prompt management, datasets, experiments and evaluators in the product, and it is still the tool teams leave in predictable directions[^pydantic-langfuse-alts-2026] Four boundaries explain the exits: the billable unit counts evaluations alongside traces, the OpenTelemetry endpoint takes traces but not logs or metrics, several governance features need an enterprise key, and ownership moved to ClickHouse in January 2026[^pydantic-langfuse-alts-2026] This page exists because Langfuse is the baseline that [LLM observability platform comparison](llm-observability-platform-comparison.md) reads every alternative against, and the same article's verdict is that it remains the right answer when permissive self-hosting, an established workflow or a specific cloud region is the binding constraint. All of it is Pydantic's reading of a competitor, written in a comparison that ranks its own product first[^pydantic-langfuse-alts-2026]

## What "MIT core" actually covers

The repository's licence file carves out the `ee/`, `web/src/ee/` and `worker/src/ee/` directories, which are governed by a separate commercial licence, and nine features require a `LANGFUSE_EE_LICENSE_KEY` at runtime: project-level RBAC roles, protected prompt labels, data retention policies, audit logs, server-side data masking, UI customization, organization creators, the org management API with SCIM, and the instance management API[^pydantic-langfuse-alts-2026] The accurate description the author offers is "MIT core with a commercially licensed enterprise edition", and he names several of the gated features as exactly what a security review asks for[^pydantic-langfuse-alts-2026]

That places Langfuse between an OSI-approved product and a source-available one: permissive for the whole LLM workflow, not permissive end to end. The comparison draws the consequence — an OSI-approval requirement sends a team to Laminar or Helicone instead[^pydantic-langfuse-alts-2026]

## Traces arrive, logs and metrics do not

The OTLP endpoint currently accepts trace data only, over HTTP/JSON or HTTP/protobuf, with gRPC not yet supported[^pydantic-langfuse-alts-2026] The article opens with the consequence: an agent answers wrongly at 2am, the trace shows prompt, model call, tool call, tokens and cost looking correct, and the actual cause — a connection-pool timeout in a retrieval service two hops upstream — never reached Langfuse, so half the story sits in another tool under a different ID and an on-call engineer reassembles it by hand[^pydantic-langfuse-alts-2026]

That is the same failure boundary the framework-independent checklist in [agent observability requirements](agent-observability-requirements.md) names: a layer that cannot carry the database and upstream-service spans makes "was it the model, the tool, or the backend?" unanswerable. It is also the structural difference from [Pydantic AI observability](pydantic-ai-observability.md)'s Logfire, which ingests traces, logs and metrics on one meter.

## The billable unit includes the score

Langfuse defines a billable unit as a trace, an observation **or a score**, so evaluations and annotations add to the same meter that tracing does; the author's warning is that improving quality measurement increases the bill in a way that is easy to miss while sizing a plan[^pydantic-langfuse-alts-2026] The published tiers are a Hobby plan of 50,000 units a month with 30-day data access and a $29/month Core plan[^pydantic-langfuse-alts-2026] The same definition and the same tiers appear in the 2026-08-26 comparison table of a later Pydantic article compiled as [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md) — the same publisher, so a repetition rather than independent confirmation, though it does show the unit definition has not changed between the two articles[^pydantic-eval-tools-2026] The cost implication, and the contrast with per-record and per-score billing, is worked through in [LLM observability platform comparison](llm-observability-platform-comparison.md)

## Prompt management: in the core, but not the governance

Prompt management is inside the MIT core, which is why the licence-key page can say all core features and APIs are available in the OSS build without limits[^pydantic-prompt-tools-2026] Versions receive automatic IDs, labels attach a version to an environment or tenant, and rollback is setting `production` back to an earlier version in the UI[^pydantic-prompt-tools-2026] Delivery is a client-side concern: the SDK documents a 60-second cache TTL, serves stale copies while revalidating in the background, and accepts a fallback prompt for when both cache and API are unavailable[^pydantic-prompt-tools-2026]

Percentage rollout is not part of it — the A/B testing guide labels two versions and picks between them with `random.choice([prompt_a, prompt_b])` in application code[^pydantic-prompt-tools-2026] Protected prompt labels, the control that stops a member from moving `production`, are enterprise-gated: an enterprise key when self-hosted, and on cloud the Teams add-on for Pro or Enterprise[^pydantic-prompt-tools-2026] That is the same boundary the nine-feature list above draws, restated for the prompt workflow specifically, and it is the reason a self-hosted deployment most needs the part that is not MIT. Prompt experiments over a dataset with LLM-as-a-judge or code evaluators round out the in-product workflow[^pydantic-prompt-tools-2026]

The delivery-mechanism comparison against six other registries is in [prompt management tools](prompt-management-tools.md)

## Ownership and continuity

ClickHouse acquired Langfuse in January 2026, with both companies committing to keep the project open source and self-hostable and the cloud running as-is[^pydantic-langfuse-alts-2026] The author's reading is that the commitment is real and that it is also a new owner, which he says is enough for some teams to re-run the evaluation[^pydantic-langfuse-alts-2026] The same event appears in the 2026 consolidation table in [agent optimization platforms](agent-optimization-platforms.md), where the stated consequence is that the licence survives while RBAC, SCIM and audit logs still need the commercial key.

## When staying is the right call

Three situations are named as still favouring Langfuse[^pydantic-langfuse-alts-2026]

- **Licensing.** "We run it, on code we can fork" is met by the MIT core, which self-hosts with no usage limits and no scalability difference from the cloud, with the enterprise-key features as the boundary — where Logfire's Enterprise-only self-hosting does not meet it.
- **Sunk workflow.** Prompt versions, datasets, experiment history and annotation queues are real work, and none of it moves with a DSN change; migrating pays only when today's missing capability costs more than the rewrite.
- **Data residency.** Langfuse publishes EU, US, Japan and HIPAA cloud regions alongside self-hosting, which is a shorter path than a custom agreement when a jurisdiction is contractual.

## Limits

- Every claim here is a competitor's description from a Pydantic comparison article that ranks Logfire first (author Bill Easton, 2026-08-26); no Langfuse documentation, licence file, price page or repository was fetched in this ingest[^pydantic-langfuse-alts-2026]
- The capture has no dedicated Langfuse entry: its numbered sections run 1, 3, 4 … 8, so the second-ranked entry is missing and the facts above come from the introduction, §"Why teams look for a Langfuse alternative", the comparison table, §"When Langfuse is still the right call" and the FAQ, which is a narrower evidence base than the other platforms received (**Synthesis**)[^pydantic-langfuse-alts-2026] The later eval-tools capture omits a Langfuse entry in the same way, its numbered sections running 1, 2, 4, 5, 6, 7 while its frontmatter still lists seven tools, so the gap looks like a publisher habit rather than one truncated capture[^pydantic-eval-tools-2026]
- The nine enterprise-key features, the unit definition, the OTLP scope and the prices are a 2026-08-26 snapshot of documentation; none of them was exercised against an installed instance, and the licence carve-out was not opened[^pydantic-langfuse-alts-2026]
- The source names no Pydantic AI version and gives no Pydantic AI integration detail, so this page is platform-market knowledge rather than build guidance; pricing and licence columns carry the `stale_after`.
- The prompt-management facts come from a third Pydantic article (2026-08-26) that ranks Logfire first and places Langfuse second; it repeats the MIT-core boundary, the $29 Core entry and the January 2026 ClickHouse acquisition from the same publisher, so those are dated rather than independently verified, and it adds the 60-second cache TTL, the stale-serve and fallback behaviour and the A/B guide's `random.choice` pattern, none of which was executed[^pydantic-prompt-tools-2026]
- Evidence class: **Reported**.

## Relationships

- **Contrasts with** [Pydantic AI observability](pydantic-ai-observability.md): Logfire ingests traces, logs and metrics together and self-hosts only on Enterprise, where Langfuse's MIT core self-hosts freely with traces-only ingest.
- **Is the baseline for** [LLM observability platform comparison](llm-observability-platform-comparison.md), which reads every alternative against its licence, meter and ingest scope, and a table row in [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), which prices it per unit beside the eval specialists.
- **Shares its ownership event with** [agent optimization platforms](agent-optimization-platforms.md), where the ClickHouse acquisition is one row of the 2026 consolidation table.
- **Contributes the application-side half of** [prompt management tools](prompt-management-tools.md), which scores its MIT-core registry and `random.choice` rollout against six alternatives; the protected-label boundary is the same enterprise key this page's feature list describes.
- **Falls short of** [agent observability requirements](agent-observability-requirements.md) on the full-stack trace requirement, for the reason the article's opening incident illustrates.

[^pydantic-langfuse-alts-2026]: Bill Easton, "Best Langfuse Alternatives in 2026", Pydantic, published 2026-08-26; local capture `raw/best-langfuse-alternatives/index.md`, content digest sha256:ca8ebbf2. Opening incident and the traces-not-logs-and-metrics gap (lines 11–15); §"Why teams look for a Langfuse alternative" (lines 21–28) for the billable-unit definition, the traces-only OTLP endpoint with no gRPC, the nine `LANGFUSE_EE_LICENSE_KEY` features, and the ClickHouse acquisition; §"Comparison at a glance" (lines 102–113) for the Hobby 50k-units and $29/month Core figures, the licence carve-out wording and the ingest scope; §"When Langfuse is still the right call" (lines 127–135) for the licensing, sunk-workflow and EU/US/Japan/HIPAA residency reasons; §"Frequently asked questions" (lines 137–149) for the `ee/`, `web/src/ee/`, `worker/src/ee/` carve-out paths and the "MIT core with a commercially licensed enterprise edition" phrasing. Evidence class: **Reported** — a competitor description inside a vendor comparison; nothing was installed, fetched or licence-checked.

[^pydantic-eval-tools-2026]: Bill Easton, "Best LLM Evaluation Tools 2026", Pydantic, published 2026-08-26 with prices checked 2026-08-26; local capture `raw/best-llm-evaluation-tools/index.md`, content digest sha256:6a9f0092. §"Comparison at a glance" (table row, line 121) for the repeated Langfuse unit definition, the HTTP/JSON and HTTP/protobuf ingest with no gRPC, the Hobby 50k-unit and $29/month Core tiers and the `ee/` licence note; frontmatter description and §heading list for the seven-name shortlist against numbered sections 1, 2, 4, 5, 6, 7 with no Langfuse entry. Evidence class: **Reported** — same publisher as the page's primary source, read once, nothing fetched.

[^pydantic-prompt-tools-2026]: Bill Easton, "Best Prompt Management Tools 2026", Pydantic, published 2026-08-26, 3,421 words as declared; local capture `raw/best-prompt-management-tools/index.md`, content digest sha256:db5ee87b. §"2. Langfuse: if you would rather spend time than money to self-host" (lines 54–60) for prompt management in the MIT core, the licence-key wording, automatic version IDs and label-based rollback, the 60-second client cache with stale-serve and fallback prompt, prompt experiments with LLM and code judges, the A/B guide's `random.choice([prompt_a, prompt_b])`, the enterprise-key and Teams-add-on split for protected prompt labels, the Postgres/ClickHouse/Redis/object-storage stack, the ClickHouse acquisition date and the $29 Core entry; §"Comparison at a glance" (lines 102–114) for the Hobby 50k-unit, 2-user tier. Evidence class: **Reported** — a competitor description inside a vendor comparison; nothing was installed, cached or licence-checked.
