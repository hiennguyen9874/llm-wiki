---
type: Concept
title: Pydantic AI Harness shell
description: The Harness Shell capability — four run-scoped command tools plus an opt-in persistent one, the allow/deny and operator filters that surface denials as retries, tail-keeping truncation, per-file and per-log byte limits, environment scrubbing, and background jobs that outlive a run.
tags: [pydantic-ai, agents, harness, execution]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-shell-docs
    resource: ../raw/harness/shell/index.md
    scope: ../raw/harness/shell/
    kind: documentation
    revision: sha256:c4c4ea10e3a2dd90040f3085f54724d3a72ecc72e335baab980c4e44d725a19b
    title: "Shell"
---

`Shell` is the [Harness](pydantic-ai-harness.md) capability that gives an agent command execution in the run's [workspace](pydantic-ai-workspaces-and-sandboxes.md), bundling the plumbing a coding agent needs — streaming, timeouts, truncation, process-group kills, background jobs across runs, and environment scrubbing — into one capability[^pydantic-shell-docs] It is the half of the filesystem story that [FileSystem](pydantic-ai-harness-filesystem.md) cannot cover: files the agent may not touch through a root-bounded tool, and work that only a process can do. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

Two framing facts decide most of what follows. Commands run in the run's workspace, so a run **without** one fails at its start and a **read-only** workspace offers no tools at all[^pydantic-shell-docs] And `Shell` is **not a security boundary**: a command reaches whatever the workspace lets it, whatever `FileSystem`'s `root_dir` says, and with `LocalWorkspace` it can read the process's environment and files — untrusted commands need a sandbox.

## Four tools, or one

The default registration is four **run-scoped** tools; naming `shell` in `tools` replaces them with a single **persistent** tool[^pydantic-shell-docs]:

| Tool | Job |
| --- | --- |
| `run_command` | Runs synchronously; returns labelled `[stdout]`/`[stderr]` and an `[exit code: N]` line on non-zero exit; takes a per-call `timeout_seconds` overriding `default_timeout` |
| `start_command` | Launches a long-running command (server, watcher) in the background and returns an ID |
| `check_command` | Polls a background command's status and accumulated output |
| `stop_command` | Terminates a background command and returns its final output |
| `shell` (opt-in, `tools=['shell']`) | Runs in `foreground` (waits up to the timeout, then hands back the still-running process) or `background`, returning the PID plus the paths of its output log and JSON status file |

Output is truncated from the **head**, keeping the tail, so stack traces, errors and the whole `[stderr]` section survive a long run; background status and exit metadata are written after the captured output so they stay in the retained tail too[^pydantic-shell-docs] `max_output_chars` defaults to 50,000 and bounds the returned tool result.

## What may run

Two mutually exclusive executable lists plus two filters[^pydantic-shell-docs]:

| Field | Effect |
| --- | --- |
| `allowed_commands` | When non-empty, only these executables may run |
| `denied_commands` | Always rejected; defaults to `rm`, `rmdir`, `mkfs`, `dd`, `format`, `shutdown`, `reboot`, `halt`, `poweroff`, `init` |
| `denied_operators` | Shell operators such as `>`, `>>`, `|` rejected whenever present |
| `allow_interactive` | `False` by default, blocking commands that expect a TTY (`vi`, `sudo`, `ssh`, …) |

Three details are easy to get wrong. Setting both lists raises `ValueError` at toolset construction. An **empty** `allowed_commands` does **not** select allowlist mode — the configured denylist stays active — so turning command-name filtering off means `denied_commands=[]`. And the executable is extracted with `shlex`, so arguments cannot smuggle a denied name through.

The denial is a [`ModelRetry`](pydantic-ai-tool-execution.md), not a hard error, and that split is the design[^pydantic-shell-docs]: every failure the model can act on — a denied command, a working directory an earlier command deleted, a command the OS refuses to spawn for a NUL or unencodable character, a command line too long to start — comes back as a retry, so the run continues and the model picks another route. Failures it cannot act on abort the run: no process available, an application-supplied `env` too large or invalid, a workspace that is gone. A command that overruns its timeout returns its output so far, ending in `[Command timed out after Ns]`.

## Byte limits: three different bounds

The source separates three limits that are often conflated, and only one of them is a quota[^pydantic-shell-docs]:

- **`max_output_chars`** (50,000) bounds the tool result returned to the model.
- **`max_file_bytes`** bounds each **regular file** written by `run_command` and `start_command`, including redirected output and background logs, applied through the workspace shell's `ulimit -f` and rounded up to whole 512-byte (POSIX `sh`) or 1 KiB (bash) blocks. A lower workspace limit makes the command fail with `Unable to apply max_file_bytes.` It cannot be combined with `persist_cwd=True` or `tools=['shell']`, and it is **not** a disk quota or a sandbox: it does not remove partial files, shrink existing ones, or stop a command creating many small files.
- **`max_log_bytes`** (100 MB) bounds the output logs of `start_command` and `shell` commands. Each log is checked once a second while the command runs and once more when it ends; a log past the limit is **emptied** and carries the notice `[Log exceeded max_log_bytes=<n>; earlier output was cleared.]`, while the command keeps running and later output is logged normally.

