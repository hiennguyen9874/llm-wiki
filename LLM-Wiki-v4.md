This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.
The content has been processed where security check has been disabled.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: claude-plugin/skills/wiki-manager/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Security check has been disabled - content may contain sensitive information
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
claude-plugin/
  skills/
    wiki-manager/
      references/
        command-prelude.md
        compilation.md
        hub-resolution.md
        indexing.md
        ingestion.md
        librarian.md
        linting.md
        projects.md
        research-infrastructure.md
        wiki-structure.md
      SKILL.md
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="claude-plugin/skills/wiki-manager/references/command-prelude.md">
# Command Prelude

> **Note (v0.4.1):** The hub resolution steps are now inlined directly in each
> command file. Commands no longer depend on reading this file at runtime. This
> file remains as canonical developer documentation for the protocol, but is not
> load-bearing for command execution.

Every `/wiki:*` command starts with the same handful of steps: resolve the hub path, figure out which wiki to use, and decide what to do if no wiki exists. This file is the canonical version of those steps so each command can reference it instead of restating it.

## Why this file exists

The prelude appeared verbatim in 14 command files. Every time the hub resolution protocol changed, it had to be edited in every command. That's a drift trap and an LLM token tax. As of v0.4.1, the steps are inlined in each command file for reliability, but this file remains as the canonical reference for the protocol design.

## Standard prelude

**IMPORTANT: Hub resolution is 1-2 file reads, not an exploration task. Do NOT launch Explore agents, run `find` commands, or search the filesystem. Just read the files below in order.**

Every command that needs a wiki follows these steps in order:

1. **Resolve HUB.** Follow the protocol in [`hub-resolution.md`](hub-resolution.md). Short version: read `~/.config/llm-wiki/config.json` (expand `~` to `$HOME`). If it has `resolved_path`, HUB = that value, done. If no config exists, try `$HOME/wiki/_index.md` as fallback. That's it — one or two file reads at most.

2. **Resolve wiki location.** The target wiki is determined by this order (first match wins):
   1. `--local` flag → `.wiki/` in the current directory
   2. `--wiki <name>` flag → look up in `HUB/wikis.json`
   3. Current directory contains a `.wiki/` → use it
   4. Otherwise → HUB (use the hub's active topic wiki, or fail per the command's wiki-requirement variant below)

3. **Verify existence.** Try to read `<wiki-root>/_index.md`. If missing, follow the command's wiki-requirement variant below.

4. **Parse `$ARGUMENTS`.** Each command defines its own flags; parse them after the wiki is resolved so flag validation can use wiki state (for example, `--project <slug>` checking whether the project exists).

## Wiki-requirement variants

Commands differ in what they do when no wiki is found. Each command picks one of these variants and states it in its task section.

### Variant A: wiki-required (most read/write commands)

If no wiki exists, stop with:

> No wiki found. Run `/wiki init <topic>` first.

Commands using this variant: `compile`, `lint`, `query`, `output`, `plan`, `retract`, `assess`. The rationale is correctness — running these on an empty state would silently produce nothing or corrupt derived caches.

### Variant B: wiki-creating (ingest, research, thesis)

These commands accept `--new-topic <name>` (or equivalent) and will create a topic wiki on the fly when the flag is set. When `--new-topic` is **not** set and no wiki is found, they stop with:

> No wiki found. Use `--new-topic <name>` to create one, or run `/wiki init` first.

The rationale is ergonomics — research and ingestion are often the first operation on a new subject, so forcing a separate `init` step doubles the friction. `--new-topic` is explicit opt-in to creation so the default path still errs cautiously.

### Variant C: wiki-neutral (project, output without articles, status)

These commands either don't require wiki content (project manifest operations, wiki status) or have their own "no articles yet" message. They resolve HUB and wiki location, then handle missing state inline with command-specific messaging.

## Project scoping

Commands that accept `--project <slug>` (`ingest`, `research`, `output`, `compile`) apply it as an explicit flag only. There is no ambient project focus — earlier iterations of this plugin had a `.wiki-session.json` focus mechanism that made project scope sticky, but it was removed in the v0.2 projects simplification. The rationale is documented in [`projects.md`](projects.md) § "Focus": one explicit flag per command is simpler than a whole session-state mechanism, and if a user finds themselves typing `--project foo` on every invocation that's a signal to `cd` into the project folder directly.

## What commands still handle inline

Anything command-specific stays in the command file:

- `### Parse $ARGUMENTS` sections (flag docs)
- Command-specific deviations from the 4-step wiki resolution (e.g., `assess` asks which wiki to compare against when none is specified, `thesis` has its own `--new-topic`-equivalent branching in Phase 1)
- Per-command `--project` behavior details (which commands support it and how they scope outputs)
- The command's actual work (the reason the command exists)

## When to edit this file

Edit `command-prelude.md` when:

- The hub resolution protocol changes (e.g., new config location, new fallback path)
- The wiki resolution order changes (e.g., a new flag like `--wiki` or `--local` is added)
- A new wiki-requirement variant is introduced (e.g., a command that wants to lazy-create a wiki on write)
- The explicit project-scoping rules change

Do **not** edit this file for command-specific changes. Those stay in the command.
</file>

<file path="claude-plugin/skills/wiki-manager/references/compilation.md">
# Compilation Protocol

## Overview

Compilation transforms raw sources into wiki articles. This is the core "LLM compiler" operation — read sources and produce synthesized, cross-referenced knowledge articles.

## Incremental vs Full

- **Incremental** (default): Only process sources ingested since the last compilation date (from master `_index.md`). Compare source `ingested` dates against `Last compiled` in master index.
- **Full** (`--full`): Re-read all sources, rewrite all articles. Expensive but ensures consistency.

## The Compilation Loop

### Step 1: Survey

1. Read `raw/_index.md` to see all sources
2. Read `wiki/_index.md` to see existing articles
3. For incremental: identify sources with `ingested` date after last compile date
4. For full: use all sources
5. Read each uncompiled source in full

### Step 2: Extract

For each source, identify:
- **Key concepts**: nouns, technical terms, named entities
- **Key facts**: claims, data points, measurements, relationships
- **Key relationships**: X relates to Y, X is a type of Y, X was created by Y

### Step 3: Map to Existing Wiki

Read `wiki/_index.md` and category indexes. For each key concept:
- Already has an article? → plan to UPDATE it with new information
- Major concept worthy of its own article? → plan to CREATE one
- Minor mention? → will be referenced within another article

### Step 4: Classify New Articles

- **concept**: A specific, bounded idea explainable in 1-3 pages. Examples: "Transformer Architecture", "Gradient Descent", "Docker Container"
- **topic**: A broader theme tying concepts together. Examples: "Deep Learning", "DevOps", "Functional Programming"
- **reference**: A curated list of resources, tools, or links. Examples: "Python ML Libraries", "Transformer Paper Timeline"

### Step 5: Write/Update Articles

**For new outputs with binary artifacts:** If a new output will produce binary siblings (images, diagrams, CSVs, rendered screenshots, code files), create it inside `output/projects/<slug>/` from the start rather than scattering into `output/` root. The reason is colocation — relative asset paths only work when the markdown and its assets live in the same folder. See `references/projects.md` for the full rationale. If the user passed `--project <slug>` explicitly, write into that project folder. Otherwise prompt for a slug and goal and invoke `/wiki:project new` before writing the artifacts. Loose markdown outputs (no binary siblings) can still land flat in `output/` for backward compatibility.

**For new articles:**

1. Write the abstract paragraph — what is this and why does it matter?
2. Write the body — explain using information from source(s). Synthesize, contextualize, explain. Do NOT copy-paste.
3. When referencing another wiki article inline, use dual-link format: `[[slug|Name]] ([Name](../category/slug.md))` — this serves both Obsidian and the agent.
4. Add "See Also" links to related wiki articles using dual-link format (check wiki index for related tags/concepts)
5. Add "Sources" section linking back to raw files
6. Generate frontmatter per `references/wiki-structure.md` — include `aliases` for alternate names
7. Add `aliases` in frontmatter for any common alternate names (e.g., `aliases: [GPT, Generative Pre-trained Transformer]`)
8. Set `confidence` in frontmatter based on source credibility AND corroboration:
   - `high`: multiple sources with credibility score 4+ agree, OR single peer-reviewed meta-analysis/systematic review
   - `medium`: single credible source (score 2-3), OR multiple sources partially agree, OR recent findings not yet replicated
   - `low`: single non-peer-reviewed source (score 0-1), OR sources disagree, OR anecdotal only

   When Phase 2b credibility scores are available, use them directly. When compiling without a preceding research phase (e.g., manual ingest → compile), assess credibility inline.

When creating or updating a wiki article, set `volatility` and `verified` in frontmatter. Default `volatility` to `warm`. Set `verified` to today's date. If the article's sources are primarily news/trends (type: articles with recent ingestion dates), suggest `hot`. If sources are foundational papers, historical references, or mathematical content, suggest `cold`. The author can override during review.

**For updated articles:**

1. Read the existing article
2. Identify what the new source adds (new facts, perspectives, connections)
3. Integrate new information into appropriate sections using Edit (not full rewrite)
4. Add the new source to the Sources section
5. Update the `updated` date in frontmatter
6. Check if new "See Also" links are warranted

### Step 6: Bidirectional Linking

For every "See Also" link from article A → article B:
- Check if B has a "See Also" link back to A
- If not, add one with a brief relationship note
- Use dual-link format: `[[slug|Name]] ([Name](../category/slug.md)) — relationship note`

### Step 7: Update All Indexes

After all articles are written/updated:

