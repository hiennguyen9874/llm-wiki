---
type: Concept
title: Pydantic AI Harness coder
description: The Harness Coder combined capability — six coding tools, an unrestricted persistent shell, delegation to a fresh run of itself, repository instructions, argument repair and context controls, with its install extra and ripgrep search fallbacks, long-running-command handles, autonomy levels, strict-mode and caching defaults, filesystem scope, and the 0.x migration rules.
tags: [pydantic-ai, agents, harness, coding-agents]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:15:16Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-coder-docs
    resource: ../raw/harness/coder/index.md
    scope: ../raw/harness/coder/
    kind: documentation
    revision: sha256:8e37199809fecdbb41179e31ec87e5ec855962e11e2a210c56163c3cf6621f9d
    title: "Coder"
---

`Coder` is the [Harness](pydantic-ai-harness.md)'s complete coding agent expressed as one **combined capability**: file tools, a persistent shell, repository instructions, self-delegation and context controls, assembled in a fixed order, so it can be used whole or taken apart with any single setting changed[^pydantic-coder-docs] It is the natural home of the [filesystem](pydantic-ai-harness-filesystem.md), [shell](pydantic-ai-harness-shell.md) and [subagent](pydantic-ai-subagents.md) capabilities, and the shortest path from an empty Python file to an agent that fixes a failing test. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

It is also the only Harness capability whose *defaults* are the interesting part: strict tool schemas off, prompt caching on, retries loosened, tool output capped, and instructions scoped to everyday project work rather than benchmark grading. Most of this page is those defaults.

## The composition, in order

`Coder()` is eleven entries, the first five of which the model can see[^pydantic-coder-docs]:

| # | Part | Configuration |
| --- | --- | --- |
| 1 | Instructions | The default block plus any `instructions=` you pass (appended, not replacing) |
| 2 | `FileSystem` | `content_hashes=False`, `max_read_chars=50_000`, `tools=FILE_TOOL_NAMES` (`read_file`, `write_file`, `edit_file`, `list_files`, `grep`), `max_retries=5`, `root_dir` = the working directory |
| 3 | `Shell` | `denied_commands=[]`, `allow_interactive=True`, `default_timeout=270`, `tools=['shell']` |
| 4 | `RepoContext` | `walk_up='repo_root'` — each directory's `AGENTS.md`, else `CLAUDE.md`, from the repository root down at run start, and subdirectory files when the agent first touches something under them; a subdirectory file that would exceed the 32,000-character inlined budget becomes a pointer |
| 5 | `SubAgents` | `include_self=True`, `agent_folders=None` — one delegate, `self`, a fresh run of the same agent |
| 6 | `ClearToolResults` | `max_fraction=0.7` |
| 7 | A private `ToolOutputLimits` | Truncates any tool result over 64,000 characters with **no** spill-retrieval tool; its stable id is `coder_tool_output_limits`, so durability capabilities bind its operations without colliding with a separately configured `ToolOutputLimits` |
| 8 | `RepairToolArguments` | `json-repair` on malformed JSON before schema validation |
| 9 | Retry exhaustion | Once a tool's retries run out **during execution**, its last error returns to the model as a failed tool result with a prompt to try a different approach instead of ending the run — for every tool, `delegate_task` included; running out on argument *validation* still ends the run |
| 10 | Prompt caching | `cache=True` through the unified model setting, unless the model, the agent, or a capability listed before `Coder` already sets it; `caching=False` leaves it out |
| 11 | Strict mode off | `strict=False` for Coder's own tools; `strict=None` defers to the provider |

Item 2's `max_retries=5` is a deliberate deviation from the agent's default: a denied path or a stale edit is a correctable mistake, and five consecutive retries keep a repeated slip from ending a long autonomous run[^pydantic-coder-docs] Item 9 is the same idea one level up — a tool that keeps failing degrades into advice rather than a dead run, while [usage limits](pydantic-ai-run-controls.md) still bound a model that never changes course.

## The six tools

Every tool comes from `FileSystem`, `Shell` or `SubAgents`; `Coder` contributes none of its own[^pydantic-coder-docs]

