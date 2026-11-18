---
type: Concept
title: Pydantic AI Harness file system
description: The Harness FileSystem capability — eight file tools plus two ripgrep-backed ones, contained by one root_dir and three glob lists, with fallback search stacks, approval events that can cancel a change, content-hash concurrency, and a guardrail that is not isolation.
tags: [pydantic-ai, agents, harness, filesystem]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:19:19Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-filesystem-docs
    resource: ../raw/harness/filesystem/index.md
    scope: ../raw/harness/filesystem/
    kind: documentation
    revision: sha256:adf7e011d23b118e46e52cbdabce73d2b79a2cd1762a31c2e3d5cfce27a1dfdb
    title: "FileSystem"
---

`FileSystem` is the [Harness](pydantic-ai-harness.md) capability that gives an agent a fixed set of file tools, all scoped to a single `root_dir` in the run's [workspace](pydantic-ai-workspaces-and-sandboxes.md), with every path resolved — symlinks included — and containment-checked before any I/O[^pydantic-filesystem-docs] It centralises the guards that are otherwise re-implemented per tool: path traversal, clobbering `.git`, leaking `.env`. It is the file half of [Coder](pydantic-ai-harness-coder.md), and the half [Shell](pydantic-ai-harness-shell.md) explicitly does not share a boundary with. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## The ten tools

Eight are registered by default, and two more are ripgrep-backed and opt-in by name in `tools`[^pydantic-filesystem-docs]:

| Tool | Job |
| --- | --- |
| `read_file` | Text with line numbers and a content hash; an image (PNG/JPEG/GIF/WebP) or PDF up to 5 MB is returned as the file itself; other binaries are described by size, media type and their first 64 bytes in hex; `offset`/`limit` paging |
| `write_file` | Create or overwrite, with optional `expected_hash` against a stale write |
| `edit_file` | Exact-string replacement — one `old_text`/`new_text` pair or a `replacements` batch applied in order, each matching exactly once, checked in memory and written only if every replacement matches |
| `list_directory` | Entries with type indicators and sizes |
| `search_files` | Regex over file contents, optionally narrowed by an `include_glob`; skips files over 10 MiB or unreadable ones and reports the skipped paths |
| `find_files` | Glob over file names, relative to `path`; absolute patterns are rejected |
| `create_directory` | Creates a directory and its missing parents |
| `file_info` | Size, type, binary-ness, a text file's line count and hash, and a symlink target where the workspace provides it |
| `list_files` (opt-in) | Ripgrep-backed recursive listing, sorted by path, with an optional `glob` |
| `grep` (opt-in) | Ripgrep-backed content search with `glob`, `file_type`, `ignore_case`, `literal` and `context` (0–20) |

Two read behaviours are worth naming because they bound cost. A file over **64 MiB** is described by its size rather than read, since `read_file` and `file_info` read a file whole for its line count and hash. And a missing path — including a directory passed to `read_file` — returns `Path not found: <path>` as a **tool result**, not a retry, so repeated lookups do not exhaust the model's retry budget; invalid arguments still request a retry[^pydantic-filesystem-docs]

## The search fallback stack

Search quality depends on what the workspace can run, and the source documents three tiers rather than one[^pydantic-filesystem-docs]:

1. **`rg` on the workspace's `PATH`** — the opt-in `grep` and `list_files` tools, honouring `.gitignore` inside a git repository and `.ignore` anywhere, with `file_type` support. The `coder` extra installs `rg` for a local workspace; installing it on the agent host does **not** install it in a remote workspace, so a sandbox image needs it.
2. **An in-workspace POSIX `git`/`grep`/`find` command** — used by command-capable POSIX workspaces without `rg`, after an initial probe, for `grep`, `list_files` and `search_files`. It lacks `file_type` and some ignore rules: it honours nested `.gitignore` in repositories and a search-root `.ignore` when git is available, but not nested `.ignore`; without git it applies no ignore files at all; and with git it searches tracked files that `.gitignore` lists, which `rg` skips. The first search that falls back logs one debug message saying so.
3. **Bounded Python walks** — for filesystem-only and read-only workspaces, for `list_directory`, `find_files` and walker-backed searches. The walkers apply no ignore files and have no `file_type`.

Tier 3 carries the sharpest limit: Python's regex engine has no time limit, so it **refuses** a pattern that repeats a repeating group, such as `(a+)+`, which can take exponential time, while allowing a bounded repeat of a bounded group such as `([0-9]{1,3}[.]){3}`[^pydantic-filesystem-docs] The check is a heuristic for that one shape, not a time bound: overlapping alternatives (`(a|aa)+`) and quantifier runs (`a*a*a*a*b`) still run.