1. Each category `_index.md` (concepts, topics, references) — add/update rows
2. `wiki/_index.md` — add/update rows
3. Master `_index.md` — update article count, set "Last compiled" to today, add to Recent Changes
4. If `output/projects/` exists, regenerate `output/_index.md` as a projects-aware listing: scan each `output/projects/*/WHY.md` for its first `#` heading (title) and first non-heading paragraph (goal, first ~120 chars), list them as a table, then list any remaining loose outputs in `output/` below. This is **best-effort** — if skipped or clobbered by a concurrent session, the next lint/compile will fix it. Member counts per project come from folder scans at render time; there is no cached Members list on disk anymore (the v0.2 simplification removed the `_project.md` manifest, so there's nothing to regenerate inside the project folders themselves — see `references/projects.md`).

## Quality Standards

- **Self-contained**: Articles are readable without consulting raw sources
- **Synthesized**: Draw from multiple sources when possible, not just one
- **Accurate**: Do not simplify to the point of being wrong
- **Clear**: Direct language. Knowledge base, not blog post.
- **Honest disagreement**: When sources disagree, note the disagreement rather than picking a side
- **Connected**: Every article should link to at least one other article via "See Also"
</file>

<file path="claude-plugin/skills/wiki-manager/references/hub-resolution.md">
# Hub Path Resolution

Every wiki operation must resolve the hub path before doing anything else. Follow this protocol exactly.

## Why this protocol exists

The hub path can come from config (most common — iCloud, Dropbox, NAS), a symlink at `~/wiki/` pointing elsewhere, or `~/wiki/` directly (simple). Earlier versions checked `~/wiki/` first, but that fails in sandboxed environments where `~/wiki/` isn't an allowed path. The v0.3 protocol below checks config first (one file read), falling back to `~/wiki/` only when no config exists.

> **Note (v0.4.1):** The resolution steps are now inlined directly in each
> command file. Commands no longer depend on reading this file at runtime. This
> file remains as canonical developer documentation for the protocol, but is not
> load-bearing for command execution.

## Resolution Steps

**This is a sequential file-read protocol. Do NOT use Explore agents, `find`, `ls -R`, or any filesystem search. Each step is a single Read tool call. Most sessions resolve at step 1 or step 2.**

1. **Read `~/.config/llm-wiki/config.json`** (expand `~` to `$HOME`).

2. **If config has `resolved_path`** → **HUB** = that value verbatim (it's already an absolute path — no expansion needed). Done.

3. **If config has only `hub_path`** (no `resolved_path`) → expand the leading `~` ONLY (see Tilde Expansion below), set **HUB**, then **write `resolved_path` back to config** so this expansion never has to happen again:
   ```json
   {
     "hub_path": "~/Library/Mobile Documents/com~apple~CloudDocs/wiki",
     "resolved_path": "/Users/jane/Library/Mobile Documents/com~apple~CloudDocs/wiki"
   }
   ```

4. **If no config exists** → try `$HOME/wiki/_index.md`. If it exists, **HUB** = `$HOME/wiki`. Done.

5. **If nothing found** → ask the user where they want the wiki before creating anything.

Most sessions hit step 1-2 and resolve from config. The `~/wiki/` fallback (step 4) is only for users with no config file.

> **CRITICAL — Do NOT confuse directory existence with hub existence.**
> A directory may exist (e.g., leftover `.DS_Store`, empty folder, or a symlink to an uninitialized path) without being an initialized hub. Only `_index.md` existing at the hub root counts as an initialized hub.

> **Config is authoritative.** If `~/.config/llm-wiki/config.json` exists with a `hub_path` or `resolved_path`, ALL initialization MUST happen at the config path. Never create a hub at `~/wiki/` when config points elsewhere.

> **Never access `~/wiki/` when config exists.** In sandboxed environments, `~/wiki/` may not be an allowed path. The config path is the only path the agent should touch.

## Optional setup: symlink

For users who want the convenience of `~/wiki/` without granting sandbox access to their real wiki path, a symlink works:

```bash
ln -s "/Users/jane/Library/Mobile Documents/com~apple~CloudDocs/wiki" ~/wiki
```

This is optional — config-based resolution (steps 1-2) works without it. The symlink is a convenience for shell access, not a requirement for the agent.

## Tilde Expansion — Correct Method

Only needed when step 3 runs (first use with an old config that lacks `resolved_path`). Replace ONLY the leading `~` with the user's home directory. **Do NOT expand tildes anywhere else** — characters like `~` in `com~apple~CloudDocs` are literal directory names.

```bash
hub_path="~/Library/Mobile Documents/com~apple~CloudDocs/wiki"  # from config
expanded="${hub_path/#\~/$HOME}"
# Result: /Users/jane/Library/Mobile Documents/com~apple~CloudDocs/wiki
#                                  ↑ these tildes are UNTOUCHED
```

**Never** use `eval` or unquoted expansion — these break on paths with spaces.

## Paths with Spaces

The resolved path may contain spaces (e.g., `Mobile Documents`). When using the path in Bash commands, **always double-quote it**:

```bash
ls "$HUB/topics/"           # correct
ls $HUB/topics/             # WRONG — breaks on spaces
```

The Read, Write, Edit, Glob, and Grep tools handle spaces natively.

## After Resolution

Once HUB is resolved, determine which wiki to target:

1. `--local` flag → `.wiki/` in current directory
2. `--wiki <name>` flag → look up in `HUB/wikis.json`
3. Current directory has `.wiki/` → use it
4. Otherwise → HUB (the hub itself)
</file>

<file path="claude-plugin/skills/wiki-manager/references/indexing.md">
# Indexing Protocol

## Purpose

Index files (`_index.md`) are the agent's navigation system. Instead of scanning hundreds of files, the agent reads a single index to find what it needs. This is the key efficiency mechanism.

## The 3-Hop Strategy

When answering a query or finding content:

1. **Hop 1**: Read master `_index.md` → get overview, identify which section is relevant
2. **Hop 2**: Read `wiki/{category}/_index.md` → scan summaries and tags for matches
3. **Hop 3**: Read only the matched article files

This means the agent typically reads 2-3 small index files + 3-8 full articles, rather than scanning dozens of files.

## Derived Index Protocol

**Indexes are a cache, not a source of truth.** The `.md` files and their YAML frontmatter are the source of truth. Indexes are rebuilt on read when stale. This makes the wiki concurrent-safe — multiple sessions can write simultaneously without locks.

### Stale Detection

Before using any `_index.md`, check staleness:

1. Count `.md` files in the directory (excluding `_index.md`)
2. Count rows in the `_index.md` contents table
3. If counts differ → index is stale → rebuild inline before proceeding

### Rebuild Inline

When an index is stale:

1. List all `.md` files in the directory (excluding `_index.md`)
2. Read each file's YAML frontmatter (title, summary, tags, updated)
3. Regenerate the `_index.md` contents table from frontmatter
4. Recalculate statistics (source count, article count, etc.)
5. Write the new `_index.md`
6. Continue with the original operation

### Write Operations (ingest, compile, research)

- Write the article/source file with correct frontmatter — this is the source of truth
- Index updates are **best-effort** — update if convenient, but if skipped or if a concurrent session overwrites, no data is lost
- The next read will detect staleness and rebuild

### Read Operations (query, status, lint)

- Always stale-check before trusting the index
- If stale, rebuild first, then proceed
- This adds a small overhead on first read after writes, but guarantees accuracy

### Why This Works for Concurrency

- Two sessions writing articles simultaneously: both write files, neither corrupts the other
- Index may be momentarily stale or one rebuild may overwrite another's rebuild — but since both rebuild from the same source files on disk, the result converges to the same correct state
- `log.md` is append-only with small atomic writes — already safe
- No locks needed, no stale lock cleanup, no coordination between sessions

## When to Update Indexes (Best-Effort)

Write operations SHOULD update indexes when convenient:
- A file is added to the directory
- A file is removed from the directory
- A file's frontmatter (title, summary, tags) changes
- Statistics change (after compilation, after lint)

But these updates are optional. If skipped (e.g., due to a crash or concurrent write), the next read operation will detect the stale index and rebuild it automatically.

## Index Update Procedure

### Adding a file

1. Read the current `_index.md`
2. Add a new row to the Contents table: `| [filename.md](filename.md) | Summary | tags | YYYY-MM-DD |`
3. If the file's tags introduce a new category, add it to the Categories section
4. Add entry to Recent Changes: `- YYYY-MM-DD: Added filename.md (brief note)`
5. Update "Last updated" date

### Removing a file

1. Read the current `_index.md`
2. Remove the row from Contents table
3. Remove from Categories if it was the only file with that category
4. Add removal entry to Recent Changes
5. Update "Last updated" date

### Master Index Statistics

The root `_index.md` statistics are derived from actual file counts, not manual tracking:
- Sources: count .md files in `raw/` subdirectories (excluding `_index.md`)
- Articles: count .md files in `wiki/` subdirectories (excluding `_index.md`)
- Outputs: count .md files in `output/` (excluding `_index.md`)

## Cross-Wiki Index Peek

When peeking at sibling wikis for overlap:
1. Read `HUB/wikis.json` to get the list of all wikis
2. For each sibling wiki, read ONLY its `_index.md` (not full articles)
3. Check if any summaries or tags match the current query
4. If overlap found, note it in the response — never read full articles from sibling wikis unless explicitly asked
</file>

<file path="claude-plugin/skills/wiki-manager/references/ingestion.md">
# Ingestion Protocol

## Overview

Ingestion converts external material into a standardized raw source file in the wiki's `raw/` directory. Sources are immutable after ingestion.

## Source Types

| Type | Directory | Auto-detect signals |
|------|-----------|-------------------|
| articles | raw/articles/ | General web URLs, blog posts |
| papers | raw/papers/ | arxiv.org, scholar.google, .pdf URLs, academic language |
| repos | raw/repos/ | github.com, gitlab.com URLs |
| notes | raw/notes/ | Freeform text, tweets, no URL |
| data | raw/data/ | .csv, .json, .tsv URLs or files, dataset references |

## URL Ingestion

1. **Detect X.com / Twitter URLs**: If the URL matches `x.com/*/status/*` or `twitter.com/*/status/*`, follow this fallback chain in order:

   **a) Grok MCP (preferred)**: Check if the `grok` MCP server is available by looking for tools matching `mcp__grok__*` (e.g., `mcp__grok__search`). If available, use it to fetch the tweet/thread content. Extract: author handle, display name, full text, date, media descriptions, thread context.
   > Install: [github.com/nvk/ask-grok-mcp](https://github.com/nvk/ask-grok-mcp)

   **b) FxTwitter proxy**: If Grok MCP is not available, rewrite the URL:
   - `x.com/user/status/123` → `https://api.fxtwitter.com/user/status/123`
   - WebFetch this API URL — it returns JSON with full tweet text, author, media, and thread data.
   - Parse the JSON response for `tweet.text`, `tweet.author`, `tweet.created_at`.

   **c) VxTwitter proxy**: If FxTwitter fails, try:
   - `x.com/user/status/123` → `https://api.vxtwitter.com/user/status/123`
   - Same JSON extraction as FxTwitter.

   **d) Direct WebFetch**: Last resort — WebFetch the original `x.com` URL. This often returns limited content (login walls), but sometimes works for public tweets.

   **e) Manual fallback**: If all above fail, report: "Could not fetch tweet content. Options: install [ask-grok-mcp](https://github.com/nvk/ask-grok-mcp) for X.com access, or paste the tweet text manually via `/wiki:ingest \"text\" --title \"@author tweet\"`."

   Type: notes (unless overridden).

2. **General URLs**: Use WebFetch to retrieve content. Prompt:

   > "Extract the complete article content from this page. Return: title, author(s) if listed, date published if listed, and the full article text preserving all factual claims, data points, code examples, and technical details. Format as clean markdown."

3. **GitHub repo URLs**: Use WebFetch with prompt:

   > "Extract from this GitHub repository: name, description, key technologies, main purpose, README content. Format as markdown."

4. **Failure handling**: If WebFetch fails (auth wall, paywall), report the failure. Suggest: paste content manually via `/wiki:ingest "text" --title "Title"`.

## File Ingestion

1. Read the file directly
2. Markdown → preserve formatting
3. Plain text → wrap in markdown
4. JSON/CSV/structured data → describe schema + representative sample (not full dataset)
5. Images → create a metadata stub noting the image path and any visible content description

## Freeform Text Ingestion

1. User provides quoted text as the argument
2. If `--title` not provided, derive a title from the first sentence or ask
3. Auto-tag based on content keywords

## Inbox Processing

The `inbox/` directory is a drop zone. Users dump files there via Finder, `cp`, etc.

### Processing `--inbox`:

1. Scan `inbox/` for all files (exclude `.processed/` subdirectory and hidden files)
2. For each file:
   - `.url` or `.webloc` files → extract the URL, then follow URL ingestion flow
   - `.md` or `.txt` files → ingest as notes or articles (auto-detect)
   - `.pdf` files → create a metadata stub, note the file path for reference
   - `.json`, `.csv`, `.tsv` → ingest as data
   - Other files → create a metadata stub noting file type and path
3. Move each processed file to `inbox/.processed/` (or delete if user did not pass `--keep`)
4. Report each item processed
5. If 5+ items were processed, suggest: "You've ingested N new sources. Want me to compile? Run `/wiki:compile`"

## Slug Generation

1. Take the title, lowercase, replace spaces with hyphens, remove special characters
2. Prepend today's date: `YYYY-MM-DD-`
3. Truncate to 60 characters max (not counting .md extension)
4. Example: "Attention Is All You Need" → `2026-04-04-attention-is-all-you-need.md`
5. If a file with that slug already exists, append `-2`, `-3`, etc.

## Post-Ingestion Index Updates

After writing each source file, update indexes in order:

1. `raw/{type}/_index.md` — add row to Contents table
2. `raw/_index.md` — add row to Contents table
3. `_index.md` (master) — increment source count, add to Recent Changes

## Batch Ingestion

If the user provides multiple URLs or paths (comma-separated, space-separated, or one per line), process each sequentially. Report progress after each item.

## Compilation Nudge

After ingestion, count uncompiled sources (sources ingested after last compile date). If 5+, suggest running `/wiki:compile`.
</file>

<file path="claude-plugin/skills/wiki-manager/references/librarian.md">
# Librarian Reference

Content-level wiki maintenance: staleness detection, quality scoring, factual verification, semantic coherence, deduplication. This reference defines the scoring algorithms, report formats, and operational protocols for `/wiki:librarian`.

## Design Principles

1. **Score then act.** The librarian produces scores and reports. It never modifies wiki content during a scan. Write operations (fix, auto-fix) are separate commands requiring explicit confirmation.
2. **Conservative by default.** When uncertain, flag for human review rather than auto-classifying as clean. Lean toward false positives over false negatives.
3. **Checkpoint everything.** After scoring each article, write the result to `.librarian/checkpoint.json`. If the session drops, the next invocation resumes from where it left off.
4. **Two-tier escalation.** Quick metadata-only scan first (cheap). Deep content read only for articles that score below threshold or have `volatility: hot`. Token cost scales with problem density, not wiki size.
5. **Machine-readable first.** `.librarian/scan-results.json` is the source of truth. `REPORT.md` is rendered from it. Other skills read the JSON.

## Staleness Scoring (Pass 1)

Composite score 0-100 across four dimensions, each contributing 0-25 points. Uses the same four dimensions as the freshness design in `wiki-structure.md`, applied per-article.

### Dimensions

| Dimension | Measures | Source Field | Computation |
|-----------|----------|-------------|-------------|
| Source freshness | Age of raw sources | `sources:` → each raw file's `ingested:` date | Average days since ingestion across all sources |
| Verification recency | Last human confirmation | `verified:` date | Days since verified |
| Compilation recency | Article currency | `updated:` date | Days since updated |
| Source chain integrity | Referenced sources exist | `sources:` entries | Percentage of sources that resolve to actual files |