| Tool | Behaviour |
| --- | --- |
| `read_file(path, offset=0, limit=None)` | Zero-based offset, one-based displayed numbers, 2,000 lines and at most 50,000 characters of complete lines, with the exact next offset in the hint and no hash header |
| `write_file(path, content)` | Creates in an existing directory or replaces; no `expected_hash` |
| `edit_file(path, old_text, new_text)` or `edit_file(path, replacements=[...])` | Exact replacements, each matching once; a batch is checked in memory and written only if every replacement matches |
| `list_files(path='.', glob=None)` | `rg --files`, sorted, honouring ignore files and skipping hidden files |
| `grep(pattern, …)` | Ripgrep with `path`, `glob`, `file_type`, `ignore_case`, `literal`, `context` (0–20) |
| `shell(command, mode='foreground', timeout=270)` | Unrestricted commands rooted at the workspace, outliving the run |
| `delegate_task(agent_name, task)` | Hands a self-contained sub-task to `self`; absent when `sub_agents=False` |

Bounds stack: `FileSystem`'s caps (2,000 lines and 50,000 characters per read; 1,000 entries per listing or search) sit under Coder's 64,000-character tool-output limit, so a `read_file` window always fits and paging by `offset` never skips lines[^pydantic-coder-docs] A truncation marker means narrowing the search, not assuming completeness. Read-only path rules (`.git`, `.env`, keys, secrets) still apply to the file tools — and `shell` can bypass them, which is why the default instructions and the `Permissions` capability exist.

`Coder` deliberately excludes **planning** and the `run_command` family: planning is added separately as [Harness planning](pydantic-ai-harness-planning.md), and background commands run through the persistent `shell` tool instead.

## The extra and search tooling

`Coder` is not in the base install: `pip install "pydantic-ai-harness[coder]"` supplies `json-repair` (which `RepairToolArguments` needs) and `ripgrep==14.1.0` (which backs `list_files` and `grep`), and importing `Coder` or `coder_agent` from a plain install raises an `ImportError` naming the extra; add a provider extra as `[coder,anthropic]` when needed[^pydantic-coder-docs] The `rg` wheel is skipped on Android, where `rg` must already be supplied on `PATH`.

Two operating consequences follow, and both are easy to get wrong[^pydantic-coder-docs]:

- **The extra installs `rg` on the agent host, not in a remote image.** With a sandbox, put `rg` and `git` in the image for fast search, and prefer the file tools (`grep`, `list_files`, `read_file`) over sending whole files through shell `cat`.
- **Large or generated trees belong in Shell.** Run `rg -n 'pattern' path` or `rg --files` through `shell` and cap the output, rather than letting a full-tree listing pile up against the 64,000-character tool-output limit.

Without `rg`, `grep` and `list_files` degrade after an initial `rg` probe: one `git`/`grep`/`find` command in a command-capable POSIX workspace, or a bounded file walk on a filesystem-only backend[^pydantic-coder-docs] With git present the POSIX fallback honours nested `.gitignore` in repositories plus the search root's `.ignore`, but **not** nested `.ignore`; without git it cannot apply ignore files at all; and rg-only regex features require `rg`. Searches report their output and result caps instead of presenting partial results as complete — the same discipline the truncation marker asks of the reader.

## Autonomy is guidance, not a gate

`autonomy` is one of four levels, and all of them are instructions to the model[^pydantic-coder-docs]:

| Level | Behaviour |
| --- | --- |
| `'low'` | Proposes a plan and waits for approval before editing |
| `'medium'` | Works until done, asking when a choice really matters |
| `'high'` (default) | Works until done, asking only for credentials, approvals or real ambiguity, and measures results against any numeric target the task states |
| `'max'` | Never asks; chooses sensible defaults, measures numeric targets, deletes its scratch files, and treats an unmet stated criterion as a sign it misread the task rather than settling — for runs nobody can answer, such as CI |

Nothing stops an agent that ignores the sentence from editing or running commands: requiring approval means adding [`Permissions`](pydantic-ai-harness.md) or a `FileChangeRequestedEvent` listener, not raising the autonomy level. And a **delegate** is always told to choose sensible defaults and finish and to measure numeric targets, whatever level it inherits — it was handed its task by a parent[^pydantic-coder-docs]

## Default instructions

