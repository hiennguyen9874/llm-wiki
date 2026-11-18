---
type: Concept
title: Pydantic AI Harness smart search
description: The Harness SmartSearch capability — behaviour-level code search that lists files with rg, chunks them into snippets, shortlists by BM25, then pays one judge-model request per snippet, with the request budget, threshold and index cache that decide whether it is worth it.
tags: [pydantic-ai, agents, harness, retrieval]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:10:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-smart-search-docs
    resource: ../raw/harness/smart-search/index.md
    scope: ../raw/harness/smart-search/
    kind: documentation
    revision: sha256:a1eb49c5f3313c826f0a331b89fddb4b256b1fc355df8d7880dc1f7e847fc32e
    title: "Smart Search"
---

`SmartSearch` is the [Harness](pydantic-ai-harness.md) capability that searches code by **behaviour** rather than by name: the model asks "where do we reject expired sessions?" in plain English and gets ranked source excerpts with file and line ranges[^pydantic-smart-search-docs] It exists because a coding agent in an unfamiliar repository spends its first turns guessing identifiers and chaining `grep` calls, and text search only finds what you can already name. Unlike [tool search](pydantic-ai-tool-search.md), which selects tool *definitions*, this retrieves source *content*, and unlike[RAG retrieval pipeline design](rag-retrieval-pipeline.md) it is a two-stage symbolic-then-judged pipeline with no embeddings. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## The four-step pipeline

One `smart_search` call runs four steps, and knowing which step each limit belongs to is the whole operational picture[^pydantic-smart-search-docs]:

1. **List** files under `directory` with `rg --files`, which honours `.gitignore` and skips hidden files; binary, non-UTF-8 and minified files are skipped and counted.
2. **Chunk** each file: overlapping 60-line windows of plain text, except Python, which is parsed with the standard library so functions, methods and classes become snippets and the blocks of a long function become snippets of their own.
3. **Shortlist** the `candidates` snippets that best match the query with local **BM25**, weighting paths and symbol names and expanding common programming synonyms — 128 by default, at most 256.
4. **Judge** each shortlisted snippet with the judge model, which rates how well the snippet *acts on what the query names* and how well it *performs the action the query describes*; relevance is the product of the two, and snippets at or above `threshold` are returned best first with a focused excerpt of at most 12 lines.

The workspace requirement follows from step 1: the run's workspace must be able to run commands and have `rg` on its `PATH` (the `coder` extra installs it locally; a sandbox image needs it), the tool is **not offered at all** on a workspace that cannot run commands, and a run with no workspace fails at its start[^pydantic-smart-search-docs] No search happens without a workspace, and nothing is searched outside it.

A single failed judgment fails the whole search and is reported to the model as a tool failure, so the model can fall back to ordinary search instead of acting on half-judged results[^pydantic-smart-search-docs] The returned `SmartSearchResult` carries the matches, how many passed but were cut by `limit`, coverage figures (files seen and skipped, snippets built and judged, whether the shortlist was complete) and warnings — which is what lets the model tell "nothing matched" apart from "the search did not look everywhere". Matches in test files are labelled `kind='test'` rather than demoted.

Being offered is itself an instruction. `guidance` adds discovery guidance to the system prompt *whenever the tool is offered*: `None`, the default, tells the model to reach for `smart_search` before exploratory text search, and `''` contributes no instructions at all[^pydantic-smart-search-docs] Attaching the capability therefore changes the agent's stated search order before the model ever picks a tool, which is a second reason — beyond the judge — why this is a configuration decision rather than a neutral addition.

## The judge is required, and it is a data-flow decision

`model` has no default: the judge decides which provider receives the searched source, so the capability never picks one for you[^pydantic-smart-search-docs] That is the privacy edge of the design — every shortlisted snippet leaves the machine — and it is why the recommendation is a [decision model](pydantic-ai-capability-model-control.md) rather than the run's own model:

| Judge | How | Cost shape |
| --- | --- | --- |
| Any decision model over the System One API | `model='system-one:<name>'` with `SYSTEM_ONE_BASE_URL`/`SYSTEM_ONE_API_KEY`, or a `SystemOneModel`; CLM, Laya, or a local Ollama | One request per snippet, answered as a probability in "a fraction of the time" a language model takes; needs nothing beyond `pydantic-ai-slim` |
| Jev through TypeSafe | `model='typesafe:jev-latest'` with `TYPESAFE_API_KEY`; needs the `typesafe` extra | Same shape; the default `threshold` is tuned for Jev |
| Any language model | Any model or model name | Two ratings as ordinary structured output, so it works — but slower per snippet, and better as a small fast model than the run's own |

A judge given **by name** times out each request after 30 seconds; a model **instance** keeps its own `settings`, so `settings={'timeout': ...}` is the lever for a slow local judge[^pydantic-smart-search-docs]

`threshold=0.5` is the default and is tuned for Jev's probabilities; another decision model's, and especially a language model's, ratings calibrate differently, so the source's advice is to check a few searches, adjust, and then **pin a model version** once tuned[^pydantic-smart-search-docs]

## The request budget is the binding constraint

Every judged snippet is one request in the run's usage, and the judge's tokens are added to it, so `result.usage` and `UsageLimits` cover the search[^pydantic-smart-search-docs] To stop one search eating the run, it judges at most **half** the requests the run's `request_limit` has left, after keeping one for the model's next turn: under the default `request_limit` of 50, a run's first search judges 24 snippets, not 128.

The consequences are concrete[^pydantic-smart-search-docs]:

- Shortlists are judged best-ranked first, and a warning reports how many were left unjudged.
- A full 128-snippet search needs a raised limit, such as `agent.run(..., usage_limits=UsageLimits(request_limit=500))` — see [run controls](pydantic-ai-run-controls.md).
- When no request is left to spend, the search fails and the model is told to use regular search.
- `concurrency` (default 8) sets how many snippets are judged at once, so wall-clock time and provider rate limits trade against each other here.

## Large codebases and the index cache

A search is capped at 200,000 files (counted after `glob`), 50 million lines and 2 GiB of source — "enough for the Linux kernel" — and past that asks the model to narrow `directory` or `glob`[^pydantic-smart-search-docs] Without caching, every search reads, chunks and indexes its directory from scratch. `cache_index=True` keeps each searched directory's index for the life of the agent: later searches **still read every file** to catch changes by content hash, but only chunk and index what changed, and parallel `smart_search` calls on one directory take turns so the index is built once. Up to four directories (each with its `glob`) are kept, least recently searched evicted, and memory grows with the source they hold.

The cache belongs to the **toolset**, not the agent. `get_toolset` provides the stable `smart_search` toolset shared with every per-run copy, and a run whose capabilities differ from the agent's — an instrumented one, or one given extra `capabilities` — asks for the toolset again; a new one starts with an empty `cache_index`[^pydantic-smart-search-docs] So anything that changes the capability set re-pays for the index, and the measured saving is per toolset life rather than per agent.

The one measurement the source gives is vendor-reported and belongs to the cache argument, not to this page's verification[^pydantic-smart-search-docs]: on the Pydantic AI repository (4,500 files, 2 million lines, 126,000 snippets) the first search spent about 9 seconds building the index and later ones under a second refreshing it, against 10–14 seconds for every search uncached. It is **Reported**, not **Reproduced** here, and it is a single repository on one machine — the ratio, not the seconds, is the transferable part.

## Identity, telemetry and specs

`SmartSearch` declares the default `id` `'smart_search'`, under which durable execution records each search's judgments[^pydantic-smart-search-docs] Two instances sharing it merge when they agree and raise `UserError` at construction when they differ — a merge could send source to a judge neither chose — so keeping two needs distinct `id`s wrapped in `PrefixTools`, since both register `smart_search`, and `combine` treats two under one `id` as "one search stated twice"[^pydantic-smart-search-docs] The page also notes that earlier releases declared **no** default `id`, so two instances always failed on the tool name when the run started; it names no release for that change, so the migration boundary is undated here.