### Decay Curves by Volatility

Each dimension's raw day-count is converted to a 0-25 score using exponential decay scaled by the article's `volatility` tier:

| Volatility | Half-life (days) | Effect |
|------------|-----------------|--------|
| `hot` | 30 | Score decays quickly — 60-day-old hot article scores ~50% |
| `warm` | 90 | Moderate decay — 90-day-old warm article scores ~50% |
| `cold` | 365 | Slow decay — cold articles stay fresh for a year |

**Formula per dimension** (except source chain integrity):

```
dimension_score = 25 * 0.5^(days_old / half_life)
```

**Source chain integrity** (no decay — binary per source):

```
integrity_score = 25 * (resolved_sources / total_sources)
```

**Composite staleness score**:

```
staleness_score = source_freshness + verification_recency + compilation_recency + integrity
```

Range: 0 (completely stale) to 100 (perfectly fresh).

### Missing Fields

- Missing `volatility`: treat as `warm` (safe default, matches C15 auto-fix)
- Missing `verified`: treat as never verified — verification_recency = 0
- Missing `updated`: fall back to `created` date
- Missing `sources`: integrity = 0 (no sources to verify)

### Staleness Threshold

Read `freshness_threshold` from the wiki's `config.md` (default: 70). Articles scoring below this threshold are flagged.

## Quality Scoring (Pass 5)

Four dimensions, each scored 1-5. Composite quality score is the average, mapped to 0-100.

### Dimensions

| Dimension | 1 (Stub) | 3 (Adequate) | 5 (Featured) |
|-----------|----------|-------------|--------------|
| **Depth** | Single paragraph, no structure | Multiple sections, covers key aspects | Comprehensive treatment with nuance, examples, and edge cases |
| **Source quality** | No sources or single low-confidence source | 2-3 sources, mixed confidence | 4+ high-confidence sources that corroborate |
| **Coherence** | Disjointed, no logical flow | Readable structure, minor gaps | Clear narrative arc, smooth transitions, no logical gaps |
| **Utility** | Trivial or obvious information | Useful for understanding the topic | Actionable for decision-making, includes tradeoffs and recommendations |

### Scoring Protocol

**Tier 1 (metadata-only, all articles)**:
- Source quality: count sources, read their `confidence:` fields. Score derivable without reading article body.
- Depth (proxy): word count + heading count from file stats. <200 words or 0 headings = stub (1-2). >1000 words + 3+ headings = likely good (4-5).

**Tier 2 (deep read, escalated articles only)**:
- Read the full article body.
- Score coherence and utility by analyzing the content.
- Refine the depth and source quality scores from Tier 1.
- Escalation triggers: staleness score < 70, volatility = hot, or Tier 1 depth proxy = 1-2.

### Quality Flags

In addition to numeric scores, tag articles with specific quality flags:

| Flag | Trigger |
|------|---------|
| `thin-coverage` | Depth score 1-2 |
| `single-source` | Only one source in `sources:` |
| `low-confidence-sources` | Average source confidence below medium |
| `no-see-also` | Zero "See Also" cross-references |
| `stale` | Staleness score below threshold |
| `unverified` | Missing `verified:` field |

### Composite Quality Score

```
quality_score = ((depth + source_quality + coherence + utility) / 4) * 20
```

Range: 20 (worst possible — all 1s) to 100 (all 5s). Articles below 50 are surfaced for review.

## Checkpoint Protocol

The `.librarian/` directory lives inside each topic wiki (e.g., `~/wiki/topics/meta-llm-wiki/.librarian/`). Created on first scan.

### checkpoint.json

Written after each article is scored. If the session drops, the next `scan` or `scan --resume` reads this file and skips already-scored articles.

```json
{
  "scan_id": "2026-04-22T10:30:00Z",
  "wiki": "meta-llm-wiki",
  "passes": ["staleness", "quality"],
  "scope": "full",
  "threshold": 70,
  "completed": ["wiki/concepts/article-a.md", "wiki/concepts/article-b.md"],
  "pending": ["wiki/topics/article-c.md"],
  "results": {
    "wiki/concepts/article-a.md": {
      "staleness": { "score": 92, "factors": { "source_freshness": 23, "verification": 24, "compilation": 22, "integrity": 23 } },
      "quality": { "score": 85, "dimensions": { "depth": 4, "source_quality": 5, "coherence": 4, "utility": 4 }, "flags": [] },
      "tier": 1,
      "scanned_at": "2026-04-22T10:31:00Z"
    }
  }
}
```

**Atomic writes**: Write to `.librarian/.checkpoint.tmp`, then rename to `checkpoint.json`. Incomplete writes from crashes are detected (missing or unparseable tmp file) and the last article is rescanned.

**Clearing**: Checkpoint is deleted when a scan completes successfully and `scan-results.json` is written.

### scan-results.json

The complete scan output. Source of truth for other skills.

```json
{
  "scan_id": "2026-04-22T10:30:00Z",
  "wiki": "meta-llm-wiki",
  "completed_at": "2026-04-22T10:45:00Z",
  "passes": ["staleness", "quality"],
  "threshold": 70,
  "summary": {
    "articles_scanned": 29,
    "stale_count": 4,
    "low_quality_count": 2,
    "avg_staleness": 78,
    "avg_quality": 72,
    "worst_staleness": { "article": "wiki/topics/some-topic.md", "score": 31 },
    "worst_quality": { "article": "wiki/concepts/some-concept.md", "score": 42 }
  },
  "articles": {
    "wiki/concepts/article-a.md": {
      "staleness": { "score": 92, "factors": { "source_freshness": 23, "verification": 24, "compilation": 22, "integrity": 23 } },
      "quality": { "score": 85, "dimensions": { "depth": 4, "source_quality": 5, "coherence": 4, "utility": 4 }, "flags": [] },
      "tier": 1
    }
  }
}
```

### REPORT.md

Human-readable report generated from `scan-results.json`. Format:

```markdown
# Librarian Report — YYYY-MM-DD

> Scanned N articles in <wiki-name>. Passes: staleness, quality.

## Summary

| Metric | Value |
|--------|-------|
| Articles scanned | N |
| Below staleness threshold | N |
| Low quality (< 50) | N |
| Average staleness | N/100 |
| Average quality | N/100 |

## Stale Articles (staleness < threshold)

| Article | Score | Top Factor | Recommendation |
|---------|-------|-----------|----------------|
| [Title](path) | 31/100 | sources 180d old | refresh |
| [Title](path) | 45/100 | unverified 120d | verify |

## Low Quality Articles (quality < 50)

| Article | Score | Flags | Recommendation |
|---------|-------|-------|----------------|
| [Title](path) | 42/100 | thin-coverage, single-source | expand and add sources |

## All Articles (sorted by combined score)

| Article | Staleness | Quality | Flags |
|---------|-----------|---------|-------|
| ... | ... | ... | ... |
```

### log.md

Append-only librarian activity log at `.librarian/log.md`:

```
## [YYYY-MM-DD] scan | N articles, M stale, K low-quality (passes: staleness, quality)
## [YYYY-MM-DD] scan --article wiki/concepts/foo.md | staleness 45, quality 72
```

## Boundary with Other Commands

| Command | Responsibility | Librarian Does NOT |
|---------|---------------|-------------------|
| `lint` | Structure: broken links, missing indexes, frontmatter schema, file placement | Lint's territory — librarian skips |
| `lint --deep` (C7) | Quick spot-check: a few web searches for obvious staleness | Lightweight — librarian goes deeper |
| `refresh` | Re-fetch sources, compare changes, offer recompilation | Librarian flags, then delegates to refresh |
| `compile` | Transform raw sources into wiki articles | Librarian reviews compiled output, never compiles |

When the librarian flags an article as stale and the user confirms, it delegates to the refresh protocol in `commands/refresh.md` for that article.
</file>

<file path="claude-plugin/skills/wiki-manager/references/linting.md">
# Linting Rules

## Development Note — Lint is the Migration

**When you change the canonical structure or frontmatter schema, update the rules in this file and in `compilation.md` — do NOT write migration code.**

The wiki treats "file in the wrong place from an old version" and "file in the wrong place from user error" as the same defect. `/wiki:lint --fix` heals both, idempotently. Indexes are already derived caches (see `indexing.md` Derived Index Protocol) — this principle extends to file placement and frontmatter shape.

There are two layers where this principle applies, each with its own rules:

- **Mechanical layer (C11/C12/C13)** — raw-source and wiki-article placement and frontmatter schema. Fully auto-fixable because the canonical location and field shape are pure functions of frontmatter. No judgment required.
- **Editorial layer (C8/C9)** — project grouping inside `output/projects/`. **Never auto-fixed** because "these files belong together" requires human sense-making. C9 surfaces candidates and emits ready-to-paste `/wiki:project new` + `/wiki:project add` blocks for the user to run.

Concretely, when evolving the schema:

- **Renamed a `raw/` or `wiki/` directory?** Update the placement map in C11 and the allowlist in C12. Every existing wiki self-heals on the next lint.
- **Renamed a frontmatter field?** Append an entry to C13's alias table (old → new). Never remove old aliases.
- **Changed an enum value?** Add a value alias in C13. Never remove old values.
- **Added a required field?** Add it to C2 and give it an inference rule (derive from body/filename) or a sane default.
- **New directory under `raw/` or `wiki/`?** Add it to C12's allowlist and C11's placement map.
- **New project-level structure or manifest rule?** Update C8 (and projects.md). Candidate heuristics go in C9.

There is no `/wiki:migrate` command and there should never be one. Lint rules **are** the schema.

**When editing the canonical spec** (`wiki-structure.md`, `compilation.md`, `ingestion.md`, `projects.md`, or any reference that defines paths or frontmatter fields), also:

1. Update the relevant check(s) in this file — mechanical changes touch C11/C12/C13; project-model changes touch C8/C9.
2. Verify `commands/lint.md` still runs the placement/alias pass in the correct order.
3. Verify `commands/compile.md` still runs the placement pre-check on `raw/` as step 0.

## Severity Levels

- **Critical**: Broken functionality — missing indexes, broken links, corrupted frontmatter
- **Warning**: Inconsistency — mismatched counts, stale dates, non-bidirectional links
- **Suggestion**: Improvement opportunity — new connections, missing tags, content gaps

## Check Catalog

### C1: Structure (Critical)

- [ ] Master `_index.md` exists
- [ ] `config.md` exists
- [ ] Every subdirectory under `raw/` and `wiki/` has `_index.md`
- [ ] `output/` has `_index.md`
- [ ] Every `.md` file (excluding `_index.md` and `config.md`) has valid YAML frontmatter delimited by `---`

### C2: Frontmatter (Critical/Warning)

- [ ] Every raw source has: title, source, type, ingested, tags, summary
- [ ] Every wiki article has: title, category, sources, created, updated, tags, summary
- [ ] No empty title or summary fields
- [ ] `category` is one of: concept, topic, reference
- [ ] `type` is one of: articles, papers, repos, notes, data
- [ ] `tags` is a list, not empty

### C3: Index Consistency (Warning)

- [ ] Every .md file in a directory appears in that directory's `_index.md` Contents table
- [ ] No `_index.md` references a non-existent file (dead entries)
- [ ] Statistics in master `_index.md` match actual file counts
- [ ] "Last compiled" and "Last lint" dates are present and valid

### C4: Link Integrity (Warning)

- [ ] All markdown links `[text](path)` in wiki articles resolve to existing files
- [ ] All "See Also" links are bidirectional (if A→B, then B→A)
- [ ] All "Sources" links in wiki articles point to existing raw files

### C4b: Source Provenance (Warning)

- [ ] All `sources:` entries in wiki article frontmatter point to existing raw files (no dangling references to deleted/retracted sources)
- [ ] No `<!--RETRACTED-SOURCE-->` markers remain in article body (these should be resolved via `--recompile` or manual review)
- [ ] No raw source file is referenced by zero wiki articles (orphan source — suggest compilation or removal)

### C5: Tag Hygiene (Warning)

- [ ] No near-duplicate tags (e.g., `ml` and `machine-learning`, `nlp` and `natural-language-processing`)
- [ ] Tags in article frontmatter match tags listed in `_index.md` entries
- [ ] Suggest canonical tag when duplicates found

### C6: Coverage (Suggestion)

- [ ] Every raw source is referenced by at least one wiki article's `sources` field
- [ ] No wiki article has an empty `sources` field
- [ ] Articles with overlapping tags that don't link to each other via "See Also" — suggest connection
- [ ] Orphan articles: no incoming "See Also" links from other articles

### C7: Deep Checks (Suggestion, --deep only)

