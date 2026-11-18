---
type: Concept
title: Pydantic AI Harness memory
description: The Harness Memory capability — a Markdown notebook injected once per changed run inside a bounded token budget, four tools with compare-and-swap writes and idempotency receipts, five stores with different concurrency guarantees, namespaces that are not authorization, optional write metadata, and the snapshot's prompt-cache and compaction behaviour.
tags: [pydantic-ai, agents, harness, memory]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:13:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-memory-docs
    resource: ../raw/harness/memory/index.md
    scope: ../raw/harness/memory/
    kind: documentation
    revision: sha256:fe2791f633810f8ada1de015e753c80f7c9234fb9e53785bc9ba358141c10bb6
    title: "Memory"
---

`Memory` is the [Harness](pydantic-ai-harness.md) capability that gives an agent a persistent **notebook of Markdown files** across runs, delivered as a bounded excerpt injected once per changed run rather than as a store loaded wholesale into every prompt[^pydantic-memory-docs] It is the concrete answer to "the agent should remember", and its design is entirely about the tension in that sentence: model-written text re-entering future prompts, a fixed context budget, non-unique file paths, and several writers. The [skills](pydantic-ai-harness-skills.md) page covers the other half of long-term agent knowledge — procedures rather than notes. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## The notebook model

`MEMORY.md` is the main notebook; other files hold longer or focused notes[^pydantic-memory-docs] Four tools are registered:

| Tool | Purpose |
| --- | --- |
| `write_memory` | Append to a file or replace one unique text fragment — with `\r\n` files, an `old_text` using `\n` as the injected snapshot shows it still matches |
| `read_memory` | Read a bounded prefix of one file; **left out** when `FileSystem` can read the files |
| `delete_memory` | Delete a file; the main notebook is protected |
| `search_memory` | Literal text search under configured result, character and file-scan limits |

Files live at `{namespace}/{agent_name}/{file}`, so with the defaults a UI edits `{user_id}/main/MEMORY.md` to change what the agent reads[^pydantic-memory-docs] `agent_name` is a storage segment only and never appears in the prompt — which is why several notebooks on one agent need distinct `heading`s as well.

## Injection: one snapshot per changed run, inside a budget

Automatic injection is on by default, and the mechanics are where most of the operational consequences live[^pydantic-memory-docs]:

- The **guidance** goes in the model instructions (trusted and static, so it stays inside the cached prefix); the **stored memory** goes in a `<memory>` block as a **user-role part** recorded with the user's prompt. Model-written content therefore never sits in the instruction channel.
- The guidance, `MEMORY.md` and the list of other files share `max_tokens` (default 2,000, estimated at four characters per token); the default guidance alone uses about 200. `max_lines` (200) additionally caps the notebook's lines and `max_memory_size` (65,536) caps each backend read, so the capability never requests an unbounded file or listing.
- Whatever does not fit is omitted with a note pointing at `read_memory` (or `read_file`, where it replaces it) or `search_memory`. When the guidance alone fills the budget, **nothing** is injected and the `memory.inject` span records `memory.outcome='budget_exhausted'`.
- A snapshot is added on the **first request of a run**, with the user's prompt, and only when memory changed since the latest snapshot in the history (or there is none). It is written into message history, so every later request resends it unchanged and the cached prefix holds; the guidance tells the model that a later block for the same memory supersedes earlier ones. A snapshot before the latest compaction boundary stops counting, so the next run records current memory again.
- Emptied memory produces a snapshot that **says so**, since "what was deleted" is itself the information.
- Nothing is injected after tool results, where a model could read it as a new user message — with one exception: if compaction drops the snapshot the run started with, the **same** snapshot is enqueued again on the same request without re-reading the store, landing after the tool results, which is the one position every compaction strategy keeps, native compaction included.
- Runs that start without a prompt ending in tool results or a response — resuming after a deferred approval, continuing a provider-suspended response — and a `Memory` loaded mid-run via `defer_loading=True` add no snapshot at all. A run with no prompt and no tool results (an empty-history `agent.run()`) does get one on that request.

The snapshot is a `MemorySnapshotPart`, a capability part recognised by **type and its `scope_hash`/`memory_id` fields, never by its text**[^pydantic-memory-docs] Because the UI adapters (Vercel AI, AG-UI) keep capability parts on the server, a history that round-trips through a UI client comes back **without** its snapshots and gets a fresh one every run — so server-held history is what makes the once-per-run behaviour actually hold. Stored content goes in as written with a note in the application's voice that the agent wrote it earlier, and text that looks like `<system>` or opens/closes `<memory>` gets a further note, so memory cannot end its block early or speak as the application.

`inject_memory=False` keeps memory out of the conversation entirely and leaves the tools, so the model fetches only when needed — the documented answer for stores less-trusted parties can write to. Snapshots earlier runs added stay in the history.

