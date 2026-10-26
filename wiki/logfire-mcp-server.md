---
type: Concept
title: Logfire MCP server
description: Pydantic Logfire's hosted MCP server — a SQL-first trace query surface for coding agents, its three setup routes, its write powers, and the separate Python code-execution server, plus the investigations it cannot do.
tags: [ml, logfire, mcp, observability, debugging]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:40:00Z }
stale_after: 2027-01-30
sources:
  - id: logfire-mcp-debugging-2026
    resource: ../raw/debugging-production-with-logfire-mcp-and-cursor/index.md
    scope: ../raw/debugging-production-with-logfire-mcp-and-cursor/
    kind: article
    revision: sha256:4b0bb14153999e7b0a9b223758fd0b17a76bd6073592f89215a3d83fcaa3e562
    title: "Debug production from Cursor with the Logfire MCP server"
---

The Logfire MCP server is a hosted Model Context Protocol server that exposes Logfire's OpenTelemetry traces, logs and metrics to an MCP client, so a coding agent can query production data over SQL and return answers with trace IDs attached instead of a person moving stack traces between windows[^logfire-mcp-debugging-2026] It is framework-agnostic — Logfire ingests OTel from any stack, and Pydantic AI's built-in instrumentation only shortens setup[^logfire-mcp-debugging-2026] This page records Pydantic's own account of the server; no client, project or query was exercised here.

## Endpoint, auth and tool surface

Projects in the US use `https://logfire-us.pydantic.dev/mcp` and EU projects use `https://logfire-eu.pydantic.dev/mcp`; a self-hosted Logfire supplies its own URL. Authentication is OAuth in the browser or a Logfire API key sent as a bearer token[^logfire-mcp-debugging-2026]

The server exposes 51 tools across queries, dashboards, alerts, notification channels, issues and feature-flag variables. One tool dominates: `query_run` is put at over 99% of all calls by Marcelo Trylesinski, who helped build it, because Logfire stores spans in a SQL-queryable table and models write SQL well[^logfire-mcp-debugging-2026]

## Three setup routes

| Client | Route in |
| --- | --- |
| Claude Code | `/plugins`, then install `logfire` from the official marketplace; the plugin bundles the MCP server with skills for querying, instrumenting and navigating Logfire |
| Codex | The Logfire plugin on the OpenAI marketplace, or the `pydantic/skills` marketplace over the CLI |
| Cursor and other clients | The remote server URL in the client's MCP configuration |

For Cursor, the documented configuration is `.cursor/mcp.json` in the project root with `mcpServers.logfire.url` set to the regional endpoint; Cursor prompts for browser authentication on the first tool call. Claude Code without the plugin uses `claude mcp add --transport http logfire <url>` followed by `claude mcp login logfire`. The Codex CLI route adds the marketplace with `codex plugin marketplace add pydantic/skills --ref main`, installs with `codex plugin add logfire@pydantic-skills`, logs in with `codex mcp login logfire`, and requires a new conversation before the tools load[^logfire-mcp-debugging-2026]

For CI, a container or anywhere without a browser, a Logfire API key with read scope is the credential. The suggested first check is to ask whether Logfire has data at all and expect a project name and a row count back; the article reports the demo client going further and grouping records by service with an exception count because it could see which tools it had[^logfire-mcp-debugging-2026]

## SQL is the interface

Logfire stores spans in a `records` table rather than behind a filter DSL or a dropdown vocabulary, which is the stated reason `query_run` carries almost all traffic[^logfire-mcp-debugging-2026] A first pass at a failing endpoint is ordinary SQL:

```sql
SELECT start_timestamp,
       http_route,
       http_response_status_code,
       exception_type,
       exception_message,
       trace_id
FROM records
WHERE is_exception
  AND http_route = '/api/chat'
ORDER BY start_timestamp DESC
LIMIT 20
```

Two failure modes are named. Models sometimes reach for a function from a dialect they have seen more often, such as ClickHouse, because Logfire's dialect is DataFusion; and an agent left alone will request a two-month window when the last hour would do. The `query_run` description instructs the agent to fetch the schema reference first when it lacks one, because hallucinated column names cause most failed observability queries[^logfire-mcp-debugging-2026] The query planner also fails a query fast when it can see the query will run long, and the agent reads the tool error, narrows the window or adds a filter, and retries — a loop the article says happens constantly and mostly invisibly[^logfire-mcp-debugging-2026]