- [ ] Use WebSearch to verify key factual claims in wiki articles
- [ ] Identify articles that could be enhanced with newer information
- [ ] Suggest new articles that would connect existing ones
- [ ] Check for stale sources (ingested > 6 months ago with no recent compilation)

### C8: Project Hygiene (Critical/Warning/Suggestion)

Validates projects under `output/projects/`. The architecture was simplified in v0.2: a project is a folder with a `WHY.md` that holds the goal/rationale in plain markdown. No manifest format, no DERIVED sections, no status field. See `references/projects.md` for the full rationale.

**Execution order**: run C8c (migration) first so migrated projects pass C8a in the same lint pass. The labels below are in execution order, not alphabetical.

- [ ] **C8c** Legacy `_project.md` migration (**Critical** — auto-fixable). See migration rule below. Runs first so any legacy manifests are healed into `WHY.md` before the presence check looks for them.
- [ ] **C8a** Every `output/projects/<slug>/` directory has a `WHY.md` with non-empty content (**Critical** — projects without rationale become black boxes; LLMs rebuild wrong without the why). The file has no frontmatter requirement. Any `#` heading + body counts as non-empty.
- [ ] **C8d** Slug conforms to spec: lowercase, hyphen-separated, ≤40 chars, no dates (**Warning**).
- [ ] **C8b** Staleness check — for every project, compute transitive source freshness (**Suggestion**). For each member file with `sources:` frontmatter, follow the chain to raw sources. If any raw source's `ingested:` date is newer than the member's `updated:` date, the project may be stale. Report as: `Project <slug> may be stale: N source(s) newer than member artifacts.` Never auto-fixed — staleness triggers human re-evaluation, not automatic regeneration.

**C8c migration rule** (legacy `_project.md` → `WHY.md`):

Pre-v0.2 wikis have `_project.md` manifests with YAML frontmatter and derived Members sections. When lint encounters one:

1. Read `_project.md` frontmatter — extract `goal` and `title` (fall back to slug-derived title if `title:` is absent).
2. Read the body and split into sections by `## ` headings.
3. Identify **derived sections** to drop: any section whose body is (a) entirely between `<!-- DERIVED -->` and `<!-- /DERIVED -->` delimiter comments, or (b) matches the header text `## Members` or `## External Members` even if delimiters are missing. These are regeneratable and not precious.
4. Identify **human sections** to preserve: everything else. This includes `## Goal`, `## Context`, `## Current State`, `## Research Sessions`, and any custom sections the user added (decision logs, open questions, retrospectives, etc.). **The default is preserve — when in doubt, keep it.** LLMs rebuild wrong without rationale, and custom sections are almost always rationale.
5. Determine how to surface the goal. Two cases:
   - **If the body has a `## Goal` section**: preserve it as-is. Do NOT also prepend the frontmatter `goal:` text — that would duplicate. The body version usually has more detail and the same or better phrasing.
   - **If the body has no `## Goal` section**: prepend the frontmatter `goal:` text as the first body paragraph of `WHY.md`, so the rationale is visible without reading the whole file.
6. Write `WHY.md` in the same folder, structured as:
   ```markdown
   # <title>

   <frontmatter goal as first paragraph — ONLY if the body had no ## Goal section; otherwise omit this paragraph>

   <every preserved human section from step 4, in original order, with original `## ` headings>
   ```
7. Delete `_project.md`.
8. Report: `Migrated <slug>/_project.md → <slug>/WHY.md (preserved N sections: <list>).`

**Lossless guarantee**: every human-written section that existed in `_project.md` appears verbatim in `WHY.md`. The only things dropped are frontmatter metadata (dates live in git log, status in filesystem state, tags are optional, type is structural) and derived Members/External Members lists (recomputable by scanning the folder — never precious).

This is the first real application of the lint-is-the-migration principle codified in this file's dev note. Idempotent — re-running has no effect once WHY.md exists. No separate migration command, no version detection. Just lint.

### C9: Project Candidates (Suggestion)

Surfaces loose `output/` content that should be grouped into projects. **Never auto-fixed** — grouping decisions require human judgment.

- [ ] **C9a** Binary assets (`.png`, `.jpg`, `.pdf`, `.csv`, `.svg`, `.zip`) loose directly in `output/` root (not inside `projects/`) — these cannot stay loose per the projects architecture because relative asset paths break. Propose the likely owning project based on filename prefix. (**Critical** — architecture violation)
- [ ] **C9b** Any subdirectory inside `output/` that is NOT `projects/` (or `.archive/` inside `projects/`) and contains files — architecture violation, all subdirectories should be under `output/projects/`. (**Critical**)
- [ ] **C9c** Any `output/projects/<slug>/` folder without a `WHY.md` — this is a malformed project. Suggest: `echo "# <Title>\n\nTODO: goal" > WHY.md` or run `/wiki:project new <slug> "goal"` after archiving the existing folder. (**Warning**)
- [ ] **C9d** ≥3 loose markdown outputs in `output/` that share a common slug prefix (after stripping dates, version tags, and type prefixes) — suggest grouping into a project. (**Suggestion**)

**Candidate report format** (for C9d):

```
### Project Candidates (N)

Suggested: bitcoin-quantum-fud (proposed slug)
  Reason: 5 files share prefix "article-bitcoin-quantum-fud-"
  Files:
    - article-bitcoin-quantum-fud-2026-04-05.md
    - article-bitcoin-quantum-fud-v2-2026-04-06.md
    ...
  Create with:
    /wiki:project new bitcoin-quantum-fud "TODO: fill in goal"
    /wiki:project add bitcoin-quantum-fud article-bitcoin-quantum-fud-2026-04-05.md
    ...
```

**Slug derivation heuristic** (C9d): longest common prefix of ≥3 files, stripped of trailing hyphens, dates (`YYYY-MM-DD`), version tags (`-v\d+`, `-final`, `-release`), and the `article-` / `output-` / `report-` prefixes. If the result is <4 chars or ambiguous, report without a proposed slug and let the user name it.

### C11: Canonical Placement (Critical)

A `raw/` or `wiki/` file's correct path is a pure function of its frontmatter. Misplacement is a structural defect regardless of whether the cause was user error or an old wiki layout. This is the mechanical counterpart to C8/C9, which handle project-level organization. C11 does not touch `output/projects/` — that's C8's territory.

**Placement map** (derive expected path from frontmatter). Resolve in order — the first matching rule wins:

| Order | File kind | Frontmatter key | Value → directory |
|-------|-----------|----------------|-------------------|
| 1 | Thesis file (wiki-side) | `type: thesis` | `wiki/theses/` |
| 2 | Raw source | `type` | `articles` → `raw/articles/`, `papers` → `raw/papers/`, `repos` → `raw/repos/`, `notes` → `raw/notes/`, `data` → `raw/data/` |
| 3 | Wiki article | `category` | `concept` → `wiki/concepts/`, `topic` → `wiki/topics/`, `reference` → `wiki/references/` |

**Disambiguating raw `type: articles/papers/...` from wiki thesis `type: thesis`**: Rule 1 matches only when the value is literally `thesis`. Raw sources never use `thesis` as a type. A file whose frontmatter has both `category` and `type` is a wiki article — use `category` (rule 3). A file with only `type: thesis` is a thesis file (rule 1). A file with only `type` in {articles, papers, repos, notes, data} is a raw source (rule 2).

**Checks**:

- [ ] For every `.md` file under `raw/` and `wiki/` (excluding `_index.md` and `config.md`), compute the expected directory from frontmatter and compare to the actual directory.
- [ ] Raw sources at the hub level (not inside a topic wiki) → misplaced. Hub must only contain `wikis.json`, `_index.md`, `log.md`, and `topics/`.
- [ ] Content directories (`raw/`, `wiki/`, `output/`, `inbox/`) at the hub level → misplaced. Move contents into a topic wiki or quarantine.
- [ ] Files with missing or unreadable frontmatter → defer to C2 (frontmatter fix) before placement can be determined.
- [ ] Out of scope: anything under `output/projects/`. Project-level placement is C8/C9.

**Auto-fix**: `mv` the file to its canonical path (create the destination directory if missing). If the destination already contains a file with the same slug, skip and warn (potential duplicate — user must resolve). After any move, the containing indexes on both sides are invalidated and will rebuild on next read per the Derived Index Protocol.

### C12: Unknown File Quarantine (Warning)

Any file that is not in the canonical allowlist for its location is either a user mistake, a stale artifact from an older wiki version, or a legitimate new kind of thing that the schema hasn't caught up to. Lint surfaces it either way. Like C11, this is scoped to `raw/`, `wiki/`, and the wiki root — not `output/projects/` (C8 handles that).

**Allowlists** (per location):

| Location | Allowed items |
|----------|--------------|
| HUB | `wikis.json`, `_index.md`, `log.md`, `topics/` |
| Topic wiki root | `_index.md`, `config.md`, `log.md`, `raw/`, `wiki/`, `output/`, `inbox/`, `.obsidian/`, `.research-session.json`, `.thesis-session.json` |
| `raw/` | `_index.md`, `articles/`, `papers/`, `repos/`, `notes/`, `data/` |
| `wiki/` | `_index.md`, `concepts/`, `topics/`, `references/`, `theses/` |
| `raw/<type>/` | `_index.md` + `*.md` files with valid frontmatter |
| `wiki/<category>/` | `_index.md` + `*.md` files with valid frontmatter |
| `inbox/` | `.processed/`, `.unknown/`, user-dropped files |

**Checks**:

- [ ] Walk `raw/`, `wiki/`, and the wiki root. For each entry, check against the allowlist for that location.
- [ ] Flag unknown files and directories.
- [ ] Skip `output/` — C8 and C9 own that subtree.

**Auto-fix**:

- Unknown `.md` file with valid frontmatter → route via C11 (canonical placement).
- Unknown `.md` file without frontmatter → move to `inbox/.unknown/` for user triage.
- Unknown directory → **do not auto-delete**. Warn only. Directories may hold user data.
- Unknown non-`.md` file at an unexpected location → move to `inbox/.unknown/`.

### C13: Frontmatter Aliases (Warning)

Legacy field names and enum values are rewritten to their canonical form. This is the one place where schema evolution is encoded — add aliases here instead of writing migrations. Run this check **before** C2 and C11 so downstream checks see canonical field names.

**Why this check exists at all (even while empty):** we want the *framework* for schema evolution in place before we need it, so the first rename ever made to a frontmatter field is a one-line addition to a table rather than "let's design a migration system." The dev note at the top of this file explains the full lint-as-migration principle. C13 itself is the mechanism.

**Key aliases** (old → canonical, append-only — never remove an entry). Populate this table when a real field rename happens; do not pre-populate with speculative entries.

```
# (empty — add entries as schema evolves)
# Format:  old_key  →  canonical_key
# Example: source_url  →  source        # added when raw sources dropped source_url in v0.X.Y
```

**Value aliases** (enum drift — append-only). Populate when an enum value is renamed.

```
# (empty — add entries as enums evolve)
# Format:  old_value  →  canonical_value  (for field: <field_name>)
# Example: article  →  articles  (for field: type)  # added when type enum went plural
```

Note: thesis files use `type: thesis`, not `category`. Do not alias `theses` to a `category` value if anyone ever proposes it — theses are their own file kind under C11 rule 1.

**Checks**:

- [ ] For every `.md` file's frontmatter, scan keys against the key-alias table. If a match is found, rewrite the key to canonical (preserve value).
- [ ] For fields with known enums (`type`, `category`, `confidence`), scan values against the value-alias table. If a match is found, rewrite the value to canonical.
- [ ] Unknown keys not in the alias table and not in the canonical schema → warn (potential new alias needed or typo).

**Auto-fix**: Rewrite the YAML key or value in place using Edit. Preserve field order and comments.

**When the tables are empty** (current state), C13 only runs the unknown-key warning — alias rewriting is a no-op. This is the honest default: we have no backward-compat debt yet, so advertising alias entries would be fiction. First real rename → first real alias entry.

### C14: Freshness (Warning/Info)

Computes a composite freshness score (0-100) for each compiled wiki article based on four dimensions: source freshness, verification recency, compilation recency, and source chain integrity. Each dimension contributes 0-25 points, with decay curves scaled by the article's `volatility` tier. See `wiki-structure.md` § Freshness Score for the full formula.

- [ ] For each wiki article with `volatility` and `verified` fields, compute the four-dimension composite score
- [ ] Read `freshness_threshold` from `config.md` (default: 70 if not set)
- [ ] Flag articles scoring below the threshold

**Severity**: Warning for `hot` and `warm` articles below threshold. Info for `cold` articles below threshold (Lindy Effect — cold content scoring low is unusual and worth noting, but rarely urgent).

**Output**: `Freshness score [score]/100: [article] — source age [avg days], verified [days] ago, compiled [days] ago, [N/M] sources intact. Run /wiki:refresh [path]`

**Auto-fix**: None. Freshness requires human judgment — automated recompilation risks the "confident wrong answer" problem where stale content is replaced by hallucinated content.

### C15: Missing Volatility (Info)

Flags wiki articles that lack the `volatility` field. New articles should always have volatility set during compilation.

- [ ] For each `.md` file in `wiki/` (excluding `_index.md`), check for `volatility` field in frontmatter
- [ ] Flag files missing the field

**Severity**: Info (not blocking — existing wikis predate this field).

**Auto-fix**: Add `volatility: warm` and `verified: <updated date from frontmatter>` — safe defaults that put the article into the standard monitoring cadence.

## Auto-Fix Rules (when --fix is set)

| Issue | Auto-Fix Action |
|-------|----------------|
| Missing `_index.md` | Generate from directory contents (read frontmatter of each file) |
| File not in index | Add row using file's frontmatter data |
| Dead index entry | Remove the row |
| Statistics mismatch | Recalculate from actual file counts |
| Missing bidirectional link | Add "See Also" entry to the article missing the backlink |
| Empty frontmatter field | Infer: title from `# heading`, summary from first paragraph |
| Near-duplicate tags | Replace all instances with the canonical form |
| Dangling source reference | Remove the entry from `sources:` frontmatter |
| Unresolved retraction marker | Warn: "Retracted claim not yet reviewed — run `/wiki:retract --recompile` or edit manually" |
| **C8a** `output/projects/<slug>/` missing `WHY.md` | **Warn only** — a project without rationale is a malformed project. Report and prompt the user to create one. Auto-creation would manufacture a fake goal, which is worse than the missing file. |
| **C8b** Staleness detected | **Never auto-fix** — staleness is a signal for human re-evaluation, not automatic content regeneration. |
| **C8c** Legacy `_project.md` found | Migrate to `WHY.md`: extract goal + title + preserved sections from manifest frontmatter and body, write `WHY.md`, delete `_project.md`. See C8 migration rule for the full procedure. |
| Stale `output/_index.md` when `projects/` exists | Regenerate as a projects-aware listing: scan `output/projects/*/WHY.md` for first-heading titles + first-paragraph goals, list them as a table, then list any remaining loose outputs in `output/` below. |
| **C9a/C9b** architecture violations | **Warn** — surface the problem, suggest the fix, never auto-move. User decides. |
| **C9c** Project folder without `WHY.md` | **Warn only** — same as C8a but surfaced in the candidates section. Suggest running `/wiki:project new <slug> "goal"` with the existing slug. |
| **C9d** Loose markdown cluster | **Never auto-fix** — grouping is human-authored via `/wiki:project new` + `/wiki:project add`. |
| **C11** Misplaced file in `raw/` or `wiki/` | `mv` to canonical path derived from frontmatter; create destination dir if missing; invalidate containing indexes. Skip and warn on slug collision |
| **C11** Content dir at hub level | Move contents into appropriate topic wiki or quarantine to `inbox/.unknown/`. Never delete user data |
| **C12** Unknown file in known location | Route through C11 if it has frontmatter, else move to `inbox/.unknown/` |
| **C12** Unknown directory | **Warn only** — never auto-delete |
| **C13** Legacy frontmatter key | Rewrite key to canonical per alias table |
| **C13** Legacy enum value | Rewrite value to canonical per alias table |
| **C14** Article below freshness score threshold | **Warn/Info only** — composite score below `freshness_threshold` (default 70). Report score breakdown and suggest `/wiki:refresh`. |
| **C15** Missing volatility field | Add `volatility: warm` and `verified: <updated>` — safe defaults |