`injection_errors` decides what a **store failure during automatic injection** does: `'ignore'` (the default) skips injection and emits content-safe telemetry, while `'raise'` fails the run rather than let it proceed without injected memory[^pydantic-memory-docs] The spans record the backend type, a hash of the resolved scope, counts, whether a snapshot was appended (`memory.appended`) and the exception type — never memory content. Namespace and `store_resolver` failures always propagate whatever this setting says, and it covers injection only: inside the tools, a path resolving outside the store asks the model to retry, a write or delete that keeps conflicting asks it to retry again, a workspace failure during `write_memory`/`delete_memory` returns a failed tool call unless the workspace is unavailable, and any other store error ends the run. The failure message names only the memory file, so backend paths and the namespace stay out of the model's context.

## Reading memory with FileSystem

When the store is a `FileMemoryStore` keeping files in the run's workspace (no `workspace=` of its own, and a relative `directory` inside the working directory) **and** `FileSystem` is on the agent, `read_memory` steps aside for `FileSystem`'s `read_file` via `unless_tool_kind=READ_FILE_KIND`[^pydantic-memory-docs] An instruction block named `directory` then says where the files are ("Memory files are in `.agent-memory/main/` in the workspace; read them with the file-reading tool"), present from the first request, empty while no file reader is on the run, and appended to history when one joins; its text counts against `max_tokens`, and when it does not fit, `read_memory` stays and the block says nothing.

The decision is made from the **store**, not from `FileSystem`'s access rules — so a `FileSystem` whose `denied_patterns` cover the memory directory still replaces `read_memory` and then cannot open the files; giving the store its own `workspace=` is the fix[^pydantic-memory-docs] The same section carries the namespace leak that matters most: with file tools over the run's workspace, the model can read **every** namespace's files under `directory`, whether or not `read_memory` is offered — so namespaces that separate users who must not see each other's memory require a store with its own workspace. That is the [workspace file authority](pydantic-ai-workspace-authority.md) problem in a memory costume.

## Persistence, concurrency and receipts

Two mechanisms apply to every store, and custom stores must implement both atomically[^pydantic-memory-docs]:

- **Compare-and-swap**: a mutation based on stale content fails with a conflict instead of overwriting a concurrent edit — so editing a Markdown file outside the capability changes its version, and a write based on the old content conflicts.
- **Idempotency**: a replayed tool call is not applied twice, identified from the run, its step and the tool call; reusing that identifier with **different** arguments raises `MemoryOperationConflictError`.

| Store | Persistence and concurrency boundary |
| --- | --- |
| `InMemoryMemoryStore()` | Process lifetime; atomic across tasks sharing the instance; receipts for the 1,024 most recent mutations |
| `FileMemoryStore(directory)` | Markdown in the run's workspace or in `workspace=`; versions are content hashes; receipts in `.memory-operations.json` beside the files; **one writer per directory** |
| `SqliteMemoryStore(database=…)` | Durable single-host; compare-and-swap and idempotency in database transactions; receipts accumulate in `memory_operations` until deleted |
| `PostgresMemoryStore(pool)` | Durable shared; same guarantees in transactions; receipts in `{table}_operations`; caller owns the pool |
| `PixeltableMemoryStore(table_name=…)` | Durable shared in a Pixeltable catalog; receipts and table history retained; Python 3.11–3.14 with the `pixeltable` extra |

`FileMemoryStore` serializes **its own** operations but not another store's or another process's writing the same directory, so concurrent writers need one shared instance or a SQLite/Postgres store; it also skips symlinked directories, including links out of the store[^pydantic-memory-docs] On first call `PostgresMemoryStore` checks its three tables, `{table}_versions` sequence and later-added columns and creates what is missing under `pg_advisory_xact_lock` — only that step needs `CREATE` on the schema and table ownership, after which `SELECT`/`INSERT`/`UPDATE`/`DELETE` plus sequence `USAGE` suffice. It creates an index on `path COLLATE "C"` so scope filters stay sargable under any database collation; a table from an earlier release does not get it automatically (building it blocks writes), so the documented migration is `CREATE INDEX CONCURRENTLY`.

`SqliteMemoryStore` can instead take a caller-owned `sqlite3.Connection`, which must be created with `check_same_thread=False` because operations run off the event loop, stay dedicated to the store and be idle at the start of every operation — a call fails rather than commit or roll back an active caller transaction[^pydantic-memory-docs]

Two write-side limits: `write_memory` **refuses** to append to or edit a file larger than `max_memory_size`, because it would build the new content from a partial read (edit or replace the file in the backing store first), and every bounded read returns `MemoryFile.truncated=True` with the version of the complete file[^pydantic-memory-docs] A corrupt receipts file warns and starts a fresh journal — restore a backup if replay protection for earlier operations matters.