Because the spans share one table, anything under `gen_ai.*` slices the same way. The article's example compares latency by model and operation, and states that token counts, providers, tool names, reasoning traces and HTTP spans are all queryable if they render in a span in the Logfire UI[^logfire-mcp-debugging-2026] The article also states that `query_run` has its own eval suite across several models and coding agents[^logfire-mcp-debugging-2026] A second habit it recommends is asking whether a code path fired at all — the check that catches a deployment which merged green, passed CI and does nothing[^logfire-mcp-debugging-2026]

## A debugging session that ends in monitoring

The worked session runs six steps: find the problem from whether data exists (a `ZeroDivisionError` surfaces immediately); fix it from the span's stack trace and exact line; ask a question a stack trace cannot answer (which agent was most verbose); turn the one-off into a dashboard measuring average visible output tokens per agent turn; ask for an alert suggestion rather than specifying one, and get a 5xx query with a count threshold; and create a webhook notification channel pointing at an ngrok tunnel whose receiver spawns a coding agent with read-only tools. The article's summary is that the coding agent configured an alert that pages a coding agent[^logfire-mcp-debugging-2026]

The durable point is the closing move: the signal that would have caught an incident is known at fix time, and creating the alert then is what improves resilience rather than leaving the diagnosis as a one-off answer[^logfire-mcp-debugging-2026]

## Write powers and the credential boundary

With write scopes, the server can create and modify dashboards (panels, variables, layout groups), alerts (queries, thresholds, evaluation windows), notification channels (webhook and Opsgenie), managed feature-flag variables (versions, labels, rollout), and notification schedules, and it can move existing issues between states rather than open new ones[^logfire-mcp-debugging-2026]

The article pairs that power with two cautions. An agent deletes a dashboard as fluently as it builds one, so write scopes should be granted only when the session needs them. And read access is not the harmless half: traces and logs carry user-controlled content, model payloads and tool arguments, which an agent can surface to the wrong place or read as instructions[^logfire-mcp-debugging-2026] **Synthesis:** that is a prompt-injection surface as much as a data-exposure one, and it follows from putting production content inside a model's context.

## When to hand the work to Python

Reach for the separate code-execution server when a task needs more than about three chained queries, because six sequential tool calls mean six round trips and six JSON payloads accumulating in context. That server has three tools: `exec` runs Python server-side in Monty with all 51 tools wrapped as functions, `help` lets the agent discover those functions, and `results` retrieves output from earlier runs. Only the printed summary crosses the wire, so intermediate data never enters the context window[^logfire-mcp-debugging-2026]

The article cites Anthropic reporting a reduction from 150,000 tokens to 2,000 in a comparable setup (98.7%), and Cloudflare finding that a full MCP implementation of its 2,500-endpoint API would have consumed 1.17 million tokens before the first user message. The article quotes Jiri's conclusion that code execution wins decisively on multistep composition while plain tool calls stay faster for a single lookup[^logfire-mcp-debugging-2026] The token figures are other vendors' reports relayed here, not measurements from this source.

## Where the server stops helping

Four limits bound the approach[^logfire-mcp-debugging-2026]:

- **A trace pointing at a line is the best case.** The agent is strong when evidence localises to one file and weak at "the same missing cleanup exists in nine components", because no single trace says to look for the pattern.
- **Shipping the fix is not evidence the fix worked.** The agent knows the code changed, not what production did afterward; querying the traces again a day later is the missing verification, and AutonomyAI's automated post-merge pass is where its 12 silent no-op deployments surfaced.
- **The query itself needs review.** A long query full of nested CTEs usually means the model overcomplicated something, so asking the agent to explain its query or to state which conditions would make an alert fire and which would not is part of the workflow.
- **Grounding raises the floor, not the ceiling.** The model argues from real spans but will still draw confident conclusions from queries that quietly excluded half the traffic.

## Reported outcomes

Dosu runs 54 agents across more than 697,000 production runs, some traces past 25 minutes, and worked through 193 production traces in one 14-day period before the MCP server changed the workflow; it reports a 90% cut in debugging time, root cause falling from about an hour to a few minutes, and prompt-caching bugs worth over $30,000 a year surfaced by the Logfire agents dashboard[^logfire-mcp-debugging-2026] AutonomyAI points its own agents at Logfire while building and again in the days after a merge; over five weeks that post-merge pass covered 105 merged PRs, surfaced 65 issues from real traffic and caught 12 deployments that merged clean and did nothing, with Logfire ingesting over 35 million spans in three weeks and running about 3.5 times cheaper than the Datadog deployment beside it[^logfire-mcp-debugging-2026]