The log limit earns its place through one specific failure: a command that reads its own log (`cat .pydantic-ai-harness/shell/*/output.log | grep failed`) appends to the file it is reading, so without a limit it never reaches the end and the disk fills; once the log is emptied the read ends and the command exits[^pydantic-shell-docs] Unlike `max_file_bytes`, it works with `tools=['shell']`, and a log can grow by up to one second of output past the limit before it is cleared. Neither byte limit emits a telemetry span; the failure appears in the tool result, and a mid-call clear appears as `truncated=True` on the `shell` finished event.

## Environment

A command gets the workspace's environment plus `Shell(env=...)`, and `LocalWorkspace` passes on only `PATH`, `HOME`, `LANG`, `LC_ALL` and `LC_CTYPE` — nothing else — while a sandbox has whatever its provider configures[^pydantic-shell-docs] `denied_env_patterns` then drops variables from `env` by `fnmatch` glob, mirroring `denied_commands`, and filters **only** `env`, not `LocalWorkspace(env=)`, so a larger mapping can be narrowed on the way in.

The package ships `LLM_API_KEY_ENV_PATTERNS` as a ready-made starting point covering `ANTHROPIC_*`, `GATEWAY_*`, `GEMINI_*`, `GOOGLE_*`, `OPENAI_*`, `OPENROUTER_*` and `PYDANTIC_AI_GATEWAY_API_KEY`[^pydantic-shell-docs] Two limits are stated plainly: it covers LLM credentials only — a `LOGFIRE_TOKEN`, a GitHub token or cloud credentials pass through — and its prefixes are coarse enough that `GOOGLE_*` also strips `GOOGLE_APPLICATION_CREDENTIALS`. Treat it as a filter, not a boundary.

## Background and persistent processes

`start_command` runs the command inside the workspace and logs it under `.pydantic-ai-harness/shell/` in the working directory (git-ignored)[^pydantic-shell-docs] A background command is **not tied to the run**: a conversation spans runs, so a later run on the same workspace can `check_command` or `stop_command` by ID, and it keeps running until it exits, is stopped, or the workspace ends. `stop_command` signals the whole process group — `SIGTERM`, then `SIGKILL` after a grace period, so a `SIGTERM` stop reports `[exit code: 143]` — and removes the job's output files; if the command removed write permission from `.pydantic-ai-harness/shell/`, the directory stays and the result ends with `[job directory not removed: permission denied]`. Without `setsid` the job cannot get its own process group, only the wrapper is signalled, and the command and its children keep running.

The persistent `shell` tool is a different contract[^pydantic-shell-docs]: a small supervisor writes combined output to a log and `{"pid": …, "exit_code": …}` (`exit_code` null while running) to a JSON file, and the tool returns the PID and both paths so the model reads progress with its own file tools and stops the process with the `kill` command the result names. Foreground waits up to `timeout` (default `default_timeout`, capped at `MAX_FOREGROUND_WAIT` = 270 seconds), returns the last 16,000 bytes of the log followed by the handles, starts at a line with a note about how many earlier bytes were left out when the log is longer, and returns even if the command is still running. The handles come **last** precisely so tail-keeping truncation cannot drop them, and the 270-second cap keeps a call shorter than typical provider request timeouts — the model gets handles back, does other work, and polls the status file instead of stalling on a long build.

Nothing wakes the agent when a persistent command finishes; the model polls. Cancelling a foreground call kills the command, the command outlives the run and the event loop, logs that were handed back are never deleted, and — the durability limit — the workspace calls that start and poll these processes are **not replay-safe**[^pydantic-shell-docs] `allowed_commands`, `denied_commands`, `denied_operators`, `allow_interactive`, `env` and `denied_env_patterns` apply to `shell` exactly as to `run_command`; `persist_cwd` does not, because every `shell` command starts in the workspace's working directory.

## Streaming events

`shell` calls emit three progress events in the `shell` namespace so a UI can render output as it arrives without parsing the tool result[^pydantic-shell-docs]:

| Event | Dispatch | Payload |
| --- | --- | --- |
| `CommandStartedEvent` | stream | `command`, `pid` |
| `CommandOutputEvent` | stream | `text`, an incrementally decoded chunk of the combined log |
| `CommandFinishedEvent` | stream | `pid`, `output_path`, `status_path`, `exit_code`, `truncated`, `line_count` |

Output events fire only while a foreground call waits: at most the first 16,000 bytes of the log per call, in chunks of up to 4,096 bytes, polled every 50 ms to 1 s; a background call emits only started and finished. `finished` means the tool **stopped waiting**, not that the command exited — `exit_code` is `None` while no status is published, `truncated` says the log held more than the events showed, and `line_count` is `None` for logs over 1 MiB, which are not scanned. `total_lines` is the deprecated name of `line_count`: it still reads with a warning and a payload saved under it still loads. The payloads carry command text and output, so they are untrusted when rendered, and they add no telemetry spans because core already traces the tool call.

## Working directory