The bundled instructions are short and shape a run more than their length suggests: match the surrounding code's style, structure and imports; read files with `read_file`; confirm each stated requirement and edge case explicitly; check behaviour with heredocs rather than new files; and finish long-running work before replying[^pydantic-coder-docs] Guidance that only pays off under a benchmark verifier is opt-in through `BenchmarkInstructions`. `Coder(instructions='...')` **appends** project-specific policy — file-size limits, a preferred verification workflow — rather than replacing any of this, while tool usage itself comes from the tool descriptions and repository instructions and structure come from `RepoContext`.

## Delegation to self

`SubAgents(include_self=True)` gives `delegate_task` one delegate named `self`: a fresh run of the same agent, with the same model, workspace, instructions and capabilities — including an approval gate, guardrail or audit hook bound next to `Coder`, which therefore sees the commands a delegate runs[^pydantic-coder-docs] The delegate starts without the conversation, so the parent must pass everything the task needs, and it can delegate again up to `max_depth=3` counting the top-level run. Disk-defined delegates load only when `agent_folders=` is passed; `task_control=TaskControl()` upgrades delegations into managed background tasks (see [subagent task control](pydantic-ai-subagent-tasks.md)) and requires `sub_agents=True`.

Two operational rules follow from the composition mechanism[^pydantic-coder-docs]:

- Only what is bound to the `Agent` carries into a delegate; capabilities, toolsets, instructions and model settings passed to `run()` do not. Binding `Coder` therefore means `Agent(capabilities=[...])`; passing it to `run()` raises `UserError` unless `sub_agents=False`.
- Coder's instructions tell the agent **not** to delegate unless the user or `AGENTS.md` asks — the same rule Codex gives its models — because a delegate re-explores the project from a fresh context, so unrequested delegation multiplies tool calls and cost. Opting in means asking in the prompt, in `AGENTS.md`, or in `instructions=`.

## Filesystem scope, strictness and cache

Three settings are worth knowing separately, because each trades safety or token cost[^pydantic-coder-docs]:

- **`unrestricted_filesystem=True`** sets `FileSystem(root_dir='/', read_only_patterns=[])`: relative paths still resolve from the working directory, but absolute paths anywhere in the run's workspace are accepted and `.git`, `.env`, keys and secrets become writable. OS permissions and event listeners still apply; use it only for trusted local work, since shell commands were already unrestricted.
- **`strict=False`** (the default) turns off [strict tool schemas](pydantic-ai-tool-definitions.md) for Coder's tools, which OpenAI would otherwise constrain and Gemini 2.5+ would run in `VALIDATED` mode, and relies on argument repair plus validation retries instead. `strict=True` forces it on; `strict=None` leaves it to the provider. The Gemini caveat is request-wide: while an Coder tool has `strict=False`, the whole request stays on `AUTO`, including tools bound next to Coder.
- **`caching=True`** (the default) sets the unified `cache` model setting, because a coding run resends the same tool definitions and instructions plus a monotonically growing conversation on every request[^pydantic-coder-docs] A `cache` on the model, in the agent's `model_settings`, or from a capability listed **before** Coder replaces the default, as do a capability listed after it and the run's own `model_settings`; `model_settings={'cache': '1h'}` stretches the window and `caching=False` removes the default. Provider-specific settings such as `anthropic_cache` still win — see [prompt caching](pydantic-ai-prompt-caching.md).

Argument repair is heuristic and its limits are stated: `json-repair` runs only on malformed JSON, valid and already-parsed arguments pass through, missing fields and wrong types still follow normal validation, a parser value or recursion error falls back to the original arguments, and it neither receives the schema nor bypasses exact edit matching[^pydantic-coder-docs] Each attempt emits a `repair_tool_arguments` span through `ctx.tracer` without arguments or file contents.

## The command environment

Commands in a `LocalWorkspace` get `PATH`, `HOME`, `LANG`, `LC_ALL` and `LC_CTYPE` and nothing else[^pydantic-coder-docs] That has two consequences worth carrying: under `uv run`, `python` and `pytest` resolve through the agent project's virtualenv rather than the workspace's, so `LocalWorkspace('.', env={'PATH': ...})` is the fix; and secrets must be passed explicitly, one at a time — passing `os.environ` hands the model's commands every secret in the process, LLM API keys included.

## Long-running commands