## Report Format

**User-facing output must lead with plain-English descriptions, not check codes.** The C-codes (C1, C8c, C11, etc.) are internal identifiers for cross-referencing between this file and `commands/lint.md`. They must never appear as the leading text in any line the user sees. If a code is useful for debugging, append it in parentheses at the end — but prefer omitting it entirely.

```markdown
## Wiki Lint Report — YYYY-MM-DD

### Summary
- Ran N health checks
- Issues found: N (N critical, N warnings, N suggestions)
- Auto-fixed: N (if --fix was used)

### Critical Issues
1. [description] — [file path]

### Warnings
1. [description] — [file path]

### Suggestions
1. [suggestion] — [reasoning]

### Coverage
- Sources with no wiki articles: [list]
- Wiki articles with broken links: [list]
- Missing bidirectional links: [list]
- Potential new connections: [list]

### Projects
- Active: N | Archived: N (in `.archive/`)
- Missing project rationale (WHY.md): [list of slugs]
- Possibly stale (sources newer than artifacts): [list of slugs with source-count diff]
- Migrated legacy manifests (_project.md → WHY.md): [list of slugs]

### Project Candidates
- [grouped suggestions, formatted as the candidate report block above]

### File Placement & Schema
- Misplaced files moved to canonical location: [count, list of moves as `old → new`]
- Unknown files quarantined to inbox: [count, list of moves to `inbox/.unknown/`]
- Legacy frontmatter keys updated: [count by alias]
- Legacy enum values updated: [count by alias]
- Unknown directories (not auto-deleted): [list]
```
</file>

<file path="claude-plugin/skills/wiki-manager/references/projects.md">
# Projects

Projects group related outputs — markdown deliverables, images, code, data — into a single folder with a goal. They live inside a topic wiki's `output/projects/` directory.

## Why projects exist at all

Outputs are often multi-artifact. A single deliverable can produce a markdown playbook plus images referenced by `![](screenshot.png)`, a Python prototype, a CSV export, and a generated diagram. **Relative paths only work when these artifacts colocate.** A pure metadata overlay that keeps `output/` flat and tags via frontmatter breaks the moment the first binary asset appears — markdown image links no longer resolve, scripts can't find their data files, and the user has to manually prefix every asset reference.

Project folders solve this by making colocation the primary structure. The folder *is* the project. Everything else (goal, status, members) is derivable from the folder and what's in it.

## Why `WHY.md` is the only required file

Earlier iterations of this architecture (v0.1.0, v0.1.1) used a `_project.md` manifest with YAML frontmatter (`type: project-manifest`, `goal`, `status`, `created`, `updated`), human-written narrative sections, and a derived Members list between `<!-- DERIVED -->` delimiters. That manifest held exactly one thing that couldn't be derived from elsewhere: **the goal — the "why this project exists"**. Everything else (status, timestamps, member list) was either filesystem state or derivable by scanning the folder.

`WHY.md` preserves the precious part (the goal / rationale / "why") and drops the machinery around it. It is plain markdown, no frontmatter, no schema. The convention is:

- First `#` heading → the project title
- Body → goal, rationale, context, current state, notes — whatever the human wants to write

LLMs rebuild wrong without rationale. LLMs don't need a manifest format to read a markdown file. Keep the first, drop the second.

## Directory layout

```
<topic-wiki>/
└── output/
    ├── _index.md
    ├── projects/
    │   ├── bitcoin-quantum-risk/
    │   │   ├── WHY.md                  # goal + rationale (the only required file)
    │   │   ├── playbook.md             # main deliverable
    │   │   ├── threat-model.png        # assets colocated with the markdown that uses them
    │   │   ├── code/
    │   │   │   └── ecc-crack-demo.py
    │   │   └── data/
    │   │       └── key-exposure-analysis.csv
    │   ├── llm-wiki-roadmap/
    │   │   └── WHY.md
    │   └── .archive/                   # archived projects live here
    │       └── old-thing/
    │           └── WHY.md
    └── playbook-improving-llm-wiki-2026-04-08.md   # loose outputs still allowed
```

## Rules

1. **Folder is the project.** The directory name is the slug. No manifest file beyond `WHY.md`.
2. **`WHY.md` is required and non-empty.** Plain markdown. First `#` heading is the title. Body is the rationale.
3. **Multi-file or binary artifacts require a project folder.** Code, images, CSVs, SVGs, PDFs colocate with the markdown that references them. This is the whole reason projects exist.
4. **Single loose markdown outputs can stay flat in `output/`** for backward compatibility.
5. **No frontmatter schema on member files.** `project: <slug>` in frontmatter is optional sugar for Obsidian tag-based search; folder position is authoritative. If the two disagree, folder wins.
6. **Max nesting depth: 3 levels inside a project folder.** `projects/<slug>/code/file.py` is the deepest shape allowed.
7. **Slugs**: lowercase, hyphen-separated, max 40 characters. Semantic, not date-prefixed. Unique within the topic wiki.
8. **Goal is mandatory at creation.** Enforced by `/wiki:project new <slug> "goal"` — the goal becomes the body of `WHY.md`.

## Archive = move the folder

Archiving a project is a filesystem operation, not a metadata flip:

```
mv output/projects/<slug> output/projects/.archive/<slug>
```

The folder is preserved, all files stay put, git history continues. `/wiki:project list` shows active projects only by default; `list --archived` includes `.archive/`.

Reason: a `status: archived` frontmatter field in the old model required the manifest to exist, which required the manifest format, which required the derived-members machinery. Moving the folder is one operation and needs zero schema. The tradeoff is that links to archived projects from other files break — but broken links are something lint already catches (C4), so the existing tooling handles it.

There is no separate `retract` lifecycle state. Retraction means deleting the folder. That's a manual operation (`rm -rf`), deliberately not wrapped in a subcommand, because it's destructive and rare.

## Staleness detection

A project is **stale** when new information relevant to it has been ingested since its artifacts were last updated. This is detected by lint check C8b, not by a manifest field, and the chain runs through frontmatter that already exists:

1. Scan the project folder for member files with `sources:` in frontmatter
2. Follow each `sources:` entry to the raw source file
3. Compare the raw source's `ingested:` date to the member's `updated:` date
4. If any source is newer than the member that cites it → the project is stale

No `updated:` field on a manifest. No derived cache. Pure function over the frontmatter that already exists on every output and every raw source. Guaranteed to be accurate because it reads from the authoritative state.

## Focus / ambient project context

**Removed in the v0.2 simplification.** Earlier iterations used a `.wiki-session.json` file with a `focused_project` field, so that `/wiki:ingest`, `/wiki:research`, `/wiki:query`, etc., would implicitly scope to the focused project. This worked but added a mutable state file, focus-aware logic in every consumer command, and two subcommands (`focus`, `unfocus`) whose only job was to manage it.

The simpler model: pass `--project <slug>` explicitly when you want project scope. One extra flag per command vs. a whole session-state mechanism. If a user finds themselves typing `--project foo` on every command, that's a signal they're deep in the project and should probably `cd` into the folder directly.

## What to avoid

- **Physical lifecycle folders** (`active/`, `done/`) — breaks links on status changes. Archive via `.archive/` is the one exception because it's rare.
- **Deep nesting beyond 3 levels** — `projects/<slug>/code/file.py` is the max shape.
- **Date-prefixed slugs** — dates live in filenames inside the folder, not in the slug.
- **Mandatory projects** — loose single-markdown outputs remain allowed in `output/`.
- **File duplication for multi-membership** — use markdown links to cross-reference between projects.
- **Frontmatter-driven lifecycle** — filesystem state is simpler and can't drift.

## Migration from legacy `_project.md`

Existing wikis created under v0.1.0/v0.1.1 will have `_project.md` manifests. Lint check C8c detects these and auto-migrates:

1. Read `_project.md` frontmatter
2. Extract `goal:` (or `title:` if goal is missing)
3. Read the `## Goal`, `## Context`, `## Current State` sections if present
4. Write `WHY.md` in the same folder with the first `#` heading as the title and the extracted prose as the body
5. Delete `_project.md`
6. Report the migration in the lint output

This is the first real application of the lint-is-the-migration principle codified in `linting.md`. One-time healing; idempotent; no separate migration command needed. See `linting.md` C8c for the full rule.
</file>

<file path="claude-plugin/skills/wiki-manager/references/research-infrastructure.md">
# Research Infrastructure

Shared subsystems used by `/wiki:research` (including `--mode thesis`). Consolidated from five separate files (agent-prompts, credibility-scoring, progress-metrics, gap-scoring, session-registry) into one because all five were consumed by exactly the same pipeline and the cross-file navigation was pure noise. Thesis mode was later merged into research (Move 2), so this file now serves one command.

## Agent Prompt Templates

### Why

Well-structured prompts are the #1 predictor of agent success. These templates ensure every research agent receives the same context shape (objective, focus, constraints, return format, quality guide) regardless of which mode spawned it.

### Research Agent Template (Topic Mode)

