---
title: "Code mode vs tool calling: a 5,276-run benchmark"
author: "Michael Pfaffenberger"
site: "Pydantic"
published: 2026-10-28T09:00:00.000Z
source: "https://pydantic.dev/articles/why-code-mode-is-the-future?utm_source=X&utm_medium=social&utm_campaign=blog-why-code-mode-is-the-future"
domain: "pydantic.dev"
language: "en"
description: "Code mode vs tool calling across 5,276 graded Pydantic AI runs on eight models: on long tasks it was 58% cheaper, 51% faster and 16 points more often right."
word_count: 5089
---

![Illustration. On the left, tool calling: a model and its tools trade round trip after round trip, and the context the model re-reads grows on every lap. On the right, code mode: the model writes one Python program that pages through a cart, filters it and removes every expensive item, the program fans out into twelve tool calls, and only the answer comes back](assets/hero.svg)

Everyone I talk to has an opinion about code mode right now. Mine was lit by Prime Intellect's [Prime Agent](https://www.primeintellect.ai/blog/prime-agent), a coding harness built around a persistent REPL, and by Alex Zhang's [speculative programmatic tool calling](https://alexzhang13.github.io/blog/2026/spec-ptc/), which (among other things) can run tools while the model is still streaming code. [Cloudflare](https://blog.cloudflare.com/code-mode/) has one. [Anthropic](https://www.anthropic.com/research/code-execution-with-mcp) has one. We've had a few of our own, from [MCP code execution](https://pydantic.dev/articles/your-agent-would-rather-write-code) to [Pydantic Monty](https://pydantic.dev/articles/pydantic-monty). Coding agents are moving the same way: [OpenCode 2](https://opencode.ai/v2/docs/mcp-servers/) now sends MCP tools through Code Mode by default, and [Pi](https://pi.dev/docs/latest/codemode) ships a `codemode` tool. The pitch usually goes like this: stop making the model call your tools one at a time, let it write a little program that calls them instead, and everything gets cheaper, faster and better.

I believe that. But almost every number I'd seen came from agents with hundreds of tools or huge payloads, and many agents in the wild are boring: a handful of CRUD tools and a job to do. So I built a benchmark out of exactly that. Five small [Pydantic AI](https://pydantic.dev/docs/ai/overview/) apps, single-item tools only, and three kinds of work: everyday requests, long multi-step jobs, and five tasks I could dial from 5 items to 200. Eight models, code mode off and on, 5,276 graded runs on an internal benchmark.

The short version: the longer the task, the bigger the win. And it gets big.

## TL;DR

- **On long tasks, code mode roughly halved cost and wall time.** Across all eight models: cost **\-58%**, wall time **\-51%**, success **+16.0 points**. Without code mode 67 of 288 runs failed; with it, 21.
- **It scales.** For gpt-6.1-sol, every 100 extra items cost 30 to 79 seconds and $0.04 to $0.07 per run without code mode. With it: 4 to 9 seconds on four of the five tasks, and under a cent on three. At 200 items, code mode was 47% to 75% cheaper.
- **Correctness falls off without it.** From 5 items to 200, success without code mode dropped from 92-100% to 62-79%. With code mode it was 92-100% at 200.
- **It isn't about round trips.** Models already batch: one response carried 200 tool calls. At 200 items, averaged over the eight models, model requests fell by between 1% and 22% per task; deepseek-v4.1-flash on its own fell much further. What code mode cuts is what goes *into* each request.
- **Small jobs pay a tax.** At 5 items code mode cost more on three of the five tasks (+21% to +38%). On the 50 everyday tasks it was 16% cheaper overall, but success was flat (+1.6 points, noise).
- **It's sandboxed, and it leaves a trail.** In Pydantic AI Harness the model's code runs in Monty, which starts with no access to the host and, by default, stops any snippet after 30 seconds of execution time or at a 256 MiB heap. With Pydantic [Logfire](https://pydantic.dev/logfire) [tracing the agent](https://pydantic.dev/logfire/llm-observability), every tool call that code makes shows up as its own span.

How much faster and cheaper each extra 100 items are with code mode on, for gpt-6.1-sol:

| Task | Faster | Cheaper |
| --- | --- | --- |
| cart | 7x | 8x |
| calendar | 9x | 25x+ |
| chat | 5x | 2.4x |
| kanban | 20x | 11x |
| inventory | 2.2x | 2.2x |

My read: models are much better at writing a loop than at being one, and the gap grows with the length of the task.

## The loop, and why it hurts

In a normal tool-calling agent, the model picks a tool, emits some JSON, stops, waits for the harness to run it, reads the result, and picks again. The model sits in the middle of every step, and the costs compound: tool definitions crowd the context, every intermediate result flows through the model, and, the usual story goes, every tool call is another model turn that resends the whole growing context.

Code mode flips it. The tools become functions inside a sandbox, the model writes one program that loops and branches over them, and only the result comes back. In [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/code-mode/) that sandbox is [Monty](https://pydantic.dev/articles/pydantic-monty), our Python interpreter written in Rust, and the model sees a single `run_code` tool.

![Schematic of one task done two ways. Tool calling: a loop of model, tool call and result, 25 tool calls, with the context the model re-reads growing across five requests. Code mode: the model calls run_code once per step, a Monty sandbox makes 3 list_items calls and 22 remove_item calls and does the filtering in Python, and the context stays small apart from the code mode guidance added to every request](assets/loop-vs-code.svg)

Here's one of the 50 tasks, verbatim: *"can you get rid of everything in my cart that costs more than $50 a piece? it's getting out of hand"*. The cart has 122 lines, a list tool that returns at most 50 per page, and a remove tool that takes one id. 22 lines need to go. Without code mode that's three pages of listing and 22 removes, every one of them chosen by the model. With code mode, it's this:

```python
import asyncio

items, offset = [], 0
while offset is not None:
    page = await list_items(offset=offset, limit=50)
    items += page["items"]
    offset = page["next_offset"]

pricey = [i for i in items if i["unit_price"] > 50]
await asyncio.gather(*(remove_item(item_id=i["id"]) for i in pricey))
len(pricey)
```

The model never reads the 100 cheap lines. It doesn't have to remember which ids it already removed. The comparison `> 50` is done by Python, not by a language model squinting at a float.

## Code mode with guardrails

That program is code a model wrote, and something has to run it. What that something lets the code touch is the biggest design decision in code mode.

Prime Agent makes the open choice. Its model's only tool is a persistent IPython kernel, and the rest of the harness, sub-agents included, lives in that kernel as functions. An IPython kernel is a full Python process: unless something around it says otherwise, the code can import any library, read and write files and open network connections. For a coding assistant on your own machine, that's what you want. It's not something I'd put in a web server and let every user's prompt drive.

Pydantic AI Harness makes the opposite choice. `CodeMode` runs the model's program in [Monty](https://pydantic.dev/articles/pydantic-monty), our Python interpreter written in Rust, which starts from nothing and adds only what you allow:

- **No host access by default.** Sandboxed code [starts with no access](https://pydantic.dev/docs/ai/harness/code-mode/#filesystem-and-os-access) to the host's files, environment or clock, and there is no network. If the agent needs a directory, an environment variable or the time, you grant it per request. This benchmark granted the built-in `OSAccess` handler: an in-memory filesystem and environment, and the host clock.
- **Your tools are the way out.** The program reaches the world through the functions you register, plus any OS access you grant it, and each tool call goes through Pydantic AI to your real tool. It can do what those allow, and nothing else.
- **Hard limits.** By default each `run_code` snippet gets 30 seconds of execution time and a 256 MiB heap ([details](https://pydantic.dev/docs/ai/harness/code-mode/)), which is what stops a runaway loop.
- **Fast to start.** Each Monty session runs in a local worker process, and a [new sandbox](https://github.com/pydantic/monty) takes under a millisecond from a running pool, so the guardrails don't add a container start to every snippet.

So you get code mode with guardrails. Every code mode run in this benchmark ran in Monty.

## The code is the graph

Samuel wrote a whole post about this, [The code is the graph](https://pydantic.dev/articles/the-code-is-the-graph), and if you build agents you should read it. His argument is that graph libraries rebuild control flow badly: " `if` is a branch. `for` is a loop. A function call is an edge", and `asyncio.gather` is a fan-out and a join. Or in his words about a five-line example: "Fan out, join, branch. That is a graph, and it's also a Python function."

The program above is exactly that. Here's the graph it encodes:

![A ten-line Python program that pages through a cart, filters lines over $50, removes them with asyncio.gather and returns the count, next to the graph it encodes: a list_items node with a next-page cycle, a filter node, a fan-out to 22 remove calls, a join, and the answer. The while loop is the cycle, the comprehension is the filter, gather is the fan-out and the return value is the join](assets/code-is-the-graph.svg)

I wrote that program for the figure, but the models write the same shape on their own in the benchmark, at run time, for a task they've never seen (in one cart run, gpt-6.1-sol spread it over three `run_code` calls). Nobody drew that graph in advance. That's the bit that makes me think code mode is where agents are going: the model isn't just calling your tools more cheaply, it's designing the workflow on the fly.

But this is a blog post with a benchmark in it, so let's find out whether any of that is true.

## The benchmark

The benchmark is trivial on purpose. Five tiny Pydantic AI apps: a shopping cart, a calendar, a chatroom, a kanban board and an inventory system. Each one has only single-item CRUD tools (list, get, create, update, delete), with paginated lists. No shell, no filesystem, no bulk endpoints. If the agent wants to change 200 things, it has to make 200 calls, or write a loop.

No single step here is hard. What's hard is doing an easy step a few hundred times, in the right order, without losing count, and that's the part I wanted to isolate: iteration over a long horizon. The code is the graph. Let your agent write the graph.

On top of those apps sit three tiers of work:

![The benchmark design. Five apps (cart, calendar, chat, kanban, inventory) with single-item CRUD tools only, and three tiers, each run on eight models. Everyday: 50 tests, 10 per app, 4 reps, 3,500 runs, about 13 tool calls per run without code mode. Long horizon: 12 multi-step tests over 60 to 500 records, 3 reps, 576 runs, about 68 tool calls per run. Scaling: one task per app at N = 5, 20, 50, 100 and 200 items, 3 reps, 1,200 runs, 168 tool calls per run at N = 200. Each tile is one tool call. 5,276 graded runs, deterministic graders, no LLM judge](assets/benchmark-design.svg)
- **Everyday:** 50 tests, ten per app. Single edits, bulk changes, rules with branches, lookups and sums. Without code mode, a run made about 13 tool calls.
- **Long horizon:** 12 multi-step jobs over 60 to 500 records, two per app and two that cross apps. *"Alex is leaving the team. go through Alex's open tasks (not done) in order of id: if it's urgent or high priority, give it to whoever has the fewest open points at that moment..."* About 68 tool calls per run.
- **Scaling:** one task per app, with the same rule at N = 5, 20, 50, 100 and 200 items. *"I have a pile of meeting invites I never answered. for each one: accept it if it's on a weekday and ends by 5pm, decline it if it's on a weekend or ends after 5pm."* At N = 200, runs without code mode averaged 168 tool calls.

Each app is a Pydantic AI agent. With code mode on, it gets Pydantic AI Harness's [`CodeMode`](https://pydantic.dev/docs/ai/harness/code-mode/) capability with [eager execution](https://pydantic.dev/docs/ai/harness/code-mode/#eager-execution), which can start running a complete statement before the model finishes writing the `run_code` call. With code mode off, the same agent calls the same tools directly. Everything was pinned to one commit, and code mode was flipped with a single setting, so the only difference between arms is code mode itself. The prompts are written the way a person actually types, and every run is graded by a deterministic oracle: the app's end state has to match the expected state exactly (money within a cent), and the reply has to contain the right numbers. No LLM judge.

> [!note] Note
> - **Availability:** the benchmark code isn't public, so this note gives the full setup: versions, models, cost, arms, runs, validation and statistics, plus its known warts.
> - **System under test:** Pydantic AI `2.56.1.dev13` and Pydantic AI Harness `0.56.1.dev13`, both built from `pydantic/pydantic-ai` commit `b82f0f258f4d`, the same settings in every arm apart from code mode.
> - **Models:** `gpt-6.1-sol`, `gpt-6-luna` and `gpt-6-astra` through a Codex subscription, `claude-sonnet-5-5` and `claude-haiku-5-5` through a Claude Code subscription, `muse-spark-1.3-contributor` and `muse-wonder-1.0-contributor` through Meta's contributor API, and `deepseek-v4.1-flash` on our own vLLM server. All eight ran every tier, each with its provider's default settings.
> - **Cost:** API list prices from `genai-prices` for the GPT and Claude models. It has no prices for the other three, so their runs are priced from their recorded tokens: the Muse models at Meta's standard list prices for `muse-spark-1.3` and `muse-wonder-1.0` (not the cheaper contributor rates), and `deepseek-v4.1-flash` at its price in OpenRouter's model catalog on October 22, 2026 ([archived copy](https://web.archive.org/web/20261023141351/https://openrouter.ai/api/v1/models)): $0.30 per million input tokens, $0.006 cached and $1.20 output. That's also the most common rate across the model's 40 provider endpoints there (12 charge it). Input prices ranged from $0.07 to $0.60, so your deepseek bill depends on where you run it.
> - **Arms:** code mode off (plain tool calling) and code mode on (`CodeMode(eager=True)` with the default resource limits and the built-in `OSAccess` handler: an in-memory filesystem and environment, and the host clock). The first everyday batch also ran code mode with speculative execution.
> - **Runs:** everyday 3,500 (50 tests × 2 arms × 8 models × 4 reps, plus a third arm in the first batch); long horizon 576 (12 tests × 2 arms × 8 models × 3 reps); scaling 1,200 (25 tests × 2 arms × 8 models × 3 reps). 5,276 graded runs in randomized blocks. 27 infrastructure failures were retried. No run timed out, and no cell is missing.
> - **Validation before any model run:** for every test, the untouched seed fails its grader, a scripted reference solution passes, and a deliberately wrong one (a missed page, an off-by-one boundary) fails.
> - **Statistics:** task-balanced means and 95% bootstrap intervals over tests, planned before each batch ran. The benchmark grew in stages, each planned after the previous results were in: the GPT models first, then the Claude models and the long and scaling tiers, then the Muse and deepseek models. Pooling all eight models in every tier was decided before their last batches ran, and the Muse and deepseek prices were added after every run had finished. deepseek-v4.1-flash's everyday runs shared its server with up to 15 others, so compare its wall time across arms, not across tiers.
> - **Known warts:** two prompts are ambiguous, one everyday and one long ("how many lines are still in the cart"). Both are graded as frozen. Leaving them out changes no headline by more than a point.

Everything below compares code mode on to code mode off.

## The longer the task, the bigger the gap

Start with the scaling tier, because it's the cleanest experiment in the whole benchmark: same app, same rule, same prompt, and the only thing that changes is how many items the rule touches. Here's gpt-6.1-sol on all five tasks, wall time on top and cost below:

![Wall time and cost per run against N for gpt-6.1-sol on five tasks. Without code mode both climb steeply with N; at N = 200 wall time is 147 s for cart, 119 s for calendar, 71 s for chat, 167 s for kanban and 141 s for inventory. With code mode the lines stay nearly flat, at 25 to 32 seconds, except inventory at 73 s. Cost at N = 200 falls from $0.08 to $0.15 without code mode to $0.02 to $0.07 with it](assets/chart-scale-curves.svg)

Without code mode, both lines climb with every item. That's what tool calling *is*: every item is a call the model has to write, and every result is something it has to read back. For gpt-6.1-sol, each extra 100 items added 30 to 79 seconds and $0.04 to $0.07 per run.

With code mode, four of the five lines are close to flat. Closing out a sprint of 200 cards took 166.6 seconds without code mode and 26.6 seconds with it. Each extra 100 cards added 79 seconds without code mode and 4 seconds with it.

What each extra 100 items cost gpt-6.1-sol, per task:

| Task | Code mode off | Code mode on |
| --- | --- | --- |
| cart | +66 s, +$0.065 | +9 s, +$0.008 |
| calendar | +54 s, +$0.068 | +6 s, +$0.002 |
| chat | +30 s, +$0.039 | +6 s, +$0.016 |
| kanban | +79 s, +$0.067 | +4 s, +$0.006 |
| inventory | +63 s, +$0.061 | +29 s, +$0.028 |

Inventory is the exception, and it's a fair one: the delivery is pasted into the prompt as a list of N lines, so with or without code mode, the model has to read all of it.

Across all eight models, here's where code mode starts to pay:

![Change with code mode against off by N, mean of the per-model changes over eight models. Cost: at N = 5, cart minus 11%, calendar plus 21%, chat plus 38%, kanban plus 35%, inventory plus 3% (noise); at N = 200, minus 71%, minus 75%, minus 51%, minus 66% and minus 47%. Wall time at N = 200: minus 67%, minus 61%, minus 45%, minus 65%, minus 42%. Model requests at N = 200 fall by 1% to 22%, most within noise](assets/chart-scale-change.svg)

At 5 items, code mode costs more on three of the five tasks, by 21% to 38%. Its guidance rides along on every request, and five calls is not much work to fold into a loop. By 50 items it's cheaper on four of the five, and by 200 it saves 47% to 75% of the cost and 42% to 67% of the wall time on every task.

Look at the bottom panel, though: even at 200 items, model requests barely move on average, down 1% to 22%. More on that below.

And then there's correctness:

![Share of runs graded correct by N, pooled over eight models, 24 runs per arm at each N. Without code mode success falls from 92 to 100% at N = 5 to 75% for cart, 79% for calendar, 62% for chat, 75% for kanban and 75% for inventory at N = 200. With code mode it ends at 92%, 92%, 100%, 96% and 92%. Over all sizes: 518 of 600 runs correct without code mode, 577 of 600 with it](assets/chart-scale-success.svg)

Without code mode, success slides as N grows: from 92-100% at 5 items to 62-79% at 200. With code mode it ends at 92-100%. Across every size, that's 518 of 600 runs right without code mode and 577 of 600 with it. Per size the samples are small (24 runs per arm), and only 5 of the 25 gaps clear zero on their own, but the direction is the same on all five tasks: at 200 items, code mode was ahead on every one.

The weakest model shows it most. At 200 items gpt-6-luna got **0 of 15** runs right without code mode, and in 7 of them it never changed anything. It just explained why it couldn't:

> I found 200 cards labelled `sprint-42`, but I haven't changed them yet: the board tools require updating each card individually, and the card list is too large to safely process in a single operation here.

With code mode, the same model got 8 of those 15 right. It wasn't a crash, a timeout or a context overflow: no run without code mode had any of those. It's a model looking at 200 calls and declining to make them.

Some models never missed with code mode. Across all five tasks, muse-spark-1.3-contributor, muse-wonder-1.0-contributor and deepseek-v4.1-flash got all 225 of their code mode runs right, against 202 of 225 without.

| Model | Correct runs, off → on | Wall time at 200 items |
| --- | --- | --- |
| muse-spark-1.3-contributor | 65 → 75 of 75 | \-28% to -50% |
| muse-wonder-1.0-contributor | 75 → 75 of 75 | \-41% to -61% |
| deepseek-v4.1-flash | 62 → 75 of 75 | \-58% to -87% |

Eight of muse-spark-1.3-contributor's ten failures were one habit: it triaged the chat correctly, then posted a summary as a new message in #support, which the prompt didn't ask for. As graded, those runs are wrong. Ignore the posted messages and it got 14 of 15 chat runs right without code mode. With code mode it never posted one.

## One task at 200 items

One of those runs, up close: gpt-6.1-sol answering 200 invites, both arms graded correct.

![One calendar task at N = 200 for gpt-6.1-sol, both runs correct. Without code mode: 8 model requests, 205 tool calls, 183,723 input tokens, 4,430 output tokens, 119.5 seconds, $0.1425. With code mode: 6 requests (minus 25%), 215 tool calls, 34,461 input tokens (minus 81%), 573 output tokens (minus 87%), 28.5 seconds (minus 76%), $0.0231 (minus 84%)](assets/one-run-200.svg)

Without code mode it made 205 tool calls, packed into 7 responses, up to 43 in one. The batching was already good. The trouble is what each request carries: the conversation so far, including every tool result. By the end it had read 183,723 input tokens, written 4,430 output tokens to spell out those 205 calls and the answer, and taken two minutes.

With code mode it wrote 5 snippets, the calendar served 215 calls, and the model read 34,461 tokens and wrote 573. Wall time fell 76%, cost 84%. Requests went from 8 to 6.

## Models already batch

I assumed going in that "remove 22 items" meant 22 round trips without code mode. It doesn't. Modern models emit [parallel tool calls](https://developers.openai.com/api/docs/guides/function-calling#parallel-function-calling), and they emit a lot of them. In the long tier, the busiest single response carried 77 calls from gpt-6.1-sol and 119 from both Claude models. At 200 items, claude-haiku-5-5 put all 200 calls in one response.

So round trips don't fall the way the pitch says, at least not for the models that batch hardest. Across the long tier, model requests fell 22%, but it depends on the model. The GPT models made a third fewer requests (-33%), and the Claude models made *more*, +24% for claude-haiku-5-5 and +26% for claude-sonnet-5-5. Without code mode they fire one huge burst; with it they write about five short snippets per run and read each result before writing the next. They still cost 67% and 70% less. The models that batch least gained the most: muse-spark-1.3-contributor, muse-wonder-1.0-contributor and deepseek-v4.1-flash put at most 25 to 50 calls in one response, made 13 to 22 requests per run without code mode, and 27% to 52% fewer with it (muse-spark-1.3-contributor's drop is within noise).

This is where I'd push on the usual pitch, that every tool call costs another model turn. For independent calls on current models, that mostly isn't true. What still costs a turn is a *dependent* step: you can't answer an invite until you've listed the page it's on. What code mode removes is the part of each turn that grows with the work: the calls the model has to write out, and the results it has to read back in.

The exception is deepseek-v4.1-flash. It does batch, up to 80 calls in one response, but at 200 items without code mode it averaged 64 requests per run (up to 171) and read 2.8 million input tokens. With code mode: 11 requests and 86,000 tokens. Answering 200 invites took it 1,070 seconds per run without code mode and 138 with it. It ran on one vLLM server whose load we didn't control, so read its seconds loosely; the requests and tokens don't depend on the server.

## Where the tokens go

The token picture is what explains the cost:

![Tokens per long-horizon run, code mode off versus on. Output tokens fall on every model: gpt-6.1-sol 2,428 to 688, gpt-6-luna 1,339 to 765, gpt-6-astra 2,209 to 669, claude-haiku-5-5 15,506 to 4,065, claude-sonnet-5-5 9,856 to 1,970, muse-spark-1.3-contributor 15,470 to 7,566, muse-wonder-1.0-contributor 10,348 to 3,211, deepseek-v4.1-flash 11,966 to 3,726. Input tokens fall too: 76,256 to 30,945, 49,739 to 39,611, 84,162 to 31,423, 104,140 to 75,474, 83,747 to 54,891, 659,026 to 220,188, 255,810 to 90,258, 601,528 to 71,882](assets/chart-long-tokens.svg)

Output tokens fell 66% across the eight models, from -43% on gpt-6-luna to -80% on claude-sonnet-5-5. Output is the slow, expensive part, and it's what the model spends writing out every call and every intermediate value. Input tokens fell 53% too, because fewer results pile up in the context.

On short tasks the input side goes the other way. Code mode's guidance (how `run_code` works, what's available in the sandbox) adds about 2,600 characters to every request, a flat fee you pay per request no matter how small the job. On the everyday tasks input rose 29% while output fell 37%. At 5 items in the scaling tier total tokens rose 65% to 114%. That flat fee is most of the tax, and on long work it disappears into the savings.

## Everyday tasks: cheaper, about as correct

The 50 everyday tests are short: four or five requests and a dozen tool calls each. This is where I started, and where code mode's case is quietest.

| Model (4 reps, 3,200 runs) | Success | Cost per run |
| --- | --- | --- |
| gpt-6.1-sol | 96% → 98% (noise) | **\-9%** |
| gpt-6-luna | **66% → 85%** | **+19%** |
| gpt-6-astra | **94% → 98%** | \-7% (noise) |
| claude-haiku-5-5 | 96% → 96% (noise) | **\-40%** |
| claude-sonnet-5-5 | 97% → 95% (noise) | **\-38%** |
| muse-spark-1.3-contributor | **98% → 92%** (worse) | **\-13%** |
| muse-wonder-1.0-contributor | 98% → 94% (noise) | \-8% (noise) |
| deepseek-v4.1-flash | 96% → 95% (noise) | **\-34%** |
| all models | +1.6 pts (noise) | **\-16%** |

Across all eight models, code mode was 16% cheaper and 11% faster, and right about as often. The average hides a split. Most of the models were already right 94% to 98% of the time without code mode, and stayed there. gpt-6-luna is the exception, and most of its gain is on questions. In the first batch, twelve of the tests asked for a number ("what's my cart total going to be if dairy is 10% off?"), and gpt-6-luna got 38% of them right without code mode and 88% with it. Without code mode the models added up 30 to 120 rows in their heads and missed, stopped after two of three pages, or just declined: *"I can't reliably calculate the total from this many cart lines."* In the other direction, muse-spark-1.3-contributor was right less often with code mode, and every one of those misses left the app in the wrong state.

Splitting by kind of task shows where the tax lands:

![Change with code mode by everyday test category, mean of the eight models, 4 reps. Success: aggregate plus 8.1 points (90% to 98%), conditional plus 2.5 (90% to 93%), bulk minus 5 (95% to 90%), sequence plus 2.5 (82% to 85%), lookup plus 0.3, control plus 1.2. Cost: aggregate minus 27%, conditional minus 22%, bulk minus 15%, sequence minus 9%, lookup 0%, control plus 8%. Wall time: minus 26%, minus 15%, minus 6%, minus 14%, plus 6%, plus 16%](assets/chart-categories.svg)

Aggregates (questions over many rows) are where code mode shines: 90% to 98% correct, 27% cheaper, 26% faster. Then there's the control group, five tests that are a single operation ("change the sourdough to 2 please"). There code mode cost 8% more and took 16% longer, because the model paid for the guidance and wrote a program to make one call. Bulk edits were cheaper too, but less often right (95% to 90%), and the Muse models account for most of that drop. Categories have 5 to 10 tests each, too few for intervals, so treat those bars as direction.

## Where code mode costs

The honest list, because there is one:

- **Small jobs.** At 5 items, code mode cost more on three of the five scaling tasks; by 20 it was cheaper on three and level on one. Chat triage crossed over last: it cost more at 5 and 20 messages and only got cheaper from 100. Telling a refund request from other messages means reading the text, so with code mode the messages still pass through the model.
- **Small models that write buggy code.** gpt-6-luna paid 19% more on the everyday tasks, with 0.56 failed `run_code` snippets per run, and every failure is another round trip. Per correct run it still came out cheaper: $0.00121 against $0.00130. On the inventory scaling task its cost grew *faster* with code mode than without, while it got 9 of 15 runs right instead of 3.
- **Models that print the data back.** muse-spark-1.3-contributor's code mode runs printed much of the data into the conversation, so at 200 items its tokens fell only 5% to 64%. For muse-wonder-1.0-contributor and deepseek-v4.1-flash they fell 57% to 99%.
- **Retries can repeat writes.** A snippet that fails halfway and gets rerun can do its first half twice. Three of gpt-6-luna's failures in the long tier created the same records twice.
- **It can still get things wrong.** On the everyday tasks, muse-spark-1.3-contributor was right 92% of the time with code mode and 98% without, the one drop whose interval clears zero. Most of its misses were bulk edits that left the app in the wrong state. In the scaling tier, two cells went the wrong way, both within noise. In calendar invites at N = 20 (92% → 83%), gpt-6-luna left invites unanswered and claude-haiku-5-5 miscounted its own work. In inventory at N = 5 (100% → 92%), claude-haiku-5-5 twice left a required number out of its reply.

So code mode earns its keep once the data or the task grows past what plain tool calling handles well. On these apps, for most tasks, that point was somewhere between 20 and 50 items.

## So why is it the future?

Because the curve is real, and it points one way. Code mode charges a flat fee: a couple of thousand characters of guidance per request. Tool calling charges per item: every call written out, every result read back in, every running total held in the model's head. On a single edit the flat fee loses. A few dozen items in, it starts winning, and by 200 items it's not close. I expect agent tasks to keep getting longer. I haven't measured that, but if they do, more and more of them will land on the right side of that curve.

The tradeoffs are real, and worth taking seriously:

- **You're running LLM-generated code.** Yes, which is why the sandbox matters as much as the model. Generated code can only reach what you hand it, and it runs inside time and memory limits. Your tools are what you hand it, and they run with your app's authority, so they still need their own validation and authorization. [Samuel's Monty post](https://pydantic.dev/articles/pydantic-monty) explains why we built an interpreter that starts from nothing instead of locking down a full Python.
- **It's harder to debug.** Also yes. A failing program hides its intermediate values in the sandbox, and as gpt-6-luna showed, a rerun snippet can repeat its writes. You do have to read code now, not just JSON. What helps is that the program's calls still go through Pydantic AI to your real tools, so with [Logfire](https://pydantic.dev/docs/ai/integrations/logfire/) or any OpenTelemetry backend instrumenting the agent, each `run_code` call is a span and every tool call inside it [gets its own span](https://pydantic.dev/docs/ai/harness/code-mode/#observability) underneath.
- **You may not need it at all.** True, and our small-N results back it up. The answer there is less code mode, not none. Pydantic AI's `CodeMode` takes a [tool selector](https://pydantic.dev/docs/ai/harness/code-mode/#selective-tool-sandboxing), so you can sandbox the tools that get looped over and leave the rest as plain tool calls.

Code mode is also just where the models are heading: writing code looks like the skill they're improving at fastest. My guess is that's because code is checkable, which makes it easy to train on. Either way, giving the model a programming language to drive your tools plays to the strength that's improving fastest.

It also has to be safe to run. Every result above came from code mode inside a sandbox that could reach these apps' tools, an in-memory filesystem and environment, and the clock, and nothing else: no host files and no network. That's the setup we built Monty for.

The next step is the same idea one level up. In [dynamic workflows](https://pydantic.dev/articles/dynamic-workflows), the functions in the sandbox are sub-agents instead of tools, and the program the model writes is the orchestration. Samuel's graph, written by the model, at runtime, with agents as the nodes. That's the future I mean.

## Try it

In your own Pydantic AI agent, code mode is one capability from Pydantic AI Harness:

```bash
uv add "pydantic-ai-harness[codemode]" "pydantic-ai-slim[openai]"
export OPENAI_API_KEY="your-api-key"
```

Then give the agent its tools:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import CodeMode

CART = {
    1: {'name': 'Espresso machine', 'unit_price': 249.00},
    2: {'name': 'Oat milk', 'unit_price': 3.49},
    3: {'name': 'Cast iron pan', 'unit_price': 64.95},
}

agent = Agent(
    'openai:gpt-6.1-sol',
    instructions='You help the user manage their shopping cart. Prices are in US dollars.',
    capabilities=[CodeMode()],
)

@agent.tool_plain
def list_items(offset: int = 0, limit: int = 20) -> dict:
    """List cart items in id order, one page at a time."""
    ids = sorted(CART)[offset : offset + limit]
    next_offset = offset + limit if offset + limit < len(CART) else None
    return {'items': [{'id': i, **CART[i]} for i in ids], 'next_offset': next_offset}

@agent.tool_plain
def remove_item(item_id: int) -> str:
    """Remove one item from the cart."""
    return f'removed {CART.pop(item_id)["name"]}'

result = agent.run_sync(
    'can you get rid of everything in my cart that costs more than $50 a piece?'
)
print(result.output)
```

The model sees one tool, `run_code`, and calls `list_items` and `remove_item` as async functions from inside it. That code runs in Monty, so those two functions are all it can reach. The benchmark ran it with `eager=True`. The [code mode docs](https://pydantic.dev/docs/ai/harness/code-mode/) cover eager and [speculative execution](https://pydantic.dev/docs/ai/harness/code-mode/#speculative-execution), tool selection, resource limits and the rest.

## What about speculation?

Pydantic AI Harness's `CodeMode` also has [speculative execution](https://pydantic.dev/docs/ai/harness/code-mode/#speculative-execution): the speculative programmatic tool calling from the top of this post, which starts calls to tools you've declared safe to run early while the model is still writing the `run_code` call. None of these apps' tools were declared for it, so speculation had nothing to start early. In the first everyday batch it differed from plain code mode only in its longer guidance, and it showed: +7.7 points of success instead of +10.3, and +4% cost instead of -2%. The later batches skipped it. That's not a test of speculation, so I'm not drawing conclusions from it.

Thank you for reading!

## Acknowledgements

- [Samuel Colvin](https://pydantic.dev/articles/the-code-is-the-graph) for the graph argument, and for pushing me to find bigger differences.
- Maverick ([@maverick-jackson](https://github.com/maverick-jackson)), whose code mode study set the A/B method this benchmark follows.
- Ruben, for spotting that the first version of my success chart had "more correct" pointing the wrong way.