Shared behaviour across tiers: an explicitly named file is searched even when ignored; searches report output and result caps rather than presenting partial results as complete; an unreadable file (or, with `rg`, a directory) is skipped and named with the reason at the end of the result; recursive walks visit each real directory once, so symlinked aliases do not duplicate contents; output is sorted so a capped result is a deterministic prefix; and ripgrep output over 8 MiB is cut and reported as truncated[^pydantic-filesystem-docs] A pattern ripgrep rejects comes back as a retry so the model can correct the call.

Hidden entries belong to the ignore-file layer rather than to a fourth tier[^pydantic-filesystem-docs] An explicit dotfile glob selects hidden files, and naming a hidden directory as the search path reaches its contents. `list_directory` and the walker-backed `find_files`/`search_files` **report** the hidden entries they saw but omitted, with a pruned hidden directory counted as one entry rather than its unseen contents, while command-backed searches do not count hidden omissions at all — so what a search admits to skipping depends on which tier ran it (**Synthesis** from that last statement), and only the walker tiers can tell the model what it did not see.

## Access patterns: three lists, two granularities

Three independent `fnmatch` glob lists decide access, and `*` spans `/`, so `*.py` already matches `src/main.py`[^pydantic-filesystem-docs]:

| Field | Effect |
| --- | --- |
| `allowed_patterns` | When non-empty, only matching paths are accessible |
| `denied_patterns` | Rejected even when `allowed_patterns` matches; matching ignores case |
| `read_only_patterns` | Reads succeed, writes are rejected; matching ignores case |

A directory pattern also covers descendants, and `read_only_patterns` defaults to `**/.git`, `**/.env`, `**/.env.*`, `*.pem`, `*.key`, `**/secrets*` and `**/.pydantic-ai-harness/**` — the last because Harness capabilities keep spills and job status there[^pydantic-filesystem-docs] Protected paths stay **readable**; making one unreadable means adding it to `denied_patterns`, and `[]` makes every path writable. `protected_patterns` is the deprecated name and still works with a warning.

The rules apply at two different granularities, and this is the part most likely to surprise[^pydantic-filesystem-docs]:

- **Direct access** (`read_file`, `write_file`, `edit_file`, `file_info`, `create_directory`) gates the target path — the model must name a permitted path.
- **Walkers** (`list_directory`, `search_files`, `find_files`, `list_files`, `grep`) gate their **root** by denied patterns but **not** by `allowed_patterns`, because a root like `.` never matches a file pattern such as `src/*.py`; instead each **entry** is filtered with read-level access. So with `allowed_patterns=['*.py']`, `list_directory('.')` succeeds and shows only `.py` entries, while `read_file('notes.md')` is rejected.
- `read_only_patterns` alone never hides an entry: a protected path still appears in listings and is still readable, and only writes are refused.

## The security model, stated as a limit

The source is unusually explicit that containment is a **guardrail, not isolation**[^pydantic-filesystem-docs]:

- Every target is resolved, `..`, absolute paths and symlinks included, and rejected if it leads outside `root_dir`; listings may name an outside-leading link, but reading or writing it is rejected and the walkers do not descend into it.
- Patterns match the path relative to `root_dir`, and `read_only_patterns`/`denied_patterns` also match a symlink's **target**, so a link to `.env` is read-only like `.env`. Matching ignores case, so `.GIT/config` cannot slip past `**/.git` on a case-insensitive filesystem.
- Symlink detection needs the workspace's `realpath`: a filesystem-only backend without `SupportsRealpath` gets path-text checks only, so `..` and absolute escapes are caught but a symlink leading outside is not, and a link to `.env` does not match the patterns. That is exact for storage without symlinks, such as an object store.
- `LocalWorkspace` establishes **no** isolation boundary even with command execution disabled; bypasses inside the workspace process's OS authority are correctness bugs, not escapes. The checks run before each operation, so a symlink swapped between check and use is not caught, and `Shell` commands ignore `root_dir` entirely.
- `root_dir='/'` turns containment off while the patterns still apply, and with no patterns set as well the boundary check is off entirely.
- Bounded walks stop after 10,000 directories or 100,000 entries and end with `[... walk cut short ...]`.