## Namespaces are addressing, not authorization

A namespace resolver runs once per run from typed dependencies, and its result is hidden from the tool schema, so the model cannot select another user's namespace in a tool call[^pydantic-memory-docs] The limits are stated as limits:

- A namespace is one or more `/`-separated segments of letters, digits, `_`, `-` and `.`; a `.` segment or a segment containing `..` raises `ValueError` when the run starts.
- `FileMemoryStore` maps a namespace to a directory, so on a **case-insensitive** filesystem (macOS and Windows defaults) `Alice` and `alice` share files — normalize the identity's case first — and Windows also drops trailing dots, so `alice.` and `alice` share too.
- Spans record `memory.scope_hash`, an **unsalted** hash of namespace and `agent_name`: it keeps the identity out of telemetry, but anyone who can guess an identity can confirm it.
- Namespace isolation controls which records the capability addresses; it is **not** an authorization system for a custom or shared backing store. Validate identity in dependencies, restrict backend credentials, and ensure custom stores cannot escape the resolved namespace.

## Provenance: write metadata

When people can also edit what the agent remembered about them, `write_metadata` records who made each write[^pydantic-memory-docs] `InMemoryMemoryStore`, `SqliteMemoryStore` and `PostgresMemoryStore` implement `MetadataMemoryStore` (`write_with_metadata`, surfaced as `MemoryFile.metadata`); `FileMemoryStore` and `PixeltableMemoryStore` **do not** — a sidecar could not change atomically with the Markdown, and the model's file tools could edit it. `write_metadata` takes a mapping or a per-run callable, never appears in a tool schema, and runs inside each `write_memory` call after the replay check, so unlike `store_resolver` and `namespace` it need **not** be deterministic under Temporal or Prefect.

The semantics are version-scoped rather than historical: metadata is written in the same transaction as the content, each write replaces it, a write without metadata records none (so after the agent edits a user-typed file it no longer reads `updated_by='ui'`), a delete removes it, and a replayed call returns the original receipt, which carries none — read the file for the metadata of its current version[^pydantic-memory-docs] It stays out of the model's context, the memory spans and the snapshot a durable engine journals, and `PostgresMemoryStore` keeps it in a queryable `write_metadata JSONB` column. Setting `write_metadata` against a store that does not implement the protocol raises `UserError` rather than dropping it.

The source is explicit that metadata records **which writer produced the current version**, not that a remembered claim is true — and that optimistic concurrency prevents lost updates, not falsehood.

## Several notebooks, search, and scanning

Several `Memory` capabilities can coexist — a personal plus a shared org notebook — under four constraints: distinct `id`s (sharing `id='memory'` makes them one capability unless store and settings match), distinct `agent_name`/`namespace` for separate notes, `prefix_tools` on every instance but one (they all define the same tool names), and a distinct `heading` per instance since `agent_name` never reaches the prompt[^pydantic-memory-docs]

`search_memory` is **literal** text search — no semantic ranking is built in — bounded by `max_search_results` (10), `max_search_result_chars` (4,000, combining filename and snippet) and `max_search_files` (1,000), with queries capped at 1,000 characters and 32 unique whitespace-separated terms and case-insensitive duplicates collapsed[^pydantic-memory-docs] Scoring uses only scope-relative filenames and bounded content, so tenant namespaces and agent names never affect relevance, and scoring yields after each file so a scan near the limits slows that search without stalling other runs. The bundled stores list and search only files **directly** in the scope, skipping a nested scope such as `acme/main` under `acme`, so its files cannot fill the injected file list or a search's file limit.

`scanner=ArtifactScanner()` is the content check, and it covers every path with a different answer[^pydantic-memory-docs]: `write_memory` **refuses** flagged text with a tool failure naming the threats without quoting them and stores nothing (only the text being written is scanned, so a correction that removes a passage still succeeds); a flagged `MEMORY.md` is left out of the injected snapshot with a notice in its place, while the file list is still shown; `read_memory` refuses a flagged file; `search_memory` replaces a flagged snippet with a notice; and each decision records a zero-duration `artifact_scan flagged` span plus `memory.main_withheld` on the memory span. Two limits: the scan runs **outside** the durable operations `Memory` routes its tools through, so under Temporal/Prefect/DBOS a refusal fails the tool call rather than an operation the engine would retry; and files read by `FileSystem`'s `read_file` in place of `read_memory` are **not scanned**. Pattern matching misses paraphrased instructions and can flag a note that quotes an attack, so it is one layer beside `inject_memory=False`.

## Security, durability and specs

Memory is model-written, untrusted content re-entering future prompts[^pydantic-memory-docs] The user-role position lowers its authority relative to instructions but is **not** a hard prompt-injection boundary; the source recommends `inject_memory=False` when less-trusted actors can write, application-controlled retrieval for stronger isolation, no secrets unless the backend, retention and access controls suit them, and sanitising before rendering memory into another trust domain. Memory records carry no citations, which is why write metadata exists as the provenance mechanism.

