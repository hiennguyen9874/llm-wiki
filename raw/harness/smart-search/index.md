---
title: "Smart Search"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/harness/smart-search/"
domain: "pydantic.dev"
language: "en"
description: "Give a Pydantic AI agent code search by behavior: describe it in plain English and get ranked source excerpts, judged by any model, such as a decision model over the System One API or TypeSafe's Jev."
word_count: 2591
---

`SmartSearch` gives an agent code search by behavior: the model describes the behavior it is looking for in plain English (“where do we reject expired sessions?”) and gets back ranked source excerpts with file and line ranges, without first having to guess the symbol names a text search needs. Relevance is decided by a judge model you choose: any Pydantic AI model works, and a [decision model](https://pydantic.dev/docs/ai/models/decision/), served over the [System One API](https://pydantic.dev/docs/ai/models/system-one/) or as TypeSafe’s Jev, is the recommended kind.

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/smart_search/)

> While Pydantic AI Harness is on 0.x releases, the API may change between minor releases; when it does, deprecation warnings and release-note migration guidance tell you (or your agent) exactly how to upgrade. See the [version policy](https://pydantic.dev/docs/ai/harness/#version-policy).

```
flowchart TB
    accTitle: Smart Search: find code by what it does
    accDescr: The model sends a smart_search query to the SmartSearch capability, which lists files under the directory with rg --files in the run workspace, LocalWorkspace or a sandbox. It chunks them into snippets, shortlists 128 by default with BM25, and sends the judge model one request per snippet. Snippets at or above the relevance threshold return to the model as a SmartSearchResult.
    model(["model"])
    subgraph search["SmartSearch()"]
        files["List files<br/>under directory"]:::capability
        chunk["Chunk<br/>files into snippets"]:::capability
        shortlist["Shortlist with BM25<br/>128 by default"]:::capability
        judge["Judge<br/>relevance &gt;= threshold"]:::capability
    end
    workspace["run workspace<br/>LocalWorkspace<br/>or a sandbox"]:::external
    judgemodel(["judge model<br/>one request per snippet"])
    model -->|"smart_search query"| files
    files <-->|"rg --files"| workspace
    files --> chunk
    chunk --> shortlist
    shortlist --> judge
    judge <--> judgemodel
    judge -->|"SmartSearchResult"| model
    classDef capability stroke:#E520E9,stroke-width:2px
    classDef external stroke:#0E9C86,stroke-width:2px
```

## The problem

A coding agent dropped into an unfamiliar repository spends its first turns locating code: guessing identifiers, chaining exploratory `grep` calls, and listing and reading whole files to find the one function that matters. Every miss costs a round trip and fills the context with code it will throw away. Text search only finds what you can already name.

## Usage

Pass the judge as `model`, which is required (see [Choosing the judge](#choosing-the-judge)). `SmartSearch` searches the run’s [workspace](https://pydantic.dev/docs/ai/core-concepts/workspace/), so attach one next to it:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import SmartSearch

agent = Agent(
    'openai:gpt-6-astra',
    capabilities=[LocalWorkspace('.'), SmartSearch(model='system-one:clm-latest')],
)

result = agent.run_sync('Where do we retry failed webhook deliveries?')
print(result.output)
```

The workspace must be able to run commands and have [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) on its `PATH`, which lists the files to search. The `coder` extra installs `rg` for a local workspace; a sandbox image needs it installed. The tool is not offered on a workspace that cannot run commands, and a run without a workspace fails at its start.

## Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `model` | required | The judge: any model or model name. A judge given by name times out each request after 30 seconds; a model instance keeps its own `settings`. |
| `threshold` | `0.5` | Relevance (the product of the two judgments, 0 to 1) a snippet needs to be returned. Tuned for Jev; see [Choosing the judge](#choosing-the-judge). |
| `concurrency` | `8` | Snippets judged at once. |
| `cache_index` | `False` | Keep each searched directory’s index in memory between searches; see [Large codebases](#large-codebases). |
| `guidance` | `None` | Discovery instructions added whenever the tool is offered: `None` for the default, which has the model reach for `smart_search` before exploratory text search, `''` for none. |
| `id` | `'smart_search'` | Stable identity, under which durable execution records each search’s judgments; see [Two of them](#two-of-them). |

## Tool

| Tool | Purpose |
| --- | --- |
| `smart_search` | Find code by what it does: `query` in plain English, optionally scoped by `directory` and a ripgrep `glob`, returning up to `limit` matches after judging up to `candidates` snippets. |

A search runs in four steps:

1. **List** the files under `directory` with `rg --files`, which honors `.gitignore` and skips hidden files. Binary, non-UTF-8 and minified files are skipped and counted.
2. **Chunk** each file into snippets: overlapping 60-line windows of plain text, except for Python, which is parsed with the standard library so that functions, methods and classes become snippets, with the blocks of a long function as snippets of their own.
3. **Shortlist** the `candidates` snippets (128 by default, at most 256) that best match the query with local [BM25](https://en.wikipedia.org/wiki/Okapi_BM25), weighting paths and symbol names and expanding common programming synonyms.
4. **Judge** each shortlisted snippet with the judge model, which rates how well the snippet acts on what the query names and how well it performs the action the query describes. A snippet’s relevance is the product of the two, and those at or above `threshold` are returned, best first, each with a focused excerpt of at most 12 lines.

The result is a `SmartSearchResult`: the matches, how many passed but were cut by `limit`, coverage figures (files seen and skipped, snippets built and judged, and whether the shortlist was complete) and warnings, so the model can tell an empty result from a complete search that found nothing. Matches in test files are labeled `kind='test'` rather than demoted.

A failed judgment fails the whole search, and the error is reported to the model as a tool failure, so it can fall back to regular search instead of acting on half-judged results.

## Large codebases

A search is capped at 200,000 files (counted after `glob`), 50 million lines and 2 GiB of source, enough for the Linux kernel; past that it asks the model to narrow `directory` or `glob`. Without caching, every search reads, chunks and indexes its directory from scratch.

Set `cache_index=True` to keep each searched directory’s index between searches, for the life of the agent:

```python
from pydantic_ai_harness import SmartSearch

capability = SmartSearch(model='system-one:clm-latest', cache_index=True)
```

Later searches of the same directory still read every file, to catch changes by content hash on any workspace, but only chunk and index the files that changed. Parallel `smart_search` calls on one directory take turns, so its index is built once rather than by each call. On the Pydantic AI repository (4,500 files, 2 million lines, 126,000 snippets), the first search spent about 9 seconds building the index and later ones under a second refreshing it, against 10 to 14 seconds for every search without the cache. Up to four directories (each with its `glob`) are kept, least recently searched evicted first, and memory grows with the source they hold.

## Choosing the judge

The judge is required, and is any Pydantic AI model or model name, passed as `model`. It decides which provider receives the searched source, so it is never picked for you.

A [decision model](https://pydantic.dev/docs/ai/models/decision/) is the recommended judge: it answers each relevance question with a probability in a fraction of the time a language model takes to write one, which is what 128 judgments per search need. There are two ways to use one:

- **Any decision model served over the [System One API](https://pydantic.dev/docs/ai/models/system-one/)**, such as CLM, Laya, or one [Ollama](https://pydantic.dev/docs/ai/models/system-one/#ollama) runs locally. Set `SYSTEM_ONE_BASE_URL`, and `SYSTEM_ONE_API_KEY` if the API needs a key, then pass `model='system-one:<name>'`, or a [`SystemOneModel`](https://pydantic.dev/docs/ai/api/models/system_one/#pydantic_ai.models.system_one.SystemOneModel). This needs nothing beyond `pydantic-ai-slim`.
- **[Jev](https://pydantic.dev/docs/ai/models/typesafe/) through TypeSafe’s SDK**, as `model='typesafe:jev-latest'`, with `TYPESAFE_API_KEY` set.

To install TypeSafe’s SDK:

- [pip](#tab-panel-0-0)
- [uv](#tab-panel-0-1)

Terminal

```bash
pip install "pydantic-ai-slim[typesafe]"
```

A judge given by name times out each request after 30 seconds; a model instance keeps its own `settings`, so set `settings={'timeout': ...}` on it for a slower judge, such as a local one.

Any language model works as well, since the two ratings are ordinary structured output. As one search makes up to `candidates` judge requests, prefer a small, fast model to the run’s own when you are not using a decision model.

`threshold` (0.5 by default) is tuned for Jev’s probabilities. Another decision model’s probabilities, and even more so a language model’s ratings, can be calibrated differently, so check a few searches and adjust it if results are too sparse or too noisy. Pin a model version (for example `'typesafe:jev-1.13.0'`) once you have tuned `threshold` against it.

## Usage and limits

Each judged snippet counts as one request in the run’s [usage](https://pydantic.dev/docs/ai/core-concepts/agent/#usage-limits), and the judge’s tokens are added to it, so `result.usage` and the run’s [`UsageLimits`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits) cover the search. So that one search cannot use up the run, it judges at most half of the requests the run’s `request_limit` has left, after one kept for the model’s next turn. The shortlist’s best-ranked snippets are judged first, and a warning says how many were left unjudged. Under the default `request_limit` of 50, a run’s first search judges 24 snippets. Raise the limit for full 128-snippet searches, for example with `agent.run(..., usage_limits=UsageLimits(request_limit=500))`. When no request is left to spend, the search fails and the model is told to use regular search.

## Two of them

`SmartSearch` declares the default `id` `'smart_search'`, under which durable execution records each search’s judgments. Two `SmartSearch`s on one agent that share it become one when they agree, and the agent raises a `UserError` when it’s built if they differ, since a merge could send the source to a judge neither chose. To keep two, give each its own `id` and wrap them in [PrefixTools](https://pydantic.dev/docs/ai/capabilities/prefix-tools/), since both register `smart_search`.

Earlier releases declared no default `id`, so two always failed on the tool name when the run started.

## Telemetry

Each search opens a `smart search` span under its tool call, on the run’s tracer. The span has these attributes:

- `smart_search.judge_model`: the judge model.
- `smart_search.files`, `.skipped_files`, `.snippets` and `.evaluated`: the coverage figures.
- `smart_search.indexed_files`: how many files the search chunked and indexed. With `cache_index`, only new and changed files are, so this shows how much the cache saved.
- `smart_search.selection_complete`: whether the coverage was complete.
- `smart_search.matches` and `.omitted_matches`: how many matches were returned and cut.
- `smart_search.query`: the query, only when the run includes content in traces.

A failed search records no exception on this span; the enclosing tool span reports it, redacted by the run’s `include_content`. The judge runs themselves are not instrumented. Their prompts carry source snippets, so global instrumentation must not export them past the host agent’s own `instrument` or `include_content` settings. Their usage is still added to the run’s.

## Agent spec (YAML/JSON)

`SmartSearch` works with Pydantic AI’s [agent spec](https://pydantic.dev/docs/ai/core-concepts/agent-spec/):

```yaml
# agent.yaml
model: openai:gpt-6-astra
capabilities:
  - SmartSearch:
      model: system-one:clm-latest
      threshold: 0.6
```
```python
from pydantic_ai import Agent
from pydantic_ai_harness import SmartSearch

agent = Agent.from_file('agent.yaml', custom_capability_types=[SmartSearch])
```

Attach the workspace when running the agent, with `agent.run(..., workspace=...)`.

## API reference

### SmartSearch

**Bases:** `AbstractCapability[AgentDepsT]`

Find code by the behavior a plain-English query describes.

Adds a `smart_search` tool. A search lists the files under a directory in the run’s workspace with `rg`, cuts them into snippets (overlapping line windows, or the functions, methods and long blocks of a Python file), shortlists the snippets with local BM25, and has a judge model score each shortlisted snippet’s relevance. Matches come back ranked, with file and line ranges and a focused excerpt, plus coverage figures so the model can tell an empty result from a complete search that found nothing.

The judge is any Pydantic AI model (see `model`), and is required, since it decides which provider receives the searched source. One search makes up to `candidates` (default 128) judge requests, each counted as one request in the run’s usage and checked against its usage limits.

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace

from pydantic_ai_harness import SmartSearch

agent = Agent(
    'openai:gpt-6-astra',
    capabilities=[LocalWorkspace('.'), SmartSearch('system-one:clm-latest')],
)
```

Files are listed and read through `ctx.workspace`, so attach a workspace that can run commands and has `rg` on its `PATH` (the `coder` extra installs it for a local workspace); the tool is not offered on one that cannot run commands, and a run without a workspace fails at its start.

#### Attributes

##### model

The model that judges each snippet’s relevance: any Pydantic AI model or model name.

A decision model served over the System One API, such as `'system-one:clm-latest'`, or a `SystemOneModel`, answers each judgment with a probability, as does TypeSafe’s Jev (`'typesafe:jev-latest'`). Pin a model version (e.g. `'typesafe:jev-1.13.0'`) once you have tuned `threshold` against it.

**Type:** `Model` | `KnownModelName` | [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### threshold

Relevance a snippet needs to be returned, from 0 to 1.

A snippet’s relevance is the product of two judgments: that it acts on what the query names, and that it performs the action the query describes.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float) **Default:** `DEFAULT_THRESHOLD`

##### concurrency

How many snippets are judged at once.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `DEFAULT_CONCURRENCY`

##### cache\_index

Keep each searched directory’s index in memory between searches, re-indexing only changed files.

Off, every search reads, chunks and indexes its directory from scratch. On, later searches of the same directory still read every file to detect changes, but only re-chunk the ones that changed, and parallel searches of it build the index once. Up to four directories (with their `glob`) are kept for the life of the agent, so this holds memory in proportion to the source searched.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### guidance

Custom discovery guidance for the system prompt, added whenever the tool is offered.

Leave as `None` for the default, which tells the model to reach for `smart_search` before exploratory text search, or set `''` to contribute no instructions at all.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### id

Stable identity for durable execution, which records each search’s judgments under it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `'smart_search'`

#### Methods

##### combine

`@classmethod`

```python
def combine(
    cls,
    capabilities: Sequence[AbstractCapability[AgentDepsT]],
) -> AbstractCapability[AgentDepsT]
```

Two under one `id` are one search stated twice; two that disagree raise rather than merge.

###### Returns

`AbstractCapability`\[`AgentDepsT`\]

##### get\_toolset

```python
def get_toolset() -> SmartSearchToolset[AgentDepsT]
```

Provide the stable `smart_search` toolset, shared with every per-run copy.

A run whose capabilities differ from the agent’s (an instrumented one, or one given extra `capabilities`) asks for the toolset again; a new one would start with an empty `cache_index`.

###### Returns

`SmartSearchToolset`\[`AgentDepsT`\]

### SmartSearchResult

What one `smart_search` call found, and how thoroughly it looked.

#### Attributes

##### matches

Relevant snippets, best first, overlapping snippets collapsed into the best one.

**Type:** [`list`](https://docs.python.org/3/glossary.html#term-list) \[`SmartSearchMatch`\] **Default:** `field(default_factory=(list[SmartSearchMatch]))`

##### coverage

How much of the directory was judged.

**Type:** `SmartSearchCoverage` **Default:** `field(default_factory=SmartSearchCoverage)`

##### omitted\_matches

Relevant snippets beyond `limit`.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `0`

##### warnings

Why the result may be incomplete: no matches do not prove absence.

**Type:** [`list`](https://docs.python.org/3/glossary.html#term-list) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] **Default:** `field(default_factory=(list[str]))`

### SmartSearchMatch

One relevant snippet, with a short excerpt focused on the evidence.

#### Attributes

##### file\_path

The file, as a path relative to the working directory (or absolute, if the search directory was).

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### start\_line

First line of `text`, 1-based.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int)

##### end\_line

Last line of `text`, 1-based and inclusive.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int)

##### symbol

The declaration the snippet belongs to, such as `Cache.get`, when the file was parsed.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### kind

`'test'` when the file looks like a test; tests are labeled, not demoted.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘test’\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### score

The judge’s relevance score, in `[0, 1]`.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float)

##### text

At most 12 lines of the snippet, around the lines most relevant to the query.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### snippet\_start\_line

First line of the whole judged snippet `text` was taken from.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int)

##### snippet\_end\_line

Last line of the whole judged snippet `text` was taken from.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int)

### SmartSearchCoverage

How much of the directory the search actually judged.

#### Attributes

##### files

Files listed under the directory.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `0`

##### snippets

Snippets those files were cut into.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `0`

##### evaluated

Snippets the lexical shortlist sent to the judge.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `0`

##### skipped\_files

Listed files that could not be searched (binary, not UTF-8, minified, or unreadable).

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `0`

##### selection\_complete

Whether every snippet was judged; otherwise code with unrelated wording may have been missed.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`