`shell` is `Shell`'s persistent tool, and its return shape is what a polling loop or a UI has to work with[^pydantic-coder-docs] Foreground waits at most 270 seconds (or a smaller positive `timeout`) and then returns handles for the **same** running process; background returns them immediately. Both end with a PID, an absolute output-log path and an absolute JSON status path inside the workspace whose `exit_code` is `null` while the command runs, and foreground puts the last 16,000 bytes of output before them.

Three consequences matter operationally: commands **outlive the agent run**, so servers keep running; there is no completion notification and no automatic wake-up after a final response, so a caller must poll the status file; and the default instructions therefore tell the agent to finish long-running work before replying, polling until it is done or blocked — keeping the servers the task needs and stopping the rest. Commands get only the environment the workspace passes, while host files stay reachable to commands in a local workspace. The [Shell](pydantic-ai-harness-shell.md) capability owns the supervisor, cleanup and the `CommandStartedEvent`/`CommandOutputEvent`/`CommandFinishedEvent` progress a UI can subscribe to.

## Sharing the workspace

A workspace outlives the run that used it, and the source gives two distinct routes[^pydantic-coder-docs]: pass `message_history=result.all_messages()` to continue the **conversation** in the same files (history cannot move a `LocalWorkspace` elsewhere), or pass `workspace=result.workspace` to hand the **files** to another agent or a fresh conversation. `ReadOnlyWorkspace(result.workspace)` refuses commands and file changes, so a reviewer gets `read_file`, `list_files`, `grep` and `delegate_task` but no shell or editing tools; with a sandbox this is how several agents share one isolated machine. See [workspace selection and reattachment](pydantic-ai-workspace-selection.md).

Two interface differences are named rather than hidden: `to_cli_sync()` keeps one sandbox for the session, while `to_web()` starts a **new** sandbox per message because the web protocol does not carry the workspace ref — so persistent web files require `LocalWorkspace`. The exported `pydantic_ai_harness.coder:coder_agent` is the same agent, model-less and named `coder`, working in the directory current at import.

## The 0.x migration rules

The upgrade section is the most consequential part of the capture for anyone operating this, because these changes alter what a durable run records[^pydantic-coder-docs]:

- `json-repair` moved into the `coder` and `repair-tool-arguments` extras, so plain `pydantic-ai-harness` raises `ImportError` on `import Coder` / `coder_agent`.
- Repo instructions now load from the repository root (nearest directory with a `.git` entry) down to the working directory at run start, one file per directory with `AGENTS.md` ahead of `CLAUDE.md`, and 32,000 characters inlined per conversation. That adds workspace `exists`/`stat` calls at run start, so **Temporal and DBOS runs started before the upgrade no longer replay** — let them finish or version the deployment first.
- Default instructions no longer ask for self-contained deliverables checked from a clean directory or for using every field of the provided data; bind `BenchmarkInstructions()` to recover them, and record whether a run used it with its score.
- Prompt caching is now on, and strict mode is now off for Coder's own tools; `caching=False` and `strict=None` restore the old behaviour.
- The **workspace is the single place that decides where an agent works**: `Coder('dir')`, `Shell(cwd=)`, `FileSystem(cwd=)`, `RepoContext(workspace_dir=)` and `Macroscope(cwd=)` are accepted, warn with `HarnessDeprecationWarning`, and are ignored. `Coder`, `FileSystem`, `Shell`, `RepoContext` and `Macroscope` fail at run start without a workspace, as do `Skills`, `PydanticAIDocs` (with a local checkout) and `ToolOutputLimits` (when it can spill) unless given their own `workspace=` or store.
- Commands no longer inherit the whole environment, `denied_env_patterns` does not filter `LocalWorkspace(env=)`, Harness files moved into `.pydantic-ai-harness/` in the working directory (spills under `tool-output/` are **never pruned**), background commands outlive the run, `WindowsWorkspace('.')` replaces `LocalWorkspace` on a POSIX-less host, `Skills` and sub-agent definitions are read from the workspace at run start (`~/.agents/agents/` is no longer read), `FileMemoryStore` keeps its files in the workspace with receipts in `.memory-operations.json` instead of a SQLite journal, and `Capability Creation` runs only on a writable `LocalWorkspace`.