| Mode | Behaviour |
| --- | --- |
| Normal `Agent.run` | Automatic injection or on-demand tools |
| Temporal, Prefect | Snapshot loading is a **journaled capability operation**; the recorded snapshot is reused on replay; `store_resolver` and a callable `namespace` run **before** it, so they must be deterministic and free of backend I/O — a per-tenant resolver that queries a backend is not workflow-safe |
| DBOS | Snapshot loading and each memory tool call are DBOS **steps**; a recovered or forked workflow reuses their recorded results instead of re-reading or re-writing |

`Memory` carries the stable default `id='memory'`, so durable recovery needs no configuration, and each model request that injects records one bounded snapshot result in workflow history — which is why `max_memory_size` and `max_tokens` should be chosen with the engine's history limits in mind[^pydantic-memory-docs] Durable execution does **not** make an in-memory notebook persistent: the backend and the workflow state backend stay independent.

Specs register `Memory` as a custom capability type with a serializable `backend` of `memory`, `file` or `sqlite`; a namespace callable and a live PostgreSQL pool must be configured in Python[^pydantic-memory-docs]

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram was read in its text form[^pydantic-memory-docs] External links — the workspace, capability-parts, hooks, Pixeltable, artifact-scanning, logging and compaction pages, and the module source — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-opus-5-5`, an alias no release pin corroborates.

Nothing was installed, no notebook written, read, searched or deleted, no store migrated, no conflict raised and no span inspected, so every claim is **Reported** and none **Observed** or **Reproduced**. Unstated and consequential: the exact token estimator beyond "four characters per token", how `PostgresMemoryStore` behaves under heavy concurrent writers beyond the transaction guarantee, what retention the bundled stores assume for accumulated receipts, and how large a snapshot a durable engine's history can take before the journal itself becomes the bottleneck.

## Relationships

- **Depends on** a [workspace](pydantic-ai-workspaces-and-sandboxes.md) for `FileMemoryStore`, and steps aside for [FileSystem](pydantic-ai-harness-filesystem.md)'s `read_file` when the files are in that workspace.
- **Interacts with** [history processors](pydantic-ai-history-processors.md) and compaction: list compaction before `Memory`, and expect a dropped snapshot to be re-enqueued after tool results.
- **Keeps the cached prefix stable** the way [prompt caching](pydantic-ai-prompt-caching.md) requires, by putting snapshots in user-role history rather than instructions; see [Harness planning](pydantic-ai-harness-planning.md) for the same argument about plans.
- **Constrained by** [durable execution](pydantic-ai-durable-execution.md): deterministic resolvers, journaled snapshots, and one snapshot record per injected request.
- **Composed into** [Coder](pydantic-ai-harness-coder.md) agents beside [skills](pydantic-ai-harness-skills.md), which carry procedures where memory carries notes.
- **Is the cross-conversation tier of** [persistence choices](pydantic-ai-persistence-choices.md): keyed by a namespace rather than by `conversation_id`, which is what lets it outlive the thread.

[^pydantic-memory-docs]: Pydantic Docs, "Memory", <https://pydantic.dev/docs/ai/harness/memory/>; local capture `raw/harness/memory/index.md`, content digest sha256:fe2791f6, 6,190 words as declared (6,294 by `wc -w`), 808 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the one-paragraph purpose; 13–37 for the flow diagram (namespace from deps → four tools → store → first-request `<memory>` block); 39–62 for the notebook model, the four-tool table, the `\r\n` match rule, the `FileMemoryStore` workspace requirement and the machine-local backend; 64–84 for `read_memory` stepping aside for `read_file`, the `directory` instruction block, the store-not-access-rules rule and the cross-namespace read warning; 86–118 for the injection budget, the guidance/snapshot split, the change-detection rule, the compaction exception and `inject_memory=False`; 120–146 for snapshot placement, supersession, the `MemorySnapshotPart` and the UI-adapter round-trip loss; 148–176 for persistence and concurrency, the receipt tables, the SQLite `check_same_thread` rule and `FileMemoryStore`'s single-writer boundary; 178–196 for the Postgres schema bootstrap and the `COLLATE "C"` index; 198–212 for namespaces, the segment grammar, case-insensitivity and `scope_hash`; 214–236 for write metadata and its version-scoped semantics; 238–256 for several notebooks and the four constraints; 258–286 for search bounds, scoring scope and child listing; 288–312 for the configuration block, the agent-spec backends and the durable-execution table; 314–340 for the security, provenance and `ArtifactScanner` sections; 342–807 for the API reference, including `resolve_scope`, `combine`, `before_model_request` and `MemoryToolset`. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