Two further safety details belong here: `write_file`, `edit_file` and `create_directory` are **sequential tools**, so several changes in one model response apply in order and a write into a directory created earlier in the same response succeeds, while read tools still run in parallel; and binary detection is by leading bytes, not extension, so a file that looks like a PDF is sent as `BinaryContent` even with no extension[^pydantic-filesystem-docs] If the model cannot take that file kind — an image on a vision-less model, a PDF on Groq — Pydantic AI raises when it builds the next request and the run ends, so a file tool can turn an unsupported modality into a terminal failure.

### Reads, encodings and write targets

Three rules apply inside the boundary[^pydantic-filesystem-docs]:

- **Text encodings.** Text is read as UTF-8, and a byte that is not valid UTF-8 appears as U+FFFD. `edit_file` writes such bytes back unchanged when an edit matches only the text around them, while `write_file` replaces the whole file with the UTF-8 content it is given — so an edit can preserve bytes a write cannot.
- **Write targets.** `write_file` will not overwrite a directory, and a FIFO, socket or device is refused as not a regular file.
- **Bounded reads have one exception.** A file over 64 MiB is described by its size because `read_file` and `file_info` read it whole for the line count and hash — but a workspace that does not report sizes reads such a file first, so that cap rests on a backend capability rather than on the file alone.

The **5 MB** media limit is chosen as the strictest mainstream per-image limit, and where a returned file travels — inside the tool result or on the user channel — is decided per model, not by this capability[^pydantic-filesystem-docs]

### When a file tool fails

`FileSystem` splits its errors by whether the model can act on them[^pydantic-filesystem-docs] These come back as `ModelRetry`, so the agent reads the message and adjusts: a missing file, a denied path, a stale edit, a directory colliding with an existing file, an invalid glob pattern, a path name rejected by Windows, a path name the filesystem cannot encode, an over-long path name, a symlink loop, and a FIFO or other special file. Failures the model can do nothing about — a full disk, a workspace that is gone — still abort the run. When an OS error supplies a filename it is reported relative to `root_dir`, and a path outside it becomes `<outside-workspace>`; `file_info` applies the same rule to absolute symlink targets, so an error message cannot echo a host path.

## Events: veto before the write lands

`FileSystem` emits typed capability events in the `file_system` namespace, so a host can display or veto changes without parsing tool arguments[^pydantic-filesystem-docs]:

| Event | Dispatch | Operation | Payload |
| --- | --- | --- | --- |
| `FileChangeRequestedEvent` | immediate | `write_file`, `edit_file`, `create_directory` | `path`, `root_dir`, `operation`, `diff`, `truncated`; `cancel(reason)` |
| `FileReadEvent` | stream | `read_file` | `path`, `root_dir`, `content_hash` |
| `DirectoryListedEvent` | stream | `list_directory` | `path`, `root_dir`, `entry_count` |
| `FileWrittenEvent` | stream | `write_file` | `path`, `root_dir`, `content_hash` |
| `FileEditedEvent` | stream | `edit_file` | a `FileWrittenEvent` plus `diff`, `truncated` |
| `DirectoryCreatedEvent` | stream | `create_directory` | `path`, `root_dir` |
| `FilesSearchedEvent` | stream | searches | `path`, `root_dir`, `pattern`, `search_kind`, `match_count`, `truncated` |

`FileChangeRequestedEvent` is the only **decision**; the rest are notifications[^pydantic-filesystem-docs] It fires only after the path has passed the access checks and, for writes and edits, the conflict check — so a denied path, a missing parent, a stale `expected_hash`, or a directory colliding with a file emits **no** request, and a listener cannot approve what policy or the filesystem already refuses. Once the listener returns, the path is re-resolved and re-checked and the file is re-read, so a file changed while a human was reviewing the diff fails the write instead of being overwritten. `cancel(reason)` stops the change before it touches disk and hands the reason back as the tool result; a listener that raises aborts the run instead.

Diffs are cut at `MAX_EVENT_DIFF_CHARS` (8,192) with a `truncated` flag, and a change whose text exceeds `MAX_DIFF_SOURCE_CHARS` (32,768) on either side — or whose line-product exceeds 65,536 — is announced with the two file headers and no diff at all, which bounds both flooding and differ work[^pydantic-filesystem-docs] `path` is always normalised relative to `root_dir`, never absolute, so it is safe to echo to a UI; `root_dir` is absolute POSIX inside the workspace so a subscriber rooted elsewhere can rebuild the location. There are no OpenTelemetry spans of its own: the core tool-call span records each operation, and the events carry the diff a trace would not.

