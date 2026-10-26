---
title: "Debug production from Cursor with the Logfire MCP server"
author: "Laís Carvalho"
site: "Pydantic"
published: 2026-09-30T09:00:00.000Z
source: "https://pydantic.dev/articles/debugging-production-with-logfire-mcp-and-cursor"
domain: "pydantic.dev"
language: "en"
description: "Set up the Pydantic Logfire MCP server in Cursor, Claude Code, or Codex so your coding agent queries production traces in SQL, and see where it stops helping."
word_count: 2681
---

The bug report says checkout is failing. Cursor is open on the file you suspect, and [Pydantic Logfire](https://pydantic.dev/logfire) is open in another window on the trace that proves you suspect the wrong file. In between is you, moving stack traces from one to the other by hand and dropping most of the context along the way.

Your coding agent has read every line of your repository. It has never seen a single request your users made. So it guesses, and the guesses are plausible, and you spend the afternoon establishing which one was wrong.

[Marcelo Trylesinski](https://www.linkedin.com/in/marcelotryle/) and [Laura Summers](https://www.linkedin.com/in/summerscope/) ran [a live session](https://pydantic.dev/events/ask-your-traces) on this recently, showing how to use [Logfire](https://pydantic.dev/logfire) MCP to help with bug investigations.

## What is the Logfire MCP server?

The [Logfire MCP server](https://pydantic.dev/docs/logfire/guides/mcp-server/) is a hosted Model Context Protocol server that exposes your OpenTelemetry traces, logs, and metrics to any MCP client. It runs at `https://logfire-us.pydantic.dev/mcp` for US projects and `https://logfire-eu.pydantic.dev/mcp` for EU projects (the different Logfire instances) and it authenticates over OAuth in the browser or with a Logfire API key as a bearer token.

It exposes 51 tools across queries, dashboards, alerts, notification channels, issues, and feature-flag variables. One of them does nearly all the work: Marcelo, who helped build it, puts `query_run` at over 99% of all calls, because Pydantic Logfire stores spans as SQL, which makes investigations much easier since agents are very good at writing SQL.

## How do you set up the Logfire MCP server?

There are three routes in, all will take you under a minute. Pick the row that matches your editor.

| Client | Route in |
| --- | --- |
| Claude Code | `/plugins`, then install `logfire` from the official marketplace |
| Codex | Install [Logfire from the OpenAI plugin marketplace](https://chatgpt.com/plugins/plugin_asdk_app_6a9a83e37cc4819188896feeab8966ea), or add it from the CLI |
| Cursor and everything else | The remote server URL in your MCP config |

If you use Claude Code: run `/plugins`, find `logfire`, install, authenticate in the browser. You get the MCP server plus [skills](https://pydantic.dev/articles/pydantic-ai-logfire-claude-code-skills), for querying, instrumenting, and navigating the Logfire UI.

Codex users get the same content from the [Logfire plugin on the OpenAI marketplace](https://chatgpt.com/plugins/plugin_asdk_app_6a9a83e37cc4819188896feeab8966ea). Open the listing, install it, and log in. The CLI route reaches the same plugin through the published `pydantic/skills` marketplace:

```bash
codex plugin marketplace add pydantic/skills --ref main
codex plugin add logfire@pydantic-skills
codex mcp login logfire
```

Start a new Codex conversation afterward so the MCP tools load.

Everywhere else, point at the remote server directly. There is no token to paste into a file you might later commit. For Cursor, that is `.cursor/mcp.json` in your project root:

```json
{
    "mcpServers": {
        "logfire": {
            "url": "https://logfire-us.pydantic.dev/mcp"
        }
    }
}
```

Use `https://logfire-eu.pydantic.dev/mcp` if your project lives in the EU region, or your own URL if you self-host. In Claude Code without the plugin it is two commands:

```bash
claude mcp add --transport http logfire https://logfire-us.pydantic.dev/mcp
claude mcp login logfire
```

For CI, a container, or anywhere without a browser, authenticate with a Logfire API key as a bearer token. [Read scope](https://pydantic.dev/docs/logfire/instrument/typescript/reference/cli/#read-tokens) covers everything up to the section on writing.

Then verify. A question to start can be: "can you check whether I have data in Logfire?" You want a project name and a row count back. In the demo video, Claude went further unprompted and ran a query grouping records by service with an exception count, because it could see which tools it had.

## Why does the Logfire MCP server use SQL?

Logfire uses SQL because models write SQL better than they navigate bespoke query APIs. Logfire is built on OpenTelemetry and stores spans in a queryable `records` table, so there is no filter DSL for an agent to learn and no dropdown vocabulary to guess at.

That design decision is why `query_run` carries over 99% of traffic, and why it has its own eval suite across several models and coding agents. The tool description instructs the agent to fetch the SQL schema reference first if it does not already hold one, so schema grounding happens without you configuring anything. Hallucinated column names cause most failed observability queries, and this is the fix.

A first pass at a failing endpoint looks like this:

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

You will rarely write that yourself, but you should be able to read it. Marcelo's take is that he does not worry about the SQL and mostly asks the agent to explain the query back.

Some caveats: Logfire's dialect is the DataFusion flavor, and models sometimes reach for a function from a dialect they have seen more of, like ClickHouse. And on a project with a lot of spans, an agent left alone will happily request a two-month window when it needed the last hour.

The latter scenario has a check layer to help: when the query planner can see a query will run long, it fails fast with a tool error. The agent reads the error as output, narrows the window or adds a filter, and calls it again. That retry happens constantly, and it is mostly invisible to the user.

## What does a debugging session look like?

The demo app was a forum where LLM agents argue with each other, instrumented with Logfire and seeded with real exceptions. The sequence ran in six steps.

1. **Find the problem.** The opening question was just whether there was data. The answer came back with exceptions already surfaced, including a `ZeroDivisionError`.
2. **Fix it.** "Investigate and fix the zero division error." The agent queried for the exception, got the stack trace and the exact line from the span, opened the file, added the guard, and removed the now unreachable handler.
3. **Ask something a stack trace cannot answer.** Laura asked which agent in the forum was most verbose. The answer came back as the historian, which surprised no one *who has met a historian*.
4. **Make the one-off durable.** "Create a dashboard showing verbosity of the agents over time." It built one measuring average visible output tokens per agent turn, and added panel descriptions on request.
5. **Add the alert.** Rather than specifying it, Marcelo asked for a suggestion: "I've had a lot of 500s lately, can you suggest an alert for it?" The agent proposed a query filtered by service and route on 5xx status with a count threshold above 20 requests, and created it.
6. **Close the loop.** Asked for a notification channel pointing at an ngrok tunnel, the agent created the webhook channel too. The receiver on the far end was wired to spawn a coding agent on the alert payload with read-only tools. Claude configured an alert that pages Claude.

## What can you ask beyond errors?

Some of the questions you can answer with the Logfire MCP are the ones you would not build a dashboard panel for: token counts per route, whether a code path fired at all. Nobody should build a chart to answer a question they plan to ask once.

Latency by model and operation, for when a provider quietly degrades:

```sql
SELECT attributes->>'gen_ai.request.model' AS model,
       attributes->>'gen_ai.operation.name' AS operation,
       count(*) AS spans,
       avg(duration) AS avg_duration
FROM records
WHERE attributes->>'gen_ai.request.model' IS NOT NULL
GROUP BY model, operation
ORDER BY avg_duration DESC
```

Anything under `gen_ai.*` slices the same way, so token counts, providers, tool names, and model reasoning sit in the same table as your HTTP spans. If it renders in a span in the Logfire UI, your agent can query it. Reasoning traces included.

The other habit worth forming is asking whether a code path is firing at all. It sounds too simple to be useful. It catches the deployment that merged green, passed CI, and does nothing.

## Can the Logfire MCP server write as well as read?

Yes, the tool surface has read and write capabilities. An agent with the right write scopes can create and modify five kinds of object, and triage a sixth:

- **Dashboards**, including panels, variables, and layout groups
- **Alerts**, with their queries, thresholds, and evaluation windows
- **Notification channels**, webhook and Opsgenie
- **Managed feature-flag variables**, including versions, labels, and rollout
- **Notification schedules**
- **Issue states**, which it changes on existing issues rather than opening new ones

When you fix an incident you know exactly which signal would have caught it, and that knowledge has a half-life of about a day. Creating the alert before the signal is lost is what improves system resilience. It's the you-of-today preventing the issues of tomorrow.

Two caveats on credentials. An agent deletes a dashboard as fluently as it builds one, so grant write scopes only when the session needs them. And a read token is not the harmless one: traces and logs carry user-controlled content, model payloads, and tool arguments, which an agent can surface to the wrong place or read as instructions. Scope and protect both.

## When should the agent write Python instead?

Reach for the `exec` tool when a task needs more than about three chained queries. Six sequential tool calls means six round trips, each returning JSON the model must read before choosing the next, all accumulating in context.

Logfire's code-execution endpoint exists for this. It is a separate MCP server from the 51-tool one, with three tools in total. `exec` takes Python and runs it server-side in [Monty](https://pydantic.dev/articles/pydantic-monty), with every one of those 51 tools wrapped as a function inside the sandbox, `help` lets the agent discover what those functions are, and `results` retrieves output from earlier runs. Only the printed summary crosses the wire. Fetch the alert, pull metrics and traces and deploys with `asyncio.gather`, correlate them, print four lines. Intermediate data never touches your context window.

The savings are large. Anthropic has reported reductions from 150,000 tokens to 2,000 in comparable setups, a 98.7% cut, and Cloudflare found a full MCP implementation of their 2,500-endpoint API would have consumed 1.17 million tokens before the first user message. Jiri wrote up our version in [Your agent would rather write code](https://pydantic.dev/articles/your-agent-would-rather-write-code). His conclusion: it wins decisively on multistep composition, and plain tool calls stay faster for a single lookup.

## Where does the Logfire MCP server stop helping?

The Logfire MCP server localizes bugs that appear in a trace, and it does not find bugs that only appear as a pattern across files. Four limits worth knowing:

**A trace pointing at a line is the best case.** The agent is excellent when evidence localizes to one file, as the zero division fix did. It is much weaker at "this same missing cleanup exists in nine components", because nothing in a single trace tells it to look for the pattern.

**Shipping the fix is not evidence the fix worked.** The agent knows the code changed. It has no idea what production did afterward. Query the traces again a day later and compare intended against actual. AutonomyAI automated this, and it is where their 12 silent no-op deployments came from.

**Ask clarifying questions.** Laura's take is to tell the agent a query smells and ask it to explain itself, or to ask an alert query which conditions would make it fire and which would not. A long query full of nested CTEs usually means the model overcomplicated something.

**Grounding raises the floor.** The model will argue based on info from real spans, but it will still draw confident conclusions from queries that quietly excluded half the traffic.

## Which teams use the Logfire MCP server in production?

Dosu and AutonomyAI both run the Logfire MCP server as their primary debugging surface. Dosu reports the time saved; AutonomyAI reports the regressions caught.

[Dosu](https://pydantic.dev/case-studies/dosu) runs 54 agents across more than 697,000 production runs and does most debugging inside the coding agent rather than the Logfire UI. Some traces run past 25 minutes, which is a lot of tool calls to scroll through by hand. Across one 14-day period the team worked through 193 production traces this way before the MCP server changed the workflow.

> "Being able to ask questions right within our coding agent and get cited metrics back has been invaluable. It's rare that I have to really dig into Logfire unless it's a really gnarly problem."
> 
> — Taylor Dolezal, Head of OSS at Dosu

Dosu puts the cut in debugging time at 90%, with time to root cause falling from about an hour to a few minutes, and credits the Logfire agents dashboard with surfacing prompt-caching bugs worth over $30,000 a year.

[AutonomyAI](https://pydantic.dev/case-studies/autonomyai) pointed their own agents at it. Their agents query Logfire while building to check what a code path did, and again in the days after a change merges. Over five weeks that post-merge pass ran across 105 merged PRs, surfaced 65 issues from real traffic, and caught 12 deployments that merged clean and were silently doing nothing. Logfire ingested over 35 million spans in three weeks, and runs about 3.5x cheaper than the Datadog deployment it sits alongside.

> "Most of our engineers and our internal systems now use the Logfire MCP for basically everything. We barely open the Logfire UI, just because we are so happy with MCP."
> 
> — Tammuz Dubnov, co-founder and CTO at AutonomyAI

## How to get started?

Install the plugin or add the URL, authenticate, and ask your agent what broke in production this week. If you are not sending traces yet, the [Logfire docs](https://pydantic.dev/docs/logfire/) cover Python, JavaScript, Rust, and anything else that speaks OpenTelemetry. The free tier is plenty to answer the question.

Your coding agent already knows your code by heart. Give it the part your code cannot tell it.

## Frequently asked questions

**What is the Logfire MCP server?** The Logfire MCP server is a hosted Model Context Protocol server that exposes Pydantic Logfire's OpenTelemetry traces, logs, and metrics to an MCP client such as Cursor, Claude Code, or Codex. It lets a coding agent query production data in SQL and return answers with trace IDs attached, without anyone opening the Logfire UI.

**How do I connect Logfire MCP to Cursor?** Add the remote server to `.cursor/mcp.json` in your project root with the URL `https://logfire-us.pydantic.dev/mcp`, or `https://logfire-eu.pydantic.dev/mcp` for EU projects. Cursor prompts for browser authentication the first time it calls a tool. Nothing needs installing locally.

**Does the Logfire MCP server work with Claude Code and Codex?** Yes. Claude Code has an official marketplace plugin, installed by running `/plugins` and selecting `logfire`, which bundles the MCP server with skills for querying, instrumenting, and navigating Logfire. Codex installs the same content from the [Logfire plugin on the OpenAI marketplace](https://chatgpt.com/plugins/plugin_asdk_app_6a9a83e37cc4819188896feeab8966ea), or from the CLI by adding the `pydantic/skills` marketplace, running `codex plugin add logfire@pydantic-skills`, then `codex mcp login logfire`.

**Can an AI agent write SQL against production traces reliably?** Mostly, with two known failure modes. Models sometimes use functions from other SQL dialects, since Logfire uses the DataFusion flavor, and they sometimes request time windows far wider than needed. The `query_run` tool description instructs the agent to fetch the schema reference before querying, and Logfire fails long-running queries fast so the agent retries with a narrower one.

**Can the Logfire MCP server create dashboards and alerts?** Yes. Beyond querying, it creates and edits dashboards, alerts, notification channels, notification schedules, and managed feature-flag variables, and it moves existing issues between states. This lets a debugging session end with permanent monitoring rather than a one-off answer. Scope credentials carefully in both directions: an agent deletes a dashboard as easily as it creates one, and read access alone exposes whatever user content your traces carry.

**How much time does the Logfire MCP server save?** Dosu reports a 90% reduction in debugging time, with time to root cause dropping from roughly an hour to a few minutes across 54 agents and more than 697,000 production runs. AutonomyAI's post-merge review surfaced 65 issues and caught 12 silently failed deployments over five weeks.

**Does Logfire require Python or Pydantic AI?** No. Logfire is built on OpenTelemetry and ingests traces from any stack that emits OTel data, including JavaScript, Rust, and Go. Pydantic AI ships with built-in Logfire instrumentation, which makes setup a single step, but it is not a requirement.