Cleanup advice follows from the same model: after a run with a provider backend exposing `aclose()`, finish using the workspace and `await result.workspace.backend.aclose()` to release the client session — that closes the client, not necessarily the sandbox — and provider deletion should use an ID-only delete API for refs the application owns, never creating a backend merely to delete a sandbox[^pydantic-coder-docs]

## Durability and limits

`Coder` works under Temporal, DBOS and Prefect when bound next to the workspace and the durability capability; on Temporal `delegate_task` delegates to `self` only[^pydantic-coder-docs] With a remote sandbox such as `ModalSandbox(working_dir='/workspace')`, loading repo instructions at run start creates the sandbox **before** the first model tool call, so `Coder(repo_context=False)` is the lazy-creation route — and then the instructions do not name the working directory.

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram was read in its text form[^pydantic-coder-docs] External links — `FileSystem`, `Shell`, `RepoContext`, `SubAgents`, compaction, tool-output limits, repair, permissions, caching, strict mode, the workspace and durable-execution pages, the E2B article and the Terminal-Bench playbook — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-opus-5-5`, an alias no release pin corroborates.

Nothing was installed, no repository read or edited, no command run, no delegate spawned, no argument repaired and no cache hit measured, so every claim is **Reported** and none **Observed** or **Reproduced**. The source does not state how the 32,000-character instruction budget is measured, what `ClearToolResults(max_fraction=0.7)` counts against, whether item 9's degradation applies to a `delegate_task` whose child run raised, or how `strict=False` interacts with a provider whose tool schemas are strict-only. It also does not say how a search cap is reported — a structured field on the result or prose inside it — what happens when `rg` is present but older than the pinned 14.1.0, or whether the 16,000-byte foreground tail is configurable.

## Relationships

- **Composes** [FileSystem](pydantic-ai-harness-filesystem.md), [Shell](pydantic-ai-harness-shell.md), [Harness subagents](pydantic-ai-subagents.md) and the capability catalog's `RepoContext`, `ClearToolResults`, `ToolOutputLimits`, `RepairToolArguments` and `Caching` entries.
- **Extended by** [Harness planning](pydantic-ai-harness-planning.md), [Harness smart search](pydantic-ai-harness-smart-search.md), [skills](pydantic-ai-harness-skills.md) and [background tools](pydantic-ai-harness-background-tools.md), which are added beside it rather than inside it.
- **Runs in** a [workspace](pydantic-ai-workspaces-and-sandboxes.md) — local, a container, or a cloud sandbox such as [Modal](pydantic-ai-harness-modal-sandbox.md) or E2B — and is the agent CLAI's `clai2` terminal builds on.
- **Relies on** [prompt caching](pydantic-ai-prompt-caching.md), [tool definitions](pydantic-ai-tool-definitions.md)' strict mode, and [durable execution](pydantic-ai-durable-execution.md) for what survives a restart.

[^pydantic-coder-docs]: Pydantic Docs, "Coder", <https://pydantic.dev/docs/ai/harness/coder/>; local capture `raw/harness/coder/index.md`, content digest sha256:8e371998, 4,567 words as declared (4,541 by `wc -w`), 362 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the combined-capability framing; 13–37 for the flow diagram (`FileSystem`, `Shell`, `SubAgents`, `RepoContext` in one `Coder()` against the workspace); 39–79 for the `coder` extra, `ripgrep==14.1.0`, the remote-workspace advice, the usage and Modal examples, `to_cli_sync`/`to_web` and `coder_agent`; 81–104 for the command environment and the `GH_TOKEN` example; 106–140 for sharing a workspace, `ReadOnlyWorkspace` and the delegate inheritance note; 142–166 for the eleven-part composition including `max_retries=5`, `coder_tool_output_limits`, the retry-exhaustion rule, caching and strict mode; 168–180 for the six-tool table and the stacked output caps; 182–196 for the sub-agent contract, the `run()` `UserError`, the delegation instruction and `task_control`; 198–205 for `unrestricted_filesystem`; 207–214 for long-running commands; 216–232 for the default instructions and the four autonomy levels; 234–244 for argument repair; 246–258 for strict mode and the Gemini request-wide caveat; 260–280 for prompt caching and its precedence; 282–286 for durable execution; 288–318 for the upgrade rules and the sandbox-cleanup advice; 320–345 for `BenchmarkInstructions`; 347–361 for the API reference. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