Each command starts in the workspace's working directory and `cd` has no lasting effect unless `persist_cwd=True`, which wraps every command so its final directory is recorded **out-of-band** to a private file inside the workspace and carried into subsequent calls[^pydantic-shell-docs] The path updates only when the command exits `0`, a recorded directory that disappears produces a retry and a reset to the workspace directory, and the out-of-band write is what stops command output from spoofing the tracked directory. Each run gets a fresh toolset, so the tracked directory is isolated between concurrent runs and always starts at the workspace root. `cwd=` is deprecated and ignored: set the directory on the workspace instead.

## Durability, specs and defaults

`Shell` works under Temporal, DBOS and Prefect, including background jobs and `persist_cwd`, and its `shell` tool also runs under Azure Durable Task and Render Workflows[^pydantic-shell-docs] On Temporal a command runs inside its activity's timeout — 300 seconds for `run_command` and `shell` — which has to be raised for longer work; see [durable execution](pydantic-ai-durable-execution.md) for the engine-by-engine picture.

Specs declare the capability by name with `custom_capability_types=[Shell]`, and the workspace is attached at run time (`workspace=` or a workspace capability), not in the YAML[^pydantic-shell-docs] The documented defaults are `default_timeout=30.0`, `max_output_chars=50_000`, `max_file_bytes=None`, `max_log_bytes=100_000_000`, `persist_cwd=False`, `allow_interactive=False`, `env=None`, `denied_env_patterns=[]`, `tools=RUN_SCOPED_TOOL_NAMES`; with `tools=['shell']`, `default_timeout` doubles as the foreground wait and must be greater than zero and at most 270, checked at construction.

On a `WindowsWorkspace`, `shell` and the background tools run PowerShell and the `shell` description says so; a stop runs the job's `stop.ps1`, which ends the process tree with `taskkill` while the PID is still the job's and records the exit code[^pydantic-shell-docs] `run_command` is not offered there because it wraps commands in `sh` (so `persist_cwd` has no effect), and `max_file_bytes` needs a POSIX workspace.

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram was read in its text form[^pydantic-shell-docs] External links — the workspace and durable-execution pages, toolsets, `ModelRetry`, the Azure, Render and Temporal pages, and the capabilities overview — were read as links and not followed. The page names no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule; its examples pin `anthropic:claude-opus-5-5`, an alias no release pin corroborates.

Nothing was installed, no command run, blocked, backgrounded, timed out, truncated or signalled, no event received and no replay attempted, so every claim is **Reported** and none **Observed** or **Reproduced**. The source does not state the SIGKILL grace period, how `denied_operators` parses nested or quoted operators, whether `max_file_bytes` counts the logs of the persistent tool, or what happens when a background job's log directory is a symlink — the operational unknowns that decide how tight the limits really are.

## Relationships

- **Depends on** the [workspace](pydantic-ai-workspaces-and-sandboxes.md), which supplies the environment and the working directory, and is offered no tools on a read-only backend.
- **Complements** [FileSystem](pydantic-ai-harness-filesystem.md): a `root_dir` bounds the file tools only, never a command.
- **Composed into** [Coder](pydantic-ai-harness-coder.md) with the persistent `shell` tool and no allowlist, and bounded beside it by [smart search](pydantic-ai-harness-smart-search.md) and [Coder](pydantic-ai-harness-coder.md)'s tool-output limits.
- **Constrained by** [durable execution](pydantic-ai-durable-execution.md): activity timeouts bound a command, and the persistent tool's start/poll calls are not replay-safe.
- **Ordered against** [background tools](pydantic-ai-harness-background-tools.md): a background *tool* keeps the model informed, while a background *command* must be polled by the model.

[^pydantic-shell-docs]: Pydantic Docs, "Shell", <https://pydantic.dev/docs/ai/harness/shell/>; local capture `raw/harness/shell/index.md`, content digest sha256:c4c4ea10, 3,606 words as declared (3,659 by `wc -w`), 434 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the one-paragraph purpose; 13–33 for the flow diagram (tool call → executable/operator/interactive checks → workspace process, or a rejected `denied_commands` retry); 35–43 for the problem statement and the bundled plumbing; 45–68 for the usage example and the `Shell()` default; 70–74 for where commands run, the fail-at-start and read-only-workspace cases; 76–90 for the five tools and the output labelling/tail rule; 92–115 for the allow/deny/operator/interactive table, the `ValueError`, the default denylist, the `shlex` extraction, the empty-`allowed_commands` rule and the retry-versus-abort split; 117–128 for `max_file_bytes`; 130–139 for `max_log_bytes` and the self-reading-log case; 141–165 for environment control and `LLM_API_KEY_ENV_PATTERNS`; 167–195 for background processes, the `.pydantic-ai-harness/shell/` log path, the SIGTERM/SIGKILL sequence and the job-directory and `setsid` failures; 197–214 for the persistent `shell` tool, the 16,000-byte tail, the 270-second cap and the non-replay-safe note; 216–240 for the three `shell` events and their payloads; 242–266 for `persist_cwd`; 268–292 for the full default configuration block and the agent-spec form; 294–298 for the durable-execution engines and the Temporal 300-second activity timeout; 300–433 for the API reference, including the Windows-workspace behaviour. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