```
You are a research agent. Your task:

**Objective**: Research "{topic}" from the {Agent Role} angle.
**Focus**: {Role-specific focus}
**Search strategy**: {Strategy from role table}
**Current wiki state**: {Brief summary from Phase 1 — what's already covered}
**Constraints**:
- Run 2-3 WebSearch queries (vary terms)
- WebFetch full content for promising results
- Skip: paywalled, SEO spam, thin, duplicate
- Target 3-5 high-quality sources

**Return format**: For each source:
- Title, URL, quality score (1-5)
- Key findings (3-5 bullets)
- Why ingest (1 sentence)

**Quality scoring**:
- 5: Peer-reviewed, landmark, primary data
- 4: Authoritative blog, official docs, well-sourced report
- 3: Decent coverage, some original insight
- 2: Thin, mostly derivative
- 1: SEO spam, no original content
```

### Research Agent Template (Question Mode)

Same as above but replace objective line:
```
**Objective**: Answer this sub-question: "{sub-question}"
**Deliverable**: Evidence that answers this specific question.
```

### Thesis Agent Template

```
You are investigating: "{thesis}"
Key variables: {variables}
Your lens: {Agent Focus} — {Thesis Lens description}

For each source, evaluate:
- Relevance: direct | indirect | tangential (SKIP tangential)
- Evidence strength: meta-analysis > RCT > cohort > case > opinion > anecdotal
- Direction: supports | opposes | nuances
- Key finding: 1-2 sentences
- Quality: 1-5

Return ranked by (relevance × evidence strength), strongest first.
```

### Retardmax Variants

- All templates: increase to 4-5 searches
- Lower quality threshold: accept 2+ (not 3+)
- Add: "Follow interesting citations and references from pages you find"
- Rabbit Hole agents: "Start with '{topic}', follow the most compelling result, then search for what THAT references. Go deep."

---

## Credibility Scoring (Phase 2b)

### Why

Independent assessment of source credibility before ingestion. Prevents the "fox guarding the henhouse" problem where agents self-rate their own source quality. Credibility scores carry forward into article `confidence:` frontmatter tags during compilation.

### Scoring Rubric

| Signal | Points | How to Detect |
|--------|--------|---------------|
| Peer-reviewed | +2 | DOI present, journal/conference name, PubMed ID, arxiv with venue |
| Recent (<=3 years) | +1 | Publication date check |
| Older (>3 years) | 0 | — |
| Very old (>10 years) | -1 | Unless it's a foundational/landmark paper |
| Known author/institution | +1 | Recognized university, major lab, cited expert |
| Unknown author | 0 | — |
| Potential bias detected | -1 | Industry-sponsored without disclosure, activist org, predatory journal |
| Vendor primary source | -1 | First-party vendor docs or blog about own product (authoritative for facts, but inherent promotional framing) |
| Corroborated by other agents | +1 per agent (max +2) | Multiple agents found similar claims from independent sources |

**Non-stacking rule**: Bias signals do not stack. If a source triggers both "potential bias" and "vendor primary source," apply only the more specific one (-1 total, not -2). These are refinements of the same concern (promotional framing), not independent dimensions.

### Credibility Tiers

| Tier | Score Range | Action | Confidence Tag |
|------|------------|--------|---------------|
| High | 4-6 | Ingest | confidence: high |
| Medium | 2-3 | Ingest | confidence: medium |
| Low | 0-1 | Ingest only if unique angle | confidence: low |
| Reject | <0 | Skip | — |

### Bias Detection Signals

- Industry whitepaper with no independent validation
- Press release disguised as news article
- Predatory journal (check Beall's List indicators: rapid acceptance, broad scope, aggressive solicitation)
- Affiliate/sponsored content without disclosure
- Single-perspective advocacy org
- First-party vendor documentation or engineering blog about own product (authoritative for facts, but inherent promotional framing — e.g., Anthropic writing about Claude Code, LangChain surveying their own users, Factory.ai benchmarking their own compression algorithm)

### Retardmax Mode

Lower rejection threshold — accept Medium and above. Still score everything; scores carry forward into article confidence tags.

---

## Progress Scoring (0-100)

### Why

Quantify research quality per round to enable principled termination and low-yield detection. Without this, multi-round research either runs until the timer expires (wasting tokens on diminishing returns) or stops too early (missing important gaps). The score is the decision signal.

### Formula

| Component | Calculation | Max Points |
|-----------|-------------|-----------|
| Sources ingested | count x 3 | 30 |
| Articles created/updated | count x 5 | 30 |
| Cross-references added | count x 2 | max(20, existing_articles x 2) — scales with wiki maturity |
| Average credibility score | avg x 4 | 20 |

**Scaling note**: The cross-reference cap starts at 20 for new wikis and grows as the wiki matures. A wiki with 10 existing articles has a cap of 20; one with 15 articles has a cap of 30. This prevents the component from saturating on Round 1 when the wiki is small, while still rewarding dense cross-linking in mature wikis.

### Interpretation

- 0-40: Minimal yield — consider changing strategy
- 41-70: Moderate — research is productive, continue
- 71-90: Strong — good coverage being built
- 91-100: Comprehensive — near-complete coverage

### Termination Decision Tree

```
progress_score >= 80?
  |-- YES -> Any high-impact gaps remaining?
  |           |-- YES -> Continue (but note quality is high)
  |           +-- NO  -> Cross-ref density > 60%?
  |                      |-- YES -> RECOMMEND EARLY COMPLETION
  |                      +-- NO  -> One more round focusing on connections
  +-- NO  -> progress_score < 40?
             |-- YES -> LOW YIELD WARNING
             |          -> Suggest: different terms, --deep, narrower topic
             +-- NO  -> Continue normally
```

### Low-Yield Response Options

When progress_score < 40 for two consecutive rounds:
1. Switch to `--deep` mode if not already
2. Try different search angle framing
3. Narrow the topic to a more specific subtopic
4. Report early completion: "Research appears exhausted for this topic"

### Trajectory-Based Triggers

In addition to per-round thresholds, monitor the round-over-round trend:

**Declining trajectory warning**: If 3 consecutive rounds show declining scores totaling 30+ points of cumulative drop (e.g., 98→95→68→58 = -40 total), warn:
> "Research yield is declining across rounds (trajectory: {scores}). Consider: narrowing topic focus, switching to --deep mode, or completing early if core gaps are filled."

**Plateau detection**: If 2 consecutive rounds score within 5 points of each other AND no new high-impact gaps are identified, recommend early completion:
> "Research has plateaued at {score}. No new high-impact gaps found. Early completion recommended."

**Stalled detection**: If any single round scores <20, immediately flag:
> "Round yielded near-zero value. Stop and reassess: is the topic too narrow, the search terms wrong, or the knowledge base already comprehensive?"

---

## Gap Scoring & Reflection

### Why

Between multi-round research rounds, reflect holistically on accumulated knowledge and score gaps for the next round. **Key insight from testing**: plan reflection's primary value is discovering cross-topic connections between rounds — NOT changing the research direction. Testing against a real 4-round research wiki showed the research path was already well-chosen (reflection confirmed every round's direction). But it found 5 undrawn cross-references that exist in the content but were never linked. This is the 34% improvement the literature predicts.

### Gap Scoring Formula

Each gap is scored on three dimensions (1-5 each):

| Dimension | 5 (highest) | 3 (moderate) | 1 (lowest) |
|-----------|-------------|--------------|------------|
| **Impact** | Filling this gap fundamentally changes understanding | Adds useful context | Nice-to-know but not essential |
| **Feasibility** | Likely findable with web search | May exist but hard to find | Probably requires primary research |
| **Specificity** | Well-defined, searchable question | Somewhat vague | Too broad to target effectively |

**Composite score** = Impact x Feasibility x Specificity (range: 1-125)

**Selection**: Pick top 3 gaps by composite score for the next round.

### Reflection Protocol

Between rounds, the orchestrating agent should (in priority order):

1. **Draw connections** between this round's findings and ALL prior rounds (not just the previous one) — this is the highest-value activity
2. **Update cross-references** — add See Also links between articles that share concepts across rounds
3. **Re-evaluate earlier gaps** — some gaps from round 1 may now be filled or irrelevant
4. **Score remaining gaps** using the formula above
5. **Adjust research direction** — only if findings clearly indicate a shift (rare in practice)
6. **Note reflection in session registry** — add `reflection_notes` to the round entry

### Example Reflection Output

```
## Round 2 Reflection

### Cross-Topic Connections Discovered
- Round 1 finding about X connects to Round 2 finding about Y
- This suggests a new gap: "How does X influence Y?"

### Gap Re-Evaluation
- Gap "A" from Round 1: now filled by Round 2 sources (remove)
- Gap "B" from Round 1: still unfilled, upgraded to high-impact (keep)
- New gap "C": emerged from Round 2 findings (add)

### Scored Gaps for Round 3
1. Gap B: Impact 5 x Feasibility 4 x Specificity 5 = 100
2. Gap C: Impact 4 x Feasibility 5 x Specificity 4 = 80
3. Gap D: Impact 3 x Feasibility 3 x Specificity 4 = 36

### Direction Shift
Research initially focused on X but findings consistently point to Y as the more important subtopic. Round 3 should emphasize Y.
```

---

## Session Registry

### Why

Persistent state for multi-round research and thesis sessions, enabling crash recovery and round-to-round continuity. Without this, a crashed `--min-time` session loses all round state and the user has to start over. The file is ephemeral (never committed to git, never indexed), cheap to lose (worst case: user is asked "continue or start fresh?"), but valuable to have.

### Research Session Schema (.research-session.json)

```json
{
  "session_id": "2026-04-06-143022",
  "topic": "research topic",
  "start_time": "2026-04-06T14:30:22Z",
  "min_time_budget": "2h",
  "current_round": 2,
  "rounds_completed": [
    {
      "round": 1,
      "start_time": "2026-04-06T14:30:22Z",
      "end_time": "2026-04-06T15:02:45Z",
      "sources_ingested": 5,
      "articles_compiled": 3,
      "gaps": ["gap1 description", "gap2 description"],
      "progress_score": 65,
      "reflection_notes": "Initial broad coverage complete. Gap1 is highest priority."
    }
  ],
  "cumulative_sources": 5,
  "cumulative_articles": 3,
  "status": "in_progress"
}
```

### Thesis Session Schema (.thesis-session.json)

```json
{
  "session_id": "2026-04-06-143022",
  "thesis": "claim statement",
  "current_round": 2,
  "rounds_completed": [
    {
      "round": 1,
      "evidence_for": 4,
      "evidence_against": 2,
      "verdict_direction": "partially-supported",
      "next_round_focus": "opposing"
    }
  ],
  "status": "in_progress"
}
```

### Lifecycle

| Event | Action |
|-------|--------|
| --min-time research starts | Create .research-session.json |
| Round N completes | Update rounds_completed, cumulative counts, status |
| Research completes normally | Delete file (data persists in log.md) |
| Session interrupted | File persists with status: "in_progress" |
| Next invocation detects file | Ask: continue or start fresh? |
| File > 7 days old | Structural Guardian warns about stale session |

### Resume Protocol

1. Detect `.research-session.json` or `.thesis-session.json` in wiki root
2. Read file, extract last completed round
3. Ask user: "Found interrupted session (Round N, M sources). Continue or start fresh?"
4. If continue: use round N's gaps/reflection as starting point for round N+1
5. If fresh: delete file, proceed normally

### Notes

- Session files are ephemeral — never commit to git
- Never include in index counts or structural health checks
- One session per wiki at a time (new session overwrites old)

---

## Research Plan Schema

### Why

The `--plan` flag decomposes a research topic into 3-5 independent paths that execute in parallel. The plan is stored in the session registry so it persists across crashes and can be resumed path-by-path. The plan is ephemeral — it lives only in `.research-session.json` and is deleted on completion.

The architectural insight: parallel ingest is safe (each path writes unique raw files with path-prefixed slugs), but parallel compilation is not (multiple agents updating the same `_index.md` and creating overlapping articles). So the pipeline splits: search + ingest run in parallel across paths, then a single sequential compilation pass runs after all paths complete. This gives the compiler full visibility across all paths for better cross-referencing.

### Schema Extension

When `mode: "plan"` is set in `.research-session.json`, the following fields are added:

| Field | Type | Purpose |
|-------|------|---------|
| `mode` | `"plan"` | Distinguishes plan-mode sessions from single-path (`"single"`) |
| `paths` | array | Research paths with scope and execution status |
| `paths[].name` | string | Human-readable path name |
| `paths[].focus` | string | One-line description of what this path investigates |
| `paths[].search_angles` | string[] | 2-3 specific search strategies for this path |
| `paths[].status` | enum | `pending`, `in_progress`, `completed`, `failed` |
| `paths[].sources_ingested` | number | Sources ingested by this path (updated on completion) |
| `paths[].agent_mode` | string | `standard`, `deep`, or `retardmax` (inherited from session flags) |

### Example