Listening is not limited to `@agent.on_event`: another capability subscribes with `@on_event` on a method, which is how `RepoContext` follows `FileReadEvent`, `DirectoryListedEvent` and `FileWrittenEvent`[^pydantic-filesystem-docs] A host that brings its own file tools can emit these same event types by importing them from `pydantic_ai_harness.file_system`, so a subscriber hooks the event rather than a tool name or raw model arguments — the set is an interface between capabilities, not a private signal.

## Tool kinds and stepping aside

Each tool declares a [typed tool kind](pydantic-ai-tool-kinds.md) in the `file_system` namespace — `READ_FILE_KIND`, `WRITE_FILE_KIND`, and so on — with its argument shape, so a call whose arguments fit is promoted to a typed part (`ReadFileCallPart`, `WriteFileCallPart`, …) with `typed_args` in messages and loaded histories[^pydantic-filesystem-docs] The kind lives in the tool **definition**, not its name, so another capability or a history processor can recognise these tools without string-matching names. `read_file` also has a typed return part, `ReadFileReturnPart`, whose `outcome='success'` also covers `Path not found` and the over-64 MiB description — so success there does not mean content was read. The other tools return text written for the model, keep plain `ToolReturnPart`s carrying `tool_kind`, and expose their outcomes through events instead.

That kind is also how three other capabilities yield to `read_file`: `ToolOutputLimits`' `read_tool_result`, `Memory`'s `read_memory`, and `RepoContext`'s inventory tool mark their readers `unless_tool_kind=READ_FILE_KIND` when their files sit in the run's workspace, so a step that has `read_file` uses that instead[^pydantic-filesystem-docs] The trap is that the decision comes from **their** configuration, not `FileSystem`'s access rules: if `denied_patterns` cover `.pydantic-ai-harness/`, the memory directory or the asset roots, the dedicated reader still steps aside and `read_file` then refuses those files. The fix is a store with its own workspace (see [Harness memory](pydantic-ai-harness-memory.md)) or readable asset roots. A renamed `FileSystem` under `PrefixTools` still triggers it — and `PrefixTools` renames tools without scoping them, so two prefixed `FileSystem`s reach the same files under the same root.

## Configuration, specs and durability

The documented defaults are `root_dir=None` (the workspace working directory; `'/'` disables containment), `allowed_patterns=[]`, `denied_patterns=[]`, `read_only_patterns` the secrets/`.git`/`.pydantic-ai-harness` list, `max_read_lines=2_000`, `max_read_chars=50_000`, `max_list_results=1_000`, `max_search_results=1_000`, `max_find_results=1_000`, `read_only=False`, `content_hashes=True`, `tools=DEFAULT_TOOL_NAMES`, `max_retries=None`; the integer limits must be positive and are validated at construction[^pydantic-filesystem-docs] `max_read_chars` is meant to be set at or below any downstream tool-output cap, because a cap applied after the fact cuts mid-line and strands the continuation hint. `content_hashes=False` drops the hash from read headers and write results and removes `expected_hash` — for a single-writer coding agent the hashes only add tokens, while events still carry `content_hash` either way. `root_dir` must **contain** the working directory, so a subdirectory of it is rejected; work in a subdirectory by setting it on the workspace.

Further documented details sharpen those defaults[^pydantic-filesystem-docs] `max_read_chars=None` leaves only `max_read_lines` in force, and a cap smaller than the header and continuation hint themselves cannot be met — the result still carries them. `cwd` is **deprecated and ignored**, so relative paths resolve from the workspace's working directory. A walker that hits its cap ends its output with `[... truncated at N ...]`, and only when a further entry was actually dropped, which makes the marker a reliable signal rather than decoration. `tools` selects from `FILE_SYSTEM_TOOL_NAMES`, with `DEFAULT_TOOL_NAMES` the eight filesystem-only tools and `read_only=True` narrowing the selection to `READ_ONLY_TOOL_NAMES`; `before_run` fails a run that has no workspace without touching it, leaving the boundary check to the first file operation; and `get_toolset()` returns the same toolset for every run, so durable execution sees the leaf it registered.

Outside a run the toolset is callable directly: `get_toolset()` yields a `FileSystemToolset` (a `FilteredToolset` when `read_only` narrows it) whose methods take the workspace as an argument, e.g. `read_file('README.md', workspace=LocalWorkspaceBackend('.'))`, so a plain task can reuse the same containment and patterns without a model[^pydantic-filesystem-docs] Storage elsewhere needs only a `WorkspaceBackend` implementing `SupportsFilesystem` — plus `SupportsCommands` for ripgrep searches and `file_info` symlink targets — because containment, patterns, events and hashes apply unchanged, which is what makes the guardrail reusable across backends rather than tied to [local or sandbox workspaces](pydantic-ai-workspace-backends.md).