Each search opens a `smart search` span under its tool call carrying `smart_search.judge_model`, `.files`, `.skipped_files`, `.snippets`, `.evaluated`, `.indexed_files` (which shows what the cache saved), `.selection_complete`, `.matches`, `.omitted_matches`, and `.query` only when the run captures content[^pydantic-smart-search-docs] Two deliberate omissions: a failed search records no exception on this span (the enclosing tool span reports it, redacted by `include_content`), and the judge requests themselves are **not instrumented** — their prompts carry source snippets, so global instrumentation must not export them past the host agent's `instrument` or `include_content` settings. Their usage is still counted.

The capability serializes into [agent specs](pydantic-ai-agent-specs.md) by name, with the judge and threshold in the spec and the workspace attached at run time through `agent.run(..., workspace=...)`[^pydantic-smart-search-docs]

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram was read in its text form[^pydantic-smart-search-docs] External links — the workspace page, decision models, the System One API, TypeSafe, `PrefixTools`, BM25, the agent-spec and usage pages and the ripgrep repository — were read as links and not followed. The page states no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `openai:gpt-6-astra`, `system-one:clm-latest` and `typesafe:jev-latest`, aliases no release pin corroborates.

Nothing was installed, no repository indexed, no BM25 shortlist built, no judgment requested and no span inspected, so every claim is **Reported**; the timing figures are vendor-measured and not reproduced. Unstated and consequential: what BM25 parameters and synonym list are used, how the 60-line window overlap is set, whether the judge sees the query and snippet in one request or batched, and what a judgment costs in tokens — so the "fraction of the time" comparison cannot be turned into a cost per search from this page alone.

## Relationships

- **Depends on** a command-capable [workspace](pydantic-ai-workspaces-and-sandboxes.md) with ripgrep, and on a judge model whose provider receives the source.
- **Alternative to** ordinary `grep`/`read_file` exploration in [Coder](pydantic-ai-harness-coder.md) and to the [FileSystem](pydantic-ai-harness-filesystem.md) tools' literal search.
- **Uses** [decision models](pydantic-ai-capability-model-control.md) as the fast judge, and [run controls](pydantic-ai-run-controls.md)' `UsageLimits` as the budget it rations itself against.
- **Emits** `smart search` spans into [Pydantic AI observability](pydantic-ai-observability.md), while deliberately not instrumenting its judge calls.

[^pydantic-smart-search-docs]: Pydantic Docs, "Smart Search", <https://pydantic.dev/docs/ai/harness/smart-search/>; local capture `raw/harness/smart-search/index.md`, content digest sha256:a1eb49c5, 2,591 words as declared (2,696 by `wc -w`), 406 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the behaviour-search framing and the recommended judge kind; 13–35 for the flow diagram (list → chunk → BM25 shortlist of 128 → judge ≥ threshold → `SmartSearchResult`); 37–41 for the problem statement; 43–63 for the usage example, the `rg`/command-capable workspace rule and the not-offered and fail-at-start cases; 65–78 for the six settings with defaults and the 30-second named-judge timeout; 80–98 for the tool table, the four steps, the 60-line/Python-AST chunking, the 128/256 shortlist, the two-part judgment, the 12-line excerpt and the `kind='test'` label; 100–104 for the failed-judgment behaviour; 106–122 for the 200,000-file/50-million-line/2 GiB caps and the `cache_index` behaviour including the four-directory eviction; 124–145 for the judge options, `threshold` calibration and version pinning; 147–157 for the request accounting, the half-of-remaining-`request_limit` rule, the 24-of-50 example, the unjudged warning and the no-request-left failure; 159–165 for the default `id` and its merge/`UserError` rule; 235–247 for the `guidance` attribute with its `None`/`''` meanings; 249–280 for `combine` and `get_toolset`, including the new toolset that starts with an empty `cache_index` when a run's capabilities differ from the agent's; 167–181 for the `smart search` span attributes and the two omissions; 183–199 for the agent-spec form and run-time workspace; 201–405 for the API reference. Evidence class: **Reported** — vendor documentation for its own package; the index-cache timings are vendor-measured and not reproduced.