```json
{
  "session_id": "2026-04-16-143022",
  "topic": "quantum computing threats to Bitcoin",
  "mode": "plan",
  "start_time": "2026-04-16T14:30:22Z",
  "paths": [
    {
      "name": "Cryptographic foundations",
      "focus": "Shor's algorithm vs ECDLP, key sizes, quantum gate counts",
      "search_angles": ["shor algorithm elliptic curve", "quantum gate count ECDLP", "NIST post-quantum standards"],
      "status": "completed",
      "sources_ingested": 4,
      "agent_mode": "standard"
    },
    {
      "name": "Hardware timeline",
      "focus": "IBM/Google roadmaps, logical qubit milestones, error correction overhead",
      "search_angles": ["IBM quantum roadmap 2026", "logical qubit error correction overhead", "Google Willow scaling"],
      "status": "completed",
      "sources_ingested": 3,
      "agent_mode": "standard"
    },
    {
      "name": "Migration proposals",
      "focus": "BIP proposals, hash-based signatures, precommitment schemes",
      "search_angles": ["bitcoin post-quantum BIP", "hash-based signature bitcoin", "PQC precommitment soft fork"],
      "status": "in_progress",
      "sources_ingested": 0,
      "agent_mode": "standard"
    }
  ],
  "current_round": 1,
  "rounds_completed": [],
  "cumulative_sources": 7,
  "cumulative_articles": 0,
  "status": "in_progress"
}
```

### Resume Protocol (plan mode)

On resume, check `paths[].status`:

- **All `completed`** → skip to compilation (all sources are ingested, just need to compile)
- **Some `pending`** → re-launch only pending paths (completed paths are not repeated)
- **Some `in_progress`** → treat as `pending` (agent died mid-execution; raw files from partial execution are fine — deduplication handles any overlap)
- **Some `failed`** → ask user: "Path '<name>' failed. Retry or skip?"

### File Ownership

Each path prefixes its raw file slugs with the path index to prevent filename collisions between parallel agents:

```
raw/<type>/YYYY-MM-DD-p<N>-<source-slug>.md
```

Where `N` is the 1-indexed path number. Example: `raw/articles/2026-04-16-p2-ibm-quantum-roadmap.md` is a source from path 2.

Index updates are skipped during parallel ingest. The Derived Index Protocol (`indexing.md`) rebuilds them on the next read. This is safe because indexes are derived caches, not source of truth.

### Interaction with Other Flags

| Flag | Behavior with `--plan` |
|------|----------------------|
| `--deep` | Each path-agent launches 8 sub-agents instead of 5 |
| `--retardmax` | Each path-agent launches 10 sub-agents, lower quality threshold |
| `--sources <N>` | Target N sources per path (not total) |
| `--min-time` | Round 1 executes the full plan; subsequent rounds generate new plans targeting remaining gaps |
| `--mode thesis` | Plan decomposes the thesis into evidence paths (supporting, opposing, mechanistic, etc.) |
| `--project <slug>` | All paths tag outputs with the same project |
| `--new-topic` | Creates the topic wiki first, then generates and executes the plan |
</file>

<file path="claude-plugin/skills/wiki-manager/references/wiki-structure.md">
# Wiki Directory Structure

> **Configurable hub path**: The hub location is read from `~/.config/llm-wiki/config.json` (`resolved_path` field). If no config exists, `~/wiki/` is the fallback. Throughout this document, `HUB/` means "the resolved hub path". See [hub-resolution.md](hub-resolution.md) for the full resolution protocol (tilde expansion, space handling, iCloud paths).

## Hub (HUB/)

The hub is lightweight — it has NO content directories. It only tracks topic wikis.

```
HUB/                               # resolved from ~/.config/llm-wiki/config.json
├── wikis.json                     # Registry of all topic wikis
├── _index.md                      # Lists topic wikis with stats
├── log.md                         # Global activity log
└── topics/                        # Each topic is a full wiki
    ├── dementia/
    ├── quantum-computing/
    └── ...
```

## Topic Sub-Wiki (HUB/topics/<name>/)

All content lives here. Each topic wiki has the full structure:

```
HUB/topics/<name>/
├── .obsidian/                     # Obsidian vault config
├── _index.md                      # Master index: stats, quick nav, recent changes
├── config.md                      # Title, scope, conventions
├── log.md                         # Topic-level activity log
├── inbox/                         # Drop zone for this topic
│   └── .processed/
├── raw/                           # Immutable source material
│   ├── _index.md
│   ├── articles/
│   │   ├── _index.md
│   │   └── *.md
│   ├── papers/
│   │   ├── _index.md
│   │   └── *.md
│   ├── repos/
│   │   ├── _index.md
│   │   └── *.md
│   ├── notes/
│   │   ├── _index.md
│   │   └── *.md
│   └── data/
│       ├── _index.md
│       └── *.md
├── wiki/                          # Compiled articles (LLM-maintained)
│   ├── _index.md
│   ├── concepts/
│   │   ├── _index.md
│   │   └── *.md
│   ├── topics/
│   │   ├── _index.md
│   │   └── *.md
│   ├── references/
│   │   ├── _index.md
│   │   └── *.md
│   └── theses/                    # Thesis investigations
│       ├── _index.md
│       └── *.md
└── output/                        # Generated artifacts
    ├── _index.md
    ├── projects/                  # Project folders (see projects.md)
    │   ├── <slug>/
    │   │   ├── WHY.md             # Required: goal + rationale in plain markdown
    │   │   ├── *.md               # Markdown deliverables
    │   │   ├── *.png, *.svg       # Colocated images/diagrams
    │   │   ├── code/              # Optional — prototype scripts
    │   │   └── data/              # Optional — CSVs, JSON exports
    │   └── .archive/              # Archived projects (moved here by /wiki:project archive)
    │       └── <slug>/
    │           └── WHY.md
    └── *.md                       # Loose outputs (backward compatible)
```

See [projects.md](projects.md) for the full projects architecture (lifecycle, multi-membership, explicit `--project <slug>` scoping).

## Local Wiki (--local flag)

Same structure as above but rooted at `<project>/.wiki/` without `wikis.json` or `topics/`.

## Wiki Resolution Order

When a command runs, first resolve the hub path (HUB) from `~/.config/llm-wiki/config.json` (see `hub-resolution.md`). Then resolve which wiki to use:

1. `--local` flag present → `<cwd>/.wiki/`
2. `--wiki <name>` flag present → look up name in `HUB/wikis.json`
3. Current directory has `.wiki/` → use it
4. Otherwise → HUB

## wikis.json Format

```json
{
  "default": "<HUB>",
  "wikis": {
    "hub": { "path": "<HUB>", "description": "Global knowledge base" },
    "<topic>": { "path": "<HUB>/topics/<topic>", "description": "..." }
  },
  "local_wikis": [
    { "path": "/absolute/path/.wiki", "description": "..." }
  ]
}
```

## _index.md Format

Every directory has an `_index.md`. This is the agent's primary navigation aid.

```markdown
# [Directory Name] Index

> [One-line description of what this directory contains]

Last updated: YYYY-MM-DD

## Contents

| File | Summary | Tags | Updated |
|------|---------|------|---------|
| [filename.md](filename.md) | One-sentence summary | tag1, tag2 | YYYY-MM-DD |

## Categories

- **category-name**: file1.md, file2.md

## Recent Changes

- YYYY-MM-DD: Description of change
```

### Master _index.md (root level)

Additionally includes:

```markdown
## Statistics

- Sources: N raw documents
- Articles: N compiled wiki articles
- Outputs: N generated artifacts
- Last compiled: YYYY-MM-DD
- Last lint: YYYY-MM-DD

## Quick Navigation

- [All Sources](raw/_index.md)
- [Concepts](wiki/concepts/_index.md)
- [Topics](wiki/topics/_index.md)
- [References](wiki/references/_index.md)
- [Outputs](output/_index.md)
```

## log.md Format

Append-only chronological activity log. Every wiki operation appends an entry. Never edit or delete existing entries. **Always open for append, never read-modify-write** — this makes concurrent writes safe (lines from multiple sessions interleave without corruption). Format is grep-friendly:

```markdown
# Wiki Activity Log

## [2026-04-04] init | Wiki initialized
## [2026-04-04] ingest | Attention Is All You Need (raw/papers/2026-04-04-attention-is-all-you-need.md)
## [2026-04-04] ingest | Illustrated Transformer (raw/articles/2026-04-04-illustrated-transformer.md)
## [2026-04-04] compile | 2 sources → 3 new articles, 1 updated (transformer-architecture, self-attention, sequence-modeling + updated attention-mechanisms)
## [2026-04-04] query | "How does self-attention work?" → answered from 2 articles
## [2026-04-05] lint | 12 checks, 0 critical, 2 warnings, 3 suggestions, 1 auto-fixed
## [2026-04-05] research | "transformer variants" → 5 sources ingested, 4 articles compiled
## [2026-04-05] output | summary on transformer-architecture → output/summary-transformer-architecture-2026-04-05.md
```

Each entry: `## [YYYY-MM-DD] operation | Description`

Operations: `init`, `ingest`, `compile`, `query`, `lint`, `research`, `output`, `refresh`

Useful for: `grep "^## \[" log.md | tail -10` to see recent activity.

## config.md Format

```markdown
---
title: "Wiki Title"
description: "What this wiki is about"
created: YYYY-MM-DD
freshness_threshold: 70
---

# Wiki Configuration

## Scope

[What topics this wiki covers]

## Conventions

[Any wiki-specific conventions beyond defaults]
```

## Source File Format (raw/)

```markdown
---
title: "Title"
source: "URL or filepath or MANUAL"
type: articles|papers|repos|notes|data
ingested: YYYY-MM-DD
tags: [tag1, tag2]
summary: "2-3 sentence summary"
---

# Title

[Full content]
```

## Wiki Article Format (wiki/)

```markdown
---
title: "Article Title"
category: concept|topic|reference
sources: [raw/type/file1.md, raw/type/file2.md]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
aliases: [alternate names for Obsidian discovery]
confidence: high|medium|low
volatility: hot|warm|cold
verified: YYYY-MM-DD
summary: "2-3 sentence summary for index"
---

# Article Title

> [One-paragraph abstract]

## [Sections as appropriate]

[Synthesized content — explain, contextualize, connect. NOT copy-paste.]

When referencing another wiki article inline, use dual-link format:
[[article-slug|Display Name]] ([Display Name](../category/article-slug.md))

This ensures both Obsidian (reads [[wikilink]]) and the agent (follows relative path) can navigate.

## See Also

- [[related-slug|Related Article]] ([Related Article](../category/related-slug.md)) — relationship note

## Sources

- [Source Title](../../raw/type/file.md) — what this source contributed
```

## Volatility Classification

Wiki articles carry a `volatility` field that controls how quickly their freshness score decays. The `verified` field records when a human last confirmed the article's conclusions are still accurate.

| Tier | Decay rate | When to use | Examples |
|------|-----------|-------------|----------|
| `hot` | Fast | Fast-moving sources: product specs, pricing, current events, competitive landscape | NVIDIA Spark specs, election results, API changelog |
| `warm` | Moderate | Quarterly-to-annual cadence: best practices, framework comparisons, market analysis | Testing patterns, CLI UX patterns, market positioning |
| `cold` | Slow | Foundational concepts, historical events, mathematical proofs, stable reference | TCP/IP fundamentals, Lindy Effect, cryptographic algorithms |

Default is `warm`. The compilation agent sets volatility based on source characteristics: news/trends sources suggest `hot`, foundational/historical sources suggest `cold`. Authors can override.

### Freshness Score (0-100)

Each article's freshness is a composite of four dimensions, each contributing 0-25 points:

| Dimension | What it measures | Computed from |
|-----------|-----------------|---------------|
| **Source freshness** | How old are the raw sources this article was compiled from? | Average days since `ingested:` across all `sources:` entries |
| **Verification recency** | When did a human last confirm accuracy? | Days since `verified:` |
| **Compilation recency** | When was this article last recompiled? | Days since `updated:` |
| **Source chain integrity** | Do all referenced sources still exist? | % of `sources:` entries that resolve to actual files |

Each dimension's decay curve is scaled by the article's `volatility` tier — a hot article's source freshness decays faster than a cold one's. The Lindy Effect applies: cold content that has survived without needing updates is more durable, not less.

The freshness threshold is set per wiki in `config.md` (default: 70). Articles scoring below the threshold are flagged by lint. There are no hardcoded day cutoffs — the composite score naturally flags the right articles at the right time based on their volatility and the actual state of their sources.

## Dual-Link Convention

All cross-references between wiki articles use BOTH link formats on the same line:

```
[[target-slug|Display Text]] ([Display Text](../category/target-slug.md))
```

- **Obsidian** reads the `[[wikilink]]` for its graph view, backlinks panel, and navigation
- **The agent** follows the standard markdown `(relative/path.md)` link
- Both coexist on one line so neither system misses the connection

