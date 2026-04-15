# Local Pi Hook Layer

This repository now includes a project-local pi extension layer in `.pi/extensions/`.

The hook layer is intentionally narrow. It improves workflow ergonomics and safety while keeping the core knowledge workflows explicit, prompt-driven, and human-steered.

## What is implemented

### `workflow-router.ts`
Uses the `input` hook for deterministic routing:

- bare `https://...` input -> `/ingest-url <url>`
- bare `raw/...` path input -> `/ingest <path>`
- a few safe aliases:
  - `review` -> `/review`
  - `lint` -> `/lint`
  - `privacy-scan` -> `/privacy-scan`
  - `session-start` -> `/session-start`
  - `session-end` -> `/session-end`

This layer intentionally avoids broad natural-language rewriting.

### `vault-guardrails.ts`
Uses `tool_call` to apply deterministic repository policy.

Current behavior:

- blocks editing existing files in `raw/`
- blocks overwriting existing files in `raw/`
- blocks direct `write` replacement of `wiki/log.md`
- confirms or blocks destructive bash commands
- warns when editing governance files such as `AGENTS.md`, `.pi/prompts/`, and `.pi/skills/`
- warns on new markdown filenames that are not lowercase kebab-case
- warns on new wiki notes that lack YAML frontmatter
- blocks high-confidence secrets in `wiki/` and `outputs/`
- warns on medium-confidence sensitive-content patterns such as emails or phone numbers

### `workflow-auditor.ts`
Tracks file activity during an agent run and reports likely incomplete workflows at `agent_end`.

Current checks:

- durable artifacts changed without updating `wiki/log.md`
- important new wiki artifacts created without updating `wiki/index.md`
- `outputs/` changed without integrating `wiki/`
- ingest-like work that reads `raw/` but does not adequately integrate into `wiki/`
- newly created markdown artifacts that appear to lack citations

This extension is report-only. It warns after the turn instead of blocking work mid-edit.

### `session-reminders.ts`
Uses session lifecycle hooks for operational nudges.

Current behavior:

- at startup, reminds about pending captures in `raw/inbox/` and `raw/captures/`
- checks `wiki/log.md` for overdue `review` and `lint` entries
- optionally reminds about stale `privacy-scan` and `retention-pass` runs if those actions are logged
- at shutdown, suggests `/session-end` if the session changed several files and no explicit crystallization/session-end command was used

### `compaction-memory.ts`
Uses `session_before_compact` to preserve structured episodic session memory during compaction.

Current behavior:

- keeps the compaction summary shaped around:
  - goal
  - what was done
  - key findings / decisions
  - changed files / pages
  - unresolved questions
  - next recommended steps
- prefers a model-generated summary when a fast summarization model is available
- falls back to a deterministic heuristic summary when model-based compaction is unavailable
- does **not** write anything to `wiki/` or `outputs/`

### `inbox-watcher.ts`
Uses `session_start` and `session_shutdown` to run a notify-only watcher for capture folders.

Current behavior:

- watches `raw/inbox/` and `raw/captures/` while pi is running
- detects newly added files, including inside existing subdirectories
- shows a notification with the new paths
- suggests `/ingest <path>` for a single file or `/ingest-batch ...` for batches
- cleans up watchers on shutdown/reload
- does **not** auto-run ingest

### `scheduled-trigger.ts`
Uses a watched trigger queue plus extension commands for scheduled maintenance.

Current behavior:

- watches `.pi/state/maintenance-triggers.json` while pi is running
- accepts queued requests for:
  - `/review`
  - `/lint`
  - `/retention-pass`
  - `/privacy-scan`
- supports two modes:
  - `notify` = remind in the UI
  - `run` = enqueue the actual slash command in pi
- exposes opt-in commands:
  - `/maintenance-status`
  - `/maintenance-trigger <task> [notify|run] [reason]`
  - `/maintenance-run <task> [reason]`
- pairs with the helper script `.pi/scripts/trigger-maintenance.mjs`
- keeps semantic maintenance logic in the normal prompts and skills

For scheduler examples and usage details, see [`docs/pi-scheduled-maintenance.md`](./pi-scheduled-maintenance.md).

## Helper modules

Shared helper logic lives in `.pi/extensions/lib/`:

- `paths.ts` - repo-relative path handling and folder classification
- `policy.ts` - guardrail thresholds and dangerous-command rules
- `frontmatter.ts` - frontmatter, citation, and filename checks
- `secrets.ts` - secret / PII pattern scanning
- `log.ts` - `wiki/log.md` parsing helpers
- `audit.ts` - per-turn workflow audit state
- `maintenance.ts` - scheduled-maintenance queue parsing, validation, and persistence helpers

## What hooks should not do here

The hook layer does **not** replace prompts or skills.

It does not decide:

- what claims to extract from a source
- how contradictions should be resolved
- what belongs in canonical `wiki/`
- when a page should supersede another page
- how taxonomy should change

Those remain prompt/skill responsibilities.

## Reloading and rollback

After editing local extensions:

- use `/reload` inside pi to reload extensions, skills, prompts, and context

If a hook becomes noisy or too strict:

- move it out of `.pi/extensions/`, or rename the file so pi no longer auto-discovers it
- run `/reload`

Easy rollback targets for later phases:

- disable `compaction-memory.ts` to restore pi's default compaction behavior
- disable `inbox-watcher.ts` to stop live capture notifications
- disable `scheduled-trigger.ts` to stop external maintenance-trigger handling

Because each concern lives in its own extension, they can be disabled independently.