These are customer figures relayed by the vendor, not independently audited.

## Contradictions

- **SQL dialect.** Earlier Pydantic material compiled in [Logfire agent optimization](logfire-agent-optimization.md) and [Pydantic AI observability](pydantic-ai-observability.md) calls the query surface PostgreSQL-compatible, while this article names DataFusion and warns that models import functions from other dialects[^logfire-mcp-debugging-2026] **Synthesis:** a PostgreSQL-compatible core with DataFusion-specific gaps would reconcile the two, but no query was executed to establish which functions differ; neither wording is chosen here.

## Limits

- The whole page rests on one Pydantic article by Laís Carvalho; no independent source corroborates the tool count, setup commands, write surface, token figures or customer outcomes, and the article is published by the vendor that sells Logfire[^logfire-mcp-debugging-2026]
- No MCP client was configured, no server authenticated, no query run, and no dashboard, alert, channel or `exec` call created; the SQL blocks were not executed and the endpoint URLs were not fetched[^logfire-mcp-debugging-2026]
- The article names no Logfire or Pydantic AI version, and a hosted 51-tool surface can change without a release note here; the `stale_after` date reflects that rather than a known expiry[^logfire-mcp-debugging-2026]
- External documentation links in the capture — the MCP server guide, the Logfire instrumentation docs, the Monty article and the token-reduction write-ups — were read as links, not followed[^logfire-mcp-debugging-2026]
- Evidence class: **Reported**.

## Relationships

- **Queries** the spans described in [Pydantic AI observability](pydantic-ai-observability.md), turning them into SQL answers with trace IDs for a coding agent.
- **Operationalizes** the trace-query part of [agent observability requirements](agent-observability-requirements.md): the correlated trace is interrogated ad hoc instead of through a purpose-built dashboard.
- **Shares the trace store with** [Logfire agent optimization](logfire-agent-optimization.md), whose optimizer and managed configuration act on the same runs.
- **Writes into the surface** [Logfire dashboard design](logfire-dashboard-design.md) **describes**: its write scopes create dashboard panels, variables and layout groups, so programmatic dashboards land inside that page's palette, dithering and row-alignment constraints.
- **Ships beside** [Pydantic AI coding-agent skills](pydantic-ai-coding-agent-skills.md): the Claude Code `logfire` plugin installs this server together with the instrumentation skills, and the `pydantic/skills` marketplace serves both routes.
- **Runs opposite to** [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md): that page is Pydantic AI consuming an MCP server, this one is a hosted MCP server consumed by a coding agent.

[^logfire-mcp-debugging-2026]: Laís Carvalho, "Debug production from Cursor with the Logfire MCP server", Pydantic, published 2026-09-30, 2,681 words; §"What is the Logfire MCP server?" (raw lines 19–23) for the hosted-server definition, the US/EU endpoints, OAuth and API-key auth, the 51-tool surface and `query_run`'s >99% share; §"How do you set up the Logfire MCP server?" (lines 25–68) for the Claude Code, Codex and Cursor/remote routes, the API-key read-scope path, and the "do I have data?" verification; §"Why does the Logfire MCP server use SQL?" (lines 70–96) for the `records` table, the absence of a filter DSL, the DataFusion dialect, schema-reference grounding, the hallucinated-column failure and fail-fast planning; §"What does a debugging session look like?" (lines 98–107) for the six steps and the agent-pages-agent ending; §"What can you ask beyond errors?" (lines 109–128) for ad hoc questions, `gen_ai.*` attributes and reasoning traces; §"Can the Logfire MCP server write as well as read?" (lines 130–143) for the writable object families, issue triage and the credential caveats; §"When should the agent write Python instead?" (lines 145–151) for the separate `exec`/`help`/`results` server, Monty execution, the printed-summary boundary and the cited token figures; §"Where does the Logfire MCP server stop helping?" (lines 153–163) for the four limits; §"Which teams use the Logfire MCP server in production?" (lines 165–181) for the Dosu and AutonomyAI figures. Local capture: `raw/debugging-production-with-logfire-mcp-and-cursor/index.md`, content digest sha256:4b0bb141. Evidence class: **Reported** — vendor article; no server, client, project, query, dashboard, alert or `exec` call was exercised.