For inline mentions in article body text, use the same pattern:
```
The [[transformer-architecture|Transformer]] ([Transformer](../concepts/transformer-architecture.md)) uses self-attention...
```

## Obsidian Compatibility

The wiki is designed to be opened as an Obsidian vault. On `/wiki init`, a `.obsidian/` config directory is created with minimal settings. Key compatibility notes:

- YAML frontmatter `tags` field is read natively by Obsidian
- `aliases` in frontmatter lets Obsidian find articles by alternate names
- `_index.md` files appear as regular notes in Obsidian (this is fine)
- The `inbox/` folder works as a natural Obsidian inbox
- Graph view shows connections via `[[wikilinks]]`

## Output Artifact Format (output/)

```markdown
---
title: "Output Title"
type: summary|report|study-guide|slides|timeline|glossary|comparison
sources: [wiki/category/article.md, ...]
generated: YYYY-MM-DD
---

[Content in the appropriate format for the type]
```

## File Naming

- **Raw sources**: `YYYY-MM-DD-descriptive-slug.md` (date prefix for chronological order)
- **Wiki articles**: `descriptive-slug.md` (no date — living documents)
- **Output artifacts**: `{type}-{topic-slug}-{YYYY-MM-DD}.md`
- All filenames: lowercase, hyphens for spaces, no special characters, max 60 chars

## Tag Convention

Tags are lowercase, hyphenated. Prefer specific over general:
- Good: `transformer-architecture`, `self-attention`, `natural-language-processing`
- Bad: `ai`, `ml`, `tech`

Normalize across the wiki — no near-duplicates like `ml` vs `machine-learning`.
</file>

<file path="claude-plugin/skills/wiki-manager/SKILL.md">
---
name: wiki-manager
description: >
  LLM-compiled knowledge base manager. Activates when user works with wiki
  directories, mentions knowledge base management, asks knowledge questions
  in a project with a wiki, wants to ingest/compile/query/lint knowledge,
  or uses /wiki commands. Also activates when user says "wiki", "knowledge base",
  "ingest", "compile wiki", "add to wiki", "search wiki", "librarian",
  "scan quality", "article quality", "content review", or asks a factual
  question in a directory containing .wiki/ or when ~/wiki/ exists or the
  configured hub path exists (check ~/.config/llm-wiki/config.json for hub_path).
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
  - WebSearch
---

# LLM Wiki Manager

You manage an LLM-compiled knowledge base. Source documents are ingested into `raw/`, then incrementally compiled into a wiki of interconnected markdown articles. Claude Code is both the compiler and the query engine — no Obsidian, no external tools.

## Hub Path

The hub defaults to `~/wiki/`. If `~/wiki/` exists and is initialized (has `_index.md`), it is used directly — no config file needed. This is the simplest, most reliable path.

To use a different location (e.g., iCloud Drive) when `~/wiki/` is not set up, create `~/.config/llm-wiki/config.json`:

```json
{ "hub_path": "~/Library/Mobile Documents/com~apple~CloudDocs/wiki" }
```

**Resolution**: At the start of every operation, resolve **HUB** by following the protocol in [references/hub-resolution.md](references/hub-resolution.md) — check `~/wiki/` first, then fall back to config. This handles tilde expansion, paths with spaces, and iCloud directory names correctly. All references to `~/wiki/` below mean HUB.

## Wiki Location

**Topic sub-wikis are the default.** HUB is a hub — content lives in `HUB/topics/<name>/`. Each topic gets isolated indexes, sources, and articles. This keeps queries focused and prevents unrelated topics from polluting each other's search space.

Resolution order:

1. `--local` flag → `.wiki/` in current project
2. `--wiki <name>` flag → named wiki from `HUB/wikis.json`
3. Current directory has `.wiki/` → use it
4. Otherwise → HUB (the hub)

When a command targets the hub and the hub has no content, suggest creating a topic sub-wiki instead.

See [references/wiki-structure.md](references/wiki-structure.md) for the complete directory layout and all file format conventions.

## Core Principles

1. **Indexes are a derived cache.** The `.md` files and their YAML frontmatter are the source of truth. `_index.md` files are a cached view rebuilt on read when stale. Always read indexes first for navigation — but before trusting one, stale-check it (file count vs row count). See [references/indexing.md](references/indexing.md) for the Derived Index Protocol.

2. **Raw is immutable.** Once ingested into `raw/`, sources are never modified. They are a record of what was ingested and when. All synthesis happens in `wiki/`.

3. **Articles are synthesized, not copied.** A wiki article draws from multiple sources, contextualizes, and connects to other concepts. Think textbook, not clipboard.

4. **Dual-linking for Obsidian + Claude.** Cross-references use both `[[wikilink]]` (for Obsidian graph view) and standard markdown `[text](path)` (for Claude navigation) on the same line: `[[slug|Name]] ([Name](../category/slug.md))`. Bidirectional when it makes sense.

5. **Frontmatter is structured data.** Every `.md` file has YAML frontmatter with title, summary, tags, dates. This makes the wiki searchable without full-text scans.

6. **Incremental over wholesale.** Compilation processes only new sources by default. Full recompilation is expensive and explicit (`--full`).

7. **Honest gaps.** When answering questions, if the wiki doesn't have the answer, say so. Never hallucinate. Suggest what to ingest to fill the gap.

8. **Multi-wiki awareness.** When querying, answer from the primary wiki first. Then peek at sibling wiki indexes (via `HUB/wikis.json`) for relevant overlap. Flag connections but never merge content across wikis.

9. **Chunk large writes.** Never create files longer than ~200 lines in a single Write call — the API stream idles during large generations, causing timeout errors. Write the skeleton (frontmatter + headers + first section) first, then use sequential Edit calls to append remaining sections. For plans, articles, and raw notes: write one section per tool call.

## Ambient Behavior

When this skill activates outside of an explicit `/wiki:*` command:

1. Resolve the hub path (see Hub Path section above), then check if `HUB/_index.md` or `.wiki/_index.md` exists
2. Read the master `_index.md` to assess if the wiki might cover the user's question
3. If relevant content exists → read the relevant articles and answer with citations
4. If no relevant content → answer normally, optionally suggest: "This could be added to your wiki with `/wiki:ingest`"
5. When peeking at sibling wikis, only read their `_index.md` — do not read full articles unless the user asks

## Workflows

### Ingestion
See [references/ingestion.md](references/ingestion.md).
Flow: Source (URL/file/text/tweet/inbox) → fetch/read → extract metadata → write to `raw/{type}/` → update indexes → suggest compile if many uncompiled.

### Compilation
See [references/compilation.md](references/compilation.md).
Flow: Survey uncompiled sources → plan articles → classify (concept/topic/reference) → write/update articles with cross-references → update all indexes.

### Query
Flow: Read `_index.md` → identify relevant articles by summary/tag → read articles → follow See Also links → Grep for additional matches → synthesize answer with citations → note gaps → peek sibling wikis. Supports `--resume` to reload context after a session break — reads session files, recent log entries, wiki stats, and last-updated articles to produce a "where you left off" briefing.

### Linting
See [references/linting.md](references/linting.md).
Flow: Check structure → indexes → links → content → coverage → report → optionally auto-fix.

### Search
Flow: Scan indexes for summary/tag matches → Grep full-text → rank results → present.

### Output
Flow: Gather relevant articles → generate artifact (summary/report/slides/etc) → save to `output/` → update indexes.

### Lessons Learned (ll)
Flow: Scan session for error→fix patterns, corrections, discoveries → extract structured lessons → write to `raw/notes/` with `type: lessons-learned` → optionally update relevant articles → optionally suggest CLAUDE.md rules.

## Links: File Paths and URLs

Terminal links break when they wrap to a second line. Rules for all wiki operations:

1. **Full absolute paths** — expand `~`, HUB, and all relative segments. Relative paths are not clickable.
2. **Markdown link syntax for URLs** — use `[short text](url)`, never bare long URLs that wrap and break.
3. **No indentation before links** — indentation eats terminal width. Put links flush-left on their own line.
4. **One link per line** — don't embed a long path mid-sentence. Break it out:
   ```
   Saved to:
   /Users/name/wiki/topics/my-topic/output/report-2026-04-08.md
   ```

See `references/research-infrastructure.md` § Agent Prompt Templates for examples. Applies to ingest, compile, research, output, assess.

## Activity Log

Every wiki operation appends to `log.md` in the wiki root. Format: `## [YYYY-MM-DD] operation | Description`. See [references/wiki-structure.md](references/wiki-structure.md) for full format. Never edit or delete existing log entries — append only.

## Confidence Scoring

Wiki articles include a `confidence` field in frontmatter: `high`, `medium`, or `low`.

- **high**: Multiple peer-reviewed sources agree, well-established knowledge
- **medium**: Single source, or sources partially agree, or recent findings not yet replicated
- **low**: Anecdotal, single non-peer-reviewed source, or sources disagree

When answering queries, note confidence levels. When linting, flag `low` confidence articles for review.

## Compilation Nudge

Track uncompiled sources by comparing `raw/_index.md` ingestion dates against the last compile date in `_index.md`. If 5+ uncompiled sources exist after an ingestion, suggest: "You have N uncompiled sources. Run `/wiki:compile` to integrate them."

## Structural Guardian

Automatically run a quick structural check when any of these triggers occur:

### Triggers
- **After any write operation** (ingest, compile, research, output) — verify what was just written
- **When the skill activates** and the wiki hasn't been linted in 7+ days (check "Last lint" in `_index.md`)
- **When content is found in the wrong place** — articles in the global hub instead of a topic sub-wiki
- **When a user mentions wiki problems** — "wiki is broken", "empty", "missing", "wrong"
- **When no wiki exists** (first-run) — switch to guided onboarding flow instead of showing a command list. Walk the user through topic selection → init → first action suggestion. See `commands/wiki.md` § "If no wiki exists".

### Quick Structure Check (lightweight, runs inline — not a full lint)

1. **Hub integrity**: The hub (HUB) should ONLY contain `wikis.json`, `_index.md`, `log.md`, and `topics/`. If `raw/`, `wiki/`, `output/`, `inbox/`, or `config.md` exist at the hub level → **warn, do not delete**. These may hold user data from an older wiki layout. Suggest `/wiki:lint --fix`, which will move contents to the appropriate topic wiki or quarantine to `inbox/.unknown/` per C11/C12 in `references/linting.md`.

2. **Index freshness**: For the active topic wiki, compare actual file count in `wiki/concepts/`, `wiki/topics/`, `wiki/references/` against the rows in their `_index.md`. If mismatched → auto-fix by adding missing entries or removing dead ones.

3. **Orphan detection**: Check if any `.md` files exist in wiki directories but are not listed in any `_index.md`. If found → add them to the index.

4. **Missing directories**: Verify all expected subdirectories exist in the topic wiki (`raw/articles/`, `raw/papers/`, etc.). If missing → create them with empty `_index.md`.

5. **wikis.json sync**: Check that all topic sub-wikis under `HUB/topics/` are registered in `wikis.json`. If a directory exists but isn't registered → add it. If registered but directory is missing → remove the entry.

6. **Log existence**: Verify `log.md` exists in the active wiki and at the hub. If missing → create it.

### Behavior

- **Silent when clean** — don't report anything if everything checks out
- **Auto-fix trivial issues** — missing indexes, unregistered wikis, orphan files. Just fix and note in log.
- **Warn on structural problems** — content in wrong place, missing directories, stale indexes. Tell the user what's wrong and suggest `/wiki:lint --fix`.
- **Never block the user's request** — run the check, fix what you can, report issues, then continue with what the user actually asked for.

## Concurrency

Multiple Claude Code sessions can safely read and write to the same wiki simultaneously. No locks are needed.

- **Indexes** are derived from the actual files on disk. If two sessions write articles at the same time, the next read rebuilds the index from whatever files exist. Both rebuilds converge to the same correct result.
- **log.md** is append-only with small atomic writes. Concurrent appends are safe.
- **Article/source files** are written independently. Two sessions creating different files never conflict. Two sessions editing the same file is unlikely and handled by last-write-wins (acceptable for a wiki — the content is always rebuildable from raw sources).

See [references/indexing.md](references/indexing.md) for the Derived Index Protocol.

## Session Management

### Research Session Registry

When a `--min-time` research or thesis session is active, the wiki root contains a `.research-session.json` or `.thesis-session.json` file.

**Structural Guardian behavior**:
- If a session file exists with `status: "in_progress"` and `start_time` > 7 days ago → warn: "Stale research session found. Clean up with `/wiki:research` or delete manually."
- Session files are ephemeral — never included in structural health checks or index counts
- Session files should NOT be committed to git
</file>

</files>