Specs declare the capability by name with `custom_capability_types=[FileSystem]` and attach the workspace at run time[^pydantic-filesystem-docs] It works under Temporal, DBOS, Prefect, Azure Durable Task and Render Workflows, with a live-event caveat per engine: on **Temporal** only file-change requests and write events reach listeners live; on **Azure Durable Task** the three change tools run in the orchestrator, so listeners re-run on every replay, must stay deterministic and do no I/O — interactive approval through a UI is not supported there yet — and events from the other tools are dropped; on **Render** listeners run in the parent task and the other events are carried back to the run.

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram was read in its text form[^pydantic-filesystem-docs] External links — workspace, durable-execution engines, typed tool parts, tool-return file provenance, toolsets, prefix tools and input support — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-opus-5-5`, an alias no release pin corroborates.

Nothing was installed, no file read, written, edited, listed or searched, no pattern matched, no event emitted or cancelled and no replay attempted, so every claim is **Reported** and none **Observed** or **Reproduced**. This pass added no new evidence class: the sections on failure taxonomy, encodings, write targets, custom storage and the event subscription form are all **Reported** from the same capture, and the one **Synthesis** in the page (that a search's reported omissions depend on the tier that ran it) is labelled where it stands. Unstated and consequential: the exact `rg` invocation and its flags, how `include_glob` interacts with the POSIX fallback's ignore rules, what `diff` format version the events carry beyond "unified", and whether the 5 MB media cap is per file or per tool result.

## Relationships

- **Complements** [Shell](pydantic-ai-harness-shell.md): `root_dir` bounds these tools only, never a command.
- **Composed into** [Coder](pydantic-ai-harness-coder.md) with five of its tools and content hashes off; bounded beside it by tool-output limits, and shadowed where [smart search](pydantic-ai-harness-smart-search.md) is the better retrieval.
- **Steps aside for** [Memory](pydantic-ai-harness-memory.md)'s `read_memory` and `ToolOutputLimits`' `read_tool_result` when their files are in the workspace and `read_file` is present.
- **Approval-aware** through `FileChangeRequestedEvent`, which is the Harness-side complement of core's [deferred tool approval](pydantic-ai-deferred-approvals.md).
- **Depends on** the [workspace backend](pydantic-ai-workspace-backends.md) for `realpath` and for anything beyond path-text containment.

[^pydantic-filesystem-docs]: Pydantic Docs, "FileSystem", <https://pydantic.dev/docs/ai/harness/filesystem/>; local capture `raw/harness/filesystem/index.md`, content digest sha256:adf7e011, 5,382 words as declared (5,386 by `wc -w`), 481 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the one-paragraph contract; 13–33 for the flow diagram (path resolution, containment, patterns, the `FileChangeRequestedEvent` listener); 35–43 for the problem statement; 45–65 for the usage example and the `root_dir` default; 67–72 for where files live, the read-only narrowing and the `rg`/walker split; 74–90 for the ten-tool table, the `Path not found`-as-result rule and the read caps; 92–104 for tool selection, the ripgrep defaults and the fallback rules, the `path:line:text` format, the retry-on-rejected-pattern rule and the 8 MiB cut; 106–118 for the tool-name sets, `content_hashes` and the hidden-entry rules; 120–128 for the working directory, `..` paths, `include_glob` semantics and the `PrefixTools` note; 130–147 for tool kinds, the typed call/return parts and `unless_tool_kind`; 149–159 for the three capabilities that step aside and the denied-pattern trap; 161–186 for the event table, the re-check-after-listener rule, `cancel`, and the diff caps; 188–200 for the listener example; 202 for the `@on_event` subscription form and host-emitted event types; 204 for the absent OpenTelemetry spans; 206–208 for the retryable-versus-aborting error split and the `<outside-workspace>` redaction; 210–221 for the security model, bounded walks, binary detection, ordered changes, encodings, write targets and the bounded-read exception; 223–237 for custom storage and the programmatic toolset call; 239–279 for the three pattern lists, their defaults and the direct-access-versus-walker granularity; 281–303 for the configuration block, its validation and the truncation marker; 305–331 for the agent-spec form and the per-engine durable-execution caveats; 333–480 for the API reference, including the deprecated `cwd` at 355, `read_only` at 419, `tools` at 435, `before_run` at 457 and `get_toolset` at 471. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
