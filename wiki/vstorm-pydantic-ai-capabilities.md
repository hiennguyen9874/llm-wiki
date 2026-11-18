---
type: Concept
title: Vstorm Pydantic AI capabilities
description: Vstorm's roughly 20 open-source Pydantic AI capability packages — endorsed by the Pydantic team and wired into the Harness reference example — as the worked example of the community-to-core path.
tags: [ml, pydantic-ai, agents, ecosystem]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T03:52:09Z }
stale_after: 2026-12-23
sources:
  - id: vstorm-v2-blog
    resource: ../raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md
    scope: ../raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2 and the road to production-grade agentic AI"
  - id: pydantic-ai-v2
    resource: ../raw/pydantic-ai-v2/index.md
    scope: ../raw/pydantic-ai-v2/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI v2: capabilities, a leaner core, and the Harness"
  - id: pydantic-planning-docs
    resource: ../raw/harness/planning/index.md
    scope: ../raw/harness/planning/
    kind: documentation
    revision: sha256:13d1290b5beb86fcdc54d8111be20cd8fdfd48378657c9219f051a1492ba2864
    title: "Planning"
---

**Vstorm** is a Pydantic AI partner whose open-source [capabilities](pydantic-ai-capability-primitive.md) the Pydantic team endorses and links from the [Harness](pydantic-ai-harness.md); Vstorm describes the portfolio as roughly 20 packages distilled from 30+ production deployments and presents it as the worked example of the path from community building block to endorsed package to upstreamed core feature[^vstorm-v2-blog] The endorsement is not Vstorm's claim alone — the v2 announcement itself credits Vstorm and others with capabilities the team endorses and is working to upstream[^pydantic-ai-v2]

## What the Harness reference example uses

Per the post's reading of the Harness README, the official Harness wires Vstorm packages into its own reference example rather than merely listing them[^vstorm-v2-blog]:

| Package | Role in the reference example |
| --- | --- |
| `pydantic_ai_summarization` | Context management |
| `pydantic_deep` | Memory and stuck-loop detection |

Both arrive as capabilities, so they are attached through the same `capabilities=[...]` interface as first-party ones[^vstorm-v2-blog]

## Portfolio shape

Vstorm characterizes its capability packages as patterns that survived production rather than whiteboard designs, spanning middleware, subagents, summarization, monitoring, and a full-stack agent template, with `pydantic-deep` also written up as a guest post on pydantic.dev[^vstorm-v2-blog]

One package shows the arc closing from the Pydantic side rather than Vstorm's: `pydantic-ai-todo` — attributed to Vstorm and linked as `github.com/vstorm-co/pydantic-ai-todo` — supplied persistent stores, subtasks, dependencies and events for a model-maintained task list, and the first-party Harness `Planning` capability now incorporates that feature set and supersedes it, with the tools renamed (`write_todos` → `write_plan`, `read_todos` → `read_plan`, `add_todo` → `add_task`, and so on)[^pydantic-planning-docs] That is the upstreaming stage of the trajectory below happening to one named package. The capability itself is compiled in [Pydantic AI Harness planning](pydantic-ai-harness-planning.md); this page records only that its predecessor was a Vstorm package and that migration is a rename plus the loss of `create_storage(backend=...)` and `PlanEvent.timestamp`.

## The community-to-core arc

The post's thesis is a four-stage trajectory — community, endorsed, upstreamed, core — and it positions Vstorm at the third stage, contributing upstream while remaining a third-party package provider[^vstorm-v2-blog] This is the same graduation mechanism the [Harness](pydantic-ai-harness.md) page records for capabilities that prove broadly essential, viewed from the ecosystem side rather than the maintainer side.

## Endorsement in the Pydantic team's words

The post quotes Pydantic founder and CEO Samuel Colvin twice, describing Vstorm as partners who "actually build with Pydantic AI in production" and who "helped shape it – contributing extensions, pushing on the rough edges"[^vstorm-v2-blog] The quotes are attributed to external posts and are not independently archived in this capture.

## Limits

- The source is Vstorm-authored marketing for a commercial partnership; package counts ("roughly 20"), the "30+ production deployments" basis, and the maturity of each package are self-reported and were not checked against the repositories[^vstorm-v2-blog]
- The Harness README wiring is reported secondhand; the README itself was not fetched, so the exact reference-example configuration is unknown.
- The package list is illustrative, not exhaustive, and no package API or stability guarantee is documented here. `pydantic-ai-todo` is added from the Harness `Planning` reference page, which names it as a Vstorm package this page does not list and whose repository was not inspected[^pydantic-planning-docs]
- `stale_after` is short because endorsement status, upstreaming progress, and package names are version-bound and move quickly.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md) as its only composition interface.
- **Part of** the [Pydantic AI Harness](pydantic-ai-harness.md) ecosystem layer: Vstorm packages sit in the third-party tier that the Harness links and example-wires.
- **Contributes to** the [Pydantic AI v2 release](pydantic-ai-v2-release.md) adoption story, including its model-agnostic composition pitch.
- **Supplied the predecessor of** [Pydantic AI Harness planning](pydantic-ai-harness-planning.md): `pydantic-ai-todo`'s task-list feature set now ships as the first-party `Planning` capability, which supersedes it.

[^vstorm-v2-blog]: Nicholas Berryman, "Pydantic AI v2 and the road to production-grade agentic AI", Vstorm, published 2026-07-03. Sections: §"Where Vstorm fits: endorsed, linked, and upstreaming" (endorsement, Harness reference example, `pydantic_ai_summarization` and `pydantic_deep`, ~20 packages, the community-to-core arc, the Colvin quotes); §"Why this matters for production-grade agentic AI" (production-gap framing and `pydantic-deep` guest post). Local capture: `raw/pydantic-ai-v2-and-the-road-to-production-grade-agentic-ai/index.md` (revision 836bd3b1). Evidence class: **Reported** — a partner marketing post; no Vstorm package, GitHub repository, Harness README, or oss.vstorm.co page was inspected in this ingest.
[^pydantic-ai-v2]: Douwe Maan, "Pydantic AI v2: capabilities, a leaner core, and the Harness", Pydantic, published 2026-06-23, §"The Harness and a leaner core" (community capabilities, Vstorm endorsement, and upstreaming intent). Local capture: `raw/pydantic-ai-v2/index.md` (revision 836bd3b1). Evidence class: **Reported** — maintainer announcement corroborating the endorsement from the endorsing party's side.
[^pydantic-planning-docs]: Pydantic Docs, "Planning", <https://pydantic.dev/docs/ai/harness/planning/>; local capture `raw/harness/planning/index.md`, content digest sha256:13d1290b, no publication date, author or framework version. Lines 219–236 for the `pydantic-ai-todo` attribution (`vstorm-co/pydantic-ai-todo`, Vstorm), the feature set it contributes, the supersession, the tool rename table, and the removed `create_storage` and `timestamp`. Evidence class: **Reported** — vendor documentation; neither repository was inspected.
